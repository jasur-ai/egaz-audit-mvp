# E-GAZ-AUDIT MVP — ishlaydigan prototip

[![CI](https://github.com/jasur-ai/egaz-audit-mvp/actions/workflows/ci.yml/badge.svg)](https://github.com/jasur-ai/egaz-audit-mvp/actions/workflows/ci.yml) · **Repo:** https://github.com/jasur-ai/egaz-audit-mvp

> Bu papka — **TZ (`../TZ/Loyiha1_AI_anomaliya_TZ.md`) bo'yicha S0–S10 bosqichlarning bajarilgan yadrosi**
> (S1 generator → S3 feature → S4 IF → S5 AE/OCSVM → S6 baholash → S7 serving).
> Real korxona ma'lumotlari yopiq bo'lgani uchun UZ-proksi sintetik oqim ishlatiladi (TZ §6 — uch qatlamli strategiya).

## Ishga tushirish

```bash
cd MVP
make install                      # yoki: pip install -r requirements.txt
make demo                         # S1→S6 quvur (~35 s) + S8 dashboard
make test                         # 141 test
make monitor                      # dreyf/FPR trendi hisoboti
make serve                        # S7: serving :8001
make docker                       # S9: konteyner
```

## Natijalar qayerda

| Fayl | Nima |
|---|---|
| `data/uz_proxy_v1.csv.gz` | S1: ≈50 000 korxona-kvartal yozuvi (A1–A8 injected) |
| `data/features_v1.csv.gz` | S3: 26 feature (6 guruh) |
| `models/if_v1.joblib`, `ocsvm.joblib`, `ae.joblib` | S4/S5: uch model + `metadata.json` (audit izi) |
| `reports/eval_report.md` | S6: metrikalar, FPR, recall@k, tur bo'yicha recall, induksiya vaqti |
| `reports/figures/*.png` | PR-kurva, skor taqsimoti, tur bo'yicha recall |
| `web/dashboard.html` | S8 monitoring paneli (KPI, alert feed, izohlar, dreyf/FPR trendi, audit izi) |
| `reports/monitor_report.md` | Dreyf hisoboti: PSI/KS jadvali, FPR trendi, qayta o'qitish/kalibrlash qarori |
| `deploy/` | Ishlab chiqarish tarkibi (compose prod + healthcheck + avtomatik kunlik monitoring) |

## Bosqichlar xaritasi (TZ §4)

| Bosqich | Deliverable (TZ) | Holat |
|---|---|---|
| S1 UZ-proksi generator | `data/synthetic/uz_proxy_v1.parquet`, `generator.py`, `dataset_card.md` | ✅ `src/generator.py` (+ CSV; `dataset_card.md` README ichida) |
| S2 EDA + baseline | `notebooks/01_eda.ipynb`, `reports/baseline_metrics.md` | ✅ baseline hisoboti S6 hisoboti ichida (statistik baseline satri) |
| S3 Feature engineering | `src/features/build.py`, `feature_dictionary.md` | ✅ `src/features.py` + `docs/feature_dictionary.md` |
| S4 Model v1 — IF | `models/if_v1/`, `reports/if_v1_metrics.md` | ✅ `models/if_v1.joblib` + metadata |
| S5 Model v2 — AE (+OCSVM) | AE/OCSVM qiyosi | ✅ `src/models.py` — uch model, bitta baholash protokolida |
| S6 Baholash harness | `reports/eval_report.md` + `figures/*.png` | ✅ `src/evaluate.py` |
| S7 Serving | FastAPI + `/score` | ✅ `src/api/app.py` (sinxron endpointlar — FastAPI avtomatik threadpool; TZ §S7 tuzoq qoidasi) |
| S8 Dashboard | `dashboard/app.py`, skrinshotlar | ✅ `web/dashboard.html` (statik, CDN'siz; `make dashboard`) |
| S8 Monitoring (real qism) | dreyf/FPR trendi | ✅ `src/monitor.py` + `scripts/run_monitor.py` — PSI/KS, FPR trendi, qaror qoidalari (dashboard'ga ulangan) |
| S9 Test/Docker/hujjat | CI, 20+ test, docs | ✅ **141 test** · `Dockerfile` · `docker-compose.yml` · `.github/workflows/ci.yml` · `docs/architecture.md` · `docs/limitations.md` |
| **S12 Kirishsiz rejim** | ruxsatsiz tekshiruv yo'llari | ✅ **8 yo'l** (`src/kirishsiz/`) · 51 test · CLI `scripts/kirishsiz.py --list` · ochiq manbalar `scripts/fetch_public.py` · hujjat `docs/kirishsiz_yollar.md` |
| S10 Demo/himoya | taqdimot, final hisobot | ✅ `presentation/DEMO.md` (10 slayd + hakam savollari); hisobot: `reports/eval_report.md` |
