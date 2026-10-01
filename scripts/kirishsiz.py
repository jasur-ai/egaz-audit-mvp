#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""«Kirishsiz» yo'llar CLI — korxona ruxsatisiz ishlaydigan tekshiruv qurollari.

  python3 scripts/kirishsiz.py --list
  python3 scripts/kirishsiz.py ekran --lat 41.311 --lon 69.240 --kun 7 [--json out.json]
  python3 scripts/kirishsiz.py band --faoliyat 1200000 --ef-low 0.9 --ef-high 2.1 --hisobot 2600
  python3 scripts/kirishsiz.py benford --qiymatlar 12.5,120,12.3,0.00456,7,45,310,2.2,88
  python3 scripts/kirishsiz.py orbita --kesim 0.001,0.002,0.0015 --shamol 3 --dx 3500
  python3 scripts/kirishsiz.py transsect --c 1e-6 --shamol 3 --sigma-z 20 --h 10
  python3 scripts/kirishsiz.py ekran --kun 180 --shamol-fayl data/public/wind_era5_180kun.csv
  python3 scripts/kirishsiz.py nomzodlar --radius 30
  python3 scripts/kirishsiz.py sektor --haqiqiy --radius 30 --modda pm2_5,no2,so2
  python3 scripts/kirishsiz.py sorov --tashkilot "Ekologiya boshqarmasi" --tur olchov --tracker data/kirishsiz/sorovlar.jsonl
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from src.kirishsiz import bands, benford, plume, requests_gen, screener  # noqa: E402
from src.kirishsiz.registry import PATHS, conclusion_rule  # noqa: E402


def _nums(s: str) -> list[float]:
    return [float(x) for x in s.replace(";", ",").split(",") if x.strip()]


def _print_json(d) -> None:
    print(json.dumps(d, ensure_ascii=False, indent=2))


# ------------------------------------------------------------------ buyruqlar


def cmd_list(a) -> int:
    if a.json:
        _print_json({"yollar": PATHS, "qoida": conclusion_rule()})
        return 0
    print(f"{'ID':<20}{'kuch':<6}{'ruxsat':<9}nomi")
    print("-" * 96)
    for p in sorted(PATHS, key=lambda x: -x["isbot_kuchi"]):
        print(f"{p['id']:<20}{p['isbot_kuchi']:<6}{'kerak emas':<12}{p['nomi']}")
    print("\n" + conclusion_rule()["qoida"])
    print(conclusion_rule()["taqiq"])
    return 0


def _rows(path: str) -> list:
    import csv as _csv
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return list(_csv.DictReader(f))


def cmd_ekran(a) -> int:
    from scripts.fetch_public import fetch_open_meteo_aq, fetch_open_meteo_wind  # noqa: E402
    rec = fetch_open_meteo_aq(a.lat, a.lon, a.kun, a.out_csv)
    if a.shamol_fayl:
        rec_w = {"fayl": a.shamol_fayl, "manba": "fayl (berilgan shamol CSV)"}
    else:
        rec_w = fetch_open_meteo_wind(a.lat, a.lon, a.kun, a.out_wind)

    aq = _rows(rec["fayl"])
    wd = _rows(rec_w["fayl"])
    times = [r["vaqt"] for r in aq]
    vals = [r["pm2_5_ug_m3"] for r in aq]
    wind_times = [r["vaqt"] for r in wd]
    winds = [r["shamol_yonalishi_grad"] for r in wd]

    nomzodlar = []
    for spec in a.obyekt or []:
        try:
            nom, la, lo = spec.split(":")
            nomzodlar.append({"nom": nom, "lat": float(la), "lon": float(lo)})
        except ValueError:
            print(f"⚠️  --obyekt formati nom:lat:lon bo'lishi kerak: {spec}")

    juft = screener.dirty_hours_by_time(times, vals, wind_times, winds, a.soatlik_norma)
    dh = juft["soatlar"]
    for h in dh:
        h["receptor_lat"], h["receptor_lon"] = a.lat, a.lon

    rep = screener.screen_report(times, vals, norm=a.norma,
                                 dirty_hours_wind=dh if nomzodlar else None,
                                 candidates=nomzodlar or None)
    rep["soatlik_juftlash"] = {"oshgan_soat": juft["oshgan"], "shamoli_bor": len(dh),
                               "shamol_yoq": juft["shamol_yoq"], "qamrov": round(juft["qamrov"], 3),
                               "shamol_manbasi": rec_w.get("manba", "Open-Meteo shamol")}
    if a.json:
        _print_json(rep)
        return 0

    e = rep["oshish"]
    print(f"EKRAN — {rec['fayl']} · manba: Open-Meteo (CAMS) · norma {rep['norma']} µg/m³ (SanQvaM 0053-23)")
    print(f"  tekshirilgan kunlar: {e['tekshirilgan_kunlar']} · yaroqsiz: {e['yaroqsiz_kunlar']} · "
          f"normadan oshgan: {e['oshgan_kunlar']} ({e['ulush']:.0%}) · eng yuqori {e['eng_yuqori']} µg/m³")
    for d in rep["kunlik"]:
        belgi = "⚠" if d["yaroqli"] and d["qiymat"] and d["qiymat"] > rep["norma"] else " "
        print(f"   {belgi} {d['kun']}  {d['qiymat'] if d['qiymat'] is not None else '—':>6}  "
              f"(qamrov {d['qamrov']:.0%})")
    sj = rep["soatlik_juftlash"]
    print(f"  Soatlik chegara {a.soatlik_norma:g} µg/m³: oshgan {sj['oshgan_soat']} soat · "
          f"shamoli bor {sj['shamoli_bor']} ({sj['qamrov']:.0%}) · shamol yo'q {sj['shamol_yoq']}")
    if "atributsiya" in rep:
        at = rep["atributsiya"]
        print(f"\n  Nomzodlar ({at['soatlar']} oshgan soat bo'yicha):")
        for c in at["nomzodlar"]:
            print(f"   • {c['nom']:<28} {c['hits']:>3} soat ({c['ulush']:.0%}) · "
                  f"o'rt. burchak xatosi {c['ort_burchak_xatosi']}° · {c['masofa_km']} km")
        if at["barobar_manba_ogohi"]:
            print("   ⚠ Bir nechta manba bir yo'nalishda — ajratish mumkin emas (isbot kuchi 2).")
    print(f"\n  Isbot kuchi: {rep['isbot_kuchi']} · isbotlanmaydi: {rep['nima_isbotlanmaydi']}")
    return 0


def cmd_sektor(a) -> int:
    from src.kirishsiz import sector  # noqa: E402

    aq = _rows(a.fayl) if a.fayl else _rows("data/public/aq_180kun.csv")
    wd = _rows(a.shamol_fayl) if a.shamol_fayl else _rows("data/public/wind_era5_180kun.csv")
    times = [r["vaqt"] for r in aq]
    wind_map = {r["vaqt"]: screener.to_float(r["shamol_yonalishi_grad"]) for r in wd}
    winds = [wind_map.get(t) for t in times]          # vaqt bo'yicha tekislangan shamol

    # --- sektorlar ro'yxati: haqiqiy reyestr yoki qo'lda berilgan nuqtalar
    sektorlar = []
    if a.haqiqiy:
        from src.kirishsiz import facilities as F  # noqa: E402
        for c in F.from_receptor(a.lat, a.lon):
            if a.radius is not None and c["masofa_km"] > a.radius:
                continue
            sektorlar.append({"nom": c["nom"], "markaz": c["azimut"], "masofa_km": c["masofa_km"],
                              "tur": c["tur"]})
    for spec in a.obyekt or []:
        try:
            nom, la, lo = spec.split(":")
            from src.kirishsiz.plume import bearing_deg, haversine_m  # noqa: E402
            sektorlar.append({"nom": nom, "markaz": round(bearing_deg(a.lat, a.lon, float(la), float(lo)), 1),
                              "masofa_km": round(haversine_m(a.lat, a.lon, float(la), float(lo)) / 1000.0, 2),
                              "tur": "qo'lda"})
        except ValueError:
            print(f"⚠️  --obyekt formati nom:lat:lon bo'lishi kerak: {spec}")

    moddalar = [m.strip() for m in (a.modda or "pm2_5").split(",") if m.strip()]
    USTUN = {"pm2_5": "pm2_5_ug_m3", "pm10": "pm10_ug_m3", "no2": "no2_ug_m3",
             "so2": "so2_ug_m3", "co": "co_ug_m3"}
    seriyalar = {}
    for m in moddalar:
        u = USTUN.get(m)
        if u is None or u not in (aq[0] if aq else {}):
            print(f"⚠️  {m} ustuni faylda yo'q — o'tkazib yuborildi")
            continue
        seriyalar[m] = [r[u] for r in aq]

    gul = sector.wind_rose(winds)
    natijalar = []
    for sk in sektorlar:
        qator = {"sektor": sk, "moddalar": {}}
        for m, seriya in seriyalar.items():
            qator["moddalar"][m] = sector.directional_enrichment(seriya, winds, sk["markaz"],
                                                                 a.kenglik, a.kvantil)
        natijalar.append(qator)

    if a.json:
        _print_json({"shamollanish_guli": gul, "natijalar": natijalar})
        return 0

    print(f"SEKTOR TAHLILI — {a.fayl or 'data/public/aq_180kun.csv'} · shamol: {a.shamol_fayl or 'ERA5'}")
    print(f"  Soatlar: {len(times)} · shamol qamrovi: {sum(1 for w in winds if w is not None)} · "
          f"kvantil: yuqori {100 * (1 - a.kvantil):.0f}% · kenglik ±{a.kenglik:g}°")
    print("  Shamollanish guli (top-3): " +
          " · ".join(f"{x['sektor']} {x['ulush']:.0%}" for x in gul["eng_kop"]) + f" (n={gul['jami']})")
    print()
    sarlavha = f"  {'sektor (obyekt)':<44}{'masofa':>8}" + "".join(f"{m:>9}" for m in seriyalar)
    print(sarlavha)
    print("  " + "-" * (len(sarlavha) - 2))
    for q in natijalar:
        sk = q["sektor"]
        qator = f"  {sk['nom'][:42]:<44}{sk['masofa_km']:>7.1f} "
        for m in seriyalar:
            r = q["moddalar"][m]
            lift = r.get("lift")
            belgi = ""
            if lift is not None:
                belgi = "*" if lift >= 1.5 else ("~" if lift >= 1.15 else " ")
            qator += f"{('%.2f%s' % (lift, belgi)) if lift is not None else '—':>9}"
        print(qator)
    print("\n  Izoh: * lift ≥ 1,5 (signal) · ~ 1,15–1,5 (kuchsiz) · bo'sh — signal yo'q (lift < 1,15)")
    if a.haqiqiy:
        from src.kirishsiz import facilities as F  # noqa: E402
        print("  Ajratilmaydigan yo'nalishlar (shamol bilan ajratib bo'lmaydi):")
        for g in F.sektor_guruhlari(a.lat, a.lon, kenglik=15):
            if g["ajratilmaydi"]:
                print(f"   • {g['markaz']:>5.1f}° — " + " + ".join(x[:34] for x in g["azolar"]))
    print(f"\n  Isbot kuchi: 2 · {sector.ko_p_modda({}, 0)['eslatma']}")
    return 0


def cmd_nomzodlar(a) -> int:
    from src.kirishsiz import facilities as F  # noqa: E402

    rows = F.from_receptor(a.lat, a.lon)
    if a.radius is not None:
        rows = [r for r in rows if r["masofa_km"] <= a.radius]
    if a.json:
        _print_json({"receptor": {"lat": a.lat, "lon": a.lon}, "radius_km": a.radius, "obyektlar": rows})
        return 0

    print(f"NOMZODLAR REYESTRI — receptor {a.lat:.3f}/{a.lon:.3f} · radius {a.radius:g} km · "
          f"manba: data/public/nomzodlar_uz.json")
    print(f"  {'obyekt':<46}{'turi':<14}{'azimut':>8}{'masofa':>9}  holat")
    print("  " + "-" * 88)
    for r in rows:
        holat = "radiusda ✅" if r["radiusda"] else "radiusdan tashqarida ⤴"
        print(f"  {r['nom'][:44]:<46}{r['tur']:<14}{r['azimut']:>7.1f}°{r['masofa_km']:>8.2f} km  {holat}")
    print("\n  Har yozuvda koordinata manbasi (URL) va sana bor — `--json` bilan ko'rinadi.")
    print("  Eslatma: reyestrda bo'lish «ifloslantiruvchi» degani emas; yo'qligi ham «toza» degani emas.")
    return 0


def cmd_band(a) -> int:
    if a.elv_low is not None:
        res = bands.band_from_elv(a.faoliyat, a.elv_low, a.elv_high or a.elv_low,
                                  a.elv_report, a.control_low, a.control_high, a.per)
    else:
        band = bands.expected_band(a.faoliyat, a.ef_low, a.ef_high, a.control_low, a.control_high)
        res = {"faoliyat": a.faoliyat, "ef_kg_per_birlik": [a.ef_low, a.ef_high], "oraliq": band}
        if a.hisobot is not None:
            res["tekshiruv"] = bands.check_reported(a.hisobot, band)
    if a.json:
        _print_json(res)
        return 0
    b = res["oraliq"]
    print(f"KUTILGAN ORALIQ: {b['past']:,.3f} … {b['yuqori']:,.3f}  "
          f"(geometrik o'rta {b['orta_geometrik']:,.3f} · kenglik {b['kenglik_foiz']}%)")
    print(f"  formula: {b['formula']} · EF {res['ef_kg_per_birlik']}")
    if "tekshiruv" in res:
        t = res["tekshiruv"]
        print(f"  hisobot {t['hisobot']:,.3f} → nisbat {t['nisbat']} → **{t['daraja'].upper()}** ({t['xulosa']})")
        print(f"  {t['izoh']}\n  {t['eslatma']}")
    if b.get("ogohlantirish"):
        print("  ⚠ " + b["ogohlantirish"])
    return 0


def cmd_benford(a) -> int:
    if a.fayl:
        vals = []
        with open(a.fayl, encoding="utf-8") as f:
            for line in f:
                line = line.strip().split(",")[0].split(";")[0]
                try:
                    vals.append(float(line))
                except ValueError:
                    pass
    else:
        vals = _nums(a.qiymatlar)
    r = benford.analyse(vals, a.rejim)
    r["dumaloq_raqam"] = benford.round_number_share(vals)
    if a.json:
        _print_json(r)
        return 0
    print(f"BENFORD ({r['mode']}-raqam) · n={r['n']} · MAD={r['madv']} → {r['madv_bahosi']} · "
          f"χ²={r['chi2']} (p={r['p_qiymat']}) · 5% da muhim: {r['muhim_5foiz']}")
    dr = r["dumaloq_raqam"]
    print(f"  dumaloq raqam ulushi: {dr['ulush']:.0%} (kutilgan 20%) · signal: {dr['signal']}")
    for o in r["ogohlantirish"]:
        print(f"  ⚠ {o}")
    print(f"  {r['izoh']}")
    return 0


def cmd_orbita(a) -> int:
    if a.kesim:
        res = plume.csf_flux(_nums(a.kesim), a.shamol, a.dx)
    else:
        res = plume.ime_flux(a.ime, a.shamol, a.uzunlik, a.u_eff)
        res["yillik"] = plume.annualise(res["q_kg_s"], persistensiya=a.persistensiya)
    if a.sinov:
        res["sezish_chegarasi"] = plume.detection_limit_kg_s(a.shamol, a.pixel, a.shovqin)
    if a.json:
        _print_json(res)
        return 0
    print(f"ORBITA BAHOSI: Q = {res['q_kg_s']:.4f} kg/s  ({res['formula']})")
    if "yillik" in res:
        print(f"  yillik (persistensiya {res['yillik']['persistensiya']}): {res['yillik']['t_yil']:,.1f} t/yil")
    if "sezish_chegarasi" in res:
        s = res["sezish_chegarasi"]
        print(f"  sezish chegarasi (3σ, {a.pixel:.0f} m, {a.shovqin:g} kg/m²): "
              f"{s['q_min_kg_s']*1000:.2f} g/s = {s['q_min_t_kun']:.1f} t/kun")
    print(f"  manba: {res.get('manba', 'Varon et al. 2018 (IME/CSF)')}")
    return 0


def cmd_transsect(a) -> int:
    from src.kirishsiz import transect
    q_s = transect.invert_q(a.c, a.shamol, a.sigma_z, a.h)
    rel = transect.relative_error(a.rel_c, a.rel_u, a.rel_sz)
    res = {"q_kg_s": q_s, "q_h_kg": q_s * 3600, "q_t_kun": q_s * 86400 / 1000,
           "nisbiy_xato": round(rel, 3), "oraliq_95": [round(q_s * (1 - 1.96 * rel), 6),
                                                       round(q_s * (1 + 1.96 * rel), 6)]}
    if a.reja_target:
        res["reja"] = transect.plan_campaign(a.reja_target, rel)
    if a.json:
        _print_json(res)
        return 0
    print(f"TRANSSEKT INVERSIYASI: Q = {res['q_kg_s']:.6f} kg/s = {res['q_h_kg']:.2f} kg/soat "
          f"= {res['q_t_kun']:.2f} t/kun")
    print(f"  nisbiy xato ±{res['nisbiy_xato']:.0%} → 95% oraliq {res['oraliq_95']}")
    if "reja" in res:
        print(f"  reja: {res['reja']['otishlar_kerak']} o'tish kerak "
              f"(maqsad ±{res['reja']['maqsad']:.0%}, bitta o'tish ±{res['reja']['bitta_otish_xatosi']:.0%})")
    print("  eslatma: sistematik xato (σ_z modeli, fon) o'rtachalashda kamaymaydi.")
    return 0


def cmd_sorov(a) -> int:
    if a.kutish:
        _print_json(requests_gen.tracker_pending(a.tracker))
        return 0
    r = requests_gen.build_request(a.tashkilot, a.tur, a.obyekt, a.sorovchi, a.aloqa, a.sana)
    path = a.out or os.path.join(ROOT, "data", "kirishsiz", f"sorov_{a.tur}.txt")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(r["matn"] + "\n")
    requests_gen.tracker_add(a.tracker, r)
    print(r["matn"])
    print(f"\n✅ Saqlandi: {path}\n✅ Kuzatuvga qo'shildi: {a.tracker}")
    print(f"   javob muddati: {r['muddat']['javob_sana']} · eskalatsiya: {r['muddat']['eskalatsiya_sana']}")
    return 0


# ------------------------------------------------------------------ main


def main() -> int:
    ap = argparse.ArgumentParser(description="Kirishsiz (ruxsatsiz) tekshiruv yo'llari")
    ap.add_argument("--json", action="store_true", help="JSON chiqarish (subkomandadan oldin yoki keyin)")
    # umumiy flag: subkomanda ichida ham --json qabul qilinsin
    umumiy = argparse.ArgumentParser(add_help=False)
    umumiy.add_argument("--json", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--list", action="store_true", help="yo'llar reyestri (yollar bilan bir xil)")
    sub = ap.add_subparsers(dest="cmd")

    p = sub.add_parser("yollar", parents=[umumiy], help="yo'llar reyestri")
    p.set_defaults(fn=cmd_list)

    p = sub.add_parser("ekran", parents=[umumiy], help="ochiq havo sifati ekrani (kalitsiz)")
    p.add_argument("--lat", type=float, default=41.311)
    p.add_argument("--lon", type=float, default=69.240)
    p.add_argument("--kun", type=int, default=7)
    p.add_argument("--norma", type=float, default=None)
    p.add_argument("--soatlik-norma", dest="soatlik_norma", type=float, default=35.0)
    p.add_argument("--obyekt", action="append", help="nomzod: nom:lat:lon (bir necha marta)")
    p.add_argument("--out-csv", dest="out_csv", default=None)
    p.add_argument("--out-wind", dest="out_wind", default=None)
    p.add_argument("--shamol-fayl", dest="shamol_fayl", default=None,
                   help="shamol CSV (masalan ERA5 arxividan) — berilsa, API'dan olib kelinmaydi")
    p.set_defaults(fn=cmd_ekran)

    p = sub.add_parser("band", parents=[umumiy], help="pastdan yuqoriga oraliq hisobi")
    p.add_argument("--faoliyat", type=float, required=True)
    p.add_argument("--ef-low", dest="ef_low", type=float, default=None)
    p.add_argument("--ef-high", dest="ef_high", type=float, default=None)
    p.add_argument("--elv-low", dest="elv_low", type=float, default=None)
    p.add_argument("--elv-high", dest="elv_high", type=float, default=None)
    p.add_argument("--elv-report", dest="elv_report", type=float, default=None)
    p.add_argument("--per", default="t_sement", choices=["t_sement", "t_klinker"])
    p.add_argument("--control-low", dest="control_low", type=float, default=0.0)
    p.add_argument("--control-high", dest="control_high", type=float, default=0.0)
    p.add_argument("--hisobot", type=float, default=None)
    p.set_defaults(fn=cmd_band)

    p = sub.add_parser("benford", parents=[umumiy], help="Benford/dumaloq raqam skriningi")
    p.add_argument("--fayl")
    p.add_argument("--qiymatlar", default="")
    p.add_argument("--rejim", default="1", choices=["1", "2", "12"])
    p.set_defaults(fn=cmd_benford)

    p = sub.add_parser("orbita", parents=[umumiy], help="sun'iy yo'ldosh oqim bahosi")
    p.add_argument("--kesim", help="qatlam og'ishlari kg/m² (vergul bilan) — CSF")
    p.add_argument("--dx", type=float, default=3500.0)
    p.add_argument("--ime", type=float, default=None)
    p.add_argument("--uzunlik", type=float, default=None)
    p.add_argument("--u-eff", dest="u_eff", type=float, default=1.0)
    p.add_argument("--persistensiya", type=float, default=1.0)
    p.add_argument("--shamol", type=float, default=3.0)
    p.add_argument("--sinov", action="store_true", help="sezish chegarasini ham chiqarish")
    p.add_argument("--pixel", type=float, default=3500.0)
    p.add_argument("--shovqin", type=float, default=1e-5)
    p.set_defaults(fn=cmd_orbita)

    p = sub.add_parser("transsect", parents=[umumiy], help="yo'l transsekti inversiyasi")
    p.add_argument("--c", type=float, required=True, help="fon ayirilgan konsentratsiya, kg/m³")
    p.add_argument("--shamol", type=float, default=3.0)
    p.add_argument("--sigma-z", dest="sigma_z", type=float, default=20.0)
    p.add_argument("--h", type=float, default=0.0)
    p.add_argument("--rel-c", dest="rel_c", type=float, default=0.15)
    p.add_argument("--rel-u", dest="rel_u", type=float, default=0.15)
    p.add_argument("--rel-sz", dest="rel_sz", type=float, default=0.35)
    p.add_argument("--reja-target", dest="reja_target", type=float, default=None)
    p.set_defaults(fn=cmd_transsect)

    p = sub.add_parser("sorov", parents=[umumiy], help="huquqiy talab (Aarhus) generatori")
    p.add_argument("--tashkilot", required=True)
    p.add_argument("--tur", default="olchov", choices=list(requests_gen.STANDART_SOROVLAR))
    p.add_argument("--obyekt", default="⟦obyekt nomi⟧")
    p.add_argument("--sorovchi", default="⟦F.I.Sh. / tadqiqot guruhi⟧")
    p.add_argument("--aloqa", default="⟦telefon / e-pochta⟧")
    p.add_argument("--sana", default=None)
    p.add_argument("--out", default=None)
    p.add_argument("--tracker", default=os.path.join(ROOT, "data", "kirishsiz", "sorovlar.jsonl"))
    p.add_argument("--kutish", action="store_true", help="javobsiz so'rovlar holati")
    p.set_defaults(fn=cmd_sorov)

    p = sub.add_parser("sektor", parents=[umumiy],
                       help="sektor tahlili: yuqori soatlarda shamol yo'nalishi boyitilishi (lift)")
    p.add_argument("--fayl", default=None, help="havo sifati CSV (standart: data/public/aq_92kun.csv)")
    p.add_argument("--shamol-fayl", dest="shamol_fayl", default=None,
                   help="shamol CSV (standart: data/public/wind_era5_92kun.csv)")
    p.add_argument("--markaz", type=float, default=None, help="sektor markazi, gradus (yo'q bo'lsa — nomzoddan)")
    p.add_argument("--kenglik", type=float, default=45.0)
    p.add_argument("--kvantil", type=float, default=0.90, help="yuqori soatlar chegarasi (0,90 = yuqori 10%%)")
    p.add_argument("--modda", default="pm2_5", help="moddalar vergul bilan: pm2_5,pm10,no2,so2,co")
    p.add_argument("--lat", type=float, default=41.311)
    p.add_argument("--lon", type=float, default=69.240)
    p.add_argument("--obyekt", action="append", help="nomzod: nom:lat:lon (sektor shundan hisoblanadi)")
    p.add_argument("--haqiqiy", action="store_true",
                   help="haqiqiy obyektlar reyestridan foydalanish (data/public/nomzodlar_uz.json)")
    p.add_argument("--radius", type=float, default=None, help="faqat shu radiusdagi obyektlar (km)")
    p.set_defaults(fn=cmd_sektor)

    p = sub.add_parser("nomzodlar", parents=[umumiy],
                       help="haqiqiy sanoat obyektlari reyestri (koordinata + manba + holat)")
    p.add_argument("--lat", type=float, default=41.311)
    p.add_argument("--lon", type=float, default=69.240)
    p.add_argument("--radius", type=float, default=30.0)
    p.set_defaults(fn=cmd_nomzodlar)

    a = ap.parse_args()
    if getattr(a, "list", False) and not a.cmd:      # --list (yollar bilan bir xil)
        a.cmd = "yollar"
        return cmd_list(a)
    if not a.cmd:
        ap.print_help()
        return 1
    return a.fn(a)


if __name__ == "__main__":
    raise SystemExit(main())
