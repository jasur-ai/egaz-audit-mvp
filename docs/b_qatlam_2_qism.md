# B-qatlam 2-qism: EF taqqoslash, PM2,5 manbasi, retseptorlar, mavsum oynasi

> Manba hujjat: `YAKUNIY/17-B-QATLAM-2-QISM.md` · sana 2026-10-01 · kod: `src/kirishsiz/aerosol.py`, `mavsum.py`, `retseptorlar.py` · CLI: `profil`, `retseptorlar`, `pastdan --emep`

---

> **Bu hujjat nimani yopadi:** (1) `16-…MASS-BALANS.md` §2.3 da qolgan **ochiq band** — EMEP/EEA 1.A.1 koeffitsienti;
> (2) §7 dagi **halol chegara** — PM2,5 ortiqchasi nimadan; (3) B-qatlamning 3- va 6-qadamlari —
> **mavsum oynasi** va **alohida retseptorlar** (Angren/Ohangaron).
> Har bir xulosa **real kod + jonli ma'lumot** bilan, «nima isbotlanmaydi» ochiq ko'rsatilgan.

---

## 0. Qisqacha natija

| Savol | Javob | Dalil |
|---|---|---|
| EMEP/EEA koeffitsienti AP-42 ga mos keladimi? | **HA** — 89 g/GJ, AP-42 oralig'i (55,9–137,6) ichida, markazdan **1,5%** farq | §1 |
| A-qatlam hisoboti EMEP asosida ham sig'adimi? | **HA** — model 3,7–7,4 µg/m³, kuzatuv 9,24 → nisbat **1,25–2,50** (≤3) | §1.3 |
| PM2,5 ortiqchasi birlamchi gaz zarrasimi? | **YO'Q** — model kuzatuvning **4,2%** ini beradi; chang ham emas (sektor lifti 0,76) | §2 |
| NO2 va PM2,5 bir manbadanmi? | **YO'Q** — NO2 cho'qqisi **60°**, PM2,5 cho'qqisi **105°**; NO2 5,0×, PM2,5 1,55× | §3 |
| Uzoq manbalarni alohida retseptorda ajratsa bo'ladimi? | **QISMAN** — Ohangaron klasterida 3 manba 3 yo'nalishda; ammo **~7–40 km** dan yaqinini model ajratmaydi | §4–5 |
| Oyna isitish mavsumini qoplaydimi? | **YO'Q** — 4 344 soatdan **0 tasi** ≤ +8 °C | §6 |

---

## 1. Ochilgan band: EMEP/EEA 2023 koeffitsienti

### 1.1. Manba topildi va tasdiqlandi

`16-…` §2.3 da EMEP/EEA 2023 **1.A.1** jadvali olinmagan edi (EEA sahifasi jadvalni JavaScript orqali yuklaydi,
qidiruv doimiy ravishda 1.A.3.d — navigatsiya bo'limiga olib ketardi). Bu safar **PDF manbasiga** to'g'ridan-to'g'ri
yetib borildi va **Table 3-4** (1.A.1.a «Public electricity and heat production», **tabiiy gaz**) olindi:

| Modda | Qiymat | Birlik | 95% CI | Manba (EMEP ichida) |
|---|---|---|---|---|
| **NOx** | **89** | g/GJ | 15–185 | US EPA (1998), chapter 1.4 |
| CO | 39 | g/GJ | 20–60 | US EPA (1998), ch. 1.4 |
| NMVOC | 2,6 | g/GJ | 0,65–10,4 | US EPA (1998), ch. 1.4 |
| SOx (AQSh) / (YeI) | 0,281 / 0,244 | g/GJ | 0,169–0,393 / <0,030–0,458 | US EPA (1998) / DBI 2014 |
| TSP / PM10 / **PM2,5** | **<0,14** | g/GJ | <0,09–<0,19 | UBA 2019 |

*Manba: EMEP/EEA air pollutant emission inventory guidebook 2023, 1.A.1 Energy industries (02.10.2023), Table 3-4. Tier A.*

### 1.2. AP-42 bilan solishtirish — mustaqil tekshiruv

| Ko'rsatkich | Qiymat |
|---|---|
| AP-42 §3.1-1 (gaz turbinasi, NOx) | 55,9–137,6 g/GJ (0,13–0,32 lb/MMBtu) |
| AP-42 **geometrik o'rtasi** | **87,7 g/GJ** |
| EMEP/EEA 2023 1.A.1.a | **89 g/GJ** |
| Farq | **1,5%** → **«kelishadi»** ✅ |

Ikki mustaqil tizim (AQSh AP-42 va Yevropa EMEP/EEA) bir-birini **mustaqil tasdiqlaydi**.
Kod: `bottomup.ef_taqqoslash()` (test: `test_ef_taqqoslash_kelishadi`).

> **Muhim nuance:** EMEP PM2,5 qiymati **<0,14 g/GJ** — AP-42 ning 2,84 g/GJ dan **20 marta past**.
> Ya'ni birlamchi zarra bo'yicha ikki tizim *farq qiladi* va EMEP yana-da qat'iy: gaz yonishida PM2,5 ~0.

### 1.3. EMEP asosida qayta hisob (jonli)

```
EF (EMEP): 89 g/GJ (CI 15–185) → 0,641–0,915 g NOx/kWh (FIK 50%–35%)
NOx: 3 717–5 309 t/yil → oqim 0,118–0,168 kg/s
Sektor o'rtachasi (13,28 km, D, mos ulush 19,5%): 3,7 (u=4) … 7,4 (u=2) µg/m³
Kuzatuv: +9,24 µg/m³ → nisbat 1,25–2,50 → **mos (bir tartib kattaligida)** ✅
```

**Ikkala EF manbasi birgalikda:** model **3,7–11,4 µg/m³**, kuzatuv **9,24** → kuzatilgan qiymat model
«konverti»ning **ichida**. Bu A-qatlam hisobotining mustaqil bahoga sig'ishini **ikki marta** tasdiqlaydi.

---

## 2. PM2,5 ortiqchasi nimadan? — olti sinov

Sektor (54,9° ±45°), 180 kun, Toshkent retseptori. Ortiqcha = sektorda − tashqarida.

| # | Sinov | Natija | Xulosa |
|---|---|---|---|
| 1 | **Mass-rekonstruksiya** (birlamchi zarra) | model 0,12 vs kuzatuv **2,89 µg/m³** → **4,2%** | birlamchi gaz zarrasi tushuntirmaydi |
| 2 | EMEP PM2,5 bilan | <0,14 g/GJ → ≈0,006 µg/m³ → **0,2%** | yana-da qat'iyroq |
| 3 | **Chang sinovi** (CAMS `dust`, sektor nisbiy) | sektor 11,41 vs fon 15,05 → **lift 0,76** | sektorda chang **kamroq** — ortiqcha chang emas |
| 4 | AOD (butun kolonka aerozoli) | 0,18 vs 0,19 → 0,96 | kolonka yukida farq yo'q |
| 5 | **Zarra spektri** (PM2,5/PM10) | sektor **0,724** vs fon 0,626 | nozik zarra ustun — yonish/ikkilamchi belgisi |
| 6 | Harorat bog'liqligi (isitish sinovi) | r = **−0,21** (kuchsiz manfiy) | isitish emas; qisman mavsumiy |

**Yakuniy xulosa (kod: `aerosol.xulosa()`):**

> PM2,5 ortiqchasi (a) gaz yonishining **birlamchi zarrasi** bilan izohlanmaydi (4,2%);
> (b) **mexanik chang** bilan ham izohlanmaydi (chang sektorda kamroq);
> (c) zarra spektri **nozik** tomonga siljigan (0,724).
> Qoladigan izoh: **ikkilamchi aerozol** (NOx → nitrat) yoki sektordagi **boshqa nozik zarra manbalari**.
> Ularning **ulushi miqdoriy ajratilmagan** — kimyoviy tarkib o'lchovisiz buni «isbot» deb aytib bo'lmaydi.

### 2.1. Yo'l-yo'lakay tuzatilgan xato (kod diagnostikasi)

Birinchi variantda avtomatik xulosa «PM10 da chang ulushi 67% — mexanik manba ehtimoli» deb **noto'g'ri** belgi
chiqargan edi: u **umumiy** chang ulushidan foydalanardi. Aniqlashtirildi — endi **sektor nisbiy** chang sinovi
ishlatiladi (lift 0,76 → «chang emas»). Bu farqni test to'plami emas, **hisob-kitobni tekshirish** ko'rsatdi;
ikkala yo'l ham (lift va ulush) hujjatda qoldirildi.

---

## 3. Yangi usul: yo'nalish profili (sektorni qo'lda tanlash o'rniga)

Sektorni qo'lda tanlash **tanlov xatosi** (cherry-picking) riskini beradi. Shu sababli **15° lik burchaklar
bo'yicha to'liq profil** hisoblanadi va cho'qqi burchak **kod bilan** aniqlanadi (`sector.yonalish_profili`).

| Modda | Cho'qqi | Eng past | Nisbat |
|---|---|---|---|
| **NO2** | **60° = 22,36 µg/m³** (45–120° plato 20–22) | 255° = 4,46 | **5,01×** |
| **PM2,5** | **105° = 16,70 µg/m³** (30–135° plato 16,1–16,7) | 255° = 10,75 | **1,55×** |

**Talqin (ehtiyotkorlik bilan):**

1. **NO2 keskin lokallashgan** (60°; 45–90° da 20–22 µg/m³) — qisqa yashovchi gaz, yaqin klaster (IES 54,9° + Chirchiq 60,1°).
2. **PM2,5 keng plato** (30–135° oralig'ida deyarli bir xil ≈16 µg/m³) — **bitta zavodga bog'lanmaydi**;
   viloyat miqyosidagi fon/ikkilamchi jarayon ko'rinishi.
3. **PM2,5 cho'qqisi 105°** — bu yo'nalishda reyestrda obyekt **yo'q edi**; 105–115° da **Angren koridori**
   (Angren shahri 114,4°) joylashgan. Bu — **yangi nomzod kerak** degan signal (§5.2).

---

## 4. Sifat nazorati: model o'lchamini **empirik** o'lchash (yangi)

Usulning asosiy cheklovi — ma'lumot **CAMS modeli** (global katak ≈0,4°) va **ERA5 shamoli** (≈0,25°).
Buni hisoblab emas, **o'lchab** ko'rsatdik: turli retseptorlar seriyalari bir xil yoki farqli ekanini tekshirdik.

| Juftlik | Masofa | 4 320 qatordan bir xillari | O'rt. farq (PM2,5) | Xulosa |
|---|---|---|---|---|
| **Ohangaron ↔ Olmaliq** | **7,2 km** | **4 320 (100%)** | **0,000** | **bir xil katak** ⚠️ |
| Angren ↔ Ohangaron | 39,1 km | 88 | 2,148 | alohida katak |
| Toshkent ↔ Ohangaron | 56,2 km | 32 | 4,833 | alohida katak |
| Toshkent ↔ Angren | 77,3 km | 24 | 5,953 | alohida katak |

**Shamolda ham xuddi shunday:** Ohangaron va Olmaliq ERA5 fayllari **bir xil SHA-256** — bitta katak (`era5_katak_tekshiruvi()`).

**Bundan kelib chiqadigan qat'iy chegara (barcha hisobotlarga tegishli):**

| Masofa | Ajratish qobiliyati |
|---|---|
| ≤ ~7 km | **yo'q** — bir katakda qoladi (masalan, Angren IES 4,06 km) |
| ~7–40 km | chegaraviy — yo'nalish signali bor, lekin **obyekt** emas, **hudud** darajasida |
| ≥ ~40 km | yo'nalish ajratiladi (kuzatilgan: 39–77 km farqlanadi) |

Shu sababli hisobotlardagi «qaysi yo'nalish va klaster» formulasi — **tasodifiy ehtiyotkorlik emas, o'lchangan chegara**.

---

## 5. Alohida retseptorlar (B-qatlam 6-qadam)

### 5.1. Reyestr (manbali, `data/public/retseptorlar_uz.json`)

| Retseptor | Koordinata | Manba | PM2,5 | PM10 | NO2 | SO2 |
|---|---|---|---|---|---|---|
| Toshkent markaz | 41,311 / 69,240 | loyiha bazasi | **13,79** | 21,38 | **12,54** | 4,35 |
| **Ohangaron** | 40,9054 / 69,6401 | OSM relation 18507147 | 9,42 | 17,65 | 4,72 | 1,94 |
| **Olmaliq** | 40,8457 / 69,6072 | OSM relation 7726941 | 9,42 ⚠️ | 17,65 | 4,72 | 1,94 |
| **Angren** | 41,0212 / 70,0795 | OSM relation 7774377 | **8,23** | 15,23 | 6,12 | 1,94 |

⚠️ Ohangaron = Olmaliq — **bir xil katak** (§4), ya'ni ular ikkita emas, **bitta** ekran.

**Ohangaron zonasi — ajratish imkoni (yangi):** uchta manba uch xil yo'nalishda:
Akhangarancement **20,1° / 3,05 km**, Toshkent Conch **126,4° / 11,02 km**, AGMK **240,3° / 10,85 km**.
Shamol bo'yicha ajratish **printsipial mumkin** (Toshkentda bunday imkon yo'q).

Yo'nalish profili (Ohangaron, NO2): **cho'qqi 105° = 8,08** vs eng past 300° = 1,25 → **6,5×**.
Bu burchak Conch yo'nalishiga (126,4°) yaqin; sektorli hisobda Conch yo'nalishi **NO2 lift 2,60 (+4,68 µg/m³)** beradi.
**Ammo** §4 chegarasi kuchda: 11 km masofa ajratish chegarasida, ya'ni «Conch zavodi aybdor» deyilmaydi —
«SE yo'nalishida NO2 boyitilishi bor» deyiladi.

### 5.2. Angren: reyestr bo'shlig'i yopildi

PM2,5 cho'qqisining (105°) Angren koridoriga (114,4°) yaqinligi **yangi nomzod** kerakligini ko'rsatdi.
Reyestrga **6-obyekt** qo'shildi:

| Obyekt | Koordinata | Quvvat | Yoqilg'i | Manba |
|---|---|---|---|---|
| **Angren IES (ko'mir stansiyasi)** | 41,004897 / 70,122799 (exact) | 484 MVt (4×53+4×68); Wikidata: 393 MVt | **ko'mir (lignit)** | GEM *Angren power station* (18.08.2026, Tier B) |

Angren retseptoridan masofa: **4,06 km, azimut 116,6°**.

**Sinov natijasi (halol):** ko'mir stansiyaning aniq belgisi bo'lishi kerak bo'lgan **SO2** bo'yicha
sektor lifti **0,97** (signal yo'q); PM2,5 **1,00**; PM10 1,22; NO2 0,61.
**Sabab:** 4,06 km < 7 km → manba va retseptor **bir katakda** (§4). Ya'ni bu **salbiy natija** emas —
**chegaraning amaliy tasdig'i**: usul 4 km dagi manbani ko'rmaydi va buni yashirmaydi.

---

## 6. Mavsum oynasi (B-qatlam 3-qadam)

### 6.1. Hozirgi qamrov (harorat mezoni, +8 °C)

Yangi modul `mavsum.py`: isitish davri **o'rtacha kunlik harorat ≤ +8 °C** mezoni bo'yicha aniqlanadi
(bino isitish davri amaliyoti; rasmiy sanalar tuman hokimiyatlari qarori bilan — hujjatda shunday yozilgan).

| Ko'rsatkich | Qiymat |
|---|---|
| Soatlar | 4 344 (2026-04-04 → 10-01) |
| **Isitish soatlari (≤ +8 °C)** | **0 (0,0%)** |
| Harorat: min / o'rt / maks | **8,5** / 26,4 / **45,2 °C** |
| Oylik o'rtacha | apr 18,1 · may 23,7 · iyn 29,4 · iyl 31,6 · avg 30,4 · sen 24,4 |
| Namlik (o'rt.) | 38% |

**Xulosa:** A-qatlam oynasi **butunlay issiq mavsum**. Shu sababli:
- «isitish hissasi» bo'yicha **hech qanday** xulosa chiqarilmaydi (ilgari ham aytilgan, endi miqdoriy tasdiqlangan);
- **PM2,5 oylik cho'qqisi iyun (16,60)** — isitish emas, **issiq davr** manbasi (ikkilamchi aerozol/foto-kimyo §2 bilan mos).

### 6.2. Kengaytirish rejasi

| Qadam | Nima |
|---|---|
| 10.10.2026 | Yangi oyna (apr → oktabr ortidan) `fetch_public.py --source open-meteo-aq --kun <N>` + ERA5 |
| Keyin | `sektor` va **`mavsum`** qayta ishga tushiriladi → **isitish lifti** birinchi marta o'lchanadi |
| Nazorat | `mavsum.reja()` yo'q oylarni (noyabr, dekabr) avtomatik ko'rsatadi |

---

## 7. Kod, CLI, ma'lumot va testlar

### 7.1. Yangi/kengaytirilgan kod

| Fayl | Nima |
|---|---|
| `src/kirishsiz/aerosol.py` **(yangi)** | sektor tarkibi · PM2,5/PM10 spektri · chang ulushi · harorat bog'liqligi · mass-rekonstruksiya · `xulosa()` |
| `src/kirishsiz/mavsum.py` **(yangi)** | harorat mezoni · qamrov · mavsumiy lift · kengaytirish rejasi |
| `src/kirishsiz/retseptorlar.py` **(yangi)** | retseptorlar reyestri (manba majburiy) · yaqin obyektlar · ERA5 katak tekshiruvi · qiymat xulosasi |
| `src/kirishsiz/bottomup.py` | + `EMEP_EEA_2023` konstantalari · `emep_ef_g_per_kwh()` · `ef_taqqoslash()` |
| `src/kirishsiz/sector.py` | + `yonalish_profili()` · `profil_grafik()` |
| `scripts/fetch_public.py` | + 2 manba: `open-meteo-archive-havo` (harorat/namlik/yog'in) · `open-meteo-aq-qoshimcha` (CAMS chang + AOD) |
| `scripts/kirishsiz.py` | + `profil` va `retseptorlar` subkomandalari · `pastdan --emep` |

### 7.2. CLI (jonli ishga tushirildi)

```bash
python3 scripts/kirishsiz.py pastdan --obyekt "Toshkent IES:41.3796:69.370217" \
    --ishlab-chiqarish 5.8 --emep --fik 0.35,0.50 --mo-ri 100 --kuzatuv 9.24     # → nisbat 1,25–2,50
python3 scripts/kirishsiz.py profil --modda no2_ug_m3,pm2_5_ug_m3 --obyektlar    # → 60° vs 105°
python3 scripts/kirishsiz.py retseptorlar --radius 20                            # → 4 nuqta + bo'shliq/katak ogohlantirishi
```

### 7.3. Yangi ma'lumot (provenans bilan, `data/public/MANIFEST.json`)

| Fayl | Qatorlar | SHA-256 (12) | Manba |
|---|---|---|---|
| `havo_era5_180kun.csv` | 4 344 | `e06dbeb6b982` | Open-Meteo Archive (ERA5) |
| `cams_qoshimcha_180kun.csv` | 4 320 | `6b41666b1155` | Open-Meteo AQ (CAMS: `dust`, `aod`) |
| `aq_Ohangaron_180kun.csv` | 4 320 | `e1696822dd3b` | Open-Meteo AQ |
| `aq_Angren_180kun.csv` | 4 320 | `a3ca8db12ce5` | Open-Meteo AQ |
| `aq_Olmaliq_180kun.csv` | 4 320 | `d1e4baaa82b8` | Open-Meteo AQ |
| `wind_Ohangaron_180kun.csv` | 4 344 | `68be24688ef2` | ERA5 (Olmaliq bilan **bir xil katak**) |
| `wind_Angren_180kun.csv` | 4 344 | `e7d7cf1c4192` | ERA5 |
| `wind_Olmaliq_180kun.csv` | 4 344 | `68be24688ef2` | ERA5 |
| `retseptorlar_uz.json` | 4 yozuv | — | OSM Nominatim (relation ID lari) |
| `nomzodlar_uz.json` | **6 obyekt** | — | + Angren IES (GEM) |

### 7.4. Testlar

| To'plam | Test |
|---|---|
| `test_kirishsiz_aerosol.py` | **22** |
| `test_kirishsiz_mavsum.py` | **14** |
| `test_kirishsiz_retseptorlar.py` (retseptorlar + profil) | **18** |
| `test_kirishsiz_bottomup.py` | **33 → 39** (EMEP) |
| **L1 jami** | **262 ✅** (avval 208) |
| **Umumiy (L1+L2)** | **455** (262 + 193) |

---

## 8. Nima isbotlanadi / nima isbotlanmaydi (yangilangan)

| ✅ Isbotlanadi | ❌ Isbotlanmaydi |
|---|---|
| Ikki mustaqil EF tizimi (AP-42 ↔ EMEP/EEA) **kelishadi** (1,5%) | IES **haqiqiy** yillik tashlanmasi (rasmiy inventar ochiq emas) |
| A-qatlam hisoboti **ikki EF manbasi** bilan ham sig'adi (nisbat 0,8–2,5) | PM2,5 ortiqchasining **miqdoriy** taqsimoti (ikkilamchi vs boshqa) |
| PM2,5 ortiqchasi birlamchi zarra **ham**, chang **ham** emas (4,2% / lift 0,76) | NO2 va PM2,5 ning **kimyoviy** manbasi (tarkib o'lchovi yo'q) |
| NO2 va PM2,5 **har xil** yo'nalish profillariga ega (60° / 105°) | **Qaysi obyekt** — ~7–40 km dan yaqin manbalar ajratilmaydi (o'lchandi) |
| Usul chegarasi **empirik** o'lchandi (7,2 km da bir xil katak) | Isitish mavsumi hissasi — oynada **0 isitish soati** |
| Ohangaron klasterida shamol ajratish **printsipial** mumkin | Ohangaron: 3 km masofa — katak ichida, ajratib bo'lmaydi |

---

## 9. Manbalar (sana + tier)

| # | Manba | Nima uchun | Sana | Tier |
|---|---|---|---|---|
| 1 | [EMEP/EEA Guidebook 2023 — 1.A.1 Energy industries (PDF)](https://www.eea.europa.eu/en/analysis/publications/emep-eea-guidebook-2023/part-b-sectoral-guidance-chapters/1-energy/1-a-combustion/1-a-1-energy-industries-2023) | **Table 3-4**: NOx 89 g/GJ (CI 15–185), PM2,5 <0,14 g/GJ | 2023-10-02 | A |
| 2 | [EPA AP-42 §3.1-1](https://www.epa.gov/sites/default/files/2020-10/documents/b03s01.pdf) | NOx 0,13–0,32 lb/MMBtu (solishtirish asosi) | 2020-10 | A |
| 3 | [GEM — Angren power station](https://www.gem.wiki/Angren_power_station) | Koordinata 41,004897/70,122799 (exact) | 2026-08-18 | B |
| 4 | [industryabout — Angren Coal Power Plant](https://www.industryabout.com/country-territories-3/2015-uzbekistan/fossil-fuels-energy/30885-angren-coal-power-plant) | 484 MVt (4×53+4×68), lignit | 2019-05-30 | C |
| 5 | [OpenStreetMap Nominatim](https://nominatim.openstreetmap.org/) | Retseptor koordinatalari (relation ID bilan) | 2026-10-01 (jonli) | C |
| 6 | [Open-Meteo Air Quality (CAMS)](https://air-quality-api.open-meteo.com) | AQ seriyalar + `dust`/`aod` komponentlari | 2026-10-01 (jonli) | C |
| 7 | [Open-Meteo Archive (ERA5)](https://archive-api.open-meteo.com) | Shamol + harorat/namlik | 2026-10-01 (jonli) | C |

---

## 10. Keyingi qadam

1. **05.10** — 3 rasmiy talabni yuborish (javob muddati 17.10, eskalatsiya 22.10).
2. **10.10** — oynani kengaytirish: **birinchi marta isitish lifti** o'lchanadi (`mavsum` moduli tayyor).
3. **10.10+** — Ohangaron klasterida **uch yo'nalishli** ajratishni to'liq ishlatish (Conch / AGMK / Akhangarancement),
   shu jumladan PM10 (sement changi) bo'yicha; **Conch** uchun qo'shimcha dalil (ishlab chiqarish hajmi 6300 t/kun).
4. **Angren** — ko'mir stansiya uchun **yer usti o'lchovi** yoki rasmiy hisobot so'rovi (usul 4 km da ko'rmaydi).
5. **PM2,5** — kimyoviy tarkib (nitrat/sulfat/EC) bo'yicha ochiq ma'lumot izlash yoki rasmiy so'rov; aks holda
   «ikkilamchi aerozol» **gipoteza** bo'lib qoladi.
