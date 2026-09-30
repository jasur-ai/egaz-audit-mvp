# S6 — Baholash hisoboti (avtomatik)

**Yozuvlar:** 50,600 (train 41,400 / test 9,200) · **injection:** 15% · **seed:** 42
**Feature:** 26 ta (6 guruh) · **Quvur vaqti:** 24.1 s

## Asosiy natijalar (test = 2025Q3–2026Q2)

| Model | Precision | Recall | F1 | ROC-AUC | PR-AUC | FPR | Threshold (train) |
|---|---|---|---|---|---|---|---|
| IF | 0.5896 | 0.4954 | **0.5384** | 0.7888 | 0.4985 | 0.0861 | 0.0000 |
| AE | 0.457 | 0.3469 | **0.3944** | 0.6741 | 0.3661 | 0.103 | 0.5358 |
| OCSVM | 0.5231 | 0.5291 | **0.5261** | 0.7359 | 0.4304 | 0.1205 | 2.9610 |

**AC-2 tekshiruvi (FPR ≤ 0,10):** IF FPR = 0.0861 → ✅ bajarildi

## IF ish nuqtasi (alert-rate sweep — threshold train kvantilidan)

| Alert-rate | F1 | Precision | Recall | FPR |
|---|---|---|---|---|
| 0.06 | 0.3026 | 0.5494 | 0.2088 | 0.0428 |
| 0.08 | 0.4092 | 0.5882 | 0.3138 | 0.0549 |
| 0.10 | 0.4913 | 0.6022 | 0.4149 | 0.0685 |
| 0.12 ← **tanlangan (S0)** | 0.5384 | 0.5896 | 0.4954 | 0.0861 |
| 0.15 | 0.5454 | 0.5339 | 0.5574 | 0.1216 |

## IF bo'yicha qo'shimcha

- **Recall@top-5%** (faqat eng shubhali 5%ni tekshirish): **0.1223**
- **Biznes taqqoslash:** bazadagi anomaliya ulushi 0.1999, model top-200 aniqligi 0.67 → **3.4× yaxshilanish**
- **Inferens:** 0.04 ms / 1 000 yozuv
- **Tur bo'yicha recall (A1–A8):** {"A1": 0.533, "A2": 0.412, "A3": 0.42, "A4": 0.993, "A5": 0.158, "A6": 0.642, "A7": 0.079, "A8": 0.065}

## Figuralar

- `reports/figures/pr_roc.png`
- `reports/figures/score_dist.png`
- `reports/figures/per_type_recall.png`

## Cheklovlar (TZ §10 bilan mos)

- Sintetik A1–A8 real soxtalashtirishdan soddaroq bo'lishi mumkin (model yuqorisini baholaydi).
- OCSVM train uchun qism-to'plamda o'qitildi (TZ §8.3: nazorat guruhi roli).
- Threshold train kvantilidan olinadi (test'ga qaramaydi) — p-hacking yo'q.
- Model raqamni O'ZGARTIRMAYDI: faqat tekshiruv ustuvorligini belgilaydi (AC-5/§8.4).
