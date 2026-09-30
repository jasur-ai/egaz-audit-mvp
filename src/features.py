# -*- coding: utf-8 -*-
"""S3 — Feature engineering (TZ §7: 6 guruh, 26 feature).

Muhim: `implied_ghg` — ground truth; model uni KO'RMAYDI (aks holda baholash ma'nosiz bo'ladi).
Barcha feature'lar faqat "ko'rinadigan" ustunlardan hisoblanadi (reported_*, production, energy, offsets).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

FEATURE_GROUPS = {
    "nisbat": ["log_reported", "qoq_growth_reported", "reported_to_energy"],
    "energiya": ["energy_intensity", "energy_intensity_growth", "ghg_intensity", "ghg_intensity_growth"],
    "tarkib": ["gas_share", "gas_share_growth", "offsets_share", "offsets_share_growth", "fugitive_ratio_change"],
    "dinamika": ["rolling_dev", "repeat_count", "flat_flag", "seasonal_residual", "drift_slope"],
    "aniqlik": ["drift_estimate", "jump_flag", "unit_jump_flag", "boundary_mix_flag"],
    "miqyos": ["log_production", "size_pct", "quarter_index", "energy_to_prod_dev", "reporting_volatility"],
}

FEATURES = [f for g in FEATURE_GROUPS.values() for f in g]


def build_features(df: pd.DataFrame) -> pd.DataFrame:
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

    # birinchi davr NaN'larini 0 bilan to'ldirish (bitta qator = bitta korxona tarixi boshi)
    for f in FEATURES:
        d[f] = d[f].astype(float).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return d


def feature_matrix(df: pd.DataFrame):
    """(X, meta) qaytaradi — X faqat FEATURES ustunlaridan."""
    X = df[FEATURES].to_numpy(dtype=float)
    meta = df[["company_id", "quarter", "q_index", "sector", "label", "anomaly_type"]].copy()
    return X, meta
