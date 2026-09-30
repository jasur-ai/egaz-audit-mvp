# Model monitoring hisoboti — dreyf va FPR trendi

> Avtomatik: `python3 scripts/run_monitor.py` · S8 (TZ §7.4) · metodika: PSI + KS + muzlatilgan threshold

## 1. Qaror: **THRESHOLDNI QAYTA KALIBRLASH tavsiya etiladi**

- FPR chegaradan (0,10) oshgan davrlar: 2026Q1
- Model qayta o'qitilmaydi — threshold yangi train davridan qayta hisoblanadi (train kvantili)

## 2. Feature dreyfi (PSI, train → test)

| # | Feature | PSI | KS stat | KS p | Holat | x̄ train | x̄ test |
|---|---|---|---|---|---|---|---|
| 1 | `quarter_index` | 12.2033 | 1.0 | 0.00e+00 | ⚪ vaqt (monitoringdan tashqari) | 8.5 | 19.5 |
| 2 | `drift_slope` | 0.1729 | 0.0736 | 6.15e-36 | 🟡 kuzatuv | 0.0006 | 0.00484 |
| 3 | `drift_estimate` | 0.0558 | 0.0567 | 1.78e-21 | 🟢 stabil | 7.9855 | 8.91191 |
| 4 | `reporting_volatility` | 0.0384 | 0.0516 | 7.32e-18 | 🟢 stabil | 0.18686 | 0.19974 |
| 5 | `offsets_share_growth` | 0.032 | 0.0287 | 8.36e-06 | 🟢 stabil | -0.0007 | -0.00999 |
| 6 | `ghg_intensity_growth` | 0.0305 | 0.0357 | 9.03e-09 | 🟢 stabil | 62.38577 | 15.90095 |
| 7 | `gas_share_growth` | 0.0279 | 0.0304 | 1.80e-06 | 🟢 stabil | -9e-05 | 0.00044 |
| 8 | `energy_intensity_growth` | 0.0258 | 0.0334 | 1.01e-07 | 🟢 stabil | 0.00287 | 0.00316 |
| 9 | `fugitive_ratio_change` | 0.0257 | 0.0528 | 1.11e-18 | 🟢 stabil | 0.0059 | -0.00212 |
| 10 | `seasonal_residual` | 0.0195 | 0.0302 | 2.19e-06 | 🟢 stabil | 7.02165 | 7.70009 |
| 11 | `rolling_dev` | 0.0116 | 0.0229 | 7.53e-04 | 🟢 stabil | 0.00537 | 0.00548 |
| 12 | `qoq_growth_reported` | 0.0064 | 0.0286 | 8.62e-06 | 🟢 stabil | 59.33851 | 16.33877 |
| 13 | `log_reported` | 0.0026 | 0.0193 | 7.45e-03 | 🟢 stabil | 2.66942 | 2.70248 |
| 14 | `reported_to_energy` | 0.0016 | 0.0107 | 3.54e-01 | 🟢 stabil | 0.61815 | 0.60541 |
| 15 | `log_production` | 0.0013 | 0.0177 | 1.77e-02 | 🟢 stabil | 4.46155 | 4.4953 |
| 16 | `size_pct` | 0.0013 | 0.0177 | 1.77e-02 | 🟢 stabil | 0.49811 | 0.50857 |
| 17 | `energy_to_prod_dev` | 0.0013 | 0.0061 | 9.41e-01 | 🟢 stabil | -0.0015 | -0.0012 |
| 18 | `energy_intensity` | 0.001 | 0.0114 | 2.76e-01 | 🟢 stabil | 2.25149 | 2.25323 |
| 19 | `ghg_intensity` | 0.001 | 0.014 | 1.03e-01 | 🟢 stabil | 1.38364 | 1.38618 |
| 20 | `offsets_share` | 0.001 | 0.0096 | 4.87e-01 | 🟢 stabil | 0.09349 | 0.0867 |
| 21 | `gas_share` | 0.0007 | 0.0097 | 4.77e-01 | 🟢 stabil | 0.76466 | 0.76473 |
| 22 | `repeat_count` | 0.0 | 0.0264 | 5.39e-05 | 🟢 stabil | 1.08531 | 1.15043 |
| 23 | `flat_flag` | 0.0 | 0.023 | 6.93e-04 | 🟢 stabil | 0.02756 | 0.05054 |
| 24 | `jump_flag` | 0.0 | 0.0422 | 4.46e-12 | 🟢 stabil | 0.14534 | 0.10315 |
| 25 | `unit_jump_flag` | 0.0 | 0.0001 | 1.00e+00 | 🟢 stabil | 0.03246 | 0.03261 |
| 26 | `boundary_mix_flag` | 0.0 | 0.0038 | 1.00e+00 | 🟢 stabil | 0.027 | 0.03076 |

**Yakun:** 🟢 24 · 🟡 1 · 🔴 0 · ⚪ 1 vaqt (jami 26 feature)

> ⚪ Vaqt indeksi konstruksiya bo'yicha o'zgaradi (train davri ≠ test davri) — PSI unga ma'nosiz, shuning uchun qaror qabul qilishda hisobga olinmaydi.

## 3. Skor dreyfi

- KS stat = 0.146 · p = 1.606e-140 → sezilarli farq
- o'rtacha skor: train -0.03656 → test -0.02824

## 4. FPR va Recall trendi (threshold muzlatilgan)

| Davr | Yozuv | Anomaliya | FPR | Recall | Alertlar |
|---|---|---|---|---|---|
| 2025Q3 | 2300 | 519 | 0.0590 | 0.3353 | 279 |
| 2025Q4 | 2300 | 483 | 0.0699 | 0.4783 | 358 |
| 2026Q1 | 2300 | 440 | 0.1258 ⚠️ | 0.6636 | 526 |
| 2026Q2 | 2300 | 397 | 0.0883 | 0.5390 | 382 |

## 5. Qaror qoidalari (modelni qachon qayta o'qitish)

| Belgi | Chegara | Amal |
|---|---|---|
| PSI > 0.25 (bitta feature) | dreyf | feature sababini tekshirish, qayta o'qitish |
| PSI 0.1–0.25 | kuzatuv | monitoringni kuchaytirish |
| Skor KS p < 0.05 | taqsimot farqi | kalibratsiya/taqsimot tekshiruvi |
| FPR > 0,10 (davr) | AC-2 buzilishi | thresholdni qayta baholash (train'dan) |

## 6. Figuralar

- `reports/figures/drift_psi.png`
- `reports/figures/fpr_trend.png`

---

**Izoh:** threshold hech qachon test davridan tanlanmaydi — dreyf aniqlash uchun ham train taqsimoti asos qilib olinadi (p-hacking istisnosi).
