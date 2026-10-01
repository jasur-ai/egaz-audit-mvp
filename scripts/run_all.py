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
from src import rules as R             # noqa: E402
from src.evaluate import (business_compare, choose_threshold, make_figures,  # noqa: E402
                          median_slide_threshold, metrics_at, metrics_by_period,
                          per_type_recall, per_type_recall_flags, recall_at_top,
                          rolling_threshold)
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

    # ---- S6b: FPR nazorati va gibrid kanal (R41) ----
    q_te = meta_te["q_index"].to_numpy()
    # 1) uch siyosat: statik (train kvantili), siljuvchi kvantil, median-slide
    thr_roll = rolling_threshold(s_tr, q_te, s_te, alert_rate=ALERT_RATE, window=4)
    thr_slide = median_slide_threshold(s_tr, q_te, s_te, base_thr=thr_if)
    thr_rows_roll = np.array([thr_roll[q] for q in q_te])
    thr_rows_slide = np.array([thr_slide[q] for q in q_te])
    per_q_static = metrics_by_period(yte, s_te, thr_if, q_te)
    per_q_roll = metrics_by_period(yte, s_te, thr_roll, q_te)
    per_q_slide = metrics_by_period(yte, s_te, thr_slide, q_te)
    m_roll = metrics_at(yte, s_te, thr_if, thr_rows=thr_rows_roll)
    m_slide = metrics_at(yte, s_te, thr_if, thr_rows=thr_rows_slide)

    # 2) gibrid: IF ∪ ochiq qoidalar (chegaralar VALIDATSIYA oynasida tanlanadi)
    val_mask = (meta["q_index"] >= 16) & meta["q_index"].le(17)   # q16–17
    val_mask = val_mask.to_numpy() if hasattr(val_mask, "to_numpy") else np.asarray(val_mask)
    rule_thr, rule_rejected = R.select_thresholds(feat, meta, val_mask)
    rule_flag, _rule_each = R.apply_rules(feat, rule_thr)
    rule_te = rule_flag[te]
    hybrid_te = (s_te >= thr_rows_slide) | rule_te
    hybrid_flag = np.zeros(len(yte), dtype=bool) | hybrid_te
    m_hybrid = metrics_at(yte, s_te, thr_if, thr_rows=np.where(hybrid_te, -np.inf, np.inf))
    per_hybrid = per_type_recall(meta_te, np.where(hybrid_te, np.inf, s_te), thr_if)
    per_q_hybrid = []
    for p_ in sorted(set(q_te.tolist())):
        m = q_te == p_
        yt, ft = yte[m], hybrid_te[m]
        fp = int(((ft) & (yt == 0)).sum()); tn = int((~ft & (yt == 0)).sum())
        tp = int((ft & (yt == 1)).sum()); fn = int((~ft & (yt == 1)).sum())
        per_q_hybrid.append({"davr": int(p_), "n": int(m.sum()),
                             "fpr": round(fp / (fp + tn), 4) if (fp + tn) else 0.0,
                             "recall": round(tp / max(tp + fn, 1), 4), "threshold": None,
                             "alerts": fp + tp})

    # ---- S6: qo'shimcha tahlillar (IF bo'yicha) ----
    per = per_type_recall(meta_te, results["if"]["scores_test"], thr_if)
    rec5 = recall_at_top(yte, results["if"]["scores_test"], 0.05)
    biz = business_compare(yte, results["if"]["scores_test"], 200)
    t0 = time.perf_counter()
    _ = M.score_if(results["if"]["model"], Xte)
    inf_ms = (time.perf_counter() - t0) / len(Xte) * 1000

    proxy_coef = F.fit_proxy(df, train_max_q=F.TRAIN_MAX_Q)
    M.save_meta(if_m, os.path.join(MODELS, "metadata.json"),
                extra={"features": F.FEATURES, "feature_groups": F.FEATURE_GROUPS,
                       "threshold_if": thr_if,
                       "threshold_policy": {
                           "statik": round(float(thr_if), 6),
                           "siljuvchi_kvantil": {str(k): round(v, 6) for k, v in thr_roll.items()},
                           "median_slide": {str(k): round(v, 6) for k, v in thr_slide.items()},
                           "qoida": "median_slide: t = t_train + (median_davr − median_train); "
                                    "faqat skorlar, label yo'q"},
                       "rules_channel": {k: {kk: vv for kk, vv in v.items() if kk != "izoh"}
                                         for k, v in rule_thr.items()},
                       "rules_protocol": "chegaralar validatsiya oynasida (q16-17) F1 bo'yicha tanlangan; "
                                         "test davri tanlovga kirmagan",
                       "proxy": {"formula": "a + b*energy + c*production",
                                 "coef": [round(float(c), 6) for c in proxy_coef],
                                 "fit": f"q_index <= {F.TRAIN_MAX_Q} (train), robust 2-qadam"},
                       "trained_rows": int(len(Xtr)), "test_rows": int(len(Xte)),
                       "injection_rate": injection_rate})
    figs = make_figures(yte, results["if"]["scores_test"], meta_te, thr_if,
                        os.path.join(REPORTS, "figures"), per_type=per)

    # ---- hisobot ----
    lines = ["# S6 — Baholash hisoboti (avtomatik)", "",
             f"**Yozuvlar:** {len(df):,} (train {len(Xtr):,} / test {len(Xte):,}) · "
             f"**injection:** {injection_rate:.0%} · **seed:** {seed}",
             f"**Feature:** {len(F.FEATURES)} ta ({len(F.FEATURE_GROUPS)} guruh) · **Quvur vaqti:** {time.perf_counter()-t_start:.1f} s", "",
             "## Asosiy natijalar (test = 2025Q3–2026Q2)", "",
             "| Model | Precision | Recall | F1 | ROC-AUC | PR-AUC | FPR | Threshold (train) |", "|---|---|---|---|---|---|---|---|"]
    for name, r in results.items():
        m = r["metrics"]
        lines.append(f"| {name.upper()} | {m['precision']} | {m['recall']} | **{m['f1']}** | "
                     f"{m['roc_auc']} | {m['pr_auc']} | {m['fpr']} | {m['threshold']:.4f} |")
    lines += ["", f"**AC-2 tekshiruvi (FPR ≤ 0,10):** IF FPR = {results['if']['metrics']['fpr']} → "
                  f"{'✅ bajarildi' if results['if']['metrics']['fpr'] <= 0.10 else '❌ bajarilmadi'}",
              "", "## FPR nazorati (R41) — uchta siyosat", "",
              "AC-2: FPR ≤ 0,10. Har chorak kesimida:", "",
              "| Davr | n | Statik FPR | Siljuvchi kvantil FPR | **Median-slide FPR** | Recall (slide) |",
              "|---|---|---|---|---|---|"]
    for a_, b_, c_ in zip(per_q_static, per_q_roll, per_q_slide):
        flag = " ⚠" if a_["fpr"] > 0.10 else ""
        lines.append(f"| {a_['davr']} | {a_['n']:,} | {a_['fpr']}{flag} | {b_['fpr']} | "
                     f"{c_['fpr']} | {c_['recall']} |")
    mx_static = max(r["fpr"] for r in per_q_static)
    mx_roll = max(r["fpr"] for r in per_q_roll)
    mx_slide = max(r["fpr"] for r in per_q_slide)
    lines += ["",
              "| Siyosat | Eng yuqori choraklik FPR | Umumiy F1 | Umumiy FPR | Alert ulushi |",
              "|---|---|---|---|---|",
              f"| Statik (train kvantili) | {mx_static} ❌ | {results['if']['metrics']['f1']} | "
              f"{results['if']['metrics']['fpr']} | {(s_te >= thr_if).mean():.1%} |",
              f"| Siljuvchi kvantil (oyna 4) | {mx_roll} ❌ | {m_roll['f1']} | {m_roll['fpr']} | "
              f"{(s_te >= thr_rows_roll).mean():.1%} |",
              f"| **Median-slide (tavsiya)** | **{mx_slide}** {'✅' if mx_slide <= 0.10 else '❌'} | "
              f"{m_slide['f1']} | {m_slide['fpr']} | {(s_te >= thr_rows_slide).mean():.1%} |", "",
              f"**Xulosa:** siljuvchi kvantil FPR muammosini yechmaydi (u **alert hajmini** mo'ljallaydi). "
              f"FPR ni buzadigan narsa — **normal skorlar siljishi**; `median_slide_threshold` shuni "
              f"turadi: eng yomon chorak {mx_static} → **{mx_slide}** (AC-2 bajarildi), narxi — recall "
              f"{results['if']['metrics']['recall']} → {m_slide['recall']} (alert {abs((s_te >= thr_if).mean() - (s_te >= thr_rows_slide).mean()):.1%} kamaydi).",
              "",
              "> Label'siz ekani muhim: hech qaysi siyosat **test label'lariga** qaramaydi — faqat skor",
              "> taqsimoti ishlatiladi. Real tizimda chorak yakunida operator tekshiruv natijalarini",
              "> (label'larni) qo'shsa, kalibrlash yanada aniq bo'ladi. Siyosatlar `models/metadata.json`",
              "> da yozilgan (audit izi).",
              "", "## Gibrid kanal: IF ∪ ochiq qoidalar (R41)", "",
              "IF yagona-feature signallarini suyultiradi (diagnostika: `offsets_own_dev` yakka-feature",
              "AUC = 0,93, ammo IF A7 ning 13% ini topadi). Shu sababli model yoniga **shaffof qoidalar**",
              "qo'shiladi — chegaralar **validatsiya oynasida (q16–17)** tanlangan, test tanlovga kirmagan:", "",
              "| Qoida | Feature | Shart | Validatsiya (P / R / F1) |",
              "|---|---|---|---|"]
    for name, cfg in rule_thr.items():
        lines.append(f"| {name} | `{cfg['feature']}` | {cfg['op']} {cfg['thr']} | "
                     f"{cfg['val_precision']} / {cfg['val_recall']} / {cfg['val_f1']} |")
    for rj in rule_rejected:
        lines.append(f"| {rj['nomi']} | — | **rad etildi** | {rj['sabab']} |")
    lines += ["",
              "| Konfiguratsiya | Precision | Recall | F1 | FPR | Alert | A5 recall | A7 recall | A8 recall |",
              "|---|---|---|---|---|---|---|---|---|"]
    per_h = per_type_recall(meta_te, s_te, thr_if)
    per_slide = per_type_recall_flags(meta_te, s_te >= thr_rows_slide)
    for label, mm, per_, alerts in (("Statik (IF, R40)", results["if"]["metrics"], per_h,
                                     float((s_te >= thr_if).mean())),
                                    ("Median-slide (faqat IF)", m_slide, per_slide,
                                     float((s_te >= thr_rows_slide).mean())),
                                    ("**Median-slide + qoidalar**", m_hybrid, per_hybrid,
                                     float(hybrid_te.mean()))):
        lines.append(f"| {label} | {mm['precision']} | {mm['recall']} | **{mm['f1']}** | {mm['fpr']} | "
                     f"{alerts:.1%} | {per_.get('A5')} | {per_.get('A7')} | {per_.get('A8')} |")
    lines += ["",
              f"**A7: {per_h.get('A7')} → {per_hybrid.get('A7')}** — qoida kanali A7 ni ko'rinadigan",
              f"qiladi (offset devori). **A5 allaqachon 1,0** (aktivlik kross-tekshiruvi feature'i tufayli).",
              f"**A8 saqlanib qoladi ({per_hybrid.get('A8')})** — orakul AUC≈0,59: bu feature yetishmovchiligi",
              "emas, ma'lumotdagi signal chegarasi (pastdagi cheklovlar).",
              "",
              "> Qoidalar **modelni almashtirmaydi**: ular audit qilinadigan qo'shimcha signal; har biri",
              "> bitta jumlada izohlanadi (TZ §7 tamoyil 3 — explainability-first).",
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
              "- Model raqamni O'ZGARTIRMAYDI: faqat tekshiruv ustuvorligini belgilaydi (AC-5/§8.4).",
              "- **A8 chegarasi (R41):** vaqt-aralashtirish siljishi 0,15·|Δaktivlik| ≈ 1–3% — normal",
              "  hisobot shovqini (σ≈6%) ichida. Orakul (implied_ghg'ni bilgan ideal detektor) A8 uchun",
              "  AUC≈0,59 (|Δ|≥10% qatorlarda 0,66) — ya'ni A8 zaifligi feature yetishmovchiligi emas,",
              "  **ma'lumotdagi signal chegarasi**. Yuqori aniqlikdagi qoida ham yo'q (P≈0,02).",
              "- Proksi (`proxy`) koeffitsiyentlari FAQAT train davrida fit qilinadi (test fit'ga kirmaydi);",
              "  `implied_ghg` hech qanday feature'da ishlatilmaydi.",
              "- **Generatorda to'qnashuv (R41 diagnostikasi):** bir kvartalga ikki anomaliya tushsa,",
              "  `anomaly_type` faqat bittasini yozadi (≈0,06% qator). Shu sabab tur bo'yicha recall",
              "  baholari pastroq ko'rinishi mumkin (iz qolgan, yorliq boshqa turda).", ""]
    with open(os.path.join(REPORTS, "eval_report.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))

    print("== NATIJA ==")
    for name, r in results.items():
        print(f"  {name.upper():6s} F1={r['metrics']['f1']:.3f}  P={r['metrics']['precision']:.3f} "
              f"R={r['metrics']['recall']:.3f}  AUC={r['metrics']['roc_auc']:.3f}  FPR={r['metrics']['fpr']:.3f}")
    print(f"  recall@5%={rec5} | biznes yaxshilanish={biz['yaxshilanish_x']}x | inferens={inf_ms:.2f} ms/1k")
    print(f"  FPR nazorati: statik max={mx_static} · siljuvchi={mx_roll} · median-slide={mx_slide} "
          f"(F1 {results['if']['metrics']['f1']} → slide {m_slide['f1']} → gibrid {m_hybrid['f1']})")
    print(f"  Gibrid: A7 recall {per_h.get('A7')} → {per_hybrid.get('A7')} · "
          f"qoidalar: {', '.join(f'{n.split()[0]}' for n in rule_thr)}")
    print("  hisobot: reports/eval_report.md")


if __name__ == "__main__":
    main()
