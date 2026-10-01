# -*- coding: utf-8 -*-
"""Sun'iy yo'ldosh / havo o'lchovidan manba quvvatini baholash + atributsiya.

Usullar (manba: Varon et al., 2018, Atmos. Meas. Tech. 11(10):5673–5686,
DOI 10.5194/amt-11-5673-2018; umumiy ko'rinishi NIST IR 8575, 2025):
  · **CSF** (cross-section flux): Q = Σ ΔΩ_i · U · Δx_i  (qatlam og'izlari yig'indisi)
  · **IME** (integrated mass enhancement): Q = IME / τ,  τ = L / U_eff
  · Detection limit (tartib bahosi): Q_min ≈ snr · σ_Ω · U · W  (bir hujayra, 3σ)

Modul **o'lchov birliklarini** ham boshqaradi: mol/m² → kg/m² (modda molyar massasi orqali),
kg/s → t/yil (yillik normasiga keltirish; sun'iy yo'ldosh «lahzalik surat» ekanini yozib qo'yadi).

Chegara: bu baho **manba quvvati**, konsentratsiya emas; t/yilga o'tkazishda persistensiya
(manbaning doimiyligi) tuzatmasisiz xato katta bo'ladi (Cusworth et al., 2021 yondashuvi).
"""
from __future__ import annotations

import math
from typing import Any, Iterable

MOLAR_MASS_G = {"NO2": 46.0055, "SO2": 64.066, "CH4": 16.043, "CO": 28.010, "CO2": 44.009}
SECONDS_PER_YEAR = 365.25 * 24 * 3600


def mol_to_kg(mol_per_m2: float, substance: str) -> float:
    """mol/m² (yoki mol) → kg/m² (yoki kg) — molyar massa orqali."""
    if substance not in MOLAR_MASS_G:
        raise KeyError(f"modda noma'lum: {substance} (mavjud: {', '.join(MOLAR_MASS_G)})")
    return mol_per_m2 * MOLAR_MASS_G[substance] / 1000.0


def csf_flux(enhancements_kg_m2: Iterable[float], wind_ms: float, dx_m: float) -> dict[str, Any]:
    """Kesim oqimi (CSF): Q = Σ ΔΩ_i · U · Δx_i, kg/s.

    `enhancements_kg_m2` — kesim bo'ylab fon ayirilgan qatlam og'ishlari (kg/m²),
    `dx_m` — har bir element uzunligi (hujayra o'lchami bo'ylab).
    """
    if wind_ms <= 0 or dx_m <= 0:
        raise ValueError("shamol > 0 va dx > 0 bo'lishi shart")
    vals = [float(v) for v in enhancements_kg_m2]
    if not vals:
        raise ValueError("bo'sh kesim")
    if any(v < 0 for v in vals):
        raise ValueError("manfiy og'ish — fon ayirish xatosini tekshiring")
    q = sum(vals) * wind_ms * dx_m
    return {
        "q_kg_s": q,
        "yigindi_kg_m2": sum(vals),
        "element_soni": len(vals),
        "shamol_ms": wind_ms,
        "dx_m": dx_m,
        "formula": "Q = Σ ΔΩ_i · U · Δx_i",
        "manba": "Varon et al. 2018 (AMT 11:5673), CSF usuli",
    }


def ime_flux(
    ime_kg: float,
    wind_ms: float,
    plume_length_m: float,
    u_eff_factor: float = 1.0,
) -> dict[str, Any]:
    """Integral mass enhancement (IME): Q = IME / τ, τ = L / U_eff.

    `u_eff_factor` — U_eff = factor × U_10. Varon et al. (2018) U_eff ni LES orqali
    bog'laydi; bu modulda **ehtiyotkor default 1,0** (tuzatish kiritilmagan) qabul qilingan —
    qiymat o'zgartirilsa, xato ham shunga mos o'zgaradi.
    """
    if ime_kg < 0 or wind_ms <= 0 or plume_length_m <= 0:
        raise ValueError("IME ≥ 0, shamol > 0, uzunlik > 0 bo'lishi shart")
    if u_eff_factor <= 0:
        raise ValueError("u_eff_factor > 0")
    u_eff = wind_ms * u_eff_factor
    tau_s = plume_length_m / u_eff
    q = ime_kg / tau_s
    return {
        "q_kg_s": q,
        "tau_s": round(tau_s, 1),
        "u_eff_ms": round(u_eff, 3),
        "u_eff_factor": u_eff_factor,
        "formula": "Q = IME / τ, τ = L / U_eff",
        "eslatma": "U_eff tuzatmasi kiritilmagan (1,0) — xato ±30–60% oralig'ida qoladi.",
    }


def detection_limit_kg_s(
    wind_ms: float,
    pixel_m: float,
    noise_kg_m2: float,
    snr: float = 3.0,
) -> dict[str, Any]:
    """Sezish chegarasi tartib bahosi: Q_min ≈ snr · σ_Ω · U · W (bir hujayra).

    Manba: Jacob et al. (2016) / NIST IR 8575 dagi Q_min g'oyasi; bu yerda soddalashtirilgan,
    lekin **formula ochiq** — qiymat «nima uchun shunday» ekanini tekshirish mumkin.
    """
    if wind_ms <= 0 or pixel_m <= 0 or noise_kg_m2 <= 0 or snr <= 0:
        raise ValueError("barcha argumentlar > 0")
    q_min = snr * noise_kg_m2 * wind_ms * pixel_m
    return {
        "q_min_kg_s": q_min,
        "q_min_t_kun": q_min * 86400 / 1000,
        "shartlar": {"shamol_ms": wind_ms, "pixel_m": pixel_m, "shovqin_kg_m2": noise_kg_m2, "snr": snr},
        "izoh": "Shamol kuchayganda va hujayra yiriklashganda sezish chegarasi o'sadi "
                "(Varon 2018 · Nature 2025: GHGSat ~100 kg/soat chegarasi).",
    }


def annualise(q_kg_s: float, ish_soati: float = 8760.0, persistensiya: float = 1.0) -> dict[str, Any]:
    """kg/s → t/yil. `persistensiya` — manba doimiylik ulushi (0…1).

    Sun'iy yo'ldosh bir lahzalik surat: bir martalik o'lchovni yilga ko'chirish uchun
    persistensiya tuzatmasi kerak (Cusworth et al., 2021 uslubi).
    """
    if q_kg_s < 0 or ish_soati <= 0 or not 0 < persistensiya <= 1:
        raise ValueError("q ≥ 0, soat > 0, persistensiya (0;1]")
    t = q_kg_s * ish_soati * 3600 / 1000 * persistensiya
    return {
        "t_yil": t,
        "persistensiya": persistensiya,
        "ish_soati": ish_soati,
        "eslatma": "Persistensiya 1,0 = «manba yil bo'yi shunday ishlaydi» degan eng yuqori baho.",
    }


# ------------------------------------------------------------------ atributsiya


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Ikki nuqta orasidagi masofa (m), WGS-84 o'rtacha radiusi bilan."""
    r = 6371008.8
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """1-nuqtadan 2-nuqtaga boshlang'ich azimut (0° = shimol, soat strelkasi bo'ylab)."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return (math.degrees(math.atan2(y, x)) + 360) % 360


def angle_diff(a_deg: float, b_deg: float) -> float:
    """Ikki azimut orasidagi eng kichik burchak (0…180°)."""
    d = abs((a_deg - b_deg) % 360)
    return min(d, 360 - d)


def attribute_candidates(
    receptor_lat: float,
    receptor_lon: float,
    wind_from_deg: float,
    candidates: list[dict[str, Any]],
    max_angle_deg: float = 45.0,
    max_km: float = 30.0,
) -> dict[str, Any]:
    """Shamol manbadan esayotgan bo'lsa, nomzod obyektlar «yuqori tomon»da bo'lishi kerak.

    `candidates` — [{"nom": ..., "lat": ..., "lon": ...}, …] (ochiq reyestr).
    Har bir nomzod uchun azimut va masofa hisoblanadi; `|azimut − shamol_from| ≤ max_angle`
    bo'lsa — «mos». Natija — **tartiblangan nomzodlar ro'yxati**, xulosa emas.
    """
    if not 0 <= max_angle_deg <= 180:
        raise ValueError("max_angle_deg 0…180")
    out = []
    for c in candidates:
        b = bearing_deg(receptor_lat, receptor_lon, c["lat"], c["lon"])
        d_km = haversine_m(receptor_lat, receptor_lon, c["lat"], c["lon"]) / 1000
        err = angle_diff(b, wind_from_deg)
        out.append({
            "nom": c.get("nom", "?"),
            "azimut": round(b, 1),
            "masofa_km": round(d_km, 2),
            "burchak_xatosi": round(err, 1),
            "mos": err <= max_angle_deg and d_km <= max_km,
            "sabab": ("yuqori tomonda va masofa ichida" if err <= max_angle_deg and d_km <= max_km
                      else ("yo'nalish mos emas" if err > max_angle_deg else f"juda uzoq (>{max_km:g} km)")),
        })
    out.sort(key=lambda x: (not x["mos"], x["burchak_xatosi"], x["masofa_km"]))
    return {
        "shamol_from": wind_from_deg,
        "mezon": f"burchak ≤ {max_angle_deg:g}° va masofa ≤ {max_km:g} km",
        "nomzodlar": out,
        "mos_soni": sum(1 for x in out if x["mos"]),
        "izoh": "Nomzod = «yuqori tomon»dagi obyekt. Bu atributsiya emas: bir nechta manba bir yo'nalishda "
                "bo'lsa ajratilmaydi (isbot kuchi 2).",
    }
