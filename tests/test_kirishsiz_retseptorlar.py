# -*- coding: utf-8 -*-
"""Retseptorlar reyestri va yo'nalish profili testlari — R50 (B-qatlam 6-qadam)."""
from __future__ import annotations

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.kirishsiz import retseptorlar as R  # noqa: E402
from src.kirishsiz import sector as S  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAYL = os.path.join(ROOT, "data", "public", "retseptorlar_uz.json")


# ---------------------------------------------------------------- reyestr


def test_reyestr_mavjud_va_manbali():
    rows = R.load()
    assert len(rows) >= 4
    for r in rows:
        assert r["manba"] and r["sana"] and r["daraja"] in ("A", "B", "C", "D")


def test_manbasiz_yozuv_rad_etiladi(tmp_path):
    p = tmp_path / "yomon.json"
    p.write_text(json.dumps({"retseptorlar": [{"nom": "X", "lat": 41.0, "lon": 69.0}]}), encoding="utf-8")
    with pytest.raises(ValueError):
        R.load(str(p))


def test_fayl_yoq_bolsa_zaxira_ishlaydi(tmp_path):
    rows = R.load(str(tmp_path / "yoq.json"))
    assert any(r["nom"] == "Toshkent markaz" for r in rows)


def test_top_nom_boyicha():
    assert R.top("ohangaron")["lat"] == pytest.approx(40.905354)
    with pytest.raises(KeyError):
        R.top("Toshkent")


def test_nomlar_royxati():
    nomlar = R.nomlar()
    assert "Toshkent markaz" in nomlar and "Angren" in nomlar


def test_yaqin_obyektlar_masofa_boyicha_tartib():
    rows = R.yaqin_obyektlar("Ohangaron", 30.0)
    assert rows and rows[0]["nom"].startswith("Akhangarancement")
    assert rows[0]["masofa_km"] < 4
    assert all(r["masofa_km"] <= 30.0 for r in rows)


def test_angren_boeshligi_yopildi():
    """R50 da Angren zonasi bo'shlig'i yopildi: Angren IES (ko'mir) reyestrga qo'shildi."""
    rows = R.yaqin_obyektlar("Angren", 30.0)
    assert len(rows) == 1
    assert "Angren IES" in rows[0]["nom"] and rows[0]["masofa_km"] < 5
    assert rows[0]["tur"] == "energetika"
    # 2 km ichida hech narsa yo'q — retseptor shahar markazi, obyekt undan uzoqroq
    assert R.yaqin_obyektlar("Angren", 2.0) == []


def test_data_fayllar_yollari():
    assert R.data_fayllar("Toshkent markaz", "aq").endswith("aq_180kun.csv")
    assert R.data_fayllar("Ohangaron", "shamol").endswith("wind_Ohangaron_180kun.csv")
    assert R.data_fayllar("Yo'q shahar", "aq") == ""


def test_era5_katak_tekshiruvi_bir_xil(tmp_path):
    p1 = tmp_path / "a.csv"
    p2 = tmp_path / "b.csv"
    p1.write_text("x\n1\n", encoding="utf-8")
    p2.write_text("x\n1\n", encoding="utf-8")
    r = R.era5_katak_tekshiruvi({"A": str(p1), "B": str(p2)})
    assert r["bir_xil_katak"] == [["A", "B"]]
    assert r["ogohlantirish"]


def test_era5_katak_tekshiruvi_farqli(tmp_path):
    p1 = tmp_path / "a.csv"
    p2 = tmp_path / "b.csv"
    p1.write_text("x\n1\n", encoding="utf-8")
    p2.write_text("x\n2\n", encoding="utf-8")
    r = R.era5_katak_tekshiruvi({"A": str(p1), "B": str(p2)})
    assert r["bir_xil_katak"] == [] and r["ogohlantirish"] is None


def test_qiymat_xulosasi_statistika():
    r = R.qiymat_xulosasi({"pm2_5": [1.0] * 8 + [100.0]})
    assert r["pm2_5"]["n"] == 9
    assert r["pm2_5"]["maks"] == pytest.approx(100.0)
    assert r["pm2_5"]["p90"] == pytest.approx(1.0)


def test_qiymat_xulosasi_bosh():
    assert "xato" in R.qiymat_xulosasi({"pm2_5": [None, ""]})["pm2_5"]


def test_haqiqiy_reyestr_fayli_oziladi():
    assert os.path.exists(FAYL)


# ---------------------------------------------------------------- yo'nalish profili


def test_yonalish_profili_choqqi_topadi():
    winds = [80.0] * 30 + [200.0] * 30
    qiymat = [50.0] * 30 + [10.0] * 30
    p = S.yonalish_profili(qiymat, winds, 15.0, 5)
    assert p["cho_qqi"]["burchak"] == 75
    assert p["past"]["burchak"] == 195
    assert p["cho_qqi"]["ort"] == pytest.approx(50.0)


def test_yonalish_profili_kamida_hisobga_olmaydi():
    p = S.yonalish_profili([99.0] + [1.0] * 20, [0.0] + [180.0] * 20, 15.0, kamida=5)
    assert p["cho_qqi"]["burchak"] == 180


def test_yonalish_profili_qadam_xato():
    with pytest.raises(ValueError):
        S.yonalish_profili([1.0], [10.0], 7.0)
    with pytest.raises(ValueError):
        S.yonalish_profili([1.0], [10.0], 0.0)


def test_yonalish_profili_binlar_soni():
    p = S.yonalish_profili([1.0] * 10, [0.0] * 10, 30.0, 1)
    assert len(p["binlar"]) == 12


def test_profil_grafik_chizadi():
    p = S.yonalish_profili([10.0] * 10, [0.0] * 10, 45.0, 1)
    chiz = S.profil_grafik(p)
    assert "burchak" in chiz and "▉" in chiz
    assert S.profil_grafik({"binlar": []}) == "(ma'lumot yo'q)"
