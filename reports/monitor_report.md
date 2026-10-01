# Model monitoring hisoboti — dreyf va FPR trendi

> Avtomatik: `python3 scripts/run_monitor.py` · S8 (TZ §7.4) · metodika: PSI + KS + muzlatilgan threshold

## 1. Qaror: **MEDIAN-SLIDE QAYTA KALIBRLASH (R41 siyosati qo'llaniladi)**

- FPR chegaradan (0,10) oshgan davrlar: 2026Q1
- Model qayta o'qitilmaydi — threshold normal skorlar siljishiga moslashadi
- Siyosat: t = t_train + (median_davr − median_train); faqat skorlar, label yo'q
- Samara (eval_report.md §FPR nazorati): eng yomon chorak FPR 0,1075 → 0,0903 ✅

## 2. Feature dreyfi (PSI, train → test)

| # | Feature | PSI | KS stat | KS p | Holat | x̄ train | x̄ test |
|---|---|---|---|---|---|---|---|
| 1 | `quarter_index` | 12.2033 | 1.0 | 0.00e+00 | ⚪ vaqt (monitoringdan tashqari) | 8.5 | 19.5 |
| 2 | `drift_slope` | 0.1729 | 0.0736 | 6.15e-36 | 🟡 kuzatuv | 0.0006 | 0.00484 |
| 3 | `proxy_gap_x_growth` | 0.078 | 0.0561 | 4.67e-21 | 🟢 stabil | 0.00113 | 0.0022 |
| 4 | `drift_estimate` | 0.0558 | 0.0567 | 1.78e-21 | 🟢 stabil | 7.9855 | 8.91191 |
| 5 | `proxy_gap_own_dev` | 0.0455 | 0.0467 | 1.12e-14 | 🟢 stabil | 0.13776 | 0.14804 |
| 6 | `reporting_volatility` | 0.0384 | 0.0516 | 7.32e-18 | 🟢 stabil | 0.18686 | 0.19974 |
| 7 | `offsets_share_growth` | 0.032 | 0.0287 | 8.36e-06 | 🟢 stabil | -0.0007 | -0.00999 |
| 8 | `offsets_own_dev` | 0.0316 | 0.0401 | 6.22e-11 | 🟢 stabil | 0.02218 | 0.02595 |
| 9 | `ghg_intensity_growth` | 0.0305 | 0.0357 | 9.03e-09 | 🟢 stabil | 62.38577 | 15.90095 |
| 10 | `gas_share_growth` | 0.0279 | 0.0304 | 1.80e-06 | 🟢 stabil | -9e-05 | 0.00044 |
| 11 | `proxy_growth` | 0.026 | 0.0447 | 1.66e-13 | 🟢 stabil | 0.0212 | 0.017 |
| 12 | `energy_intensity_growth` | 0.0258 | 0.0334 | 1.01e-07 | 🟢 stabil | 0.00287 | 0.00316 |
| 13 | `fugitive_ratio_change` | 0.0257 | 0.0528 | 1.11e-18 | 🟢 stabil | 0.0059 | -0.00212 |
| 14 | `seasonal_residual` | 0.0195 | 0.0302 | 2.19e-06 | 🟢 stabil | 7.02165 | 7.70009 |
| 15 | `rolling_dev` | 0.0116 | 0.0229 | 7.53e-04 | 🟢 stabil | 0.00537 | 0.00548 |
| 16 | `qoq_growth_reported` | 0.0064 | 0.0286 | 8.62e-06 | 🟢 stabil | 59.33851 | 16.33877 |
| 17 | `log_reported` | 0.0026 | 0.0193 | 7.45e-03 | 🟢 stabil | 2.66942 | 2.70248 |
| 18 | `proxy_gap` | 0.002 | 0.0144 | 8.56e-02 | 🟢 stabil | 0.16349 | 0.16229 |
| 19 | `reported_to_energy` | 0.0016 | 0.0107 | 3.54e-01 | 🟢 stabil | 0.61815 | 0.60541 |
| 20 | `log_production` | 0.0013 | 0.0177 | 1.77e-02 | 🟢 stabil | 4.46155 | 4.4953 |
| 21 | `size_pct` | 0.0013 | 0.0177 | 1.77e-02 | 🟢 stabil | 0.49811 | 0.50857 |
| 22 | `energy_to_prod_dev` | 0.0013 | 0.0061 | 9.41e-01 | 🟢 stabil | -0.0015 | -0.0012 |
| 23 | `energy_intensity` | 0.001 | 0.0114 | 2.76e-01 | 🟢 stabil | 2.25149 | 2.25323 |
| 24 | `ghg_intensity` | 0.001 | 0.014 | 1.03e-01 | 🟢 stabil | 1.38364 | 1.38618 |
| 25 | `offsets_share` | 0.001 | 0.0096 | 4.87e-01 | 🟢 stabil | 0.09349 | 0.0867 |
| 26 | `gas_share` | 0.0007 | 0.0097 | 4.77e-01 | 🟢 stabil | 0.76466 | 0.76473 |
| 27 | `repeat_count` | 0.0 | 0.0264 | 5.39e-05 | 🟢 stabil | 1.08531 | 1.15043 |
| 28 | `flat_flag` | 0.0 | 0.023 | 6.93e-04 | 🟢 stabil | 0.02756 | 0.05054 |
| 29 | `jump_flag` | 0.0 | 0.0422 | 4.46e-12 | 🟢 stabil | 0.14534 | 0.10315 |
| 30 | `unit_jump_flag` | 0.0 | 0.0001 | 1.00e+00 | 🟢 stabil | 0.03246 | 0.03261 |
| 31 | `boundary_mix_flag` | 0.0 | 0.0038 | 1.00e+00 | 🟢 stabil | 0.027 | 0.03076 |
| 32 | `prod_report_gap` | 0.0 | 0.0028 | 1.00e+00 | 🟢 stabil | 0.00322 | 0.00282 |
| 33 | `energy_report_gap` | 0.0 | 0.0026 | 1.00e+00 | 🟢 stabil | 0.00018 | 0.00016 |

**Yakun:** 🟢 31 · 🟡 1 · 🔴 0 · ⚪ 1 vaqt (jami 33 feature)

> ⚪ Vaqt indeksi konstruksiya bo'yicha o'zgaradi (train davri ≠ test davri) — PSI unga ma'nosiz, shuning uchun qaror qabul qilishda hisobga olinmaydi.

## 3. Skor dreyfi

- KS stat = 0.1478 · p = 4.650e-144 → sezilarli farq
- o'rtacha skor: train -0.03682 → test -0.0293

## 4. FPR va Recall trendi (threshold muzlatilgan)

| Davr | Yozuv | Anomaliya | FPR | Recall | Alertlar |
|---|---|---|---|---|---|
| 2025Q3 | 2300 | 519 | 0.0494 | 0.3526 | 271 |
| 2025Q4 | 2300 | 483 | 0.0605 | 0.4824 | 343 |
| 2026Q1 | 2300 | 440 | 0.1075 ⚠️ | 0.6705 | 495 |
| 2026Q2 | 2300 | 397 | 0.0730 | 0.5642 | 363 |

## 5. Qaror qoidalari (modelni qachon qayta o'qitish)

| Belgi | Chegara | Amal |
|---|---|---|
| PSI > 0.25 (bitta feature) | dreyf | feature sababini tekshirish, qayta o'qitish |
| PSI 0.1–0.25 | kuzatuv | monitoringni kuchaytirish |
| Skor KS p < 0.05 | taqsimot farqi | kalibratsiya/taqsimot tekshiruvi |
| FPR > 0,10 (davr) | AC-2 buzilishi | median-slide kalibrlash (eval_report.md §FPR nazorati) |

## 6. Figuralar

- `reports/figures/drift_psi.png`
- `reports/figures/fpr_trend.png`

---

**Izoh:** threshold hech qachon test davridan tanlanmaydi — dreyf aniqlash uchun ham train taqsimoti asos qilib olinadi (p-hacking istisnosi).
