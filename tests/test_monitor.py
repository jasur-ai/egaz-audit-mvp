# -*- coding: utf-8 -*-
"""S8 monitoring testlari — PSI, KS, FPR trendi, qaror qoidalari."""
import os
import sys

import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

from src import monitor as MN  # noqa: E402


def test_psi_identical_is_near_zero():
    rng = np.random.default_rng(0)
    x = rng.normal(0, 1, 5000)
    assert MN.psi(x, x.copy()) < 0.01


def test_psi_grows_with_shift():
    rng = np.random.default_rng(1)
    x = rng.normal(0, 1, 5000)
    small = MN.psi(x, rng.normal(0.05, 1, 5000))
    big = MN.psi(x, rng.normal(2.0, 1, 5000))
    assert small < MN.PSI_STABLE < big
    assert big > MN.PSI_WATCH


def test_psi_scale_change_detected():
    rng = np.random.default_rng(2)
    x = rng.normal(0, 1, 4000)
    y = rng.normal(0, 3, 4000)          # dispersiya o'zgarishi
    assert MN.psi(x, y) > MN.PSI_STABLE


def test_psi_constant_feature_safe():
    x = np.ones(100)
    assert MN.psi(x, x) == 0.0          # deyarli o'zgarmas — bo'linish xatosi yo'q


def test_psi_empty_arrays():
    assert MN.psi(np.array([]), np.array([1.0])) == 0.0


def test_drift_table_structure():
    rng = np.random.default_rng(3)
    Xtr = rng.normal(0, 1, (1000, 3))
    Xte = rng.normal(0, 1, (500, 3))
    Xte[:, 0] += 3.0                     # birinchi feature siljigan
    rows = MN.drift_table(Xtr, Xte, ["a", "b", "c"])
    assert rows[0]["feature"] == "a" and rows[0]["status"] == "dreyf"
    assert all({"feature", "psi", "ks_stat", "ks_p", "status"} <= set(r) for r in rows)


def test_time_feature_excluded_from_verdict():
    """Vaqt indeksi «vaqt» statusi oladi va qayta o'qitish qaroriga kirmaydi."""
    rng = np.random.default_rng(9)
    Xtr = rng.normal(0, 1, (600, 2))
    Xte = rng.normal(0, 1, (600, 2))
    Xte[:, 0] = np.arange(600) / 100.0        # «quarter_index» o'rniga
    rows = MN.drift_table(Xtr, Xte, ["quarter_index", "b"])
    assert rows[0]["feature"] == "quarter_index" and rows[0]["status"] == "vaqt"
    v = MN.verdict(rows, {"drift": False}, [{"quarter": "2025Q3", "fpr": 0.05}])
    assert "quarter_index" not in v["drifted"] and "QAYTA" not in v["action"]


def test_score_drift_detects_shift():
    rng = np.random.default_rng(4)
    a = rng.normal(0, 1, 2000)
    b = rng.normal(0, 1, 2000)
    assert MN.score_drift(a, b)["drift"] is False
    assert MN.score_drift(a, b + 1.5)["drift"] is True


def test_fpr_trend_uses_frozen_threshold():
    meta = pd.DataFrame({"q_index": [18, 18, 19, 19, 20, 20],
                         "quarter": ["2025Q3", "2025Q3", "2025Q4", "2025Q4", "2026Q1", "2026Q1"]})
    y = np.array([0, 1, 0, 1, 0, 1])
    s = np.array([0.1, 0.9, 0.1, 0.9, 0.1, 0.9])
    t = MN.fpr_trend(y, s, meta, 0.5)
    assert len(t) == 3 and all(x["fpr"] == 0.0 for x in t)
    assert all(x["recall"] == 1.0 for x in t)


def test_fpr_trend_flags_high_fpr():
    meta = pd.DataFrame({"q_index": [18, 18], "quarter": ["2025Q3", "2025Q3"]})
    y = np.array([0, 0])
    s = np.array([0.9, 0.9])               # normallar alert bo'ldi
    t = MN.fpr_trend(y, s, meta, 0.5)
    assert t[0]["fpr"] == 1.0


def test_verdict_retrain_on_drift():
    drift = [{"feature": "x", "psi": 0.9, "status": "dreyf"}]
    v = MN.verdict(drift, {"drift": False}, [{"quarter": "2025Q3", "fpr": 0.02}])
    assert "QAYTA O'QITISH" in v["action"] and "x" in v["drifted"]
    # dreyf + FPR buzilishi — ikkala sabab ko'rsatiladi
    v2 = MN.verdict(drift, {"drift": False}, [{"quarter": "2026Q1", "fpr": 0.3}])
    assert len(v2["reason"]) == 2 and "2026Q1" in v2["reason"][1]


def test_verdict_recalibrate_on_fpr_only():
    """Dreyf yo'q, faqat FPR chegaradan oshgan → qayta o'qitish emas, kalibrlash."""
    v = MN.verdict([{"feature": "x", "psi": 0.01, "status": "stabil"}],
                   {"drift": False}, [{"quarter": "2025Q4", "fpr": 0.31}])
    assert "KALIBRLASH" in v["action"] and "QAYTA O'QITISH" not in v["action"]
    assert "2025Q4" in v["fpr_quarters_over"]


def test_verdict_watch_when_minor():
    v = MN.verdict([{"feature": "x", "psi": 0.15, "status": "kuzatuv"}],
                   {"drift": False}, [{"quarter": "2025Q3", "fpr": 0.05}])
    assert "KUZATUV" in v["action"]


def test_verdict_stable():
    v = MN.verdict([{"feature": "x", "psi": 0.01, "status": "stabil"}],
                   {"drift": False}, [{"quarter": "2025Q3", "fpr": 0.05}])
    assert "STABIL" in v["action"]


def test_monitor_figures_created(tmp_path):
    drift = [{"feature": f"f{i}", "psi": 0.3 - i * 0.02, "status": "kuzatuv" if i % 2 else "stabil",
              "ks_stat": 0.1, "ks_p": 0.4, "mean_train": 0.0, "mean_test": 0.1} for i in range(6)]
    trend = [{"quarter": f"2025Q{i}", "fpr": 0.05, "recall": 0.4, "n": 100, "positives": 10, "alerts": 14}
             for i in range(1, 5)]
    paths = MN.make_monitor_figures(drift, trend, str(tmp_path))
    assert len(paths) == 2 and all(os.path.exists(p) for p in paths)


def test_build_report_contains_sections(tmp_path):
    drift = [{"feature": "x", "psi": 0.5, "status": "dreyf", "ks_stat": 0.3, "ks_p": 1e-9,
              "mean_train": 0.0, "mean_test": 0.5}]
    trend = [{"quarter": "2025Q3", "n": 10, "positives": 2, "fpr": 0.2, "recall": 0.5, "alerts": 4}]
    v = MN.verdict(drift, {"drift": True, "ks_stat": 0.3, "ks_p": 1e-9, "mean_train": 0, "mean_test": 1}, trend)
    p = MN.build_report(drift, {"ks_stat": 0.3, "ks_p": 1e-9, "mean_train": 0, "mean_test": 1, "drift": True},
                        trend, v, str(tmp_path / "m.md"), [])
    text = open(p, encoding="utf-8").read()
    for sec in ("Qaror:", "Feature dreyfi", "Skor dreyfi", "FPR va Recall trendi", "Qaror qoidalari"):
        assert sec in text
    assert "⚠️" in text                    # FPR buzilishi belgilandi
