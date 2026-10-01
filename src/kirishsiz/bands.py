# -*- coding: utf-8 -*-
"""Pastdan yuqoriga oraliq hisobi — ochiq faoliyat ma'lumotidan kutilgan tashlanma oraliqi.

Manba: EMEP/EEA Guidebook 2023, 2.A.1 (sement ishlab chiqarish):
  EF[tashlanma, t kl] = ELV[mg/Nm³] × EG[Nm³/t kl]      (7-formula)
  EF[tashlanma, t sement] = EF × CF,  CF = klinker ulushi
  o'rtacha: EG = 2 300 Nm³/t klinker · CF = 0.90 (default)
  https://www.eea.europa.eu/publications/emep-eea-guidebook-2023

Model (TZ-1 §4.5 «noma'lum kattaliklar» ruhida):
  E = A × EF × (1 − η)
    A  — faoliyat (t kl/yil, t sement/yil, m³ gaz/yil, …)
    EF — solishtirma koeffitsient [kg/t] yoki [kg/m³]
    η  — ushlash/boshqaruv samarasi [0…1] (noma'lum bo'lsa 0, lekin oraliq kengayadi)

Chiqish — **oraliq**, bitta «aniq» raqam emas: EF past/yuqori va η past/yuqori
qiymatlaridan min/max olinadi. Hisobot qiymati shu oraliqqa sig'masa — «mos emas» signali.

MUHIM: bu **skrining**, isbot emas. Oraliq kengligi ±30–100% bo'lishi normal;
oraliq `chegarada` zonasiga tushsa, xulosa chiqarilmaydi (registry.conclusion_rule).
"""
from __future__ import annotations

import math
from typing import Any

# EMEP/EEA 2023, 2.A.1 — standart konversiya qiymatlari
DEFAULT_GAS_NM3_PER_T_CLINKER = 2300.0
DEFAULT_CLINKER_FACTOR = 0.90

# SanQvaM 0053-23 (PM2.5 35 µg/m³) — bu modulda ishlatilmaydi, screener'da
EVIDENCE_LEVELS = {
    "band_ichida": "hisobot oraliqqa sig'adi — qo'shimcha tekshiruvga asos yo'q",
    "chegarada": "oraliq chetida — xulosa yo'q, o'lchov talab qilinadi",
    "banddan_tashqarida": "hisobot oraliqqa sig'maydi — keyingi tekshiruv uchun asos",
}


def elv_to_ef(
    elv_mg_nm3: float,
    gas_nm3_per_t_clinker: float = DEFAULT_GAS_NM3_PER_T_CLINKER,
    clinker_factor: float = DEFAULT_CLINKER_FACTOR,
    per: str = "t_sement",
) -> float:
    """Normativ chegara qiymati (ELV, mg/Nm³) → solishtirma koeffitsient (kg/t).

    EF[mg/t kl] = ELV[mg/Nm³] × EG[Nm³/t kl]
    EF[kg/t sement] = EF[mg/t kl] × CF / 1e6
    """
    if elv_mg_nm3 < 0 or gas_nm3_per_t_clinker <= 0 or not (0 < clinker_factor <= 1):
        raise ValueError("ELV ≥ 0, gaz hajmi > 0, klinker ulushi (0;1] bo'lishi shart")
    ef_mg_per_t_clinker = elv_mg_nm3 * gas_nm3_per_t_clinker
    if per == "t_klinker":
        return ef_mg_per_t_clinker / 1e6
    if per == "t_sement":
        return ef_mg_per_t_clinker * clinker_factor / 1e6
    raise ValueError("per: 't_sement' yoki 't_klinker'")


def expected_band(
    activity: float,
    ef_low: float,
    ef_high: float,
    control_low: float = 0.0,
    control_high: float = 0.0,
) -> dict[str, Any]:
    """Kutilgan yillik tashlanma oraliqi (faoliyat bilan bir xil birlikda).

    E = A × EF × (1 − η). Oraliq = [A·EF_low·(1−η_high), A·EF_high·(1−η_low)].
    η — ushlash samarasi (0 = ushlanmaydi). η_high > η_low bo'lsa past chegara kichrayadi.
    """
    if activity < 0:
        raise ValueError("faoliyat manfiy bo'lmaydi")
    if ef_low < 0 or ef_high < 0 or ef_high < ef_low:
        raise ValueError("0 ≤ ef_low ≤ ef_high bo'lishi shart")
    for eta, nom in ((control_low, "control_low"), (control_high, "control_high")):
        if not 0 <= eta < 1:
            raise ValueError(f"{nom} [0;1) oralig'ida bo'lishi shart")
    if control_high < control_low:
        raise ValueError("control_low ≤ control_high bo'lishi shart")

    low = activity * ef_low * (1 - control_high)
    high = activity * ef_high * (1 - control_low)
    mid = math.sqrt(max(low * high, 0.0)) if low > 0 and high > 0 else (low + high) / 2
    return {
        "past": round(low, 6),
        "yuqori": round(high, 6),
        "orta_geometrik": round(mid, 6),
        "kenglik_foiz": round((high - low) / mid * 100, 1) if mid > 0 else None,
        "formula": "E = A × EF × (1 − η)",
        "ogohlantirish": ("Oraliq keng (±100% dan ko'p) — yakka xulosa uchun yaroqsiz"
                          if mid > 0 and (high - low) / mid > 1.0 else None),
    }


def check_reported(reported: float, band: dict[str, Any], near_factor: float = 1.5) -> dict[str, Any]:
    """Hisobot qiymatini oraliqqa solishtirish.

    Qaytaradi: nisbat (hisobot / oraliq o'rtasi), xulosa, izoh.
    `near_factor` — «chegarada» zonasi kengligi (oraliq chegarasidan ×1,5 gacha).
    """
    if reported < 0:
        raise ValueError("hisobot qiymati manfiy bo'lmaydi")
    low, high, mid = band["past"], band["yuqori"], band["orta_geometrik"]
    if mid <= 0:
        raise ValueError("oraliq nolga teng — EF yoki faoliyat noldan farq qilishi kerak")

    ratio = reported / mid
    if low <= reported <= high:
        level, verdict = "band_ichida", "mos"
    elif low / near_factor <= reported <= high * near_factor:
        level, verdict = "chegarada", "chegarada — xulosa yo'q"
    elif reported < low:
        level, verdict = "banddan_tashqarida", "past — hisobot kutilganidan kam"
    else:
        level, verdict = "banddan_tashqarida", "yuqori — hisobot kutilganidan ko'p"

    return {
        "hisobot": reported,
        "oraliq": [low, high],
        "nisbat": round(ratio, 3),
        "daraja": level,
        "xulosa": verdict,
        "izoh": EVIDENCE_LEVELS[level],
        "chegara_zonasi": f"×{near_factor}",
        "eslatma": "Bu skrining: faoliyat ma'lumoti va koeffitsient noaniqligi bor — "
                   "«banddan_tashqarida» = keyingi tekshiruvga asos, ayblov emas.",
    }


def band_from_elv(
    activity: float,
    elv_low_mg_nm3: float,
    elv_high_mg_nm3: float,
    elv_reported_mg_nm3: float | None = None,
    control_low: float = 0.0,
    control_high: float = 0.0,
    per: str = "t_sement",
) -> dict[str, Any]:
    """Tayyor zanjir: ELV [mg/Nm³] → EF [kg/t] → oraliq → (ixtiyoriy) hisobotni tekshirish.

    `elv_low/high` — normativ-oraliq (masalan milliy ELV va eng yaxshi texnika ELV).
    """
    ef_low = elv_to_ef(elv_low_mg_nm3, per=per)
    ef_high = elv_to_ef(elv_high_mg_nm3, per=per)
    band = expected_band(activity, ef_low, ef_high, control_low, control_high)
    out = {
        "faoliyat": activity,
        "per": per,
        "ef_kg_per_birlik": [round(ef_low, 5), round(ef_high, 5)],
        "oraliq": band,
        "manba": "EMEP/EEA Guidebook 2023, 2.A.1 (EG=2 300 Nm³/t kl, CF=0,90)",
    }
    if elv_reported_mg_nm3 is not None:
        # korxona hisobot o'lchovi (mg/Nm³) → yillik massa (gaz hajmi orqali)
        ef_rep = elv_to_ef(elv_reported_mg_nm3, per=per)
        reported = activity * ef_rep * (1 - (control_low + control_high) / 2)
        out["hisobot_bahosi"] = round(reported, 6)
        out["tekshiruv"] = check_reported(reported, band)
    return out
