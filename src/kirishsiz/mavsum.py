# -*- coding: utf-8 -*-
"""Isitish mavsumi oynasi va mavsumiy taqqoslash (R50, B-qatlam 3-qadam).

Maqsad: A-qatlam oynasi (apr–sen, issiq mavsum) **isitish mavsumini qoplamaydi**. Bu modul:
  1. oynaning mavsumiy **qamrovini** hisoblaydi (qaysi oylar, qancha soat);
  2. isitish kunlarini **harorat mezoni** bo'yicha ajratadi;
  3. mavsum bo'yicha **sektor liftini** qayta hisoblaydi (issiq ↔ isitish).

Mezon: `ISITISH_CHEGARA_C = +8 °C` — o'rtacha kunlik havo harorati shu chegaradan past bo'lsa, bino
isitish davri boshlangan hisoblanadi (binolarni proyektlash bo'yicha standart amaliyot).
O'zbekistonda isitish mavsumining **rasmiy sanalari** tuman hokimiyatlari qarori bilan belgilanadi;
shu sababli kod mezoni «operativ» deb belgilanadi va xulosada rasmiy sanaga havola qilinmaydi.

Nima isbotlanmaydi: 180 kunlik oyna issiq mavsum — isitish hissasi **baholanmaydi**; bu modul
10.10 dan keyingi kengaytirilgan oyna uchun tayyor asbob.
"""
from __future__ import annotations

from typing import Any, Iterable

from .plume import angle_diff
from .screener import to_float

ISITISH_CHEGARA_C = 8.0
ISITISH_OYLARI = (10, 11, 12, 1, 2, 3)          # operativ: oktabr–mart


def kunlik_ort(times: Iterable[str], qiymatlar: Iterable) -> list[dict[str, Any]]:
    """Soatlik qatordan kunlik o'rtacha (vaqt belgisi `YYYY-MM-DDTHH:MM`)."""
    yig: dict[str, list[float]] = {}
    for t, v in zip(times, qiymatlar):
        vv = to_float(v)
        if vv is None or not t:
            continue
        yig.setdefault(t[:10], []).append(vv)
    return [{"kun": k, "n": len(v), "ort": round(sum(v) / len(v), 2), "min": round(min(v), 2),
             "maks": round(max(v), 2)} for k, v in sorted(yig.items())]


def isitish_kunlari(kunlik: list[dict[str, Any]], chegara: float = ISITISH_CHEGARA_C) -> list[dict[str, Any]]:
    """O'rtacha kunlik harorat chegaradan past (yoki teng) kunlar."""
    return [k for k in kunlik if k["ort"] <= chegara]


def qamrov(times: Iterable[str], haroratlar: Iterable | None = None,
           chegara: float = ISITISH_CHEGARA_C) -> dict[str, Any]:
    """Oynaning mavsumiy qamrovi: oylar, soatlar, isitish ulushi."""
    oylar: dict[str, int] = {}
    jami = 0
    for t in times:
        if not t:
            continue
        jami += 1
        oylar[t[:7]] = oylar.get(t[:7], 0) + 1
    q: dict[str, Any] = {"jami_soat": jami, "oylar": dict(sorted(oylar.items())),
                         "chegara_C": chegara}
    if haroratlar is not None:
        isit = 0
        for t, h in zip(times, haroratlar):
            hh = to_float(h)
            if hh is not None and hh <= chegara:
                isit += 1
        q["isitish_soat"] = isit
        q["isitish_ulush_foiz"] = round(100.0 * isit / jami, 2) if jami else None
        q["issiq_soat"] = jami - isit
    return q


def oylik_bolish(times: Iterable[str], qiymatlar: Iterable) -> dict[str, list[float]]:
    """Vaqt bo'yicha oylik guruhlash (harorat yoki konsentratsiya uchun)."""
    out: dict[str, list[float]] = {}
    for t, v in zip(times, qiymatlar):
        vv = to_float(v)
        if vv is None or not t:
            continue
        out.setdefault(t[:7], []).append(vv)
    return out


def mavsumiy_lift(ustunlar: dict[str, Iterable], winds: Iterable, haroratlar: Iterable,
                  markaz: float, kenglik: float = 45.0,
                  chegara: float = ISITISH_CHEGARA_C) -> dict[str, Any]:
    """Sektor liftini **isitish** va **issiq** soatlarga ajratib hisoblash."""
    w = [to_float(x) for x in winds]
    h = [to_float(x) for x in haroratlar]
    natija: dict[str, Any] = {"chegara_C": chegara, "markaz": markaz, "kenglik": kenglik, "moddalar": {}}
    for nom, seriya in ustunlar.items():
        s = [to_float(x) for x in seriya]
        natija["moddalar"][nom] = {}
        for rejim in ("isitish", "issiq"):
            ichida: list[float] = []
            tashqarida: list[float] = []
            for v, ww, hh in zip(s, w, h):
                if v is None or ww is None or hh is None:
                    continue
                mos_rejim = (hh <= chegara) if rejim == "isitish" else (hh > chegara)
                if not mos_rejim:
                    continue
                (ichida if angle_diff(ww, markaz) <= kenglik else tashqarida).append(v)
            if len(ichida) < 3 or len(tashqarida) < 3:
                natija["moddalar"][nom][rejim] = {"n_sektor": len(ichida), "n_tashqari": len(tashqarida),
                                                  "xato": "ma'lumot yetarli emas (<3 soat)"}
                continue
            oi = sum(ichida) / len(ichida)
            ot = sum(tashqarida) / len(tashqarida)
            natija["moddalar"][nom][rejim] = {
                "n_sektor": len(ichida), "n_tashqari": len(tashqarida),
                "ort_sektor": round(oi, 2), "ort_tashqari": round(ot, 2),
                "lift": round(oi / ot, 2) if ot else None,
                "ortiqcha": round(oi - ot, 2)}
    return natija


def yuklama_oshishi(isitish_ulushi_mavsum: float, issiq_ulushi_mavsum: float,
                    isitish_nisbat: float, issiq_nisbat: float) -> dict[str, Any]:
    """Sektor-o'rtacha ortiqchaning mavsumiy o'zgarishi: ikkala rejim nisbatidan vaznli baho."""
    if not 0 <= isitish_ulushi_mavsum <= 1 or not 0 <= issiq_ulushi_mavsum <= 1:
        raise ValueError("ulushlar 0…1 oralig'ida bo'lishi kerak")
    if abs(isitish_ulushi_mavsum + issiq_ulushi_mavsum - 1.0) > 0.01:
        raise ValueError("ulushlar yig'indisi 1 bo'lishi kerak")
    vaznli = isitish_ulushi_mavsum * isitish_nisbat + issiq_ulushi_mavsum * issiq_nisbat
    return {"isitish_nisbat": isitish_nisbat, "issiq_nisbat": issiq_nisbat,
            "vaznli_nisbat": round(vaznli, 2),
            "izoh": "nisbat > 1 bo'lsa isitish mavsumi kuchaytiradi; hozircha o'lchov yo'q — "
                    "faqat prognoz asosi"}


def reja(qamrov_natija: dict[str, Any], maqsad_oylar: Iterable[str] = ("2026-10", "2026-11")) -> dict[str, Any]:
    """Oynani kengaytirish rejasi: hozirgi qamrov ↔ maqsadli oylar."""
    bor = set(qamrov_natija.get("oylar", {}))
    kerak = [oy for oy in maqsad_oylar if oy not in bor]
    return {"hozirgi_oylar": sorted(bor), "qo'shilishi_kerak": kerak,
            "qadam": "`fetch_public.py --source open-meteo-aq --kun <N>` va ERA5 oynasi "
                     "yangi sanalar bilan qayta olinadi; keyin `sektor` va `mavsum` qayta ishlanadi",
            "eslatma": "rasmiy isitish mavsumi sanalari hokimiyat qarori bilan — hujjatda ko'rsatiladi"}
