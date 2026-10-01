# -*- coding: utf-8 -*-
"""S6b — Ochiq qoidalar kanali (R41, gibrid aniqlash).

Nega: IF (izolyatsiya o'rmoni) yuqori o'lchamda **yagona-feature signallarini suyultiradi**.
Diagnostika (R41): `offsets_own_dev` yakka-feature AUC = 0,93 (A7), lekin IF A7 ning atigi
13% ini topadi. Shu sababli model yoniga **shaffof, audit qilinadigan qoidalar** qo'shiladi:
operator ham, sud ham har bir qoidani bir jumlada tekshira oladi (TZ §7 tamoyil 3:
explainability-first).

Muhim intizom:
  * Chegaralar **validatsiya oynasida** tanlanadi (train tail: q16–17), test davri tanlovga
    KIRMAYDI — p-hacking yo'q. Tanlangan chegaralar `models/metadata.json` ga yoziladi.
  * Har qoida bitta maqsad turni tutadi; kanal **IF skoriga qo'shiladi** (union), modelni
    almashtirmaydi.
  * A8 uchun qoida ATAYLAB yo'q: orakul tahlili (implied_ghg'ni bilgan ideal detektor)
    AUC≈0,59 ko'rsatadi — yuqori aniqlikdagi qoida mavjud emas, shuning uchun yozilmaydi
    (halol chegara, eval_report.md §cheklovlar).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# Nomzod qoidalar: (nomi, feature, yo'nalish, maqsad tur, izoh)
RULES = [
    ("R-A5 aktivlik kross-tekshiruvi", "prod_report_gap", ">=", "A5",
     "hisobot ishlab chiqarishi mustaqil statistikadan X% yuqori"),
    ("R-A7 offset devori", "offsets_own_dev", ">=", "A7",
     "hisobot offseti o'z tarixining medianasidan X× yuqori"),
]


def _rule_f1(feat: pd.DataFrame, mask: np.ndarray, col: str, op: str, thr: float,
             y: np.ndarray, atype: np.ndarray, target: str) -> tuple:
    flag = (feat[col].to_numpy() >= thr) if op == ">=" else (feat[col].to_numpy() <= thr)
    f = flag & mask
    lab = (atype == target) & mask
    tp = int((f & lab).sum())
    fp = int((f & (y == 0)).sum())
    fn = int((~f & lab).sum())
    p = tp / max(tp + fp, 1)
    r = tp / max(tp + fn, 1)
    f1 = 2 * p * r / max(p + r, 1e-9)
    return f1, p, r, tp, fp, fn


# Inson o'qiydigan chegara nomzodlari (float shovqinidan xoli)
GRID_ABS = (0.0, 0.01, 0.02, 0.03, 0.05, 0.07, 0.10, 0.15, 0.20, 0.30, 0.50, 0.70, 1.00, 1.50, 2.00)


def select_thresholds(feat: pd.DataFrame, meta: pd.DataFrame, val_mask: np.ndarray,
                      n_grid: int = 40, min_precision: float = 0.30,
                      min_support: int = 20) -> tuple:
    """Har qoida chegarasi validatsiya oynasida F1 ni maksimallashtirib tanlanadi.

    Intizom:
      * Nomzod chegaralar **yumaloqlanadi (4 xona)** va metrikalar aynan yumaloqlangan qiymat
        bilan hisoblanadi — tanlov natijasi qo'llanilganda bir xil bo'lishi shart.
      * `min_precision` dan past aniqlikdagi qoida **rad etiladi** (shovqin kanali bo'lmasin);
        rad etilganlar sababi bilan qaytariladi (hisobotda ko'rsatiladi).

    Qaytadi: (qabul qilingan qoidalar dict, rad etilganlar list).
    """
    y = meta["label"].to_numpy()
    atype = meta["anomaly_type"].fillna("").to_numpy()
    accepted, rejected = {}, []
    for name, col, op, target, note in RULES:
        # Nomzod chegaralar — **inson o'qiydigan** qat'iy qiymatlar (audit uchun muhim),
        # faqat shu feature diapazoniga tushadiganlari olinadi; juda kam qatorni
        # belgilaydigan nomzod (support < min_support) tashlab ketiladi.
        x = feat.loc[val_mask, col].to_numpy()
        grid = [t for t in GRID_ABS if x.min() <= t <= x.max()]
        grid += [round(float(np.quantile(x, q)), 2) for q in (0.9, 0.95, 0.99)]
        grid = sorted({t for t in grid})
        best = None
        for thr in grid:
            f1, p, r, tp, fp, fn = _rule_f1(feat, val_mask, col, op, thr, y, atype, target)
            if tp + fp < min_support:          # deyarli hech narsani belgilamaydi
                continue
            if best is None or f1 > best[0]:
                best = (f1, thr, p, r, tp, fp, fn)
        if best is None or best[2] < min_precision:
            rejected.append({"nomi": name, "sabab": f"validatsiyada aniqlik {best[2] if best else 0:.3f} "
                                                     f"< {min_precision} (signal yo'q)"})
            continue
        accepted[name] = {"feature": col, "op": op, "thr": best[1], "target": target,
                          "val_f1": round(best[0], 3), "val_precision": round(best[2], 3),
                          "val_recall": round(best[3], 3),
                          "val_counts": {"tp": best[4], "fp": best[5], "fn": best[6]},
                          "izoh": note}
    return accepted, rejected


def apply_rules(feat: pd.DataFrame, thresholds: dict) -> tuple:
    """Qoidalarni qatorlarga qo'llaydi. Qaytadi: (flag array, {qoida: flag array})."""
    flags = {}
    for name, cfg in thresholds.items():
        col, op, thr = cfg["feature"], cfg["op"], cfg["thr"]
        flags[name] = ((feat[col].to_numpy() >= thr) if op == ">=" else (feat[col].to_numpy() <= thr))
    any_flag = np.zeros(len(feat), dtype=bool)
    for f in flags.values():
        any_flag |= f
    return any_flag, flags
