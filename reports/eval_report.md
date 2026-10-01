# S6 — Baholash hisoboti (avtomatik)

**Yozuvlar:** 50,600 (train 41,400 / test 9,200) · **injection:** 15% · **seed:** 42
**Feature:** 33 ta (8 guruh) · **Quvur vaqti:** 26.5 s

## Asosiy natijalar (test = 2025Q3–2026Q2)

| Model | Precision | Recall | F1 | ROC-AUC | PR-AUC | FPR | Threshold (train) |
|---|---|---|---|---|---|---|---|
| IF | 0.6352 | 0.5084 | **0.5648** | 0.8117 | 0.5483 | 0.073 | 0.0000 |
| AE | 0.5307 | 0.3991 | **0.4556** | 0.7801 | 0.4401 | 0.0882 | 0.6938 |
| OCSVM | 0.5647 | 0.5432 | **0.5538** | 0.7747 | 0.4891 | 0.1046 | 2.9201 |

**AC-2 tekshiruvi (FPR ≤ 0,10):** IF FPR = 0.073 → ✅ bajarildi

## FPR nazorati (R41) — uchta siyosat

AC-2: FPR ≤ 0,10. Har chorak kesimida:

| Davr | n | Statik FPR | Siljuvchi kvantil FPR | **Median-slide FPR** | Recall (slide) |
|---|---|---|---|---|---|
| 18 | 2,300 | 0.0494 | 0.0494 | 0.0466 | 0.3218 |
| 19 | 2,300 | 0.0605 | 0.0605 | 0.0501 | 0.4079 |
| 20 | 2,300 | 0.1075 ⚠ | 0.107 | 0.0903 | 0.5886 |
| 21 | 2,300 | 0.073 | 0.0646 | 0.0583 | 0.5214 |

| Siyosat | Eng yuqori choraklik FPR | Umumiy F1 | Umumiy FPR | Alert ulushi |
|---|---|---|---|---|
| Statik (train kvantili) | 0.1075 ❌ | 0.5648 | 0.073 | 16.0% |
| Siljuvchi kvantil (oyna 4) | 0.107 ❌ | 0.5625 | 0.0706 | 15.7% |
| **Median-slide (tavsiya)** | **0.0903** ✅ | 0.5317 | 0.0615 | 13.9% |

**Xulosa:** siljuvchi kvantil FPR muammosini yechmaydi (u **alert hajmini** mo'ljallaydi). FPR ni buzadigan narsa — **normal skorlar siljishi**; `median_slide_threshold` shuni turadi: eng yomon chorak 0.1075 → **0.0903** (AC-2 bajarildi), narxi — recall 0.5084 → 0.4513 (alert 2.1% kamaydi).

> Label'siz ekani muhim: hech qaysi siyosat **test label'lariga** qaramaydi — faqat skor
> taqsimoti ishlatiladi. Real tizimda chorak yakunida operator tekshiruv natijalarini
> (label'larni) qo'shsa, kalibrlash yanada aniq bo'ladi. Siyosatlar `models/metadata.json`
> da yozilgan (audit izi).

## Gibrid kanal: IF ∪ ochiq qoidalar (R41)

IF yagona-feature signallarini suyultiradi (diagnostika: `offsets_own_dev` yakka-feature
AUC = 0,93, ammo IF A7 ning 13% ini topadi). Shu sababli model yoniga **shaffof qoidalar**
qo'shiladi — chegaralar **validatsiya oynasida (q16–17)** tanlangan, test tanlovga kirmagan:

| Qoida | Feature | Shart | Validatsiya (P / R / F1) |
|---|---|---|---|
| R-A5 aktivlik kross-tekshiruvi | `prod_report_gap` | >= 0.01 | 1.0 / 1.0 / 1.0 |
| R-A7 offset devori | `offsets_own_dev` | >= 0.7 | 0.433 / 0.643 / 0.517 |

| Konfiguratsiya | Precision | Recall | F1 | FPR | Alert | A5 recall | A7 recall | A8 recall |
|---|---|---|---|---|---|---|---|---|
| Statik (IF, R40) | 0.6352 | 0.5084 | **0.5648** | 0.073 | 16.0% | 1.0 | 0.129 | 0.059 |
| Median-slide (faqat IF) | 0.6469 | 0.4513 | **0.5317** | 0.0615 | 13.9% | 1.0 | 0.079 | 0.052 |
| **Median-slide + qoidalar** | 0.6406 | 0.4943 | **0.558** | 0.0693 | 15.4% | 1.0 | 0.633 | 0.059 |

**A7: 0.129 → 0.633** — qoida kanali A7 ni ko'rinadigan
qiladi (offset devori). **A5 allaqachon 1,0** (aktivlik kross-tekshiruvi feature'i tufayli).
**A8 saqlanib qoladi (0.059)** — orakul AUC≈0,59: bu feature yetishmovchiligi
emas, ma'lumotdagi signal chegarasi (pastdagi cheklovlar).

> Qoidalar **modelni almashtirmaydi**: ular audit qilinadigan qo'shimcha signal; har biri
> bitta jumlada izohlanadi (TZ §7 tamoyil 3 — explainability-first).

## IF ish nuqtasi (alert-rate sweep — threshold train kvantilidan)

| Alert-rate | F1 | Precision | Recall | FPR |
|---|---|---|---|---|
| 0.06 | 0.2983 | 0.5811 | 0.2007 | 0.0361 |
| 0.08 | 0.4284 | 0.636 | 0.323 | 0.0462 |
| 0.10 | 0.5091 | 0.6452 | 0.4203 | 0.0577 |
| 0.12 ← **tanlangan (S0)** | 0.5648 | 0.6352 | 0.5084 | 0.073 |
| 0.15 | 0.5858 | 0.5833 | 0.5884 | 0.105 |

## IF bo'yicha qo'shimcha

- **Recall@top-5%** (faqat eng shubhali 5%ni tekshirish): **0.1441**
- **Biznes taqqoslash:** bazadagi anomaliya ulushi 0.1999, model top-200 aniqligi 0.735 → **3.7× yaxshilanish**
- **Inferens:** 0.04 ms / 1 000 yozuv
- **Tur bo'yicha recall (A1–A8):** {"A1": 0.5, "A2": 0.256, "A3": 0.255, "A4": 0.986, "A5": 1.0, "A6": 0.589, "A7": 0.129, "A8": 0.059}

## Figuralar

- `reports/figures/pr_roc.png`
- `reports/figures/score_dist.png`
- `reports/figures/per_type_recall.png`

## Cheklovlar (TZ §10 bilan mos)

- Sintetik A1–A8 real soxtalashtirishdan soddaroq bo'lishi mumkin (model yuqorisini baholaydi).
- OCSVM train uchun qism-to'plamda o'qitildi (TZ §8.3: nazorat guruhi roli).
- Threshold train kvantilidan olinadi (test'ga qaramaydi) — p-hacking yo'q.
- Model raqamni O'ZGARTIRMAYDI: faqat tekshiruv ustuvorligini belgilaydi (AC-5/§8.4).
- **A8 chegarasi (R41):** vaqt-aralashtirish siljishi 0,15·|Δaktivlik| ≈ 1–3% — normal
  hisobot shovqini (σ≈6%) ichida. Orakul (implied_ghg'ni bilgan ideal detektor) A8 uchun
  AUC≈0,59 (|Δ|≥10% qatorlarda 0,66) — ya'ni A8 zaifligi feature yetishmovchiligi emas,
  **ma'lumotdagi signal chegarasi**. Yuqori aniqlikdagi qoida ham yo'q (P≈0,02).
- Proksi (`proxy`) koeffitsiyentlari FAQAT train davrida fit qilinadi (test fit'ga kirmaydi);
  `implied_ghg` hech qanday feature'da ishlatilmaydi.
- **Generatorda to'qnashuv (R41 diagnostikasi):** bir kvartalga ikki anomaliya tushsa,
  `anomaly_type` faqat bittasini yozadi (≈0,06% qator). Shu sabab tur bo'yicha recall
  baholari pastroq ko'rinishi mumkin (iz qolgan, yorliq boshqa turda).
