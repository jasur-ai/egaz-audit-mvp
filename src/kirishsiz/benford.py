# -*- coding: utf-8 -*-
"""Statistik skrining — Benford qonuni va dumaloq raqam belgilari.

Manba (mezonlar): Nigrini (2012) MAD oraliqlari, maqolada keltirilganidek:
  1-raqam:  <0,006 yaqin · 0,006–0,012 maqbul · 0,012–0,015 chegarada · >0,015 mos emas
  2-raqam:  <0,008 · 0,008–0,010 · 0,010–0,012 · >0,012
  1-2 raqam: <0,0012 · 0,0012–0,0018 · 0,0018–0,0022 · >0,0022
  χ²(8 df) kritik: 15,507 (5%) · 20,090 (1%)
  https://link.springer.com/article/10.1007/s00181-025-02876-0 (2026-02-04)

MUHIM (halollik qoidasi): Benford chetlanishi **firibgarlikni isbotlamaydi**.
Sabablari: kichik namuna (n < 100 kuchsiz), datchik diapazoni, yaxlitlash qoidasi,
birlashgan o'lchovlar. Shuning uchun bu modul isbot kuchi 1 (faqat signal).
"""
from __future__ import annotations

import math
from typing import Any, Iterable

MAD_LABELS = [
    (0.006, "yaqin mos"),
    (0.012, "maqbul"),
    (0.015, "chegarada"),
    (float("inf"), "mos emas"),
]
MAD_LABELS_SECOND = [(0.008, "yaqin mos"), (0.010, "maqbul"), (0.012, "chegarada"), (float("inf"), "mos emas")]
MAD_LABELS_FIRST_TWO = [(0.0012, "yaqin mos"), (0.0018, "maqbul"), (0.0022, "chegarada"), (float("inf"), "mos emas")]

CHI2_CRIT_8DF = {0.05: 15.507, 0.01: 20.090}
MIN_N_FOR_POWER = 100


def first_digit(x: float) -> int:
    """Birinchi muhim raqam (0,00456 → 4; 123 → 1; 0 → xato)."""
    x = abs(float(x))
    if x == 0 or not math.isfinite(x):
        raise ValueError("qiymat noldan farqli va chekli bo'lishi shart")
    while x < 1:
        x *= 10
    while x >= 10:
        x /= 10
    return int(x)


def second_digit(x: float) -> int:
    """Ikkinchi muhim raqam (0,00456 → 5)."""
    d1 = first_digit(x)
    x = abs(float(x))
    while x < 1:
        x *= 10
    while x >= 10:
        x /= 10
    return int((x - d1) * 10)


def benford_probs(mode: str = "1") -> dict[int, float]:
    """Benford ehtimolliklari: mode '1' (1–9), '2' (0–9), '12' (10–99)."""
    if mode == "1":
        return {d: math.log10(1 + 1 / d) for d in range(1, 10)}
    if mode == "2":
        return {d: sum(math.log10(1 + 1 / (10 * d1 + d)) for d1 in range(1, 10)) for d in range(0, 10)}
    if mode == "12":
        return {d: math.log10(1 + 1 / d) for d in range(10, 100)}
    raise ValueError("mode: '1', '2' yoki '12'")


def _chi2_sf(x: float, k: int) -> float:
    """χ² taqsimotining yuqori dum ehtimoli P(X > x), k erkinlik darajasi (regulyar gamma)."""
    if x <= 0:
        return 1.0
    a, xx = k / 2.0, x / 2.0
    # pastki regulyar gamma P(a, x) — seriya + davomli kasr
    if xx < a + 1:
        term = 1.0 / a
        total = term
        n = a
        for _ in range(500):
            n += 1
            term *= xx / n
            total += term
            if abs(term) < abs(total) * 1e-14:
                break
        p_lower = total * math.exp(-xx + a * math.log(xx) - math.lgamma(a))
    else:
        # davomli kasr (Lentz)
        tiny = 1e-300
        b = xx + 1 - a
        c = 1 / tiny
        d = 1 / b if b != 0 else 1 / tiny
        h = d
        for i in range(1, 500):
            an = -i * (i - a)
            b += 2
            d = an * d + b
            if abs(d) < tiny:
                d = tiny
            c = b + an / c
            if abs(c) < tiny:
                c = tiny
            d = 1 / d
            delta = d * c
            h *= delta
            if abs(delta - 1) < 1e-14:
                break
        p_lower = 1 - math.exp(-xx + a * math.log(xx) - math.lgamma(a)) * h
    p_lower = min(max(p_lower, 0.0), 1.0)
    return 1 - p_lower


def _mad(observed: dict[int, float], expected: dict[int, float]) -> float:
    return sum(abs(observed.get(d, 0.0) - p) for d, p in expected.items()) / len(expected)


def _label(mad: float, mode: str) -> str:
    table = {"1": MAD_LABELS, "2": MAD_LABELS_SECOND, "12": MAD_LABELS_FIRST_TWO}[mode]
    for bound, label in table:
        if mad < bound:
            return label
    return table[-1][1]


def analyse(values: Iterable[float], mode: str = "1") -> dict[str, Any]:
    """Benford tahlili: kuzatilgan/expected taqsimot, MAD (+label), χ² (+p), nazoratlar."""
    vals = [float(v) for v in values if v is not None and math.isfinite(float(v)) and float(v) != 0]
    n = len(vals)
    if n == 0:
        raise ValueError("bo'sh ketma-ketlik")
    def _norm(v: float) -> float:
        """[1;10) oralig'iga keltirish (birinchi muhim raqam 1–9 bo'lgan ko'rinish)."""
        x = abs(float(v))
        while x < 1:
            x *= 10
        while x >= 10:
            x /= 10
        return x

    if mode == "1":
        key = first_digit
    elif mode == "2":
        key = second_digit
    else:  # '12' — birinchi ikki raqam (10…99)
        key = lambda v: int(_norm(v) * 10)  # noqa: E731

    counts: dict[int, int] = {}
    for v in vals:
        d = key(v)
        counts[d] = counts.get(d, 0) + 1
    expected = benford_probs(mode)
    observed = {d: counts.get(d, 0) / n for d in expected}
    mad = _mad(observed, expected)
    chi2 = sum((counts.get(d, 0) - n * p) ** 2 / (n * p) for d, p in expected.items())
    dof = len(expected) - 1
    p_value = _chi2_sf(chi2, dof)

    ogoh = []
    if n < MIN_N_FOR_POWER:
        ogoh.append(f"n={n} < {MIN_N_FOR_POWER} — test kuchi past, natija ko'rsatkich sifatida ham cheklangan")
    if mode == "1" and any(counts.get(d, 0) == 0 for d in range(1, 10)):
        ogoh.append("ba'zi raqamlar umuman uchramadi — taqsimot uzilgan")

    return {
        "n": n,
        "mode": mode,
        "kuzatilgan": {str(d): round(observed[d], 4) for d in expected},
        "kutilgan": {str(d): round(expected[d], 4) for d in expected},
        "madv": round(mad, 5),
        "madv_bahosi": _label(mad, mode),
        "chi2": round(chi2, 3),
        "dof": dof,
        "p_qiymat": round(p_value, 4),
        "muhim_5foiz": p_value < 0.05,
        "ogohlantirish": ogoh,
        "izoh": "Signal faqat: Benford chetlanishi firibgarlikni isbotlamaydi "
                "(Nigrini 2012 mezonlari; texnik sabablar ham shunday taqsim beradi).",
        "isbot_kuchi": 1,
    }


def round_number_share(values: Iterable[float]) -> dict[str, Any]:
    """Oxirgi (eng kichik muhim) raqami 0 yoki 5 bo'lgan qiymatlar ulushi.

    Usul: qiymatning eng qisqa aniq o'nlik ko'rinishi (Python `repr`) olinadi, oxirgi raqam
    o'qiladi. Qiymat 10 dan katta/kichik eksponentada bo'lsa — o'tkazib yuboriladi.
    Tabiiy o'lchov qatorida kutilgan ulush ≈ 0,20 (10 raqamdan 2 tasi).
    Aniq statistik chegara yo'q: ≥0,40 — qo'lda yozish/dumaloqlash signali (skrining).
    """
    digits = []
    skipped = 0
    for v in values:
        if v is None:
            continue
        v = float(v)
        if v == 0 or not math.isfinite(v):
            continue
        r = repr(abs(v))
        if "e" in r or "E" in r:
            skipped += 1
            continue
        r = r.rstrip("0").rstrip(".") if "." in r else r
        last = r[-1]
        if last.isdigit():
            digits.append(last)
    if not digits:
        raise ValueError("tahlil uchun yaroqli qiymat yo'q")
    share = sum(1 for d in digits if d in ("0", "5")) / len(digits)
    return {
        "n": len(digits),
        "otkazib_yuborilgan": skipped,
        "ulush": round(share, 3),
        "kutilgan": 0.2,
        "signal": share >= 0.4,
        "izoh": "Kutilgan ≈0,20; ≥0,40 — qo'lda tuzatish/dumaloqlash signali (skrining, isbot emas).",
    }
