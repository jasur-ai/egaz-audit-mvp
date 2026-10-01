# -*- coding: utf-8 -*-
"""Retseptorlar reyestri — shahar nuqtalari bo'yicha alohida ekranlar (R50, B-qatlam 6-qadam).

Nega kerak: Toshkent markazidagi ekran **uzoq manbalarni** (54–67 km: sement zavodlari, kon-metallurgiya)
faqat zaif ko'rsatadi — shahar foni ularni bosib ketadi. Shu sababli har bir sanoat zonasi uchun
**o'z retseptori** va **o'z meteorologiyasi** (ERA5, o'sha nuqta) ishlatiladi.

Har bir yozuvda: koordinata + manba (URL) + sana + ishonch darajasi.
ERA5 katak ogohlantirishi: 0,25° ≈ 25 km — yaqin shaharlar bir katakka tushishi mumkin (kod buni tekshiradi).
"""
from __future__ import annotations

import hashlib
import json
import os
from typing import Any

from . import facilities as F

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RETSEPTOR_FAYL = os.path.join(ROOT, "data", "public", "retseptorlar_uz.json")

MAJBURIY = ("nom", "lat", "lon", "manba", "sana", "daraja")

# Zaxira nusxa (fayl bo'lmasa) — har birida manba majburiy
ZAXIRA = {
    "retseptorlar": [
        {"nom": "Toshkent markaz", "lat": 41.311, "lon": 69.240,
         "manba": "loyiha bazaviy nuqtasi (barcha A-qatlam hisobotlari shu nuqtada)",
         "sana": "2026-10-01", "daraja": "C", "izoh": "A-qatlam ekrani uchun asosiy retseptor"},
        {"nom": "Ohangaron", "lat": 40.905354, "lon": 69.6400706,
         "manba": "OpenStreetMap Nominatim (relation 18507147)",
         "sana": "2026-10-01", "daraja": "C", "izoh": "sement klasteri markazida"},
        {"nom": "Angren", "lat": 41.0212207, "lon": 70.0795361,
         "manba": "OpenStreetMap Nominatim (relation 7774377)",
         "sana": "2026-10-01", "daraja": "C", "izoh": "ko'mir zonasi (Angren IES) — reyestr kengaytirilishi kerak"},
        {"nom": "Olmaliq", "lat": 40.845729, "lon": 69.6071609,
         "manba": "OpenStreetMap Nominatim (relation 7726941)",
         "sana": "2026-10-01", "daraja": "C", "izoh": "kon-metallurgiya zonasi (AGMK)"},
    ]
}


def load(path: str = RETSEPTOR_FAYL) -> list[dict[str, Any]]:
    """Retseptorlar reyestrini o'qish; manbasiz yozuv rad etiladi."""
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        yozuvlar = data.get("retseptorlar", [])
    else:
        yozuvlar = ZAXIRA["retseptorlar"]
    tozalangan = []
    for y in yozuvlar:
        yetishmaydi = [k for k in MAJBURIY if not y.get(k)]
        if yetishmaydi:
            raise ValueError(f"retseptor yozuvida manba maydonlari yo'q: {y.get('nom')} → {yetishmaydi}")
        tozalangan.append(dict(y))
    return tozalangan


def nomlar(path: str = RETSEPTOR_FAYL) -> list[str]:
    return [r["nom"] for r in load(path)]


def top(nom: str, path: str = RETSEPTOR_FAYL) -> dict[str, Any]:
    for r in load(path):
        if r["nom"].lower() == nom.lower():
            return r
    raise KeyError(f"retseptor topilmadi: {nom} (mavjud: {', '.join(nomlar(path))})")


def yaqin_obyektlar(nom: str, radius_km: float = 30.0, path: str = RETSEPTOR_FAYL) -> list[dict[str, Any]]:
    """Retseptor atrofidagi nomzod obyektlar (facilities reyestridan)."""
    r = top(nom, path)
    return [x for x in F.from_receptor(r["lat"], r["lon"]) if x["masofa_km"] <= radius_km]


def data_fayllar(nom: str, tur: str = "aq") -> str:
    """Shu retseptorga tegishli ma'lumot fayli yo'li (mavjud bo'lmasa — baribir qaytaradi)."""
    xarita = {
        "Toshkent markaz": {"aq": "data/public/aq_180kun.csv",
                            "shamol": "data/public/wind_era5_180kun.csv"},
        "Ohangaron": {"aq": "data/public/aq_Ohangaron_180kun.csv",
                      "shamol": "data/public/wind_Ohangaron_180kun.csv"},
        "Angren": {"aq": "data/public/aq_Angren_180kun.csv",
                   "shamol": "data/public/wind_Angren_180kun.csv"},
        "Olmaliq": {"aq": "data/public/aq_Olmaliq_180kun.csv",
                    "shamol": "data/public/wind_Olmaliq_180kun.csv"},
    }
    return xarita.get(nom, {}).get(tur, "")


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(65536), b""):
            h.update(blk)
    return h.hexdigest()


def era5_katak_tekshiruvi(juftlar: dict[str, str]) -> dict[str, Any]:
    """Bir xil ERA5 katakka tushgan retseptorlarni aniqlash (bir xil SHA → bir xil katak)."""
    xesh: dict[str, list[str]] = {}
    for nom, path in juftlar.items():
        if not path or not os.path.exists(path):
            continue
        xesh.setdefault(sha256(path), []).append(nom)
    guruhlar = [v for v in xesh.values() if len(v) > 1]
    return {"tekshirildi": len(xesh), "bir_xil_katak": guruhlar,
            "ogohlantirish": ("Bir katakdagi retseptorlar meteorologiya bo'yicha **farqlanmaydi** "
                              "(ERA5 0,25° ≈ 25 km). Shunday bo'lsa, ular alohida ekran emas — "
                              "bitta hudud sifatida ko'riladi.") if guruhlar else None}


def qiymat_xulosasi(seriyalar: dict[str, list]) -> dict[str, Any]:
    """Retseptor bo'yicha modda o'rtachasi / P90 (qiyosiy jadval uchun)."""
    from .screener import to_float

    out: dict[str, Any] = {}
    for nom, s in seriyalar.items():
        v = [x for x in (to_float(y) for y in s) if x is not None]
        if not v:
            out[nom] = {"xato": "ma'lumot yo'q"}
            continue
        v.sort()
        p90 = v[min(len(v) - 1, int(round(0.9 * (len(v) - 1))))]
        out[nom] = {"n": len(v), "ort": round(sum(v) / len(v), 2), "p90": round(p90, 2),
                    "maks": round(v[-1], 2)}
    return out
