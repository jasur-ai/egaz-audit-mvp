# -*- coding: utf-8 -*-
"""Quvur testlari: generator (S1), feature (S3), model+metrika (S4/S6), serving (S7)."""
import gzip
import json
import os
import sys

import numpy as np
import pytest

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

from src import features as F          # noqa: E402
from src import models as M            # noqa: E402
from src.evaluate import choose_threshold, metrics_at   # noqa: E402
from src.generator import ANOMALY_TYPES, generate       # noqa: E402


# ---------- S1: generator ----------
@pytest.fixture(scope="module")
def small_df():
    return generate(n_companies=300, injection_rate=0.15, seed=7)


def test_generator_shape(small_df):
    assert len(small_df) == 300 * 22
    assert small_df["company_id"].nunique() == 300


def test_generator_determinism():
    a = generate(n_companies=50, injection_rate=0.15, seed=1)
    b = generate(n_companies=50, injection_rate=0.15, seed=1)
    assert a.equals(b)


def test_injection_rate_close(small_df):
    assert 0.10 <= small_df["label"].mean() <= 0.20


def test_anomaly_types_valid(small_df):
    types = set(small_df["anomaly_type"]) - {""}
    assert types <= set(ANOMALY_TYPES) and len(types) >= 6


def test_a4_unit_error_visible(small_df):
    a4 = small_df[small_df["anomaly_type"] == "A4"]
    assert len(a4) > 0
    assert (a4["reported_ghg"] > 100 * a4["implied_ghg"]).any() or \
           (a4["reported_ghg"] < 0.01 * a4["implied_ghg"]).any()


def test_a6_repeats_block(small_df):
    a6 = small_df[small_df["anomaly_type"] == "A6"]
    assert len(a6) >= 4
    comp = a6.iloc[0]["company_id"]
    vals = a6[a6["company_id"] == comp]["reported_ghg"].round(6)
    assert vals.nunique() <= 2          # blok takrori


# ---------- S3: feature ----------
def test_feature_matrix_clean(small_df):
    feat = F.build_features(small_df)
    X, meta = F.feature_matrix(feat)
    assert X.shape == (len(feat), len(F.FEATURES)) == (len(feat), 26)
    assert np.isfinite(X).all()
    assert len(meta) == len(feat)


def test_feature_groups_count():
    assert len(F.FEATURE_GROUPS) == 6


def test_flat_flag_catches_repeat(small_df):
    feat = F.build_features(small_df)
    a6 = feat[feat["anomaly_type"] == "A6"]
    normal = feat[feat["anomaly_type"] == ""]
    assert a6["flat_flag"].mean() > normal["flat_flag"].mean()


def test_no_leakage_implied_not_in_features():
    assert "implied_ghg" not in F.FEATURES
    assert all("implied" not in f for f in F.FEATURES)


# ---------- S4/S5/S6 ----------
def test_training_and_metrics(small_df):
    feat = F.build_features(small_df)
    X, meta = F.feature_matrix(feat)
    y = meta["label"].to_numpy()
    tr = (meta["q_index"] <= 17).to_numpy()
    m = M.train_if(X[tr], contamination=0.15, seed=3)
    s_tr = M.score_if(m, X[tr])
    s_te = M.score_if(m, X[~tr])
    thr = choose_threshold(s_tr, 0.15)
    r = metrics_at(y[~tr], s_te, thr)
    assert r["roc_auc"] > 0.7 and r["f1"] > 0.1
    assert set(r) >= {"precision", "recall", "f1", "roc_auc", "pr_auc", "fpr"}


def test_ae_and_ocsvm_run(small_df):
    feat = F.build_features(small_df)
    X, meta = F.feature_matrix(feat)
    tr = (meta["q_index"] <= 17).to_numpy()
    ae = M.train_ae(X[tr], max_iter=30)
    assert np.isfinite(M.score_ae(ae, X[~tr])).all()
    oc = M.train_ocsvm(X[tr], max_rows=500)
    assert np.isfinite(M.score_ocsvm(oc, X[~tr])).all()


def test_threshold_is_train_quantile():
    s = np.arange(100, dtype=float)
    assert choose_threshold(s, 0.10) == pytest.approx(89.1, abs=0.15)


# ---------- S7: serving ----------
def test_api_score(small_df, tmp_path):
    feat = F.build_features(small_df)
    X, meta = F.feature_matrix(feat)
    tr = (meta["q_index"] <= 17).to_numpy()
    import joblib
    m = M.train_if(X[tr], seed=5)
    joblib.dump(m, tmp_path / "if_v1.joblib", compress=3)
    thr = choose_threshold(M.score_if(m, X[tr]), 0.15)
    M.save_meta(m, str(tmp_path / "metadata.json"),
                extra={"features": F.FEATURES, "threshold_if": thr})

    os.environ["CARBON_MODEL_DIR"] = str(tmp_path)
    from fastapi.testclient import TestClient
    import importlib
    import src.api.app as appmod
    importlib.reload(appmod)
    client = TestClient(appmod.app)

    assert client.get("/v1/health").json()["status"] == "ok"
    feats = {f: 0.0 for f in F.FEATURES}
    r = client.post("/v1/score", json={"features": feats})
    assert r.status_code == 200
    body = r.json()
    assert "if" in body["scores"] and len(body["explain_top3"]) == 3
    r2 = client.post("/v1/score", json={"features": {"log_reported": 1.0}})
    assert r2.status_code == 400
