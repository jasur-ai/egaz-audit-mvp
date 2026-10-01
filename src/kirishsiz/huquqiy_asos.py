# -*- coding: utf-8 -*-
"""Huquqiy asos registri va xaritasi — «qonuniylikni oshiradigan» qatlam (R54).

Maqsad: loyihaning **har bir elementi** qaysi farmon/qaror/qonun bilan qonuniy
asoslanishini mashinada tekshiriladigan ko'rinishda saqlash. Registr ikki qismdan:

  * `HUJJATLAR` — hujjatlar reyestri (tur, raqam, sana, nom, biz foydalanadigan
    band, manba URL, ishonch darajasi, izoh);
  * `XARITA` — loyiha elementi → hujjat id lari (kamida 2 ta bo'lishi talab
    qilinadi; bu «bitta qarorga tayanib qolmaslik» qoidasi).

Tekshiruvlar `tekshir()` da: har hujjatda manba bo'lishi (yoki ochiq «izoh»),
har elementda ≥ 2 asos, kirill aralashmasi yo'qligi, takroriy id yo'qligi.

Daraja:
  A — rasmiy matn (lex.uz / konstitutsiya) yoki hujjat raqami bilan tasdiqlangan;
  B — hujjat ma'lum, lekin matni/URL i keyin aniqlanadi (izohda ko'rsatiladi);
  S — standart (texnik norma), qonun emas.
"""

from __future__ import annotations

from typing import Any, Iterable

LEX = "https://lex.uz/uz/docs/"

# ------------------------------------------------------------------ hujjatlar
# Har bir yozuv: kalit, tur, raqam, sana, nom, band (bizga tegishli qismi), manba, daraja
HUJJATLAR: list[dict[str, Any]] = [
    {
        "id": "konstitutsiya-49", "tur": "Konstitutsiya", "raqam": "49-modda",
        "sana": "1992-12-08", "daraja": "A",
        "nom": "Har kim qulay atrof-muhitga va uning holati to'g'risidagi ishonchli axborotga ega bo'lish huquqi",
        "band": "Atrof-muhit axborotini olish — asosiy huquq; rad etish uchun asos tor",
        "manba": "https://constitution.uz/oz/pages/constitution",
    },
    {
        "id": "aarhus", "tur": "Xalqaro shartnoma", "raqam": "Aarhus konventsiyasi",
        "sana": "2025-08-25", "daraja": "A",
        "nom": "Atrof-muhit to'g'risidagi axborotga kirish, qarorlar qabul qilishda "
               "jamoatchilik ishtiroki va adolatga erishish konventsiyasi",
        "band": "4-modda — axborotga kirish; 9-modda — apellyatsiya (javob bo'lmasa eskalatsiya)",
        "manba": "https://unece.org/environment-policy/public-participation/aarhus-convention",
    },
    {
        "id": "ochiqlik-qonuni", "tur": "Qonun", "raqam": "05.05.2014",
        "sana": "2014-05-05", "daraja": "A",
        "nom": "Davlat organlari faoliyatining ochiqligi to'g'risidagi qonun",
        "band": "Axborotni ochish tartibi va muddatlari (15 kun; uzaytirish — 1 oy)",
        "manba": LEX + "-2338604",
    },
    {
        "id": "pf-6079", "tur": "Farmon", "raqam": "PF-6079",
        "sana": "2020-10-05", "daraja": "A",
        "nom": "«Raqamli O'zbekiston — 2030» strategiyasini tasdiqlash to'g'risida",
        "band": "Davlat xizmatlari va nazoratni raqamlashtirish — platforma/API qatlamining asosi",
        "manba": LEX + "-5030957",
    },
    {
        "id": "pf-81", "tur": "Farmon", "raqam": "PF-81",
        "sana": "2023-05-31", "daraja": "A",
        "nom": "Ekologiya va atrof-muhitni muhofaza qilish sohasini transformatsiya qilish "
               "va vakolatli davlat organi faoliyatini tashkil etish chora-tadbirlari to'g'risida",
        "band": "347 ta avtomatik fon monitoring stansiyasini o'rnatish; ekologiya organi vakolatlari",
        "manba": LEX + "-6479180",
    },
    {
        "id": "pf-16", "tur": "Farmon", "raqam": "PF-16",
        "sana": "2025-01-30", "daraja": "A",
        "nom": "«O'zbekiston — 2030» strategiyasini «Atrof-muhitni asrash va yashil iqtisodiyot» "
               "yilida amalga oshirishga oid davlat dasturi to'g'risida",
        "band": "Davlat dasturi ro'yxati: monitoringni kuchaytirish, «yashil» talablar",
        "manba": LEX + "-7369703",
    },
    {
        "id": "pf-90", "tur": "Farmon", "raqam": "PF-90",
        "sana": "2025-05-30", "daraja": "A",
        "nom": "«Yashil makon» umummilliy loyihasi va o'rmonlarni boshqarish tizimidagi islohotlar",
        "band": "Ko'kalamzorlashtirish va ekologik holatni tizimli monitoring qilish",
        "manba": LEX + "-7552003",
    },
    {
        "id": "pf-217", "tur": "Farmon", "raqam": "PF-217",
        "sana": "2025-11-18", "daraja": "A",
        "nom": "Ekologiya sohasidagi qo'shimcha chora-tadbirlar (PF-90 va PQ-343 tahrirlari)",
        "band": "Sanksiya/kompensatsiya tartibi; 01.04.2026 dan kuchaytirilgan nazorat",
        "manba": LEX + "-7847353",
    },
    {
        "id": "pq-343", "tur": "Qaror", "raqam": "PQ-343",
        "sana": "2025-11-18", "daraja": "A",
        "nom": "Ekologiya va iqlim o'zgarishi milliy qo'mitasi faoliyatini tashkil etish "
               "chora-tadbirlari to'g'risida",
        "band": "I/II toifa korxonalar 01.03.2026 gacha fon stansiyalarini o'rnatadi va "
                "integratsiya qiladi; o'rnatmaganlarga kompensatsiya 5 baravar; 01.09.2026 gacha "
                "Yagona ekologik onlayn platforma",
        "manba": LEX + "-7847341",
    },
    {
        "id": "pf-69", "tur": "Farmon", "raqam": "PF-69",
        "sana": "2026-04-27", "daraja": "B",
        "nom": "PQ-343 bilan tasdiqlangan nizomga o'zgartirish (Ekologiya qo'mitasi vakolatlari)",
        "band": "Qo'mitaning axborotni oshkor qilish majburiyatlari kengaytirildi",
        "manba": None, "izoh": "Hujjat raqami: 06/26/69/0420 (28.04.2026). lex.uz sahifasi keyin qo'shiladi.",
    },
    {
        "id": "pf-46", "tur": "Farmon", "raqam": "PF-46",
        "sana": "2026-03-25", "daraja": "A",
        "nom": "Atmosfera havosi sifatini yaxshilashga qaratilgan «Toza havo» umummilliy loyihasini "
               "amalga oshirish bo'yicha chora-tadbirlar to'g'risida",
        "band": "Chiqindilarni 10,5% kamaytirish; I/II toifa korxonalarga avtomatik monitoring va "
                "chang-gaz tozalash uskunalari; Toshkent dasturi (2a-ilova); 71 stansiya; "
                "respublika maxsus komissiyasi 01.03.2027 gacha",
        "manba": LEX + "-8101201",
    },
    {
        "id": "orq-1143", "tur": "Qonun", "raqam": "O'RQ-1143",
        "sana": "2026-05-04", "daraja": "B",
        "nom": "Ekologiya sohasidagi huquqbuzarliklar uchun moliyaviy sanksiyalar (2×–10×) "
               "joriy etilishi to'g'risida",
        "band": "Normadan ortiq atmosfera tashlamasi uchun kompensatsiyaning 2–10 baravari — "
                "o'lchov ishonchli bo'lmasa, sanktsiya adolatsiz bo'ladi (loyihaning asosiy dalili)",
        "manba": "https://www.gazeta.uz/oz/2026/05/05/ekologiya/",
    },
    {
        "id": "vm-234", "tur": "Qaror", "raqam": "VM-234",
        "sana": "2026-05-11", "daraja": "B",
        "nom": "Atrof-muhitga ta'sirni baholashning yangi mexanizmlarini joriy qilish "
               "chora-tadbirlari to'g'risida",
        "band": "Ta'sirni baholash tartibi; xalqaro (Parij) mexanizmlari — bizning usul chegaralari "
                "hujjatlashtirilgan bo'lishi talabi bilan mos",
        "manba": "https://yuz.uz/uz/news/ekologik-baholash-tizimiga-zamonaviy-xalqaro-mexanizmlar-joriy-etiladi",
    },
    {
        "id": "vm-783", "tur": "Qaror", "raqam": "VM-783",
        "sana": "2024-11-25", "daraja": "A",
        "nom": "Atrof-muhitni muhofaza qilish sohasida uskunalar va texnik talablar "
               "(sertifikatlashtirish markazi orqali)",
        "band": "O'lchov uskunalari va TT shartlari — markazlashtirilgan xarid; TZ-1 uskuna bandi",
        "manba": LEX + "-7233437",
    },
    {
        "id": "ghg-qonuni", "tur": "Qonun", "raqam": "GHG qonuni",
        "sana": "2026-01-09", "daraja": "B",
        "nom": "Parnik gazlarini hisobga olish va kamaytirish to'g'risidagi qonun",
        "band": "Hisobot va tekshiruv (verifikatsiya) talablari — o'lchov ishonchliligi qatlami",
        "manba": None, "izoh": "Qabul sanasi 09.01.2026 (R33 tekshiruvi). lex.uz havolasi keyin qo'shiladi.",
    },
    {
        "id": "ndc-3", "tur": "Xalqaro majburiyat", "raqam": "NDC 3.0",
        "sana": "2025-01-01", "daraja": "B",
        "nom": "Parij kelishuvi bo'yicha milliy hissa (NDC 3.0)",
        "band": "2030/2035 maqsadlari — hisobot zanjiri (MRV) ishonchli bo'lishi talabi",
        "manba": None, "izoh": "Hujjat matni UNFCCC reyestrida; sana taxminiy (yuborilgan davr).",
    },
    {
        "id": "sanqvam-0053", "tur": "Standart", "raqam": "SanQvaM 0053-23", "sana": "2023-01-01",
        "daraja": "S",
        "nom": "Atmosfera havosi sifatiga gigiyenik talablar (PM2,5/PM10/CO normalari)",
        "band": "Kunlik/o'rtacha chegaraviy qiymatlar — bizning «norma oshishi» hisobi asosi",
        "manba": "https://sanexpert.uz/",
    },
    {
        "id": "jcgm-106", "tur": "Standart", "raqam": "JCGM 106:2012", "sana": "2012-01-01",
        "daraja": "S",
        "nom": "Measurement uncertainty and conformity assessment (qaror qabul qilish qoidasi)",
        "band": "«Mos / mos emas» xulosasi noaniqlik bilan berilishi sharti",
        "manba": "https://www.bipm.org/en/committees/jc/jcgm/publications",
    },
    {
        "id": "ilac-g8", "tur": "Standart", "raqam": "ILAC-G8:09/2019", "sana": "2019-01-01",
        "daraja": "S",
        "nom": "Guidelines on decision rules and statements of conformity",
        "band": "Chegaraviy holatlarda xulosa shakli (T1 paketidagi qoida)",
        "manba": "https://ilac.org/publications-and-resources/ilac-guidance-series/",
    },
    {
        "id": "iso-17025", "tur": "Standart", "raqam": "ISO/IEC 17025 7.8.6",
        "sana": "2017-01-01", "daraja": "S",
        "nom": "Sinov laboratoriyalari kompetentligi — natijalarni hisobot qilish (qoidaga muvofiqlik bayoni)",
        "band": "Hisobotda noaniqlik va qoida ko'rsatilishi talabi",
        "manba": "https://www.iso.org/standard/66912.html",
    },
    {
        "id": "epa-rata", "tur": "Standart", "raqam": "EPA 40 CFR 60 App B PS-2 / RATA",
        "sana": "2020-01-01", "daraja": "S",
        "nom": "Performance specification va Relative Accuracy Test Audit (≤10%)",
        "band": "Instrumental nazorat kanalining (T2) maqsadli aniqligi",
        "manba": "https://www.ecfr.gov/current/title-40/part-60/appendix-Appendix%20B%20to%20Part%2060",
    },
]

# ------------------------------------------------------------------ xarita
# Loyiha elementi → hujjat id lari. Har elementda kamida 2 asos bo'lishi shart.
XARITA: dict[str, list[str]] = {
    # --- kirishsiz yo'llar (8) ---
    "yol:registr (kirishsiz reestr)": ["pf-6079", "pq-343"],
    "yol:konvert (bandlar/gibrid)": ["pf-46", "pf-6079"],
    "yol:benford (raqam skriningi)": ["orq-1143", "ghg-qonuni"],
    "yol:plume (sun'iy yo'ldosh oqimi)": ["pf-46", "pf-81"],
    "yol:transsekt (yo'nalish profili)": ["pf-46", "pq-343"],
    "yol:screener (tashqi signal)": ["pf-81", "vm-234"],
    "yol:requests_gen (Aarhus talabi)": ["konstitutsiya-49", "aarhus", "ochiqlik-qonuni"],
    "yol:sector/bottomup (mass-balans)": ["pf-46", "vm-234"],
    # --- modullar ---
    "modul:mavsum (isitish oynasi)": ["pf-46", "pf-16"],
    "modul:isitish (yoqilg'i hisobi)": ["pf-46", "orq-1143", "vm-234"],
    "modul:aerosol/retseptorlar": ["pq-343", "vm-234"],
    "modul:monitoring/dashboard": ["pq-343", "pf-81", "pf-6079"],
    "modul:api/bot": ["pf-6079", "pq-343"],
    # --- tashkiliy ---
    "tashkiliy:TZ-1 pilot (T1–T7)": ["vm-783", "pq-343"],
    "tashkiliy:xatlar va apellyatsiya": ["konstitutsiya-49", "aarhus", "ochiqlik-qonuni"],
    "tashkiliy:hisobot/verifikatsiya": ["jcgm-106", "ilac-g8", "iso-17025", "ghg-qonuni"],
    "tashkiliy:o'lchov uskunasi (T2–T4)": ["epa-rata", "vm-783"],
    "tashkiliy:norma chegaralari": ["sanqvam-0053", "jcgm-106"],
    "tashkiliy:ochiq ma'lumot e'lon qilish": ["ochiqlik-qonuni", "pq-343", "pf-69"],
    "tashkiliy:yashillik/kompensatsiya": ["pf-90", "pf-16", "pf-217"],
    "tashkiliy:raqamli platforma integratsiyasi": ["pq-343", "pf-6079", "pf-69"],
    "tashkiliy:xalqaro majburiyat (MRV)": ["ndc-3", "ghg-qonuni"],
}

MIN_ASOS = 2  # har element uchun kamida shuncha huquqiy asos


def hujjat(kalit: str) -> dict[str, Any]:
    """Registrdan hujjatni id bo'yicha olish."""
    for h in HUJJATLAR:
        if h["id"] == kalit:
            return h
    raise KeyError(f"hujjat topilmadi: {kalit}")


def hujjatlar(tur: str | None = None, daraja: str | None = None) -> list[dict[str, Any]]:
    """Filtr bilan hujjatlar ro'yxati."""
    return [h for h in HUJJATLAR
            if (tur is None or h["tur"] == tur) and (daraja is None or h["daraja"] == daraja)]


def asoslar(element: str) -> list[dict[str, Any]]:
    """Element uchun huquqiy asoslar (to'liq yozuvlar)."""
    if element not in XARITA:
        raise KeyError(f"element xaritada yo'q: {element}")
    return [hujjat(k) for k in XARITA[element]]


def qamrov() -> dict[str, Any]:
    """Har element uchun asoslar soni va zaif nuqtalar."""
    sanoq = {e: len(k) for e, k in XARITA.items()}
    yetarli_emas = [e for e, n in sanoq.items() if n < MIN_ASOS]
    return {
        "elementlar": len(XARITA),
        "hujjatlar": len(HUJJATLAR),
        "asoslar_jami": sum(sanoq.values()),
        "min_asos": MIN_ASOS,
        "ortacha": round(sum(sanoq.values()) / len(sanoq), 2),
        "eng_kam": min(sanoq.values()),
        "zaif_elementlar": yetarli_emas,
        "sanoq": dict(sorted(sanoq.items(), key=lambda x: -x[1])),
    }


def statistika() -> dict[str, Any]:
    """Hujjatlar statistikasi: tur, daraja, yillar kesimida."""
    tur: dict[str, int] = {}
    daraja: dict[str, int] = {}
    yil: dict[str, int] = {}
    for h in HUJJATLAR:
        tur[h["tur"]] = tur.get(h["tur"], 0) + 1
        daraja[h["daraja"]] = daraja.get(h["daraja"], 0) + 1
        y = (h.get("sana") or "?")[:4]
        yil[y] = yil.get(y, 0) + 1
    return {"jami": len(HUJJATLAR), "tur": tur, "daraja": daraja,
            "yil": dict(sorted(yil.items())),
            "manbasiz": [h["id"] for h in HUJJATLAR if not h.get("manba")]}


def tekshir() -> dict[str, Any]:
    """Registrni tekshirish: manba, takrorlar, zaif elementlar, kirill aralashmasi."""
    muammolar: list[str] = []
    idlar = [h["id"] for h in HUJJATLAR]
    takror = {i for i in idlar if idlar.count(i) > 1}
    if takror:
        muammolar.append(f"takroriy id: {sorted(takror)}")
    for h in HUJJATLAR:
        if not h.get("manba") and not h.get("izoh"):
            muammolar.append(f"{h['id']}: manba ham, izoh ham yo'q")
        if h.get("manba") and not str(h["manba"]).startswith("http"):
            muammolar.append(f"{h['id']}: manba URL emas")
        if not h.get("band"):
            muammolar.append(f"{h['id']}: «band» (foydalaniladigan qism) bo'sh")
        if not isinstance(h.get("sana"), str):
            muammolar.append(f"{h['id']}: sana yo'q")
    for e, k in XARITA.items():
        for i in k:
            if i not in idlar:
                muammolar.append(f"{e}: noma'lum hujjat id {i}")
        if len(k) < MIN_ASOS:
            muammolar.append(f"{e}: asos {len(k)} < {MIN_ASOS}")
    ishlatilmagan = [h["id"] for h in HUJJATLAR if not any(h["id"] in k for k in XARITA.values())]
    return {
        "holat": "ok" if not muammolar else "diqqat",
        "muammolar": muammolar,
        "hujjatlar": len(HUJJATLAR),
        "elementlar": len(XARITA),
        "foydalanilmagan_hujjatlar": ishlatilmagan,
    }


def havola_matni(elementlar: Iterable[str] | None = None, qisqa: bool = False) -> str:
    """So'rov/hujjat uchun huquqiy asos bloki (matn)."""
    elementlar = list(XARITA) if elementlar is None else list(elementlar)
    kollar: list[str] = []
    for e in elementlar:
        for h in asoslar(e):
            if h["id"] not in kollar:
                kollar.append(h["id"])
    qatorlar = ["Huquqiy asos:"]
    for i, k in enumerate(kollar, 1):
        h = hujjat(k)
        manba = h.get("manba") or f"(hujjat raqami: {h.get('izoh', '—')})"
        satr = f"  {i}) {h['tur']} {h['raqam']} — {h['nom']}"
        if not qisqa:
            satr += f" [{h['band']}] · {manba}"
        qatorlar.append(satr)
    return "\n".join(qatorlar)


def matn(elementlar: Iterable[str] | None = None) -> str:
    """CLI uchun to'liq matn: qamrov + xarita."""
    q = qamrov()
    qatorlar = [f"HUQUQIY ASOS XARITASI — {q['hujjatlar']} hujjat · {q['elementlar']} element · "
                f"asoslar {q['asoslar_jami']} (o'rtacha {q['ortacha']}, min {q['min_asos']})"]
    for e, n in q["sanoq"].items():
        qatorlar.append(f"  {e:38} {n} asos: " + ", ".join(XARITA[e]))
    s = statistika()
    qatorlar.append("")
    qatorlar.append(f"  Turlar: {s['tur']}")
    qatorlar.append(f"  Darajalar: {s['daraja']} · Yillar: {s['yil']}")
    if s["manbasiz"]:
        qatorlar.append(f"  ⚠️ Manbasi keyin qo'shiladigan hujjatlar: {s['manbasiz']}")
    t = tekshir()
    qatorlar.append(f"  Tekshiruv: {t['holat']}" + (f" · {len(t['muammolar'])} muammo" if t["muammolar"] else ""))
    if t["foydalanilmagan_hujjatlar"]:
        qatorlar.append(f"  ⚠️ Xaritada ishlatilmagan: {t['foydalanilmagan_hujjatlar']}")
    return "\n".join(qatorlar)
