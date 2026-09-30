# -*- coding: utf-8 -*-
"""Model monitoring ishga tushirish (S8 real qismi).

    python3 scripts/run_monitor.py
"""
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

from src import monitor  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(0 if monitor.run(
        os.path.join(BASE, "data", "features_v1.csv.gz"),
        os.path.join(BASE, "models"),
        os.path.join(BASE, "reports"),
        os.path.join(BASE, "reports", "figures"),
    ) else 1)
