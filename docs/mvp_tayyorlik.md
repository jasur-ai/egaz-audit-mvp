# MVP tayyorlik hukmi


> # ✅ HA — MVP TAYYOR
> **Ishlaydigan, testlangan, jonli ochiq ma'lumotda ishlaydigan va halol chegaralari yozib qo'yilgan MVP.**
> Qolgan uchta bo'shliq **tashqi** (rasmiy javob, FIRMS kaliti, kimyo modeli) — ular MVP ishlashiga
> to'sqinlik qilmaydi, faqat **aniqlikni** oshiradi.

---

> Manba hujjat: `YAKUNIY/20-MVP-TAYYORLIK.md` · 2026-10-01 · kod: `butun repo` · CLI: `§3 buyruqlar`

---


## 1. Nima «tayyor» degani — o'lchov bilan

| Mezon | Holat | Dalil |
|---|---|---|
| **Ishlaydigan kod** | ✅ | 14 modul (`src/kirishsiz/`), 2 loyiha, CLI 20+ buyruq; har biri **jonli ma'lumotda** ishlatilgan |
| **Testlar** | ✅ | **300** (L1) + **193** (L2) = **493 passed** |
| **CI (mustaqil klon)** | ✅ | L1 `jasur-ai/egaz-audit-mvp` CI **#19 yashil** (115 s), L2 `eco-ledger-mvp` CI #16 yashil |
| **Jonli ma'lumot** | ✅ | 30+ fayl SHA-256 bilan (MANIFEST); **8 760 soat** × 4 retseptor, bo'sh qiymat **0** |
| **Qayta ishlab chiqarish** | ✅ | har raqam bitta CLI buyrug'i bilan takrorlanadi (quyida §3) |
| **Deploy** | ✅ | `https://egaz-audit.pages.dev/` **200** · API `:8000` **200** · bot `@ecoledg_bot` jonli |
| **Hujjat** | ✅ | TZ-1 v1.0 + ilovalar **K.1–K.10**, `YAKUNIY/` **1–20**, vault nusxalari |
| **Rasmiy so'rovlar** | ✅ tayyor | 4 xat, muddat **20.10**, eskalatsiya **25.10**, kuzatuv jurnali jonli |
| **Halol chegara** | ✅ | har bo'limda «isbotlanmaydi» ro'yxati (masalan §4) |

---

## 2. MVP nima qiladi (uch qatlam)

**A-qatlam — skrining (asosiy mahsulot):** hisobotdagi raqam ishonchli emasligini **kirishsiz** (ruxsatsiz)
ko'rsatadi: Benford/dumaloq skrining, sektor profillari, mass-balans, sun'iy yo'ldosh oqimi — 8 yo'l.
Hozirgi asosiy dalil: **21/181 ↔ 0/183** kun, **IES lifti 1,21 ↔ 1,20**, **Angren 0,97× va 0 epizod**.

**B-qatlam — miqdoriy tushuntirish:** EF zanjiri (EMEP/EEA 2023 ↔ AP-42 §1.4 kelishuvi **1,5%**),
quti modeli, epizod atributsiyasi, maishiy isitish bahosi (**qattiq yoqilg'i ulushi 10–25%**).

**Huquqiy yo'l:** 4 rasmiy talab (Aarhus 4-modda) — ma'lumotni ochish; javob/rad etish/jimlik —
uchalasi ham keyingi qadam uchun hujjat.

---

## 3. Reproduksiya — to'rtta buyruq

```bash
cd 01-Loyiha1-Carbon-Emission/MVP
python3 scripts/kirishsiz.py mavsum  --fayl data/public/aq_365kun.csv \
       --shamol-fayl data/public/wind_era5_365kun.csv --havo-fayl data/public/havo_era5_365kun.csv
python3 scripts/kirishsiz.py taqqos --retseptor "Toshkent:data/public/aq_365kun.csv:data/public/wind_era5_365kun.csv:data/public/havo_era5_365kun.csv" \
       --retseptor "Angren:data/public/aq_Angren_365kun.csv:data/public/wind_Angren_365kun.csv:data/public/havo_Angren_365kun.csv"
python3 scripts/kirishsiz.py isitish --aq-fayl data/public/aq_365kun.csv \
       --shamol-fayl data/public/wind_era5_365kun.csv --havo-fayl data/public/havo_era5_365kun.csv
python3 scripts/build_requests_2026_10.py --dry-run      # so'rovlar to'plami
```

---

## 4. Nima hali **yo'q** (halol ro'yxat)

| Bo'shliq | Nega muhim | Qachon yopiladi |
|---|---|---|
| **Rasmiy ma'lumot** | qattiq yoqilg'i ulushi **10–25%** bahosi hali tasdiqlanmagan | javob muddati **20.10** (eskalatsiya 25.10) |
| **FIRMS MAP_KEY** | termal anomaliya (yonish o'choqlari) tasdiqlovchi mustaqil kanal | kalit olinishi bilan |
| **EMEP 1.A.4 PDF** | EF qiymatlari qidiruv indeksidan olindi (EEA sayti vaqtincha ishlamaydi) | EEA tiklanganda to'g'ridan qayta olinadi; AP-42 §1.4 zaxira solishtiruv berdi |
| **Ikkilamchi aerozol** | NOx/SO2 → nitrat/sulfat ulushi ajratilmagan ⇒ 15,2% **yuqori baho** | kimyo modeli yoki PM2,5 tarkibi o'lchovi |
| **O'z o'lchov asbobi** | hozir hammasi ochiq ma'lumot + model (in-situ emas) | **TZ-1 pilot** (shovqin) — T1 paketi tayyor, juftlik ko'rigi 10.10 |
| **Uy xo'jaligi soni (rasmiy)** | Toshkent bo'yicha aniq uy soni e'lon qilinmagan → 3,8 kishi konvensiyasi | statistika qo'mitasi javobi |

---

## 5. Imkoniyatdan kelib chiqqan yakuniy hukm

Bugungi holatda **ishonch bilan aytish mumkin:**

1. Qishki PM2,5 muammosi **real** va **faqat isitish mavsumiga xos** (21/181 ↔ 0/183).
2. Muammo **IES sektoridan emas** — ikki mustaqil dalil: lift barqarorligi (1,21 ↔ 1,20) va
   Angren nazorati (4 km, 2 533 soat isitish, lift 0,97×, 0 epizod).
3. Ortishni **gaz isitish tushuntira olmaydi** (330× EF farqi; 37,5 mlrd m³ absurdligi).
4. Yagona izchil tushuntirish — **qattiq yoqilg'i ulushi ~10–25%** + sokin havo (14,8% soat < 2 m/s).
5. Eng og'ir kunlar **mintaqaviy** (Toshkent ↔ Ohangaron r = 0,816), mahalliy zavod emas.

**MVP — tayyor.** Bu «hammasi isbotlandi» degani emas: bu **ishlaydigan, takrorlanadigan va
chegarasi aniq** asbob degani. Keyingi haqiqiy sakrash 20.10 dan keyin — rasmiy raqamlar kelganda
«qattiq yoqilg'i ulushi» bahosi **tasdiqlanadi yoki rad etiladi** va model o'shanda miqdoriy
jihatdan yopiladi.
