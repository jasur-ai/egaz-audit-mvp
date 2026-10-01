# -*- coding: utf-8 -*-
"""Huquqiy yo'l — ma'lumotni ochish talabi (ruxsat so'rash emas, **talab**).

Asos (tekshirilgan manbalar):
  · Konstitutsiya 49-modda — «har kim qulay atrof-muhit va uning holati to'g'risida
    ishonchli axborot olish huquqiga ega» (gazeta.uz, 18.03.2025 tahlili).
  · **Aarhus konventsiyasi** — O'zbekiston qo'shildi: Prezident 2025-yil 11-martda
    qonunni imzoladi (gazeta.uz, 18.03.2025); UNECE MoP bayonotiga ko'ra Konventsiya
    O'zbekiston uchun **2025-yil 25-avgustdan kuchga kirdi** (UNECE, 2026-01-05).
    4-modda: atrof-muhit axborotiga kirish; rad etish faqat tor istisnolar bilan.
  · Davlat organlari faoliyatining ochiqligi to'g'risidagi qonun (05.05.2014) —
    axborot olish tartibi.
  · Murojaat muddati: **15 kun**, qo'shimcha o'rganish kerak bo'lsa — bir oygacha
    (constitution.uz «Murojaat huquqi» sahifasi).

Bu modul so'rov matnini, muddat kuzatuvini va eskalatsiya qadamini yaratadi —
shunda «ruxsat berishmadi» holati **hujjatli** yo'lga aylanadi: javob, rad etish yoki
jimlik — uchalasi ham keyingi qadam uchun asos.
"""
from __future__ import annotations

import json
import os
from datetime import date, datetime, timedelta, timezone
from typing import Any, Iterable

JAVOB_KUN = 15          # murojaat ko'rib chiqish muddati (konstitutsiyaviy amaliyot)
ESKALATSIYA_KUN = 5     # ichki qoidamiz: javob bo'lmasa apellyatsiya/yuqori organga
MANBALAR = [
    "Konstitutsiya 49-modda (ishonchli ekologik axborot)",
    "Aarhus konventsiyasi, 4-modda (O'zbekiston uchun 25.08.2025 dan kuchda)",
    "Davlat organlari faoliyatining ochiqligi to'g'risidagi qonun (05.05.2014)",
    "Murojaatlar 15 kun ichida ko'riladi (constitution.uz)",
]

STANDART_SOROVLAR = {
    "olchov": "Obyekt bo'yicha oxirgi 3 yildagi tashlanma o'lchov natijalari (protokollar, "
              "o'lchov sanasi, usul, akkreditatsiya raqami)",
    "inspeksiya": "Oxirgi 3 yilda o'tkazilgan inspeksiyalar dalolatnomalari va aniqlangan "
                  "huquqbuzarliklar bo'yicha choralar",
    "ruxsatnoma": "Amaldagi ekologik ruxsatnoma/ruxsat shartlari: chegaraviy tashlanma "
                  "qiymatlari, o'lchov kadansi, ushlash qurilmalari",
    "monitoring": "Hududdagi davlat monitoring stansiyalari ma'lumotlari (soatlik PM2,5/NO2/SO2) "
                  "va ularning joylashuvi",
    "fakel": "Mash'al/fakel qurilmalari ro'yxati va yonish rejimi (agar mavjud bo'lsa)",
    # R53: isitish mavsumi tahlili aniqlagan **yagona yetishmayotgan bo'g'in** uchun
    "isitish-qattiq": "Isitish mavsumi (noyabr–fevral) uchun aholiga sotilgan/berilgan qattiq "
                      "yoqilg'i (ko'mir, briket, o'tin) hajmi — tuman va sotuvchi tashkilot "
                      "kesimida; xususiy uylarda individual isitish qozonlari soni",
    "gaz-isitish": "Aholi tomonidan iste'mol qilingan tabiiy gaz hajmi **oylar kesimida** "
                    "(isitish mavsumi va mavsumdan tashqari), isitish mavsumi uchun belgilangan "
                    "ijtimoiy me'yor statistikasi va isitish bilan ta'minlangan xonadonlar soni",
}


# R53 tahlilida **o'lchangan** natijalar — so'rovga asos sifatida qo'shiladi.
# Har bir qator: (matn, manba/daraja). Raqamlar 365 kunlik ochiq ma'lumotdan (CAMS/ERA5).
TOPILMALAR: list[tuple[str, str]] = [
    ("Toshkent shahri (CAMS katagi, 2025-10-02 → 2026-10-01, 8 760 soat) bo'yicha PM2,5 "
     "o'rtachasi isitish mavsumida 25,60 µg/m³, issiq mavsumda 15,36 µg/m³ — farq 1,67×",
     "Open-Meteo/CAMS havo sifati arxivi, 2026-10-01 da olindi"),
    ("Kunlik PM2,5 normadan (35 µg/m³) oshgan kunlar: isitish mavsumida 21/181, issiq mavsumda 0/183",
     "o'sha manba, o'z hisobimiz"),
    ("Shu davrda NOx/SO2/CO ko'rsatkichlari ham ~2 barobar oshadi, PM2,5/PM10 nisbati 0,68 → 0,86 "
     "(nozik zarrachalar ulushi ortadi)", "o'sha manba, o'z hisobimiz"),
    ("Angren (4 km masofadagi IES) retseptorida isitish mavsumi ko'tarilishi **yo'q** (0,97×) va "
     "normadan oshgan kun **0** — ko'mir stansiyasi signali isitish mavsumida ham ustun emas",
     "o'sha manba + GEM koordinatalari (Angren power station, exact)"),
    ("Ohangaron/Olmaliq katagida 21 normadan oshgan kunning 3 tasi kuzatildi va uchalasi ham "
     "sement kombinati yo'nalishidan **tashqarida**", "o'sha manba, o'z hisobimiz"),
    ("EMEP/EEA 2023 1.A.4.b.i bo'yicha: tabiiy gaz PM2,5 1,2 g/GJ, qattiq yoqilg'i 398 g/GJ — "
     "farq ~330×; shu sababli gaz isitish PM2,5 ortishini tushuntira olmaydi",
     "EMEP/EEA Guidebook 2023, 1.A.4 Small combustion"),
]


def topilmalar_bloki(sarlavha: str = "Tadqiqotning ochiq ma'lumotlarga asoslangan natijalari") -> str:
    """So'rovga qo'shiladigan qisqa asos bloki (o'lchangan raqamlar + manba)."""
    qatorlar = [f"{sarlavha} (2026-yil oktabr holati):"]
    for i, (matn, manba) in enumerate(TOPILMALAR, 1):
        qatorlar.append(f"  {i}) {matn}. Manba: {manba}.")
    qatorlar.append("  Shu sababli quyidagi ma'lumotlar so'ralmoqda — ular yuqoridagi "
                    "farqni miqdoriy tushuntirish uchun yetishmayotgan yagona bo'g'in.")
    return "\n".join(qatorlar)


def build_request(
    tashkilot: str,
    murojaat_turi: str = "olchov",
    obyekt: str = "⟦obyekt nomi⟧",
    sorovchi: str = "⟦F.I.Sh. / tadqiqot guruhi⟧",
    aloqa: str = "⟦telefon / e-pochta⟧",
    sana: str | None = None,
    qoshimcha: Iterable[str] | None = None,
    topilmalar: bool = True,
) -> dict[str, Any]:
    """So'rov matni (uz) + muddat hisobi. `murojaat_turi` — STANDART_SOROVLAR kaliti."""
    if murojaat_turi not in STANDART_SOROVLAR:
        raise KeyError(f"tur noma'lum: {murojaat_turi} (mavjud: {', '.join(STANDART_SOROVLAR)})")
    sana = sana or date.today().isoformat()
    mazmun = [STANDART_SOROVLAR[murojaat_turi]] + list(qoshimcha or [])
    matn = "\n".join([
        f"{tashkilot} rahbariga",
        "",
        "AXBOROT OCHISH TALABI",
        f"(Konstitutsiyaning 49-moddasi, Aarhus konventsiyasining 4-moddasi va davlat organlari",
        f"faoliyatining ochiqligi to'g'risidagi qonun asosida)",
        "",
        f"Men, {sorovchi}, {obyekt} obyekti bo'yicha atrof-muhit holatiga oid quyidagi",
        "ma'lumotlarni so'rayman:",
        *[f"  {i}) {m}" for i, m in enumerate(mazmun, 1)],
        "",
        *([topilmalar_bloki()] if topilmalar else []),
        "",
        "Eslatma: so'ralayotgan ma'lumot davlat organlari tizimida mavjud bo'lgan rasmiy",
        "hujjat hisoblanadi; u savdo siri yoki shaxsga doir ma'lumotni oshkor qilmaydi.",
        "Qonunchilikka ko'ra murojaat 15 kun ichida ko'rib chiqilishi kerak; qo'shimcha",
        "o'rganish talab qilinsa, muddat bir oygacha uzaytirilishi mumkin (bunda sabab",
        "yozma xabar qilinishi kerak).",
        "",
        "Javobni quyidagi manzilga yuborishingizni so'rayman: " + aloqa,
        "",
        f"Sana: {sana}",
        f"Imzo: ____________________ ({sorovchi})",
    ])
    muddat = datetime.fromisoformat(sana).date() + timedelta(days=JAVOB_KUN)
    return {
        "tashkilot": tashkilot,
        "tur": murojaat_turi,
        "obyekt": obyekt,
        "sana": sana,
        "matn": matn,
        "muddat": {
            "javob_kun": JAVOB_KUN,
            "javob_sana": muddat.isoformat(),
            "eskalatsiya_sana": (muddat + timedelta(days=ESKALATSIYA_KUN)).isoformat(),
            "qoida": f"javob {JAVOB_KUN} kun; javob bo'lmasa {ESKALATSIYA_KUN} kundan keyin "
                     "yuqori organga/apellyatsiyaga (Aarhus 9-modda) murojaat",
        },
        "manbalar": MANBALAR,
        "kuzatuv_yozuvi": {
            "yuborilgan": sana,
            "holat": "yuborildi",
            "javob": None,
            "javob_sanasi": None,
        },
    }


def tracker_add(path: str, entry: dict[str, Any]) -> dict[str, Any]:
    """So'rovni kuzatuv jurnaliga qo'shish (append-only JSONL)."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    rec = dict(entry)
    rec["qoshilgan_vaqt"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec


def tracker_load(path: str) -> list[dict[str, Any]]:
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def tracker_pending(path: str, today: str | None = None) -> dict[str, Any]:
    """Muddati o'tgan / yaqinlashayotgan so'rovlar (javobsizlar)."""
    today_d = datetime.fromisoformat(today).date() if today else date.today()
    rows = tracker_load(path)
    kutayotgan, muddati_otgan = [], []
    for r in rows:
        if r.get("kuzatuv_yozuvi", {}).get("javob") or r.get("javob"):
            continue
        javob_sana = r["muddat"]["javob_sana"]
        if datetime.fromisoformat(javob_sana).date() < today_d:
            muddati_otgan.append(r)
        else:
            kutayotgan.append(r)
    return {
        "jami": len(rows),
        "javobsiz": len(kutayotgan) + len(muddati_otgan),
        "muddati_otgan": [{"tashkilot": r["tashkilot"], "javob_sana": r["muddat"]["javob_sana"],
                           "eskalatsiya": r["muddat"]["eskalatsiya_sana"]} for r in muddati_otgan],
        "kutayotgan": [{"tashkilot": r["tashkilot"], "javob_sana": r["muddat"]["javob_sana"]}
                       for r in kutayotgan],
    }
