# -*- coding: utf-8 -*-
"""Pastdan yuqoriga (bottom-up) hisob va dispersiya testlari — R50.

Tekshiriladi: birlik o'tkazmalari (lb/MMBtu → g/GJ → g/kWh), yillik tashlanma va oqim,
Briggs σ formulalari, Gauss yechimi, sektor ortiqchasi, moslik ulushi va xulosa qoidasi.
Barcha testlar deterministik va tarmoqsiz.
"""
from __future__ import annotations

import math
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.kirishsiz import bottomup as B  # noqa: E402


# ---------------------------------------------------------------- birliklar


def test_lb_per_mmbtu_to_g_per_gj_known_value():
    # 1 lb/MMBtu ≈ 430 g/GJ (453,592 g / 1,055056 GJ)
    assert B.lb_per_mmbtu_to_g_per_gj(1.0) == pytest.approx(429.9, abs=0.2)
    assert B.lb_per_mmbtu_to_g_per_gj(0.32) == pytest.approx(137.6, abs=0.2)


def test_lb_per_mmbtu_negative_rejected():
    with pytest.raises(ValueError):
        B.lb_per_mmbtu_to_g_per_gj(0)


def test_g_per_gj_to_g_per_kwh_efficiency_effect():
    # 100 g/GJ, FIK 100% → 0,36 g/kWh (3,6 MJ/kWh)
    assert B.g_per_gj_to_g_per_kwh(100.0, 1.0) == pytest.approx(0.36)
    assert B.g_per_gj_to_g_per_kwh(137.6, 0.35) == pytest.approx(1.415, abs=0.005)
    # past FIK → ko'proq yoqilg'i → yuqori koeffitsient
    past = B.g_per_gj_to_g_per_kwh(100.0, 0.30)
    yuqori = B.g_per_gj_to_g_per_kwh(100.0, 0.60)
    assert past == pytest.approx(yuqori * 2, rel=1e-9)


def test_g_per_gj_to_g_per_kwh_bad_efficiency():
    for fik in (0, -0.1, 1.5):
        with pytest.raises(ValueError):
            B.g_per_gj_to_g_per_kwh(100.0, fik)


def test_ap42_range_lands_in_expected_band():
    """AP-42 3.1-1: 0,32 (nazoratsiz) va 0,13 (suv quyish) lb/MMBtu, FIK 35–50%."""
    past = B.g_per_gj_to_g_per_kwh(B.lb_per_mmbtu_to_g_per_gj(0.13), 0.50)
    yuqori = B.g_per_gj_to_g_per_kwh(B.lb_per_mmbtu_to_g_per_gj(0.32), 0.35)
    assert 0.35 <= past <= 0.45
    assert 1.30 <= yuqori <= 1.50


# ---------------------------------------------------------------- tashlanma va oqim


def test_annual_tonnes_known():
    # 5,8 TWh × 1 g/kWh = 5 800 t
    assert B.annual_tonnes(5.8, 1.0) == pytest.approx(5800.0)


def test_annual_tonnes_zero_and_negative():
    assert B.annual_tonnes(0, 1.0) == 0.0
    with pytest.raises(ValueError):
        B.annual_tonnes(5.8, -1.0)


def test_rate_kg_s_known():
    # 31 536 t/yil = 1 kg/s (8760 soat)
    assert B.rate_kg_s(31536.0) == pytest.approx(1.0, rel=1e-9)
    assert B.rate_kg_s(3480.0) == pytest.approx(0.1104, abs=1e-3)


def test_rate_kg_s_short_window():
    # 4 320 soatlik oyna uchun o'rtacha oqim yuqoriroq bo'ladi
    assert B.rate_kg_s(3480.0, hours=4320) > B.rate_kg_s(3480.0, hours=8760)


# ---------------------------------------------------------------- Briggs sigma


def test_briggs_sigma_grows_with_distance():
    for st in ("B", "D", "F"):
        y1, z1 = B.briggs_sigma(1000, st)
        y2, z2 = B.briggs_sigma(10000, st)
        assert y2 > y1 and z2 > z1


def test_briggs_sigma_stability_order_rural():
    # 1 km da beqaror (A/B) → barqaror (F) tartibi saqlanadi: B > C > D > E > F
    z = {st: B.briggs_sigma(1000, st)[1] for st in ("B", "C", "D", "E", "F")}
    assert z["B"] > z["C"] > z["D"] > z["E"] > z["F"]
    # uzoq masofada (10 km) beqarorlik ustunligi kuchayadi
    _, zb10 = B.briggs_sigma(10000, "B")
    _, zd10 = B.briggs_sigma(10000, "D")
    assert zb10 > zd10 * 10


def test_briggs_sigma_reference_values():
    # Briggs qishloq D: σy(10 km) ≈ 600 m atrofida
    sy, sz = B.briggs_sigma(10000, "D")
    assert 550 < sy < 700
    assert 30 < sz < 50


def test_briggs_urban_larger_sigma_z():
    _, z_rural = B.briggs_sigma(10000, "D", urban=False)
    _, z_urban = B.briggs_sigma(10000, "D", urban=True)
    assert z_urban > z_rural * 5          # shahar aralashuvi kuchliroq


def test_briggs_sigma_bad_input():
    with pytest.raises(ValueError):
        B.briggs_sigma(0)
    with pytest.raises(ValueError):
        B.briggs_sigma(1000, "Z")


# ---------------------------------------------------------------- Gauss


def test_gaussian_inverse_with_distance_and_wind():
    sy, sz = B.briggs_sigma(10000, "D")
    c1 = B.gaussian_ground_conc(1.0, 4.0, 10000, sy, sz)["ug_m3"]
    c2 = B.gaussian_ground_conc(1.0, 8.0, 10000, sy, sz)["ug_m3"]
    assert c2 == pytest.approx(c1 / 2, rel=1e-9)          # shamol ikki marta → ikki marta suyultirish


def test_gaussian_linear_in_emission():
    sy, sz = B.briggs_sigma(5000, "D")
    a = B.gaussian_ground_conc(1.0, 4.0, 5000, sy, sz)["ug_m3"]
    b = B.gaussian_ground_conc(2.0, 4.0, 5000, sy, sz)["ug_m3"]
    assert b == pytest.approx(2 * a, rel=1e-9)


def test_gaussian_stack_height_reduces_ground_conc():
    sy, sz = B.briggs_sigma(1000, "D")
    past = B.gaussian_ground_conc(1.0, 4.0, 1000, sy, sz, 0.0)["ug_m3"]
    baland = B.gaussian_ground_conc(1.0, 4.0, 1000, sy, sz, 150.0)["ug_m3"]
    assert baland < past


def test_gaussian_matches_analytic_formula():
    sy, sz = 500.0, 200.0
    r = B.gaussian_ground_conc(0.5, 3.0, 10000, sy, sz)
    kutilgan = 0.5 / (math.pi * 3.0 * sy * sz) * 1e9
    assert r["ug_m3"] == pytest.approx(kutilgan, rel=1e-9)


def test_gaussian_bad_input():
    with pytest.raises(ValueError):
        B.gaussian_ground_conc(-1, 4, 1000, 100, 50)
    with pytest.raises(ValueError):
        B.gaussian_ground_conc(1, 0, 1000, 100, 50)


# ---------------------------------------------------------------- ssenariylar


def test_dispersion_table_shape_and_ordering():
    jadval = B.dispersion_table(0.19, 13300, (1.0, 4.0), ("D", "F"), 100.0)
    assert len(jadval) == 4
    # barqaror sharoit (F) yuqori konsentratsiya beradi
    f1 = next(q for q in jadval if q["barqarorlik"] == "F" and q["shamol_ms"] == 1.0)
    d1 = next(q for q in jadval if q["barqarorlik"] == "D" and q["shamol_ms"] == 1.0)
    assert f1["ug_m3"] > d1["ug_m3"]


def test_bottom_up_full_chain():
    r = B.bottom_up(5.8, 0.6, 1.5, 13.3, 4.0, "D", 100.0, urban=True)
    assert r["yillik_tonna"]["past"] == pytest.approx(3480, rel=1e-6)
    assert r["yillik_tonna"]["yuqori"] == pytest.approx(8700, rel=1e-6)
    assert 0.10 < r["oqim_kg_s"]["past"] < 0.12
    assert r["kutilgan_ug_m3"]["past"] < r["kutilgan_ug_m3"]["yuqori"]
    assert "AP-42" in r["manba"]


def test_bottom_up_inverted_range():
    with pytest.raises(ValueError):
        B.bottom_up(5.8, 1.5, 0.6, 13.3)


# ---------------------------------------------------------------- moslik ulushi


def test_alignment_share_counts_only_sector():
    winds = [55.0] * 50 + [90.0] * 50 + [180.0] * 100
    r = B.alignment_share(winds, 54.9, 45.0, 9.0)
    assert r["sektor_soat"] == 100            # 55° va 90° sektorda
    assert r["mos_soat"] == 50                # faqat 55° mos
    assert r["ulush_sektorda"] == pytest.approx(0.5)
    assert r["ulush_jami"] == pytest.approx(0.25)


def test_alignment_share_ignores_missing():
    r = B.alignment_share([55.0, None, ""], 54.9)
    assert r["jami_soat"] == 1 and r["mos_soat"] == 1


def test_alignment_share_no_data():
    assert "xato" in B.alignment_share([None, None], 54.9)


def test_sector_weighted_scenarios_scaling():
    rows = B.sector_weighted_scenarios(0.19, 13.3, 0.195, (2.0, 4.0), ("D",), 100.0)
    assert len(rows) == 2
    u2 = next(r for r in rows if r["shamol_ms"] == 2.0)
    u4 = next(r for r in rows if r["shamol_ms"] == 4.0)
    assert u2["sektor_ortacha_ug_m3"] == pytest.approx(u2["aligned_ug_m3"] * 0.195, rel=1e-3)
    assert u2["sektor_ortacha_ug_m3"] > u4["sektor_ortacha_ug_m3"]


def test_sector_weighted_scenarios_bad_share():
    with pytest.raises(ValueError):
        B.sector_weighted_scenarios(0.19, 13.3, 0.0)


# ---------------------------------------------------------------- sektor ortiqchasi


def test_sector_excess_basic():
    qiymat = [30.0] * 20 + [10.0] * 20
    shamol = [55.0] * 20 + [200.0] * 20
    r = B.sector_excess(qiymat, shamol, 54.9, 45.0)
    assert r["ort_sektor"] == pytest.approx(30.0)
    assert r["ort_tashqari"] == pytest.approx(10.0)
    assert r["farq_ug_m3"] == pytest.approx(20.0)
    assert r["nisbat"] == pytest.approx(3.0)


def test_sector_excess_skips_missing_and_empty():
    r = B.sector_excess([10.0, None], [55.0, 55.0], 54.9)
    assert "xato" in r
    assert "xato" in B.sector_excess([], [], 0)          # ma'lumot yo'q → xato kaliti


# ---------------------------------------------------------------- moslik xulosasi


@pytest.mark.parametrize("model,obs,kutilgan", [
    (10.0, 9.0, "mos"),
    (3.0, 10.0, "past"),
    (30.0, 9.0, "yuqori"),
])
def test_consistency_verdicts(model, obs, kutilgan):
    r = B.consistency(model, obs, 3.0)
    assert kutilgan in r["xulosa"]


def test_consistency_ratio_math():
    r = B.consistency(4.0, 9.0)
    assert r["nisbat"] == pytest.approx(2.25)
    with pytest.raises(ValueError):
        B.consistency(0, 9.0)

# ---------------------------------------------------------------- EMEP/EEA 2023


def test_emep_ef_konversiya():
    # 89 g/GJ, FIK 35% → 0,915 g NOx/kWh
    assert B.emep_ef_g_per_kwh(0.35, "nox") == pytest.approx(0.915, abs=0.002)
    assert B.emep_ef_g_per_kwh(0.50, "nox") == pytest.approx(0.641, abs=0.002)


def test_emep_ef_boshqa_moddalar():
    assert B.emep_ef_g_per_kwh(0.50, "co") == pytest.approx(0.281, abs=0.003)
    assert B.emep_ef_g_per_kwh(0.50, "pm25") == pytest.approx(0.001, abs=0.001)
    with pytest.raises(ValueError):
        B.emep_ef_g_per_kwh(0.5, "yoq")


def test_emep_konstantalar_manbali():
    m = B.EMEP_EEA_2023
    assert m["ef"]["nox_g_per_gj"] == 89.0
    assert m["ef"]["nox_ci"] == (15.0, 185.0)
    assert "1.A.1.a" in m["manba"] and m["tier"] == "A"


def test_ef_taqqoslash_kelishadi():
    r = B.ef_taqqoslash((55.9, 137.6), 89.0)
    assert r["emep_ap42_ichida"] is True
    assert "kelishadi" in r["xulosa"]
    assert r["ap42_geo_orta"] == pytest.approx(87.7, abs=0.3)


def test_ef_taqqoslash_tashqarida():
    r = B.ef_taqqoslash((55.9, 137.6), 300.0)
    assert r["emep_ap42_ichida"] is False
    assert "kelishmaydi" in r["xulosa"]


def test_ef_taqqoslash_xato():
    with pytest.raises(ValueError):
        B.ef_taqqoslash((137.6, 55.9))       # tartib buzuq
    with pytest.raises(ValueError):
        B.ef_taqqoslash((55.9, 137.6), 0.0)
