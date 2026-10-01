#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TZ-1 pilot faylini tekshirish (qabul/rad etish) va audit izini yozish.

Ishlatish:
  python3 scripts/validate_pilot_data.py --file data/pilot/K-1_2026-12.csv --role analyst
  python3 scripts/validate_pilot_data.py --file … --json          # mashina o'qiydigan hisobot
  python3 scripts/validate_pilot_data.py --sample data/pilot/NAMUNA.csv   # namuna fayl (korxona uchun)
  python3 scripts/validate_pilot_data.py --selftest               # o'zini sinash (yaxshi/yomon fayl)

TZ-1 §4.3: takroriy kalit, birlik mosligi, yetishmayotgan oyna — shu yerda avtomatik tekshiriladi.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import pilot_io as P  # noqa: E402


def print_report(rep: dict, verbose: bool = True) -> None:
    s = rep["stats"]
    holat = "✅ QABUL" if rep["ok"] else "❌ RAD ETILDI"
    print(f"{holat} · qatorlar={s.get('qatorlar')} · obyektlar={s.get('obyektlar')} · moddalar={s.get('moddalar')}")
    print(f"  manbalar: cems={s.get('cems_qatorlar')} hisobot={s.get('hisobot_qatorlar')} etalon={s.get('etalon_qatorlar')}"
          f" · valid: {s.get('valid_true')}/{s.get('qatorlar')}")
    for e in rep["errors"]:
        print(f"  ❌ {e}")
    for w in rep["warnings"]:
        print(f"  ⚠️  {w}")
    if rep.get("objects"):
        print("  Obyekt holati (yetishmayotgan oyna nazorati):")
        for o in rep["objects"]:
            belgi = "🟢" if o["holat"] == "qabul" else "🟡"
            oylar = {k: v for k, v in o.items() if len(k) == 7 and k[4] == "-"}
            print(f"    {belgi} {o['obyekt_id']} · {o['modda']} · {o['holat']}"
                  + (f" · bo'shliq: {oylar}" if oylar else "")
                  + (f" · {o['holat_sababi']}" if o["holat_sababi"] else ""))
    if verbose and rep.get("juftliklar"):
        x = rep["juftliklar"]
        print(f"  Juftliklar (hisobot − CEMS): n={x['n']} · median={x['median_farq']:.3f}"
              f" · MAD={x['MAD']:.3f} · musbat ulush={x['musbat_ulush']:.0%}")
        print(f"    kvantillar: q5={x['q5']:.3f} q25={x['q25']:.3f} q50={x['q50']:.3f} q75={x['q75']:.3f} q95={x['q95']:.3f}")
    a = rep.get("audit")
    if a:
        print(f"  Audit izi: sha256={a['sha256'][:16]}… · bayt={a['bayt']} · rol={a['rol']} · {a['yuklangan']}")


def selftest() -> int:
    """Yaxshi va nuqsonli fayllarni yasab, tekshiruvni sinaydi (CI uchun)."""
    with tempfile.TemporaryDirectory() as d:
        good = os.path.join(d, "good.csv")
        P.sample_rows(n_objects=1, windows=6).to_csv(good, index=False, encoding="utf-8")
        rep = P.validate_file(good, audit_path=os.path.join(d, "audit.jsonl"))
        ok1 = rep["ok"] and rep["juftliklar"]["n"] == 6
        print(f"  1) yaxshi fayl: {'✅ qabul' if rep['ok'] else '❌ xato'} · juftlik n={rep.get('juftliklar', {}).get('n')}")

        df = P.sample_rows(n_objects=1, windows=6)
        bad = pd_concat_bad(df)
        badp = os.path.join(d, "bad.csv")
        bad.to_csv(badp, index=False, encoding="utf-8")
        rep2 = P.validate(bad)
        ok2 = (not rep2["ok"]) and any("Takroriy kalit" in e for e in rep2["errors"]) \
            and any("mos emas" in e for e in rep2["errors"]) and any("offseti yo'q" in e for e in rep2["errors"])
        print(f"  2) nuqsonli fayl: {'✅ rad etildi' if not rep2['ok'] else '❌ o`tdi'}"
              f" · xatolar={len(rep2['errors'])} (kalit/birlik/offset uchovi ham bormi: {ok2})")
        return 0 if (ok1 and ok2) else 1


def pd_concat_bad(df):
    import pandas as pd
    bad = df.copy()
    # 1) birlik mos emas (PM ni mg/m³ da yozish)
    bad.loc[bad.index[0], "modda"] = "PM"
    bad.loc[bad.index[0], "birlik"] = "mg/m³"
    # 2) offset yo'q
    bad.loc[bad.index[1], "oyna_boshi"] = "2026-12-07T09:20:00"
    # 3) takroriy kalit
    dup = bad.iloc[[2]].copy()
    return pd.concat([bad, dup], ignore_index=True)


def main() -> int:
    ap = argparse.ArgumentParser(description="TZ-1 pilot faylini tekshirish (qabul/rad)")
    ap.add_argument("--file", help="tekshiriladigan CSV")
    ap.add_argument("--role", default=os.environ.get("PILOT_ROLE", "operator"), help="kim yukladi (audit izi)")
    ap.add_argument("--audit", default=os.environ.get("PILOT_AUDIT", "data/pilot/audit_log.jsonl"),
                    help="append-only audit jurnali yo'li")
    ap.add_argument("--no-audit", action="store_true", help="audit yozmasdan tekshirish")
    ap.add_argument("--json", action="store_true", help="mashina o'qiydigan hisobot")
    ap.add_argument("--sample", help="namuna fayl yozadi (korxonaga yuboriladi)")
    ap.add_argument("--selftest", action="store_true", help="o'zini sinash")
    args = ap.parse_args()

    if args.selftest:
        print("SELFTEST — pilot IO (yaxshi/nuqsonli fayl):")
        rc = selftest()
        print("NATIJA:", "✅ hammasi joyida" if rc == 0 else "❌ yiqildi")
        return rc

    if args.sample:
        df = P.sample_rows(n_objects=1, windows=6)
        os.makedirs(os.path.dirname(args.sample) or ".", exist_ok=True)
        df.to_csv(args.sample, index=False, encoding="utf-8")
        print(f"✅ Namuna yozildi: {args.sample} · {len(df)} qator · kolonkalar: {list(df.columns)}")
        print("   ⓘ Korxona shu shaklda to'ldiradi: 20 daqiqalik oyna, ISO-8601 offset bilan, birlik ustunida.")
        return 0

    if not args.file:
        print("--file yoki --sample yoki --selftest kerak (--help)")
        return 1

    audit_path = None if args.no_audit else args.audit
    rep = P.validate_file(args.file, role=args.role, audit_path=audit_path)
    if args.json:
        out = {k: v for k, v in rep.items() if k != "_df"}
        if "juftliklar" in out and isinstance(out["juftliklar"], dict):
            pass
        print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
    else:
        print(f"Fayl: {args.file}")
        print_report(rep)
        if audit_path:
            print(f"  Audit jurnali: {audit_path} (append-only)")
    return 0 if rep["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
