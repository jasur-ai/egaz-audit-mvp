# Maishiy isitish: miqdoriy baho + retseptorlar taqqoslamasi


> **Nima yangi:** ketma-ketlikning 3- va 4-qadami bajarildi:
> **(3)** Angren / Ohangaron / Olmaliq retseptorlari ham **365 kun** bilan hisoblandi;
> **(4)** maishiy isitish hissasi **yoqilg'i asosida miqdoriy** baholandi (EMEP/EEA 1.A.4 × quti modeli).
>
> **Eng muhim uchta natija:**
> 1. **Angren — kuchli manfiy nazorat:** 4 km masofada ko'mir IES, isitish soati Toshkentdan **ko'p** (2 533 ↔ 2 319),
>    lekin isitish lifti **0,97×** va normadan oshgan kun **0**. Ya'ni «qishki ko'tarilish» IES ham, iqlim ham emas.
> 2. **Toshkent ortishi gaz isitish bilan tushunarsiz:** gaz PM2,5 beradi 1,2 g/GJ, qattiq yoqilg'i 398 g/GJ
>    (**330×** farq). Kuzatilgan +10,24 µg/m³ ni gaz bilan chiqarish uchun **37,5 mlrd m³ gaz** kerak bo'lardi —
>    O'zbekistonning butun yillik qazib olishi 42,3 mlrd m³.
> 3. **Yagona izchil tushuntirish:** isitish energiyasining **≈15%** qismi qattiq yoqilg'idan bo'lsa, kuzatilgan
>    ortish to'liq qoplanadi (9 variantli sezgirlikda **10,0–25,5%**). Ana shu raqam 05.10 so'rovlarining maqsadi.

---

> Manba hujjat: `YAKUNIY/19-MAISHIY-ISITISH.md` · 2026-10-01 · kod: ``src/kirishsiz/isitish.py`` · CLI: ``scripts/kirishsiz.py isitish` · `taqqos``

---


## 1. Retseptorlar taqqoslamasi — 365 kun, bir xil mezon

Mezon: isitish kuni = o'rtacha kunlik harorat **≤ +8 °C**; epizod = kunlik PM2,5 **> 35 µg/m³**.
Manba: Open-Meteo **CAMS** havo sifati arxivi + **ERA5** (shamol/harorat), 2025-10-02 → 2026-10-01, 8 760 soat.

| Retseptor | Yillik PM2,5 | Isitish | Issiq | **Lift** | Isitish soati | Epizod | Eng yomon kun |
|---|---|---|---|---|---|---|---|
| **Toshkent** (41,311 / 69,240) | **18,07** | 25,60 | 15,36 | **1,67** | 2 319 (26,5%) | **21** | **61,7** |
| **Ohangaron = Olmaliq** | 11,92 | 15,10 | 10,97 | 1,38 | 2 019 (23,1%) | **3** | 36,9 |
| **Angren** (41,0212 / 70,0795) | **8,65** | 8,44 | 8,73 | **0,97** | **2 533 (28,9%)** | **0** | 26,5 |

Kunlik qatorlar bo'yicha Pearson korrelyatsiyasi (n = 365):

| Juftlik | r |
|---|---|
| Toshkent ↔ Ohangaron | **0,816** |
| Angren ↔ Ohangaron | **0,811** |
| Toshkent ↔ Angren | 0,533 |

**O'qilishi:** mintaqaviy fon umumiy (r ≈ 0,81), lekin **mutlaq daraja** shahar miqyosiga bog'liq:
Toshkent yillik o'rtachasi Angrendan **2,1×**, Ohangaron klasteridan **1,5×** yuqori.

---

## 2. Angren — manfiy natija eng qimmat dalil

| Tekshiruv | Natija | Ma'nosi |
|---|---|---|
| Isitish soatlari | **2 533** (Toshkentdan 9% ko'p) | Angren **ko'proq** isitiladi — sovuqroq |
| PM2,5 lifti | **0,97×** | isitish mavsumida ko'tarilish **yo'q** |
| Normadan oshgan kun | **0** | butun yilda birorta epizod yo'q |
| Sektor lifti (IES 116,5°, ±15°) | PM2,5 **0,70 ↔ 1,01** · NO2 1,05 ↔ 0,63 · SO2 **1,74 ↔ 2,02** | PM2,5 signali yo'q; **SO2** signali bor (ko'mir yonishining kimyoviy izi) |
| Eng og'ir 5 kunda | 20,5 · 19,1 · 17,1 · 22,0 · 15,6 µg/m³ | hatto mintaqaviy epizodda ham me'yordan past |

**Nega bu muhim:** agar qishki ko'tarilish «sovuq + isitish» ning tabiiy natijasi bo'lganida, ko'mir stansiyasi
4 km masofada turgan va 2 533 soat isitiladigan Angrenda ham ko'rinishi kerak edi. Ko'rinmadi ⇒
**manba kuchi + aholi zichligi** hal qiluvchi omil, harorat emas.

---

## 3. Ohangaron ≡ Olmaliq — bitta o'lchov, ikki nom emas

- AQ qatorlari **26 280/26 280 qiymatda bayt-baytga bir xil**; shamol va harorat fayllari ham bir xil SHA-256
  (`e4a358ea5a12…`, `243e7c60c60b…`).
- **Xulosa:** 7,2 km masofada CAMS katagi ajratmaydi ⇒ bu **bitta** retseptor. Ilgari o'lchangan
  «≤ 7 km ajratilmaydi» chegarasi mustaqil ravishda yana tasdiqlandi.

---

## 4. Epizodlar mintaqaviy — lekin hamma joyda emas

| Kun | Toshkent | Ohangaron | Angren | Izoh |
|---|---|---|---|---|
| 2025-12-01 | **61,7** | 35,7 | 20,5 | uch shaharda ham eng og'ir kunlardan |
| 2025-11-30 | 59,3 | 35,0 | 19,1 | |
| 2025-11-23 | 55,4 | 33,4 | 17,1 | |
| 2025-11-22 | 52,3 | **36,9** | 22,0 | Ohangaron epizodi |
| 2025-11-24 | 50,3 | 30,6 | 15,6 | |

Ohangaron/Olmaliqning 3 epizodi ham (11-21 · 11-22 · 12-01) shamol **sement kombinati sektoridan tashqarida**
(0–4%) — mahalliy zavod aybdor emas, **mintaqaviy to'planish** aybdor. Angren esa bir xil kunlarda ham
o'z me'yoridan oshmaydi ⇒ **havza chegarasi** bor (Angren boshqa vodiy/ventilyatsiya rejimi).

---

## 5. Maishiy isitish — usul va manbalar

**Zanjir:** uy xo'jaligi soni → isitish energiyasi (GJ) → EMEP/EEA EF → emissiya (t) → quti modeli → µg/m³.

| Bo'g'in | Qiymat | Manba (daraja) |
|---|---|---|
| Aholi | **3 164,0 ming** (01.10.2025, +2,2% y/y) | toshstat.uz (rasmiy, A) |
| Uy xo'jaligi kattaligi | 3,8 kishi (oraliq 3,5–4,5) | qabul qilingan konvensiya (D) — respublika bo'yicha 5,1 (2017 so'rov, stat.uz) |
| Xususiy (hovli) uylar ulushi | **35,2%** (2023, yanv–noy) — 2022 da 48,2% | stat.uz (rasmiy, A) |
| → isitiladigan uy soni | **293 086** | o'z hisobimiz |
| Gaz sarfi (isitiladigan uy) | 2 000–4 000 m³/yil (isitishsiz 300–800 m³) | calk.uz kalkulyatori, 03.02.2026 (C) |
| Ijtimoiy me'yor | isitish mavsumida **500 m³/oy**, boshqa vaqt **100 m³/oy** | gazeta.uz 02.03.2026 va 03.03.2026 (B) |
| **EF — tabiiy gaz** | NOx **51**, CO 26, SOx 0,3, **PM2,5 1,2** g/GJ (0,7–1,7) | EMEP/EEA 2023, 1.A.4.b.i Tier 1 (A) |
| **EF — qattiq/qo'ng'ir ko'mir** | NOx 110, CO 4 600, SOx 900, **PM2,5 398** g/GJ (72–480) | o'sha jadval (A) |
| Gaz energiyasi | 1 m³ ≈ 36 MJ; ko'mir 15–25 GJ/t (baza 20) | konversiya (D) |
| Shamol (quti) | **garmonik 3,16 m/s** (arifmetik 4,82) | ERA5, isitish mavsumi, n = 2 291 (A) |

**Quti modeli:** C = Q / (L · H · u), L = 20 km, H = 300 m (200–500 sinov), u — garmonik.
Garmonik o'rtacha tanlandi, chunki C ∝ ⟨1/u⟩: sokin soatlar ko'proq vazn olishi kerak
(aks holda o'rtacha konsentratsiya **kam** baholanadi).

---

## 6. Natija: gaz isitish tushuntira olmaydi, qattiq yoqilg'i tushuntiradi

Kuzatilgan ortish: **ΔPM2,5 = 25,60 − 15,36 = +10,24 µg/m³**.

| Kattalik | Qiymat |
|---|---|
| Talab qilinadigan emissiya oqimi | **194 g/s** |
| Mavsumiy massa (2 319 soat) | **1 619 t PM2,5** |
| Gaz isitish beradigan massa | **31,7 t (2,0%)** ⇒ amalda **nol** |
| Ko'mir ekvivalenti | **203 400 t/mavsum** (±) |
| **Gaz bilan xuddi shu massani chiqarish** | **37,5 mlrd m³** — mamlakat yillik qazib olishi 42,3 mlrd m³ (2025) |
| **Kerakli qattiq yoqilg'i ulushi** | **15,2%** (energiya bo'yicha) |

**Sezgirlik (9 variant, `isitish.py`):**

| Variant | Talab, t | Qattiq ulush |
|---|---|---|
| baza (H = 300 m, u = 3,16, 2 500 m³/uy) | 1 619 | **15,2%** |
| sayoz aralashish (H = 200 m) | 1 080 | 10,0% |
| chuqur aralashish (H = 500 m) | 2 699 | 25,5% |
| shamol 2,5 / 4,0 m/s | 1 282 / 2 052 | 12,0% / 19,3% |
| 1 700 / 3 200 m³/uy | 1 619 | 22,4% / 11,8% |
| xususiy uy 25% / 45% | 1 619 | 21,5% / 11,8% |

**Xulosa:** kattalik darajasi barqaror — **o'nlik bir necha foizdan chorakgacha**. Bu «aniq raqam» emas,
lekin **tekshiriladigan** raqam: rasmiy qattiq yoqilg'i savdosi statistikasi kelishi bilan bu baho
to'g'ridan-to'g'ri tasdiqlanadi yoki rad etiladi (05.10 so'rovlari aynan shuni so'raydi).

---

## 7. Traser testi — va uning halol kuchsizligi

Qishki ortishlarning **marjinal** nisbati (ΔPM2,5 / ΔCO):

| Kattalik | Qiymat |
|---|---|
| Kuzatuv (ΔPM2,5 / ΔCO) | **0,0430** |
| Ko'mir EF nisbati (398 / 4 600) | 0,0865 → kuzatuv **0,50×** |
| Gaz EF nisbati (1,2 / 26) | 0,0462 → kuzatuv **0,93×** |
| ΔSO2 / ΔCO kuzatuv | 0,0234 ↔ ko'mir EF 0,196 (0,12×) |

Ya'ni kuzatilgan qishki «qo'shimcha» yonish **gazsimon** ko'rinadi. **Lekin** bu test kuchsiz:

1. **CO qishda uzoq yashaydi** — OH radikali kamayadi, shuning uchun ΔCO nafaqat emissiyadan, balki
   kimyoviy to'planishdan ham oshadi (maxraj shishadi → nisbat pasayadi).
2. **SO2 → sulfat** aylanadi (SO2 umri kunlar) ⇒ SO2/CO nisbati tabiiy ravishda past bo'ladi.
3. Quti modeli **meteorologiyani** (inversiya) va **ikkilamchi aerozol** kimyosini ichiga olmaydi.

Shu sababli traser testi **ko'mirni rad eta olmaydi** — faqat yuqori chegarani pasaytiradi. Bu
chegarani ochiq yozib qo'yish — «o'lchov noaniqligi» ni «xulosa» dan ajratish talabining davomi.

---

## 8. Nima isbotlanadi · nima isbotlanmaydi

**Isbotlanadi (o'lchov + manba):**
- Qishki PM2,5 ortishi **real** va **takrorlanuvchi**: 21/181 ↔ 0/183 kun, 1,67×, mintaqaviy sinxronlik r = 0,816.
- Bu ortish **IES sektoridan emas** (lift 1,21 ↔ 1,20; Angren nazorati 0,97×, 0 epizod).
- **Gaz isitish** PM2,5 ortishini **strukturaviy** tushuntira olmaydi (37,5 mlrd m³ absurdligi).
- Ortishni qoplash uchun qattiq yoqilg'i ulushi **≈10–25%** (energiya bo'yicha) bo'lishi kerak.

**Isbotlanmaydi:**
- Aniq **qattiq yoqilg'i miqdori** (tonna) — rasmiy savdo statistikasi yo'q.
- **Ikkilamchi aerozol** ulushi (nitrat/sulfat) — kimyo modeli kerak; quti modeli buni «qattiq yoqilg'i»
  deb hisoblagan bo'lishi mumkin ⇒ 15,2% — **yuqori baho**, past baho emas.
- Kunlik-aniq aybdor manba; transport va chang hissasi alohida ajratilmagan.

---

## 9. 05.10 so'rovlar to'plami — tayyor va kuzatuvda

`scripts/build_requests_2026_10.py` → **4 xat** (`data/kirishsiz/yuborishga/`), har birida R53 natijalari
bloki (6 band) **asos sifatida** keltirilgan:

| # | Manzil | So'raladi | Javob muddati | Eskalatsiya |
|---|---|---|---|---|
| 1 | Ekologiya boshqarmasi | monitoring (soatlik PM2,5/NO2/SO2 + stansiya joylari) **+ qattiq yoqilg'i savdosi** | 2026-10-20 | 2026-10-25 |
| 2 | Ekologiya inspeksiyasi | inspeksiya dalolatnomalari **+ fakel rejimi** | 2026-10-20 | 2026-10-25 |
| 3 | Obyekt (IES/issiqlik stansiyasi) | o'lchov protokollari **+ ruxsatnoma shartlari** | 2026-10-20 | 2026-10-25 |
| 4 | Statistika boshqarmasi | **gaz iste'moli oylar kesimida** + qattiq yoqilg'i + isitish bilan ta'minlangan xonadonlar | 2026-10-20 | 2026-10-25 |

Kuzatuv jurnali: `data/kirishsiz/sorovlar.jsonl` (hozir **8 yozuv, 8 javobsiz** — 4 eski + 4 yangi).
CLI: `python3 scripts/kirishsiz.py sorov --kutish` (javobsizlar va muddatlar).

---

## 10. Keyingi qadam

1. **05.10** — 4 xatni yuborish; kuzatuv 20.10 gacha (javob bo'lmasa 25.10 da Aarhus 9-modda bo'yicha eskalatsiya).
2. **10.10** — joriy isitish mavsumi boshlanishi: `kirishsiz.py mavsum` har hafta (oyna orqaga surilmaydi, oldinga uzaytiriladi).
3. **Rasmiy javob kelganda** — 15,2% bahosini haqiqiy qattiq yoqilg'i miqdori bilan solishtirish (baho tasdiqlanadi/rad etiladi).
4. **Ikkilamchi aerozol** — NOx→nitrat ulushini baholash (kimyo modeli yoki PM2,5 tarkibi o'lchovi) ⇒ 15,2% yuqori baho ekanini tekshirish.

**Yangi kod:** `src/kirishsiz/isitish.py` (12 test) · `mavsum.taqqoslash()` + `pearson()` ·
CLI `kirishsiz.py isitish` va `kirishsiz.py taqqos` · `scripts/build_requests_2026_10.py`.
**Testlar:** **287** (L1) + 193 (L2) = **480**.
