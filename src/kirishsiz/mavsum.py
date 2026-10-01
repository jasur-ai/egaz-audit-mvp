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

import math
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

def o_rtacha_yonalish(yonalishlar: Iterable) -> float | None:
    """Yo'nalishlarning vektor o'rtachasi (aylana bo'yicha, 0–360°)."""
    sx = sy = 0.0
    n = 0
    for y in yonalishlar:
        yy = to_float(y)
        if yy is None:
            continue
        sx += math.sin(math.radians(yy))
        sy += math.cos(math.radians(yy))
        n += 1
    if not n or (sx == 0 and sy == 0):
        return None
    d = math.degrees(math.atan2(sx, sy)) % 360
    if d >= 359.95:          # suzuvchi nuqta: −0,0001° → 359,9999° → 0°
        d = 0.0
    return round(d, 1)


def epizod_atributsiya(times: Iterable[str], qiymatlar: Iterable, winds: Iterable,
                       haroratlar: Iterable, markaz: float, kenglik: float = 45.0,
                       chegara: float = 35.0, kamida_soat: int = 12,
                       tezliklar: Iterable | None = None) -> dict[str, Any]:
    """**Epizodlarni yo'nalish bo'yicha atributsiya qilish** (R50, isitish mavsumi).

    Har bir «normadan oshgan kun» uchun: o'sha kun shamolining qanchasi manba sektoridan (±kenglik)
    kelgan, o'rtacha yo'nalish, harorat va shamol tezligi. Shu asosda kun **uch toifaga** bo'linadi:

      • `sektor_ustun` — soatlarning ≥50% sektordan → manba hissasi ehtimoli katta;
      • `aralash` — 20–50% → qisman;
      • `sektordan_tashqarida` — <20% → **manba sektori bu kunni tushuntirmaydi**.
    """
    t = [str(x)[:10] for x in times]
    yig: dict[str, dict[str, list]] = {}
    for i, kun in enumerate(t):
        q = to_float(qiymatlar[i]) if i < len(list(qiymatlar)) else None
        savat = yig.setdefault(kun, {"v": [], "w": [], "h": [], "u": []})
        if q is None:
            continue
        savat["v"].append(q)
        w = to_float(winds[i]) if i < len(list(winds)) else None
        if w is not None:
            savat["w"].append(w)
        h = to_float(haroratlar[i]) if i < len(list(haroratlar)) else None
        if h is not None:
            savat["h"].append(h)
        if tezliklar is not None:
            u = to_float(tezliklar[i]) if i < len(list(tezliklar)) else None
            if u is not None:
                savat["u"].append(u)

    kunlar: list[dict[str, Any]] = []
    for kun, s in sorted(yig.items()):
        if len(s["v"]) < kamida_soat:
            continue
        ort = sum(s["v"]) / len(s["v"])
        if ort <= chegara:
            continue
        ulush = (sum(1 for w in s["w"] if angle_diff(w, markaz) <= kenglik) / len(s["w"])) if s["w"] else None
        if ulush is None:
            toifa = "yo'nalish_yo_q"
        elif ulush >= 0.5:
            toifa = "sektor_ustun"
        elif ulush >= 0.2:
            toifa = "aralash"
        else:
            toifa = "sektordan_tashqarida"
        kunlar.append({"kun": kun, "ort_pm": round(ort, 2), "soat": len(s["v"]),
                       "sektor_ulush": round(ulush, 3) if ulush is not None else None,
                       "ort_yonalish": o_rtacha_yonalish(s["w"]),
                       "ort_harorat": round(sum(s["h"]) / len(s["h"]), 1) if s["h"] else None,
                       "ort_shamol_ms": round(sum(s["u"]) / len(s["u"]), 2) if s["u"] else None,
                       "toifa": toifa})
    hisob = {k: sum(1 for x in kunlar if x["toifa"] == k)
             for k in ("sektor_ustun", "aralash", "sektordan_tashqarida", "yo'nalish_yo_q")}
    return {"chegara": chegara, "markaz": markaz, "kenglik": kenglik, "kunlar": kunlar,
            "jami": len(kunlar), "hisob": hisob,
            "xulosa": (f"{len(kunlar)} epizoddan {hisob['sektor_ustun']} tasida shamol asosan manba "
                       f"sektoridan; {hisob['sektordan_tashqarida']} tasida esa **undan emas**") if kunlar
            else "normadan oshgan kun yo'q"}
