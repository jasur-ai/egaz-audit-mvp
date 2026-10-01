# -*- coding: utf-8 -*-
"""Ochiq havo sifati qatoridan hududiy ekran + shamol bo'yicha nomzod atributsiyasi.

Zanjir (hammasi ochiq manbadan, korxona ruxsatisiz):
  1) soatlik qator (Open-Meteo CAMS, `fetch_public.py`) → **kunlik o'rtachalar** (qamrov nazorati bilan);
  2) norma bilan solishtirib **normadan oshgan kunlar** statistikasi;
  3) oshgan soatlarning **shamol yo'nalishi** bo'yicha nomzod obyektlar (ochiq reyestr) sanaladi.

Chegara (ochiq yoziladi): bu ekran **hududiy** — «shu hududda muammo bor» deydi.
Obyektni «ayblash» uchun isbot kuchi 3+ ikkinchi yo'l kerak (registry.conclusion_rule).
"""
from __future__ import annotations

from typing import Any, Iterable

from .plume import angle_diff, attribute_candidates

# SanQvaM 0053-23 — PM2,5 uchun kunlik o'rtacha norma (boshqa moddalar — foydalanuvchi beradi)
NORMS = {
    "pm2_5": {"qiymat": 35.0, "birlik": "µg/m³", "ortacha": "kunlik (24 soat)", "manba": "SanQvaM 0053-23"},
}


def daily_means(
    times: Iterable[str],
    values: Iterable[float],
    min_completeness: float = 0.75,
) -> list[dict[str, Any]]:
    """Soatlik qatorni kunlik o'rtachalarga yig'ish (ISO vaqt, mahalliy +05).

    `min_completeness` — kun yaroqli hisoblanishi uchun minimal soat qamrovi (0,75 = 18/24 soat).
    Qamrov yetmasa — kun «yaroqsiz» belgilanadi (norma bilan solishtirilmaydi).
    """
    if not 0 < min_completeness <= 1:
        raise ValueError("min_completeness (0;1]")
    buckets: dict[str, list[float]] = {}
    for t, v in zip(times, values):
        kun = str(t)[:10]
        buckets.setdefault(kun, []).append(v)
    out = []
    for kun in sorted(buckets):
        vals = [float(v) for v in buckets[kun] if v is not None]
        n = len(vals)
        out.append({
            "kun": kun,
            "qiymat": round(sum(vals) / n, 2) if n else None,
            "soat_soni": n,
            "qamrov": round(n / 24, 3),
            "yaroqli": (n / 24) >= min_completeness and n > 0,
        })
    return out


def exceedance_days(daily: list[dict[str, Any]], norm: float) -> dict[str, Any]:
    """Normadan oshgan kunlar (faqat yaroqli kunlar hisobga olinadi)."""
    if norm <= 0:
        raise ValueError("norma > 0")
    yaroqli = [d for d in daily if d["yaroqli"] and d["qiymat"] is not None]
    oshgan = [d for d in yaroqli if d["qiymat"] > norm]
    return {
        "norma": norm,
        "tekshirilgan_kunlar": len(yaroqli),
        "yaroqsiz_kunlar": len(daily) - len(yaroqli),
        "oshgan_kunlar": len(oshgan),
        "ulush": round(len(oshgan) / len(yaroqli), 3) if yaroqli else None,
        "kunlar": [d["kun"] for d in oshgan],
        "eng_yuqori": max((d["qiymat"] for d in yaroqli), default=None),
        "izoh": "Kunlik o'rtacha norma bo'yicha; soatlik cho'qqilar alohida hisoblanadi.",
    }


def attribute_hours(
    dirty_hours: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    max_angle_deg: float = 45.0,
    max_km: float = 30.0,
) -> dict[str, Any]:
    """Oshgan soatlarning shamol yo'nalishi bo'yicha nomzodlarni sanash.

    `dirty_hours` — [{"vaqt": …, "wind_from": gradus, "receptor_lat": …, "receptor_lon": …}, …]
    Natija: har bir nomzod qancha soatda «yuqori tomonda» bo'lgan (hits) va o'rtacha burchak xatosi.
    """
    if not dirty_hours:
        raise ValueError("bo'sh ro'yxat")
    hits: dict[str, dict[str, Any]] = {}
    for h in dirty_hours:
        res = attribute_candidates(
            h["receptor_lat"], h["receptor_lon"], h["wind_from"], candidates,
            max_angle_deg=max_angle_deg, max_km=max_km,
        )
        for c in res["nomzodlar"]:
            if not c["mos"]:
                continue
            slot = hits.setdefault(c["nom"], {"nom": c["nom"], "hits": 0, "burchak_yigindi": 0.0,
                                              "masofa_km": c["masofa_km"]})
            slot["hits"] += 1
            slot["burchak_yigindi"] += c["burchak_xatosi"]
    ro = []
    for slot in hits.values():
        ro.append({
            "nom": slot["nom"],
            "hits": slot["hits"],
            "ulush": round(slot["hits"] / len(dirty_hours), 3),
            "ort_burchak_xatosi": round(slot["burchak_yigindi"] / slot["hits"], 1),
            "masofa_km": slot["masofa_km"],
        })
    ro.sort(key=lambda x: (-x["hits"], x["ort_burchak_xatosi"]))
    return {
        "soatlar": len(dirty_hours),
        "nomzodlar": ro,
        "barobar_manba_ogohi": (len(ro) > 1 and ro[0]["ulush"] < 0.6),
        "izoh": "«hits» — soatlar ulushi; bir yo'nalishda bir nechta obyekt bo'lsa ajratilmaydi.",
        "isbot_kuchi": 2,
    }


def screen_report(
    times: Iterable[str],
    values: Iterable[float],
    substance: str = "pm2_5",
    norm: float | None = None,
    dirty_hours_wind: list[dict[str, Any]] | None = None,
    candidates: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """To'liq ekran hisoboti: kunlik o'rtachalar → oshgan kunlar → (ixtiyoriy) atributsiya."""
    if norm is None:
        if substance not in NORMS:
            raise ValueError(f"{substance} uchun standart norma yo'q — `norm` bering")
        norm = NORMS[substance]["qiymat"]
    daily = daily_means(times, values)
    exc = exceedance_days(daily, norm)
    out: dict[str, Any] = {
        "modda": substance,
        "norma": norm,
        "kunlik": daily,
        "oshish": exc,
        "kirish_kaliti": "kerak emas (ochiq API)",
        "manba": "Open-Meteo Air Quality (CAMS) · SanQvaM 0053-23",
        "isbot_kuchi": 2,
        "nima_isbotlanmaydi": "Qaysi korxona sabab ekani; bir nechta manba ajratilmaydi; "
                              "model hujayrasi ~10–25 km.",
    }
    if dirty_hours_wind and candidates:
        out["atributsiya"] = attribute_hours(dirty_hours_wind, candidates)
    return out


def to_float(x) -> float | None:
    """CSV/JSON qiymatini xavfsiz songa aylantirish: bo'sh satr, None, «—» → None.

    Nima uchun kerak: ochiq API'lar (masalan Open-Meteo shamol) oynaning boshida bo'sh
    qatorlar qaytarishi mumkin — bunday qatorlar **0 emas, «yo'q»** deb qaralishi shart,
    aks holda atributsiya noto'g'ri hisoblanadi.
    """
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    t = str(x).strip().replace(",", ".")
    if t in ("", "-", "—", "nan", "NaN", "null", "None"):
        return None
    try:
        return float(t)
    except ValueError:
        return None


def dirty_hours_by_time(
    aq_times: Iterable[str],
    aq_values: Iterable[float | None],
    wind_times: Iterable[str],
    wind_values: Iterable[float | None],
    norm_hourly: float,
) -> dict[str, Any]:
    """Normadan oshgan soatlarni shamol bilan **vaqt bo'yicha** juftlash.

    Indeks bo'yicha juftlash xato: ikki fayl turli davrni qoplashi mumkin (masalan havo sifati
    92 kun, shamol 66 kun) — u holda qiymatlar siljib ketadi. Shu sababli kalit — `vaqt`.

    Qaytadi: `soatlar` (atributsiya uchun), `oshgan` (jami oshgan soat), `shamol_yoq`
    (shamoli bo'lmagan oshgan soatlar), `qamrov` (shamoli bor oshgan soatlar ulushi).
    """
    wind_map = {t: to_float(v) for t, v in zip(wind_times, wind_values)}
    soatlar: list[dict[str, Any]] = []
    oshgan = 0
    shamol_yoq = 0
    for t, v in zip(aq_times, aq_values):
        val = to_float(v)
        if val is None or val <= norm_hourly:
            continue
        oshgan += 1
        w = wind_map.get(t)
        if w is None:
            shamol_yoq += 1
            continue
        soatlar.append({"vaqt": t, "qiymat": val, "wind_from": w})
    return {
        "soatlar": soatlar,
        "oshgan": oshgan,
        "shamol_yoq": shamol_yoq,
        "qamrov": (len(soatlar) / oshgan if oshgan else 0.0),
    }


def dirty_hours(times: Iterable[str], values: Iterable[float], wind_from: Iterable[float],
                norm_hourly: float) -> list[dict[str, Any]]:
    """Soatlik norma oshgan soatlarni shamol yo'nalishi bilan juftlash (atributsiya uchun)."""
    out = []
    for t, v, w in zip(times, values, wind_from):
        if v is None or w is None:
            continue
        if float(v) > norm_hourly:
            out.append({"vaqt": t, "qiymat": float(v), "wind_from": float(w)})
    return out
