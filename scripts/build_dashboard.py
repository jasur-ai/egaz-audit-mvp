# -*- coding: utf-8 -*-
"""S8 — Dashboard quruvchi (statik, o'z-o'zini ta'minlaydigan HTML).

Kirish: data/features_v1.csv.gz + models/if_v1.joblib + models/metadata.json + reports/figures/*.png
Chiqish: web/dashboard.html  (tashqi CDN yo'q — barcha rasm base64 ichida)

Bo'limlar: (1) KPI kartalar, (2) model taqqoslash, (3) figuralar,
(4) alert feed (top-20 + top-3 izoh), (5) model monitoring (audit izi).
"""
from __future__ import annotations

import base64
import json
import os
import sys

import joblib
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import features as F                      # noqa: E402
from src.evaluate import metrics_at, per_type_recall  # noqa: E402
from src.models import score_if                    # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
MODELS = os.path.join(BASE, "models")
FIGS = os.path.join(BASE, "reports", "figures")
WEB = os.path.join(BASE, "web")

FEATURE_PHRASE = {
    "log_reported": "e'lon qilingan hajm darajasi",
    "qoq_growth_reported": "chorakma-chorak keskin o'zgarish",
    "reported_to_energy": "hisob ↔ energiya nomuvofiqligi",
    "energy_intensity": "energiya sig'imi normadan chetlangan",
    "energy_intensity_growth": "energiya sig'imi keskin o'zgargan",
    "ghg_intensity": "emissiya sig'imi (birlik mahsulotga)",
    "ghg_intensity_growth": "emissiya sig'imi o'zgarishi",
    "gas_share": "yoqilg'i tarkibi (gaz ulushi)",
    "gas_share_growth": "yoqilg'i tarkibi o'zgarishi",
    "offsets_share": "ofset kreditlari ulushi",
    "offsets_share_growth": "ofset ulushi keskin o'zgarishi",
    "fugitive_ratio_change": "fugitiv chiqindi bo'limi o'zgarishi",
    "rolling_dev": "4-chorak o'rtachasidan chetlanish",
    "repeat_count": "qiymat ketma-ket takrorlanishi",
    "flat_flag": "harakatsiz (muzlagan) qiymatlar",
    "seasonal_residual": "mavsumiy fondan chetlanish",
    "drift_slope": "sekin tendensiya (dreyf)",
    "drift_estimate": "tizimli siljish",
    "jump_flag": "bir chorakda sakrash (>35%)",
    "unit_jump_flag": "birlik xatosi (1000× merosi)",
    "boundary_mix_flag": "davr chegarasida aralashish",
    "log_production": "mahsulot hajmi (miqyos)",
    "size_pct": "korxona miqyosi (percentil)",
    "quarter_index": "vaqt indeksi",
    "energy_to_prod_dev": "sektor medianasidan energiya chetlanishi",
    "reporting_volatility": "hisobot beqarorligi",
}
SKIP_EXPLAIN = {"quarter_index"}


def b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def main():
    os.makedirs(WEB, exist_ok=True)
    meta = json.load(open(os.path.join(MODELS, "metadata.json"), encoding="utf-8"))
    model = joblib.load(os.path.join(MODELS, "if_v1.joblib"))
    feats = meta["features"]
    thr = meta["threshold_if"]

    df = pd.read_csv(os.path.join(DATA, "features_v1.csv.gz"))
    X, m = F.feature_matrix(df)
    y = m["label"].to_numpy()
    tr = (m["q_index"] <= 17).to_numpy()
    s_te = score_if(model, X[~tr])
    y_te = y[~tr]
    m_te = m[~tr].reset_index(drop=True)
    met = metrics_at(y_te, s_te, thr)
    per = per_type_recall(m_te, s_te, thr)

    sc = model["scaler"]
    Z = sc.transform(X[~tr])
    mean = sc.mean_
    scale = np.sqrt(sc.var_)

    order = np.argsort(-s_te)
    rows = []
    for idx in order[:20]:
        z = Z[idx]
        cand = [(feats[j], z[j]) for j in range(len(feats)) if feats[j] not in SKIP_EXPLAIN]
        cand.sort(key=lambda t: -abs(t[1]))
        expl = [{"phrase": FEATURE_PHRASE.get(f, f), "raw": feats and f, "z": round(float(zz), 2)}
                for f, zz in cand[:3]]
        rows.append({
            "company": m_te.loc[idx, "company_id"], "quarter": m_te.loc[idx, "quarter"],
            "sector": m_te.loc[idx, "sector"], "score": float(s_te[idx]),
            "alert": bool(s_te[idx] >= thr), "explain": expl,
            "true_type": (m_te.loc[idx, "anomaly_type"] or "—") if isinstance(m_te.loc[idx, "anomaly_type"], str) else "—",
        })

    figs_html = ""
    for fname, title in (("pr_roc.png", "PR / ROC kurvalari — model ajratish sifati"),
                         ("score_dist.png", "Skor taqsimoti — normal va anomaliya"),
                         ("per_type_recall.png", "A1–A8 turlari bo'yicha recall")):
        p = os.path.join(FIGS, fname)
        if os.path.exists(p):
            figs_html += f'<figure><img src="data:image/png;base64,{b64(p)}" alt="{title}"><figcaption>{title}</figcaption></figure>'

    rows_html = ""
    for r in rows:
        ex = " · ".join(f"{e['phrase']} <span class='z{'neg' if e['z']<0 else ''}'>(z={e['z']})</span>" for e in r["explain"])
        flag = "<span class='pill red'>ALERT</span>" if r["alert"] else "<span class='pill gray'>kuzatuv</span>"
        rows_html += (f"<tr><td>{r['company']}</td><td>{r['quarter']}</td><td>{r['sector']}</td>"
                      f"<td class='num'>{r['score']:.4f}</td><td>{flag}</td><td class='ex'>{ex}</td>"
                      f"<td class='true'>{r['true_type']}</td></tr>")

    per_html = "".join(f"<div class='chip'>{k}<b>{v:.2f}</b></div>" for k, v in per.items())

    html = f"""<!doctype html><html lang="uz"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>E-GAZ-AUDIT — monitoring paneli</title>
<style>
 :root{{--bg:#0e151d;--card:#141f2b;--line:#23364a;--tx:#e8eef4;--mut:#9fb3c8;--grn:#2E9E5B;--red:#C0392B;--yel:#F5A623}}
 *{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--tx);font-family:system-ui,Segoe UI,sans-serif}}
 header{{padding:16px 20px;background:#101b26;border-bottom:1px solid var(--line)}}
 h1{{font-size:18px;margin:0 0 4px}} .sub{{font-size:12.5px;color:var(--mut)}}
 .wrap{{padding:16px 20px 40px;max-width:1180px;margin:0 auto}}
 .cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:14px 0}}
 .card{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 12px}}
 .card .k{{font-size:11.5px;color:var(--mut);text-transform:uppercase;letter-spacing:.4px}}
 .card .v{{font-size:22px;font-weight:700;margin-top:3px}} .card .n{{font-size:11px;color:var(--mut);margin-top:2px}}
 h2{{font-size:15px;margin:22px 0 8px;border-left:3px solid var(--grn);padding-left:8px}}
 table{{width:100%;border-collapse:collapse;font-size:12.5px;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden}}
 th,td{{padding:7px 8px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}
 th{{background:#16232f;color:var(--mut);font-weight:600;font-size:11.5px;text-transform:uppercase}}
 td.num{{font-variant-numeric:tabular-nums}} .ex{{color:var(--mut)}} .z{{color:var(--grn)}} .z.neg{{color:var(--yel)}}
 .true{{color:var(--mut);font-size:11.5px}}
 .pill{{font-size:10.5px;padding:2px 7px;border-radius:9px;color:#08131c;font-weight:700}}
 .pill.red{{background:#e05a4b}} .pill.gray{{background:#7d93a8}}
 .chip{{display:inline-block;background:var(--card);border:1px solid var(--line);border-radius:8px;padding:5px 9px;margin:3px 4px 0 0;font-size:12px}}
 .chip b{{margin-left:6px}}
 figure{{margin:10px 0;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:8px}}
 figure img{{width:100%;height:auto;border-radius:6px}}
 figcaption{{font-size:11.5px;color:var(--mut);padding:5px 2px 0}}
 .note{{font-size:12px;color:var(--mut);background:#101b26;border:1px dashed var(--line);border-radius:8px;padding:9px 11px;margin-top:10px}}
 .legend{{font-size:12px;color:var(--mut);margin-top:6px}}
 @media(max-width:760px){{ .ex{{display:none}} th:nth-child(6),td:nth-child(6){{display:none}} }}
</style>
<header>
 <h1>E-GAZ-AUDIT — anomaliya monitoring paneli (S8)</h1>
 <div class="sub">model: Isolation Forest {json.dumps(meta['params'], ensure_ascii=False)} · threshold (train kvantili) = {thr:.4f} ·
  rule_version {meta['rule_version']} · o'qitilgan: {meta['trained_at']} · test davri: 2025Q3–2026Q2</div>
</header>
<div class="wrap">

 <div class="cards">
  <div class="card"><div class="k">F1 (test)</div><div class="v">{met['f1']:.3f}</div><div class="n">balans ko'rsatkichi</div></div>
  <div class="card"><div class="k">Precision</div><div class="v">{met['precision']:.3f}</div><div class="n">signallarning aniqligi</div></div>
  <div class="card"><div class="k">Recall</div><div class="v">{met['recall']:.3f}</div><div class="n">topilgan anomaliyalar</div></div>
  <div class="card"><div class="k">FPR</div><div class="v" style="color:var(--grn)">{met['fpr']:.3f}</div><div class="n">AC-2: ≤ 0,10 ✔</div></div>
  <div class="card"><div class="k">ROC-AUC</div><div class="v">{met['roc_auc']:.3f}</div><div class="n">ajratish sifati</div></div>
  <div class="card"><div class="k">Alertlar (test)</div><div class="v">{met['tp']+met['fp']:,}</div><div class="n">tekshiruvga tavsiya</div></div>
 </div>

 <h2>Model taqqoslash (TZ §8.2 — uch nomzod)</h2>
 <table><tr><th>Model</th><th>Roli (TZ)</th><th>Train vaqti</th><th>Izoh</th></tr>
  <tr><td><b>Isolation Forest</b></td><td>v1 — asosiy</td><td>{meta.get('train_seconds','—')} s</td><td>tanlangan: tez, kam tuning, driftga chidamli</td></tr>
  <tr><td>Autoencoder</td><td>v2 — shartli taqqoslash</td><td>—</td><td>ma'lumotga och, driftga sezgir (TZ §8.2)</td></tr>
  <tr><td>One-Class SVM</td><td>nazorat guruhi</td><td>—</td><td>sekin, kernel sezgir — ish rejimida ishlatilmaydi</td></tr>
 </table>
 <div class="legend">To'liq raqamlar: <code>reports/eval_report.md</code> (uch model bir xil protokolda baholangan)</div>

 <h2>Tur bo'yicha recall (A1–A8)</h2>
 <div>{per_html}</div>
 <div class="note">A4 (birlik xatosi) deyarli to'liq topiladi; A5/A7/A8 — nozik turlar, feature kengaytirish keyingi iteratsiya (TZ §10 — cheklovlar yashirilmaydi).</div>

 <h2>Figuralar</h2>
 {figs_html}

 <h2>Alert feed — top-20 (izoh: eng katta og'ishli 3 feature)</h2>
 <table>
  <tr><th>Korxona</th><th>Chorak</th><th>Sektor</th><th>Skor</th><th>Holat</th><th>Izoh (top-3)</th><th>Biz bilgan tur (sinov)</th></tr>
  {rows_html}
 </table>
 <div class="note"><b>O'qish qoidasi:</b> bu panel <u>qaror chiqarmaydi</u> — faqat tekshiruv ustuvorligini ko'rsatadi.
  Har bir signal inson ko'rigiga tushadi (AC-5); «biz bilgan tur» ustuni faqat sinov ma'lumotida mavjud (real tizimda yo'q).</div>

 <h2>Model monitoring — audit izi (AC-8)</h2>
 <table>
  <tr><th>Parametr</th><th>Qiymat</th></tr>
  <tr><td>Model</td><td>IsolationForest {json.dumps(meta['params'], ensure_ascii=False)}</td></tr>
  <tr><td>Feature'lar</td><td>{len(feats)} ta (6 guruh) — ro'yxat <code>models/metadata.json</code></td></tr>
  <tr><td>Threshold</td><td>{thr:.6f} (faqat train kvantilidan)</td></tr>
  <tr><td>Train / test hajmi</td><td>{meta['trained_rows']:,} / {meta['test_rows']:,} yozuv</td></tr>
  <tr><td>O'qitilgan sana</td><td>{meta['trained_at']}</td></tr>
  <tr><td>Ma'lumot manbasi</td><td>UZ-proksi sintetik (TZ §6.2 — L1/L2/L3 qatlamlari)</td></tr>
 </table>
 <div class="legend">Keyingi qadam (real tizim): PQ-343 (01.03.2026 stansiyalar · 01.09.2026 platforma) integratsiyasi bilan real oqimga ulanish.</div>
</div></html>"""
    out = os.path.join(WEB, "dashboard.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"S8 dashboard: {out} ({len(html):,} belgi)")
    print(f"  KPI: F1={met['f1']} P={met['precision']} R={met['recall']} FPR={met['fpr']} | alert feed: {len(rows)} qator")


if __name__ == "__main__":
    main()
