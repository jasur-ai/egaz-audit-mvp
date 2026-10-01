# -*- coding: utf-8 -*-
"""S3 — Feature engineering (TZ §7: 8 guruh, 33 feature — v1.4).

Muhim: `implied_ghg` — ground truth; model uni KO'RMAYDI (aks holda baholash ma'nosiz bo'ladi).
Barcha feature'lar faqat "ko'rinadigan" ustunlardan hisoblanadi (reported_*, production, energy, offsets).

v1.4 qo'shimlari (R41 — A5/A7/A8 uchun kengaytirish, diagnostika asosida):
  * **F7 aktivlik kross-tekshiruvi** — hisobot faoliyati ↔ mustaqil statistika (production, energy).
    A5 (ishlab chiqarishni 1,18× oshirib ko'rsatish) shu yerda ko'rinadi: `prod_report_gap` ≈ +0,18.
  * **F8 quyi-dan-yuqoriga proksi** — `proxy = a + b·energy + c·production` (koeffitsiyentlar FAQAT
    train davrida, robust 2 qadamli regressiya). A1/A3/A7 uchun modeldan tashqari kross-tekshiruv;
    A8 (vaqt-aralashtirish) uchun `proxy_gap_x_growth` o'zaro ta'siri.
  * `offsets_own_dev` (tarkib) — A7: offsetlar ikki baravar → o'z tarixiga nisbatan +0,8.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

FEATURE_GROUPS = {
    "nisbat": ["log_reported", "qoq_growth_reported", "reported_to_energy"],
    "energiya": ["energy_intensity", "energy_intensity_growth", "ghg_intensity", "ghg_intensity_growth"],
    "tarkib": ["gas_share", "gas_share_growth", "offsets_share", "offsets_share_growth",
               "fugitive_ratio_change", "offsets_own_dev"],
    "dinamika": ["rolling_dev", "repeat_count", "flat_flag", "seasonal_residual", "drift_slope"],
    "aniqlik": ["drift_estimate", "jump_flag", "unit_jump_flag", "boundary_mix_flag"],
    "miqyos": ["log_production", "size_pct", "quarter_index", "energy_to_prod_dev", "reporting_volatility"],
    "aktivlik": ["prod_report_gap", "energy_report_gap"],
    "proksi": ["proxy_gap", "proxy_gap_own_dev", "proxy_growth", "proxy_gap_x_growth"],
}

# Proksi regressiyasi fit qilinadigan oxirgi davr (train chegarasi — test davri fit'ga KIRMAYDI).
TRAIN_MAX_Q = 17

FEATURES = [f for g in FEATURE_GROUPS.values() for f in g]


def fit_proxy(df: pd.DataFrame, train_max_q: int = TRAIN_MAX_Q) -> np.ndarray:
    """`proxy = a + b·energy + c·production` koeffitsiyentlari — FAQAT train davridan.

    Robust: bir marta fit → |qoldiq| > 3·MAD bo'lgan qatorlar chiqariladi → qayta fit.
    Faqat ko'rinadigan ustunlar (energy, production, reported_ghg); `implied_ghg` ishlatilmaydi.
    """
    need = {"energy", "production", "reported_ghg", "q_index"}
    if not need.issubset(df.columns):
        return np.array([0.0, 0.0, 0.0])
    tr = df["q_index"].to_numpy() <= train_max_q
    if tr.sum() < 50:                       # juda kichik namuna — proksi o'chiriladi
        return np.array([0.0, 0.0, 0.0])
    X = np.column_stack([np.ones(int(tr.sum())), df.loc[tr, "energy"].to_numpy(float),
                         df.loc[tr, "production"].to_numpy(float)])
    y = df.loc[tr, "reported_ghg"].to_numpy(float)
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ coef
    mad = np.median(np.abs(resid - np.median(resid)))
    if mad > 0:
        keep = np.abs(resid) < 3.0 * 1.4826 * mad
        if keep.sum() >= 50:
            coef, *_ = np.linalg.lstsq(X[keep], y[keep], rcond=None)
    return coef


def build_features(df: pd.DataFrame, train_max_q: int = TRAIN_MAX_Q) -> pd.DataFrame:
    d = df.sort_values(["company_id", "q_index"]).copy()
    g = d.groupby("company_id", group_keys=False)
    eps = 1e-9

    d["log_reported"] = np.log1p(d["reported_ghg"].clip(lower=0))
    d["qoq_growth_reported"] = g["reported_ghg"].pct_change().replace([np.inf, -np.inf], np.nan)
    d["reported_to_energy"] = d["reported_ghg"] / (d["reported_energy"] + eps)

    d["energy_intensity"] = d["reported_energy"] / (d["reported_production"] + eps)
    d["energy_intensity_growth"] = g["energy_intensity"].pct_change().replace([np.inf, -np.inf], np.nan)
    d["ghg_intensity"] = d["reported_ghg"] / (d["reported_production"] + eps)
    d["ghg_intensity_growth"] = g["ghg_intensity"].pct_change().replace([np.inf, -np.inf], np.nan)

    d["gas_share"] = d["gas_share_reported"]
    d["gas_share_growth"] = g["gas_share"].diff()
    d["offsets_share"] = d["offsets_reported"] / (d["reported_ghg"].abs() + eps)
    d["offsets_share_growth"] = g["offsets_share"].diff()
    d["fugitive_ratio_change"] = g["fugitive_reported"].pct_change().replace([np.inf, -np.inf], np.nan)

    roll_mean = g["reported_ghg"].transform(lambda s: s.rolling(4, min_periods=2).mean())
    d["rolling_dev"] = (d["reported_ghg"] - roll_mean) / (roll_mean.abs() + eps)
    d["repeat_count"] = g["reported_ghg"].transform(
        lambda s: s.groupby((s.diff().abs() > 1e-6).cumsum()).cumcount() + 1)
    d["flat_flag"] = (d["repeat_count"] >= 3).astype(int)
    med = g["reported_ghg"].transform(lambda s: s.rolling(4, min_periods=2).median())
    d["seasonal_residual"] = (d["reported_ghg"] - med) / (med.abs() + eps)
    d["drift_slope"] = g["reported_ghg"].transform(
        lambda s: s.rolling(4, min_periods=3).apply(
            lambda w: np.polyfit(np.arange(len(w)), w, 1)[0] / (abs(np.mean(w)) + eps), raw=True))

    roll_mean4 = g["reported_ghg"].transform(lambda s: s.rolling(4, min_periods=2).mean())
    roll_med4 = g["reported_ghg"].transform(lambda s: s.rolling(4, min_periods=2).median())
    d["drift_estimate"] = roll_mean4 / (roll_med4.abs() + eps)
    d["jump_flag"] = (d["reported_ghg"].pct_change().abs() > 0.35).astype(int)
    ratio = d["reported_ghg"] / (d["reported_ghg"].shift(1).abs() + eps)
    d["unit_jump_flag"] = ((ratio > 100) | (ratio < 0.01)).astype(int)
    d["boundary_mix_flag"] = (
        (d["q_index"] % 4 == 0) & (d["rolling_dev"].abs() > 0.15)).astype(int)

    d["log_production"] = np.log1p(d["reported_production"])
    d["size_pct"] = d["log_production"].rank(pct=True)
    d["quarter_index"] = d["q_index"]
    sec_med = d.groupby(["sector", "q_index"])["energy_intensity"].transform("median")
    d["energy_to_prod_dev"] = (d["energy_intensity"] - sec_med) / (sec_med.abs() + eps)
    d["reporting_volatility"] = g["reported_ghg"].transform(lambda s: s.rolling(4, min_periods=2).std()) / \
        (g["reported_ghg"].transform(lambda s: s.rolling(4, min_periods=2).mean()).abs() + eps)

    # ---- F7: aktivlik kross-tekshiruvi (hisobot ↔ mustaqil statistika) ----
    # eps taqsimlagichda qoladi (nolga bo'linishdan himoya), lekin hisobot == statistika
    # bo'lgan qatorda natija aniq 0 bo'lishi kerak (float shovqini qoida chegarasini buzmasin)
    pr = d["reported_production"].to_numpy(float) / (d["production"].to_numpy(float) + eps) - 1.0
    er = d["reported_energy"].to_numpy(float) / (d["energy"].to_numpy(float) + eps) - 1.0
    d["prod_report_gap"] = np.where(np.isclose(d["reported_production"], d["production"]), 0.0, pr)
    d["energy_report_gap"] = np.where(np.isclose(d["reported_energy"], d["energy"]), 0.0, er)

    # ---- F8: quyi-dan-yuqoriga proksi (train koeffitsiyentlari) ----
    coef = fit_proxy(df, train_max_q=train_max_q)
    proxy = coef[0] + coef[1] * d["energy"] + coef[2] * d["production"]
    proxy = np.maximum(proxy, eps)                     # manfiy proksi ma'nosiz
    d["proxy"] = proxy                                 # audit uchun (FEATURES ga KIRMAYDI)
    # Ekstremal qiymatlar ±CLIP oralig'ida qisqartiriladi: proksi nolga yaqin bo'lsa bo'linma
    # portlaydi (audit uchun xom ma'lumot `data/` da qoladi, feature esa barqaror bo'lishi kerak).
    CLIP = 20.0
    d["proxy_gap"] = np.clip((d["reported_ghg"] - d["proxy"]) / (d["proxy"].abs() + eps), -CLIP, CLIP)
    g2 = d.groupby("company_id", group_keys=False)     # proksi ustunlari uchun guruhlash
    med_gap = g2["proxy_gap"].transform(lambda s: s.rolling(4, min_periods=2).median())
    d["proxy_gap_own_dev"] = np.clip(d["proxy_gap"] - med_gap, -CLIP, CLIP)
    d["proxy_growth"] = np.clip(g2["proxy"].pct_change().replace([np.inf, -np.inf], np.nan),
                                -CLIP, CLIP)
    d["proxy_gap_x_growth"] = np.clip(d["proxy_gap_own_dev"] * d["proxy_growth"], -CLIP, CLIP)

    # ---- A7: offsetlarning o'z tarixiga nisbatan chetlanishi ----
    med_off = g2["offsets_reported"].transform(lambda s: s.rolling(4, min_periods=2).median())
    d["offsets_own_dev"] = np.where(med_off.abs() > 1e-9,
                                    d["offsets_reported"] / (med_off.abs() + eps) - 1.0, 0.0)

    # birinchi davr NaN'larini 0 bilan to'ldirish (bitta qator = bitta korxona tarixi boshi)
    for f in FEATURES:
        d[f] = d[f].astype(float).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return d


def feature_matrix(df: pd.DataFrame):
    """(X, meta) qaytaradi — X faqat FEATURES ustunlaridan."""
    X = df[FEATURES].to_numpy(dtype=float)
    meta = df[["company_id", "quarter", "q_index", "sector", "label", "anomaly_type"]].copy()
    return X, meta
