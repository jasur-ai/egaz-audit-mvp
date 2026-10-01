# -*- coding: utf-8 -*-
"""Sektor tahlili — «yuqori tomon» signalining kuchini o'lchash (isbot kuchi 2).

G'oya: agar havoning ifloslanishi ma'lum bir yo'nalishdagi manbalardan kelayotgan bo'lsa,
**yuqori soatlar** (qiymat bo'yicha yuqori kvantil) ichida o'sha sektordan esgan shamol
ulushi **fon ulushidan ko'p** bo'lishi kerak. Bu nisbat — *yo'nalish boyitilishi* (lift):

    lift = (yuqori soatlarda sektor ulushi) / (barcha soatlarda sektor ulushi)

Nima isbotlanadi: qiymatlar shu sektorga bog'liq bo'lishi mumkin (skrining signali).
Nima isbotlanmaydi: **qaysi obyekt** ekani; lift sababi boshqa manba (yo'l changi, uy isitish,
transchegaraviy oqim) ham bo'lishi mumkin; CAMS hujayrasi 10–25 km, shamol ERA5 (10 m) —
shu sababli lift **faqat keyingi tekshiruvga asos**, dalil emas.
"""
from __future__ import annotations

from typing import Any, Iterable, Sequence

from .plume import angle_diff
from .screener import to_float

SEKTORLAR = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]


def _yaroqli(values: Iterable[float | None], winds: Iterable[float | None]) -> list[tuple[float, float]]:
    """(qiymat, shamol) juftliklari — bo'sh satr/None «yo'q» deb qaraladi (0 emas)."""
    juft = []
    for v, w in zip(values, winds):
        vv, ww = to_float(v), to_float(w)
        if vv is None or ww is None:
            continue
        juft.append((vv, ww))
    return juft


def wind_rose(winds: Iterable[float | None]) -> dict[str, Any]:
    """8 sektor bo'yicha shamol takrorlanishi (shamollanish gulining asosi)."""
    hisob = {s: 0 for s in SEKTORLAR}
    jami = 0
    for w in winds:
        ww = to_float(w)
        if ww is None:
            continue
        ww = ww % 360.0
        idx = int(((ww + 22.5) % 360.0) // 45.0)     # «qayerdan esadi» → sektor
        hisob[SEKTORLAR[idx]] += 1
        jami += 1
    ulush = {s: (hisob[s] / jami if jami else 0.0) for s in SEKTORLAR}
    eng = sorted(ulush.items(), key=lambda kv: -kv[1])[:3] if jami else []
    return {"sektorlar": hisob, "ulush": ulush, "jami": jami,
            "eng_kop": [{"sektor": s, "ulush": round(u, 3)} for s, u in eng],
            "nima_isbotlanmaydi": "Shamollanish guli — iqlim tavsifi, manba ko'rsatmaydi."}


def sektor_ulushi(winds: Iterable[float | None], markaz: float, kenglik: float = 45.0) -> dict[str, Any]:
    """Berilgan yo'nalish (±kenglik) sektoridan esgan soatlar ulushi."""
    mos = jami = 0
    for w in winds:
        ww = to_float(w)
        if ww is None:
            continue
        jami += 1
        if angle_diff(ww, float(markaz)) <= kenglik:
            mos += 1
    return {"mos": mos, "jami": jami, "ulush": (mos / jami if jami else 0.0),
            "markaz": float(markaz), "kenglik": float(kenglik)}


def _kvantil(qiymatlar: Sequence[float], p: float) -> float:
    """Chiziqli interpolyatsiyali kvantil (numpy'siz, aniq ta'rif bilan)."""
    if not qiymatlar:
        raise ValueError("bo'sh ro'yxat")
    s = sorted(qiymatlar)
    if len(s) == 1:
        return s[0]
    pos = (len(s) - 1) * p
    past = int(pos)
    yuqori = min(past + 1, len(s) - 1)
    frac = pos - past
    return s[past] * (1 - frac) + s[yuqori] * frac


def directional_enrichment(
    values: Iterable[float | None],
    winds: Iterable[float | None],
    markaz: float,
    kenglik: float = 45.0,
    kvantil: float = 0.90,
) -> dict[str, Any]:
    """Yuqori soatlarda sektor ulushining fonga nisbatan boyitilishi (lift)."""
    juft = _yaroqli(values, winds)
    if len(juft) < 50:
        return {"xato": "juda kam ma'lumot (≥50 soat kerak)", "n": len(juft)}
    chegaralangan = _kvantil([v for v, _ in juft], kvantil)
    yuqori = [(v, w) for v, w in juft if v >= chegaralangan]
    fon = sektor_ulushi([w for _, w in juft], markaz, kenglik)
    sign = sektor_ulushi([w for _, w in yuqori], markaz, kenglik)
    lift = (sign["ulush"] / fon["ulush"]) if fon["ulush"] > 0 else None
    return {
        "n_soat": len(juft),
        "kvantil": kvantil,
        "chegara": round(chegaralangan, 2),
        "yuqori_soatlar": len(yuqori),
        "sektor": {"markaz": float(markaz), "kenglik": float(kenglik)},
        "fon_ulushi": round(fon["ulush"], 3),
        "yuqori_ulushi": round(sign["ulush"], 3),
        "lift": (round(lift, 2) if lift is not None else None),
        "xulosa": _xulosa(lift),
        "isbot_kuchi": 2,
        "nima_isbotlanmaydi": "Qaysi obyekt ekani; lift boshqa manba (chang, transport, uy isitish, "
                              "transchegaraviy oqim) hisobidan ham bo'lishi mumkin.",
    }


def _xulosa(lift: float | None) -> str:
    if lift is None:
        return "fon ulushi nol — lift hisoblanmaydi"
    if lift >= 1.5:
        return "sektor bo'yicha signal bor (keyingi tekshiruvga asos)"
    if lift >= 1.15:
        return "kuchsiz signal — ehtiyotkorlik bilan"
    return "signal yo'q — qiymatlar sektorga bog'lanmadi"


def ko_p_modda(values_by_substance: dict[str, tuple[Iterable[float | None], Iterable[float | None]]],
               markaz: float, kenglik: float = 45.0, kvantil: float = 0.90) -> dict[str, Any]:
    """Bir necha modda bo'yicha taqqoslama sektor tahlili."""
    out = {}
    for modda, (vals, winds) in values_by_substance.items():
        out[modda] = directional_enrichment(vals, winds, markaz, kenglik, kvantil)
    eng = sorted(((m, r.get("lift")) for m, r in out.items() if r.get("lift") is not None),
                 key=lambda kv: -kv[1])
    return {"moddalar": out,
            "eng_kuchli": ({"modda": eng[0][0], "lift": eng[0][1]} if eng else None),
            "eslatma": "Lift — skrining ko'rsatkichi; moddalar bir xil sharoitda (bir xil soatlar) "
                       "taqqoslanadi va faqat nisbiy kuchni ko'rsatadi."}


def candidate_sector(lat: float, lon: float, nomzodlar: list[dict[str, Any]],
                     kenglik: float = 45.0) -> dict[str, Any]:
    """Nomzodlarga qarab «tekshiriladigan sektorlar» ro'yxatini berish (tahlil rejasi uchun)."""
    from .plume import bearing_deg, haversine_m

    sektorlar = []
    for c in nomzodlar:
        b = bearing_deg(lat, lon, c["lat"], c["lon"])
        sektorlar.append({"nom": c.get("nom", "?"), "markaz": round(b, 1), "kenglik": kenglik,
                          "masofa_km": round(haversine_m(lat, lon, c["lat"], c["lon"]) / 1000.0, 2)})
    return {"sektorlar": sektorlar,
            "eslatma": "Sektor markazi — nomzod yo'nalishi; tahlil shu sektor bo'yicha o'tkaziladi."}

def yonalish_profili(qiymatlar: Iterable[float | None], winds: Iterable[float | None],
                     qadam: float = 15.0, kamida: int = 5) -> dict[str, Any]:
    """Yo'nalish profili: 15° lik burchaklar bo'yicha o'rtacha konsentratsiya.

    Sektorni **qo'lda tanlash** o'rniga profil eng yuqori burchakni o'zi ko'rsatadi —
    bu tanlov xatosi (cherry-picking) riskini kamaytiradi.
    """
    if qadam <= 0 or 360 % qadam:
        raise ValueError("qadam 360 ning bo'luvchisi bo'lishi kerak")
    savat: dict[int, list[float]] = {}
    for v, w in _yaroqli(qiymatlar, winds):
        b = int(((w + qadam / 2) % 360) // qadam) * int(qadam)
        savat.setdefault(b, []).append(v)
    binlar = []
    for b in range(0, 360, int(qadam)):
        v = savat.get(b, [])
        binlar.append({"burchak": b, "n": len(v),
                       "ort": round(sum(v) / len(v), 2) if v else None})
    yaroqli = [b for b in binlar if b["n"] >= kamida and b["ort"] is not None]
    cho_qqi = max(yaroqli, key=lambda x: x["ort"]) if yaroqli else None
    past = min(yaroqli, key=lambda x: x["ort"]) if yaroqli else None
    return {"qadam": qadam, "binlar": binlar, "cho_qqi": cho_qqi, "past": past,
            "kamida_bin": kamida,
            "izoh": "Cho'qqi burchagi — **nomzod**, tasdiqlangan manba emas; sektor kengligini "
                    "profil kengligi (qadam) belgilaydi."}


def profil_grafik(profil: dict[str, Any], kenglik: int = 30) -> str:
    """Profilni ASCII ustunlar bilan ko'rsatish (chop etish uchun)."""
    qiymatlar = [b["ort"] for b in profil["binlar"] if b["ort"] is not None]
    if not qiymatlar:
        return "(ma'lumot yo'q)"
    eng = max(qiymatlar)
    satrlar = [f"  {'burchak':>8}  {'o\u2019rt':>7}  {'n':>5}  profil"]
    for b in profil["binlar"]:
        if b["ort"] is None:
            satrlar.append(f"  {b['burchak']:>7}°  {'—':>7}  {b['n']:>5}")
            continue
        uzun = int(round(b["ort"] / eng * kenglik)) if eng else 0
        satrlar.append(f"  {b['burchak']:>7}°  {b['ort']:>7.2f}  {b['n']:>5}  {'▉' * uzun}")
    return "\n".join(satrlar)
