# -*- coding: utf-8 -*-
"""Haqiqiy obyektlar reyestri (nomzodlar) testlari — R49.

Tekshiriladi: fayl formati qat'iyligi, majburiy maydonlar, koordinata chegaralari,
masofa/azimut hisobi, radius filtri, yo'nalish guruhlari (ajratilmaydigan holat).
"""
from __future__ import annotations

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.kirishsiz import facilities as F  # noqa: E402

REC = (41.311, 69.240)


def test_default_fayl_mavjud_va_yuklanadi():
    data = F.load()
    assert data["obyektlar"], "reyestr bo'sh bo'lmasligi kerak"
    assert all(o["koordinata_url"].startswith("http") for o in data["obyektlar"])


def test_har_obyektda_manba_va_sana():
    for o in F.obyektlar():
        assert o["koordinata_manba"] and o["koordinata_url"]
        assert len(o["sana"]) == 10 and o["sana"][4] == "-"
        assert o.get("tier") in ("A", "B", "C", "D")


def test_reestrda_taxminiy_nuqtalar_yoq():
    """«taxminiy» so'zi reyestrga kirmasligi kerak — faqat manbali koordinatalar."""
    for o in F.obyektlar():
        assert "taxminiy" not in o["nom"].lower(), o["nom"]


def test_majburiy_maydon_yetishmasa_xato(tmp_path):
    p = tmp_path / "nomzodlar.json"
    p.write_text(json.dumps({"obyektlar": [{"nom": "X", "lat": 41.0, "lon": 69.0}]}), encoding="utf-8")
    with pytest.raises(ValueError) as e:
        F.load(str(p))
    assert "maydon yetishmaydi" in str(e.value)


def test_koordinata_chegarasidan_tashqarida_xato(tmp_path):
    p = tmp_path / "nomzodlar.json"
    p.write_text(json.dumps({"obyektlar": [{
        "nom": "X", "lat": 141.0, "lon": 69.0, "tur": "test",
        "koordinata_manba": "m", "koordinata_url": "http://x", "sana": "2026-01-01"}]}), encoding="utf-8")
    with pytest.raises(ValueError) as e:
        F.load(str(p))
    assert "chegaradan tashqarida" in str(e.value)


def test_fayl_yoq_bolsa_xato(tmp_path):
    with pytest.raises(FileNotFoundError):
        F.load(str(tmp_path / "yoq.json"))


def test_from_receptor_masofa_azimut_radius():
    rows = F.from_receptor(*REC)
    ies = next(r for r in rows if "IES" in r["nom"])
    assert 13.0 < ies["masofa_km"] < 13.6
    assert 54 < ies["azimut"] < 56
    assert ies["radiusda"] is True          # 13,3 km < 30 km
    conch = next(r for r in rows if "Conch" in r["nom"])
    assert conch["radiusda"] is False       # ~67 km
    assert 140 < conch["azimut"] < 141


def test_from_receptor_masofa_boyicha_tartiblangan():
    rows = F.from_receptor(*REC)
    masofalar = [r["masofa_km"] for r in rows]
    assert masofalar == sorted(masofalar)
    assert rows[0]["nom"].startswith("Toshkent IES")


def test_radius_km_reestrdan_olinadi():
    rows = F.from_receptor(*REC)
    assert all(r["radius_km"] == 30.0 for r in rows)


def test_candidates_radius_va_tur_filtri():
    barchasi = F.candidates(*REC, radius_km=100)
    assert len(barchasi) == len(F.obyektlar())
    yaqin = F.candidates(*REC, radius_km=30)
    assert len(yaqin) == 1 and "IES" in yaqin[0]["nom"]
    sement = F.candidates(*REC, radius_km=100, tur="sement")
    assert len(sement) == 2 and all("sement" == c["tur"] for c in sement)
    # qaytgan format atributsiya modullariga mos bo'lishi kerak
    assert {"nom", "lat", "lon"} <= set(yaqin[0])


def test_sektor_guruhlari_ies_va_maxam_ajratilmaydi():
    guruhlar = F.sektor_guruhlari(*REC, kenglik=15)
    ies_guruh = next(g for g in guruhlar if any("IES" in a for a in g["azolar"]))
    assert ies_guruh["ajratilmaydi"] is True
    assert any("Maxam" in a for a in ies_guruh["azolar"])
    assert 55 < ies_guruh["markaz"] < 70


def test_sektor_guruhlari_janubiy_uchlik():
    guruhlar = F.sektor_guruhlari(*REC, kenglik=15)
    janub = next(g for g in guruhlar if len(g["azolar"]) == 3)
    assert janub["ajratilmaydi"] is True
    assert 140 < janub["markaz"] < 160


def test_sektor_guruhlari_kenglik_ozgartirilganda():
    tor = F.sektor_guruhlari(*REC, kenglik=3)
    # 3° kenglikda IES (54,9°) va Maxam (60,1°) ajraladi
    assert len(tor) >= 4


def test_yuklash_keshga_boglanmagan():
    """Ikki marta chaqirilganda bir xil natija (determinizm)."""
    assert F.from_receptor(*REC) == F.from_receptor(*REC)
