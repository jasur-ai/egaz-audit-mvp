# Arxitektura — E-GAZ-AUDIT MVP (S1–S8)

```
┌─ S1 generator ────────────┐   ┌─ S3 feature store ─────────┐   ┌─ S4/S5 modellar ───────────┐
│ uz_proxy_v1.csv.gz        │   │ features_v1.csv.gz         │   │ if_v1.joblib (600×0,5)     │
│ 2 300 korxona × 22 kvartal│──▶│ 26 feature / 6 guruh       │──▶│ ae.joblib · ocsvm.joblib   │
│ A1–A8 injection 15%       │   │ feature_dictionary.md      │   │ metadata.json (audit izi)  │
└───────────────────────────┘   └────────────────────────────┘   └────────────┬───────────────┘
                                                                              │
┌─ S8 dashboard ────────────┐   ┌─ S7 serving ───────────────┐   ┌─ S6 baholash ──────────────┐
│ web/dashboard.html        │◀──│ FastAPI :8001              │◀──│ eval_report.md             │
│ KPI + alert feed + izoh   │   │ /v1/score · /v1/model/info │   │ PR/ROC · FPR · tur recall  │
└───────────────────────────┘   └────────────────────────────┘   └────────────────────────────┘
```

## Qatlamlar (TZ §5.1 oqimiga mos)

| Qatlam | Kod | Mas'uliyat |
|---|---|---|
| **Ma'lumot** | `src/generator.py` | UZ-proksi: sektorlar, kvartallar, A1–A8 injected label |
| **Feature** | `src/features.py` | 6 guruh, 26 feature; `implied_ghg` (ground truth) **ko'rinmaydi** |
| **Model** | `src/models.py` | Uch nomzod bitta protokolda; scaler har model ichida |
| **Baholash** | `src/evaluate.py` | Threshold faqat train'dan; FPR/tur recall/biznes modeli |
| **Serving** | `src/api/app.py` | Sinxron endpointlar (FastAPI threadpool) — TZ S7 tuzoq qoidasi |
| **UI** | `scripts/build_dashboard.py` | Statik, CDN'siz HTML — audit paneli |

## Asosiy dizayn qarorlari (ADR uslubida)

1. **Nega sintetik ma'lumot?** Real korxona GHG ma'lumotlari hozircha yopiq (TZ §6.1);
   ground truth faqat injection bilan bo'ladi (TZ §6.4) — SWaT/TEP amaliyoti.
2. **Nega IF birinchi?** inferens 36× tez (OCSVM'ga nisbatan), kam tuning, driftga chidamli (TZ §8.3).
3. **Nega `max_samples=0,5`?** R34 tajribada F1 0,488 → 0,538 (izolyatsiya daraxtlari xilma-xilligi).
4. **Nega threshold train'dan?** p-hacking'ni istisno qilish; alert-rate S0'da muzlatilgan (0,12).
5. **Nega model raqamni o'zgartirmaydi?** AC-5: model faqat ustuvorlik beradi, qaror insonda.

## Ishlab chiqish oqimi

```bash
make install   # pip install -r requirements.txt
make demo      # python3 scripts/run_all.py && python3 scripts/build_dashboard.py
make test      # pytest -q tests/  (25 test)
make serve     # uvicorn src.api.app:app --port 8001
make docker    # docker compose up --build
```
