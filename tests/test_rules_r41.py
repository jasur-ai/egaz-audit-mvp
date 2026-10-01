# -*- coding: utf-8 -*-
"""R41 — ochiq qoidalar kanali va FPR siyosatlari uchun testlar (gibrid aniqlash)."""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import features as F                     # noqa: E402
from src import rules as R                        # noqa: E402
from src.evaluate import (median_slide_threshold, metrics_at,  # noqa: E402
                          metrics_by_period, rolling_threshold)
from src.generator import generate                # noqa: E402


@pytest.fixture(scope="module")
def big():
    df = generate(n_companies=400, injection_rate=0.20, seed=33)
    feat = F.build_features(df)
    X, meta = F.feature_matrix(feat)
    return feat, meta


# ---------------- qoidalar kanali ----------------

def test_thresholds_are_human_readable(big):
    """Chegaralar `GRID_ABS` dan olinadi — audit qilinadigan sonlar (float shovqini yo'q)."""
    feat, meta = big
    val = ((meta["q_index"] >= 16) & (meta["q_index"] <= 17)).to_numpy()
    accepted, rejected = R.select_thresholds(feat, meta, val)
    assert accepted, "hech bo'lmaganda bitta qoida qabul qilinishi kerak"
    for name, cfg in accepted.items():
        assert cfg["thr"] in R.GRID_ABS, f"{name}: {cfg['thr']} grid'da yo'q"
        assert cfg["val_precision"] >= 0.30


def test_selection_uses_validation_only(big):
    """Leak testi: test davri qiymatlarini buzish tanlangan chegaraga ta'sir qilmaydi."""
    feat, meta = big
    val = ((meta["q_index"] >= 16) & (meta["q_index"] <= 17)).to_numpy()
    a1, _ = R.select_thresholds(feat, meta, val)
    tampered = feat.copy()
    te = (meta["q_index"] > 17).to_numpy()
    tampered.loc[te, "prod_report_gap"] = 0.99
    tampered.loc[te, "offsets_own_dev"] = 9.9
    a2, _ = R.select_thresholds(tampered, meta, val)
    assert {k: v["thr"] for k, v in a1.items()} == {k: v["thr"] for k, v in a2.items()}


def test_noise_rule_is_rejected(big):
    """Signal yo'q feature — `min_precision` tufayli rad etiladi (shovqin kanali bo'lmasin)."""
    feat, meta = big
    val = ((meta["q_index"] >= 16) & (meta["q_index"] <= 17)).to_numpy()
    noisy = feat.copy()
    rng = np.random.default_rng(0)
    noisy["prod_report_gap"] = rng.normal(0, 1, len(noisy))          # A5 signali yo'q
    accepted, rejected = R.select_thresholds(noisy, meta, val)
    names = [r["nomi"] for r in rejected]
    assert any("A5" in n for n in names), "shovqin qoidasi rad etilishi kerak edi"


def test_apply_rules_union(big):
    feat, meta = big
    val = ((meta["q_index"] >= 16) & (meta["q_index"] <= 17)).to_numpy()
    accepted, _ = R.select_thresholds(feat, meta, val)
    flag, each = R.apply_rules(feat, accepted)
    assert flag.shape == (len(feat),)
    union = np.zeros(len(feat), dtype=bool)
    for f in each.values():
        union |= f
    assert np.array_equal(flag, union)


def test_rule_catches_a5_without_false_positives(big):
    """A5 qoidasi aniq: normal qatorlarni belgilamaydi (validatsiya + test birga)."""
    feat, meta = big
    val = ((meta["q_index"] >= 16) & (meta["q_index"] <= 17)).to_numpy()
    accepted, _ = R.select_thresholds(feat, meta, val)
    if "R-A5 aktivlik kross-tekshiruvi" not in accepted:
        pytest.skip("A5 qoidasi bu namunada qabul qilinmadi")
    flag, each = R.apply_rules(feat, accepted)
    a5_flag = each["R-A5 aktivlik kross-tekshiruvi"]
    y = meta["label"].to_numpy()
    at = meta["anomaly_type"].fillna("").to_numpy()
    assert (a5_flag & (y == 0)).sum() == 0, "A5 qoidasi normal qatorni belgilamasligi kerak"
    # Qolgan belgilangan qatorlar ham anomaliya bo'lishi kerak: generatorda bitta qatorda
    # ikki anomaliya to'qnashishi mumkin (masalan A5 izi + A6 bloki), shuning uchun 95% mezon.
    flagged = a5_flag
    assert (flagged & (y == 1)).sum() / max(flagged.sum(), 1) >= 0.95


# ---------------- FPR siyosatlari ----------------

def test_median_slide_preserves_fpr_under_location_shift():
    """Asosiy xossa: FPR = P(skor ≥ t | normal). Normal taqsimot δ ga siljisa, statik threshold
    FPR ni buzadi; median-slide esa δ ni turadi va FPR ni mo'ljalda (10%) ushlab qoladi."""
    rng = np.random.default_rng(1)
    ref = rng.normal(0, 1, 20000)
    base = float(np.quantile(ref, 0.90))          # ma'lumotnoma FPR = 10% (mo'ljal)
    fpr_ref = float((ref >= base).mean())
    assert abs(fpr_ref - 0.10) < 0.01

    s = rng.normal(0.4, 1, 20000)                 # butun taqsimot +0,4 siljigan (dreyf)
    periods = np.array([20] * 10000 + [21] * 10000)
    thr = median_slide_threshold(ref, periods, s, base_thr=base)
    assert abs(thr[20] - (base + 0.4)) < 0.08     # siljish to'g'ri baholandi
    assert abs(thr[20] - thr[21]) < 0.05          # median bahosi namuna shovqiniga sezgir

    fpr_static = float((s >= base).mean())
    fpr_slide = float(np.mean([s[i] >= thr[periods[i]] for i in range(len(s))]))
    assert fpr_static > 0.15, "statik threshold siljishda FPR ni buzishi kerak"
    assert abs(fpr_slide - 0.10) < 0.03, f"median-slide FPR ni ushlab turmadi: {fpr_slide:.3f}"


def test_policies_do_not_use_labels():
    """Label'larni almashtirish siyosat threshold'lariga TA'SIR QILMAYDI (label'siz siyosat)."""
    rng = np.random.default_rng(2)
    ref = rng.normal(0, 1, 3000)
    s = rng.normal(0.3, 1, 4000)
    periods = np.array([18] * 1000 + [19] * 1000 + [20] * 1000 + [21] * 1000)
    t1 = median_slide_threshold(ref, periods, s, base_thr=0.5)
    t2 = rolling_threshold(ref, periods, s, alert_rate=0.12, window=4)
    y = rng.integers(0, 2, 4000)                 # tasodifiy label'lar — hech qayerda ishlatilmaydi
    t3 = median_slide_threshold(ref, periods, s, base_thr=0.5)
    t4 = rolling_threshold(ref, periods, s, alert_rate=0.12, window=4)
    assert t1 == t3 and t2 == t4
    assert np.isfinite(list(t1.values())).all()


def test_rolling_threshold_uses_only_past_periods():
    """Davr threshold'i faqat o'zidan OLDINGI davrlarga qaraydi (kelajak ma'lumoti yo'q)."""
    rng = np.random.default_rng(3)
    ref = rng.normal(0, 1, 2000)
    periods = np.array([18] * 500 + [19] * 500 + [20] * 500)
    s = rng.normal(0, 1, 1500)
    thr = rolling_threshold(ref, periods, s, alert_rate=0.10, window=2)
    s_changed = s.copy()
    s_changed[periods == 20] += 10.0             # 20-davrni buzamiz
    thr2 = rolling_threshold(ref, periods, s_changed, alert_rate=0.10, window=2)
    assert thr[18] == thr2[18] and thr[20] == thr2[20], "o'zgarish faqat 21-davrga ta'sir qilishi kerak"


def test_metrics_at_with_thr_rows():
    y = np.array([0, 0, 1, 1])
    s = np.array([0.1, 0.9, 0.8, 0.2])
    m = metrics_at(y, s, thr=0.5, thr_rows=np.array([0.5, 0.95, 0.7, 0.1]))
    # pred = [0, 0, 1, 1] → tp=2 (0.8 ≥ 0.7 va 0.2 ≥ 0.1), fp=0, fn=0, tn=2
    assert (m["tp"], m["fp"], m["fn"], m["tn"]) == (2, 0, 0, 2)


def test_metrics_by_period_shapes():
    y = np.array([0, 1, 0, 1])
    s = np.array([0.1, 0.9, 0.2, 0.8])
    rows = metrics_by_period(y, s, 0.5, np.array([18, 18, 19, 19]))
    assert [r["davr"] for r in rows] == [18, 19]
    assert all(0.0 <= r["fpr"] <= 1.0 for r in rows)
