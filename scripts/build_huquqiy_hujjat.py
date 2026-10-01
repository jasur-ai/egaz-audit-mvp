# -*- coding: utf-8 -*-
"""`YAKUNIY/21-QONUNIY-ASOS-XARITASI.md` ni **registrdan** yasaydi (R54).

Nega generator: xarita va reyestr kodda (`src/kirishsiz/huquqiy_asos.py`) — hujjat
ular bilan har doim bir xil bo'lishi kerak. Registr o'zgarsa, hujjat qayta yasaladi.
Ish stolida chiqish: `../YAKUNIY/21-QONUNIY-ASOS-XARITASI.md`; boshqa joyda (klon/CI):
`docs/20-qonuniy-asos-xaritasi.md`.

    python3 scripts/build_huquqiy_hujjat.py            # yozadi
    python3 scripts/build_huquqiy_hujjat.py --check    # farqni ko'rsatadi (yozmaydi)
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.kirishsiz import huquqiy_asos as H  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Ish stolida: ../YAKUNIY/21-... · boshqa joyda (masalan, mustaqil klonda): docs/20-...
_YUQORI = os.path.dirname(ROOT)
_ISH_STOLI = os.path.basename(_YUQORI) == "01-Loyiha1-Carbon-Emission" and os.path.isdir(
    os.path.join(os.path.dirname(_YUQORI), "YAKUNIY"))
CHIQISH = (os.path.join(os.path.dirname(_YUQORI), "YAKUNIY", "21-QONUNIY-ASOS-XARITASI.md")
           if _ISH_STOLI else os.path.join(ROOT, "docs", "20-qonuniy-asos-xaritasi.md"))

SARLAVHA = """# 21 — QONUNIY ASOS XARITASI: «HAR BIR ELEMENT — FARMON BILAN» · **2026-10-01** (R54)

> **Nima yangi:** loyihaning **har bir elementi** (8 kirishsiz yo'l, 6 modul, 8 tashkiliy band)
> endi **kamida 2 ta** rasmiy hujjat bilan bog'langan. Registr **kodda** saqlanadi
> (`src/kirishsiz/huquqiy_asos.py`) va **mashinada tekshiriladi** — ya'ni «qonuniylik» da'vo emas,
> test bilan qo'riqlanadigan fakt.
>
> **Raqamlar:** **{hujjatlar} hujjat** (Konstitutsiya · xalqaro shartnoma · 3 qonun · {farmon} farmon ·
> {qaror} qaror · 5 standart) · **{elementlar} element** · **{asoslar} huquqiy bog'lanish**
> (o'rtacha {ortacha}, eng kam {eng_kam}) · tekshiruv holati: **{holat}**.

---

## 1. Xarita — element → huquqiy asoslar

| Loyiha elementi | Asoslar soni | Hujjatlar |
|---|---|---|
"""

KEYINGI = """
---

## 2. Hujjatlar reyestri

| # | Tur | Raqam | Sana | Biz foydalanadigan band | Manba | Daraja |
|---|---|---|---|---|---|---|
"""

IZOH_BLOKI = """
**Daraja:** **A** — rasmiy matn yoki hujjat raqami bilan tasdiqlangan (%A% ta) ·
**B** — hujjat ma'lum, matni/URL keyin qo'shiladi (%B% ta, §5 da ro'yxat) ·
**S** — standart (texnik norma, qonun emas) (%S% ta).

---

## 3. Nega bu «qonuniylikni oshiradi» — beshta aniq mexanizm

1. **Har bir da'vo bandga bog'langan.** «Toza havo» loyihasining maqsadlari (chiqindini **10,5%**
   kamaytirish, I/II toifa korxonalarga avtomatik monitoring va chang-gaz tozalash uskunalari,
   Toshkent dasturi) — PF-46; fon stansiyalari va integratsiya majburiyati, 5 baravar kompensatsiya —
   PQ-343. Bizning o'lchovlar aynan shu bandlarning **ijrosini tekshiradi**.
2. **Sanksiya o'lchov ishonchiga bog'liq.** O'RQ-1143 (04.05.2026) normadan ortiq tashlama uchun
   kompensatsiyani **2×–10×** qildi. Ishonchsiz raqam bilan solinadigan sanktsiya — adolatsiz
   sanktsiya; shu sababli o'lchov ishonchi **huquqiy** masala, nafaqat texnik.
3. **Axborot olish — huquq, iltimos emas.** Konstitutsiya 49-modda + Aarhus (4-modda) + ochiqlik
   qonuni: so'rovlar shu uchlikka tayanadi, javob bo'lmasa Aarhus 9-modda bo'yicha eskalatsiya
   (20.10 muddat → 25.10 eskalatsiya).
4. **Platformaga integratsiya — talab, imkoniyat emas.** PQ-343: I/II toifa korxonalar stansiyalarni
   Ekologik monitoring milliy markaziga **integratsiya qilishi shart**; 01.09.2026 gacha Yagona
   ekologik onlayn platforma. Bizning eksport formatlari (GeoJSON/JSON, audit izi) shu integratsiyaga
   tayyor.
5. **Xalqaro hisobot zanjiri (MRV).** GHG qonuni + NDC 3.0 va VM-234 (ta'sirni baholash) —
   hisobotning qayta tekshirilishi (verifikatsiya) talab qilinadi; standartlar qatori
   (JCGM 106 · ILAC-G8 · ISO/IEC 17025 · EPA RATA) shu talabni **o'lchov amaliyotiga** o'giradi.

---

## 4. «Juda ko'p joyda» — bog'lanish qayerda ishlatiladi

| Qayerda | Qanday ishlatiladi |
|---|---|
| **4 rasmiy so'rov (05.10)** | Har xatda **6 huquqiy asos** bloki (Konstitutsiya · Aarhus · ochiqlik qonuni · PQ-343 · PF-69 · muddat qoidasi) |
| **TZ-1 va ilovalar** | T1–T7 bosqichlari VM-783 (uskuna/TT), PQ-343 (stansiya/integratsiya) bilan bog'langan; **K.11** — shu xarita |
| **Kirishsiz yo'llar (8)** | Har yo'l uchun 2 asos: PF-46 · PQ-343 · PF-81 · PF-90 · PF-217 · VM-234 · O'RQ-1143 · GHG |
| **Dashboard va hisobotlar** | Ochiq ma'lumot talabi (ochiqlik qonuni) va verifikatsiya qatori (JCGM/ILAC/ISO) ustunlari |
| **Bot (`@ecoledg_bot`)** | Murojaat zanjiri + 15 kun qoidasi; javobsiz so'rov eskalatsiyasi |
| **Apellyatsiya paketi** | Aarhus 9-modda + O'RQ-1143 sanksiya mantig'i |
| **Deck (taqdimot)** | «Qonuniy asos» slaydi — 5 mexanizm, rahbariyat uchun bir ekranda |
| **Maqolalar (draft)** | Har bir raqamli da'vo yonida hujjat havolasi (manba + sana + daraja qoidasi) |
| **Rahbariyat paketi** | Qaror loyihasi bandlari aynan shu hujjatlarga tayanadi (`YAKUNIY/22-...`) |

---

## 5. Tekshiruv (mashinada) va qolgan ish

```bash
python3 scripts/kirishsiz.py huquqiy --qamrov    # elementlar, asoslar, zaif nuqtalar
python3 scripts/kirishsiz.py huquqiy --tekshir   # to'liq tekshiruv (holat: ok)
python3 scripts/kirishsiz.py huquqiy --havola --element "modul:isitish (yoqilg'i hisobi)"
```

Testlar (`tests/test_kirishsiz_huquqiy.py`, **13 test**): har elementda ≥2 asos · manba yoki izoh bor ·
takroriy id yo'q · foydalanilmagan hujjat yo'q · 8/8 kirishsiz yo'l qoplangan · registrda kirill
aralashmasi yo'q · xat matnida huquqiy blok bor.

**Qolgan ish (ochiq, yashirilmaydi):** quyidagi %MANBASIZ% ta hujjatda rasmiy havola hali
qo'shilmagan — ular **izoh bilan belgilangan** (soxta URL yozilmaydi): %MANBASIZ_LIST%.

---

## 6. Keyingi qadam

1. **05.10** — 4 so'rovni yuborish (huquqiy blok allaqachon xat ichida).
2. **PF-69 · GHG qonuni · NDC 3.0** uchun lex.uz havolalarini qo'shish (registr `manba` maydoni).
3. Qaror loyihasi (§`YAKUNIY/22`) tasdiqlangach — xaritani **hujjatlararo havola** rejimiga o'tkazish.
"""


def build() -> str:
    q = H.qamrov()
    s = H.statistika()
    t = H.tekshir()
    farmon = s["tur"].get("Farmon", 0)
    qaror = s["tur"].get("Qaror", 0)
    matn = SARLAVHA.format(hujjatlar=q["hujjatlar"], farmon=farmon, qaror=qaror,
                           elementlar=q["elementlar"], asoslar=q["asoslar_jami"],
                           ortacha=q["ortacha"], eng_kam=q["eng_kam"], holat=t["holat"])
    for e, n in q["sanoq"].items():
        matn += f"| **{e}** | {n} | " + " · ".join(f"`{k}`" for k in H.XARITA[e]) + " |\n"
    matn += KEYINGI
    for i, h in enumerate(H.HUJJATLAR, 1):
        manba = h.get("manba") or "— (izohga qarang)"
        matn += (f"| {i} | {h['tur']} | **{h['raqam']}** | {h['sana']} | {h['band']} | "
                 f"{manba} | {h['daraja']} |\n")
    izoh = (IZOH_BLOKI.replace("%A%", str(s["daraja"].get("A", 0)))
            .replace("%B%", str(s["daraja"].get("B", 0)))
            .replace("%S%", str(s["daraja"].get("S", 0))))
    matn += izoh
    manbasiz = s["manbasiz"]
    # 5-bo'lim matnini aniq raqam bilan to'ldiramiz
    matn = matn.replace("%MANBASIZ%", str(len(manbasiz)))
    matn = matn.replace("%MANBASIZ_LIST%", ", ".join(f"`{i}`" for i in manbasiz))
    return matn


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="yozmasdan farqni ko'rsatish")
    ap.add_argument("--out", default=os.path.normpath(CHIQISH))
    a = ap.parse_args()
    matn = build()
    if a.check:
        bor = open(a.out, encoding="utf-8").read() if os.path.exists(a.out) else ""
        print("✅ bir xil" if bor == matn else "⚠️ farq bor — qayta yasash kerak")
        return 0 if bor == matn else 1
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(matn)
    q = H.qamrov()
    print(f"✅ {a.out}")
    print(f"   {q['hujjatlar']} hujjat · {q['elementlar']} element · {q['asoslar_jami']} bog'lanish")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
