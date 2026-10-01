#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ochiq manbalardan ma'lumot yig'ish (kalitsiz / bepul kalit bilan) + provenans jurnali.

Manbalar va holati (2026-10-01 da tekshirilgan):
  open-meteo-aq      havo sifati (CAMS): PM2,5 / NO2 / SO2      — kalit KERAK EMAS ✅ jonli tekshirildi
  open-meteo-wind    shamol (10 m) + harorat                   — kalit KERAK EMAS ✅
  open-meteo-archive tarixiy shamol (ERA5 arxivi)              — kalit KERAK EMAS ✅
  firms              NASA FIRMS issiqlik anomaliyasi (VIIRS)   — bepul MAP_KEY (FIRMS_MAP_KEY)
  openaq             stansiya o'lchovlari (v3)                 — bepul kalit (OPENAQ_API_KEY)
  carbon-mapper      yuqori aniqlikdagi metan kuzatuvlari      — kalit kerak emas (API hujjati)

Har yozuv `data/public/MANIFEST.json` ga tushadi: manba, URL, olingan vaqt (UTC),
qatorlar soni, SHA-256, litsenziya, tekshirish sanasi. Ma'lumot **o'zgartirilmaydi**.

Ishlatish:
  python3 scripts/fetch_public.py --check
  python3 scripts/fetch_public.py --source open-meteo-aq --lat 41.311 --lon 69.240 --kun 7
  python3 scripts/fetch_public.py --source firms --bbox "41.2,69.1,41.5,69.5" --kun 2 --out data/public/firms.csv
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "data", "public")
MANIFEST = os.path.join(OUTDIR, "MANIFEST.json")

LITSENZIYA = {
    "open-meteo-aq": "CC-BY-4.0 (Open-Meteo; CAMS ma'lumoti)",
    "open-meteo-wind": "CC-BY-4.0 (Open-Meteo; ECMWF/ERA5)",
    "open-meteo-archive": "CC-BY-4.0 (Open-Meteo Archive API)",
    "open-meteo-archive-havo": "CC-BY-4.0 (Open-Meteo Archive API; ECMWF/ERA5)",
    "open-meteo-aq-qoshimcha": "CC-BY-4.0 (Open-Meteo; CAMS global)",
    "open-meteo-aq-tarix": "CC-BY-4.0 (Open-Meteo; CAMS tarixi 2022 dan)",
    "firms": "NASA FIRMS — ochiq (manba ko'rsatiladi)",
    "openaq": "CC-BY-4.0 (OpenAQ)",
    "carbon-mapper": "Carbon Mapper ochiq litsenziyasi (plume ma'lumotlari CC-BY-NC-SA bo'lishi mumkin)",
}


# ------------------------------------------------------------------ URL quruvchilar (test uchun)


def url_open_meteo_aq(lat: float, lon: float, kun: int) -> str:
    return ("https://air-quality-api.open-meteo.com/v1/air-quality"
            f"?latitude={lat}&longitude={lon}"
            "&hourly=pm2_5,pm10,nitrogen_dioxide,sulphur_dioxide,carbon_monoxide"
            f"&timezone=Asia%2FTashkent&past_days={kun}&forecast_days=0")


def url_open_meteo_wind(lat: float, lon: float, kun: int) -> str:
    return ("https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            "&hourly=wind_speed_10m,wind_direction_10m,temperature_2m,relative_humidity_2m"
            f"&timezone=Asia%2FTashkent&past_days={kun}&forecast_days=0")


def url_open_meteo_archive(lat: float, lon: float, boshlanish: str, tugash: str) -> str:
    return ("https://archive-api.open-meteo.com/v1/archive"
            f"?latitude={lat}&longitude={lon}&start_date={boshlanish}&end_date={tugash}"
            "&hourly=wind_speed_10m,wind_direction_10m&timezone=Asia%2FTashkent")


def url_open_meteo_archive_havo(lat: float, lon: float, boshlanish: str, tugash: str) -> str:
    """ERA5: harorat + namlik (isitish mavsumi va ikkilamchi aerozol tahlili uchun)."""
    return ("https://archive-api.open-meteo.com/v1/archive"
            f"?latitude={lat}&longitude={lon}&start_date={boshlanish}&end_date={tugash}"
            "&hourly=temperature_2m,relative_humidity_2m,precipitation"
            "&timezone=Asia%2FTashkent")


def url_open_meteo_aq_qoshimcha(lat: float, lon: float, kun: int) -> str:
    """CAMS: chang (dust) va aerozol optik qalinligi — PM2,5 manbasini ajratish uchun."""
    return ("https://air-quality-api.open-meteo.com/v1/air-quality"
            f"?latitude={lat}&longitude={lon}"
            "&hourly=pm2_5,pm10,dust,aerosol_optical_depth"
            "&timezone=Asia%2FTashkent&past_days={kun}&forecast_days=0".format(kun=kun))


def url_open_meteo_aq_tarix(lat: float, lon: float, boshlanish: str, tugash: str) -> str:
    """CAMS tarixi (2022 dan) — A-qatlam oynasini orqaga (o'tgan isitish mavsumiga) uzaytirish uchun."""
    return ("https://air-quality-api.open-meteo.com/v1/air-quality"
            f"?latitude={lat}&longitude={lon}"
            "&hourly=pm2_5,pm10,nitrogen_dioxide,sulphur_dioxide,carbon_monoxide"
            f"&start_date={boshlanish}&end_date={tugash}&timezone=Asia%2FTashkent")


def url_firms(bbox: str, kun: int) -> str:
    key = os.environ.get("FIRMS_MAP_KEY", "")
    if not key:
        raise SystemExit("❌ FIRMS_MAP_KEY env kerak — bepul kalit: https://firms.modaps.eosdis.nasa.gov/api/map_key/")
    return f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{key}/VIIRS_SNPP_NRT/{bbox}/{kun}"


def url_openaq(lat: float, lon: float, radius_m: int = 25000) -> str:
    if not os.environ.get("OPENAQ_API_KEY"):
        raise SystemExit("❌ OPENAQ_API_KEY env kerak — bepul ro'yxat: https://explore.openaq.org/")
    return f"https://api.openaq.org/v3/locations?coordinates={lat},{lon}&radius={radius_m}&limit=100"


# ------------------------------------------------------------------ yuklash va jurnal


def _get(url: str, timeout: int = 30, headers: dict | None = None) -> bytes:
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "egaz-audit/1.0 (ochiq ma'lumot)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310 (ochiq, fiksirlangan domen)
        return r.read()


def save_csv(path: str, sarlavha: list[str], qatorlar: list[list]) -> str:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(sarlavha)
        w.writerows(qatorlar)
    return path


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(65536), b""):
            h.update(blk)
    return h.hexdigest()


def manifest_add(manba: str, url: str, path: str, qatorlar: int, kalit: str) -> dict:
    os.makedirs(OUTDIR, exist_ok=True)
    data = {"yozuvlar": []}
    if os.path.exists(MANIFEST):
        with open(MANIFEST, encoding="utf-8") as f:
            data = json.load(f)
    rec = {
        "manba": manba,
        "url": url,
        "fayl": os.path.relpath(path, ROOT),
        "qatorlar": qatorlar,
        "kalit": kalit,
        "litsenziya": LITSENZIYA.get(manba, "—"),
        "olingan_vaqt_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sha256": sha256(path),
    }
    data["yozuvlar"].append(rec)
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return rec


# ------------------------------------------------------------------ manba ishlovchilari


def fetch_open_meteo_aq(lat: float, lon: float, kun: int, out: str | None) -> dict:
    url = url_open_meteo_aq(lat, lon, kun)
    d = json.loads(_get(url).decode("utf-8"))
    h = d["hourly"]
    rows = [[t, h["pm2_5"][i], h["pm10"][i], h["nitrogen_dioxide"][i],
             h["sulphur_dioxide"][i], h["carbon_monoxide"][i]] for i, t in enumerate(h["time"])]
    path = out or os.path.join(OUTDIR, f"open-meteo-aq_{lat}_{lon}_{kun}k.csv")
    save_csv(path, ["vaqt", "pm2_5_ug_m3", "pm10_ug_m3", "no2_ug_m3", "so2_ug_m3", "co_ug_m3"], rows)
    return manifest_add("open-meteo-aq", url, path, len(rows), "kerak emas")


def fetch_open_meteo_wind(lat: float, lon: float, kun: int, out: str | None) -> dict:
    url = url_open_meteo_wind(lat, lon, kun)
    d = json.loads(_get(url).decode("utf-8"))
    h = d["hourly"]
    rows = [[t, h["wind_speed_10m"][i], h["wind_direction_10m"][i], h["temperature_2m"][i],
             h["relative_humidity_2m"][i]] for i, t in enumerate(h["time"])]
    path = out or os.path.join(OUTDIR, f"open-meteo-wind_{lat}_{lon}_{kun}k.csv")
    save_csv(path, ["vaqt", "shamol_ms", "shamol_yonalishi_grad", "harorat_C", "namlik_foiz"], rows)
    return manifest_add("open-meteo-wind", url, path, len(rows), "kerak emas")


def fetch_open_meteo_archive(lat: float, lon: float, boshlanish: str, tugash: str, out: str | None) -> dict:
    url = url_open_meteo_archive(lat, lon, boshlanish, tugash)
    d = json.loads(_get(url).decode("utf-8"))
    h = d["hourly"]
    rows = [[t, h["wind_speed_10m"][i], h["wind_direction_10m"][i]] for i, t in enumerate(h["time"])]
    path = out or os.path.join(OUTDIR, f"era5-wind_{lat}_{lon}_{boshlanish}_{tugash}.csv")
    save_csv(path, ["vaqt", "shamol_ms", "shamol_yonalishi_grad"], rows)
    return manifest_add("open-meteo-archive", url, path, len(rows), "kerak emas")


def fetch_open_meteo_archive_havo(lat: float, lon: float, boshlanish: str, tugash: str,
                                   out: str | None) -> dict:
    url = url_open_meteo_archive_havo(lat, lon, boshlanish, tugash)
    d = json.loads(_get(url).decode("utf-8"))
    h = d["hourly"]
    rows = [[t, h["temperature_2m"][i], h["relative_humidity_2m"][i], h["precipitation"][i]]
            for i, t in enumerate(h["time"])]
    path = out or os.path.join(OUTDIR, f"era5-havo_{lat}_{lon}_{boshlanish}_{tugash}.csv")
    save_csv(path, ["vaqt", "harorat_C", "namlik_foiz", "yogin_mm"], rows)
    return manifest_add("open-meteo-archive-havo", url, path, len(rows), "kerak emas")


def fetch_open_meteo_aq_qoshimcha(lat: float, lon: float, kun: int, out: str | None) -> dict:
    url = url_open_meteo_aq_qoshimcha(lat, lon, kun)
    d = json.loads(_get(url).decode("utf-8"))
    h = d["hourly"]
    rows = [[t, h["pm2_5"][i], h["pm10"][i], h["dust"][i], h["aerosol_optical_depth"][i]]
            for i, t in enumerate(h["time"])]
    path = out or os.path.join(OUTDIR, f"cams-qoshimcha_{lat}_{lon}_{kun}k.csv")
    save_csv(path, ["vaqt", "pm2_5_ug_m3", "pm10_ug_m3", "chang_ug_m3", "aod"], rows)
    return manifest_add("open-meteo-aq-qoshimcha", url, path, len(rows), "kerak emas")


def fetch_open_meteo_aq_tarix(lat: float, lon: float, boshlanish: str, tugash: str,
                              out: str | None) -> dict:
    url = url_open_meteo_aq_tarix(lat, lon, boshlanish, tugash)
    d = json.loads(_get(url, timeout=90).decode("utf-8"))
    h = d["hourly"]
    rows = [[t, h["pm2_5"][i], h["pm10"][i], h["nitrogen_dioxide"][i],
             h["sulphur_dioxide"][i], h["carbon_monoxide"][i]] for i, t in enumerate(h["time"])]
    path = out or os.path.join(OUTDIR, f"aq-tarix_{lat}_{lon}_{boshlanish}_{tugash}.csv")
    save_csv(path, ["vaqt", "pm2_5_ug_m3", "pm10_ug_m3", "no2_ug_m3", "so2_ug_m3", "co_ug_m3"], rows)
    return manifest_add("open-meteo-aq-tarix", url, path, len(rows), "kerak emas")


def fetch_firms(bbox: str, kun: int, out: str | None) -> dict:
    url = url_firms(bbox, kun)
    matn = _get(url).decode("utf-8", errors="replace")
    path = out or os.path.join(OUTDIR, f"firms_{bbox.replace(',', '_')}_{kun}k.csv")
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(matn)
    qatorlar = max(len(matn.strip().split("\n")) - 1, 0)
    return manifest_add("firms", url.split("/area/csv/")[0] + "/api/area/ (MAP_KEY yashirilgan)", path,
                        qatorlar, "FIRMS_MAP_KEY")


def fetch_openaq(lat: float, lon: float, out: str | None) -> dict:
    url = url_openaq(lat, lon)
    d = json.loads(_get(url, headers={"X-API-Key": os.environ["OPENAQ_API_KEY"],
                                      "User-Agent": "egaz-audit/1.0"}).decode("utf-8"))
    rows = []
    for loc in d.get("results", []):
        rows.append([loc.get("id"), loc.get("name"), loc.get("coordinates", {}).get("latitude"),
                     loc.get("coordinates", {}).get("longitude"), loc.get("country", {}).get("code"),
                     ",".join(s.get("parameter", {}).get("name", "") for s in loc.get("sensors", []))])
    path = out or os.path.join(OUTDIR, f"openaq-stansiyalar_{lat}_{lon}.csv")
    save_csv(path, ["id", "nomi", "lat", "lon", "davlat", "sensorlar"], rows)
    return manifest_add("openaq", "https://api.openaq.org/v3/locations", path, len(rows), "OPENAQ_API_KEY")


CHECK_URLS = {
    "open-meteo-aq": "https://air-quality-api.open-meteo.com/v1/air-quality?latitude=41.31&longitude=69.24&hourly=pm2_5&past_days=1&forecast_days=0",
    "open-meteo-wind": "https://api.open-meteo.com/v1/forecast?latitude=41.31&longitude=69.24&hourly=wind_speed_10m&past_days=1&forecast_days=0",
    "open-meteo-archive": "https://archive-api.open-meteo.com/v1/archive?latitude=41.31&longitude=69.24&start_date=2026-09-01&end_date=2026-09-02&hourly=wind_speed_10m",
    "firms (kalit kerak)": "https://firms.modaps.eosdis.nasa.gov/api/map_key/",
    "openaq (kalit kerak)": "https://api.openaq.org/v3/locations?limit=1",
    # hujjat sahifasi 200 beradi; aniq endpoint yo'li hali tekshirilmagan (xato da'vo qilmaymiz)
    "carbon-mapper (hujjat)": "https://api.carbonmapper.org/api/v1/docs",
}


def check() -> int:
    ok = 0
    for nom, url in CHECK_URLS.items():
        try:
            _get(url, timeout=20)
            print(f"✅ {nom}")
            ok += 1
        except urllib.error.HTTPError as e:
            izoh = "kalit/royxat kerak" if e.code in (401, 403) else "xato"
            print(f"⚠️  {nom} — HTTP {e.code} ({izoh})")
        except Exception as e:  # noqa: BLE001
            print(f"❌ {nom} — {type(e).__name__}: {e}")
    print(f"\nNatija: {ok}/{len(CHECK_URLS)} manba javob berdi")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Ochiq manbalardan ma'lumot yig'ish (provenans bilan)")
    ap.add_argument("--check", action="store_true", help="manbalar mavjudligini tekshirish")
    ap.add_argument("--source", choices=["open-meteo-aq", "open-meteo-wind", "open-meteo-archive",
                                         "open-meteo-archive-havo", "open-meteo-aq-qoshimcha",
                                         "open-meteo-aq-tarix", "firms", "openaq"])
    ap.add_argument("--lat", type=float, default=41.311)
    ap.add_argument("--lon", type=float, default=69.240)
    ap.add_argument("--kun", type=int, default=7)
    ap.add_argument("--bbox", default="41.2,69.1,41.5,69.5")
    ap.add_argument("--boshlanish", default="2026-09-01")
    ap.add_argument("--tugash", default="2026-09-30")
    ap.add_argument("--out")
    a = ap.parse_args()

    if a.check:
        return check()
    if not a.source:
        ap.print_help()
        return 1
    if a.source == "open-meteo-aq":
        rec = fetch_open_meteo_aq(a.lat, a.lon, a.kun, a.out)
    elif a.source == "open-meteo-wind":
        rec = fetch_open_meteo_wind(a.lat, a.lon, a.kun, a.out)
    elif a.source == "open-meteo-archive":
        rec = fetch_open_meteo_archive(a.lat, a.lon, a.boshlanish, a.tugash, a.out)
    elif a.source == "open-meteo-archive-havo":
        rec = fetch_open_meteo_archive_havo(a.lat, a.lon, a.boshlanish, a.tugash, a.out)
    elif a.source == "open-meteo-aq-qoshimcha":
        rec = fetch_open_meteo_aq_qoshimcha(a.lat, a.lon, a.kun, a.out)
    elif a.source == "open-meteo-aq-tarix":
        rec = fetch_open_meteo_aq_tarix(a.lat, a.lon, a.boshlanish, a.tugash, a.out)
    elif a.source == "firms":
        rec = fetch_firms(a.bbox, a.kun, a.out)
    else:
        rec = fetch_openaq(a.lat, a.lon, a.out)
    print(f"✅ {rec['manba']}: {rec['fayl']} ({rec['qatorlar']} qator) · sha256 {rec['sha256'][:12]}…")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
