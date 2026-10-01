# -*- coding: utf-8 -*-
"""Yo'l #2 — pastdan yuqoriga (bottom-up) oqim hisobi va uning haqiqat bilan solishtiruvi.

Zanjir: **ishlab chiqarish (faoliyat) × koeffitsient (EF) → yillik tashlanma → oqim (kg/s) →
Gauss dispersiyasi → kutilgan konsentratsiya → jonli ekran bilan solishtirish**.

Koeffitsient manbasi (ochiq, tekshiriladigan):
  • EPA AP-42 §3.1 «Stationary Gas Turbines», Table 3.1-1 — tabiiy gaz turbinalari uchun
    NOx: 0,32 lb/MMBtu (nazoratsiz) va 0,13 lb/MMBtu (bug'/suv quyish bilan). 1 lb/MMBtu = 430 g/GJ.
  • EPA NSPS chiqish standarti: yangi turbinalar uchun 2,3 lb/MWh ≈ **1,04 g/kWh** (yuqori chegara).
  • EMEP/EEA Guidebook 2023, 1.A.1 «Energy industries» — uslub va Tier 1/Tier 2 yondashuvi.

Disperisiya: Briggs σ_y/σ_z formulalari (qishloq va shahar rejimlari), yerdan aks ettirish bilan
Gauss yechimi:  C = Q / (π · u · σ_y · σ_z).

Nima isbotlanadi: pastdan hisoblangan oqim kuzatilgan yo'nalish effektini **miqyos bo'yicha**
tushuntira oladimi (tartib kattaligi tekshiruvi).
Nima isbotlanmaydi: qaysi obyekt; EF real qurilma ko'rsatkichi emas (nazoratsiz/stabil holat oralig'i);
bitta o'rtacha shamol tezligi bilan butun oyna tavsiflanmaydi; fon va boshqa manbalar ajratilmaydi.
"""
from __future__ import annotations

import math
from typing import Any, Iterable

# AP-42 3.1-1 (lb/MMBtu → g/GJ): 1 lb = 453,592 g · 1 MMBtu = 1,055056 GJ
LB_PER_MMBTU_TO_G_PER_GJ = 453.59237 / 1.05505585262          # ≈ 429,9

# Briggs σ koeffitsientlari: (a, b, c, d) → σ = a·x·(1+b·x)^c   [x, m]
BRIGGS_QISHLOQ = {
    "A": (0.22, 0.0001, -0.5),
    "B": (0.16, 0.0001, -0.5),
    "C": (0.11, 0.0001, -0.5),
    "D": (0.08, 0.0001, -0.5),
    "E": (0.06, 0.0001, -0.5),
    "F": (0.04, 0.0001, -0.5),
}
BRIGGS_SIGMA_Z = {
    "A": lambda x: 0.20 * x,
    "B": lambda x: 0.12 * x,
    "C": lambda x: 0.08 * x * (1 + 0.0002 * x) ** -0.5,
    "D": lambda x: 0.06 * x * (1 + 0.0015 * x) ** -1,
    "E": lambda x: 0.03 * x * (1 + 0.0003 * x) ** -1,
    "F": lambda x: 0.016 * x * (1 + 0.0003 * x) ** -1,
}
# Shahar rejimi (Briggs, urban) — qo'shimcha variant
BRIGGS_SHAHAR = {
    "A_B": (0.32, 0.0004, -0.5),
    "C": (0.22, 0.0004, -0.5),
    "D": (0.16, 0.0004, -0.5),
    "E_F": (0.11, 0.0004, -0.5),
}
BRIGGS_SHAHAR_Z = {"A_B": lambda x: 0.24 * x * (1 + 0.001 * x) ** 0.5,
                   "C": lambda x: 0.20 * x,
                   "D": lambda x: 0.14 * x * (1 + 0.0003 * x) ** -0.5,
                   "E_F": lambda x: 0.08 * x * (1 + 0.0015 * x) ** -0.5}


def lb_per_mmbtu_to_g_per_gj(qiymat: float) -> float:
    """AP-42 birligini (lb/MMBtu) EMEP/EEA uslubiga (g/GJ) o'tkazish."""
    if qiymat <= 0:
        raise ValueError("koeffitsient musbat bo'lishi kerak")
    return qiymat * LB_PER_MMBTU_TO_G_PER_GJ


def g_per_gj_to_g_per_kwh(ef_g_per_gj: float, foydali_fik: float) -> float:
    """Yoqilg'i asosidagi koeffitsientni **chiqish** asosiga o'tkazish: g/GJ → g/kWh.

    1 kWh elektr = 3,6 MJ = 0,0036 GJ *foydali* energiya; FIK η bo'lsa yoqilg'i energiyasi
    0,0036/η GJ. Shuning uchun: EF[g/kWh] = EF[g/GJ] · 0,0036 / η.
    Nazorat: 137,6 g/GJ (0,32 lb/MMBtu) va η = 35% → 1,42 g NOx/kWh.
    """
    if not 0 < foydali_fik <= 1:
        raise ValueError("foydali FIK 0 va 1 oralig'ida bo'lishi kerak")
    return ef_g_per_gj * 0.0036 / foydali_fik


def annual_tonnes(generation_twh: float, ef_g_per_kwh: float) -> float:
    """Yillik tashlanma, tonna: ishlab chiqarish (TWh) × koeffitsient (g/kWh)."""
    if generation_twh < 0 or ef_g_per_kwh < 0:
        raise ValueError("manfiy qiymat")
    return generation_twh * 1e9 * ef_g_per_kwh / 1e6       # kWh × g/kWh / 1e6 = t


def rate_kg_s(annual_t: float, hours: float = 8760.0) -> float:
    """Yillik massani o'rtacha oqimga aylantirish (kg/s)."""
    if annual_t < 0 or hours <= 0:
        raise ValueError("noto'g'ri qiymat")
    return annual_t * 1e3 / (hours * 3600.0)


def briggs_sigma(x_m: float, stability: str = "D", urban: bool = False) -> tuple[float, float]:
    """Briggs bo'yicha σ_y va σ_z (m). Stability: A (juda beqaror) … F (barqaror)."""
    if x_m <= 0:
        raise ValueError("masofa musbat bo'lishi kerak")
    st = stability.upper()
    if urban:
        kalit = {"A": "A_B", "B": "A_B", "C": "C", "D": "D", "E": "E_F", "F": "E_F"}.get(st)
        if kalit is None:
            raise ValueError(f"noma'lum barqarorlik: {stability}")
        a, b, c = BRIGGS_SHAHAR[kalit]
        sigma_y = a * x_m * (1 + b * x_m) ** c
        return sigma_y, BRIGGS_SHAHAR_Z[kalit](x_m)
    if st not in BRIGGS_QISHLOQ:
        raise ValueError(f"noma'lum barqarorlik: {stability}")
    a, b, c = BRIGGS_QISHLOQ[st]
    sigma_y = a * x_m * (1 + b * x_m) ** c
    return sigma_y, BRIGGS_SIGMA_Z[st](x_m)


def gaussian_ground_conc(q_kg_s: float, u_ms: float, x_m: float, sigma_y: float,
                         sigma_z: float, h_eff_m: float = 0.0) -> dict[str, Any]:
    """O'q chizig'idagi yer usti konsentratsiyasi (Gauss, yerdan aks ettirish bilan).

    h_eff > 0 → samarali mo'ri balandligi;  C = Q/(π·u·σy·σz) · exp(−h²/2σz²)
    Qaytadi: µg/m³ (SO2/NOx massasi sifatida).
    """
    if q_kg_s < 0 or u_ms <= 0 or x_m <= 0 or sigma_y <= 0 or sigma_z <= 0:
        raise ValueError("noto'g'ri kirish")
    c = q_kg_s / (math.pi * u_ms * sigma_y * sigma_z)
    if h_eff_m:
        c *= math.exp(-(h_eff_m ** 2) / (2 * sigma_z ** 2))
    return {"ug_m3": c * 1e9, "q_kg_s": q_kg_s, "u_ms": u_ms, "x_km": x_m / 1000.0,
            "sigma_y": round(sigma_y, 1), "sigma_z": round(sigma_z, 1), "h_eff_m": h_eff_m}


def dispersion_table(q_kg_s: float, x_m: float, shamollar: Iterable[float] = (1.0, 2.0, 4.0, 8.0),
                     barqarorliklar: Iterable[str] = ("B", "D", "F"),
                     h_eff_m: float = 0.0, urban: bool = True) -> list[dict[str, Any]]:
    """Turlicha ob-havo sharoitida kutilgan konsentratsiya jadvali (sezgirlik)."""
    out = []
    for st in barqarorliklar:
        sy, sz = briggs_sigma(x_m, st, urban=urban)
        for u in shamollar:
            r = gaussian_ground_conc(q_kg_s, u, x_m, sy, sz, h_eff_m)
            out.append({"barqarorlik": st, "shamol_ms": u, **{k: r[k] for k in ("ug_m3", "sigma_y", "sigma_z")}})
    return out


def bottom_up(generation_twh: float, ef_low_g_per_kwh: float, ef_high_g_per_kwh: float,
              masofa_km: float, shamol_ms: float = 4.0, barqarorlik: str = "D",
              h_eff_m: float = 0.0, urban: bool = True) -> dict[str, Any]:
    """To'liq zanjir: ishlab chiqarish → tashlanma oralig'i → oqim → kutilgan konsentratsiya."""
    if ef_low_g_per_kwh > ef_high_g_per_kwh:
        raise ValueError("EF oralig'i teskarisi")
    yillik = {nom: annual_tonnes(generation_twh, ef) for nom, ef in
              (("past", ef_low_g_per_kwh), ("yuqori", ef_high_g_per_kwh))}
    olcham = {nom: rate_kg_s(v) for nom, v in yillik.items()}
    sy, sz = briggs_sigma(masofa_km * 1000.0, barqarorlik, urban=urban)
    kons = {nom: gaussian_ground_conc(q, shamol_ms, masofa_km * 1000.0, sy, sz, h_eff_m)
            for nom, q in olcham.items()}
    return {
        "kirish": {"ishlab_chiqarish_twh": generation_twh, "ef_g_per_kwh": [ef_low_g_per_kwh, ef_high_g_per_kwh],
                   "masofa_km": masofa_km, "shamol_ms": shamol_ms, "barqarorlik": barqarorlik,
                   "h_eff_m": h_eff_m, "shahar_rejimi": urban},
        "yillik_tonna": yillik,
        "oqim_kg_s": {k: round(v, 4) for k, v in olcham.items()},
        "kutilgan_ug_m3": {k: round(v["ug_m3"], 3) for k, v in kons.items()},
        "sigma": {"sigma_y": round(sy, 1), "sigma_z": round(sz, 1)},
        "manba": "EPA AP-42 §3.1 Table 3.1-1 (gaz turbinalari NOx) · Briggs σ formulalari · Gauss yechimi",
        "nima_isbotlanmaydi": "Qaysi obyekt; EF qurilma ko'rsatkichi emas; o'rtacha shamol butun oynani "
                              "tavsiflamaydi; fon va boshqa manbalar ajratilmaydi.",
    }


# ---------------------------------------------------------------- EMEP/EEA 2023, 1.A.1.a (Tier 1)

EMEP_EEA_2023 = {
    "manba": "EMEP/EEA air pollutant emission inventory guidebook 2023, 1.A.1.a «Public electricity "
             "and heat production», Table 3-4 (tabiiy gaz)",
    "url": "https://www.eea.europa.eu/en/analysis/publications/emep-eea-guidebook-2023/"
           "part-b-sectoral-guidance-chapters/1-energy/1-a-combustion/1-a-energy-industries-2023",
    "sana": "2023-10-02",
    "tier": "A",
    "ef": {
        "nox_g_per_gj": 89.0,        # CI 95%: 15–185
        "nox_ci": (15.0, 185.0),
        "co_g_per_gj": 39.0,         # CI 20–60
        "nmvoc_g_per_gj": 2.6,       # CI 0.65–10.4
        "sox_g_per_gj": 0.281,       # AQSh hududi; YeI 0,244
        "pm_tsp_g_per_gj": 0.14,     # «<0,14» — aniqlash chegarasidan past
        "pm10_g_per_gj": 0.14,
        "pm25_g_per_gj": 0.14,
        "pm_izoh": "«<» belgisi — o'lchov aniqlash chegarasidan past; baribir hisobda ishlatiladi",
    },
}


def emep_ef_g_per_kwh(foydali_fik: float, modda: str = "nox") -> float:
    """EMEP/EEA 2023 1.A.1.a koeffitsientini chiqish asosiga o'tkazish (g/kWh)."""
    kalit = {"nox": "nox_g_per_gj", "co": "co_g_per_gj", "nmvoc": "nmvoc_g_per_gj",
             "sox": "sox_g_per_gj", "pm25": "pm25_g_per_gj"}.get(modda)
    if kalit is None:
        raise ValueError(f"noma'lum modda: {modda}")
    return g_per_gj_to_g_per_kwh(EMEP_EEA_2023["ef"][kalit], foydali_fik)


def ef_taqqoslash(ap42_g_per_gj: tuple[float, float], emep_g_per_gj: float = 89.0) -> dict[str, Any]:
    """AP-42 oralig'i bilan EMEP/EEA bitta qiymatini solishtirish.

    Geometrik o'rtalar nisbati 10% dan kam bo'lsa — «kelishadi» deb baholanadi.
    """
    past, yuqori = ap42_g_per_gj
    if not 0 < past <= yuqori or emep_g_per_gj <= 0:
        raise ValueError("qiymatlar musbat va tartibda bo'lishi kerak")
    geo = math.sqrt(past * yuqori)
    nisbat = emep_g_per_gj / geo
    ichida = past <= emep_g_per_gj <= yuqori
    if abs(nisbat - 1.0) <= 0.10 and ichida:
        xulosa = "**kelishadi** (10% dan kam farq, EMEP qiymati AP-42 oralig'i ichida)"
    elif ichida:
        xulosa = "EMEP qiymati AP-42 oralig'i ichida, lekin markazdan uzoqroq"
    else:
        xulosa = "**kelishmaydi** — EMEP qiymati AP-42 oralig'idan tashqarida"
    return {"ap42_g_per_gj": [past, yuqori], "ap42_geo_orta": round(geo, 1),
            "emep_g_per_gj": emep_g_per_gj, "nisbat": round(nisbat, 3),
            "emep_ap42_ichida": ichida, "xulosa": xulosa,
            "manba": "AP-42 §3.1-1 (lb/MMBtu → g/GJ) · EMEP/EEA 2023 1.A.1.a Table 3-4"}


def sector_excess(values: Iterable[float | None], winds: Iterable[float | None], markaz: float,
                  kenglik: float = 45.0) -> dict[str, Any]:
    """Jonli ekrandan **yo'nalish ortiqchasi**: sektorda o'rtacha − sektordan tashqarida o'rtacha."""
    from .screener import to_float
    from .plume import angle_diff

    ichida: list[float] = []
    tashqarida: list[float] = []
    for v, w in zip(values, winds):
        vv, ww = to_float(v), to_float(w)
        if vv is None or ww is None:
            continue
        (ichida if angle_diff(ww, markaz) <= kenglik else tashqarida).append(vv)
    if not ichida or not tashqarida:
        return {"xato": "sektor yoki tashqarisida ma'lumot yo'q"}
    o_i = sum(ichida) / len(ichida)
    o_t = sum(tashqarida) / len(tashqarida)
    return {"sektor": {"markaz": markaz, "kenglik": kenglik}, "n_sektor": len(ichida),
            "n_tashqari": len(tashqarida), "ort_sektor": round(o_i, 2), "ort_tashqari": round(o_t, 2),
            "farq_ug_m3": round(o_i - o_t, 2),
            "nisbat": round(o_i / o_t, 2) if o_t else None,
            "izoh": "Yo'nalish ortiqchasi — kuzatilgan farq; sababi (obyekt, transport, uy isitish) "
                    "shu usul bilan ajratilmaydi."}


def consistency(model_ug: float, observed_ug: float, faktor_chegara: float = 3.0) -> dict[str, Any]:
    """Model va kuzatuv nisbatini baholash (tartib kattaligi tekshiruvi)."""
    if model_ug <= 0 or observed_ug <= 0:
        raise ValueError("qiymatlar musbat bo'lishi kerak")
    nisbat = observed_ug / model_ug
    if 1 / faktor_chegara <= nisbat <= faktor_chegara:
        xulosa = "mos (bir tartib kattaligida)"
    elif nisbat > faktor_chegara:
        xulosa = ("model kuzatuvdan past — sabab: noqulay dispersiya (tinch/barqaror tun), "
                  "qo'shimcha manbalar yoki past baholangan EF")
    else:
        xulosa = "model kuzatuvdan yuqori — EF ortiqcha yoki mo'ri balandligi hisobga olinmagan"
    return {"model_ug_m3": model_ug, "kuzatuv_ug_m3": observed_ug, "nisbat": round(nisbat, 2),
            "faktor_chegara": faktor_chegara, "xulosa": xulosa}

def alignment_share(winds: Iterable[float | None], markaz: float, kenglik: float = 45.0,
                    tol: float = 9.0) -> dict[str, Any]:
    """Shamol berilgan yo'nalishdan **aniq** esgan soatlar ulushi.

    Sektor (±`kenglik`) ichida shamol faqat `tol` daraja oralig'ida chindan ham manbadan
    retseptorga yo'nalgan bo'ladi — qolgan soatlarda oqim retseptordan chetga o'tadi.
    Shu sababli model qiymatini sektor o'rtachasiga aylantirish uchun bu ulush kerak.
    """
    from .plume import angle_diff
    from .screener import to_float

    sektor = 0
    mos = 0
    jami = 0
    for w in winds:
        ww = to_float(w)
        if ww is None:
            continue
        jami += 1
        if angle_diff(ww, markaz) <= kenglik:
            sektor += 1
            if angle_diff(ww, markaz) <= tol:
                mos += 1
    if not sektor:
        return {"xato": "sektorda shamol ma'lumoti yo'q", "jami_soat": jami}
    return {"markaz": markaz, "kenglik": kenglik, "tol": tol, "jami_soat": jami,
            "sektor_soat": sektor, "mos_soat": mos,
            "ulush_sektorda": round(mos / sektor, 4), "ulush_jami": round(mos / jami, 4)}


def sector_weighted_scenarios(q_kg_s: float, masofa_km: float, mos_ulush: float,
                              shamollar: Iterable[float] = (2.0, 4.0),
                              barqarorliklar: Iterable[str] = ("D",),
                              h_eff_m: float = 100.0, urban: bool = True) -> list[dict[str, Any]]:
    """Ssenariylar bo'yicha **sektor o'rtachasi** kutilgan konsentratsiya (µg/m³)."""
    if not 0 < mos_ulush <= 1:
        raise ValueError("mos ulush 0 va 1 oralig'ida bo'lishi kerak")
    out = []
    for st in barqarorliklar:
        sy, sz = briggs_sigma(masofa_km * 1000.0, st, urban=urban)
        for u in shamollar:
            aligned = gaussian_ground_conc(q_kg_s, u, masofa_km * 1000.0, sy, sz, h_eff_m)["ug_m3"]
            out.append({"barqarorlik": st, "shamol_ms": u, "aligned_ug_m3": round(aligned, 2),
                        "mos_ulush": mos_ulush, "sektor_ortacha_ug_m3": round(aligned * mos_ulush, 2)})
    return out
