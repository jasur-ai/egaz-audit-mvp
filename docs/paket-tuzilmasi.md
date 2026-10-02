# E-GAZ-AUDIT — kelgan odam shu yerdan boshlaydi

**Loyiha:** Atmosfera tashlamalari hisobotining ishonchini **kirishsiz** (ruxsatsiz, ochiq ma'lumotlar bilan) tekshirish tizimi.
**Muallif:** ⟦F.I.Sh.⟧ · **Sana:** 2026-yil oktabr · **Holat:** ishlaydigan MVP (testlangan, CI yashil)

---

## 1. Bu paketda nima bor (5 daqiqada ko'rish uchun tartib)

| # | Papka / fayl | Nima uchun |
|---|---|---|
| 1 | `MAQOLA/Maqola-1-Nashrga.docx` | Tayyor maqola (xalqaro format, muallif joyi to'ldirilgan holda) |
| 2 | `HUJJATLAR/` | Texnik topshiriq (TZ v1.0) va hisobotlar — nima qilingani ketma-ket |
| 3 | `NATIJALAR/presentation/` | Taqdimot (PPTX, 28 slayd) — 10 daqiqada butun loyiha |
| 4 | `NATIJALAR/web/dashboard.html` | Nashr qilingan boshqaruv paneli (brauzerda ochiladi) |
| 5 | `src/kirishsiz/` | Kod: 15 modul (skrining, o'lchov, huquqiy registr) |
| 6 | `tests/` | 300 test — har bir raqam mashinada tekshiriladi |
| 7 | `data/public/` | 365 kunlik jonli ma'lumot (havo, shamol, harorat) + SHA-256 manifest |

## 2. Nima isbotlangan (qisqa)

- **Muammo real va mavsumiy:** Toshkentda PM2,5 me'yordan oshgan kunlar — isitish mavsumida **21/181**, issiq mavsumda **0/183**.
- **Manba issiqlik elektr stansiyasi emas:** Toshkent lifti **1,67×**, Angren (4 km, ko'mir IES) **0,97× va 0 epizod**.
- **Gaz isitish tushuntirmaydi:** PM2,5 bo'yicha gaz ko'mirga nisbatan ~330× toza; kerakli gaz hajmi milliy iste'moldan oshib ketadi.
- **Izchil tushuntirish:** qattiq yoqilg'i ulushi **~10–25%** + sokin havo (isitish soatlarining 14,8% i 2 m/s dan past).
- **Huquqiy zamin:** har bir loyiha elementi kamida 2 rasmiy hujjat bilan bog'langan — **21 hujjat × 22 element = 53 bog'lanish** (`HUJJATLAR/21-QONUNIY-ASOS-XARITASI.md`).

## 3. Kodni ishga tushirish (5 buyruq)

```bash
cd Loyiha-1-E-GAZ-AUDIT
pip install -r requirements.txt
python3 scripts/run_all.py               # modelni qayta o'qitadi (28 s, birinchi marta)
python3 -m pytest -q                     # 300 test o'tadi
python3 scripts/kirishsiz.py mavsum --fayl data/public/aq_365kun.csv \
        --shamol-fayl data/public/wind_era5_365kun.csv --havo-fayl data/public/havo_era5_365kun.csv
python3 scripts/kirishsiz.py huquqiy --tekshir     # huquqiy registr holati: ok
```

Python 3.11+ kerak. Ma'lumot allaqachon paketda — internet talab qilinmaydi.

## 4. Paketda nima **yo'q** (halol ro'yxat)

- **`models/if_v1.joblib`** (26 MB) — o'qitilgan model; hajm uchun kiritilmagan. **Bir buyruq bilan qayta yasaladi (28 soniya):** `python3 scripts/run_all.py`. Model yo'qligida testlardan biri o'tkazib yuboriladi (299 passed, 1 skipped); model yasalgach — **300 passed**.
- **Rasmiy javoblar** — 4 so'rov 05.10.2026 da yuboriladi, muddat 20.10.
- **Birlamchi o'lchovlar** — loyiha ochiq ma'lumot va modelga tayanadi; xususiy o'lchov asboblari TZ-1 pilotida (T1–T7).

## 5. Qayerdan boshlash kerak (rollar bo'yicha)

- **Rahbar / qaror qabul qiluvchi:** `HUJJATLAR/22-RAHBARIYAT-PAKETI.md` (1 betlik xulosa + qaror loyihasi + kafolat mexanizmi).
- **Texnik mutaxassis:** `HUJJATLAR/15-A-QATLAM-HISOBOTI.md` → `NATIJALAR/reports/eval_report.md` → `src/`.
- **Ilmiy rahbar / taqrizchi:** `MAQOLA/` → `HUJJATLAR/19-MAISHIY-ISITISH.md` → `tests/`.
- **Jurnalist / jamoatchilik:** `NATIJALAR/web/dashboard.html` → `HUJJATLAR/18-ISITISH-MAVSUMI.md`.

## 6. Litsenziya va manbalar

Ma'lumotlar ochiq manbalardan (Open-Meteo/CAMS, ERA5, rasmiy hujjatlar) olingan va SHA-256 bilan qayd etilgan (`data/public/MANIFEST.json`). Har bir raqam yonida manba va sana ko'rsatilgan.
