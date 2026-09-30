# Feature lug'ati (TZ §7 — 6 guruh, 26 feature)

> Har feature: formula, manba ustun (faqat "ko'rinadigan"), kutilgan yo'nalish.
> `implied_ghg` (ground truth) modelga **berilmaydi** — aks holda baholash ma'nosiz bo'ladi.

## 1. Nisbat (3)
| Feature | Formula | Nimani tutadi |
|---|---|---|
| `log_reported` | log1p(reported_ghg) | aniqlik/miqyos bazasi |
| `qoq_growth_reported` | Δ% (chorakma-chorak) | keskin sakrash (A1, A4, A7) |
| `reported_to_energy` | reported / reported_energy | hisob-kitob mosligi (A2, A4) |

## 2. Energiya (4)
| Feature | Formula | Nimani tutadi |
|---|---|---|
| `energy_intensity` | energy / production | texnologik me'yor buzilishi |
| `energy_intensity_growth` | Δ% intensity | A5 (energiya ishlab chiqarishdan uzilishi) |
| `ghg_intensity` | reported / production | A1, A4 (nisbat o'zgarishi) |
| `ghg_intensity_growth` | Δ% intensity | A1, A7 |

## 3. Tarkib (5)
| Feature | Formula | Nimani tutadi |
|---|---|---|
| `gas_share` | gas ulushi (e'lon) | A2 (EF yangilanmagan mix o'zgarishi) |
| `gas_share_growth` | Δ share | A2 |
| `offsets_share` | offsets / reported | A7 (ikki marta hisoblangan kredit) |
| `offsets_share_growth` | Δ share | A7 |
| `fugitive_ratio_change` | Δ% fugitive | A3 (bo'lim nolga tushirilgan) |

## 4. Dinamika (5)
| Feature | Formula | Nimani tutadi |
|---|---|---|
| `rolling_dev` | (x − MA4)/MA4 | umumiy chetlanish |
| `repeat_count` | bir xil qiymat ketma-ketligi | A6 (takror) |
| `flat_flag` | repeat ≥ 3 | A6 |
| `seasonal_residual` | (x − med4)/med4 | mavsumiy fon |
| `drift_slope` | 4 chorak trend (norm.) | sekin dreyf |

## 5. Aniqlik (4)
| Feature | Formula | Nimani tutadi |
|---|---|---|
| `drift_estimate` | MA4 / med4 | tizimli siljish |
| `jump_flag` | |Δ%| > 35% | A1, A4, A7 |
| `unit_jump_flag` | nisbat >100× yoki <0,01× | **A4** (birlik xatosi) |
| `boundary_mix_flag` | chorak chegarasi + chetlanish | **A8** (davr siljishi) |

## 6. Miqyos (5)
| Feature | Formula | Nimani tutadi |
|---|---|---|
| `log_production` | log1p(reported_production) | miqyos |
| `size_pct` | log_production percentile | kattalar filtri |
| `quarter_index` | vaqt indeksi | rejim |
| `energy_to_prod_dev` | sektor medianidan chetlanish | sektor ichida anomaliya |
| `reporting_volatility` | std4/mean4 | beqaror hisobot |

**Audit:** feature'larni hisoblash kodi versiyalanadi (`src/features.py`); model metadata'da
feature ro'yxati va `threshold_if` saqlanadi (TZ AC-8).
