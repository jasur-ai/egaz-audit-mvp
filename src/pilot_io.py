# -*- coding: utf-8 -*-
"""TZ-1 pilot ma'lumotini qabul qilish, tekshirish va audit izini yuritish.

Manba: `YAKUNIY/6-TZ-1-Shovqin-Pilot.md`
  §4.2 — fayl sxemasi (kolonkalar, vaqt, birlik, kalit)
  §4.3 — sifat nazorati (takroriy kalit, yetishmayotgan oyna, birlik mosligi)
  §4.6 — audit izi (SHA-256, yuklash vaqti, kim yukladi, qatorlar soni, append-only)

Modul **hech narsani o'zgartirmaydi**: faqat o'qiydi, tekshiradi va hisobot beradi.
Qoida buzilsa — fayl «rad etiladi» (TZ-1 §4.3: «Fayl qaytariladi»), qisman qabul qilinmaydi.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd

# ------------------------------------------------------------------ konstantalar

REQUIRED_COLS = ["obyekt_id", "modda", "oyna_boshi", "qiymat", "birlik", "valid", "manba"]
OPTIONAL_COLS = ["izoh"]

# TZ-1 §4.2: SO2/NOx/CO — mg/m³, PM — µg/m³ (aralash birlik qabul qilinmaydi)
EXPECTED_UNIT = {"SO2": "mg/m3", "NOx": "mg/m3", "CO": "mg/m3", "PM": "ug/m3"}
MANBA_ALLOWED = {"cems", "hisobot", "etalon"}

WINDOW_MIN = 20                      # 20 daqiqalik oyna
WINDOWS_PER_DAY = 24 * 60 // WINDOW_MIN          # 72
MISSING_LIMIT = 0.10                 # §4.3: oyiga >10% bo'shliq → «shartli»

_UNIT_ALIASES = {
    "mg/m3": "mg/m3", "mg/m³": "mg/m3", "mg/m^3": "mg/m3",
    "ug/m3": "ug/m3", "µg/m³": "ug/m3", "μg/m³": "ug/m3", "ug/m³": "ug/m3",
    "µg/m3": "ug/m3", "μg/m3": "ug/m3",
}


def normalize_birlik(raw: Any) -> str | None:
    """Birlik yozuvini kanonik ko'rinishga keltiradi; noma'lum bo'lsa None."""
    if raw is None or (isinstance(raw, float) and np.isnan(raw)):
        return None
    return _UNIT_ALIASES.get(str(raw).strip().lower().replace(" ", ""))


def _as_bool(v: Any) -> bool | None:
    """`valid` ustunini bool ga aylantiradi (true/false/1/0/ha/yo'q)."""
    if isinstance(v, bool):
        return v
    s = str(v).strip().lower()
    if s in {"true", "1", "ha", "yes", "y"}:
        return True
    if s in {"false", "0", "yo'q", "yoq", "no", "n"}:
        return False
    return None


# ------------------------------------------------------------------ o'qish

def read_csv(path: str) -> pd.DataFrame:
    """CSV ni UTF-8 da o'qiydi (sarlavha qatori majburiy — TZ-1 §4.2)."""
    return pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8")


def validate(df: pd.DataFrame) -> dict:
    """Fayl mazmunini TZ-1 §4.2/§4.3 bo'yicha tekshiradi.

    Qaytadi: {"ok": bool, "errors": [...], "warnings": [...], "stats": {...}, "objects": [...]}
    """
    errors: list[str] = []
    warnings: list[str] = []
    stats: dict[str, Any] = {}

    cols = [c.strip() for c in df.columns]
    df = df.rename(columns=dict(zip(df.columns, cols)))

    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        errors.append(f"Majburiy kolonkalar yo'q: {', '.join(missing)}")
        return {"ok": False, "errors": errors, "warnings": warnings, "stats": stats, "objects": []}

    unknown = [c for c in df.columns if c not in REQUIRED_COLS + OPTIONAL_COLS]
    if unknown:
        warnings.append(f"Ortiqcha kolonkalar (hisobga olinmaydi): {', '.join(unknown)}")

    if df.empty:
        errors.append("Fayl bo'sh (qator yo'q)")
        return {"ok": False, "errors": errors, "warnings": warnings, "stats": stats, "objects": []}

    stats["qatorlar"] = int(len(df))

    # --- vaqt: ISO-8601, mahalliy offset MAJBURIY (+05:00), 20 daqiqaga karrali
    raw_time = df["oyna_boshi"].astype(str).str.strip()
    has_offset = raw_time.str.contains(r"[+-]\d{2}:?\d{2}$|Z$", regex=True)
    if (~has_offset).any():
        n = int((~has_offset).sum())
        errors.append(f"{n} qatorda vaqt offseti yo'q (ISO-8601 UTC+5 talab qilinadi, masalan 2026-12-07T08:20:00+05:00)")

    t = pd.to_datetime(raw_time, errors="coerce", utc=True, format="ISO8601")
    bad_time = t.isna()
    if bad_time.any():
        errors.append(f"{int(bad_time.sum())} qatorda vaqt o'qilmadi (format xato)")
    t_local = t.dt.tz_convert("Asia/Tashkent")
    minute = t_local.dt.minute.fillna(-1).astype(int)
    sec = t_local.dt.second.fillna(-1).astype(int)
    misaligned = (minute % WINDOW_MIN != 0) | (sec != 0)
    if misaligned.any():
        errors.append(f"{int(misaligned.sum())} qatorda oyna boshi 20 daqiqaga karrali emas (§4.2: oyna boshlanishi yoziladi)")
    df = df.assign(_t=t_local)

    # --- modda / birlik
    modda = df["modda"].astype(str).str.strip()
    bad_modda = ~modda.isin(EXPECTED_UNIT)
    if bad_modda.any():
        errors.append(f"Noma'lum modda: {sorted(set(modda[bad_modda]))[:5]} (ruxsat: {sorted(EXPECTED_UNIT)})")

    unit = df["birlik"].map(normalize_birlik)
    bad_unit = unit.isna()
    if bad_unit.any():
        errors.append(f"{int(bad_unit.sum())} qatorda birlik noma'lum/bo'sh (ruxsat: mg/m³, µg/m³)")
    # Birlik moddaga mos keladimi (faqat modda va birlik o'qilgan qatorlarda)
    ok_rows = (~bad_modda) & (~bad_unit)
    expected = modda[ok_rows].map(EXPECTED_UNIT)
    mism = unit[ok_rows].to_numpy(dtype=object) != expected.to_numpy(dtype=object)
    unit_mismatch = pd.Series(False, index=df.index, dtype=bool)
    unit_mismatch.loc[ok_rows] = mism
    if unit_mismatch.any():
        ex = df[unit_mismatch].head(3)[["obyekt_id", "modda", "birlik"]].to_dict("records")
        errors.append(f"{int(unit_mismatch.sum())} qatorda birlik moddaga mos emas: {ex}")

    # --- qiymat va valid
    qiymat = pd.to_numeric(df["qiymat"].astype(str).str.strip().replace({"": None}), errors="coerce")
    valid_flag = df["valid"].map(_as_bool)
    if valid_flag.isna().any():
        errors.append(f"{int(valid_flag.isna().sum())} qatorda `valid` tushunarsiz (true/false bo'lishi kerak)")
    valid_bool = valid_flag.fillna(False)
    # §4.2: bo'sh qiymat faqat valid=false bilan yoziladi
    empty_not_invalid = qiymat.isna() & valid_bool
    if empty_not_invalid.any():
        errors.append(f"{int(empty_not_invalid.sum())} qatorda qiymat bo'sh, lekin valid=true")
    not_empty_invalid = qiymat.notna() & ~valid_bool
    if not_empty_invalid.any():
        warnings.append(f"{int(not_empty_invalid.sum())} qatorda qiymat bor, lekin valid=false (juftlikka kirmaydi)")
    negative = (qiymat < 0).fillna(False)
    if negative.any():
        errors.append(f"{int(negative.sum())} qatorda manfiy qiymat")

    # --- manba
    manba = df["manba"].astype(str).str.strip().str.lower()
    bad_manba = ~manba.isin(MANBA_ALLOWED)
    if bad_manba.any():
        errors.append(f"Noma'lum manba: {sorted(set(manba[bad_manba]))[:5]} (ruxsat: {sorted(MANBA_ALLOWED)})")

    # --- takroriy kalit (§4.3: >0 bo'lsa fayl qaytariladi)
    # Kalit to'rt qismli: `manba` kirmasa, bir oynada cems va hisobot qatori birga turolmaydi
    # (TZ-1 §4.2 sxemasida `manba` ustuni bor) — bu aniqlashtirish T1 paketida qayd etilgan.
    key = df[["obyekt_id", "modda", "oyna_boshi", "manba"]].astype(str).agg("|".join, axis=1)
    dup_mask = key.duplicated(keep=False)
    n_dup = int(dup_mask.sum())
    if n_dup:
        sample = df[dup_mask].head(3)[["obyekt_id", "modda", "oyna_boshi", "manba"]].to_dict("records")
        errors.append(f"Takroriy kalit: {n_dup} qator (kalit: obyekt_id|modda|oyna_boshi|manba) — masalan {sample}")

    df = df.assign(_qiymat=qiymat, _valid=valid_bool, _manba=manba, _birlik=unit)

    # --- yetishmayotgan oyna (§4.3): CEMS uchun oy kesimida
    # Bo'shliq fayl QAMROVI (min…max oyna) asosida o'lchanadi: oy boshidan emas — aks holda
    # qisqa (kunlik) fayl soxta «shartli» bo'lib chiqadi. Choralar TZ-1 §4.3 bo'yicha.
    objects: list[dict] = []
    cems = df[(df["_manba"] == "cems") & df["_t"].notna()]
    for (oid, md), g in cems.groupby(["obyekt_id", "modda"]):
        row: dict[str, Any] = {"obyekt_id": oid, "modda": md, "holat": "qabul", "sabab": [],
                               "qamrov_boshi": str(g["_t"].min()), "qamrov_oxiri": str(g["_t"].max())}
        for (y, mth), gm in g.groupby([g["_t"].dt.year, g["_t"].dt.month]):
            m_start = gm["_t"].min()          # fayl qamrovi: oy boshidan emas, birinchi oynadan
            m_end = gm["_t"].max()
            span_slots = int((m_end - m_start).total_seconds() // (WINDOW_MIN * 60)) + 1
            observed = int(gm["_t"].nunique())
            share = max(0.0, 1.0 - observed / max(1, span_slots))
            row[f"{y}-{mth:02d}"] = round(share, 4)
            if share > MISSING_LIMIT:
                row["holat"] = "shartli"
                row["sabab"].append(f"{y}-{mth:02d}: {share:.1%} bo'shliq (qamrov ichida, >10%) — D3 jurnalidan izohlansin")
        row["holat_sababi"] = "; ".join(row["sabab"]) if row["sabab"] else ""
        objects.append(row)

    stats.update({
        "cems_qatorlar": int((df["_manba"] == "cems").sum()),
        "hisobot_qatorlar": int((df["_manba"] == "hisobot").sum()),
        "etalon_qatorlar": int((df["_manba"] == "etalon").sum()),
        "valid_true": int(df["_valid"].sum()),
        "valid_false": int((~df["_valid"]).sum()),
        "takroriy_kalit": n_dup,
        "obyektlar": sorted(set(df["obyekt_id"].astype(str))),
        "moddalar": sorted(set(modda)),
    })
    return {"ok": not errors, "errors": errors, "warnings": warnings, "stats": stats, "objects": objects,
            "_df": df}


# ------------------------------------------------------------------ juftliklar

def pair_windows(df: pd.DataFrame) -> dict:
    """CEMS ↔ hisobot juftliklarini tuzadi: farq = hisobot − CEMS (belgili, TZ-1 §1).

    Faqat `valid=true` qatorlar olinadi; bir xil (obyekt_id, modda, oyna_boshi) kalitda
    ikkala manba bo'lishi shart.
    """
    d = df[df["_valid"] & df["_t"].notna()].copy()
    idx = ["obyekt_id", "modda", "_t"]
    cems = d[d["_manba"] == "cems"].set_index(idx)["_qiymat"]
    rep = d[d["_manba"] == "hisobot"].set_index(idx)["_qiymat"]
    cems = cems[~cems.index.duplicated()]
    rep = rep[~rep.index.duplicated()]
    joined = pd.concat({"cems": cems, "hisobot": rep}, axis=1, join="inner").dropna()
    if joined.empty:
        return {"n": 0, "juftliklar": joined.reset_index(), "xulosa": {}}

    farq = joined["hisobot"] - joined["cems"]
    rel = farq / joined["cems"].replace(0, np.nan)
    out = {
        "n": int(len(joined)),
        "juftliklar": joined.assign(farq=farq, nisbiy=rel).reset_index(),
        "xulosa": {
            "n": int(len(joined)),
            "median_farq": float(np.median(farq)),
            "median_nisbiy": float(np.nanmedian(rel)) if rel.notna().any() else None,
            "MAD": float(np.median(np.abs(farq - np.median(farq)))),
            "musbat_ulush": float((farq > 0).mean()),
            "q5": float(np.quantile(farq, 0.05)),
            "q25": float(np.quantile(farq, 0.25)),
            "q50": float(np.quantile(farq, 0.50)),
            "q75": float(np.quantile(farq, 0.75)),
            "q95": float(np.quantile(farq, 0.95)),
        },
    }
    return out


# ------------------------------------------------------------------ audit izi

def audit_record(path: str, role: str = "operator", extra: dict | None = None) -> dict:
    """§4.6: SHA-256, hajm, qatorlar, vaqt (UTC), kim yukladi."""
    h = hashlib.sha256()
    n_bytes = 0
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
            n_bytes += len(chunk)
    rec = {
        "fayl": os.path.basename(path),
        "sha256": h.hexdigest(),
        "bayt": n_bytes,
        "qatorlar": sum(1 for _ in open(path, encoding="utf-8")) - 1,
        "yuklangan": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "rol": role,
    }
    if extra:
        rec.update(extra)
    return rec


def append_audit(rec: dict, audit_path: str) -> None:
    """Audit yozuvini **append-only** jurnalga qo'shadi (mavjud satrlar o'zgarmaydi)."""
    os.makedirs(os.path.dirname(audit_path) or ".", exist_ok=True)
    with open(audit_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


# ------------------------------------------------------------------ yuqori daraja

def validate_file(path: str, role: str = "operator", audit_path: str | None = None) -> dict:
    """Fayl → tekshiruv → (ixtiyoriy) audit yozuvi. Qaytadi: report (audit maydoni bilan)."""
    df = read_csv(path)
    rep = validate(df)
    rec = audit_record(path, role=role, extra={"natija": "qabul" if rep["ok"] else "rad etildi"})
    rep["audit"] = rec
    if audit_path:
        append_audit(rec, audit_path)
    if rep["ok"]:
        rep["juftliklar"] = pair_windows(rep["_df"])["xulosa"]
    return rep


def sample_rows(n_objects: int = 1, windows: int = 6, seed: int = 42) -> pd.DataFrame:
    """Namuna fayl («korxona shu shaklda to'ldiradi»): CEMS + hisobot, 20 daqiqalik oyna."""
    rng = np.random.default_rng(seed)
    base = pd.Timestamp("2026-12-07T08:00:00+05:00")
    rows = []
    for o in range(1, n_objects + 1):
        oid = f"K-{o}"
        for i in range(windows):
            t = base + pd.Timedelta(minutes=WINDOW_MIN * i)
            cems = float(rng.normal(420, 12))
            his = float(cems * (1 + rng.normal(0.030, 0.010)))   # ~3% surilish
            for manba, qiymat in (("cems", cems), ("hisobot", his)):
                rows.append({
                    "obyekt_id": oid, "modda": "NOx", "oyna_boshi": t.isoformat(),
                    "qiymat": round(qiymat, 3), "birlik": "mg/m³", "valid": "true",
                    "manba": manba, "izoh": "",
                })
    return pd.DataFrame(rows)[REQUIRED_COLS + OPTIONAL_COLS]
