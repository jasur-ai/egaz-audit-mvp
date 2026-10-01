# -*- coding: utf-8 -*-
"""Umumiy yo'ldagi mobil o'lchov (transsekt) → manba quvvati Q (teskari masala).

Model: uzluksiz nuqtaviy manba uchun ko'ndalang-integrallangan Gauss tenglamasi
(ground-level, shamol bo'ylab x masofada):

    C(x) = Q / (√(2π) · σ_z(x) · U) · exp(−H² / (2 σ_z²))        [kg/m³]

Bu yerdan Q (kg/s):

    Q = C · √(2π) · σ_z · U · exp(+H² / (2 σ_z²))

Bu — **manba tomon ruxsat kerak bo'lmagan** yo'l: o'lchov ochiq yo'lda, manba
panjara ortida qoladi. σ_z Pasquill–Gifford sinfi va masofadan baholanadi (yoki
o'lchanadi) — model xatosi ±40–70% bo'lishi normal.

Halollik: Q bahosi **pastki chegara** sifatida ishlatiladi («manba shundan kam
bo'lishi mumkin emas» degan ma'noda emas, balki «o'lchangan yo'nalishda shu
quvvat ko'rindi»). Ortiqcha manba (transport, boshqa korxona) — asosiy xato manbai,
shuning uchun fon nazorati (`background_check`) majburiy.
"""
from __future__ import annotations

import math
from typing import Any, Iterable

SQRT_2PI = math.sqrt(2 * math.pi)


def invert_q(c_kg_m3: float, u_ms: float, sigma_z_m: float, h_m: float = 0.0) -> float:
    """Bitta o'tishdan Q (kg/s). `c_kg_m3` — fon ayirilgan konsentratsiya."""
    if c_kg_m3 < 0:
        raise ValueError("konsentratsiya (fon ayirilgandan keyin) manfiy bo'lmaydi")
    if u_ms <= 0 or sigma_z_m <= 0:
        raise ValueError("shamol > 0 va σ_z > 0 bo'lishi shart")
    if h_m < 0:
        raise ValueError("H ≥ 0")
    return c_kg_m3 * SQRT_2PI * sigma_z_m * u_ms * math.exp(h_m ** 2 / (2 * sigma_z_m ** 2))


def relative_error(rel_c: float, rel_u: float, rel_sz: float) -> float:
    """Q ning nisbiy xatosi (kvadratik yig'indi) — σ_z model xatosi kiradi."""
    for r, nom in ((rel_c, "rel_c"), (rel_u, "rel_u"), (rel_sz, "rel_sz")):
        if r < 0:
            raise ValueError(f"{nom} manfiy bo'lmaydi")
    return math.sqrt(rel_c ** 2 + rel_u ** 2 + rel_sz ** 2)


def background_check(c_upwind_kg_m3: float, c_road_kg_m3: float) -> dict[str, Any]:
    """Fon nazorati: yo'ldagi fon o'lchovga nisbatan juda katta bo'lsa — o'lchov yaroqsiz."""
    if c_road_kg_m3 < 0 or c_upwind_kg_m3 < 0:
        raise ValueError("konsentratsiyalar manfiy bo'lmaydi")
    if c_road_kg_m3 == 0:
        raise ValueError("c_road = 0")
    share = c_upwind_kg_m3 / c_road_kg_m3
    return {
        "fon_ulushi": round(share, 3),
        "yaroqli": share <= 0.5,
        "daraja": "yaroqli" if share <= 0.5 else ("chegarada" if share <= 0.8 else "yaroqsiz"),
        "izoh": "Fon yo'l qiymatining yarmidan ko'p bo'lsa, Q xatosi tez o'sadi "
                "(fon ayirish xatosi to'g'ridan-to'g'ri Q ga o'tadi).",
    }


def fit_campaign(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Kampaniya (bir nechta o'tish) bo'yicha Q ni vaznli o'rtachalashtirish.

    Har bir qator: {"c": kg/m³ (fon ayirilgan), "u": m/s, "sigma_z": m, "h": m (ixtiyoriy),
                    "rel_c": %, "rel_u": %, "rel_sz": % (nisbiy xatolar, kasrda)}
    Vazn: 1/σ_Q². Natija: Q_ort (kg/s), standart xato, 95% oraliq, tarmoqlanish (scatter).
    """
    qs, ws, items = [], [], []
    for r in rows:
        c, u, sz = float(r["c"]), float(r["u"]), float(r.get("sigma_z", 0.0))
        h = float(r.get("h", 0.0))
        q = invert_q(c, u, sz, h)
        rel = relative_error(float(r.get("rel_c", 0.15)), float(r.get("rel_u", 0.15)),
                             float(r.get("rel_sz", 0.35)))
        if rel <= 0:
            raise ValueError("nisbiy xato > 0 bo'lishi shart")
        qs.append(q)
        ws.append(1.0 / ((q * rel) ** 2))
        items.append({"q_kg_s": q, "rel_xato": round(rel, 3), "manba": r.get("manba", "transsekt")})

    w_sum = sum(ws)
    q_mean = sum(q * w for q, w in zip(qs, ws)) / w_sum
    var = 1.0 / w_sum
    se = math.sqrt(var)
    spread = (max(qs) - min(qs)) / q_mean if q_mean > 0 else None
    return {
        "otishlar": len(qs),
        "q_kg_s": round(q_mean, 6),
        "standart_xato": round(se, 6),
        "ishonch_95": [round(max(q_mean - 1.96 * se, 0), 6), round(q_mean + 1.96 * se, 6)],
        "tarqoqlik_foiz": round(spread * 100, 1) if spread is not None else None,
        "qatorlar": items,
        "ogohlantirish": ("Tarqoqlik 100%+ — model yoki manba barqaror emas, o'tishlarni ko'paytirish kerak"
                          if spread is not None and spread > 1.0 else None),
        "izoh": "Vaznli o'rtacha 1/σ² bo'yicha; sistematik xato (σ_z modeli, fon) o'rtachalashda "
                "kamaymaydi — u oraliqdan tashqarida qoladi.",
    }


def plan_campaign(rel_target: float, rel_single: float) -> dict[str, Any]:
    """Maqsadli aniqlikka yetish uchun minimal o'tishlar soni: n = ⌈(σ₁/σ_maqsad)²⌉."""
    if rel_target <= 0 or rel_single <= 0:
        raise ValueError("nisbiy xatolar > 0")
    n = math.ceil((rel_single / rel_target) ** 2)
    return {
        "otishlar_kerak": n,
        "maqsad": round(rel_target, 3),
        "bitta_otish_xatosi": round(rel_single, 3),
        "izoh": "Bu **tasodifiy** xato uchun; sistematik xato (model) kamaymaydi — "
                "uning uchun mustaqil usul (orbita, pastdan-yuqoriga) kerak.",
        "chora": "Har o'tishda fon (yuqori tomon) ham o'lchanadi — fon xatosi Q ga to'g'ridan-to'g'ri o'tadi.",
    }
