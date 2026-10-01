# Huquqiy asoslar registri (R54)

**Nima:** loyihaning har bir elementi (kirishsiz yo'llar, modullar, tashkiliy bandlar) rasmiy
hujjatlar bilan **mashinada tekshiriladigan** tarzda bog'langan. Da'vo emas — registr.

```bash
python3 scripts/kirishsiz.py huquqiy                 # to'liq xarita (matn)
python3 scripts/kirishsiz.py huquqiy --xarita        # element → asoslar
python3 scripts/kirishsiz.py huquqiy --qamrov --json # statistika (JSON)
python3 scripts/kirishsiz.py huquqiy --tekshir       # holat: ok / muammolar
python3 scripts/kirishsiz.py huquqiy --havola --element "modul:isitish (yoqilg'i hisobi)"
python3 scripts/build_huquqiy_hujjat.py              # hujjatni registrdan qayta yasash
```

| Ko'rsatkich | Qiymat |
|---|---|
| Hujjatlar | **21** (Konstitutsiya 1 · xalqaro shartnoma 1 · qonun 3 · farmon 7 · qaror 3 · xalqaro majburiyat 1 · standart 5) |
| Elementlar | **22** (8 kirishsiz yo'l · 6 modul · 8 tashkiliy band) |
| Bog'lanishlar | **53** (o'rtacha 2.41, eng kam 2) |
| Darajalar | A 11 (rasmiy) · B 5 (matni keyin) · S 5 (standart) |
| Testlar | `tests/test_kirishsiz_huquqiy.py` — **13** |

**Muhim qoida:** manba havolasi yo'q hujjat **o'ylab topilmaydi** — `izoh` maydoni bilan
belgilanadi va `tekshir()` chiqishida ko'rinadi (`pf-69`, `ghg-qonuni`, `ndc-3`).

**Xatga ta'siri:** `requests_gen.MANBALAR` va xat matnidagi «Huquqiy asos» bloki endi shu
registrdan olinadi (6 asos: Konstitutsiya 49 · Aarhus · ochiqlik qonuni · PQ-343 · PF-69 · muddat).
