# -*- coding: utf-8 -*-
"""«Kirishsiz» yo'llar testlari — reyestr, oraliq hisobi, Benford, oqim, transsekt, huquqiy talab.

Barcha testlar **deterministik va tarmoqsiz** (jonli manbalar `scripts/fetch_public.py --check`
bilan alohida tekshiriladi; CI'da tarmoqqa chiqilmaydi).
"""
from __future__ import annotations

import math
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.kirishsiz import bands, benford, plume, requests_gen, screener  # noqa: E402
from src.kirishsiz import registry, transect  # noqa: E402


# ---------------------------------------------------------------- reyestr


def test_registry_has_eight_paths():
    assert len(registry.PATHS) == 8
    assert len({p["id"] for p in registry.PATHS}) == 8


def test_every_path_has_evidence_and_legal_basis():
    for p in registry.PATHS:
        assert p["isbot_kuchi"] in (1, 2, 3, 4, 5), p["id"]
        assert p["manba"], p["id"]
        assert p["huquqiy_asos"], p["id"]
        assert p["cheklov"], p["id"]          # «nima isbotlanmaydi» yozilgan bo'lishi shart
        assert len(p["cheklov"]) > 40, p["id"]


def test_no_path_requires_enterprise_permission():
    for p in registry.PATHS:
        assert p["kirish_kerak"] is False, p["id"]


def test_conclusion_rule_requires_two_strong_paths():
    r = registry.conclusion_rule()
    assert r["min_kuch"] >= 3 and r["min_yol"] >= 2


def test_paths_by_power_sorted():
    ps = registry.paths_by_power(3)
    assert [p["isbot_kuchi"] for p in ps] == sorted([p["isbot_kuchi"] for p in ps], reverse=True)
    assert all(p["isbot_kuchi"] >= 3 for p in ps)


def test_registry_json_serialisable():
    import json
    d = json.loads(registry.registry_json())
    assert len(d["yollar"]) == 8 and "qoida" in d


# ---------------------------------------------------------------- oraliq hisobi


def test_elv_to_ef_matches_guidebook_conversion():
    # EMEP/EEA 2023: EF[mg/t kl] = ELV × 2300 Nm³/t kl; sement uchun × 0,90 / 1e6 → kg/t
    ef = bands.elv_to_ef(500.0, per="t_sement")
    assert ef == pytest.approx(500 * 2300 * 0.9 / 1e6) == pytest.approx(1.035, abs=1e-6)
    ef_kl = bands.elv_to_ef(500.0, per="t_klinker")
    assert ef_kl == pytest.approx(1.15, abs=1e-9)


def test_elv_to_ef_rejects_bad_input():
    with pytest.raises(ValueError):
        bands.elv_to_ef(-1)
    with pytest.raises(ValueError):
        bands.elv_to_ef(500, clinker_factor=0)
    with pytest.raises(ValueError):
        bands.elv_to_ef(500, per="tosh")


def test_expected_band_geometry():
    b = bands.expected_band(1000, 2.0, 4.0)
    assert b["past"] == pytest.approx(2000.0)
    assert b["yuqori"] == pytest.approx(4000.0)
    assert b["orta_geometrik"] == pytest.approx(math.sqrt(2000 * 4000))


def test_expected_band_with_control_shrinks_and_range_wide():
    b0 = bands.expected_band(1000, 2.0, 4.0)
    b1 = bands.expected_band(1000, 2.0, 4.0, control_low=0.5, control_high=0.9)
    assert b1["past"] < b0["past"] and b1["yuqori"] < b0["yuqori"]
    assert b1["past"] == pytest.approx(1000 * 2.0 * 0.1)
    assert b1["yuqori"] == pytest.approx(1000 * 4.0 * 0.5)


def test_expected_band_rejects_inverted_inputs():
    with pytest.raises(ValueError):
        bands.expected_band(1000, 4.0, 2.0)
    with pytest.raises(ValueError):
        bands.expected_band(-1, 1.0, 2.0)
    with pytest.raises(ValueError):
        bands.expected_band(1000, 1.0, 2.0, control_low=0.9, control_high=0.1)


@pytest.mark.parametrize("reported,expected_level", [
    (2500, "band_ichida"),
    (3000, "band_ichida"),
    (1500, "chegarada"),       # pastdan ×1,5 ichida (oraliq [2000; 4000])
    (5500, "chegarada"),       # yuqoridan ×1,5 ichida
    (100, "banddan_tashqarida"),
    (50000, "banddan_tashqarida"),
])
def test_check_reported_levels(reported, expected_level):
    b = bands.expected_band(1000, 2.0, 4.0)
    r = bands.check_reported(reported, b)
    assert r["daraja"] == expected_level


def test_check_reported_note_is_honest():
    b = bands.expected_band(1000, 2.0, 4.0)
    r = bands.check_reported(100, b)
    assert "ayblov emas" in r["eslatma"]
    assert r["daraja"] == "banddan_tashqarida"


def test_band_from_elv_full_chain():
    out = bands.band_from_elv(1_200_000, 500, 1200, elv_reported_mg_nm3=900, per="t_sement")
    assert out["ef_kg_per_birlik"][0] == pytest.approx(1.035)
    assert out["tekshiruv"]["daraja"] in ("band_ichida", "chegarada")
    assert "EMEP/EEA" in out["manba"]


# ---------------------------------------------------------------- Benford


def test_chi2_survival_matches_critical_values():
    assert benford._chi2_sf(15.507, 8) == pytest.approx(0.05, abs=5e-4)
    assert benford._chi2_sf(20.090, 8) == pytest.approx(0.01, abs=5e-4)
    assert benford._chi2_sf(3.841, 1) == pytest.approx(0.05, abs=2e-3)


def test_first_and_second_digit_normalisation():
    assert benford.first_digit(0.00456) == 4
    assert benford.second_digit(0.00456) == 5
    assert benford.first_digit(987.0) == 9
    assert benford.second_digit(987.0) == 8
    with pytest.raises(ValueError):
        benford.first_digit(0)


def test_benford_probs_sum_to_one():
    assert sum(benford.benford_probs("1").values()) == pytest.approx(1.0)
    assert sum(benford.benford_probs("2").values()) == pytest.approx(1.0)
    assert sum(benford.benford_probs("12").values()) == pytest.approx(1.0)
    with pytest.raises(ValueError):
        benford.benford_probs("3")


def test_benford_conforming_series_is_close():
    import random
    rng = random.Random(42)
    vals = []
    for _ in range(4000):
        # Benford taqsimotidan teskari namuna: F(x)=log10(x) → x = 10^u
        vals.append(10 ** rng.uniform(0, 3))
    r = benford.analyse(vals, "1")
    assert r["madv"] < 0.006
    assert r["madv_bahosi"] == "yaqin mos"
    assert r["p_qiymat"] > 0.01


def test_benford_fabricated_round_numbers_flagged():
    vals = [5 * (10 ** (i % 3)) for i in range(120)]        # faqat 5 bilan boshlanadi
    r = benford.analyse(vals, "1")
    assert r["madv"] > 0.015 and r["madv_bahosi"] == "mos emas"
    assert r["muhim_5foiz"] is True


def test_benford_low_n_warning():
    r = benford.analyse([1.2, 3.4, 5.6, 7.8, 9.1], "1")
    assert any("kuchi past" in w for w in r["ogohlantirish"])
    assert r["isbot_kuchi"] == 1
    assert "isbotlamaydi" in r["izoh"]


def test_round_number_share_detects_rounding():
    tabiiy = [12.3, 45.7, 88.1, 3.9, 67.4, 21.6, 99.2, 5.5, 41.3, 77.8]
    r = benford.round_number_share(tabiiy)
    assert r["ulush"] == pytest.approx(0.1, abs=0.11)
    dumaloq = [900, 1200, 1500, 900, 750, 1050, 900, 1500, 1200, 900]
    r2 = benford.round_number_share(dumaloq)
    assert r2["ulush"] >= 0.4 and r2["signal"] is True


# ---------------------------------------------------------------- orbita (oqim)


def test_mol_to_kg_conversion():
    assert plume.mol_to_kg(1.0, "CH4") == pytest.approx(0.016043, abs=1e-6)
    assert plume.mol_to_kg(1.0, "NO2") == pytest.approx(0.0460055, abs=1e-7)
    with pytest.raises(KeyError):
        plume.mol_to_kg(1.0, "Xx")


def test_csf_flux_mass_balance():
    q = plume.csf_flux([0.001, 0.002, 0.0015], wind_ms=3.0, dx_m=3500)
    assert q["q_kg_s"] == pytest.approx((0.0045) * 3.0 * 3500)
    assert "CSF" in q["formula"] or "Σ" in q["formula"]
    with pytest.raises(ValueError):
        plume.csf_flux([0.001, -0.002], 3.0, 3500)
    with pytest.raises(ValueError):
        plume.csf_flux([0.001], 0.0, 3500)


def test_ime_flux_residence_time():
    r = plume.ime_flux(ime_kg=1000.0, wind_ms=3.0, plume_length_m=3000.0)
    assert r["tau_s"] == pytest.approx(1000.0, rel=1e-6)      # τ = L / U_eff = 3000/3
    assert r["q_kg_s"] == pytest.approx(1.0, rel=1e-6)        # Q = IME/τ = 1000/1000
    assert r["u_eff_factor"] == 1.0
    with pytest.raises(ValueError):
        plume.ime_flux(-1, 3.0, 3000.0)


def test_ime_flux_sensitive_to_effective_wind():
    a = plume.ime_flux(1000, 3.0, 3000, u_eff_factor=1.0)
    b = plume.ime_flux(1000, 3.0, 3000, u_eff_factor=0.5)
    assert b["q_kg_s"] == pytest.approx(a["q_kg_s"] * 0.5, rel=1e-9)   # τ ikki marta uzun


def test_detection_limit_grows_with_pixel_and_wind():
    a = plume.detection_limit_kg_s(3.0, 3500, 1e-5)
    b = plume.detection_limit_kg_s(6.0, 7000, 1e-5)
    assert b["q_min_kg_s"] == pytest.approx(4 * a["q_min_kg_s"], rel=1e-9)
    assert a["q_min_t_kun"] > 0


def test_annualise_and_persistence():
    a = plume.annualise(1.0, persistensiya=1.0)
    b = plume.annualise(1.0, persistensiya=0.5)
    assert a["t_yil"] == pytest.approx(1.0 * 8760 * 3600 / 1000)
    assert b["t_yil"] == pytest.approx(a["t_yil"] / 2)
    with pytest.raises(ValueError):
        plume.annualise(1.0, persistensiya=0)


def test_bearing_and_distance_known_geometry():
    # bir xil uzunlikda 0,09° shimolga ≈ 10,0 km; azimut 0°
    d = plume.haversine_m(41.31, 69.24, 41.40, 69.24)
    assert d == pytest.approx(9990, rel=0.02)
    assert plume.bearing_deg(41.31, 69.24, 41.40, 69.24) == pytest.approx(0.0, abs=0.5)
    assert plume.bearing_deg(41.31, 69.24, 41.31, 69.40) == pytest.approx(90.0, abs=0.5)
    assert plume.angle_diff(350, 10) == pytest.approx(20.0)


def test_attribute_candidates_orders_by_wind():
    cands = [
        {"nom": "Shimoliy", "lat": 41.40, "lon": 69.24},   # azimut ~0°
        {"nom": "Sharqiy", "lat": 41.31, "lon": 69.40},    # azimut ~90°
    ]
    r = plume.attribute_candidates(41.31, 69.24, wind_from_deg=5.0, candidates=cands)
    assert r["nomzodlar"][0]["nom"] == "Shimoliy" and r["nomzodlar"][0]["mos"] is True
    assert r["nomzodlar"][1]["mos"] is False
    assert "Nomzod" in r["izoh"]


def test_attribute_respects_max_distance():
    cands = [{"nom": "Uzoq", "lat": 42.0, "lon": 69.24}]     # ~77 km
    r = plume.attribute_candidates(41.31, 69.24, 0.0, cands, max_km=30)
    assert r["mos_soni"] == 0


# ---------------------------------------------------------------- transsekt


def test_invert_q_round_trip_with_forward_model():
    q_true, u, sz = 0.05, 3.0, 20.0
    c = q_true / (math.sqrt(2 * math.pi) * sz * u)          # H=0
    assert transect.invert_q(c, u, sz) == pytest.approx(q_true, rel=1e-9)


def test_invert_q_with_stack_height_increases_q():
    q0 = transect.invert_q(1e-6, 3.0, 20.0, h_m=0.0)
    q1 = transect.invert_q(1e-6, 3.0, 20.0, h_m=30.0)
    assert q1 > q0
    with pytest.raises(ValueError):
        transect.invert_q(-1e-6, 3.0, 20.0)


def test_relative_error_quadrature():
    assert transect.relative_error(0.3, 0.4, 0.0) == pytest.approx(0.5)


def test_fit_campaign_weighted_mean_recovers_q():
    q_true, u, sz = 0.02, 3.0, 25.0
    c = q_true / (math.sqrt(2 * math.pi) * sz * u)
    rows = [{"c": c, "u": u, "sigma_z": sz} for _ in range(4)]
    r = transect.fit_campaign(rows)
    assert r["q_kg_s"] == pytest.approx(q_true, rel=1e-6)
    assert r["otishlar"] == 4 and r["ishonch_95"][0] <= r["q_kg_s"] <= r["ishonch_95"][1]


def test_fit_campaign_flags_large_spread():
    rows = [{"c": 1e-6, "u": 3.0, "sigma_z": 20.0}, {"c": 1e-4, "u": 3.0, "sigma_z": 20.0}]
    r = transect.fit_campaign(rows)
    assert r["ogohlantirish"] is not None and "Tarqoqlik" in r["ogohlantirish"]


def test_plan_campaign_count():
    r = transect.plan_campaign(rel_target=0.2, rel_single=0.4)
    assert r["otishlar_kerak"] == 4
    with pytest.raises(ValueError):
        transect.plan_campaign(0, 0.4)


def test_background_check_levels():
    assert transect.background_check(1e-7, 1e-6)["daraja"] == "yaroqli"
    assert transect.background_check(6e-7, 1e-6)["daraja"] == "chegarada"
    assert transect.background_check(9e-7, 1e-6)["daraja"] == "yaroqsiz"


# ---------------------------------------------------------------- ekran


def test_daily_means_completeness_guard():
    times = [f"2026-09-0{d}T{h:02d}:00" for d in (1, 2) for h in range(24)]
    vals = [10.0] * 24 + [40.0] * 12 + [None] * 12           # 1-kun to'liq, 2-kun 12 soat
    d = screener.daily_means(times, vals)
    assert d[0]["yaroqli"] is True and d[0]["qiymat"] == 10.0
    assert d[1]["yaroqli"] is False and d[1]["qamrov"] == 0.5


def test_exceedance_days_counts_only_valid():
    times = ["2026-09-01T00:00"] * 2
    daily = [{"kun": "2026-09-01", "qiymat": 50.0, "soat_soni": 24, "qamrov": 1.0, "yaroqli": True},
             {"kun": "2026-09-02", "qiymat": 90.0, "soat_soni": 5, "qamrov": 0.2, "yaroqli": False}]
    e = screener.exceedance_days(daily, norm=35.0)
    assert e["oshgan_kunlar"] == 1 and e["tekshirilgan_kunlar"] == 1 == e["ulush"] * 1
    assert e["yaroqsiz_kunlar"] == 1


def test_screen_report_honest_boundaries():
    times = [f"2026-09-0{d}T{h:02d}:00" for d in (1, 2, 3) for h in range(24)]
    vals = [10.0] * 24 + [60.0] * 24 + [12.0] * 24
    rep = screener.screen_report(times, vals, norm=35.0)
    assert rep["oshish"]["oshgan_kunlar"] == 1
    assert rep["isbot_kuchi"] == 2
    assert "Qaysi korxona" in rep["nima_isbotlanmaydi"]


def test_attribute_hours_counts_and_warns():
    dh = []
    for i in range(10):
        dh.append({"vaqt": f"t{i}", "wind_from": 5.0, "receptor_lat": 41.31, "receptor_lon": 69.24})
    cands = [{"nom": "A", "lat": 41.40, "lon": 69.24}, {"nom": "B", "lat": 41.20, "lon": 69.24}]
    r = screener.attribute_hours(dh, cands)
    assert r["nomzodlar"][0]["nom"] == "A" and r["nomzodlar"][0]["ulush"] == 1.0
    assert r["barobar_manba_ogohi"] is False      # faqat A mos keladi


def test_dirty_hours_pairs_value_and_wind():
    out = screener.dirty_hours(["t1", "t2"], [10.0, 50.0], [180.0, 20.0], norm_hourly=35.0)
    assert len(out) == 1 and out[0]["wind_from"] == 20.0


# ---------------------------------------------------------------- huquqiy talab


def test_request_text_cites_sources_and_deadline():
    r = requests_gen.build_request("Ekologiya boshqarmasi", "olchov", sana="2026-10-01")
    m = r["matn"]
    assert "49-moddasi" in m and "Aarhus" in m and "15 kun" in m
    assert r["muddat"]["javob_sana"] == "2026-10-16"
    assert r["muddat"]["eskalatsiya_sana"] == "2026-10-21"
    assert len(r["manbalar"]) == 4


def test_request_unknown_type_rejected():
    with pytest.raises(KeyError):
        requests_gen.build_request("X", "yoq_tur")


def test_tracker_add_load_pending(tmp_path):
    p = str(tmp_path / "sorovlar.jsonl")
    requests_gen.tracker_add(p, requests_gen.build_request("A", "ruxsatnoma", sana="2026-10-01"))
    requests_gen.tracker_add(p, requests_gen.build_request("B", "inspeksiya", sana="2026-10-01"))
    assert len(requests_gen.tracker_load(p)) == 2
    pend = requests_gen.tracker_pending(p, today="2026-10-20")
    assert pend["jami"] == 2 and pend["javobsiz"] == 2 and len(pend["muddati_otgan"]) == 2
    pend2 = requests_gen.tracker_pending(p, today="2026-10-10")
    assert len(pend2["muddati_otgan"]) == 0 and len(pend2["kutayotgan"]) == 2


def test_tracker_empty_when_missing(tmp_path):
    assert requests_gen.tracker_load(str(tmp_path / "yoq.jsonl")) == []


def test_sorov_yangi_turlari_va_topilmalar():
    """R53: isitish-qattiq va gaz-isitish turlari + topilmalar bloki."""
    for tur in ("isitish-qattiq", "gaz-isitish"):
        assert tur in requests_gen.STANDART_SOROVLAR
    r = requests_gen.build_request("Boshqarma", "isitish-qattiq", sana="2026-10-05")
    assert "qattiq yoqilg'i" in r["matn"]
    # topilmalar bloki standart holatda qo'shiladi va o'lchangan raqamlar ko'rinadi
    assert "Tadqiqotning ochiq ma'lumotlarga asoslangan natijalari" in r["matn"]
    assert "25,60" in r["matn"] and "398 g/GJ" in r["matn"]
    assert len(requests_gen.TOPILMALAR) >= 5
    assert r["muddat"]["javob_sana"] == "2026-10-20"


def test_sorov_topilmalarsiz():
    r = requests_gen.build_request("Boshqarma", "olchov", sana="2026-10-05", topilmalar=False)
    assert "Tadqiqotning ochiq ma'lumotlarga asoslangan natijalari" not in r["matn"]
    assert "Tadqiqotning ochiq ma'lumotlarga asoslangan natijalari" in R_bloki()


def R_bloki():
    return requests_gen.topilmalar_bloki()
