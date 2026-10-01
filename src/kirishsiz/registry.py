# -*- coding: utf-8 -*-
"""Kirishsiz yo'llar reyestri — 8 yo'l, har biri manba + huquqiy asos + isbot kuchi bilan.

«Isbot kuchi» (1–5) — **shu yo'l yakka o'zi qanday da'voni ko'tara oladi**:
  1 — faqat signal/qiziqish («bu yerda nima bo'layotganini bilish kerak»)
  2 — hududiy/skrining: «hududda muammo bor, manba bir nechta bo'lishi mumkin»
  3 — yarim obyekt: «manba shu obyekt bo'lishi ehtimoli yuqori / oraliq mos emas»
  4 — obyekt darajasi: «obyekt hisoboti bilan mustaqil baho bir-biriga sig'maydi»
  5 — rasmiy hujjat: «davlat organi yozma javobida raqamni tasdiqladi»

Hech bir yo'l **yakkasicha** jarima/oqlamaga asos bo'lmaydi: 3+ kuchdagi kamida ikkitasi
yoki 5-kuchli hujjat kerak (qaror qoidasi `min_power_for_conclusion`).
"""
from __future__ import annotations

import json
from typing import Any

# ------------------------------------------------------------------ manba toifalari

MANBA_TIER = {
    "A": "rasmiy ochiq reyestr/davlat tizimi (qonuniy ochiq)",
    "B": "xalqaro dastur/agentlik ochiq ma'lumoti (ESA/NASA/EEA/UNECE)",
    "C": "ilmiy maqola yoki uslubiy qo'llanma (peer-review/guidebook)",
    "D": "ochiq API/portal (kalitsiz yoki bepul kalit bilan)",
}

PATHS: list[dict[str, Any]] = [
    {
        "id": "ochiq-havo",
        "nomi": "Hududiy fon va normadan oshish kunlari (ochiq havo sifati)",
        "nima_qilinadi": "Ochiq API'dan PM2.5/NO2/SO2 soatlik qatorlari olinadi (CAMS asosida), "
                         "kunlik o'rtachalar hisoblanadi va SanQvaM 0053-23 normalari bilan "
                         "solishtirib «normadan oshgan kunlar» statistikasi chiqariladi.",
        "manba": [
            {"nom": "Open-Meteo Air Quality (CAMS)", "url": "https://air-quality-api.open-meteo.com", "tier": "D",
             "kalit": "kerak emas", "tekshirilgan": "2026-10-01 (jonli javob olindi)"},
            {"nom": "OpenAQ v3", "url": "https://api.openaq.org/v3", "tier": "D",
             "kalit": "X-API-Key (bepul ro'yxat)", "tekshirilgan": "hujjat, 2026-10-01"},
            {"nom": "SanQvaM 0053-23 normalari", "url": "https://lex.uz", "tier": "A", "kalit": "—"},
        ],
        "huquqiy_asos": "Konstitutsiya 49-modda (ishonchli ekologik axborot olish huquqi); "
                        "Aarhus konventsiyasi (O'zbekiston uchun 25.08.2025 dan kuchga kirgan) 4-modda.",
        "kirish_kerak": False,
        "isbot_kuchi": 2,
        "aniqlik": "soatlik model qatori; hujayra ~10–25 km (CAMS), shuning uchun **obyektga bog'lab bo'lmaydi**",
        "kadans": "kunlik (5 kun prognoz + 92 kun tarix)",
        "kod": "scripts/kirishsiz.py (ekran) · scripts/fetch_public.py --source open-meteo-aq",
        "cheklov": "Model mahsuloti (stansiya emas): komponent ulushi ~±30–50%. Faqat «hududda muammo bor» deydi, "
                   "«kim aybdor» degan savolga javob bermaydi.",
    },
    {
        "id": "shamol-atributsiya",
        "nomi": "Shamol yo'nalishi bo'yicha «yuqori tomon» atributsiyasi",
        "nima_qilinadi": "Oshgan soatlarda shamol qayerdan esayotgani aniqlanib, o'sha yo'nalishdagi nomzod "
                         "obyektlar (ochiq reyestrdagi koordinatalar) burchak xatosi va masofa bilan tartiblanadi.",
        "manba": [
            {"nom": "Open-Meteo/ERA5 shamol", "url": "https://api.open-meteo.com", "tier": "D",
             "kalit": "kerak emas", "tekshirilgan": "2026-10-01 (jonli)"},
            {"nom": "gis.uznature.uz (obyekt koordinatalari)", "url": "https://gis.uznature.uz", "tier": "A"},
        ],
        "huquqiy_asos": "Aarhus 4-modda (ochiq reyestrlar); PQ-343 (18.11.2025) — yagona platforma 01.09.2026.",
        "kirish_kerak": False,
        "isbot_kuchi": 2,
        "aniqlik": "burchak ±10–20°, masofa ±50 m; shamol 10 m balandlikda (mo'ri 40+ m) — siljish bor",
        "kadans": "kunlik",
        "kod": "kirishsiz.screener.attribute_hours · kirishsiz.sector.directional_enrichment",
        "cheklov": "Bir nechta manba bir yo'nalishda bo'lsa ajratilmaydi — «nomzod», «aybdor» emas.",
    },
    {
        "id": "orbita",
        "nomi": "Sun'iy yo'ldosh o'lchovi: qatlam og'ishi → oqim (kg/s)",
        "nima_qilinadi": "TROPOMI (SO2/NO2/CH4) yoki yuqori aniqlikdagi (GHGSat/Carbon Mapper) yozuvlardan "
                         "qatlam og'ishi olinadi; IME/kesim oqimi usuli bilan manba quvvati (kg/s · t/y) baholanadi.",
        "manba": [
            {"nom": "Sentinel-5P TROPOMI L2", "url": "https://dataspace.copernicus.eu", "tier": "B",
             "kalit": "bepul hisob (OAuth)", "tekshirilgan": "NASA Earthdata katalogi, 2026-09-23"},
            {"nom": "Carbon Mapper portali (API hujjati)", "url": "https://api.carbonmapper.org/api/v1/docs", "tier": "B",
             "kalit": "hujjat ochiq (200); aniq endpoint yo'li tekshirilmoqda", "tekshirilgan": "2026-10-01"},
        ],
        "huquqiy_asos": "Copernicus ochiq litsenziyasi; ESA/NASA ochiq ma'lumot siyosati (manba ko'rsatiladi).",
        "kirish_kerak": False,
        "isbot_kuchi": 3,
        "aniqlik": "TROPOMI hujayra 5,5×3,5 km (nadir) — yirik manbalar uchun; oqim bahosi ±30–60%",
        "kadans": "kunlik (TROPOMI), kamdan-kam (GHGSat/Carbon Mapper)",
        "kod": "kirishsiz.plume.ime_flux / csf_flux",
        "cheklov": "Kichik manba (masalan bitta o'choq) TROPOMI hujayrasida yo'qoladi; bulut qoplami oynani kesadi.",
    },
    {
        "id": "issiqlik-mashal",
        "nomi": "Fakel/mash'al va yonish nuqtalari (issiqlik anomaliyasi)",
        "nima_qilinadi": "NASA FIRMS (VIIRS 375 m) maydon so'rovi bilan obyekt atrofidagi yonish/fakel nuqtalari "
                         "sanaladi — e'lon qilinmagan yonishning dalili.",
        "manba": [
            {"nom": "NASA FIRMS area API", "url": "https://firms.modaps.eosdis.nasa.gov/api/area/", "tier": "B",
             "kalit": "bepul MAP_KEY (email)", "tekshirilgan": "FIRMS hujjati, 2026-10-01"},
        ],
        "huquqiy_asos": "NASA ochiq ma'lumot (public domain) — manba ko'rsatish bilan.",
        "kirish_kerak": False,
        "isbot_kuchi": 3,
        "aniqlik": "375 m nuqta ~0,5 ga maydon; kichik mash'allar sezilmaydi, chang/issiq yuza yolg'on signal beradi",
        "kadans": "kuniga 2–4 o'tish",
        "kod": "scripts/fetch_public.py --source firms",
        "cheklov": "«Yonish bor» ≠ «ruxsatsiz». Nuqta obyekt hududida bo'lsa ham, tegishlilik alohida o'lchanadi.",
    },
    {
        "id": "pastdan-yuqoriga",
        "nomi": "Pastdan yuqoriga oraliq hisobi (faoliyat × koeffitsient)",
        "nima_qilinadi": "Ochiq statistika (ishlab chiqarish hajmi, yoqilg'i xaridi) va normativ gaz hajmi (ELV × Nm³/t) "
                         "asosida kutilgan yillik tashlanma **oraliqi** hisoblanadi; hisobot qiymati shu oraliqqa "
                         "sig'ish-sig'masligi tekshiriladi.",
        "manba": [
            {"nom": "EMEP/EEA Guidebook 2023, 2.A.1 (sement)", "url": "https://www.eea.europa.eu/publications/emep-eea-guidebook-2023",
             "tier": "C", "tekshirilgan": "2026-10-01 (2 300 Nm³/t klinker · 90% klinker ulushi)"},
            {"nom": "stat.uz / ochiq e'lonlar", "url": "https://stat.uz", "tier": "A"},
            {"nom": "xarid.uzex.uz (davlat xaridlari)", "url": "https://xarid.uzex.uz", "tier": "A"},
        ],
        "huquqiy_asos": "O'RQ-707 (Rasmiy statistika, 11.08.2021) — ochiq statistikadan foydalanish huquqi.",
        "kirish_kerak": False,
        "isbot_kuchi": 4,
        "aniqlik": "oraliq kengligi ±30–100% (koeffitsient + boshqaruv samarasi noaniqligi)",
        "kadans": "yillik/choraklik",
        "kod": "kirishsiz.bands.expected_band / elv_to_ef",
        "cheklov": "Faoliyat ma'lumoti «korxona darajasida» bo'lmasa, ajratish xatosi o'sadi (birlashgan ishlab chiqarish).",
    },
    {
        "id": "statistik-skrining",
        "nomi": "Hisobot qatorlarining statistik skriningi (Benford/dumaloqlash)",
        "nima_qilinadi": "E'lon qilingan qatorlar (masalan oylik o'lchovlar) taqsimoti Benford qonuni va "
                         "«dumaloq raqam» belgilariga tekshiriladi — qo'lda tuzatishga moyillik signali.",
        "manba": [
            {"nom": "Nigrini (2012) MAD mezonlari", "url": "https://link.springer.com/article/10.1007/s00181-025-02876-0",
             "tier": "C", "tekshirilgan": "2026-02-04 (mezonlar maqolada keltirilgan)"},
        ],
        "huquqiy_asos": "— (hisoblash usuli; ma'lumot ochiq manbadan olinadi)",
        "kirish_kerak": False,
        "isbot_kuchi": 1,
        "aniqlik": "faqat signal; n ≥ 100 kerak, aks holda kuchsiz",
        "kadans": "yillik",
        "kod": "kirishsiz.benford.analyse",
        "cheklov": "Benford chetlanishi **firibgarlikni isbotlamaydi** — texnik sabab (datchik diapazoni, "
                   "yaxlitlash qoidasi) ham shunday taqsim beradi.",
    },
    {
        "id": "yol-transsekti",
        "nomi": "Umumiy yo'ldagi mobil o'lchov (transsekt inversion)",
        "nima_qilinadi": "Ochiq yo'ldan (ruxsat kerak emas) o'tishda ko'chma sensor bilan fon+cho'qqi o'lchanadi; "
                         "Gauss teskari masalasi bilan manba quvvati Q baholanadi (± oraliq bilan).",
        "manba": [
            {"nom": "Pasquill–Gifford dispersiya usuli", "url": "https://www.epa.gov/scram/air-quality-dispersion-modeling",
             "tier": "C", "tekshirilgan": "uslubiy qo'llanma"},
        ],
        "huquqiy_asos": "Umumiy yo'l — ochiq joy; o'lchov chegara qiymatlari (SanQvaM) nazorat organi o'lchovi "
                        "uchun asos. Ruxsat faqat obyekt hududiga kirish uchun kerak, yo'lga emas.",
        "kirish_kerak": False,
        "isbot_kuchi": 3,
        "aniqlik": "Q xatosi ±40–70% (σz modeli + fon ayirish); past chegara signali kuchli bo'lsa yaxshilanadi",
        "kadans": "o'lchov kampaniyasi (10–30 o'tish)",
        "kod": "kirishsiz.transect.invert_q / fit_campaign / plan_campaign",
        "cheklov": "Yo'l manba yo'nalishiga **pastda** bo'lishi kerak; ortiqcha manba (transport) signalni buzadi — "
                   "fon o'lchovi va tunda o'lchash bilan kamaytiriladi.",
    },
    {
        "id": "huquqiy-talab",
        "nomi": "Ma'lumotni ochish talabi (Aarhus/Konstitutsiya asosida)",
        "nima_qilinadi": "Nazorat organi va korxona davlat tizimlarida bor ma'lumot (o'lchov natijalari, inspeksiya "
                         "dalolatnomalari, ruxsatnoma shartlari) **yozma so'rov** bilan talab qilinadi; 15 kunlik "
                         "javob muddati va apellyatsiya yo'li kuzatiladi.",
        "manba": [
            {"nom": "Aarhus konventsiyasi (25.08.2025 dan kuchda)", "url": "https://unece.org/environment-policy/public-participation/aarhus-convention",
             "tier": "A", "tekshirilgan": "UNECE, 2026-01-05 holat bayonoti"},
            {"nom": "Murojaat muddati 15 kun", "url": "https://constitution.uz/oz/pages/murojaat_huquq", "tier": "A",
             "tekshirilgan": "2026-10-01"},
            {"nom": "Ochiqlik qonuni (05.05.2014)", "url": "https://lex.uz", "tier": "A"},
        ],
        "huquqiy_asos": "Konstitutsiya 49-modda · Aarhus 4-modda · davlat organlari faoliyati ochiqligi to'g'risidagi qonun · "
                        "murojaatlar 15 kun ichida ko'riladi",
        "kirish_kerak": False,
        "isbot_kuchi": 5,
        "aniqlik": "rasmiy hujjat (agar berilsa) — eng kuchli dalil",
        "kadans": "so'rov har 2 hafta",
        "kod": "kirishsiz.requests_gen.build_request / tracker_add",
        "cheklov": "«Savdo siri» yoki «ichki hujjat» sababi bilan rad etilishi mumkin; rad javobi ham dalil "
                   "(rad etish asosini apellyatsiyada tekshirish mumkin).",
    },
]

# Yakuniy xulosa uchun minimal talab
MIN_POWER_FOR_CONCLUSION = 3
MIN_PATHS_FOR_CONCLUSION = 2


def get_path(path_id: str) -> dict[str, Any]:
    for p in PATHS:
        if p["id"] == path_id:
            return p
    raise KeyError(f"yo'l topilmadi: {path_id}")


def paths_by_power(min_power: int = 1) -> list[dict[str, Any]]:
    return sorted([p for p in PATHS if p["isbot_kuchi"] >= min_power],
                  key=lambda p: -p["isbot_kuchi"])


def conclusion_rule() -> dict[str, Any]:
    """Bitta yo'l bilan xulosa chiqarish mumkinmi — qoida."""
    return {
        "min_kuch": MIN_POWER_FOR_CONCLUSION,
        "min_yol": MIN_PATHS_FOR_CONCLUSION,
        "qoida": f"Xulosa uchun isbot kuchi ≥{MIN_POWER_FOR_CONCLUSION} bo'lgan kamida "
                 f"{MIN_PATHS_FOR_CONCLUSION} mustaqil yo'l kerak (yoki 5-kuchli rasmiy hujjat).",
        "taqiq": "1–2 kuchdagi yagona yo'l bilan «obyekt aybdor» deyilmaydi (skrining → keyingi tekshiruv).",
    }


def registry_json() -> str:
    return json.dumps({"yollar": PATHS, "qoida": conclusion_rule()}, ensure_ascii=False, indent=2)
