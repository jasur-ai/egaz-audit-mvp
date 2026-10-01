# -*- coding: utf-8 -*-
"""Maishiy isitish moduli testlari — R53 (miqdoriy atributsiya)."""
from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.kirishsiz import isitish as I  # noqa: E402


def test_uy_xo_jaliklari():
    uy = I.uy_xo_jaliklari(3164.0, kishi_uy=3.8)
    assert uy == pytest.approx(832631.578, rel=1e-6)
    # kishi soni oshsa uy kamayadi
    assert I.uy_xo_jaliklari(3164.0, 4.5) < uy < I.uy_xo_jaliklari(3164.0, 3.5)


def test_uy_xo_jaliklari_xato():
    with pytest.raises(ValueError):
        I.uy_xo_jaliklari(1000.0, kishi_uy=0.0)


def test_energiya_gj():
    assert I.energiya_gj(gaz_m3=2500.0) == pytest.approx(90.0)
    assert I.energiya_gj(komir_t=1.0) == pytest.approx(20.0)
    assert I.energiya_gj(gaz_m3=1000.0, komir_t=2.0) == pytest.approx(76.0)


def test_emissiya_va_ko_mir_gaz_nisbati():
    gaz = I.emissiya_g(1000.0, "gaz", "pm25")
    komir = I.emissiya_g(1000.0, "komir", "pm25")
    assert gaz == pytest.approx(1200.0)
    assert komir == pytest.approx(398000.0)
    assert komir / gaz == pytest.approx(331.6667, rel=1e-4)


def test_emissiya_xato():
    with pytest.raises(KeyError):
        I.emissiya_g(10.0, "yadro", "pm25")
    with pytest.raises(KeyError):
        I.emissiya_g(10.0, "gaz", "ch4")


def test_garmonik_shamol():
    # bir xil qiymatlar — arifmetik o'rtachaga teng
    assert I.garmonik_shamol([3.0] * 5) == pytest.approx(3.0)
    # [1,2,4] → 3 / (1 + 0.5 + 0.25) = 1.7143
    assert I.garmonik_shamol([1.0, 2.0, 4.0]) == pytest.approx(3 / 1.75)
    # sokin soatlar chiqarib tashlanadi; hamma sokin bo'lsa None
    assert I.garmonik_shamol([0.2, 0.3]) is None
    assert I.garmonik_shamol([0.2, 4.0]) == pytest.approx(4.0)
    assert I.garmonik_shamol([None, 4.0]) == pytest.approx(4.0)
    # garmonik o'rtacha arifmetikdan kichik (yumshoq soatlar ko'proq vazn oladi)
    assert I.garmonik_shamol([1.0, 5.0]) < 3.0


def test_quti_modeli_va_teskari_izchillik():
    Q, L, H, u = 194.0, 20000.0, 300.0, 3.16
    c = I.quti_konstentratsiyasi(Q, L, H, u)
    assert c == pytest.approx(Q / (L * H * u) * 1e6, rel=1e-12)
    # teskari: shu konsentratsiyani beradigan oqim — aynan Q
    assert I.talab_emissiya(c, L, H, u) == pytest.approx(Q, rel=1e-12)
    # massaga o'tkazish: 194 g/s × 2319 soat
    assert I.mavsum_massasi_tonna(Q, 2319.0) == pytest.approx(194.0 * 2319 * 3600 / 1e6)
    with pytest.raises(ValueError):
        I.quti_konstentratsiyasi(Q, L, 0.0, u)


def test_kerak_qattiq_ulush_va_ssenariy_izchilligi():
    uy = I.uy_xo_jaliklari(3164.0)
    isitiladigan = uy * 0.352
    talab = 1619.2
    k = I.kerak_qattiq_ulush(talab, isitiladigan, 2500.0, "pm25")
    # ssenariy bilan tekshiruv: shu ulushda jami massa = talab
    s = I.stsenariy(uy, 0.352, 1.0 - k["qattiq_ulush"], 2500.0, 2319.0, 20000.0, 300.0, 3.16)
    assert s["jami_t"] == pytest.approx(talab, rel=1e-9)
    # qattiq ulush 0–1 oralig'ida va gaz hissasi juda kichik
    assert 0.0 < k["qattiq_ulush"] < 1.0
    assert k["gaz_only_t"] < 0.05 * talab


def test_kerak_ulush_yuqori_talabda_os_adi():
    uy = I.uy_xo_jaliklari(3164.0) * 0.352
    a = I.kerak_qattiq_ulush(1000.0, uy, 2500.0)["qattiq_ulush"]
    b = I.kerak_qattiq_ulush(2000.0, uy, 2500.0)["qattiq_ulush"]
    assert b > a


def test_traser_tekshiruvi():
    # kuzatuv: ΔPM 10,24 · ΔCO 238,05 · ΔSO2 5,57 (jonli 365 kun ma'lumotidan)
    t = I.traser_tekshiruvi(10.24, 238.05, 5.57, "komir")
    assert t["kuzatuv"]["pm_co"] == pytest.approx(10.24 / 238.05, rel=1e-9)
    assert t["ef_nisbat"]["pm_co"] == pytest.approx(398.0 / 4600.0, rel=1e-9)
    # kuzatilgan marjinal nisbat ko'mir EF nisbatidan ~2 barobar kichik
    assert 0.4 < t["komir_nisbati"]["pm_co"] < 0.6
    with pytest.raises(ValueError):
        I.traser_tekshiruvi(10.0, 0.0, 1.0)


def test_hisobot_tuzilishi():
    h = I.hisobot(shamol=[3.0] * 10)
    assert h["u_ms"] == pytest.approx(3.0)
    assert h["uy_jami"] == pytest.approx(832631.578, rel=1e-6)
    assert len(h["ssenariylar"]) == 4
    assert 0.0 < h["kerak_ulush"]["qattiq_ulush"] < 1.0
    assert len(h["sezgirlik"]) == 9
    assert h["sezgirlik"]["sayoz aralashish H=200 m"]["talab_t"] < h["sezgirlik"]["chuqur aralashish H=500 m"]["talab_t"]
    # matn ishlab chiqadi va kalit raqamlarni o'z ichiga oladi
    m = I.matn(h)
    assert "MAISHIY ISITISH" in m and "TALAB" in m and "µg/m³" in m


def test_gaz_kerak_pm():
    # 1 619,2 t PM2,5 ni gaz bilan chiqarish uchun ~37,5 mlrd m³ kerak (42,3 mlrd — mamlakat yilligi)
    g = I.gaz_kerak_pm(1619.2)
    assert g["gaz_mlrd_m3"] == pytest.approx(1619.2 * 1e6 / 1.2 / I.GAZ_NCV_GJ_M3 / 1e9, rel=1e-9)
    assert 35.0 < g["gaz_mlrd_m3"] < 40.0
    # ko'mir bilan esa ikki yuz ming tonna atrofida
    assert 180000 < I.yoqilgi_kerak(1619.2, "komir")["komir_t"] < 220000
