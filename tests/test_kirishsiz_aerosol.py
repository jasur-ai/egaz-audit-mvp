# -*- coding: utf-8 -*-
"""Ikkilamchi aerozol moduli testlari — R50 (B-qatlam, PM2,5 gipotezasi)."""
from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.kirishsiz import aerosol as A  # noqa: E402


def test_pearson_mukammal_musbat():
    r = A.pearson([(1, 2), (2, 4), (3, 6), (4, 8)])
    assert r["r"] == pytest.approx(1.0)
    assert r["n"] == 4


def test_pearson_mukammal_manfiy():
    r = A.pearson([(1, 8), (2, 6), (3, 4), (4, 2)])
    assert r["r"] == pytest.approx(-1.0)


def test_pearson_kam_malumot():
    assert A.pearson([(1, 2), (2, 4)])["r"] is None
    assert "xato" in A.pearson([])


def test_pearson_ozgarmas_qator():
    r = A.pearson([(1, 5), (2, 5), (3, 5)])
    assert r["r"] is None and r["xato"]


def test_sektor_tarkibi_asosiy():
    ustunlar = {"pm2_5_ug_m3": [30.0] * 50 + [10.0] * 50}
    winds = [55.0] * 50 + [180.0] * 50
    r = A.sektor_tarkibi(ustunlar, winds, 54.9, 45.0)
    m = r["moddalar"]["pm2_5_ug_m3"]
    assert m["ort_sektor"] == pytest.approx(30.0)
    assert m["ort_tashqari"] == pytest.approx(10.0)
    assert m["ortiqcha"] == pytest.approx(20.0)
    assert m["lift"] == pytest.approx(3.0)


def test_sektor_tarkibi_bosh_seriya():
    r = A.sektor_tarkibi({"x": [None] * 10}, [55.0] * 10, 54.9)
    assert "xato" in r["moddalar"]["x"]


def test_nisbat_belgisi_chegaralari():
    assert "yonish" in A.nisbat_belgisi(20.0, 25.0, 10.0, 20.0)["xulosa"]
    assert "aralash" in A.nisbat_belgisi(10.0, 25.0, 10.0, 20.0)["xulosa"]
    assert "chang" in A.nisbat_belgisi(5.0, 25.0, 10.0, 20.0)["xulosa"]


def test_nisbat_belgisi_xato():
    with pytest.raises(ValueError):
        A.nisbat_belgisi(10.0, 0.0, 10.0, 20.0)
    with pytest.raises(ValueError):
        A.nisbat_belgisi(-1.0, 25.0, 10.0, 20.0)


def test_chang_ulushi():
    r = A.chang_ulushi([20.0, 40.0], [10.0, 10.0])
    assert r["pm10_ort"] == pytest.approx(30.0)
    assert r["chang_ort"] == pytest.approx(10.0)
    assert r["ulush_foiz"] == pytest.approx(33.3, abs=0.1)


def test_chang_ulushi_bosh():
    assert "xato" in A.chang_ulushi([None], [None])


def test_harorat_bogliqlik_manfiy():
    harorat = list(range(0, 40))
    pm25 = [50 - 1.0 * t for t in harorat]          # qishda yuqori → isitish belgisi
    r = A.harorat_bogliqlik(pm25, harorat)
    assert r["r"] <= -0.3
    assert "isitish" in r["xulosa"]


def test_harorat_bogliqlik_musbat():
    harorat = list(range(0, 40))
    pm25 = [10 + 1.0 * t for t in harorat]          # issiqda yuqori → ikkilamchi aerozol
    r = A.harorat_bogliqlik(pm25, harorat)
    assert r["r"] >= 0.1
    assert "musbat" in r["xulosa"]


def test_harorat_bogliqlik_neytral():
    r = A.harorat_bogliqlik([10, 20, 15, 12], [1, 2, 3, 4])
    assert "isitish bilan izohlanmaydi" in r["xulosa"] or "qisman" in r["xulosa"]


def test_mass_rekonstruksiya_uch_holat():
    assert "birlamchi zarra yetarli" in A.mass_rekonstruksiya(10.0, 8.0)["xulosa"]
    assert "qisman" in A.mass_rekonstruksiya(10.0, 3.0)["xulosa"]
    assert "tushuntirmaydi" in A.mass_rekonstruksiya(2.89, 0.12)["xulosa"]


def test_mass_rekonstruksiya_xato():
    with pytest.raises(ValueError):
        A.mass_rekonstruksiya(0.0, 1.0)
    with pytest.raises(ValueError):
        A.mass_rekonstruksiya(1.0, -1.0)


def test_oylik_korinish():
    vaqt = ["2026-04-01T00:00", "2026-04-02T00:00", "2026-05-01T00:00"]
    q = A.oylik_korinish(vaqt, [10.0, 20.0, 30.0])
    assert q[0]["oy"] == "2026-04" and q[0]["ort"] == pytest.approx(15.0)
    assert q[1]["oy"] == "2026-05" and q[1]["ort"] == pytest.approx(30.0)


def test_oylik_korinish_bosh_qiymatlarni_tashlaydi():
    q = A.oylik_korinish(["2026-04-01T00:00", "2026-04-02T00:00"], [10.0, None])
    assert q[0]["n"] == 1


def test_ascii_ustun_chizadi():
    chiz = A.ascii_ustun([{"oy": "2026-04", "ort": 10.0}, {"oy": "2026-05", "ort": 20.0}])
    assert "2026-05" in chiz and "▉" in chiz
    assert A.ascii_ustun([]) == "(ma'lumot yo'q)"


def test_xulosa_belgilar_yigiladi():
    tarkib = {}
    pm = {"farq": 0.02, "nisbat_sektor": 0.45}
    chang = {"ulush_foiz": 55.0}
    harorat = {"r": 0.25}
    rekon = {"ulush_foiz": 5.0}
    r = A.xulosa(tarkib, pm, chang, harorat, rekon, chang_lift=0.76)
    assert len(r["belgilar"]) == 4
    assert "kamroq" in " ".join(r["belgilar"])
    assert "o'lchov emas" in r["daraja"]


def test_xulosa_belgisiz():
    r = A.xulosa({}, {"farq": 0.2, "nisbat_sektor": 0.7}, {"ulush_foiz": 10.0},
                 {"r": -0.5}, {"ulush_foiz": 80.0}, chang_lift=1.0)
    assert r["belgilar"] == ["belgilar aralash — qo'shimcha o'lchov (kimyoviy tarkib) kerak"]


def test_xulosa_chang_lift_yuqori():
    r = A.xulosa({}, {"farq": 0.2, "nisbat_sektor": 0.7}, {"ulush_foiz": 30.0}, {"r": 0.0},
                 {"ulush_foiz": 80.0}, chang_lift=1.4)
    assert any("mexanik manba" in b for b in r["belgilar"])


def test_xulosa_chang_umumiy_ogohlantirish():
    r = A.xulosa({}, {"farq": 0.2, "nisbat_sektor": 0.7}, {"ulush_foiz": 67.0}, {"r": 0.0},
                 {"ulush_foiz": 80.0})
    assert any("sektor nisbiy sinovi kerak" in b for b in r["belgilar"])
