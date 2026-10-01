# -*- coding: utf-8 -*-
"""Ikkilamchi aerozol va PM2,5 manbasini ajratish (R50, B-qatlam).

Savol: sektor ortiqchasidagi PM2,5 (+2,89 µg/m³) **birlamchi gaz yonishi zarrasi** bilan izohlanadimi?
Javob «yo'q» bo'lsa — qaysi mexanizm ko'rsatilishi mumkin (chang / ikkilamchi aerozol / isitish)?

Usullar (hammasi kod bilan, tarmoqsiz):
  • PM2,5/PM10 nisbati — zarra o'lcham taqsimoti: yuqori nisbat (>0,6) → yonish/ikkilamchi aerozol;
    past (<0,3) → mexanik chang (grunt, qurilish, sement).
  • Chang ulushi (CAMS `dust`) — PM10 ning qanchasi cho'l/chang modeli komponenti.
  • AOD (aerozol optik qalinligi) — butun kolonka aerozol yuki (mustaqil proksi).
  • Harorat bog'liqligi (Pearson r) — isitish (qish) signali bo'lsa r < −0,3 bo'ladi.
  • Mass-rekonstruksiya — modellashtirilgan birlamchi zarra kuzatuv ortiqchasining necha foizini beradi.

Nima isbotlanmaydi: kimyoviy tarkib (nitrat/sulfat) o'lchovi yo'q; CAMS komponentlari — model, stansiya emas;
180 kunlik oyna **issiq mavsum** (apr–sen) — isitish xulosasi chiqarilmaydi.
"""
from __future__ import annotations

import math
from typing import Any, Iterable

from .plume import angle_diff
from .screener import to_float


def _juftlik(a: Iterable, b: Iterable) -> list[tuple[float, float]]:
    """Ikkala qatorda ham qiymat bo'lsa ulaşuvchi juftlar."""
    out: list[tuple[float, float]] = []
    for x, y in zip(a, b):
        xx, yy = to_float(x), to_float(y)
        if xx is not None and yy is not None:
            out.append((xx, yy))
    return out


def pearson(juftlar: list[tuple[float, float]]) -> dict[str, Any]:
    """Pearson korrelyatsiya koeffitsienti (n ≥ 3 talab)."""
    n = len(juftlar)
    if n < 3:
        return {"n": n, "r": None, "xato": "kamida 3 juft kerak"}
    mx = sum(p[0] for p in juftlar) / n
    my = sum(p[1] for p in juftlar) / n
    sxy = sum((p[0] - mx) * (p[1] - my) for p in juftlar)
    sx = math.sqrt(sum((p[0] - mx) ** 2 for p in juftlar))
    sy = math.sqrt(sum((p[1] - my) ** 2 for p in juftlar))
    if sx == 0 or sy == 0:
        return {"n": n, "r": None, "xato": "o'zgarishsiz qator"}
    return {"n": n, "r": round(sxy / (sx * sy), 4), "xato": None}


def sektor_tarkibi(ustunlar: dict[str, Iterable], winds: Iterable,
                   markaz: float, kenglik: float = 45.0) -> dict[str, Any]:
    """Har bir modda uchun: sektorda o'rt., tashqarida o'rt., ortiqcha, lift, n."""
    w = [to_float(x) for x in winds]
    natija: dict[str, Any] = {"sektor": {"markaz": markaz, "kenglik": kenglik}, "moddalar": {}}
    for nom, seriya in ustunlar.items():
        ichida: list[float] = []
        tashqarida: list[float] = []
        for v, ww in zip(seriya, w):
            vv = to_float(v)
            if vv is None or ww is None:
                continue
            (ichida if angle_diff(ww, markaz) <= kenglik else tashqarida).append(vv)
        if not ichida or not tashqarida:
            natija["moddalar"][nom] = {"xato": "ma'lumot yetarli emas"}
            continue
        oi = sum(ichida) / len(ichida)
        ot = sum(tashqarida) / len(tashqarida)
        natija["moddalar"][nom] = {
            "n_sektor": len(ichida), "n_tashqari": len(tashqarida),
            "ort_sektor": round(oi, 2), "ort_tashqari": round(ot, 2),
            "ortiqcha": round(oi - ot, 2),
            "lift": round(oi / ot, 2) if ot else None,
        }
    return natija


def nisbat_belgisi(pm25_sektor: float, pm10_sektor: float, pm25_fon: float, pm10_fon: float) -> dict[str, Any]:
    """PM2,5/PM10 nisbati — zarra o'lchami belgisi (yonish ↔ chang)."""
    for q in (pm25_sektor, pm10_sektor, pm25_fon, pm10_fon):
        if q < 0:
            raise ValueError("konsentratsiya manfiy bo'lmaydi")
    if pm10_sektor <= 0 or pm10_fon <= 0:
        raise ValueError("PM10 nolga teng bo'lishi mumkin emas")
    n_s = pm25_sektor / pm10_sektor
    n_f = pm25_fon / pm10_fon
    if n_s >= 0.6:
        xulosa = "sektorda nozik zarra ustun — yonish/ikkilamchi aerozol belgisi"
    elif n_s >= 0.3:
        xulosa = "aralash (chang + yonish)"
    else:
        xulosa = "sektorda yirik zarra ustun — mexanik chang belgisi"
    return {"nisbat_sektor": round(n_s, 3), "nisbat_fon": round(n_f, 3),
            "farq": round(n_s - n_f, 3), "xulosa": xulosa,
            "eshik": "≥0,6 yonish/ikkilamchi · 0,3–0,6 aralash · <0,3 chang"}


def chang_ulushi(pm10: Iterable, chang: Iterable) -> dict[str, Any]:
    """PM10 ning qanchasi CAMS chang (`dust`) komponenti (o'rtacha, foizda)."""
    juft = _juftlik(pm10, chang)
    if not juft:
        return {"xato": "juft ma'lumot yo'q"}
    pm = sum(p[0] for p in juft) / len(juft)
    ch = sum(p[1] for p in juft) / len(juft)
    ulush = (ch / pm * 100.0) if pm else None
    return {"n": len(juft), "pm10_ort": round(pm, 2), "chang_ort": round(ch, 2),
            "ulush_foiz": round(ulush, 1) if ulush is not None else None,
            "izoh": "chang ulushi yuqori bo'lsa PM10 mexanik kelib chiqishi ehtimoli katta"}


def harorat_bogliqlik(pm25: Iterable, harorat: Iterable) -> dict[str, Any]:
    """PM2,5 ↔ harorat korrelyatsiyasi (isitish signali sinovi)."""
    r = pearson(_juftlik(pm25, harorat))
    if r["r"] is None:
        return {**r, "xulosa": "hisoblanmadi"}
    rr = r["r"]
    if rr <= -0.3:
        xulosa = "kuchli manfiy — **isitish (qish) signali**"
    elif rr <= -0.1:
        xulosa = "kuchsiz manfiy — qisman mavsumiy ta'sir"
    elif rr < 0.1:
        xulosa = "bog'liqlik yo'q — isitish bilan izohlanmaydi"
    else:
        xulosa = "musbat — issiq davr manbasi (ikkilamchi aerozol / foto-kimyo) belgisi"
    return {**r, "xulosa": xulosa}


def mass_rekonstruksiya(kuzatuv_ortiqcha: float, model_birlamchi: float) -> dict[str, Any]:
    """Modellashtirilgan birlamchi zarra kuzatuv ortiqchasining necha foizini beradi."""
    if kuzatuv_ortiqcha <= 0:
        raise ValueError("kuzatuv ortiqchasi musbat bo'lishi kerak")
    if model_birlamchi < 0:
        raise ValueError("model qiymati manfiy bo'lmaydi")
    ulush = model_birlamchi / kuzatuv_ortiqcha * 100.0
    if ulush >= 60:
        xulosa = "birlamchi zarra yetarli — manba gaz yonishi bo'lishi mumkin"
    elif ulush >= 20:
        xulosa = "qisman tushuntiradi — qo'shimcha manba kerak"
    else:
        xulosa = ("**birlamchi zarra tushuntirmaydi** — ikkilamchi aerozol yoki boshqa manba "
                  "(sement, grunt, transport) ehtimoli katta")
    return {"kuzatuv_ortiqcha": kuzatuv_ortiqcha, "model_birlamchi": model_birlamchi,
            "ulush_foiz": round(ulush, 1), "qoplovchi_emas": round(100 - ulush, 1), "xulosa": xulosa}


def oylik_korinish(times: Iterable[str], qiymatlar: Iterable) -> list[dict[str, Any]]:
    """Oylik o'rtacha jadval (vaqt belgisi `YYYY-MM-DDTHH:MM`)."""
    yig: dict[str, list[float]] = {}
    for t, v in zip(times, qiymatlar):
        vv = to_float(v)
        if vv is None or not t:
            continue
        oy = t[:7]
        yig.setdefault(oy, []).append(vv)
    return [{"oy": oy, "n": len(v), "ort": round(sum(v) / len(v), 2)}
            for oy, v in sorted(yig.items())]


def ascii_ustun(qatorlar: list[dict[str, Any]], nom: str = "oy", kenglik: int = 40) -> str:
    """Oddiy ASCII grafik (oylik ko'rinish uchun) — chop etishda ko'rinadigan bo'lsin."""
    if not qatorlar:
        return "(ma'lumot yo'q)"
    eng = max(q["ort"] for q in qatorlar)
    satrlar = [f"  {nom:<8}{'o\u2019rt':>7}  grafik"]
    for q in qatorlar:
        uzun = int(round(q["ort"] / eng * kenglik)) if eng else 0
        satrlar.append(f"  {q['oy']:<8}{q['ort']:>7.2f}  {'▉' * uzun}")
    return "\n".join(satrlar)


def xulosa(tarkib: dict[str, Any], pm_nisbat: dict[str, Any], chang: dict[str, Any],
           harorat: dict[str, Any], rekon: dict[str, Any],
           chang_lift: float | None = None) -> dict[str, Any]:
    """Barcha sinovlarni bitta qarorga yig'ish (kod bilan, qo'lda emas).

    `chang_lift` — sektor ichidagi changning tashqariga nisbati (CAMS `dust`).
    Muhim: **umumiy** chang ulushi emas, **sektor nisbiy** changi ishlatiladi — chunki
    umumiy chang yuqori bo'lsa ham, sektorda kam bo'lsa, ortiqcha chang bilan izohlanmaydi.
    """
    belgilar: list[str] = []
    if pm_nisbat.get("farq", 0) < 0.05 and pm_nisbat.get("nisbat_sektor", 0) < 0.6:
        belgilar.append("zarra spektri yonishga xos emas (yirik ulush katta)")
    if chang_lift is not None:
        if chang_lift >= 1.15:
            belgilar.append(f"sektorda chang ko'proq (lift {chang_lift}) — mexanik manba ehtimoli")
        elif chang_lift <= 0.9:
            belgilar.append(f"sektorda chang **kamroq** (lift {chang_lift}) — ortiqcha chang bilan "
                            "izohlanmaydi")
    elif chang.get("ulush_foiz") is not None and chang["ulush_foiz"] >= 40:
        belgilar.append(f"umumiy chang ulushi {chang['ulush_foiz']}% — lekin sektor nisbiy sinovi "
                        "kerak (umumiy ulush sabab ko'rsatmaydi)")
    if (harorat.get("r") or 0) >= 0.1:
        belgilar.append("harorat bilan musbat bog'liqlik — issiq davr/ikkilamchi jarayon")
    if rekon.get("ulush_foiz", 100) < 20:
        belgilar.append(f"birlamchi zarra hissasi {rekon.get('ulush_foiz')}% — gaz yonishi yetarli emas")
    if not belgilar:
        belgilar.append("belgilar aralash — qo'shimcha o'lchov (kimyoviy tarkib) kerak")
    return {"belgilar": belgilar,
            "daraja": "kuzatuvga asoslangan (o'lchov emas)",
            "eslatma": "Xulosa model komponentlari + mahalliy nisbatlarga tayanadi; kimyoviy tahlil "
                       "(nitrat/sulfat/EC) bo'lmasa «isbot» emas, «ko'rsatkich»."}
