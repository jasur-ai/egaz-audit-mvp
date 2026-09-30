# -*- coding: utf-8 -*-
"""S1→S6 to'liq quvur: generator → feature → uch model → baholash → hisobot."""
from __future__ import annotations

import gzip
import json
import os
import sys
import time

import joblib
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import features as F          # noqa: E402
from src import models as M            # noqa: E402
from src.evaluate import (business_compare, choose_threshold, make_figures,  # noqa: E402
                          metrics_at, per_type_recall, recall_at_top)
from src.generator import generate     # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA, MODELS, REPORTS = (os.path.join(BASE, p) for p in ("data", "models", "reports"))


def main(n_companies: int = 2300, injection_rate: float = 0.15, seed: int = 42):
    for p in (DATA, MODELS, REPORTS, os.path.join(REPORTS, "figures")):
        os.makedirs(p, exist_ok=True)
    t_start = time.perf_counter()

    # ---- S1 ----
    if os.path.exists(os.path.join(DATA, "features_v1.csv.gz")):
        df = pd.read_csv(os.path.join(DATA, "features_v1.csv.gz"))
    else:
        df = generate(n_companies=n_companies, injection_rate=injection_rate, seed=seed)
        with gzip.open(os.path.join(DATA, "uz_proxy_v1.csv.gz"), "wt", encoding="utf-8") as fh:
            df.to_csv(fh, index=False)
    # ---- S3 ----
    feat = F.build_features(df)
    with gzip.open(os.path.join(DATA, "features_v1.csv.gz"), "wt", encoding="utf-8") as fh:
        feat.to_csv(fh, index=False)
    X, meta = F.feature_matrix(feat)
    y = meta["label"].to_numpy()

    tr = (meta["q_index"] <= 17).to_numpy()          # 2021Q1–2025Q2
    te = ~tr                                          # 2025Q3–2026Q2
    Xtr, Xte, yte = X[tr], X[te], y[te]
    meta_te = meta[te].reset_index(drop=True)

    # ---- S4/S5 ----
    results = {}
    ALERT_RATE = 0.12     # S0'da muzlatilgan ish nuqtasi (AC-2: FPR ≤ 0,10 talabidan)
    if_m = M.train_if(Xtr, contamination=ALERT_RATE)
    s_tr, s_te = M.score_if(if_m, Xtr), M.score_if(if_m, Xte)
    thr_if = choose_threshold(s_tr, ALERT_RATE)
    sweep = []
    for a in (0.06, 0.08, 0.10, 0.12, 0.15):
        th = choose_threshold(s_tr, a)
        rr = metrics_at(yte, s_te, th)
        sweep.append((a, rr["f1"], rr["precision"], rr["recall"], rr["fpr"]))
    results["if"] = {"model": if_m, "scores_test": s_te, "thr": thr_if,
                     "metrics": metrics_at(yte, s_te, thr_if)}
    joblib.dump(if_m, os.path.join(MODELS, "if_v1.joblib"), compress=3)

    ae_m = M.train_ae(Xtr)
    s_tr_ae, s_te_ae = M.score_ae(ae_m, Xtr), M.score_ae(ae_m, Xte)
    thr_ae = choose_threshold(s_tr_ae, ALERT_RATE)
    results["ae"] = {"model": ae_m, "scores_test": s_te_ae, "thr": thr_ae,
                     "metrics": metrics_at(yte, s_te_ae, thr_ae)}
    joblib.dump(ae_m, os.path.join(MODELS, "ae.joblib"), compress=3)

    oc_m = M.train_ocsvm(Xtr)
    s_tr_oc, s_te_oc = M.score_ocsvm(oc_m, Xtr), M.score_ocsvm(oc_m, Xte)
    thr_oc = choose_threshold(s_tr_oc, ALERT_RATE)
    results["ocsvm"] = {"model": oc_m, "scores_test": s_te_oc, "thr": thr_oc,
                        "metrics": metrics_at(yte, s_te_oc, thr_oc)}
    joblib.dump(oc_m, os.path.join(MODELS, "ocsvm.joblib"), compress=3)

    # ---- S6: qo'shimcha tahlillar (IF bo'yicha) ----
    per = per_type_recall(meta_te, results["if"]["scores_test"], thr_if)
    rec5 = recall_at_top(yte, results["if"]["scores_test"], 0.05)
    biz = business_compare(yte, results["if"]["scores_test"], 200)
    t0 = time.perf_counter()
    _ = M.score_if(results["if"]["model"], Xte)
    inf_ms = (time.perf_counter() - t0) / len(Xte) * 1000

    M.save_meta(if_m, os.path.join(MODELS, "metadata.json"),
                extra={"features": F.FEATURES, "threshold_if": thr_if,
                       "trained_rows": int(len(Xtr)), "test_rows": int(len(Xte)),
                       "injection_rate": injection_rate})
    figs = make_figures(yte, results["if"]["scores_test"], meta_te, thr_if,
                        os.path.join(REPORTS, "figures"), per_type=per)

    # ---- hisobot ----
    lines = ["# S6 — Baholash hisoboti (avtomatik)", "",
             f"**Yozuvlar:** {len(df):,} (train {len(Xtr):,} / test {len(Xte):,}) · "
             f"**injection:** {injection_rate:.0%} · **seed:** {seed}",
             f"**Feature:** {len(F.FEATURES)} ta (6 guruh) · **Quvur vaqti:** {time.perf_counter()-t_start:.1f} s", "",
             "## Asosiy natijalar (test = 2025Q3–2026Q2)", "",
             "| Model | Precision | Recall | F1 | ROC-AUC | PR-AUC | FPR | Threshold (train) |", "|---|---|---|---|---|---|---|---|"]
    for name, r in results.items():
        m = r["metrics"]
        lines.append(f"| {name.upper()} | {m['precision']} | {m['recall']} | **{m['f1']}** | "
                     f"{m['roc_auc']} | {m['pr_auc']} | {m['fpr']} | {m['threshold']:.4f} |")
    lines += ["", f"**AC-2 tekshiruvi (FPR ≤ 0,10):** IF FPR = {results['if']['metrics']['fpr']} → "
                  f"{'✅ bajarildi' if results['if']['metrics']['fpr'] <= 0.10 else '❌ bajarilmadi'}",
              "", "## IF ish nuqtasi (alert-rate sweep — threshold train kvantilidan)", "",
              "| Alert-rate | F1 | Precision | Recall | FPR |", "|---|---|---|---|---|"]
    for a, f1, pr, rc, fp in sweep:
        mark = " ← **tanlangan (S0)**" if abs(a - ALERT_RATE) < 1e-9 else ""
        lines.append(f"| {a:.2f}{mark} | {f1} | {pr} | {rc} | {fp} |")
    lines += ["", "## IF bo'yicha qo'shimcha", "",
              f"- **Recall@top-5%** (faqat eng shubhali 5%ni tekshirish): **{rec5}**",
              f"- **Biznes taqqoslash:** bazadagi anomaliya ulushi {biz['baza_ulushi']}, "
              f"model top-200 aniqligi {biz['model_top_n_aniqlik']} → **{biz['yaxshilanish_x']}× yaxshilanish**",
              f"- **Inferens:** {inf_ms:.2f} ms / 1 000 yozuv",
              f"- **Tur bo'yicha recall (A1–A8):** {json.dumps(per, ensure_ascii=False)}", "",
              "## Figuralar", ""]
    for f in figs:
        lines.append(f"- `{os.path.relpath(f, BASE)}`")
    lines += ["", "## Cheklovlar (TZ §10 bilan mos)", "",
              "- Sintetik A1–A8 real soxtalashtirishdan soddaroq bo'lishi mumkin (model yuqorisini baholaydi).",
              "- OCSVM train uchun qism-to'plamda o'qitildi (TZ §8.3: nazorat guruhi roli).",
              "- Threshold train kvantilidan olinadi (test'ga qaramaydi) — p-hacking yo'q.",
              "- Model raqamni O'ZGARTIRMAYDI: faqat tekshiruv ustuvorligini belgilaydi (AC-5/§8.4).", ""]
    with open(os.path.join(REPORTS, "eval_report.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))

    print("== NATIJA ==")
    for name, r in results.items():
        print(f"  {name.upper():6s} F1={r['metrics']['f1']:.3f}  P={r['metrics']['precision']:.3f} "
              f"R={r['metrics']['recall']:.3f}  AUC={r['metrics']['roc_auc']:.3f}  FPR={r['metrics']['fpr']:.3f}")
    print(f"  recall@5%={rec5} | biznes yaxshilanish={biz['yaxshilanish_x']}x | inferens={inf_ms:.2f} ms/1k")
    print("  hisobot: reports/eval_report.md")


if __name__ == "__main__":
    main()
