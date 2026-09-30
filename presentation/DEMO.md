# S10 — Demo va himoya stsenariysi (8–10 daqiqa)

> Har bir slayd ortida **ishlaydigan artefakt** bor — so'z emas, natija ko'rsatiladi.

| # | Slayd | Nima ko'rsatiladi | Vaqt |
|---|---|---|---|
| 1 | Muammo | VM-783 bo'yicha 2 335 obyekt; 44 stansiya (≈1,9%); PF-46 majburiyati | 40 s |
| 2 | Savol | «Qaysi hisobotni birinchi tekshirish kerak?» — 750 tekshiruv/yil (Sputnik) | 30 s |
| 3 | Ma'lumot strategiyasi | TZ §6.2 uch qatlam (L1/L2/L3); nega sintetik oqlanadi | 50 s |
| 4 | Quvur | `make demo` jonli: generator → feature → IF → hisobot (35 s) | 90 s |
| 5 | Natija — metrikalar | F1 0,538 · AUC 0,789 · **FPR 0,086 (AC-2 ✅)** · biznes 3,4× | 60 s |
| 6 | Model tanlovi | IF vs AE vs OCSVM jadvali (TZ §8.2) — nega IF birinchi | 60 s |
| 7 | Izohlanuvchanlik | Dashboard: top-20 alert + har biriga top-3 sabab (z-qiymat) | 80 s |
| 8 | Ish rejimi | `POST /v1/score` jonli misol (alert: ha/yo'q + explain_top3) | 60 s |
| 9 | Cheklovlar | `docs/limitations.md` — halol ro'yxat (A5/A7/A8, sintetik oqim) | 50 s |
| 10 | Yo'l xaritasi | PQ-343: 01.03.2026 stansiyalar → 01.09.2026 platforma → real oqim | 40 s |

## Jonli demo buyruqlari (terminal)

```bash
cd 01-Loyiha1-Carbon-Emission/MVP
make demo               # quvur + dashboard
make test               # 25 test — yashil
make serve              # :8001
curl -s localhost:8001/v1/model/info | python3 -m json.tool | head -20
```

```bash
# jonli skoring (test to'plamidan bir anomaliya yozuvi)
python3 - <<'PY'
import pandas as pd, requests, sys; sys.path.insert(0,'.')
from src import features as F
f = pd.read_csv("data/features_v1.csv.gz"); row = f[f["label"]==1].iloc[0]
r = requests.post("http://127.0.0.1:8001/v1/score",
                  json={"features": {k: float(row[k]) for k in F.FEATURES}})
print(r.json())
PY
```

## Kutiladigan savollar (hakam/taqrizchi)

| Savol | Javob (dalil) |
|---|---|
| «Sintetik ma'lumot bilan natija ishonchlimi?» | Ground truth boshqa yo'l yo'q (TZ §6.4); A1–A8 turlari kod bilan izlanadi; real oqim PQ-343'dan keyin |
| «Nega FPR 0,10 chegarasi?» | AC-2: cheklangan inspektor resursi; 0,086 tanlangan ish nuqtasida (sweep jadvali) |
| «Model huquqbuzarlikni "aniqlaydimi"?» | Yo'q — «tekshirishga loyiq signal» (anti-mezonlar); qaror insonda (AC-5) |
| «p-hacking bormi?» | Threshold faqat train kvantilidan; alert-rate 0,12 S0'da yozilgan |
| «Nima uchun OCSVM ishlatilmadi?» | Uch baravar sekin va kernel sezgir; nazorat guruhi sifatida baholandi (§8.3) |
