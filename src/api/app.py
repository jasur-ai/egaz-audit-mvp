# -*- coding: utf-8 -*-
"""S7 — serving qatlami (FastAPI).

TZ §S7 qoidasi: og'ir CPU inferens `async def` ichida chaqirilmaydi.
Bu yerda endpointlar sinxron (`def`) — FastAPI ularni avtomatik threadpool'da bajaradi.
"""
from __future__ import annotations

import json
import os

import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

MODEL_DIR = os.environ.get("CARBON_MODEL_DIR") or os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "models")

app = FastAPI(title="E-GAZ-AUDIT serving", version="1.0",
              description="AI-asoslangan GHG hisobot anomaliya skoringi (TZ S7 prototipi)")

_CACHE: dict = {}


def load_models():
    if _CACHE:
        return _CACHE
    if_v = os.path.join(MODEL_DIR, "if_v1.joblib")
    if not os.path.exists(if_v):
        raise HTTPException(503, "Model topilmadi — avval `python3 scripts/run_all.py` ishga tushiring")
    _CACHE["if"] = joblib.load(if_v)
    for name in ("ae", "ocsvm"):
        p = os.path.join(MODEL_DIR, f"{name}.joblib")
        if os.path.exists(p):
            _CACHE[name] = joblib.load(p)
    meta_p = os.path.join(MODEL_DIR, "metadata.json")
    _CACHE["meta"] = json.load(open(meta_p, encoding="utf-8")) if os.path.exists(meta_p) else {}
    return _CACHE


class ScoreRequest(BaseModel):
    features: dict[str, float]          # feature nomi → qiymat (26 ta)
    explain: bool = True


@app.get("/v1/health")
def health():
    ok = os.path.exists(os.path.join(MODEL_DIR, "if_v1.joblib"))
    return {"status": "ok" if ok else "model_missing", "model_dir": MODEL_DIR,
            "models": [p[:-7] for p in sorted(os.listdir(MODEL_DIR)) if p.endswith(".joblib")] if ok else []}


@app.get("/v1/model/info")
def model_info():
    c = load_models()
    return {"metadata": c.get("meta", {}),
            "available": [k for k in ("if", "ae", "ocsvm") if k in c]}


@app.post("/v1/score")
def score(req: ScoreRequest):
    from ..models import SCORERS
    c = load_models()
    meta = c.get("meta", {})
    feats = meta.get("features", [])
    missing = [f for f in feats if f not in req.features]
    if missing:
        raise HTTPException(400, f"Feature yetishmaydi ({len(missing)} ta): {missing[:5]}...")
    x = np.array([[req.features[f] for f in feats]], dtype=float)
    out: dict = {"scores": {}, "flags": {}}
    for name in ("if", "ae", "ocsvm"):
        if name in c:
            s = float(SCORERS[name](c[name], x)[0])
            out["scores"][name] = round(s, 4)
    thr = meta.get("threshold_if")
    if thr is not None and "if" in out["scores"]:
        out["flags"]["if_alert"] = bool(out["scores"]["if"] >= thr)
    if req.explain and "if" in c and feats:
        sc = c["if"]["scaler"]
        xs = sc.transform(x)[0]
        contrib = np.abs(xs)
        top = np.argsort(-contrib)[:3]
        out["explain_top3"] = [{"feature": feats[i], "z": round(float(xs[i]), 2)} for i in top]
    return out
