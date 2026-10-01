# -*- coding: utf-8 -*-
"""Huquqiy asos registri testlari — R54 (qonuniylik qatlami)."""
from __future__ import annotations

import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.kirishsiz import huquqiy_asos as H  # noqa: E402


def test_tekshir_muammosiz():
    t = H.tekshir()
    assert t["muammolar"] == [], t["muammolar"]
    assert t["holat"] == "ok"
    assert t["hujjatlar"] == len(H.HUJJATLAR)
    assert t["foydalanilmagan_hujjatlar"] == []


def test_har_elementda_kamida_ikki_asos():
    for element, kalitlar in H.XARITA.items():
        assert len(kalitlar) >= H.MIN_ASOS, element
        assert len(set(kalitlar)) == len(kalitlar), f"{element}: takroriy asos"


def test_hujjatlarda_manba_yoki_izoh_bor():
    for h in H.HUJJATLAR:
        assert h.get("manba") or h.get("izoh"), h["id"]
        assert h.get("band"), h["id"]
        assert isinstance(h.get("sana"), str) and len(h["sana"]) == 10, h["id"]


def test_sakkizta_kirishsiz_yol_qoplangan():
    yollar = [e for e in H.XARITA if e.startswith("yol:")]
    assert len(yollar) == 8, yollar
    for e in yollar:
        assert len(H.asoslar(e)) >= 2


def test_havola_matni_takrorlanmaydi():
    m = H.havola_matni(["yol:requests_gen (Aarhus talabi)", "tashkiliy:xatlar va apellyatsiya"])
    assert m.startswith("Huquqiy asos:")
    assert "Aarhus" in m and "Konstitutsiya" in m
    # ikkala element bir xil asoslarga tayansa ham, ro'yxat takrorlanmaydi
    assert m.count("49-modda") == 1
    qisqa = H.havola_matni(["yol:requests_gen (Aarhus talabi)"], qisqa=True)
    assert "[" not in qisqa and len(qisqa) < len(m)


def test_statistika():
    s = H.statistika()
    assert s["jami"] == len(H.HUJJATLAR)
    assert sum(s["tur"].values()) == s["jami"]
    assert sum(s["daraja"].values()) == s["jami"]
    assert s["daraja"].get("A", 0) >= 8
    # manbasi hali qo'shilmagan hujjatlar ochiq ko'rsatiladi
    assert set(s["manbasiz"]) == {"pf-69", "ghg-qonuni", "ndc-3"}


def test_daraja_faqat_A_B_S():
    assert {h["daraja"] for h in H.HUJJATLAR} <= {"A", "B", "S"}


def test_xato_holatlari():
    with pytest.raises(KeyError):
        H.hujjat("yoq-bunday")
    with pytest.raises(KeyError):
        H.asoslar("yoq:bunday element")


def test_filtrlar():
    farmonlar = H.hujjatlar(tur="Farmon")
    assert len(farmonlar) >= 6
    assert all(h["tur"] == "Farmon" for h in farmonlar)
    assert all(h["daraja"] == "A" for h in H.hujjatlar(daraja="A"))


def test_kirill_aralashmasi_yoq():
    matn = " ".join(str(v) for h in H.HUJJATLAR for v in h.values() if isinstance(v, str))
    matn += " ".join(H.XARITA)
    assert not re.search(r"[\u0400-\u04FF]", matn), "registrda kirill harfi bor"


def test_qamrov_va_matn():
    q = H.qamrov()
    assert q["elementlar"] == len(H.XARITA)
    assert q["asoslar_jami"] == sum(len(v) for v in H.XARITA.values())
    assert q["zaif_elementlar"] == []
    assert q["eng_kam"] >= H.MIN_ASOS
    m = H.matn()
    assert "HUQUQIY ASOS XARITASI" in m and "Tekshiruv: ok" in m
    assert "yol:requests_gen" in m


def test_xat_matnida_registrdan_huquqiy_asos():
    """R54: so'rov xatiga registr asosidagi huquqiy blok tushadi."""
    from src.kirishsiz import requests_gen as R
    assert len(R.MANBALAR) >= 5
    r = R.build_request("Boshqarma", "olchov", sana="2026-10-05")
    assert "Huquqiy asos:" in r["matn"]
    # kamida 4 xil hujjat nomi xat ichida ko'rinadi
    for kalit in ("49-modda", "Aarhus", "05.05.2014"):
        assert kalit in r["matn"], kalit
    assert "PQ-343" in r["matn"]
    assert set(r["manbalar"]) == set(R.MANBALAR)


def test_barcha_elementlar_uchun_havola_ishlaydi():
    for e in H.XARITA:
        m = H.havola_matni([e], qisqa=True)
        assert m.startswith("Huquqiy asos:") and len(m.splitlines()) >= 3, e
