# -*- coding: utf-8 -*-
"""Haqiqiy sanoat obyektlari reyestri (nomzodlar) — koordinata + quvvat + manba.

Ma'lumot fayli: `data/public/nomzodlar_uz.json` (har yozuvda URL + sana + tier).

Nima uchun: «taxminiy» nuqtalar bilan atributsiya qilish professional emas — har bir nomzod
**rasmiy manbadan olingan koordinata** bilan turishi kerak. Shu modul shu intizomni kodga
majburlaydi: koordinatasi yoki manbasi yo'q yozuv **yuklanmaydi** (xato beradi).

Nima isbotlanmaydi: reyestr — tekshiriladigan obyektlar ro'yxati, dalil emas. Unda bo'lish
o'zi «ifloslantiruvchi» degani EMAS; yo'qligi ham «toza» degani emas.
"""
from __future__ import annotations

import json
import os
from typing import Any

from .plume import bearing_deg, haversine_m

MAJBURIY_MAYDONLAR = ("nom", "lat", "lon", "tur", "koordinata_manba", "koordinata_url", "sana")


def default_path() -> str:
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(root, "data", "public", "nomzodlar_uz.json")


def load(path: str | None = None) -> dict[str, Any]:
    """Reyestrni o'qish va tekshirish. Maydon yetishmasa — ValueError."""
    p = path or default_path()
    if not os.path.exists(p):
        raise FileNotFoundError(f"nomzodlar fayli topilmadi: {p}")
    with open(p, encoding="utf-8") as f:
        data = json.load(f)
    obyektlar = data.get("obyektlar") or []
    for i, o in enumerate(obyektlar):
        yoq = [m for m in MAJBURIY_MAYDONLAR if not o.get(m)]
        if yoq:
            raise ValueError(f"{i}-yozuvda maydon yetishmaydi: {', '.join(yoq)}")
        if not (-90 <= float(o["lat"]) <= 90) or not (-180 <= float(o["lon"]) <= 180):
            raise ValueError(f"{i}-yozuvda koordinata chegaradan tashqarida: {o['nom']}")
    return data


def obyektlar(path: str | None = None) -> list[dict[str, Any]]:
    return load(path)["obyektlar"]


def from_receptor(lat: float, lon: float, path: str | None = None) -> list[dict[str, Any]]:
    """Har bir nomzod uchun azimut, masofa va radius holatini qo'shadi."""
    data = load(path)
    radius = float(data.get("radius_km", 30))
    out = []
    for o in data["obyektlar"]:
        d = haversine_m(lat, lon, float(o["lat"]), float(o["lon"])) / 1000.0
        out.append({
            "nom": o["nom"], "tur": o["tur"], "lat": o["lat"], "lon": o["lon"],
            "azimut": round(bearing_deg(lat, lon, float(o["lat"]), float(o["lon"])), 1),
            "masofa_km": round(d, 2),
            "radius_km": radius,
            "radiusda": d <= radius,
            "quvvat": o.get("quvvat"), "yoqilgi": o.get("yoqilg'i"),
            "koordinata_manba": o["koordinata_manba"], "koordinata_url": o["koordinata_url"],
            "sana": o["sana"], "tier": o.get("tier"), "izoh": o.get("izoh"),
        })
    return sorted(out, key=lambda x: x["masofa_km"])


def candidates(lat: float, lon: float, radius_km: float | None = None, *,
               path: str | None = None, tur: str | None = None) -> list[dict[str, Any]]:
    """`plume`/`sector` modullari kutadigan formatdagi nomzodlar ro'yxati."""
    rows = from_receptor(lat, lon, path)
    if radius_km is not None:
        rows = [r for r in rows if r["masofa_km"] <= radius_km]
    if tur:
        rows = [r for r in rows if r["tur"] == tur]
    return [{"nom": r["nom"], "lat": r["lat"], "lon": r["lon"], "tur": r["tur"],
             "masofa_km": r["masofa_km"], "azimut": r["azimut"]} for r in rows]


def sektor_guruhlari(lat: float, lon: float, *, path: str | None = None,
                     kenglik: float = 15.0) -> list[dict[str, Any]]:
    """Bir yo'nalishda turgan nomzodlarni guruhlaydi (shamol bilan ajratilmaydigan holat).

    Agar ikki obyekt azimuti `kenglik` darajadan yaqin bo'lsa — shamol tahlili ularni
    **ajratib bera olmaydi**; bu guruh sifatida qaytariladi va xulosada shunday yoziladi.
    """
    rows = from_receptor(lat, lon, path)
    guruhlar: list[dict[str, Any]] = []
    for r in rows:
        qo_shildi = False
        for g in guruhlar:
            if abs(((r["azimut"] - g["markaz"] + 180) % 360) - 180) <= kenglik:
                g["azolar"].append(r["nom"])
                g["markaz"] = round((g["markaz"] * (len(g["azolar"]) - 1) + r["azimut"]) / len(g["azolar"]), 1)
                qo_shildi = True
                break
        if not qo_shildi:
            guruhlar.append({"markaz": r["azimut"], "azolar": [r["nom"]]})
    return [{"markaz": g["markaz"], "azolar": g["azolar"], "ajratilmaydi": len(g["azolar"]) > 1}
            for g in guruhlar]
