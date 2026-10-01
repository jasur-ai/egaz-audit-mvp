# -*- coding: utf-8 -*-
"""05.10.2026 uchun rasmiy so'rovlar to'plamini yig'ish (R53).

To'rt xat — to'rt manzil; har biri R53 tahlilida o'lchangan natijalar bloki bilan
(«nima uchun so'ralmoqda» asosi ko'rinib turadi):

  1. Ekologiya boshqarmasi  — monitoring + isitish (qattiq yo'qilg'i) ma'lumotlari
  2. Ekologiya inspeksiyasi — inspeksiya dalolatnomalari + fakel rejimi
  3. Obyekt (IES/issiqlik stansiyasi) — o'lchov protokollari + ruxsatnoma shartlari
  4. Statistika boshqarmasi — gaz iste'moli (oylar kesimida) + qattiq yoqilg'i savdosi

Ishlatish:
    python3 scripts/build_requests_2026_10.py            # yozadi + kuzatuvga qo'shadi
    python3 scripts/build_requests_2026_10.py --dry-run  # faqat ko'rsatadi
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.kirishsiz import requests_gen as R  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SANA = "2026-10-05"
CHIQISH = os.path.join(ROOT, "data", "kirishsiz", "yuborishga")
TRACKER = os.path.join(ROOT, "data", "kirishsiz", "sorovlar.jsonl")

XATLAR = [
    {
        "fayl": "1_ekologiya_boshqarmasi.txt",
        "tashkilot": "Toshkent shahar ekologiya va atrof-muhitni muhofaza qilish boshqarmasi",
        "tur": "monitoring",
        "obyekt": "Toshkent shimoli-sharqidagi sanoat zonasi",
        "qoshimcha": [R.STANDART_SOROVLAR["isitish-qattiq"]],
    },
    {
        "fayl": "2_ekologiya_inspeksiyasi.txt",
        "tashkilot": "O'zbekiston Respublikasi Ekologiya, atrof-muhitni muhofaza qilish va iqlim "
                     "o'zgarishi vazirligi huzuridagi Ekologik nazorat inspeksiyasi",
        "tur": "inspeksiya",
        "obyekt": "Toshkent shimoli-sharqidagi sanoat zonasi",
        "qoshimcha": [R.STANDART_SOROVLAR["fakel"]],
    },
    {
        "fayl": "3_obyekt_olchov.txt",
        "tashkilot": "⟦obyekt rahbariyati (IES / issiqlik stansiyasi)⟧",
        "tur": "olchov",
        "obyekt": "Toshkent shimoli-sharqidagi sanoat zonasi",
        "qoshimcha": [R.STANDART_SOROVLAR["ruxsatnoma"]],
    },
    {
        "fayl": "4_statistika_boshqarmasi.txt",
        "tashkilot": "Toshkent shahar statistika boshqarmasi (Milliy statistika qo'mitasi)",
        "tur": "gaz-isitish",
        "obyekt": "Toshkent shahri uy xo'jaliklari (isitish mavsumi)",
        "qoshimcha": [R.STANDART_SOROVLAR["isitish-qattiq"]],
    },
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--sana", default=SANA)
    a = ap.parse_args()

    os.makedirs(CHIQISH, exist_ok=True)
    print(f"SO'ROVLAR TO'PLAMI — sana {a.sana} · {len(XATLAR)} xat")
    for x in XATLAR:
        r = R.build_request(x["tashkilot"], x["tur"], x["obyekt"],
                            qoshimcha=x["qoshimcha"], sana=a.sana)
        path = os.path.join(CHIQISH, x["fayl"])
        if not a.dry_run:
            with open(path, "w", encoding="utf-8") as f:
                f.write(r["matn"] + "\n")
            R.tracker_add(TRACKER, r)
        print(f"  ✅ {x['fayl']:32} javob muddati {r['muddat']['javob_sana']} · "
              f"eskalatsiya {r['muddat']['eskalatsiya_sana']}")
    if not a.dry_run:
        print(f"\n  Saqlandi: {CHIQISH}")
        print(f"  Kuzatuv:  {TRACKER}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
