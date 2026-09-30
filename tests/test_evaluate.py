# -*- coding: utf-8 -*-
"""Qo'shimcha testlar (S9 — 20+ talab): baholash, meta, figuralar."""
import json
import os
import sys

import numpy as np
import pytest

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

from src import models as M                                  # noqa: E402
from src.evaluate import (business_compare, choose_threshold, metrics_at,  # noqa: E402
                          per_type_recall, recall_at_top)
from src.generator import generate                           # noqa: E402
from src import features as F                                # noqa: E402


def test_threshold_monotonic():
    """Alert-rate oshsa — threshold pasayadi (kvantil ta'rifi bo'yicha)."""
    s = np.linspace(0, 1, 1001)
    t10 = choose_threshold(s, 0.10)
    t20 = choose_threshold(s, 0.20)
    assert t20 < t10


def test_metrics_perfect_separation():
    y = np.array([0] * 100 + [1] * 20)
    s = np.concatenate([np.zeros(100), np.ones(20)])
    r = metrics_at(y, s, 0.5)
    assert r["f1"] == 1.0 and r["fpr"] == 0.0 and r["recall"] == 1.0


def test_metrics_all_negative_predicted():
    y = np.array([0] * 50 + [1] * 10)
    r = metrics_at(y, np.zeros(60), 10.0)
    assert r["precision"] == 0.0 and r["recall"] == 0.0 and r["fpr"] == 0.0


def test_recall_at_top_perfect():
    y = np.array([1, 1, 0, 0, 0, 0, 0, 0, 0, 0])
    s = np.array([0.9, 0.8, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1])
    assert recall_at_top(y, s, 0.2) == 1.0


def test_recall_at_top_worst():
    y = np.array([1, 1, 0, 0, 0, 0, 0, 0, 0, 0])
    s = np.array([0.1, 0.1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2])
    assert recall_at_top(y, s, 0.2) == 0.0


def test_business_compare_improvement():
    rng = np.random.default_rng(0)
    y = (rng.random(1000) < 0.2).astype(int)
    s = y * 10 + rng.random(1000)
    b = business_compare(y, s, 200)
    assert b["yaxshilanish_x"] > 1.5
    assert b["model_top_n_aniqlik"] > b["random_top_n_aniqlik"]


def test_per_type_recall_nan_safe():
    import pandas as pd
    meta = pd.DataFrame({"anomaly_type": [np.nan, "A1", "A1", ""]})
    s = np.array([0.9, 0.9, 0.1, 0.1])
    out = per_type_recall(meta, s, 0.5)
    assert out.get("A1") == 0.5


def test_save_meta_writes_json(tmp_path):
    m = {"name": "if", "params": {"a": 1}, "train_seconds": 1.23}
    p = tmp_path / "meta.json"
    M.save_meta(m, str(p), extra={"features": ["x"], "threshold_if": 0.5})
    d = json.loads(p.read_text())
    assert d["name"] == "if" and d["features"] == ["x"] and d["rule_version"] == "1.0"


def test_make_figures_creates_three(tmp_path):
    from src.evaluate import make_figures
    rng = np.random.default_rng(0)
    y = (rng.random(400) < 0.2).astype(int)
    s = y + rng.random(400)
    import pandas as pd
    meta = pd.DataFrame({"anomaly_type": ["A1" if v else "" for v in y], "company_id": "C", "quarter": "q",
                         "q_index": 0, "sector": "energy"})
    paths = make_figures(y, s, meta, 0.5, str(tmp_path), per_type={"A1": 0.5})
    assert len(paths) == 3 and all(os.path.exists(p) for p in paths)


def test_dashboard_builder_phrases_cover_all_features():
    """Izoh kaliti barcha 26 feature'ni qoplashi shart (dashboard sifati sharti)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "bd", os.path.join(BASE, "scripts", "build_dashboard.py"))
    bd = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bd)
    missing = [f for f in F.FEATURES if f not in bd.FEATURE_PHRASE]
    assert not missing, f"izohsiz feature'lar: {missing}"


def test_features_deterministic():
    d1 = generate(n_companies=30, injection_rate=0.15, seed=11)
    d2 = generate(n_companies=30, injection_rate=0.15, seed=11)
    f1 = F.build_features(d1)
    f2 = F.build_features(d2)
    assert np.allclose(F.feature_matrix(f1)[0], F.feature_matrix(f2)[0])
