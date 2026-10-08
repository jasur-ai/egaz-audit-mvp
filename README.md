# E-GAZ-AUDIT MVP — ishlaydigan prototip

[![CI](https://github.com/jasur-ai/egaz-audit-mvp/actions/workflows/ci.yml/badge.svg)](https://github.com/jasur-ai/egaz-audit-mvp/actions/workflows/ci.yml) · **Repo:** https://github.com/jasur-ai/egaz-audit-mvp

> Bu papka — **TZ (`../TZ/Loyiha1_AI_anomaliya_TZ.md`) bo'yicha S0–S10 bosqichlarning bajarilgan yadrosi**
> (S1 generator → S3 feature → S4 IF → S5 AE/OCSVM → S6 baholash → S7 serving).
> Real korxona ma'lumotlari yopiq bo'lgani uchun UZ-proksi sintetik oqim ishlatiladi (TZ §6 — uch qatlamli strategiya).

## Jonli ko'rish va uzilish paytidagi zaxira

- **Asosiy panel (Cloudflare):** https://egaz-audit.pages.dev/
- **Mustaqil statik zaxira (GitHub Pages):** https://jasur-ai.github.io/egaz-audit-mvp/
- **To'liq oflayn nusxa:** shu repodagi `docs/index.html`; tanlov papkasida `08-DEMO-OFFLINE.html`.

GitHub Pages zaxirasi — brauzer ichida ishlaydigan kalkulyator va huquqiy xarita; u jonli API/panelning
ma'lumot bazasi yoki Telegram botining o'rnini bosmaydi. Internet butunlay uzilsa, oflayn HTML faylni
kompyuterda oching. Zaxira holatini tekshirish: workspace'da `python3 infra/monitor_tanlov_external.py`.

## Ishga tushirish

```bash
cd MVP
make install                      # yoki: pip install -r requirements.txt
make demo                         # S1→S6 quvur (~35 s) + S8 dashboard
make test                         # 273 test
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
| S9 Test/Docker/hujjat | CI, 20+ test, docs | ✅ **300 test** · `Dockerfile` · `docker-compose.yml` · `.github/workflows/ci.yml` · `docs/architecture.md` · `docs/limitations.md` |
| **S12 Kirishsiz rejim** | ruxsatsiz tekshiruv yo'llari | ✅ **8 yo'l** (`src/kirishsiz/`) · 51 test · CLI `scripts/kirishsiz.py --list` · ochiq manbalar `scripts/fetch_public.py` · hujjat `docs/kirishsiz_yollar.md` |
| **S13 A-qatlam (92 kun)** | ochiq manbalar bilan birinchi tekshiruv | ✅ `screener.dirty_hours_by_time` + `sector.directional_enrichment` (lift) · `scripts/kirishsiz.py sektor` · 20 test · hisobot `docs/a_qatlam_hisoboti.md` |
| **S14 A-qatlam v2 (180 kun)** | real obyektlar bilan tekshiruv | ✅ `facilities.py` (manbali koordinatalar, radius, ajratilmaydigan guruhlar) · `data/public/nomzodlar_uz.json` (5 obyekt) · CLI `nomzodlar` va `sektor --haqiqiy` · 14 test · 0/180 kun · IES NO2 lift 2,30 · hisobot `docs/a_qatlam_hisoboti.md` |
| **S15 B-qatlam: mass-balans** | pastdan yuqoriga tekshiruv (yo'l #2) | ✅ `bottomup.py` (AP-42 EF zanjiri · Briggs σ · Gauss · mos kelish ulushi) · CLI `scripts/kirishsiz.py pastdan` · **33 test** · EF 0,40–1,42 g NOx/kWh → 0,074–0,260 kg/s → model 5,7–11,5 vs kuzatuv +9,24 µg/m³ (nisbat 0,80–1,62) · hujjat `docs/b_qatlam_mass_balans.md` |
| **S16 B-qatlam 2-qism** | EF taqqoslash · PM2,5 manbasi · retseptorlar · mavsum | ✅ EMEP/EEA 2023 1.A.1.a **89 g NOx/GJ** ↔ AP-42 (farq **1,5%**) · PM2,5: birlamchi zarra **4,2%**, chang **emas** (lift 0,76) · yo'nalish profillari (NO2 60° / PM2,5 105°) · usul chegarasi **o'lchandi** (7,2 km da bir xil katak) · 4 retseptor + **Angren IES** (ko'mir) reyestrga · **+46 test** (aerosol 22 · mavsum 14 · retseptorlar 18 · EMEP 6) · hujjat `docs/b_qatlam_2_qism.md` |
| **S17 Isitish mavsumi (365 kun)** | oynani orqaga uzaytirish | ✅ `mavsum.epizod_atributsiya()` · CLI `scripts/kirishsiz.py mavsum` · `fetch_public.py --source open-meteo-aq-tarix` · **+5 test** · natija: **21/181 ↔ 0/183** (norma oshishlari faqat isitish mavsumida), noyabr PM2,5 **31,23**, IES lifti barqaror (**1,21 ↔ 1,20**), epizodlar 6/10/5, sokin soatlar **14,8%** · hujjat `docs/isitish_mavsumi.md` |
| **S19 Huquqiy asos (R54)** | Har element — farmon/qaror bilan | ✅ `src/kirishsiz/huquqiy_asos.py` (21 hujjat · 22 element · **53 bog'lanish**, har elementda ≥2 asos) · CLI `huquqiy --xarita/--qamrov/--tekshir/--havola` · `scripts/build_huquqiy_hujjat.py` · xatlarga registrdan 6 asos · **+13 test** → **300** · hujjat `docs/huquqiy_asos.md`, `docs/20-qonuniy-asos-xaritasi.md` |
| **S18 Retseptorlar + maishiy isitish** | 365 kun × 4 retseptor · isitish hissasi | ✅ `mavsum.taqqoslash()` + `pearson()` · `src/kirishsiz/isitish.py` (EMEP/EEA 1.A.4 Tier 1 · quti modeli · garmonik shamol · traser testi) · CLI `taqqos` va `isitish` · `scripts/build_requests_2026_10.py` (4 so'rov) · **+14 test** → **300** · natija: Toshkent lift **1,67×** · Ohangaron **1,38×** · **Angren 0,97× va 0 epizod** (4 km ko'mir IES nazorati) · r(Toshkent↔Ohangaron) **0,816** · qattiq yoqilg'i ulushi bahosi **10–25%** (gaz 330× kam PM2,5 beradi) · hujjat `docs/maishiy_isitish.md`, `docs/mvp_tayyorlik.md` |
| S10 Demo/himoya | taqdimot, final hisobot | ✅ `presentation/DEMO.md` (10 slayd + hakam savollari); hisobot: `reports/eval_report.md` |
