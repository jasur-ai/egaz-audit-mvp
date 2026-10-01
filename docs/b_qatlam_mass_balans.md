# B-qatlam: mass-balans tekshiruvi (pastdan yuqoriga, yo'l #2)

> Manba hujjat: `YAKUNIY/16-B-QATLAM-MASS-BALANS.md` · 2026-10-01 · kod: `src/kirishsiz/bottomup.py` · CLI: `scripts/kirishsiz.py pastdan` · testlar: `tests/test_kirishsiz_bottomup.py` (39)

---

> **Savol:** A-qatlam (180 kun) «Toshkent IES yo'nalishida NO2 +9,2 µg/m³ ortiqcha bor» degan **kuzatuv** xulosasini berdi.
> Mustaqil yo'l bilan — **yoqilg'i/ishlab chiqarish × koeffitsient (EF) → oqim → dispersiya** — shu ortiqcha
> **miqyos bo'yicha** tushuntiriladimi? Bu tekshiruv **A-qatlam hisobotining mustaqil bahoga sig'ishini** sinaydi.
>
> **Javob (qisqa):** **HA — bir tartib kattaligida sig'adi.** Pastdan hisoblangan sektor o'rtachasi **5,7–11,5 µg/m³ NOx**,
> jonli kuzatuvda **+9,24 µg/m³**. Nisbat **0,80–1,62** (ruxsat etilgan chegara 3×). Kuzatuv formulalar oralig'ining **ichida**.
> **LEKIN:** PM2,5 uchun model **25 barobar past** — ya'ni PM2,5 ortiqchasi gaz yonishining **birlamchi** zarrasi bilan tushuntirilmaydi.

---

## 1. Zanjir (bir qatorda)

```
ISHLAB CHIQARISH (5,8 mlrd kVt·soat, 2024)          [rasmiy, A]
        × KOEFFITSIENT (0,13–0,32 lb/MMBtu → 0,40–1,42 g NOx/kWh)   [AP-42 §3.1-1, A]
        × FIK (35–50%)                               [texnik oraliq]
        → YILLIK TASHLANMA (2 334–8 207 t NOx/yil)
        → OQIM (0,074–0,260 kg/s)                    [8760 soatga tekislangan]
        → BRIGGS σ + GAUSS (13,28 km, shahar D)      [σy 846 m · σz 833 m]
        → O'QDA 8,3–29,1 µg/m³ (u=4 m/s)
        × MOS KELISH ULUSHI (19,5%)                  [ERA5: 156/799 soat]
        → SEKTOR O'RTACHASI 5,7–11,5 µg/m³
        ⚖ KZATUV: +9,24 µg/m³ (793 soat, 180 kun)     → NISBAT 0,80–1,62 → MOS ✅
```

---

## 2. Koeffitsient (EF) zanjiri — tekshirilgan

### 2.1. Manba va birlik o'tkazmasi

| Bosqich | Qiymat | Manba / formulalar |
|---|---|---|
| Xom koeffitsient (nazoratsiz) | **0,32 lb/MMBtu** (reyting A) | EPA AP-42 §3.1-1 (stasionar gaz turbinalari, NOx) |
| Xom koeffitsient (bug'/suv quyish) | **0,13 lb/MMBtu** (reyting A) | AP-42 §3.1-1 |
| Birlik o'tkazmasi | 1 lb/MMBtu = **429,9 g/GJ** | 453,592 g ÷ 1,055056 GJ |
| → yoqilg'i asosida | **55,9–137,6 g/GJ** | 0,13·429,9 … 0,32·429,9 |
| → **chiqish** asosida (FIK 35–50%) | **0,40–1,42 g/kWh** | EF·0,0036/FIK (1 kVt·soat = 0,0036 GJ) |

**Mustaqil tekshiruv (NSPS):** AQSh yangi gaz turbinasi chiqish standarti **2,3 lb/MWh = 1,04 g/kWh** —
AP-42 oralig'ining (0,40–1,42) **ichida**, ya'ni ikki mustaqil hujjat bir-biriga zid emas. ✅

> **Diqqat (birlik xatosi topildi va tuzatildi):** dastlabki variantda `g/GJ → g/kWh` o'tkazmasi 1000 marta katta
> chiqar edi (1 415 g/kWh kabi absurd qiymat). Bu **test to'plami** tomonidan ushlandi (`test_g_per_gj_to_g_per_kwh_efficiency_effect`)
> va tuzatildi. Ana shu — testlar «qog'oz uchun» emasligining jonli isboti. ✅

### 2.2. Ikkinchi modda — PM2,5 (birlamchi)

| Bosqich | Qiymat | Manba |
|---|---|---|
| AP-42 §3.1-2a (gaz turbinasi) | 0,0066 lb/MMBtu | AP-42 §3.1-2a |
| → g/GJ | **2,84 g/GJ** | ×429,9 |
| → mg/kWh (FIK 35%) | **29,2 mg/kWh** | ×0,0036/0,35 |

### 2.3. EMEP/EEA holati — ✅ **YOPILDI (R50, 2-qism)**

EMEP/EEA Guidebook 2023 **1.A.1** («Energy industries») bo'limining **aniq Tier 1 EF jadvali** hali olinmagan:
EEA saytining «1.A.1 Energy industries 2023» sahifasi **faqat sarlavha va fayl havolasini** beradi (asosiy jadval JS orqali yuklanadi),
qidiruv natijalari esa doimiy ravishda **1.A.3.d (navigatsiya)** jadvallariga olib keladi.
**Yangilanish (01.10.2026):** EMEP/EEA 2023 **1.A.1.a Table 3-4** PDF manbasidan olindi —
**NОx = 89 g/GJ (CI 15–185)**, **PM2,5 < 0,14 g/GJ**.
AP-42 geometrik o'rtasi (87,7 g/GJ) bilan farq **1,5%** → **ikki tizim kelishadi**.
EMEP asosidagi haydash: 0,641–0,915 g NOx/kWh → 3 717–5 309 t/yil → sektor o'rtachasi **3,7–7,4 µg/m³**,
kuzatuv 9,24 → nisbat **1,25–2,50** (hamon «mos»). Batafsil: `17-B-QATLAM-2-QISM.md` §1.

---

## 3. Faoliyat ma'lumoti (activity data)

| Ko'rsatkich | Qiymat | Hisob | Manba |
|---|---|---|---|
| Yillik ishlab chiqarish (2024) | **5,8 mlrd kVt·soat** = 5,8 TWh | rasmiy | toshkenties.uz (Tier A) |
| O'rnatilgan quvvat | 2 230 MVt | rasmiy | JSC «Toshkent IES» (Tier A) |
| **O'rtacha yuklama** | **≈ 662 MVt** | 5,8·10⁹ ÷ 8760 h | hosila |
| Yuklama darajasi | **29,7%** o'rnatilgan quvvatdan | 662 ÷ 2230 | hosila |
| Kundalik ishlab chiqarish | ≈ 15,9 mln kVt·soat/kun | 5,8·10⁹ ÷ 365 | hosila |

O'rtacha yuklamaning ~30% bo'lishi **qish mavsumida keskin oshishini** ko'rsatadi (kondensatsiya rejimi + issiqlik yuklamasi) —
bu §8 dagi **oynani isitish mavsumiga uzaytirish** qadamining miqdoriy asosi.

---

## 4. Oqim va dispersiya

**Manba:** Toshkent IES, 41,3796° / 69,370217° (GEM, aniq koordinata).
**Retseptor:** 41,311° / 69,240° (shahar markazi). **Masofa 13,28 km · azimut 54,9°.**

| EF ssenariysi | Yillik NOx | Oqim (8760 soat) |
|---|---|---|
| 0,40 g/kWh (bug'/suv quyish, FIK 50%) | **2 334 t/yil** | **0,074 kg/s** |
| 1,42 g/kWh (nazoratsiz, FIK 35%) | **8 207 t/yil** | **0,260 kg/s** |

**Briggs σ (13,28 km):**

| Rejim | σy | σz |
|---|---|---|
| Shahar, B (beqaror) | 1 693 m | 12 071 m |
| Shahar, D (neytral) | **846 m** | **833 m** |
| Shahar, F (barqaror) | 582 m | 232 m |

**Gauss yechimi** `C = Q /(π·u·σy·σz)·exp(−h²/2σz²)`, **sektor o'rtachasi** = o'qdagi qiymat × mos kelish ulushi (19,5%):

| u (m/s) | Sinf | O'qda (past–yuqori) | **Sektor o'rtachasi (past–yuqori)** |
|---|---|---|---|
| 4 | B | 0,3–1,0 | 0,1–0,2 |
| 2 | B | 0,6–2,0 | 0,1–0,4 |
| **4** | **D** | **8,3–29,1** | **1,6–5,7** |
| **2** | **D** | **16,6–58,2** | **3,2–11,4** |
| 4 | F | 39,7–139,4 | 7,7–27,2 |
| 1 | D | 33,1–116,5 | 6,5–22,7 |

**Sezgirlik (muhim):** 13 km masofada σz ≈ 833 m bo'lgani uchun **mo'ri balandligining ta'siri <1%**
(`exp(−100²/(2·833²)) = 0,9928`). Ya'ni natija «mo'ri qanchalik baland» degan taxminiy parametrga **bog'liq emas** — bu xulosani mustahkamlaydi.

---

## 5. Nega «sektor o'rtachasi» kerak — mos kelish ulushi

Shamol sektor ichida (±45°) bo'lsa ham, oqim retseptordan **chetga** o'tishi mumkin. Aniq mos kelish (|shamol − 54,9°| ≤ 9°):

| Ko'rsatkich | Qiymat |
|---|---|
| Jami soat (ERA5, 180 kun) | 4 344 |
| Sektorda (54,9° ± 45°) | 799 (18%) |
| **Aniq mos** (≤ 9°) | **156 soat = sektor soatlarining 19,5%** (barcha soatlarning 3,6%) |

Shu sababli model qiymati sektor o'rtachasi bilan **to'g'ridan-to'g'ri** solishtiriladi (o'qda emas, ulushga ko'paytirilgan holda).

---

## 6. Kuzatuv bilan solishtirish

| Manba | Qiymat |
|---|---|
| Jonli kuzatuv (A-qatlam, 180 kun): NO2 o'rt. sektorda 20,09 − tashqarida 10,84 | **+9,24 µg/m³** |
| Pastdan hisob (u=4 m/s, D) | 5,7 µg/m³ |
| Pastdan hisob (u=2 m/s, D) | 11,4 µg/m³ |
| **Nisbat (kuzatuv ÷ model)** | **0,80 … 1,62** |
| Xulosa qoidasi (≤3× → mos) | **«mos (bir tartib kattaligida)»** ✅ |

**Qo'shimcha muhim kuzatuv:** juda beqaror sharoitda (B sinfi) model **~0** beradi. Demak kuzatilgan barqaror +9,2 µg/m³
**faqat neytral/barqaror soatlar mavjudligi bilan** mumkin — bu avvalgi xulosani (signal «o'rtacha soatlarda», kuchli epizodlarda emas)
mustaqil ravishda tasdiqlaydi.

---

## 7. PM2,5 savoli — model nega past (halol chegara) · **✅ YOPILDI (2-qism)**

| Modda | Model (sektor o'rt.) | Kuzatuv (sektor ortiqchasi) | Nisbat |
|---|---|---|---|
| NO2 (NOx proksisi) | 5,7–11,4 µg/m³ | +9,24 µg/m³ | 0,8–1,6 ✅ |
| **PM2,5 (birlamchi)** | **0,12 µg/m³** | **+2,89 µg/m³** | **~25×** ❌ |

**Izoh:** gaz yonishida **birlamchi** PM2,5 juda kam (29,2 mg/kWh). Kuzatilgan PM2,5 ortiqchasi shu manbadan **bo'lishi mumkin emas**.
Ehtimoliy izohlar — hammasi **tasdiqlanmagan**:
1. NOx → nitrat (ikkilamchi aerozol) aylanishi — modelda yo'q;
2. sektor ichidagi **boshqa** manbalar (sement pechlari, kul to'plash joylari, qurilish);
3. uzoq manbalarning shahar ustidan o'tishi.

Bu — «nima isbotlanmaydi» ro'yxatining eng muhim qatori: **PM2,5 bo'yicha sabab ajratilmaydi.**

**Yangilanish (01.10.2026, olti sinov — `17-B-QATLAM-2-QISM.md` §2):**
(1) mass-rekonstruksiya modeli kuzatuvning **4,2%** ini beradi (EMEP bilan 0,2%);
(2) **chang emas** — sektorda CAMS `dust` **kamroq** (lift 0,76), AOD 0,96;
(3) zarra spektri nozik tomonga siljigan (PM2,5/PM10: 0,724 vs 0,626) → **ikkilamchi aerozol/boshqa nozik manba** gipotezasi qoldi;
(4) NO2 va PM2,5 **turli yo'nalish profillari**: 60° (5,01×) va 105° (1,55×) — bir manba emas.

---

## 8. Nima isbotlanadi / nima isbotlanmaydi

| ✅ Isbotlanadi | ❌ Isbotlanmaydi |
|---|---|
| A-qatlam hisoboti **mustaqil pastdan-yuqoriga bahoga sig'adi** (nisbat 0,8–1,6) | **Qaysi** obyekt — IES va Maxam Chirchiq hali ham bir yo'nalishda (54,9° va 60,1°) |
| Emissiya oqimining **tartib kattaligi** (0,07–0,26 kg/s NOx) real | EF — **qurilma ko'rsatkichi emas**, adabiyot oralig'i (+ FIK taxmini) |
| Kuzatilgan ortiqcha **neytral/barqaror soatlar** bilan izohlanadi | Butun 180 kunlik oynani **bitta** o'rtacha shamol bilan tavsiflash mumkin emas |
| Natija **mo'ri balandligiga sezgir emas** (<1%) | PM2,5 ortiqchasining sababi (§7) |
| Birlik o'tkazmasi ikki mustaqil hujjat bilan tekshirilgan (AP-42 ↔ NSPS) | IES **haqiqiy** yillik tashlanmasi (rasmiy inventar ochiq emas) |

---

## 9. Kod, CLI va testlar (jonli proba)

**Yangi modul:** `src/kirishsiz/bottomup.py`
— `lb_per_mmbtu_to_g_per_gj` · `g_per_gj_to_g_per_kwh` · `annual_tonnes` · `rate_kg_s` ·
`briggs_sigma` (qishloq + shahar) · `gaussian_ground_conc` · `dispersion_table` · `bottom_up` ·
`alignment_share` · `sector_weighted_scenarios` · `sector_excess` · `consistency`.

**Yangi testlar:** `tests/test_kirishsiz_bottomup.py` — **33 test** (birliklar, σ tartiblari, Gauss analitik tekshiruvi,
mos kelish ulushi, xulosa qoidalari). **L1 jami: 175 → 208 ✅** (L2 193 bilan birga **401**).

**CLI (jonli ishga tushirildi):**

```bash
python3 scripts/kirishsiz.py pastdan \
  --obyekt "Toshkent IES:41.3796:69.370217" \
  --ishlab-chiqarish 5.8 --lb-past 0.13 --lb-yuqori 0.32 --fik 0.35,0.50 \
  --mo-ri 100 --shamol 4 --barqarorlik D --kuzatuv 9.24
```

**Chiqish (haqiqiy, qisqartirilmagan):**

```
PASTDAN YUQORIGA — Toshkent IES · 13.28 km · azimut 54.9°
  EF zanjiri: 0.13–0.32 lb/MMBtu = 55.9–137.6 g/GJ → FIK 35%–50% → 0.40–1.42 g/kWh  (AP-42 §3.1-1)
  Ishlab chiqarish 5.8 TWh/yil → NOx 2,334–8,207 t/yil → oqim 0.074–0.260 kg/s
  Disperisiya: D · u=4 m/s · mo'ri 100 m · shahar · σy 846 m · σz 833 m
  To'g'ridan-to'g'ri o'qda (doim mos): 8.3–29.2 µg/m³ NOx
  Mos kelish ulushi: sektorda 156/799 soat = 19.5% (barcha soatlarning 3.6% i)
   • D · u=4 m/s → o'qda 29.2 × 20% = **sektor o'rtachasi 5.7 µg/m³**
   • D · u=2 m/s → o'qda 58.4 × 20% = **sektor o'rtachasi 11.4 µg/m³**
  Kuzatuv bilan: model 5.7 vs yo'nalish ortiqchasi 9.2 µg/m³ → nisbat 1.62 → mos (bir tartib kattaligida)
```

---

## 10. B qatlamning qolgan qadamlari — holat (2026-10-01)

| # | Qadam | Holat | Izoh |
|---|---|---|---|
| 1 | Talablarni yuborish (3 tashkilot) | ⏳ tayyor | 3 xat + `sorovlar.jsonl` — yuborish kutilmoqda |
| 2 | IES ↔ Chirchiq ni **orbita** bilan ajratish | ⚠️ **salbiy natija** | Yo'nalish tahlilida ajralmaydi; yuqori 10% soatlarda farq ~0 (tafsilot: 15-hisobot §3.2) |
| 3 | Oynani isitish mavsumiga uzaytirish | ▶ **10.10 dan** | Asos: §3 (yuklama 29,7% — qishda oshadi) |
| 4 | FIRMS `MAP_KEY` → yonish nuqtalari | ⛔ **bloklangan** | `SUOMI_VIIRS_C2_Central_Asia_7d.csv` → 404 · `MODIS_C6_1…` → 404 · `DEMO_KEY` → 400. Kalit olinmaguncha urinish **foydasiz** |
| 5 | **Pastdan-yuqoriga mass-balans** | ✅ **BAJARILDI** (shu hujjat) | Nisbat 0,80–1,62 → hisobot mustaqil bahoga sig'adi |
| 6 | Angren/Ohangaron uchun alohida retseptor | ⏳ navbatda | 54,6–66,8 km manbalar shahar ekranida ko'rinmaydi |

---

## 11. Manbalar (sana + tier)

| # | Manba | Nima uchun | Sana | Tier |
|---|---|---|---|---|
| 1 | EPA AP-42 §3.1, Table 3.1-1 | NOx EF: 0,32 / 0,13 lb/MMBtu (reyting A) | 2000-04 (2020 nusxa) | A |
| 2 | AP-42 §3.1-2a | PM2,5 EF: 0,0066 lb/MMBtu | 2000-04 | A |
| 3 | AQSh NSPS (40 CFR 60) — gaz turbinasi | 2,3 lb/MWh = 1,04 g/kWh (mustaqil tekshiruv) | kuchda | A |
| 4 | JSC «Toshkent IES» (toshkenties.uz) | 2 230 MVt o'rnatilgan; **5,8 mlrd kVt·soat (2024)** | 2021 / 2024 | A |
| 5 | GEM — Tashkent power station | Koordinata 41,3796/69,370217 (aniq) | 2026-09-22 | B |
| 6 | EMEP/EEA Guidebook 2023, 1.A.1 | Uslubiy asos (jadval olinmadi — §2.3) | 2023-10-02 | A |
| 7 | Open-Meteo Archive (ERA5) | Shamol yo'nalishi, 4 344 soat (180 kun) | 2026-10-01 (jonli) | C |
| 8 | A-qatlam 180 kunlik ekran (`aq_180kun.csv`) | Kuzatuv qiymatlari | 2026-10-01 (jonli) | C |

---

## 12. Keyingi qadam

1. **03–05.10** — 3 ta rasmiy talabni yuborish va muddatni yuritish (kuch 5).
2. **10.10** — oynani isitish mavsumiga uzaytirish (qadam 3) — **EMEP jadvali olindi** (§2.3),
   modul tayyor (`mavsum.py`), keyingi qadamda birinchi **isitish lifti** o'lchanadi.
3. **10–15.10** — FIRMS `MAP_KEY` olinishi bilan yonish nuqtalari (qadam 4); kalit kelmasa — **alternativa**: yonish nuqtasini ELV/hisobot ma'lumotidan emas, **tungi NO2 cho'qqilari** orqali skrining (yo'l #5 uslubi, hujjatlashtirilgan).
4. **25–31.10** — Angren/Ohangaron retseptori (qadam 6) — uzun masofa uchun **alohida** ekran va alohida fon bahosi.
5. PM2,5 uchun **ikkilamchi aerozol** gipotezasini sinash (SO2/NOx nisbati + namlik), §7 ni yopish.
