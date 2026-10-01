# -*- coding: utf-8 -*-
"""S8 (real qism) — Model monitoring: dreyf va FPR trendi.

TZ §7.4 talabi: model ishga tushgandan keyin ham nazorat qilinadi:
  • Feature dreyfi — PSI (Population Stability Index) va KS testi
  • Skor dreyfi — train/test taqsimot farqi
  • FPR trendi — davrlar kesimida (muzlatilgan threshold bilan)
  • Qaror qoidalari: qachon qayta o'qitish kerak

Chiqish: reports/monitor_report.md + reports/figures/drift_psi.png + fpr_trend.png

Metodika (adabiyotda standart):
  PSI = Σ (P_test − P_train) · ln(P_test / P_train)  — 10 equal-frequency binned
  PSI < 0,10 stabil · 0,10–0,25 kuzatuv · > 0,25 dreyf (qayta o'qitish signali)
  KS  — ikki taqsimot tengligi (p < 0,05 → sezilarli farq)
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

from src import features as F          # noqa: E402

PSI_STABLE = 0.10
PSI_WATCH = 0.25
KS_ALPHA = 0.05

# Vaqt indeksi konstruksiya bo'yicha o'zgaradi (train ≤17 → test ≥18): PSI ma'nosiz.
# Shuning uchun monitoringdan chiqariladi, hisobotda alohida ko'rsatiladi.
TIME_FEATURES = {"quarter_index"}


def psi(expected: np.ndarray, actual: np.ndarray, bins: int = 10, eps: float = 1e-6) -> float:
    """Population Stability Index (equal-frequency chegaralar train'dan)."""
    expected = np.asarray(expected, dtype=float)
    actual = np.asarray(actual, dtype=float)
    if len(expected) == 0 or len(actual) == 0:
        return 0.0
    qs = np.unique(np.quantile(expected, np.linspace(0, 1, bins + 1)))
    if len(qs) < 3:                       # deyarli o'zgarmas feature
        return 0.0
    qs[0], qs[-1] = -np.inf, np.inf
    e = np.histogram(expected, bins=qs)[0] / len(expected)
    a = np.histogram(actual, bins=qs)[0] / len(actual)
    e = np.clip(e, eps, None)
    a = np.clip(a, eps, None)
    return float(np.sum((a - e) * np.log(a / e)))


def drift_table(X_train: np.ndarray, X_test: np.ndarray, feature_names: list[str]) -> list[dict]:
    """Har bir feature uchun PSI + KS. Vaqt feature'lari «vaqt» statusi bilan ajratiladi."""
    rows = []
    for j, name in enumerate(feature_names):
        tr, te = X_train[:, j], X_test[:, j]
        p = psi(tr, te)
        ks = stats.ks_2samp(tr, te)
        if name in TIME_FEATURES:
            status = "vaqt"
        else:
            status = "dreyf" if p > PSI_WATCH else ("kuzatuv" if p > PSI_STABLE else "stabil")
        rows.append({"feature": name, "psi": round(p, 4), "ks_stat": round(float(ks.statistic), 4),
                     "ks_p": float(ks.pvalue), "status": status,
                     "mean_train": round(float(np.mean(tr)), 5), "mean_test": round(float(np.mean(te)), 5)})
    rows.sort(key=lambda r: -r["psi"])
    return rows


def score_drift(scores_train: np.ndarray, scores_test: np.ndarray) -> dict:
    ks = stats.ks_2samp(scores_train, scores_test)
    return {"ks_stat": round(float(ks.statistic), 4), "ks_p": float(ks.pvalue),
            "mean_train": round(float(np.mean(scores_train)), 5),
            "mean_test": round(float(np.mean(scores_test)), 5),
            "drift": bool(ks.pvalue < KS_ALPHA)}


def fpr_trend(y: np.ndarray, scores: np.ndarray, meta: pd.DataFrame, thr: float) -> list[dict]:
    """Davrlar kesimida FPR va precision (threshold MUZLATILGAN — qayta tanlanmaydi)."""
    out = []
    for q in sorted(meta["q_index"].unique()):
        mask = (meta["q_index"] == q).to_numpy()
        yy, ss = y[mask], scores[mask]
        neg = int((yy == 0).sum())
        pos = int((yy == 1).sum())
        alerts = ss >= thr
        fp = int((alerts & (yy == 0)).sum())
        tp = int((alerts & (yy == 1)).sum())
        out.append({"quarter": str(meta.loc[mask, "quarter"].iloc[0]), "q_index": int(q),
                    "n": int(mask.sum()), "negatives": neg, "positives": pos,
                    "fpr": round(fp / neg, 4) if neg else None,
                    "recall": round(tp / pos, 4) if pos else None,
                    "alerts": int(alerts.sum())})
    return out


def verdict(drift_rows: list[dict], sd: dict, trend: list[dict], fpr_limit: float = 0.10) -> dict:
    """Qaror qoidalari — qayta o'qitish kerakmi?"""
    drifted = [r["feature"] for r in drift_rows if r["status"] == "dreyf"]
    watch = [r["feature"] for r in drift_rows if r["status"] == "kuzatuv"]
    over = [t["quarter"] for t in trend if t["fpr"] is not None and t["fpr"] > fpr_limit]
    if drifted:
        action = "QAYTA O'QITISH tavsiya etiladi"
        reason = [f"{len(drifted)} feature dreyfda (PSI>{PSI_WATCH}): {', '.join(drifted[:4])}"]
        if over:
            reason.append(f"FPR chegaradan oshgan davrlar: {', '.join(over)}")
    elif over:
        action = "MEDIAN-SLIDE QAYTA KALIBRLASH (R41 siyosati qo'llaniladi)"
        reason = [f"FPR chegaradan (0,10) oshgan davrlar: {', '.join(over)}",
                  "Model qayta o'qitilmaydi — threshold normal skorlar siljishiga moslashadi",
                  "Siyosat: t = t_train + (median_davr − median_train); faqat skorlar, label yo'q",
                  "Samara (eval_report.md §FPR nazorati): eng yomon chorak FPR 0,1075 → 0,0903 ✅"]
    elif watch or sd["drift"]:
        action = "KUZATUVNI KUCHAYTIRISH"
        reason = [f"{len(watch)} feature kuzatuvda (PSI {PSI_STABLE}–{PSI_WATCH})"] if watch else []
        if sd["drift"]:
            reason.append("skor taqsimoti sezilarli farq qiladi (KS p<0,05)")
    else:
        action = "STABIL — joriy model bilan davom"
        reason = ["barcha PSI < 0,10, skor dreyfi yo'q, FPR chegarada"]
    return {"action": action, "reason": reason, "drifted": drifted, "watch": watch,
            "fpr_quarters_over": over}


def make_monitor_figures(drift_rows: list[dict], trend: list[dict], outdir: str) -> list[str]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    os.makedirs(outdir, exist_ok=True)
    paths = []

    # 1) PSI bar chart (top-15)
    top = drift_rows[:15][::-1]
    fig, ax = plt.subplots(figsize=(8.2, 5.2), dpi=140)
    colors = ["#C0392B" if r["status"] == "dreyf" else "#F5A623" if r["status"] == "kuzatuv"
              else "#8FA3B5" if r["status"] == "vaqt" else "#2E9E5B" for r in top]
    ax.barh([r["feature"] for r in top], [r["psi"] for r in top], color=colors, height=0.72)
    ax.axvline(PSI_STABLE, color="#5B6B7A", ls="--", lw=1, label=f"stabil < {PSI_STABLE}")
    ax.axvline(PSI_WATCH, color="#C0392B", ls="--", lw=1, label=f"dreyf > {PSI_WATCH}")
    ax.set_xlabel("PSI (train → test)")
    ax.set_title("Feature dreyfi (PSI)", fontsize=12, fontweight="bold")
    ax.legend(fontsize=9, loc="lower right")
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    p1 = os.path.join(outdir, "drift_psi.png")
    fig.savefig(p1); plt.close(fig); paths.append(p1)

    # 2) FPR trend + recall
    qs = [t["quarter"] for t in trend]
    fig, ax = plt.subplots(figsize=(8.2, 4.4), dpi=140)
    ax.plot(qs, [t["fpr"] for t in trend], "o-", color="#C0392B", lw=2, label="FPR")
    ax.plot(qs, [t["recall"] if t["recall"] is not None else np.nan for t in trend], "s--",
            color="#2C7FB8", lw=2, label="Recall")
    ax.axhline(0.10, color="#5B6B7A", ls=":", lw=1.2, label="FPR chegarasi (AC-2: 0,10)")
    ax.set_ylim(0, 1)
    ax.set_title("FPR va Recall trendi (threshold muzlatilgan)", fontsize=12, fontweight="bold")
    ax.set_xlabel("Davr"); ax.grid(alpha=0.25); ax.legend(fontsize=9)
    fig.tight_layout()
    p2 = os.path.join(outdir, "fpr_trend.png")
    fig.savefig(p2); plt.close(fig); paths.append(p2)
    return paths


def build_report(drift_rows, sd, trend, verdict_d, out_md: str, figures: list[str]) -> str:
    lines = ["# Model monitoring hisoboti — dreyf va FPR trendi", "",
             "> Avtomatik: `python3 scripts/run_monitor.py` · S8 (TZ §7.4) · metodika: PSI + KS + muzlatilgan threshold",
             "",
             f"## 1. Qaror: **{verdict_d['action']}**", ""]
    for r in verdict_d["reason"]:
        lines.append(f"- {r}")
    lines += ["", "## 2. Feature dreyfi (PSI, train → test)", "",
              "| # | Feature | PSI | KS stat | KS p | Holat | x̄ train | x̄ test |",
              "|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(drift_rows, 1):
        mark = {"dreyf": "🔴 dreyf", "kuzatuv": "🟡 kuzatuv", "stabil": "🟢 stabil",
                "vaqt": "⚪ vaqt (monitoringdan tashqari)"}[r["status"]]
        lines.append(f"| {i} | `{r['feature']}` | {r['psi']} | {r['ks_stat']} | {r['ks_p']:.2e} | {mark} "
                     f"| {r['mean_train']} | {r['mean_test']} |")
    n_st = sum(1 for r in drift_rows if r["status"] == "stabil")
    n_wa = sum(1 for r in drift_rows if r["status"] == "kuzatuv")
    n_dr = sum(1 for r in drift_rows if r["status"] == "dreyf")
    n_tm = sum(1 for r in drift_rows if r["status"] == "vaqt")
    lines += ["", f"**Yakun:** 🟢 {n_st} · 🟡 {n_wa} · 🔴 {n_dr} · ⚪ {n_tm} vaqt "
              f"(jami {len(drift_rows)} feature)", "",
              "> ⚪ Vaqt indeksi konstruksiya bo'yicha o'zgaradi (train davri ≠ test davri) — "
              "PSI unga ma'nosiz, shuning uchun qaror qabul qilishda hisobga olinmaydi.", "",
              "## 3. Skor dreyfi", "",
              f"- KS stat = {sd['ks_stat']} · p = {sd['ks_p']:.3e} → "
              f"{'sezilarli farq' if sd['drift'] else 'sezilarli farq yo`q'}",
              f"- o'rtacha skor: train {sd['mean_train']} → test {sd['mean_test']}", "",
              "## 4. FPR va Recall trendi (threshold muzlatilgan)", "",
              "| Davr | Yozuv | Anomaliya | FPR | Recall | Alertlar |", "|---|---|---|---|---|---|"]
    for t in trend:
        fpr_s = f"{t['fpr']:.4f}" if t["fpr"] is not None else "—"
        rec_s = f"{t['recall']:.4f}" if t["recall"] is not None else "—"
        flag = " ⚠️" if (t["fpr"] is not None and t["fpr"] > 0.10) else ""
        lines.append(f"| {t['quarter']} | {t['n']} | {t['positives']} | {fpr_s}{flag} | {rec_s} | {t['alerts']} |")
    lines += ["", "## 5. Qaror qoidalari (modelni qachon qayta o'qitish)", "",
              f"| Belgi | Chegara | Amal |", "|---|---|---|",
              f"| PSI > {PSI_WATCH} (bitta feature) | dreyf | feature sababini tekshirish, qayta o'qitish |",
              f"| PSI {PSI_STABLE}–{PSI_WATCH} | kuzatuv | monitoringni kuchaytirish |",
              f"| Skor KS p < {KS_ALPHA} | taqsimot farqi | kalibratsiya/taqsimot tekshiruvi |",
              f"| FPR > 0,10 (davr) | AC-2 buzilishi | median-slide kalibrlash (eval_report.md §FPR nazorati) |", "",
              "## 6. Figuralar", ""]
    for f in figures:
        lines.append(f"- `{os.path.relpath(f, os.path.dirname(os.path.dirname(out_md)))}`")
    lines += ["", "---", "",
              "**Izoh:** threshold hech qachon test davridan tanlanmaydi — dreyf aniqlash uchun ham "
              "train taqsimoti asos qilib olinadi (p-hacking istisnosi)."]
    with open(out_md, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return out_md


def run(data_path: str, model_dir: str, outdir: str, figures_dir: str) -> dict:
    import joblib
    df = pd.read_csv(data_path)
    X, meta = F.feature_matrix(df)
    y = meta["label"].to_numpy()
    tr = (meta["q_index"] <= 17).to_numpy()
    te = ~tr

    model = joblib.load(os.path.join(model_dir, "if_v1.joblib"))
    from src.models import score_if
    s_tr = score_if(model, X[tr])
    s_te = score_if(model, X[te])

    meta_te = meta[te].reset_index(drop=True)
    dt = drift_table(X[tr], X[te], F.FEATURES)
    sd = score_drift(s_tr, s_te)
    thr = json.load(open(os.path.join(model_dir, "metadata.json"), encoding="utf-8"))["threshold_if"]
    trend = fpr_trend(y[te], s_te, meta_te, thr)
    v = verdict(dt, sd, trend)
    figs = make_monitor_figures(dt, trend, figures_dir)
    md = build_report(dt, sd, trend, v, os.path.join(outdir, "monitor_report.md"), figs)
    return {"verdict": v, "n_drift": len(v["drifted"]), "n_watch": len(v["watch"]),
            "report": md, "figures": figs, "score_drift": sd,
            "trend": trend, "drift": dt, "threshold": thr}


if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    res = run(os.path.join(base, "data", "features_v1.csv.gz"), os.path.join(base, "models"),
              os.path.join(base, "reports"), os.path.join(base, "reports", "figures"))
    print(f"Qaror: {res['verdict']['action']}")
    for r in res["verdict"]["reason"]:
        print(f"  · {r}")
    print(f"  dreyf: {res['n_drift']} · kuzatuv: {res['n_watch']} · hisobot: {res['report']}")
