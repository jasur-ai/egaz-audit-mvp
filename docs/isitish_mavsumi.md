# Isitish mavsumi: birinchi haqiqiy o'lchov (365 kun)

> Manba hujjat: `YAKUNIY/18-ISITISH-MAVSUMI.md` · 2026-10-01 · kod: `src/kirishsiz/mavsum.py` · CLI: `scripts/kirishsiz.py mavsum` · ma'lumot: `data/public/{aq_365kun,wind_era5_365kun,havo_era5_365kun}.csv`

---

> **Nima yangi:** oyna **orqaga** — o'tgan isitish mavsumiga (2025-10-02 → 2026-03-31) uzaytirildi
> (kutish shart emas: CAMS tarixi + ERA5 365 kun beradi). Bu **birinchi marta** isitish mavsumini
> o'lchash imkonini berdi va A-qatlam hisobotining eng zaif bandini — «oyna isitishni qoplamaydi» — yopdi.
>
> **Eng muhim uchta natija:**
> 1. **Normadan oshgan kunlar 21/365 — hammasi isitish mavsumida** (isitish davrida 11,6%, issiq davrda **0%**).
> 2. **IES yo'nalishi qishki ko'tarilishni tushuntirmaydi**: sektor lifti isitishda **1,21**, issiqda **1,20** — o'zgarmaydi.
> 3. **Eng yomon 21 kundan faqat 6 tasida** shamol IES sektoridan; 5 tasida u **umuman yo'q** → qishki epizodlar shahar miqyosidagi manba (isitish + inversiya).

---

## 1. Oyna va qamrov

| Ko'rsatkich | Qiymat |
|---|---|
| Oyna | **2025-10-02 → 2026-10-01** (8 760 soat, 365 kun) |
| Ma'lumot to'liqligi | AQ 8 760/8 760 · shamol 8 760 · harorat 8 760 (**bo'sh qiymat yo'q**) |
| **Isitish soatlari** (o'rt. kunlik ≤ +8 °C) | **2 319 (26,5%)** — 1 138 kun·soat |
| Issiq soatlar | 6 441 (73,5%) |
| Harorat: min / o'rt / maks | **−8,6** / 17,4 / **45,2 °C** |
| Oylar | 2025-10 → 2026-10 |

**Yangi manbalar (provenans bilan):** `aq_365kun.csv` (`ddf00f075e3f…`), `wind_era5_365kun.csv` (`181f84e8c28d…`),
`havo_era5_365kun.csv` (`5b194cf5f1af…`). CLI: `fetch_public.py --source open-meteo-aq-tarix`
(CAMS tarixi 2022 dan — yangi rejim).

---

## 2. Oylik dinamika — qishki cho'qqi aniq ko'rinadi

| Oy | Harorat (o'rt / min) | PM2,5 | Holat |
|---|---|---|---|
| 2025-10 | 17,1 / 6,4 | 17,16 | o'tish |
| **2025-11** | **7,7 / −2,8** | **31,23** | 🔥 **cho'qqi** |
| **2025-12** | 3,5 / −7,0 | **26,47** | 🔥 |
| **2026-01** | **2,1 / −8,6** | **23,96** | 🔥 |
| 2026-02 | 9,0 / 0,1 | 16,01 | chegara |
| 2026-03 | 10,8 / −6,2 | 19,19 | o'tish |
| 2026-04 | 18,3 / 8,5 | 12,47 | issiq |
| 2026-05 | 23,7 / 13,4 | 13,66 | issiq |
| **2026-06** | 29,4 / 21,1 | **16,60** | issiq cho'qqi (aerozol) |
| 2026-07 | 31,6 / 18,8 | 14,03 | issiq |
| 2026-08 | 30,4 / 18,9 | 12,03 | eng toza oy |
| 2026-09 | 24,4 / 13,7 | 13,77 | issiq |

**Nisbat:** noyabr (31,23) ÷ avgust (12,03) = **2,60×**. Yillik o'rtacha **18,07 µg/m³**
(180 kunlik «issiq» oynadagi 13,79 dan **31% yuqori**).

---

## 3. Normadan oshgan kunlar — asosiy natija

| Davr | Kunlar | Normadan oshgan (>35 µg/m³) | Ulush |
|---|---|---|---|
| **Isitish davri** (2025-10 → 2026-03) | 181 | **21** | **11,6%** |
| **Issiq davr** (2026-04 → 09) | 183 | **0** | **0,0%** |
| Butun yil | 365 | 21 | 5,8% |

**O'zaro tekshiruv:** 2026-04-04 → 09-30 oralig'ida (A-qatlamning 180 kunlik oynasi) **0 kun** — hisobotdagi
«0/180 kun» bilan **to'liq mos** ✅. Yangi ma'lumot uni **rad etmaydi**, balki **kontekstga qo'yadi**.

**Eng og'ir kunlar:**

| # | Kun | PM2,5 kunlik | Harorat | Izoh |
|---|---|---|---|---|
| 1 | **2025-12-01** | **61,66** | 2,7 °C | normadan **1,76×** |
| 2 | 2025-11-30 | 59,27 | 3,8 °C | |
| 3 | 2025-11-23 | 55,40 | 7,3 °C | |
| 4 | 2025-11-22 | 52,25 | 7,5 °C | |
| 5 | 2025-11-24 | 50,32 | 6,7 °C | |

Soatlik daraja: **> 25 µg/m³ — 1 709 soat (19,5%)** · **> 35 µg/m³ — 659 soat (7,5%)**
(issiq oynada: 233 va 8 soat). P95 = 39,80 · maks = **93,80 µg/m³**.

---

## 4. Epizod atributsiyasi — kim aybdor? (yangi usul)

Har bir normadan oshgan kun uchun shamolning qanchasi manba sektoridan (54,9° ±45°) kelgani hisoblanadi
(kod: `mavsum.epizod_atributsiya`):

| Toifa | Kunlar | Ma'nosi |
|---|---|---|
| `sektor_ustun` (≥50%) | **6** | IES yo'nalishi ehtimoliy |
| `aralash` (20–50%) | **10** | qisman |
| `sektordan_tashqarida` (<20%) | **5** | **IES tushuntirmaydi** |

**Eng yomon 5 kun:** 2025-12-01 (IES 38%), 11-30 (33%), 11-23 (21%), 11-22 (25%), 11-24 (38%) —
hech birida IES sektori ustun emas. **Eng toza IES ishi:** 2025-11-26 (71%), 12-02 (67%).

**Epizod kunlarining sharoiti:** o'rt. harorat **4,4 °C**, o'rt. shamol **3,38 m/s**
(yillik isitish o'rtachasi 4,77 m/s) — ya'ni **sokin + sovuq** = to'planish sharoiti.

---

## 5. Sektor lifti mavsumiy — hal qiluvchi dalil

| Modda | Isitish lifti (n=822) | Issiq lifti (n=1 286) | Farq |
|---|---|---|---|
| **PM2,5** | **1,21** | **1,20** | **o'zgarmaydi** |
| PM10 | 1,15 | 1,04 | +0,11 |
| **NO2** | **1,31** | **1,73** | **−0,42** |
| SO2 | 0,99 | 1,06 | −0,07 |

**Talqin:**

1. **PM2,5 bo'yicha IES yo'nalishining nisbiy hissasi qishda o'zgarmaydi** (1,21 ↔ 1,20). Ya'ni qishki
   2,6 barobar ko'tarilish **IES sektoridan kelmaydi** — u **shahar miqyosidagi** manba (maishiy isitish,
   ko'cha changi, transport) va **sokin havo** natijasi.
2. Absolyut ortiqcha o'sadi (isitishda +4,98, issiqda +2,89 µg/m³), lekin bu **fon ham birga o'sgani** uchun —
   nisbat barqaror.
3. **NO2 lifti qishda pasayadi** (1,31 vs 1,73): sovuq havoda shahar fon NO2 si (isitish qozonlari, transport)
   shunchalik oshadiki, IES ulushi **nisbatan** kichrayadi.

**Qo'shimcha:** PM2,5/PM10 nisbati — isitishda **0,860**, issiqda **0,680** → qishda **nozik yonish zarrasi**
ustun (maishiy isitish spektri), yozda esa yirikroq ulush (chang). Harorat korrelyatsiyasi (365 kun):
**r = −0,461** (180 kunlik issiq oynada −0,21 edi).

---

## 6. Dispersiya sharoiti (nega qishda to'planadi)

| Ko'rsatkich | Isitish | Issiq |
|---|---|---|
| Shamol tezligi (o'rt. / mediana) | **4,77 / 4,40 m/s** | 6,40 / 5,80 m/s |
| **Sokin soatlar (<2 m/s)** | **343 (14,8%)** | 394 (6,1%) |
| Maks. shamol | 18,6 m/s | 23,1 m/s |

Ya'ni qishda **shamol 25% kuchsizroq** va **sokin soatlar 2,4 barobar ko'proq** → bir xil oqim **yuqoriroq
konsentratsiya** beradi. Bu — «IES ko'proq chiqaryapti» emas, «havo chiqindini ko'tarmayapti» degani.
Shu sababli yo'nalish tahlilining ishonchliligi ham pasayadi (14,8% soatda yo'nalish deyarli yo'q).

---

## 7. Nima isbotlanadi / nima isbotlanmaydi

| ✅ Isbotlanadi | ❌ Isbotlanmaydi |
|---|---|
| Norma oshishlari **faqat** isitish mavsumida (21/181 ↔ 0/183) | Qishki PM2,5 ning **manbalar bo'yicha ulushi** (maishiy isitish vs boshqa) |
| IES yo'nalishi hissasi mavsumdan qat'i nazar **barqaror** (1,21 ↔ 1,20) | Har bir kun uchun aniq aybdor (yo'nalish — ehtimol, dalil emas) |
| Eng yomon 21 kundan **6 tasida** (29%) IES sektori ustun | Aniq **obyekt** (IES ↔ Chirchiq ajratilmaydi; ≤7 km chegarasi) |
| Sokin havo (14,8%) + sovuq → to'planish sharoiti | Rasmiy isitish sanalari (hokimiyat qarori; mezon operativ) |
| A-qatlam «0/180» bilan **mos** (0/183) | Maishiy isitishning **miqdoriy** hissasi (yoqilg'i statistikasi kerak) |

---

## 8. Kod, CLI, ma'lumot, testlar

### 8.1. Kod

| Fayl | Nima qo'shildi |
|---|---|
| `src/kirishsiz/mavsum.py` | `o_rtacha_yonalish()` (aylana bo'yicha vektor o'rtacha) · **`epizod_atributsiya()`** (uch toifa) |
| `scripts/fetch_public.py` | yangi rejim: **`open-meteo-aq-tarix`** (`--boshlanish/--tugash`, CAMS 2022 dan) |
| `scripts/kirishsiz.py` | yangi subkomanda: **`mavsum`** (qamrov · oylik · liftlar · epizodlar) |

### 8.2. CLI (jonli)

```bash
python3 scripts/kirishsiz.py mavsum
# → isitish 2 319 (26,5%) · noyabr PM2,5 31,23 🔥 · lift PM2,5 1,21 ↔ 1,20 · epizodlar 6/10/5
```

### 8.3. Ma'lumot

| Fayl | Qatorlar | SHA-256 (12) |
|---|---|---|
| `aq_365kun.csv` | 8 760 | `ddf00f075e3f` |
| `wind_era5_365kun.csv` | 8 760 | `181f84e8c28d` |
| `havo_era5_365kun.csv` | 8 760 | `5b194cf5f1af` |

**Sifat nazorati:** API 8 760/8 760 soat qaytardi (bo'sh 0); oyna chegaralari 2025-10-02T00:00 → 2026-10-01T23:00.

### 8.4. Testlar

`test_kirishsiz_mavsum.py`: **14 → 19** (vektor o'rtacha · uch toifa · chegara · qisqa kun · maydonlar).
**L1 jami: 273 ✅** · **Umumiy: 466** (273 + 193).

---

## 9. A-qatlam raqamlariga ta'siri (halol tuzatish)

| Raqam | Ilgari | Endi (kontekst bilan) |
|---|---|---|
| Kunlik norma oshishlari | «0/180 kun» | «**0/180 (issiq oyna)** · **21/365 (butun yil)** · isitish davrida 11,6%, issiqda 0%» |
| PM2,5 o'rtachasi | 13,79 (issiq oyna) | **18,07 (yillik)** · 25,60 (isitish) · 15,36 (issiq) |
| Cho'qqi kunlik | 26,82 (issiq) | **61,66 (2025-12-01)** |
| Sektor lifti (IES) | NO2 2,30 · PM2,5 1,86 | **o'zgarmaydi** (issiq oynada) · qishda NO2 1,31 · PM2,5 1,21 |

**Xulosa:** A-qatlam xulosasi **rad etilmadi** — aksincha, yangi ma'lumot uning **chegarasini** ko'rsatdi:
issiq oynadagi «toza» manzara **yilning eng toza davri**. Haqiqiy muammo — **isitish mavsumi**, va u
**shahar miqyosida**, IES yo'nalishida emas.

---

## 10. Keyingi qadam

1. **05.10** — 3 rasmiy talabni yuborish (matnga qishki natija qo'shiladi: so'rovlar maishiy isitish va
   fon monitoringiga ham tegishli bo'ladi).
2. **10.10** — joriy isitish mavsumi boshlanishi bilan **real vaqtda** kuzatish (oyna avtomatik yangilanadi:
   `fetch_public.py --source open-meteo-aq-tarix`).
3. **Maishiy isitish hissasi** — yoqilg'i statistikasi (gaz iste'moli, qozonxonalar) ochiq manbalardan izlash;
   bu qishki 21 epizodning **miqdoriy** atributsiyasi uchun yagona yetishmayotgan bo'g'in.
4. **Epizod atributsiyasini Ohangaron va Angren retseptorlarida** ham ishga tushirish (365 kun) —
   sement klasteri va ko'mir stansiyasi uchun mavsumiy xulq-atvor.
