# -*- coding: utf-8 -*-
"""Isitish mavsumi moduli testlari — R50 (B-qatlam 3-qadam)."""
from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.kirishsiz import mavsum as M  # noqa: E402

VAQT = ["2026-01-01T00:00", "2026-01-01T12:00", "2026-07-01T00:00", "2026-07-01T12:00"]


def test_kunlik_ort():
    k = M.kunlik_ort(VAQT, [0.0, 4.0, 30.0, 40.0])
    assert len(k) == 2
    assert k[0]["kun"] == "2026-01-01" and k[0]["ort"] == pytest.approx(2.0)
    assert k[1]["maks"] == pytest.approx(40.0)


def test_kunlik_ort_bosh_qiymat():
    k = M.kunlik_ort(["2026-01-01T00:00", "2026-01-01T01:00"], [5.0, None])
    assert k[0]["n"] == 1 and k[0]["ort"] == pytest.approx(5.0)


def test_isitish_kunlari_chegara():
    k = M.kunlik_ort(VAQT, [0.0, 4.0, 30.0, 40.0])
    isit = M.isitish_kunlari(k, 8.0)
    assert len(isit) == 1 and isit[0]["kun"] == "2026-01-01"
    assert len(M.isitish_kunlari(k, 45.0)) == 2


def test_qamrov_soatlari():
    q = M.qamrov(VAQT)
    assert q["jami_soat"] == 4
    assert q["oylar"] == {"2026-01": 2, "2026-07": 2}


def test_qamrov_isitish_ulushi():
    q = M.qamrov(["2026-01-01T00:00", "2026-07-01T00:00"], [0.0, 30.0], 8.0)
    assert q["isitish_soat"] == 1
    assert q["isitish_ulush_foiz"] == pytest.approx(50.0)
    assert q["issiq_soat"] == 1


def test_qamrov_haroratsiz_foiz_yoq():
    assert "isitish_ulush_foiz" not in M.qamrov(VAQT)


def test_oylik_bolish():
    b = M.oylik_bolish(VAQT, [0.0, 2.0, 30.0, 34.0])
    assert b["2026-01"] == [0.0, 2.0] and b["2026-07"] == [30.0, 34.0]


def test_mavsumiy_lift_ikkala_rejim():
    # 20 isitish soati + 20 issiq soati, barchasi sektorda/yo'q
    vaqt = ["2026-01-01T%02d:00" % i for i in range(20)] + ["2026-07-01T%02d:00" % i for i in range(20)]
    harorat = [0.0] * 20 + [30.0] * 20
    winds = [55.0] * 10 + [180.0] * 10 + [55.0] * 10 + [180.0] * 10
    qiymat = [40.0] * 10 + [20.0] * 10 + [30.0] * 10 + [10.0] * 10
    r = M.mavsumiy_lift({"pm2_5_ug_m3": qiymat}, winds, harorat, 54.9, 45.0, 8.0)
    m = r["moddalar"]["pm2_5_ug_m3"]
    assert m["isitish"]["lift"] == pytest.approx(2.0)
    assert m["issiq"]["lift"] == pytest.approx(3.0)
    assert m["isitish"]["n_sektor"] == 10 and m["issiq"]["n_sektor"] == 10


def test_mavsumiy_lift_malumot_yetarli_emas():
    r = M.mavsumiy_lift({"x": [10.0, 20.0]}, [55.0, 180.0], [0.0, 30.0], 54.9)
    assert "xato" in r["moddalar"]["x"]["isitish"]


def test_yuklama_oshishi_vaznli():
    r = M.yuklama_oshishi(0.25, 0.75, 2.0, 1.0)
    assert r["vaznli_nisbat"] == pytest.approx(1.25)
    assert "isitish" in r["izoh"]


def test_yuklama_oshishi_xato():
    with pytest.raises(ValueError):
        M.yuklama_oshishi(0.5, 0.4, 1.0, 1.0)
    with pytest.raises(ValueError):
        M.yuklama_oshishi(1.5, -0.5, 1.0, 1.0)


def test_reja_qoshilishi_kerak():
    r = M.reja({"oylar": {"2026-04": 100, "2026-09": 100}}, ("2026-10", "2026-11"))
    assert r["qo'shilishi_kerak"] == ["2026-10", "2026-11"]
    assert "fetch_public" in r["qadam"]


def test_reja_allaqachon_bor():
    r = M.reja({"oylar": {"2026-10": 10}}, ("2026-10",))
    assert r["qo'shilishi_kerak"] == []


def test_chegara_konstantasi():
    assert M.ISITISH_CHEGARA_C == 8.0
    assert 10 in M.ISITISH_OYLARI and 7 not in M.ISITISH_OYLARI

# ---------------------------------------------------------------- epizod atributsiyasi


def test_ortacha_yonalish_aylana_boyicha():
    # 350° va 10° → o'rtacha 0° (360° emas!)
    assert M.o_rtacha_yonalish([350.0, 10.0]) == pytest.approx(0.0, abs=0.1)
    assert M.o_rtacha_yonalish([90.0, 90.0]) == pytest.approx(90.0, abs=0.1)
    assert M.o_rtacha_yonalish([None, ""]) is None


def test_epizod_atributsiya_uch_toifa():
    # 3 kun: (a) sektor ustun, (b) aralash, (c) sektordan tashqarida
    vaqt, qiymat, shamol, harorat = [], [], [], []
    for i in range(24):
        vaqt.append(f"2025-12-01T{i:02d}:00"); qiymat.append(50.0); shamol.append(55.0); harorat.append(2.0)
    for i in range(24):
        vaqt.append(f"2025-12-02T{i:02d}:00")
        qiymat.append(50.0)
        shamol.append(55.0 if i % 3 == 0 else 180.0)   # 33% sektorda
        harorat.append(2.0)
    for i in range(24):
        vaqt.append(f"2025-12-03T{i:02d}:00"); qiymat.append(50.0); shamol.append(200.0); harorat.append(2.0)
    r = M.epizod_atributsiya(vaqt, qiymat, shamol, harorat, 54.9, 45.0, 35.0)
    assert r["jami"] == 3
    assert r["hisob"]["sektor_ustun"] == 1
    assert r["hisob"]["aralash"] == 1
    assert r["hisob"]["sektordan_tashqarida"] == 1
    assert "1 tasida" in r["xulosa"]


def test_epizod_atributsiya_chegaradan_past_kunlar_tashlanadi():
    vaqt = [f"2025-12-01T{i:02d}:00" for i in range(24)]
    r = M.epizod_atributsiya(vaqt, [10.0] * 24, [55.0] * 24, [2.0] * 24, 54.9, 45.0, 35.0)
    assert r["jami"] == 0 and "yo'q" in r["xulosa"]


def test_epizod_atributsiya_qisqa_kun_hisobga_olinmaydi():
    vaqt = [f"2025-12-01T{i:02d}:00" for i in range(5)]
    r = M.epizod_atributsiya(vaqt, [50.0] * 5, [55.0] * 5, [2.0] * 5, 54.9, 45.0, 35.0, kamida_soat=12)
    assert r["jami"] == 0


def test_epizod_atributsiya_kun_maydonlari():
    vaqt = [f"2025-12-01T{i:02d}:00" for i in range(24)]
    r = M.epizod_atributsiya(vaqt, [40.0] * 24, [55.0] * 24, [-3.0] * 24, 54.9, 45.0, 35.0)
    k = r["kunlar"][0]
    assert k["ort_pm"] == pytest.approx(40.0)
    assert k["ort_harorat"] == pytest.approx(-3.0)
    assert k["sektor_ulush"] == pytest.approx(1.0)
    assert k["toifa"] == "sektor_ustun"
