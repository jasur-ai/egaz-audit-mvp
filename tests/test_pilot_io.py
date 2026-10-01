# -*- coding: utf-8 -*-
"""TZ-1 pilot IO testlari — sxema (§4.2), sifat nazorati (§4.3), audit izi (§4.6)."""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import pilot_io as P  # noqa: E402


@pytest.fixture()
def good_df():
    return P.sample_rows(n_objects=1, windows=8, seed=11)


# ---------------------------------------------------------------- sxema (§4.2)

def test_valid_file_passes(good_df):
    rep = P.validate(good_df)
    assert rep["ok"], rep["errors"]
    assert rep["stats"]["qatorlar"] == 16
    assert rep["stats"]["cems_qatorlar"] == 8 and rep["stats"]["hisobot_qatorlar"] == 8


def test_missing_required_column_rejected(good_df):
    rep = P.validate(good_df.drop(columns=["birlik"]))
    assert not rep["ok"]
    assert any("birlik" in e for e in rep["errors"])


def test_time_without_offset_rejected(good_df):
    df = good_df.copy()
    df.loc[df.index[0], "oyna_boshi"] = "2026-12-07T08:00:00"      # offset yo'q
    rep = P.validate(df)
    assert not rep["ok"] and any("offseti yo'q" in e for e in rep["errors"])


def test_window_not_aligned_to_20_minutes_rejected(good_df):
    df = good_df.copy()
    df.loc[df.index[0], "oyna_boshi"] = "2026-12-07T08:13:00+05:00"
    rep = P.validate(df)
    assert not rep["ok"] and any("20 daqiqaga karrali" in e for e in rep["errors"])


def test_unit_modda_mismatch_rejected(good_df):
    df = good_df.copy()
    df["modda"] = "PM"                    # PM — µg/m³ bo'lishi kerak, faylda mg/m³
    rep = P.validate(df)
    assert not rep["ok"] and any("birlik moddaga mos emas" in e for e in rep["errors"])


def test_unit_alias_accepted(good_df):
    df = good_df.copy()
    df["birlik"] = "mg/m3"                 # ASCII varianti ham qabul qilinadi
    assert P.validate(df)["ok"]
    assert P.normalize_birlik("µg/m³") == "ug/m3" and P.normalize_birlik("nomalum") is None


def test_empty_value_requires_valid_false(good_df):
    df = good_df.copy()
    df["qiymat"] = df["qiymat"].astype(object)
    df.loc[df.index[0], "qiymat"] = ""
    rep = P.validate(df)
    assert not rep["ok"] and any("valid=true" in e for e in rep["errors"])

    df2 = good_df.copy()
    df2["qiymat"] = df2["qiymat"].astype(object)
    df2.loc[df2.index[0], "qiymat"] = ""
    df2.loc[df2.index[0], "valid"] = "false"
    assert P.validate(df2)["ok"]            # bo'sh qiymat valid=false bilan qabul qilinadi


def test_negative_value_rejected(good_df):
    df = good_df.copy()
    df["qiymat"] = df["qiymat"].astype(object)
    df.loc[df.index[0], "qiymat"] = "-5"
    rep = P.validate(df)
    assert not rep["ok"] and any("manfiy" in e for e in rep["errors"])


# ---------------------------------------------------------------- sifat (§4.3)

def test_duplicate_key_rejected_same_manba(good_df):
    df = pd.concat([good_df, good_df.iloc[[0]]], ignore_index=True)
    rep = P.validate(df)
    assert not rep["ok"] and any("Takroriy kalit" in e for e in rep["errors"])


def test_same_window_two_manba_is_not_duplicate(good_df):
    """Kalitda `manba` bor: bir oynada cems + hisobot — normal holat, rad etilmaydi."""
    rep = P.validate(good_df)
    assert rep["ok"]


def test_missing_windows_marks_object_conditional():
    df = P.sample_rows(n_objects=1, windows=72, seed=5)
    drop = df.index[df["manba"] == "cems"][10:22]          # 12 ta oyna yo'q (16,7%)
    df = df.drop(drop).reset_index(drop=True)
    rep = P.validate(df)
    assert rep["ok"], "bo'shliq — «shartli», rad etish emas"
    obj = rep["objects"][0]
    assert obj["holat"] == "shartli" and "bo'shliq" in obj["holat_sababi"]


def test_full_coverage_stays_accepted():
    df = P.sample_rows(n_objects=2, windows=72, seed=6)
    rep = P.validate(df)
    assert [o["holat"] for o in rep["objects"]] == ["qabul", "qabul"]


def test_unknown_manba_rejected(good_df):
    df = good_df.copy()
    df.loc[df.index[0], "manba"] = "laboratoriya"
    rep = P.validate(df)
    assert not rep["ok"] and any("manba" in e for e in rep["errors"])


# ---------------------------------------------------------------- juftliklar

def test_pair_windows_signed_difference(good_df):
    rep = P.validate(good_df)
    pw = P.pair_windows(rep["_df"])
    assert pw["n"] == 8
    x = pw["xulosa"]
    # namuna generatori ~+3% surilish beradi: farq = hisobot − cems > 0
    assert x["musbat_ulush"] == 1.0
    assert 0.0 < x["median_nisbiy"] < 0.10
    assert set(["q5", "q25", "q50", "q75", "q95", "MAD"]).issubset(x)


def test_pair_windows_skips_invalid(good_df):
    df = good_df.copy()
    df.loc[df[df["manba"] == "hisobot"].index[0], "valid"] = "false"
    rep = P.validate(df)
    assert P.pair_windows(rep["_df"])["n"] == 7


# ---------------------------------------------------------------- audit (§4.6)

def test_audit_record_sha256_stable(tmp_path, good_df):
    f = tmp_path / "K-1.csv"
    good_df.to_csv(f, index=False, encoding="utf-8")
    r1 = P.audit_record(str(f), role="metrolog")
    r2 = P.audit_record(str(f), role="analyst")
    assert r1["sha256"] == r2["sha256"] and len(r1["sha256"]) == 64
    assert r1["qatorlar"] == 16 and r1["rol"] == "metrolog"
    assert r1["sha256"] != P.audit_record(str(f) + ".x", role="x")["sha256"] if os.path.exists(str(f) + ".x") else True


def test_audit_appends_only(tmp_path, good_df):
    f = tmp_path / "f.csv"
    good_df.to_csv(f, index=False, encoding="utf-8")
    ap = tmp_path / "audit.jsonl"
    P.validate_file(str(f), role="metrolog", audit_path=str(ap))
    P.validate_file(str(f), role="analyst", audit_path=str(ap))
    lines = [json.loads(x) for x in open(ap, encoding="utf-8").read().strip().split("\n")]
    assert len(lines) == 2 and [x["rol"] for x in lines] == ["metrolog", "analyst"]
    assert all(x["natija"] == "qabul" for x in lines)


def test_rejected_file_logged_as_rad_etildi(tmp_path):
    df = P.sample_rows(n_objects=1, windows=4)
    df.loc[df.index[0], "birlik"] = "ppm"
    f = tmp_path / "bad.csv"
    df.to_csv(f, index=False, encoding="utf-8")
    ap = tmp_path / "audit.jsonl"
    rep = P.validate_file(str(f), role="operator", audit_path=str(ap))
    assert not rep["ok"]
    rec = json.loads(open(ap, encoding="utf-8").read().strip())
    assert rec["natija"] == "rad etildi"
