# -*- coding: utf-8 -*-
"""R41 — F7 (aktivlik) va F8 (proksi) guruhlari + own-history feature'lari uchun testlar."""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import features as F            # noqa: E402
from src.generator import generate       # noqa: E402


@pytest.fixture(scope="module")
def big_df():
    return generate(n_companies=120, injection_rate=0.15, seed=7)


def test_new_groups_present():
    assert {"aktivlik", "proksi"} <= set(F.FEATURE_GROUPS)
    assert len(F.FEATURES) == 33
    assert all(f in F.FEATURES for f in ("prod_report_gap", "energy_report_gap",
                                         "offsets_own_dev", "proxy_gap", "proxy_gap_own_dev",
                                         "proxy_growth", "proxy_gap_x_growth"))


def test_proxy_fit_uses_train_only(big_df):
    """Leak testi: test davridagi qiymatlarni o'zgartirish koeffitsiyentlarga TA'SIR QILMAYDI."""
    c1 = F.fit_proxy(big_df, train_max_q=17)
    tampered = big_df.copy()
    te = tampered["q_index"] > 17
    tampered.loc[te, "reported_ghg"] = tampered.loc[te, "reported_ghg"] * 5.0
    tampered.loc[te, "energy"] = tampered.loc[te, "energy"] * 3.0
    c2 = F.fit_proxy(tampered, train_max_q=17)
    assert np.allclose(c1, c2), "proksi koeffitsiyentlari test davriga qaramaydi"


def test_proxy_not_negative_and_clipped(big_df):
    feat = F.build_features(big_df)
    assert (feat["proxy"] > 0).all()
    for c in ("proxy_gap", "proxy_gap_own_dev", "proxy_growth", "proxy_gap_x_growth"):
        assert feat[c].abs().max() <= 20.0 + 1e-9, f"{c} qisqartirish chegarasidan tashqarida"


def test_activity_gap_signals_a5(big_df):
    """A5 (ishlab chiqarish 1,18×) — `prod_report_gap` da ko'rinadi; normallar 0."""
    feat = F.build_features(big_df)
    a5 = feat[feat["anomaly_type"] == "A5"]["prod_report_gap"]
    normal = feat[feat["anomaly_type"] == ""]["prod_report_gap"]
    assert len(a5) > 10
    assert abs(a5.median() - 0.18) < 0.01, "A5 signali kutilgan 0,18 emas"
    assert normal.abs().max() < 1e-6, "normal qatorlarda gap aniq 0 bo'lishi kerak"


def test_offsets_own_dev_signals_a7(big_df):
    """A7 (offset 2×) — o'z tarixiga nisbatan +0,7 atrofida ko'rinadi."""
    feat = F.build_features(big_df)
    a7 = feat[feat["anomaly_type"] == "A7"]["offsets_own_dev"]
    normal = feat[feat["anomaly_type"] == ""]["offsets_own_dev"]
    assert a7.median() > 0.5
    assert abs(normal.median()) < 0.05


def test_proxy_gap_x_growth_negative_for_a8():
    """A8 (vaqt-aralashtirish) — interaksiya feature'i manfiy tomonga siljiydi.

    A8 test davrida kam uchraydi, shuning uchun kattaroq namuna olinadi (400 korxona).
    """
    df = generate(n_companies=400, injection_rate=0.20, seed=21)
    feat = F.build_features(df)
    d = feat[feat["q_index"] > 17]
    a8 = d[d["anomaly_type"] == "A8"]
    norm = d[d["label"] == 0]
    assert len(a8) >= 15, f"A8 qatorlari yetarli emas: {len(a8)}"
    assert a8["proxy_gap_x_growth"].median() < norm["proxy_gap_x_growth"].median()


def test_features_deterministic_with_new_groups(big_df):
    f1 = F.build_features(big_df)
    f2 = F.build_features(big_df)
    for c in ("prod_report_gap", "offsets_own_dev", "proxy_gap", "proxy_gap_x_growth"):
        assert np.allclose(f1[c].to_numpy(), f2[c].to_numpy())


def test_missing_activity_columns_fallback():
    """Aktivlik ustunlari bo'lmasa — proksi o'chadi, lekin quvur yiqilmaydi."""
    df = generate(n_companies=40, injection_rate=0.15, seed=9)
    subset = df.drop(columns=["energy", "production"])
    coef = F.fit_proxy(subset, train_max_q=17)
    assert np.allclose(coef, 0.0)
