# -*- coding: utf-8 -*-
"""«Kirishsiz» (ruxsatsiz) tekshiruv yo'llari — L1 uchun.

Muammo (real holat): korxona hududiga kirishga va CEMS/hisobot ma'lumotini berishga
ruxsat bermaydi. Demak, pilotning T1–T7 zanjiri (D1–D5 oqimlari) **to'liq bajarilmaydi**
va isbot zanjiri uziladi. Bu paket uzilishni **ochiq manbalar + huquqiy talab** bilan
qoplaydigan yo'llarni kodga aylantiradi.

Tamoyil (TZ-1 §0.1 ruhida): har bir yo'l uchun **nima isbotlanadi / nima isbotlanmaydi**
ochiq yoziladi — «kuchli ko'rinadigan, lekin bo'sh» dalil qurilmaydi.

Yo'llar reyestri: `registry.PATHS` (8 ta) · CLI: `scripts/kirishsiz.py --list`
"""
from __future__ import annotations

from .registry import PATHS, get_path, paths_by_power, registry_json

__all__ = ["PATHS", "get_path", "paths_by_power", "registry_json"]
__version__ = "1.0"
