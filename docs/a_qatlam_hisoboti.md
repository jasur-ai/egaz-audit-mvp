# 15 — A-QATLAM HISOBOTI (kirishsiz rejim) · **v2 — 180 kun, haqiqiy obyektlar**

> **B-qatlam (01.10.2026):** pastdan-yuqoriga mass-balans bajarildi — EF 0,40–1,42 g NOx/kWh, oqim 0,074–0,260 kg/s, model 5,7–11,5 µg/m³ vs kuzatuv +9,24 µg/m³ → nisbat 0,80–1,62 → **mustaqil bahoga sig'adi** (`docs/b_qatlam_mass_balans.md`).

**Davr:** 2026-04-04 → 2026-09-30 (4 320 soat / 180 kun) · **Retseptor:** Toshkent markazi, 41,311°N / 69,240°E
**Hisobot sanasi:** 2026-10-01 · **Yo'llar:** #7 «shamol atributsiyasi» + #6 «ochiq ekran» (`registry.PATHS`)
**Isbot kuchi:** **2** — hududiy skrining; obyekt darajasidagi xulosa uchun ≥3 kuchli ≥2 yo'l kerak

> **Bir jumlada:** 180 kunlik tekshiruvda kunlik norma **hech qachon oshmagan** (0/180), lekin yuqori soatlar
> **shahar shimoli-sharqidagi real manba** yo'nalishida to'planadi: **Toshkent IES** sektorida NO2 **2,30×**,
> PM2,5 **1,86×**. Uzoqdagi sement zavodlari (55–67 km) shahar ekranidan **tashqarida** — ular o'z
> retseptorini talab qiladi. Aynan shu sababli A-qatlam «kim aybdor» demaydi, **«qayerga qarash kerak»** deydi.

**v1 → v2 farqi:** oyna 92 → **180 kun** · «taxminiy» nuqtalar → **rasmiy manbali koordinatalar** (5 obyekt) ·
yangi `facilities` moduli va `nomzodlar` CLI buyrug'i · 20 → **34 yangi test**.

---

## 1. Nima o'zgardi va nima uchun (metodik tuzatish)

v1 da nomzodlar **taxminiy** nuqtalar edi («Sement zavodi: 41.36/69.30»). Bu atributsiya uchun yaroqsiz:
nuqta noto'g'ri bo'lsa, sektor ham noto'g'ri chiqadi. Endi har nomzod **rasmiy manbadan** olingan
koordinata bilan turadi va kod buni **majburiy** qiladi (`facilities.load()` manbasiz yozuvni rad etadi):

| Obyekt | Koordinata (WGS 84) | Manba | Quvvat |
|---|---|---|---|
| **Toshkent IES** | 41,3796 / 69,370217 | GEM — *Tashkent power station* (exact) | 2 230 MVt, gaz |
| Maxam Chirchiq (kimyo) | 41,455790 / 69,576856 | GEM — *Maxam Chirchiq Ammonia Plant* (exact) | ammiak/nitrat |
| Akhangarancement (sement) | 40,931159 / 69,652550 | GEM — *Akhangarantsement Ohangaron* (exact) | 2,18 mln t/yil |
| AGMK Olmaliq (metallurgiya) | 40,857 / 69,528 | Sulphuric-Acid.com (40°51′26″N, 69°31′40″E) | mis/Zn + H₂SO₄ |
| Toshkent Conch (sement) | 40,846490 / 69,745487 | GEM — *Tashkent Conch Cement Plant* (exact) | 6 300 t/kun |

**Birinchi muhim natija — masofa:** retseptordan faqat **Toshkent IES** 30 km radiusda (13,3 km).
Qolganlari 32–67 km — shahar havosi ekranida ular **hisobga olinmaydi** (model hujayrasi 10–25 km).

---

## 2. Daraja ko'rsatkichlari (180 kun)

| Ko'rsatkich | Qiymat |
|---|---|
| Kunlik norma oshgan kunlar (PM2,5 35 µg/m³) | **0 / 180** · eng yuqori kunlik **26,82** |
| Soatlar > 25 µg/m³ | **233** (5,4%) |
| Soatlar > 35 µg/m³ | **8** (0,2%) · barchasida shamol ma'lumoti bor |
| PM2,5: o'rt / P90 / P95 / maks | 13,79 / 22,40 / 25,30 / **37,40** µg/m³ |
| PM10: o'rt / P90 / P95 / maks | 21,38 / 39,20 / 49,40 / **89,90** |
| NO2: o'rt / P90 / maks | 12,54 / 27,10 / **47,70** |
| SO2: o'rt / maks | 4,35 / **11,80** |

**Oylik PM2,5 o'rtachasi:** aprel 12,62 · may 13,66 · **iyun 16,60 (eng yuqori)** · iyul 14,03 ·
avgust 12,03 · sentabr 13,77 µg/m³. Iyun cho'qqisi — issiq davr (fotokimyoviy hosil + chang),
isitish mavsumi emas. Bu **kutilmagan natija** va u keyingi oynani (oktabr–fevral) talab qiladi.

---

## 3. Yo'nalish tahlili — haqiqiy obyektlar bo'yicha (yangi)

| Obyekt | Masofa | PM2,5 | NO2 | SO2 | PM10 |
|---|---|---|---|---|---|
| **Toshkent IES** | **13,3 km** | **1,86** ✱ | **2,30** ✱ | 1,19 ~ | 0,77 |
| Maxam Chirchiq | 32,4 km | 1,88 ✱ | 2,43 ✱ | 1,03 | 0,68 |
| Akhangarancement | 54,6 km | 1,15 ~ | 1,59 ✱ | 0,62 | 1,01 |
| AGMK Olmaliq | 56,0 km | 0,96 | 1,26 ~ | 0,65 | 1,18 |
| Toshkent Conch | 66,8 km | 1,15 ~ | 1,59 ✱ | 0,62 | 1,01 |

✱ lift ≥ 1,5 (signal) · ~ 1,15–1,5 (kuchsiz) · bo'sh — signal yo'q

**Shamollanish guli (ERA5, n=4 320):** NW 16% · SE 15% · W 14%.

### 3.1. Nima ko'rinadi

1. **Yonish belgilari (NO2) shimoli-sharqda to'plangan** — IES sektorida fon ulushi 18,4% → yuqori soatlarda **42,2%**.
2. **SO2 signal bermayapti** (IES 1,19 · boshqalar ≤1,03) — bu gaz yoqilg'isi bilan mos keladi
   (SO2 asosan ko'mir/mazutdan chiqadi). Ya'ni natija **kutilgan yo'nalishda**, sun'iy emas.
3. **PM10 hech qayerda boyitilmagan** (IES 0,77; AGMK 1,18) — chang asosan **shahar va regional** fon
   (yo'l, qurilish, cho'l), ma'lum bir obyektga bog'lanmagan.

### 3.2. Nima ajratilmaydi (halol chegara)

| Yo'nalish | Guruh | Muammo |
|---|---|---|
| **57,5°** | Toshkent IES **+** Maxam Chirchiq | 54,9° va 60,1° — bir xil yo'nalish; shamol **ajratmaydi** |
| **145,2°** | Akhangarancement **+** AGMK **+** Toshkent Conch | 140–154° — uzoq janubi-sharq guruhi |

Ya'ni «NO2 ni aynan IES chiqaryapti» deyish mumkin emas: **Chirchiq klasteri ham** o'sha yo'nalishda.
Ajratish uchun yonish-kanal usuli (orbita, yo'l #3) yoki rasmiy o'lchovlar kerak — B qatlam ishi.

---

## 4. Nazorat tekshiruvi (o'zgarmadi)

CAMS model hujayrasi shahar stansiyalaridan **past** ko'rsatadi: 180-kunlik o'rtacha 13,79 µg/m³,
holbuki 2024-yil stansiya asosida Toshkent bo'yicha yillik o'rtacha **38,8 µg/m³** (WB/kun.uz, 09.10.2024).
**Xulosa:** modeldan faqat **nisbiy/yo'nalish** signali olinadi; mutlaq «norma oshdi/oshdi» xulosasi
faqat rasmiy stansiya ma'lumoti bilan qilinadi. Modelning past baholashi bizning 0/180 natijasini ham
**ehtiyotkorlik bilan** o'qishni talab qiladi.

---

## 5. Nima isbotlanadi / nima isbotlanmaydi

| Da'vo | Holat |
|---|---|
| Model bo'yicha kunlik norma oshmagan (180 kun) | ✅ aytiladi — lekin model past baholaydi (§4) |
| Yuqori NO2/PM2,5 soatlari shimoli-sharqiy sektorga bog'langan | ✅ skrining signali (lift 1,9–2,3) |
| Bunda gaz yoqilg'isiga xos manzara (SO2 past) ko'rinadi | ✅ kuzatuv, tasdiq emas |
| Sabab aynan **Toshkent IES** | ❌ ajratilmaydi (Chirchiq klasteri bir yo'nalishda) |
| Qaysi korxona aybdor / huquqbuzarlik | ❌ A-qatlam hech qachon buni aytmaydi |

---

## 6. Rasmiy talablar holati (yo'l #1, isbot kuchi 5)

| # | Tashkilot | Tur | Javob muddati | Eskalatsiya |
|---|---|---|---|---|
| 1 | Ekologiya, atrof-muhitni muhofaza qilish va iqlim o'zgarishi vazirligi | o'lchovlar | **2026-10-17** | 2026-10-22 |
| 2 | Toshkent shahar ekologiya boshqarmasi | monitoring | **2026-10-17** | 2026-10-22 |
| 3 | Gidrometeorologiya xizmati agentligi (Hydromet) | inspeksiya | **2026-10-17** | 2026-10-22 |

Asos: Konstitutsiya 49-modda · Aarhus 4-modda (kuchda **25.08.2025**) · 15 kun muddati.
⚠ Yuborishdan oldin tashkilot nomlari/manzillari va imzo `⟦…⟧` maydonlari tasdiqlanadi.

---

## 7. Kod, CLI va testlar (nima yangi qo'shildi)

| Fayl | Nima |
|---|---|
| `src/kirishsiz/facilities.py` | Haqiqiy obyektlar reyestri: majburiy maydonlar tekshiruvi, masofa/azimut, radius filtri, **yo'nalish guruhlari** (ajratilmaydigan holat) |
| `data/public/nomzodlar_uz.json` | 5 obyekt — koordinata + quvvat + **manba URL + sana + tier** |
| `scripts/kirishsiz.py nomzodlar` | Reyestr jadvali (azimut, masofa, radius holati) |
| `scripts/kirishsiz.py sektor --haqiqiy` | Har bir haqiqiy obyekt sektori bo'yicha lift jadvali + ajratilmaydigan guruhlar |
| `tests/test_kirishsiz_facilities.py` | 14 test: format qat'iyligi, chegara tekshiruvi, masofa/azimut, radius, guruhlar |
| `tests/test_kirishsiz_sector.py` | 20 test (v1 dan) |

```bash
cd 01-Loyiha1-Carbon-Emission/MVP
python3 scripts/kirishsiz.py nomzodlar --radius 100
python3 scripts/kirishsiz.py sektor --haqiqiy --radius 100 --modda pm2_5,no2,so2 \
        --fayl data/public/aq_180kun.csv --shamol-fayl data/public/wind_era5_180kun.csv
python3 scripts/kirishsiz.py ekran --kun 180 --shamol-fayl data/public/wind_era5_180kun.csv \
        --obyekt "Toshkent IES:41.3796:69.370217"
```

**Testlar:** L1 jami **175** (kirishsiz paketi: 71 + 14 = 85).

---

## 8. Ma'lumot va provenans

| Fayl | Manba | Qatorlar | SHA-256 (qisqa) | Litsenziya |
|---|---|---|---|---|
| `aq_180kun.csv` | Open-Meteo Air Quality (CAMS) | 4 320 | `366c0c552563…` | CC-BY-4.0 |
| `wind_era5_180kun.csv` | Open-Meteo Archive (ERA5) | 4 344 | `34feadfcc540…` | CC-BY-4.0 |
| `aq_92kun.csv` / `wind_era5_92kun.csv` | v1 (solishtirish uchun saqlanadi) | 2 208 | `abf15b74…` / `0790afd4…` | CC-BY-4.0 |
| `nomzodlar_uz.json` | GEM · Eurocement · Sulphuric-Acid.com · UzDaily | 5 obyekt | — (matn) | manba ko'rsatilgan |

---

## 9. Keyingi qadamlar (B qatlam)

| # | Qadam | Muddat | Natija |
|---|---|---|---|
| 1 | Talablarni yuborish (3 tashkilot) va muddatni yuritish | 02–05.10 | Rasmiy hujjat (kuch 5) |
| 2 | IES va Maxam **yonish** manbalarini ajratish: orbita (TROPOMI NO2) oynasi | 05–15.10 | Yo'l #3 ishga tushadi |
| 3 | Oynani isitish mavsumiga uzaytirish (oktabr–fevral) | 10.10 dan | Mavsumiy tasdiq; IES yuklamasi oshadi |
| 4 | FIRMS MAP_KEY → IES/Chirchiq hududida yonish nuqtalari | 10–15.10 | Yo'l #4 |
| 5 | Pastdan-yuqoriga oraliq: IES yoqilg'i × ELV (yo'l #2) | 15–25.10 | Hisobot mustaqil bahoga sig'adimi |
| 6 | Yangi retseptorlar: Angren/Ohangaron (sement zavodlari zonasi) | 25–31.10 | Uzoq manbalar uchun alohida ekran |

---

## 10. Xatarlar (yangilangan)

| Xatar | Baho | Chora |
|---|---|---|
| IES ↔ Chirchiq klasteri ajratilmaydi | **Yuqori** (tasdiqlandi) | Orbita + rasmiy o'lchovlar; ikkalasini birga tekshirish |
| Model past baholaydi (CAMS ↔ stansiya farqi) | Yuqori | Nisbiy xulosa; rasmiy javob kutiladi |
| Isitish mavsumi hali oynaga kirmagan | O'rta | 10.10 dan oyna uzaytiriladi |
| Nomzod reyestri to'liq emas (kichik manbalar yo'q) | O'rta | Reestr kengaytiriladi (masalan, kogeneratsiya stansiyalari — 203 MVt, 7 tuman) |
| Uzoq manbalar (55–67 km) shahar ekranida ko'rinmaydi | O'rta | Alohida retseptor (§9, 6-qadam) |

---

## 11. Manbalar (sana + tier)

| # | Manba | Nima uchun | Sana | Tier |
|---|---|---|---|---|
| 1 | [GEM — Tashkent power station](https://www.gem.wiki/Tashkent_power_station) | IES koordinatasi (exact) + bloklar | 2026-09-22 | B |
| 2 | [JSC «Toshkent IES» rasmiy](https://toshkenties.uz/uz/page/ies-az) | 2 230 MVt o'rnatilgan quvvat | 2021-08-12 | A |
| 3 | [GEM — Maxam Chirchiq Ammonia Plant](https://www.gem.wiki/Maxam_Chirchiq_Ammonia_Plant) | Chirchiq zavodi koordinatasi | 2026-09-11 | B |
| 4 | [GEM — Akhangarantsement](https://www.gem.wiki/Akhangarantsement_OJSC_Ohangaron_Cement_Plant) | Sement zavodi koordinatasi | 2026-07-16 | B |
| 5 | [Eurocement — Akhangarancement](https://www.eurocement.ru/cntnt/eng10/plants2/uzbekistan2/akhangaran1/akhangaran2.html) | 2,18 mln t/yil quvvat | 2019 | B |
| 6 | [GEM — Tashkent Conch Cement Plant](https://www.gem.wiki/Tashkent_Conch_Cement_Plant) | Conch koordinatasi (exact) | 2025-07-15 | B |
| 7 | [UzDaily — 40 sement zavodi](https://www.uzdaily.uz/en/uzbekistan-operates-40-cement-plants-with-a-capacity-of-397-million-tons/) | Viloyatda 4 zavod, 6,5 mln t | 2025-03-08 | B |
| 8 | [Sulphuric-Acid.com — Almalyk MMC](http://www.sulphuric-acid.com/sulphuric-acid-on-the-web/acid%20plants/Almalyk%20MMC.htm) | AGMK koordinatasi (DMS) | 2019 | C |
| 9 | [Open-Meteo Air Quality](https://air-quality-api.open-meteo.com) / [Archive (ERA5)](https://archive-api.open-meteo.com) | 180 kunlik seriya — **jonli olindi** | 2026-10-01 | C/D |
| 10 | SanQvaM 0053-23 | PM2,5 kunlik norma 35 µg/m³ | kuchda | A |
| 11 | [kun.uz/WB — 38,8 µg/m³](https://kun.uz) | Model–stansiya farqi | 2024-10-09 | B |
| 12 | [gazeta.uz — kogeneratsiya 203 MVt](https://www.gazeta.uz/oz/2026/08/13/cogeneration-tashkent/) | Reestrni kengaytirish asosi | 2026-08-13 | A |

---

**Hisobot oxiri (v2).** Kod: `src/kirishsiz/{facilities,sector,screener}.py` · CLI: `scripts/kirishsiz.py nomzodlar|sektor|ekran` ·
Testlar: 34 yangi (jami L1 175) · Hammasi §7 dagi buyruqlar bilan qayta ishlab chiqariladi.
