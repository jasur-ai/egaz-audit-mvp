# -*- coding: utf-8 -*-
"""S4/S5 — uch model, bitta protokol: Isolation Forest (v1), Autoencoder (v2), OCSVM (nazorat).

Har model: scaler + estimator, skor = anomaliya darajasi (katta = shubhaliroq).
"""
from __future__ import annotations

import json
import time

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.svm import OneClassSVM

RULE_VERSION = "1.0"


def _fit_scaler(X):
    sc = StandardScaler()
    return sc, sc.fit_transform(X)


def train_if(X_train, contamination: float = 0.12, seed: int = 42) -> dict:
    sc, Xs = _fit_scaler(X_train)
    t0 = time.perf_counter()
    # max_samples=0,5 — kichikroq namuna izolyatsiya daraxtlarini xilma-xil qiladi va
    # nozik anomaliyalarni (A5/A8) yaxshiroq ajratadi (R34 tajriba: F1 0,49 → 0,54).
    model = IsolationForest(n_estimators=600, max_samples=0.5, contamination=contamination,
                            random_state=seed, n_jobs=-1)
    model.fit(Xs)
    el = time.perf_counter() - t0
    return {"name": "if", "model": model, "scaler": sc, "contamination": contamination,
            "train_seconds": round(el, 2),
            "params": {"n_estimators": 600, "max_samples": 0.5,
                       "contamination": contamination, "random_state": seed}}


def score_if(m: dict, X) -> np.ndarray:
    return -m["model"].decision_function(m["scaler"].transform(X))


def train_ae(X_train, hidden: int = 16, seed: int = 42, max_iter: int = 200) -> dict:
    sc, Xs = _fit_scaler(X_train)
    t0 = time.perf_counter()
    model = MLPRegressor(hidden_layer_sizes=(hidden,), activation="relu", solver="adam",
                         max_iter=max_iter, random_state=seed, early_stopping=True,
                         n_iter_no_change=10, batch_size=256)
    model.fit(Xs, Xs)                       # avtoenkoder: kirish = chiqish
    el = time.perf_counter() - t0
    return {"name": "ae", "model": model, "scaler": sc, "train_seconds": round(el, 2),
            "params": {"hidden": hidden, "seed": seed, "max_iter": max_iter}}


def score_ae(m: dict, X) -> np.ndarray:
    Xs = m["scaler"].transform(X)
    rec = m["model"].predict(Xs)
    return np.sqrt(((Xs - rec) ** 2).mean(axis=1))     # RMSE = rekonstruksiya xatosi


def train_ocsvm(X_train, max_rows: int = 4000, nu: float = 0.15, seed: int = 42) -> dict:
    rng = np.random.default_rng(seed)
    if len(X_train) > max_rows:
        idx = rng.choice(len(X_train), size=max_rows, replace=False)
        X_sub = X_train[idx]
    else:
        X_sub = X_train
    sc, Xs = _fit_scaler(X_sub)
    t0 = time.perf_counter()
    model = OneClassSVM(kernel="rbf", gamma="scale", nu=nu)
    model.fit(Xs)
    el = time.perf_counter() - t0
    return {"name": "ocsvm", "model": model, "scaler": sc, "train_seconds": round(el, 2),
            "train_rows": int(len(X_sub)), "params": {"nu": nu, "kernel": "rbf", "subset": int(len(X_sub))}}


def score_ocsvm(m: dict, X) -> np.ndarray:
    return -m["model"].decision_function(m["scaler"].transform(X))


SCORERS = {"if": score_if, "ae": score_ae, "ocsvm": score_ocsvm}


def save_meta(m: dict, path: str, extra: dict | None = None) -> None:
    meta = {"name": m["name"], "params": m.get("params", {}), "train_seconds": m.get("train_seconds"),
            "rule_version": RULE_VERSION, "trained_at": time.strftime("%Y-%m-%d %H:%M:%S")}
    if extra:
        meta.update(extra)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
