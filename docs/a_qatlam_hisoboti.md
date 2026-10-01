# 15 — A-QATLAM HISOBOTI (kirishsiz rejim, birinchi 92 kun)

**Davr:** 2026-07-01 → 2026-09-30 (2 208 soat) · **Receptor:** Toshkent markazi, 41,311°N / 69,240°E
**Hisobot sanasi:** 2026-10-01 · **Yo'l:** #7 «shamol atributsiyasi» + #6 «ochiq ekran» (`registry.PATHS`)
**Isbot kuchi:** **2** (hududiy skrining — obyekt darajasidagi xulosa bermaydi; qaror qoidasi: ≥3 kuchli ≥2 yo'l)

> **Bir jumlada:** ochiq manbalar bilan 92 kunlik tekshiruv o'tkazildi. Kunlik normadan **oshgan kun yo'q**
> (0/92), lekin **yo'nalish signali bor**: sanoat sektori shamolida NO2 va SO2 **1,7–2,5 barobar** ko'proq
> uchraydi — bu keyingi (B) qatlamga asos, ayblov emas.

---

## 1. Hisobot nima beradi (A-qatlam)

| Savol | Javob | Dalil |
|---|---|---|
| 92 kun ichida hududda norma oshgan kun bormi? | **Yo'q** — 0/92 kun (eng yuqori kunlik o'rtacha 22,49 µg/m³, norma 35) | CAMS kunlik seriyasi |
| Soatlik darajada signal bormi? | **Bor** — 108 soat (4,9%) 25 µg/m³ dan yuqori; 35 dan yuqori soat yo'q | CAMS soatlik seriyasi |
| Ifloslanish ma'lum yo'nalishdan kelayotganmi? | **Bor** — NE sektorida NO2 lift **2,45**, PM2,5 lift **2,33**, SO2 lift **1,72** | ERA5 shamol + sektor tahlili |
| Qaysi obyekt ekani aniqlanganmi? | **Yo'q** | isbot kuchi 2 — bir nechta manba bir yo'nalishda |
| Rasmiy organlar so'ralganmi? | **Ha** — 3 talab yuborishga tayyor (muddat 17.10, eskalatsiya 22.10) | `data/kirishsiz/sorovlar.jsonl` |

---

## 2. Ma'lumot va provenans (har fayl: manba + SHA-256 + litsenziya)

| Fayl | Manba (tier) | Oryolgan | SHA-256 (qisqa) | Litsenziya |
|---|---|---|---|---|
| `aq_92kun.csv` (2 208 qator) | Open-Meteo Air Quality — CAMS (D: ochiq API, jonli) | 2026-10-01 | `abf15b741808…` | CC-BY-4.0 |
| `wind_era5_92kun.csv` (2 208 qator) | Open-Meteo Archive — ERA5 (C: hujjatlashtirilgan qayta tahlil) | 2026-10-01 | `0790afd4568c…` | CC-BY-4.0 |
| `wind_92kun.csv` (1 563/2 208) | Open-Meteo Forecast shamol — **66 kun** (ishlatilmadi) | 2026-10-01 | `59d5c02f1670…` | CC-BY-4.0 |
| `MANIFEST.json` | yuklash jurnali (URL, vaqt, sha256, litsenziya) | 2026-10-01 | — | — |

**Diqqat (metodik topilma):** prognoz API'si 92 kunlik oynani **to'liq qoplamadi** (shamol 27.07 dan).
Shu sababli tarixiy shamol **ERA5 arxividan** olindi va juftlash **indeks bo'yicha emas, vaqt bo'yicha**
qilindi (`screener.dirty_hours_by_time`) — aks holda qiymatlar siljib, tahlil buzilardi (bu xato kodda
tutildi va test bilan qo'riqlandi).

---

## 3. Metodika (3 qadam, hammasi takrorlanadigan)

1. **Kunlik ekran** — soatlik PM2,5 → kunlik o'rtacha (qamrov ≥75% sharti) → SanQvaM 0053-23 normasi
   (35 µg/m³) bilan solishtirish.
2. **Soatlik juftlash** — 25 µg/m³ dan yuqori soatlar **aynan shu vaqtdagi** ERA5 shamol yo'nalishi bilan
   bog'lanadi; shamoli yo'q soatlar sanaladi (qamrov ko'rsatkichi).
3. **Sektor boyitilishi (lift)** — yuqori 10% soatlarda berilgan yo'nalish (±45°) ulushi fon ulushiga
   bo'linadi: `lift = yuqori ulush / fon ulush`. `lift ≥ 1,5` — signal; `1,15–1,5` — kuchsiz; `< 1,15` — yo'q.

---

## 4. Natijalar

### 4.1. 92 kunlik daraja

| Ko'rsatkich | PM2,5 | NO2 |
|---|---|---|
| O'rtacha | **13,27** µg/m³ | 12,99 µg/m³ |
| Mediana | 12,40 | 12,10 |
| P90 / P95 | 22,10 / 24,90 | 27,30 / 29,90 |
| Maksimal (soatlik) | **32,90** | 39,70 |
| Soatlar > 25 µg/m³ | 108 (4,9%) | — |
| Soatlar > 35 µg/m³ | **0** | — |
| Kunlik norma oshgan kunlar | **0 / 92** | — |

### 4.2. Yo'nalish tahlili (lift) — uch nomzod sektori bo'yicha

| Nomzod (taxminiy nuqta) | Azimut / masofa | PM2,5 lift | NO2 lift | SO2 lift | PM10 lift |
|---|---|---|---|---|---|
| Sement zavodi sektori | 42,6° · 7,40 km | **2,33** | **2,45** | **1,72** | 1,09 |
| IES sektori | 126,4° · 11,42 km | 1,23 | 1,91 | 0,60 | — |
| G'isht zavodi sektori | 211,4° · 14,45 km | 0,62 | 0,35 | 0,98 | — |

**Shamollanish guli (ERA5, n=2 208):** NW 19% · SE 17% · W 17% — fon ulushi 42,6° sektorida 12,9%.

**O'qish:** yonish belgilari (NO2, SO2) NE/SE sektorlarida boyitilgan, **chang (PM10) esa yo'q** —
bu shahar changi (yo'l, qurilish, cho'l) regional ekanini ko'rsatadi va kuzatuvni aynan yonish
manbalariga qaratish kerakligini bildiradi.

### 4.3. Nazorat tekshiruvi — model vs stansiya (halollik uchun)

CAMS model hujayrasi (10–25 km) shahar ichidagi stansiyalardan **past** ko'rsatadi: bizning 92-kunlik
o'rtacha 13,27 µg/m³, holbuki 2024-yil stansiya ma'lumotlari asosida Toshkent bo'yicha yillik o'rtacha
**38,8 µg/m³** qayd etilgan (WB/kun.uz, 09.10.2024). **Xulosa:** modeldan faqat **nisbiy/yo'nalish**
signali olinadi; mutlaq daraja bo'yicha «norma buzilgan/buzilmagan» xulosasi **qilinmaydi**.

---

## 5. Nima isbotlanadi / nima isbotlanmaydi

| Da'vo | Holat |
|---|---|
| Hududda o'lchangan davrda kunlik norma oshmagan (model bo'yicha) | ✅ aytish mumkin (0/92) |
| Yuqori soatlar ma'lum sektorga bog'langan | ✅ skrining signali (lift 1,7–2,5) |
| Sabab — **aynan** NE sektoridagi obyekt | ❌ isbotlanmaydi (bir nechta manba; chang manbasi boshqa) |
| **Qaysi korxona** aybdor | ❌ isbotlanmaydi (A-qatlam hech qachon buni aytmaydi) |
| Norma umuman buzilmayapti (shahar bo'ylab) | ❌ noto'g'ri xulosa bo'lardi — model past baholaydi |

---

## 6. Rasmiy talablar holati (yo'l #1, isbot kuchi 5)

| # | Tashkilot | Tur | Fayl | Javob muddati | Eskalatsiya |
|---|---|---|---|---|---|
| 1 | Ekologiya, atrof-muhitni muhofaza qilish va iqlim o'zgarishi vazirligi | o'lchovlar | `sorov_-_olchov.txt` | **2026-10-17** | 2026-10-22 |
| 2 | Toshkent shahar ekologiya boshqarmasi | monitoring | `sorov_-_monitoring.txt` | **2026-10-17** | 2026-10-22 |
| 3 | Gidrometeorologiya xizmati agentligi (Hydromet) | inspeksiya | `sorov_-_inspeksiya.txt` | **2026-10-17** | 2026-10-22 |

Asos: Konstitutsiya 49-modda · Aarhus konventsiyasi 4-modda (O'zbekiston uchun kuchga kirgan
**25.08.2025**) · davlat organlari faoliyatining ochiqligi to'g'risidagi qonun. Javob **15 kun**
(qo'shimcha o'rganishda 1 oygacha). Javob bo'lmasa — 9-modda yo'li (apellyatsiya).
⚠ Yuborishdan oldin: tashkilot nomlari/manzillari va imzo shaxsi tasdiqlanadi (`⟦…⟧` maydonlar).

---

## 7. TZ-1 bilan bog'lanish

- **Ilova K** (kirishsiz rejim) endi amalda sinaldi: A-qatlam ishlaydi va raqam beradi.
- **T7 «Natija shakli»** jadvaliga «**A/B qatlam (kirishsiz)**» ustuni qo'shiladi: yo'l ID · isbot kuchi ·
  baholangan qiymat/oraliq · sana. Ustun bo'sh qolsa — sabab yoziladi.
- **T1** o'zgargan maqsadi (ruxsat emas — **talab + muddat**) amalda: 3 talab, 15 kunlik nazorat jadvali.

---

## 8. Qayta ishlab chiqarish (aynan shu buyruqlar)

```bash
cd 01-Loyiha1-Carbon-Emission/MVP
python3 scripts/fetch_public.py --source open-meteo-aq     --lat 41.311 --lon 69.240 --kun 92 --out data/public/aq_92kun.csv
python3 scripts/fetch_public.py --source open-meteo-archive --lat 41.311 --lon 69.240 \
        --boshlanish 2026-07-01 --tugash 2026-09-30 --out data/public/wind_era5_92kun.csv
python3 scripts/kirishsiz.py ekran  --kun 92 --shamol-fayl data/public/wind_era5_92kun.csv \
        --obyekt "Sement zavodi:41.36:69.30" --obyekt "IES:41.25:69.35"
python3 scripts/kirishsiz.py sektor --fayl data/public/aq_92kun.csv \
        --shamol-fayl data/public/wind_era5_92kun.csv --obyekt "Sement zavodi:41.36:69.30" \
        --modda pm2_5,pm10,no2,so2
python3 scripts/kirishsiz.py sorov --tashkilot "…" --tur olchov --sana 2026-10-02
```

---

## 9. Keyingi qadamlar (B qatlamga o'tish)

| # | Qadam | Muddat | Kutilgan natija |
|---|---|---|---|
| 1 | So'rovlarni yuborish va muddatni yuritish | 02–05.10 | Rasmiy hujjat (kuch 5) yoki apellyatsiya asosi |
| 2 | Nomzod koordinatalarini rasmiy manbadan olish (gis.uznature.uz) | 05–10.10 | «Taxminiy» → aniq nuqta |
| 3 | Oynani 180 kunga uzaytirish + isitish mavsumi (oktabr–fevral) | 10–20.10 | Yonish signalining mavsumiy tasdig'i |
| 4 | FIRMS MAP_KEY → obyekt hududida yonish nuqtalari (yo'l #4) | 10–15.10 | Mash'al/yonish dalili |
| 5 | Pastdan-yuqoriga oraliq (yo'l #2): ishlab chiqarish × ELV | 15–25.10 | Hisobot mustaqil bahoga sig'adimi |
| 6 | Transsekt kampaniyasi rejasi (yo'l #5) | 25–31.10 | Q ± oraliq (o'lchov) |

---

## 10. Manbalar (sana va tier bilan)

| # | Manba | Nima uchun | Sana | Tier |
|---|---|---|---|---|
| 1 | [Open-Meteo Air Quality API](https://air-quality-api.open-meteo.com) | PM2,5/NO2/SO2/CO soatlik seriya — **jonli olindi** | 2026-10-01 | D |
| 2 | [Open-Meteo Archive API (ERA5)](https://archive-api.open-meteo.com) | Tarixiy shamol (10 m) — **jonli olindi** | 2026-10-01 | C |
| 3 | SanQvaM 0053-23 · [Hydromet izohi](https://hydromet.uz) | PM2,5 kunlik norma 35 µg/m³ | kuchda | A |
| 4 | [kun.uz/WB — Toshkent havosi, 38,8 µg/m³](https://kun.uz) | Model–stansiya farqi (nazorat) | 2024-10-09 | B |
| 5 | Aarhus konventsiyasi · UNECE MoP bayonoti | Kuchga kirish **25.08.2025** | 2026-01-05 | A |
| 6 | Konstitutsiya 49-modda · murojaat tartibi | **15 kun** muddati | amalda | A |
| 7 | Varon et al., AMT 11:5673 (2018) | Sektor/atributsiya yondashuvi | 2018 | C |
| 8 | `MANIFEST.json` (workspace) | Har faylning SHA-256 va litsenziyasi | 2026-10-01 | — |

---

**Hisobot oxiri.** Kod: `src/kirishsiz/sector.py` + `screener.py` · CLI: `scripts/kirishsiz.py ekran|sektor` ·
Testlar: `tests/test_kirishsiz_sector.py` (20) · Hammasi qayta ishlab chiqariladi (§8).
