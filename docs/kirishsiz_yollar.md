# 13 — KIRISHSIZ YO'LLAR (ruxsatsiz tekshiruv rejimi)

**Sana:** 2026-10-01 · **Holat:** ishlaydigan kod + jonli tekshiruv · **Kod:** `01-Loyiha1-Carbon-Emission/MVP/src/kirishsiz/`
**Sabab (foydalanuvchi, R47):** «realligini inobatga old — korxona bizga kirishga ruxsat bermaydi, shuning uchun boshqa usullarni ko'rib chiq va ustida ishla».

> **Bir jumlada:** pilotning **T1–T7** zanjiri korxona ichidagi ma'lumotga (D1–D5) tayanadi — ruxsat
> berilmasa zanjir uziladi. Bu hujjat uzilishni **ochiq manbalar + huquqiy talab** bilan qoplaydigan
> **8 yo'lni** kod, test va jonli natija bilan beradi — va har birining **nima isbotlab, nima
> isbotlamasligini** ochiq yozadi.

---

## 1. Uzilish nimada — aniq ro'yxat

| TZ-1 bosqichi | Nima kerak edi | Ruxsatsiz holat | Yo'qoladigan narsa |
|---|---|---|---|
| T1 | Memorandum, mas'ul mutaxassis | Xat yuboriladi, javob yo'q | `D3/D4` (uskuna jurnali, oqim o'lchagich) |
| T2/T3 | CEMS + etalon solishtiruv | **Bajarilmaydi** | Taqsimot, kvantil, MAD — asosiy natija |
| T4 | 8 haftalik oyna | **Bajarilmaydi** | Mavsumiy qamrov |
| T5 | Obyektga kirish (etalon) | **Bajarilmaydi** | «U» (noaniqlik) maydoni |
| T6/T7 | Uch zona jadvali | Faqat **kirishsiz** natijalardan | Obyekt darajasidagi xulosa |

**Xulosa:** «kutish» strategiyasi muddatni yo'qotadi. Shuning uchun isbot zanjiri **parallel**
quriladi: qaysi yo'l bugun ishlaydi — shundan boshlanadi.

---

## 2. Sakkiz yo'l — xarita (kodda: `registry.PATHS`)

| # | ID | Yo'l | Asosiy manba | Isbot kuchi | Kirish | Holat |
|---|---|---|---|---|---|---|
| 1 | `huquqiy-talab` | Ma'lumotni ochish talabi (so'rash emas — **talab**) | Aarhus 4-modda · Konstitutsiya 49 · 15 kun | **5** | kerak emas | ✅ kod + shablon |
| 2 | `pastdan-yuqoriga` | Faoliyat × koeffitsient → oraliq | EMEP/EEA 2023 (2 300 Nm³/t kl · 0,90) · stat.uz · xarid.uzex | **4** | kerak emas | ✅ kod + testlar |
| 3 | `orbita` | Qatlam og'ishi → oqim (kg/s) | TROPOMI (5,5×3,5 km) · Carbon Mapper | **3** | kerak emas | ✅ kod (CSF/IME) + chegarasi |
| 4 | `issiqlik-mashal` | Yonish/mash'al nuqtalari | NASA FIRMS (VIIRS 375 m) | **3** | kerak emas | ✅ fetch (MAP_KEY bepul) |
| 5 | `yol-transsekti` | Umumiy yo'lda mobil o'lchov → Q | Gauss teskari masala · SanQvaM | **3** | kerak emas | ✅ kod + testlar |
| 6 | `ochiq-havo` | Hududiy fon, normadan oshgan kunlar | Open-Meteo (CAMS) · SanQvaM 0053-23 | 2 | kerak emas | ✅ **jonli ishlaydi** |
| 7 | `shamol-atributsiya` | «Yuqori tomon»dagi nomzodlar | ERA5 shamol · gis.uznature.uz | 2 | kerak emas | ✅ **jonli ishlaydi** |
| 8 | `statistik-skrining` | Benford / dumaloq raqam signali | Nigrini (2012) mezonlari | 1 | kerak emas | ✅ kod + testlar |

**Qaror qoidasi (`registry.conclusion_rule`):** xulosa uchun **kuchi ≥3 bo'lgan kamida 2 mustaqil yo'l**
(yoki 5-kuchli rasmiy hujjat) kerak. Bitta 1–2 kuchli yo'l bilan «obyekt aybdor» deb aytilmaydi.

---

## 3. Uch qatlamli rejim — muddat bilan

| Qatlam | Muddat | Yo'llar | Kutilgan natija | Nima isbotlaydi |
|---|---|---|---|---|
| **A — bugun** | 0–4 hafta | 1 + 6 + 7 (+8) | Hududiy ekran, nomzodlar reytingi, so'rovlar yuborilishi, 15 kunlik muddatlar | «Muammo bor va u shu yo'nalishda» + rasmiy javob talabi |
| **B — 1–3 oy** | 1–3 oy | 2 + 3 + 4 | Oraliq mosligi, oqim bahosi (kg/s · t/y), yonish nuqtalari | «Obyekt hisoboti mustaqil bahoga sig'maydi» (kuch 3–4) |
| **C — 2–4 oy** | 2–4 oy | 5 + (T1–T7 qaytishi) | Yo'l o'lchovi Q (±oraliq), ehtimol to'liq pilot | O'lchangan quvvat + rasmiy hujjat (kuch 5) |

**Muhim:** qatlamlar **ketma-ket emas, parallel** — B ishlab turgan paytda A ning so'rovi muddati ham o'tadi,
shu bilan eskalatsiya huquqi paydo bo'ladi (Aarhus 9-modda yo'li).

---

## 4. Nima isbotlanadi / nima isbotlanmaydi (halol jadval)

| Da'vo | A+B qatlam bilan | To'liq pilot (T1–T7) bilan |
|---|---|---|
| Hududda norma oshgan kunlar bor | ✅ (model, ±30–50%) | ✅ (stansiya) |
| Manba shu **yo'nalishda** | ✅ (nomzod, bir necha bo'lishi mumkin) | ✅ |
| **Shu obyekt** hisoboti bilan mustaqil baho mos emas | ⚠️ ehtimol (kuch 3–4) | ✅ |
| O'lchov noaniqligi **U** (k=2) | ❌ (etalon kerak) | ✅ |
| Yuridik jihatdan isbotlangan huquqbuzarlik | ❌ | ⚠️ faqat nazorat organi xulosasi bilan |

Shu jadval hujjatning **eng muhim qismi**: u «kuchli ko'rinadigan, lekin bo'sh» dalil qurishni to'sadi.

---

## 5. Jonli natija (2026-10-01, Toshkent markazi 41,311/69,240)

**A-qatlam 1-bosqichi — hududiy ekran** (kalitsiz, ochiq API'dan, 7 kun):

| Kun | PM2,5 (kunlik, µg/m³) | Qamrov |
|---|---|---|
| 2026-09-24 | 14,59 | 100% |
| 2026-09-25 | 16,91 | 100% |
| 2026-09-26 | 9,54 | 100% |
| 2026-09-27 | 12,42 | 100% |
| 2026-09-28 | 16,55 | 100% |
| 2026-09-29 | 14,30 | 100% |
| 2026-09-30 | **20,88** | 100% |

Norma **35 µg/m³** (SanQvaM 0053-23, kunlik o'rtacha) → **oshgan kun yo'q** (0/7), eng yuqori 20,88.
Ya'ni **bu oynada hududiy signal yo'q** — bu ham natija: keyingi qadam oynani (kunlarni, joyni)
kengaytirish yoki boshqa moddaga (NO2/SO2) o'tish.

**A-qatlam 2-bosqichi — atributsiya sinovi** (soatlik chegara test maqsadida 25 µg/m³ ga tushirilganda,
22 soat ajraldi; 3 ta taxminiy nomzod):

| Nomzod | «Yuqori tomon» soatlari | O'rt. burchak xatosi | Masofa |
|---|---|---|---|
| Sement zavodi (taxminiy nuqta) | 11 soat (50%) | 23,8° | 7,4 km |
| IES (taxminiy nuqta) | 9 soat (41%) | 26,8° | 11,4 km |
| Boshqa zavod | 4 soat (18%) | 20,1° | 14,5 km |

⚠ Tizim o'zi ogohlantiradi: **«Bir nechta manba bir yo'nalishda — ajratish mumkin emas (isbot kuchi 2)».**
Bu — halol xulosa: atributsiya *nomzod* beradi, *ayblov* bermaydi.

---

## 6. Kod, CLI va testlar

**Paket:** `src/kirishsiz/` — `registry.py` · `bands.py` · `benford.py` · `plume.py` · `transect.py` ·
`screener.py` · `requests_gen.py` (7 modul, 1 500+ satr).
**Skriptlar:** `scripts/fetch_public.py` (kalit/provenans jurnali bilan) · `scripts/kirishsiz.py` (CLI).

```bash
cd 01-Loyiha1-Carbon-Emission/MVP
python3 scripts/kirishsiz.py --list                          # 8 yo'l + qaror qoidasi
python3 scripts/kirishsiz.py ekran --lat 41.311 --lon 69.240 --kun 7 \
        --obyekt "Sement:41.36:69.30" --obyekt "IES:41.25:69.35"   # JONLI (kalitsiz)
python3 scripts/kirishsiz.py band --faoliyat 1200000 --elv-low 500 --elv-high 1200 --elv-report 900
python3 scripts/kirishsiz.py benford --fayl data/public/olchovlar.csv
python3 scripts/kirishsiz.py orbita --kesim 0.001,0.002,0.0015 --shamol 3.2 --dx 3500 --sinov
python3 scripts/kirishsiz.py transsect --c 1.2e-6 --shamol 2.8 --sigma-z 22 --h 8 --reja-target 0.2
python3 scripts/kirishsiz.py sorov --tashkilot "Ekologiya boshqarmasi" --tur olchov   # huquqiy talab
python3 scripts/fetch_public.py --check                      # manbalar mavjudligi
```

**Manbalar tekshiruvi (`fetch_public.py --check`, 2026-10-01):** 5/6 javob berdi —
Open-Meteo havo sifati ✅ · shamol ✅ · ERA5 arxivi ✅ · FIRMS sahifasi ✅ · Carbon Mapper hujjati ✅ ·
OpenAQ **401** (bepul kalit kerak — hujjatda shunday yozilgan).
Har bir yuklash `data/public/MANIFEST.json` ga **URL + vaqt + SHA-256 + litsenziya** bilan yoziladi.

**Testlar:** `tests/test_kirishsiz.py` — **51 test** (reyestr, oraliq hisobi, Benford χ²/MAD,
CSF/IME, transsekt inversiyasi, ekran, huquqiy talab va kuzatuv). Jami L1: **141 test**.

---

## 7. Huquqiy qatlam — nima uchun bu «so'rov» emas, «talab»

| Sana | Hujjat | Ma'nosi |
|---|---|---|
| 2025-03-11 | Qonun imzolandi (Aarhus'ga qo'shilish) | gazeta.uz, 18.03.2025 |
| **2025-08-25** | **Aarhus kuchga kirdi** (O'zbekiston uchun) | UNECE MoP bayonoti, 2026-01-05 |
| — | Konstitutsiya 49-modda | «ishonchli axborot olish huquqi» |
| 2014-05-05 | Ochiqlik to'g'risidagi qonun | axborot olish tartibi |
| — | Murojaat muddati | **15 kun** (qo'shimcha o'rganishda — 1 oy) |

Shu asosda `requests_gen.build_request()` 5 turdagi so'rovni (o'lchovlar, inspeksiya dalolatnomalari,
ruxsatnoma shartlari, monitoring stansiyalari, mash'al rejimi) **muddat kuzatuvi** bilan yaratadi:
javob sanasi (15-kun) va eskalatsiya sanasi (+5 kun) avtomatik hisoblanadi.
Rad javobi ham **dalil**: u asosini apellyatsiyada tekshirish yo'lini ochadi (Aarhus 9-modda).

---

## 8. Xatarlar (halol ro'yxat)

| Xatar | Ehtimol | Kamaytirish |
|---|---|---|
| CAMS hujayrasi yirik (10–25 km) → obyekt ajralmaydi | Yuqori | Faqat **signal** sifatida ishlatish (kuch 2); obyekt uchun orbita + transsekt |
| TROPOMI kichik manbani ko'rmaydi | Yuqori | Pastdan-yuqoriga (kuch 4) bilan qoplash; katta manbalarga ustuvorlik |
| `σ_z` model xatosi (±40–70%) | O'rta | Ko'p o'tish + fon o'lchovi; mustaqil usul bilan kesishma |
| So'rov «savdo siri» bilan rad etilishi | O'rta | Rad javobi → 9-modda apellyatsiyasi; rad sababini ochish talabi |
| FIRMS hujayrasi 375 m, maydon tegishliligi | O'rta | Faqat obyekt hududidagi nuqtalar + vaqt kesishmasi |
| Ma'lumot «ochiq, lekin ko'rsatilmagan» | O'rta | Har yuklamada litsenziya + SHA-256 (provenans) yoziladi |

---

## 9. TZ-1 ga ta'siri (nima o'zgaradi)

1. **T1 qoladi**, lekin uning maqsadi o'zgaradi: «ruxsat olish» → **«talab yuborish va muddatni yuritish»**
   (`requests_gen` + kuzatuv jurnali).
2. TZ-1 ga **Ilova K** qo'shiladi: kirishsiz rejim shartlari, 8 yo'l, qaror qoidasi (quyida).
3. **T4 oynasi (07.12.2026)** ruxsatga bog'liq bo'lmagan qism bilan boshlanadi: A-qatlam (ekran +
   so'rovlar) shu sanada allaqachon 2 oylik tarixga ega bo'ladi.
4. Himoyada **ikki variant** ko'rsatiladi: (a) to'liq pilot (ruxsat olinsa), (b) A+B qatlam
   (ruxsat bo'lmasa) — ikkalasi ham bir xil «U va ishonch» mantiqiga xizmat qiladi.

---

## 10. Keyingi 10 qadam

| # | Qadam | Muddat | Natija |
|---|---|---|---|
| 1 | So'rovlarni 3 tashkilotga yuborish (Turar joy/ekologiya/prokuratura nazorati) | 02–05.10 | 3 muddat kuzatuvda |
| 2 | Ekran oynasini 92 kunga uzaytirish (`--kun 92`) + PM2,5 + NO2 | 06–08.10 | Hududiy tarix |
| 3 | Nomzodlar ro'yxatini gis.uznature.uz dan rasmiy koordinatalar bilan almashtirish | 09–12.10 | Atributsiya bazasi |
| 4 | FIRMS kaliti olish + obyekt hududida yonish nuqtalari | 09–12.10 | 4-yo'l ishga tushadi |
| 5 | Pastdan-yuqoriga: 3 nomzod uchun ELV/ishlab chiqarish ma'lumoti yig'ish | 13–20.10 | Oraliqlar |
| 6 | Birinchi orbita oynasi (TROPOMI SO2/NO2) uchun hisob va skript | 20–27.10 | Oqim bahosi |
| 7 | Transsekt kampaniyasi rejasi (10–30 o'tish, yo'l marshruti) | 27–31.10 | Q ±oraliq |
| 8 | So'rovlarga javob bo'lmasa — 9-modda apellyatsiyasi matni | 01–05.11 | Eskalatsiya |
| 9 | A-qatlam hisoboti (2 oylik) TZ-1 T7 shabloniga kiritish | 05–10.11 | «Kirishsiz natija» varaqasi |
| 10 | T1 xatini qayta yuborish (yangi dalillar bilan) | 10–12.11 | Ruxsat ehtimoli oshadi |

---

## 11. Manbalar (har biri sana va daraja bilan)

| # | Manba | Nima uchun | Sana | Tier |
|---|---|---|---|---|
| 1 | [UNECE — O'zbekiston Aarhus'ga qo'shildi](https://unece.org/biodiversity/press/uzbekistan-accedes-aarhus-convention-empowering-public-shape-clean-healthy-and) | Qo'shilish fakti, 48 tomon | 2025-03-28 | A |
| 2 | [UNECE MoP bayonoti (PDF)](https://unece.org/sites/default/files/2026-01/5Jan26_Aarhus%20ECO%20Forum%20NGO%20statements.pdf) | **Kuchga kirish sanasi 25.08.2025** | 2026-01-05 | A |
| 3 | [gazeta.uz — Aarhus](https://www.gazeta.uz/en/2025/03/18/aarhus-convention/) | Qonun imzolanishi, 49-modda izohi | 2025-03-18 | A |
| 4 | [ICNL — Civic Freedom Monitor (UZ)](https://www.icnl.org/resources/civic-freedom-monitor/uzbekistan) | Qonun raqami (ZRU-1045), EIA qonuni | 2026-05-06 | A |
| 5 | [constitution.uz — murojaat huquqi](https://constitution.uz/oz/pages/murojaat_huquq) | **15 kun** muddati | 2026-10-01 tekshirildi | A |
| 6 | [NASA Earthdata — TROPOMI NO2 L2](https://www.earthdata.nasa.gov/data/catalog/ges-disc-s5p-l2-no2-hir-nrt-2) | 5,5×3,5 km, bepul | 2026-09-23 | B |
| 7 | [Digital Earth Africa — Sentinel-5P spetsifikatsiyasi](https://docs.digitalearthafrica.org/en/latest/data_specs/Sentinel-5P_specs.html) | Kundalik qamrov, SO2/CH4/CO | 2026 | B |
| 8 | [Carbon Mapper — ma'lumot portali](https://carbonmapper.org/articles/updated-carbon-mapper-data-portal) | Ochiq metan kuzatuvlari | hujjat | B |
| 9 | [NASA FIRMS — area API](https://firms.modaps.eosdis.nasa.gov/api/map_key/) | Bepul MAP_KEY, VIIRS | 2026-10-01 | B |
| 10 | [Open-Meteo havo sifati (CAMS)](https://air-quality-api.open-meteo.com) | Kalitsiz API — **jonli sinaldi** | 2026-10-01 | D |
| 11 | [OpenAQ — rate limit hujjati](https://docs.openaq.org/using-the-api/rate-limits) | Kalit talabi, 60/min | 2026-10-01 | D |
| 12 | [EMEP/EEA Guidebook 2023, 2.A.1](https://www.eea.europa.eu/publications/emep-eea-guidebook-2023/part-b-sectoral-guidance-chapters/2-industrial-processes-and-product-use/2-a-mineral-products/2-a-1-cement-production-2023) | 2 300 Nm³/t kl · 0,90 kl faktor | 2023 | C |
| 13 | [Varon et al. 2018, AMT 11:5673](https://doi.org/10.5194/amt-11-5673-2018) | CSF/IME usullari, aniqlik | 2018 | C |
| 14 | [NIST IR 8575 (2025)](https://nvlpubs.nist.gov/nistpubs/ir/2025/NIST.IR.8575.pdf) | IME/CSF amaliyoti, Q_min g'oyasi | 2025-05-05 | C |
| 15 | [Nigrini MAD mezonlari (Springer, 2026)](https://link.springer.com/article/10.1007/s00181-025-02876-0) | 0,006/0,012/0,015; χ² 15,507 | 2026-02-04 | C |
| 16 | [Nature (2025) — poligon metan tadqiqoti](https://www.nature.com/articles/s41586-025-09683-8) | ~100 kg/soat sezish chegarasi | 2025-11-05 | C |

---

**Hujjat oxiri.** Kod: `src/kirishsiz/` · CLI: `scripts/kirishsiz.py` · Testlar: `tests/test_kirishsiz.py` (51).
Har bir da'vo manba + sana + tier bilan; isbot kuchi raqam bilan; «nima isbotlanmaydi» har yo'lda yozilgan.
