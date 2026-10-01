# -*- coding: utf-8 -*-
"""S6 — baholash harness: metrikalar, biznes taqqoslash, figuralar (TZ §9)."""
from __future__ import annotations

import os

import numpy as np
from sklearn.metrics import (average_precision_score, confusion_matrix, f1_score,
                             precision_score, recall_score, roc_auc_score)


def choose_threshold(train_scores: np.ndarray, contamination: float) -> float:
    """Threshold FAQAT train skorlaridan olinadi (test'ga qaramasdan)."""
    return float(np.quantile(train_scores, 1.0 - contamination))


def rolling_threshold(scores_ref: np.ndarray, periods: np.ndarray, scores: np.ndarray,
                      alert_rate: float = 0.12, window: int = 4, min_n: int = 200) -> dict:
    """Siljuvchi qayta kalibrlash (dreyfga javob, R41).

    Har bir davr `p` uchun threshold = (train skorlari + `p` dan OLDINGI `window` davr skorlari)
    kvantili (1 − alert_rate) — ya'ni **alert ulushi mo'ljalda ushlanadi**. **Faqat skorlar
    ishlatiladi — label'lar emas** (p-hacking yo'q).
    Shu sabab siyosat ishlab chiqarishda ham qo'llaniladi: yangi davr kelganda threshold yangilanadi.
    """
    out: dict = {}
    order = sorted(set(periods.tolist()))
    for i, p_ in enumerate(order):
        prev = [q for q in order[max(0, i - window):i]]
        base = scores_ref
        if prev:
            m = np.isin(periods, prev)
            base = np.concatenate([scores_ref, scores[m]])
        out[p_] = float(np.quantile(base, 1.0 - alert_rate)) if len(base) >= min_n else \
            float(np.quantile(scores_ref, 1.0 - alert_rate))
    return out


def median_slide_threshold(scores_ref: np.ndarray, periods: np.ndarray, scores: np.ndarray,
                           base_thr: float) -> dict:
    """Median-slide qayta kalibrlash (R41) — FPR dreyfini label'siz ushlab turish.

    Mantiq: FPR = P(skor ≥ t | normal) — demak **normal skorlar siljishi** (δ) FPR ni buzadi.
    Median normal qatorlar hukmron bo'lgan sohada yotadi, shuning uchun δ ≈ median_davr − median_train.
    Yangi threshold: `t = base_thr + δ`. Shaffof, audit qilinadigan va taqsimotning siljishiga
    moslashadi (kvantil-shakli o'zgarsa cheklovi bor — eval_report.md da yozilgan).
    """
    med_ref = float(np.median(scores_ref))
    out = {}
    for p_ in sorted(set(periods.tolist())):
        m = periods == p_
        out[p_] = float(base_thr + (float(np.median(scores[m])) - med_ref))
    return out


def metrics_by_period(y_true: np.ndarray, scores: np.ndarray, thr, periods: np.ndarray) -> list:
    """Davr (kvartal) kesimida FPR va recall. `thr` — skalyar yoki {davr: threshold}."""
    rows = []
    for p_ in sorted(set(periods.tolist())):
        m = periods == p_
        t = thr[p_] if isinstance(thr, dict) else thr
        yp = (scores[m] >= t).astype(int)
        yt = y_true[m]
        fp = int(((yp == 1) & (yt == 0)).sum())
        tn = int(((yp == 0) & (yt == 0)).sum())
        tp = int(((yp == 1) & (yt == 1)).sum())
        fn = int(((yp == 0) & (yt == 1)).sum())
        rows.append({"davr": int(p_), "n": int(m.sum()),
                     "fpr": round(fp / (fp + tn), 4) if (fp + tn) else 0.0,
                     "recall": round(tp / max(tp + fn, 1), 4),
                     "threshold": round(float(t), 4),
                     "alerts": fp + tp})
    return rows


def metrics_at(y_true: np.ndarray, scores: np.ndarray, thr: float,
               thr_rows: np.ndarray | None = None) -> dict:
    """Metrikalar. `thr_rows` berilsa — har qator uchun alohida threshold (siljuvchi siyosat);
    AUC/PR-AUC esa barcha skorlardan hisoblanadi (thresholdsiz metrikalar)."""
    y_pred = (scores >= thr_rows).astype(int) if thr_rows is not None else (scores >= thr).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return {
        "precision": round(precision_score(y_true, y_pred, zero_division=0), 4),
        "recall": round(recall_score(y_true, y_pred, zero_division=0), 4),
        "f1": round(f1_score(y_true, y_pred, zero_division=0), 4),
        "roc_auc": round(roc_auc_score(y_true, scores), 4),
        "pr_auc": round(average_precision_score(y_true, scores), 4),
        "fpr": round(fp / (fp + tn), 4) if (fp + tn) else 0.0,
        "tp": int(tp), "fp": int(fp), "fn": int(fn), "tn": int(tn),
        "threshold": round(thr, 4),
    }


def recall_at_top(y_true: np.ndarray, scores: np.ndarray, frac: float = 0.05) -> float:
    k = max(1, int(len(scores) * frac))
    top = np.argsort(-scores)[:k]
    return round(float(y_true[top].sum() / max(1, y_true.sum())), 4)


def per_type_recall(meta, scores: np.ndarray, thr: float) -> dict:
    out = {}
    types = meta["anomaly_type"].fillna("")
    for t in sorted(set(types) - {""}):
        m = types == t
        if m.sum() == 0:
            continue
        out[t] = round(float(((scores >= thr) & m.to_numpy()).sum() / m.sum()), 3)
    return out


def per_type_recall_flags(meta, flags: np.ndarray) -> dict:
    """Tur bo'yicha recall — tayyor alert bayroqlaridan (siljuvchi siyosat va gibrid uchun)."""
    out = {}
    types = meta["anomaly_type"].fillna("")
    for t in sorted(set(types) - {""}):
        m = (types == t).to_numpy()
        if m.sum() == 0:
            continue
        out[t] = round(float((flags & m).sum() / m.sum()), 3)
    return out


def business_compare(y_true: np.ndarray, scores: np.ndarray, n_inspectors: int = 200) -> dict:
    """TZ §9.4: random 200 tekshiruv vs model top-200."""
    base = float(y_true.mean())
    top = np.argsort(-scores)[:n_inspectors]
    hit_model = float(y_true[top].mean())
    return {"baza_ulushi": round(base, 4), "model_top_n_aniqlik": round(hit_model, 4),
            "random_top_n_aniqlik": round(base, 4),
            "yaxshilanish_x": round(hit_model / max(base, 1e-9), 1)}


def make_figures(y_true, scores, meta, thr, outdir, per_type=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from sklearn.metrics import precision_recall_curve, roc_curve

    os.makedirs(outdir, exist_ok=True)
    paths = []

    # 1) PR-kurva
    p, r, _ = precision_recall_curve(y_true, scores)
    fpr, tpr, _ = roc_curve(y_true, scores)
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    ax[0].plot(r, p, lw=1.6)
    ax[0].set_xlabel("Recall"); ax[0].set_ylabel("Precision"); ax[0].set_title("PR-kurva")
    ax[1].plot(fpr, tpr, lw=1.6); ax[1].plot([0, 1], [0, 1], "--", color="gray", lw=0.8)
    ax[1].set_xlabel("FPR"); ax[1].set_ylabel("TPR"); ax[1].set_title("ROC-kurva")
    for a in ax:
        a.grid(alpha=0.3)
    fp = os.path.join(outdir, "pr_roc.png"); fig.tight_layout(); fig.savefig(fp, dpi=130); plt.close(fig)
    paths.append(fp)

    # 2) skor taqsimoti
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(scores[y_true == 0], bins=60, alpha=0.6, label="normal", density=True)
    ax.hist(scores[y_true == 1], bins=60, alpha=0.6, label="anomaliya", density=True)
    ax.axvline(thr, color="red", ls="--", lw=1.2, label=f"threshold={thr:.3f}")
    ax.set_xlabel("Anomaliya skori"); ax.legend(); ax.grid(alpha=0.3)
    fp = os.path.join(outdir, "score_dist.png"); fig.tight_layout(); fig.savefig(fp, dpi=130); plt.close(fig)
    paths.append(fp)

    # 3) tur bo'yicha recall
    if per_type:
        fig, ax = plt.subplots(figsize=(7, 4))
        keys = list(per_type)
        ax.bar(keys, [per_type[k] for k in keys], color="#2E9E5B")
        ax.set_ylim(0, 1.05); ax.set_ylabel("Recall"); ax.set_title("A1–A8 tur bo'yicha recall")
        ax.grid(alpha=0.3, axis="y")
        fp = os.path.join(outdir, "per_type_recall.png"); fig.tight_layout(); fig.savefig(fp, dpi=130); plt.close(fig)
        paths.append(fp)
    return paths
