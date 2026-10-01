# -*- coding: utf-8 -*-
"""Sektor tahlili va vaqt bo'yicha juftlash testlari (R48).

Barcha testlar deterministik va tarmoqsiz.
"""
from __future__ import annotations

import math
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.kirishsiz import screener, sector  # noqa: E402


# ---------------------------------------------------------------- wind rose


def test_wind_rose_counts_eight_sectors():
    winds = [0, 45, 90, 135, 180, 225, 270, 315, 350]
    r = sector.wind_rose(winds)
    assert r["jami"] == 9
    assert r["sektorlar"]["N"] == 2          # 0° va 350° ikkalasi N sektorida
    assert sum(r["sektorlar"].values()) == 9
    assert abs(sum(r["ulush"].values()) - 1.0) < 1e-9


def test_wind_rose_skips_missing():
    r = sector.wind_rose([0, None, "", 90])
    assert r["jami"] == 2
    assert r["sektorlar"]["E"] == 1


def test_wind_rose_empty_is_safe():
    r = sector.wind_rose([])
    assert r["jami"] == 0 and r["eng_kop"] == []


# ---------------------------------------------------------------- sektor ulushi


def test_sektor_ulushi_basic_and_wraparound():
    r = sector.sektor_ulushi([10, 350, 90, 180], 0, 45)
    assert r["mos"] == 2 and r["jami"] == 4 and r["ulush"] == pytest.approx(0.5)
    r2 = sector.sektor_ulushi([350], 10, 45)      # burchak o'tishi (360→0)
    assert r2["ulush"] == pytest.approx(1.0)


def test_sektor_ulushi_ignores_none():
    r = sector.sektor_ulushi([None, 20, None], 20, 10)
    assert r["jami"] == 1 and r["ulush"] == pytest.approx(1.0)


# ---------------------------------------------------------------- kvantil


def test_kvantil_median_and_edges():
    assert sector._kvantil([1, 2, 3, 4], 0.5) == pytest.approx(2.5)
    assert sector._kvantil([5], 0.9) == 5
    assert sector._kvantil([1, 2, 3, 4], 1.0) == 4


def test_kvantil_interpolates():
    assert sector._kvantil([0, 10], 0.5) == pytest.approx(5.0)
    with pytest.raises(ValueError):
        sector._kvantil([], 0.9)


# ---------------------------------------------------------------- boyitilish (lift)


def test_enrichment_needs_enough_data():
    r = sector.directional_enrichment([1, 2, 3] * 5, [0] * 15, 0)
    assert "xato" in r and r["n"] == 15


def test_enrichment_detects_sector_signal():
    # 200 soat: yuqori soatlar (20%) butunlay 45° sektordan
    qiymatlar = [10.0] * 200
    shamollar = [270.0] * 200
    for i in range(20):
        qiymatlar[i] = 50.0
        shamollar[i] = 45.0
    r = sector.directional_enrichment(qiymatlar, shamollar, 45.0, 45.0, 0.90)
    assert r["fon_ulushi"] == pytest.approx(0.10)    # 20/200 soat sektordan
    assert r["yuqori_ulushi"] == pytest.approx(1.0)
    assert r["lift"] == pytest.approx(10.0, rel=0.05)
    assert r["lift"] > 1.5
    assert r["isbot_kuchi"] == 2


def test_enrichment_no_signal_when_uniform():
    qiymatlar = [10.0] * 100 + [50.0] * 100
    shamollar = ([0.0, 180.0] * 50) + ([0.0, 180.0] * 50)   # taqsimot bir xil
    r = sector.directional_enrichment(qiymatlar, shamollar, 0.0, 45.0, 0.90)
    assert r["fon_ulushi"] == pytest.approx(r["yuqori_ulushi"], abs=0.02)
    assert r["lift"] == pytest.approx(1.0, abs=0.1)
    assert "signal yo'q" in r["xulosa"]


@pytest.mark.parametrize("lift_va_xulosa", [
    (2.0, "sektor bo'yicha signal bor"),
    (1.2, "kuchsiz signal"),
    (1.0, "signal yo'q"),
])
def test_enrichment_xulosa_thresholds(lift_va_xulosa):
    kutilgan_lift, kutilgan_matn = lift_va_xulosa
    assert kutilgan_matn in sector._xulosa(kutilgan_lift)
    assert sector._xulosa(None) == "fon ulushi nol — lift hisoblanmaydi"


def test_enrichment_uses_only_valid_pairs():
    qiymatlar = [10.0] * 100
    shamollar = [0.0] * 100
    qiymatlar[0] = None                     # bu soat tashlanadi
    shamollar[1] = None
    r = sector.directional_enrichment(qiymatlar, shamollar, 0.0, 45.0, 0.90)
    assert r["n_soat"] == 98


# ---------------------------------------------------------------- ko'p modda


def test_ko_p_modda_picks_strongest():
    qiymatlar_a = [5.0] * 100
    qiymatlar_b = [5.0] * 100
    shamollar = [90.0] * 100
    for i in range(10):                    # b modda kuchli signal beradi
        qiymatlar_b[i] = 100.0
        shamollar[i] = 30.0
    rep = sector.ko_p_modda({"a": (qiymatlar_a, [90.0] * 100), "b": (qiymatlar_b, shamollar)}, 30.0, 45.0)
    assert rep["eng_kuchli"]["modda"] == "b"
    assert "skrining" in rep["eslatma"]


def test_candidate_sector_bearings():
    r = sector.candidate_sector(41.311, 69.240, [{"nom": "Shimol", "lat": 41.40, "lon": 69.24}])
    s = r["sektorlar"][0]
    assert s["markaz"] == pytest.approx(0.0, abs=1.0)
    assert s["masofa_km"] == pytest.approx(9.9, rel=0.03)


# ---------------------------------------------------------------- vaqt bo'yicha juftlash


def test_to_float_variants():
    assert screener.to_float("") is None
    assert screener.to_float(None) is None
    assert screener.to_float("—") is None
    assert screener.to_float("nan") is None
    assert screener.to_float(" 12,5 ") == pytest.approx(12.5)
    assert screener.to_float(7) == pytest.approx(7.0)


def test_dirty_hours_by_time_aligns_not_by_index():
    aq_t = ["t1", "t2", "t3"]
    aq_v = [50.0, 60.0, 10.0]
    w_t = ["t3", "t1", "t2"]                 # tartib boshqa — vaqt bo'yicha topilishi kerak
    w_v = [270.0, 45.0, 90.0]
    r = screener.dirty_hours_by_time(aq_t, aq_v, w_t, w_v, norm_hourly=35.0)
    juft = {h["vaqt"]: h["wind_from"] for h in r["soatlar"]}
    assert juft == {"t1": 45.0, "t2": 90.0}
    assert r["oshgan"] == 2 and r["shamol_yoq"] == 0 and r["qamrov"] == pytest.approx(1.0)


def test_dirty_hours_by_time_counts_missing_wind():
    r = screener.dirty_hours_by_time(["t1", "t2"], [40.0, 40.0], ["t1"], [""], 35.0)
    assert r["oshgan"] == 2 and r["shamol_yoq"] == 2 and r["qamrov"] == 0.0


def test_dirty_hours_by_time_strictly_greater():
    r = screener.dirty_hours_by_time(["t1"], ["35.0"], ["t1"], ["0"], 35.0)
    assert r["oshgan"] == 0
