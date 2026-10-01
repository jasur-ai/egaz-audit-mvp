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


def cmd_pastdan(a) -> int:
    """Yo'l #2 — pastdan yuqoriga: ishlab chiqarish → EF → oqim → dispersiya → kuzatuv bilan solishtirish."""
    from src.kirishsiz import bottomup as BU  # noqa: E402
    from src.kirishsiz import screener  # noqa: E402

    # --- 1) EF zanjiri
    ef_past, ef_yuqori = a.ef_past, a.ef_yuqori
    izoh = []
    if a.emep:
        ef_past = BU.emep_ef_g_per_kwh(max(_nums(a.fik) or [0.5]), "nox")
        ef_yuqori = BU.emep_ef_g_per_kwh(min(_nums(a.fik) or [0.35]), "nox")
        izoh.append({"emep": BU.EMEP_EEA_2023["manba"],
                     "g_per_gj": BU.EMEP_EEA_2023["ef"]["nox_g_per_gj"],
                     "ci": BU.EMEP_EEA_2023["ef"]["nox_ci"],
                     "g_per_kwh": [round(ef_past, 3), round(ef_yuqori, 3)]})
    if a.lb_past is not None or a.lb_yuqori is not None:
        fiklar = _nums(a.fik) or [0.35, 0.5]
        lp = a.lb_past if a.lb_past is not None else a.lb_yuqori
        ly = a.lb_yuqori if a.lb_yuqori is not None else a.lb_past
        ggj_p = BU.lb_per_mmbtu_to_g_per_gj(lp)
        ggj_y = BU.lb_per_mmbtu_to_g_per_gj(ly)
        ef_past = BU.g_per_gj_to_g_per_kwh(ggj_p, max(fiklar))
        ef_yuqori = BU.g_per_gj_to_g_per_kwh(ggj_y, min(fiklar))
        izoh.append({"lb_mmbtu": [lp, ly], "g_gj": [round(ggj_p, 1), round(ggj_y, 1)],
                     "fik": [min(fiklar), max(fiklar)]})
    if ef_past is None or ef_yuqori is None:
        print("⚠️  EF kerak: --ef-past/--ef-yuqori (g/kWh) yoki --lb-past/--lb-yuqori (+ --fik)")
        return 2

    # --- 2) masofa
    masofa = a.masofa
    nom = a.obyekt or "obyekt"
    if masofa is None and a.obyekt:
        try:
            nm, la, lo = a.obyekt.split(":")
            from src.kirishsiz.plume import haversine_m, bearing_deg  # noqa: E402
            nom = nm
            masofa = haversine_m(a.lat, a.lon, float(la), float(lo)) / 1000.0
            a._azimut = round(bearing_deg(a.lat, a.lon, float(la), float(lo)), 1)
        except ValueError:
            print(f"⚠️  --obyekt formati nom:lat:lon bo'lishi kerak: {a.obyekt}")
            return 2
    if masofa is None:
        print("⚠️  masofa kerak: --masofa km yoki --obyekt nom:lat:lon")
        return 2
    azimut = getattr(a, "_azimut", a.azimut)

    # --- 3) hisob
    res = BU.bottom_up(a.ishlab_chiqarish, ef_past, ef_yuqori, masofa, a.shamol,
                       a.barqarorlik, a.mo_ri, not a.qishloq)

    # --- 4) sektor bo'yicha mos kelish ulushi va o'rtacha model qiymati
    mos = None
    ilova = {}
    if azimut is not None and a.shamol_fayl:
        wd = _rows(a.shamol_fayl)
        winds = [r["shamol_yonalishi_grad"] for r in wd]
        mos = BU.alignment_share(winds, azimut, a.kenglik, a.tol)
        if "xato" not in mos:
            ilova["ssenariylar"] = BU.sector_weighted_scenarios(
                res["oqim_kg_s"]["yuqori"], masofa, mos["ulush_sektorda"],
                (a.shamol, a.shamol * 0.5), (a.barqarorlik,), a.mo_ri, not a.qishloq)
            ilova["past_oqim"] = BU.sector_weighted_scenarios(
                res["oqim_kg_s"]["past"], masofa, mos["ulush_sektorda"],
                (a.shamol, a.shamol * 0.5), (a.barqarorlik,), a.mo_ri, not a.qishloq)
    if a.kuzatuv is not None and ilova.get("ssenariylar"):
        sm = ilova["ssenariylar"][0]["sektor_ortacha_ug_m3"]
        ilova["solishtirish"] = BU.consistency(sm, a.kuzatuv)

    if a.json:
        _print_json({"obyekt": nom, "ef_zanjiri": izoh, "natija": res, "mos_ulush": mos, **ilova})
        return 0

    # --- 5) chop etish
    print(f"PASTDAN YUQORIGA — {nom} · {masofa:.2f} km" + (f" · azimut {azimut:.1f}°" if azimut is not None else ""))
    if izoh and "emep" in izoh[0]:
        z = izoh[0]
        print(f"  EF zanjiri (EMEP/EEA 2023 1.A.1.a): {z['g_per_gj']:g} g/GJ "
              f"(CI95 {z['ci'][0]:g}–{z['ci'][1]:g}) → FIK bo'yicha {z['g_per_kwh'][0]}–{z['g_per_kwh'][1]} g NOx/kWh "
              f"· {z['emep'][:60]}…")
    elif izoh:
        z = izoh[0]
        print(f"  EF zanjiri: {z['lb_mmbtu'][0]}–{z['lb_mmbtu'][1]} lb/MMBtu = "
              f"{z['g_gj'][0]}–{z['g_gj'][1]} g/GJ → FIK {z['fik'][0]:.0%}–{z['fik'][1]:.0%} → "
              f"{ef_past:.2f}–{ef_yuqori:.2f} g/kWh  (AP-42 §3.1-1)")
    else:
        print(f"  EF (berilgan): {ef_past:.2f}–{ef_yuqori:.2f} g/kWh")
    y = res["yillik_tonna"]
    q = res["oqim_kg_s"]
    print(f"  Ishlab chiqarish {a.ishlab_chiqarish:g} TWh/yil → NOx {y['past']:,.0f}–{y['yuqori']:,.0f} t/yil "
          f"→ oqim {q['past']:,.3f}–{q['yuqori']:,.3f} kg/s")
    print(f"  Disperisiya: {a.barqarorlik} · u={a.shamol:g} m/s · mo'ri {a.mo_ri:g} m · "
          f"{'shahar' if not a.qishloq else 'qishloq'} · σy {res['sigma']['sigma_y']:,.0f} m · "
          f"σz {res['sigma']['sigma_z']:,.0f} m")
    print(f"  To'g'ridan-to'g'ri o'qda (doim mos): {res['kutilgan_ug_m3']['past']:,.1f}–"
          f"{res['kutilgan_ug_m3']['yuqori']:,.1f} µg/m³ NOx")
    if mos and "xato" not in mos:
        print(f"  Mos kelish ulushi: sektorda {mos['mos_soat']}/{mos['sektor_soat']} soat "
              f"= {mos['ulush_sektorda']:.1%} (barcha soatlarning {mos['ulush_jami']:.1%} i)")
        for r in ilova["ssenariylar"]:
            print(f"   • {r['barqarorlik']} · u={r['shamol_ms']:g} m/s → o'qda {r['aligned_ug_m3']:,.1f} × "
                  f"{r['mos_ulush']:.0%} = **sektor o'rtachasi {r['sektor_ortacha_ug_m3']:,.1f} µg/m³**")
    if "solishtirish" in ilova:
        c = ilova["solishtirish"]
        print(f"  Kuzatuv bilan: model {c['model_ug_m3']:,.1f} vs yo'nalish ortiqchasi "
              f"{c['kuzatuv_ug_m3']:,.1f} µg/m³ → nisbat {c['nisbat']} → {c['xulosa']}")
    print(f"\n  Nima isbotlanmaydi: {res['nima_isbotlanmaydi']}")
    print("  Isbot kuchi: 3 · EF adabiyot qiymati, dispersiya soddalashtirilgan (bitta shamol, "
          "bir necha soat emas, o'rtacha yil)")
    return 0


def cmd_profil(a) -> int:
    """Yo'nalish profili — 15° lik burchaklar bo'yicha o'rtacha (sektorni qo'lda tanlash o'rniga)."""
    from src.kirishsiz import sector as S  # noqa: E402

    aq = _rows(a.fayl) if a.fayl else _rows("data/public/aq_180kun.csv")
    wd = _rows(a.shamol_fayl) if a.shamol_fayl else _rows("data/public/wind_era5_180kun.csv")
    wmap = {r["vaqt"]: r["shamol_yonalishi_grad"] for r in wd}
    winds = [wmap.get(r["vaqt"]) for r in aq]
    ustunlar = [m.strip() for m in (a.modda or "no2_ug_m3,pm2_5_ug_m3").split(",") if m.strip()]
    natijalar = {}
    for u in ustunlar:
        if u not in (aq[0] if aq else {}):
            print(f"⚠️  {u} ustuni faylda yo'q")
            continue
        natijalar[u] = S.yonalish_profili([r[u] for r in aq], winds, a.qadam, a.kamida)

    if a.json:
        _print_json({"fayl": a.fayl or "data/public/aq_180kun.csv", "profillar": natijalar})
        return 0

    print(f"YO'NALISH PROFILI — {a.fayl or 'data/public/aq_180kun.csv'} · qadam {a.qadam:g}° · "
          f"kamida {a.kamida} soat")
    for u, pr in natijalar.items():
        ch = pr["cho_qqi"]
        pa = pr["past"]
        print(f"\n══ {u} ══  cho'qqi {ch['burchak']}° = {ch['ort']} (n={ch['n']}) · "
              f"eng past {pa['burchak']}° = {pa['ort']} · nisbat {ch['ort']/pa['ort']:.2f}×")
        print(S.profil_grafik(pr))
        if a.obyektlar:
            from src.kirishsiz import facilities as F  # noqa: E402
            from src.kirishsiz.plume import angle_diff  # noqa: E402
            mos = [o for o in F.from_receptor(a.lat, a.lon)
                   if angle_diff(o["azimut"], ch["burchak"]) <= a.qadam]
            if mos:
                print(f"  shu burchakda ({ch['burchak']}°±{a.qadam:g}°): " +
                      " · ".join(f"{o['nom'][:36]} ({o['masofa_km']:.1f} km)" for o in mos))
            else:
                print(f"  shu burchakda reyestrda obyekt yo'q — profil **yangi nomzod** ko'rsatyapti")
    print("\n  Izoh: cho'qqi burchagi — nomzod, tasdiqlangan manba emas; model katagi (CAMS) "
          "o'lchamidan kichik masofalar ajratilmaydi.")
    return 0


def cmd_retseptorlar(a) -> int:
    """Retseptorlar reyestri: shahar nuqtalari bo'yicha alohida ekranlar."""
    from src.kirishsiz import retseptorlar as R  # noqa: E402

    nomlar = R.nomlar()
    hisobot = {"retseptorlar": []}
    for nom in nomlar:
        r = R.top(nom)
        yaqin = R.yaqin_obyektlar(nom, a.radius)
        aq_yol = R.data_fayllar(nom, "aq")
        sh_yol = R.data_fayllar(nom, "shamol")
        qator = {"nom": nom, "lat": r["lat"], "lon": r["lon"], "manba": r["manba"],
                 "sana": r["sana"], "daraja": r["daraja"], "yaqin_obyektlar": yaqin,
                 "aq_fayl": aq_yol, "shamol_fayl": sh_yol}
        if aq_yol:
            from src.kirishsiz.retseptorlar import ROOT  # noqa: E402
            yol = aq_yol if os.path.isabs(aq_yol) else os.path.join(ROOT, aq_yol)
            if os.path.exists(yol):
                rows = _rows(yol)
                qator["dozalar"] = R.qiymat_xulosasi({
                    "pm2_5": [x.get("pm2_5_ug_m3") for x in rows],
                    "pm10": [x.get("pm10_ug_m3") for x in rows],
                    "no2": [x.get("no2_ug_m3") for x in rows],
                    "so2": [x.get("so2_ug_m3") for x in rows]})
        hisobot["retseptorlar"].append(qator)
    hisobot["era5_katak"] = R.era5_katak_tekshiruvi({n: R.data_fayllar(n, "shamol") for n in nomlar})

    if a.json:
        _print_json(hisobot)
        return 0

    print(f"RETSEPTORLAR REYESTRI — {len(nomlar)} nuqta · radius {a.radius:g} km · "
          f"manba: data/public/retseptorlar_uz.json")
    for q in hisobot["retseptorlar"]:
        print(f"\n── {q['nom']} ({q['lat']:.4f}/{q['lon']:.4f}) · daraja {q['daraja']} · {q['sana']}")
        print(f"   manba: {q['manba'][:88]}")
        d = q.get("dozalar")
        if d:
            print(f"   AQ (180 kun): PM2,5 {d['pm2_5']['ort']:>5.2f} (P90 {d['pm2_5']['p90']:>5.2f}) · "
                  f"PM10 {d['pm10']['ort']:>5.2f} · NO2 {d['no2']['ort']:>5.2f} · SO2 {d['so2']['ort']:>4.2f}")
        if q["yaqin_obyektlar"]:
            print(f"   yaqin obyektlar ({len(q['yaqin_obyektlar'])}):")
            for o in q["yaqin_obyektlar"][:5]:
                print(f"     • {o['nom'][:42]:<44}{o['azimut']:>6.1f}° {o['masofa_km']:>6.2f} km · {o['tur']}")
        else:
            print("   yaqin obyektlar: yo'q — **yangi nomzod kerak** (reyestr bo'shlig'i)")
    ek = hisobot["era5_katak"]
    if ek.get("ogohlantirish"):
        print(f"\n  ⚠️  ERA5: {ek['ogohlantirish']}")
        print(f"      bir xil katak: {ek['bir_xil_katak']}")
    print("\n  Izoh: har nuqta — alohida ekran; meteorologiya o'sha nuqtaning ERA5 qatori.")
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

    p = sub.add_parser("pastdan", parents=[umumiy],
                       help="pastdan yuqoriga: ishlab chiqarish × EF → oqim → dispersiya (yo'l #2)")
    p.add_argument("--obyekt", help="nom:lat:lon (masofa va azimut shundan)")
    p.add_argument("--ishlab-chiqarish", type=float, required=True, help="yillik ishlab chiqarish, TWh")
    p.add_argument("--ef-past", type=float, help="EF, g/kWh (quyi)")
    p.add_argument("--ef-yuqori", type=float, help="EF, g/kWh (yuqori)")
    p.add_argument("--lb-past", type=float, help="EF, lb/MMBtu (AP-42 quyi, masalan 0,13)")
    p.add_argument("--lb-yuqori", type=float, help="EF, lb/MMBtu (AP-42 yuqori, masalan 0,32)")
    p.add_argument("--fik", default="0.35,0.50", help="foydali FIK lar (vergul bilan), masalan 0.35,0.50")
    p.add_argument("--emep", action="store_true",
                   help="EF ni EMEP/EEA 2023 1.A.1.a Table 3-4 dan olish (89 g/GJ, CI 15–185)")
    p.add_argument("--masofa", type=float, help="masofa, km (berilmasa --obyekt dan)")
    p.add_argument("--shamol", type=float, default=4.0, help="shamol tezligi, m/s (o'rtacha)")
    p.add_argument("--barqarorlik", default="D", help="Briggs barqarorlik sinfi: A…F")
    p.add_argument("--mo-ri", type=float, default=100.0, help="samarali mo'ri balandligi, m")
    p.add_argument("--qishloq", action="store_true", help="qishloq rejimi (standart: shahar)")
    p.add_argument("--fayl", help="havo sifati fayli (solishtirish uchun, ixtiyoriy)")
    p.add_argument("--shamol-fayl", default="data/public/wind_era5_180kun.csv",
                   help="shamol fayli (mos kelish ulushi uchun)")
    p.add_argument("--kenglik", type=float, default=45.0, help="sektor yarim kengligi, daraja")
    p.add_argument("--tol", type=float, default=9.0, help="«mos» tolerantligi, daraja")
    p.add_argument("--lat", type=float, default=41.311, help="receptor kengligi")
    p.add_argument("--lon", type=float, default=69.240, help="receptor uzunligi")
    p.add_argument("--azimut", type=float, help="obyekt azimuti (--obyekt berilmasa)")
    p.add_argument("--kuzatuv", type=float, help="kuzatilgan yo'nalish ortiqchasi, µg/m³")
    p.set_defaults(fn=cmd_pastdan)

    p = sub.add_parser("profil", parents=[umumiy],
                       help="yo'nalish profili (15° burchaklar) — sektorni qo'lda tanlamaslik uchun")
    p.add_argument("--fayl", default="data/public/aq_180kun.csv", help="havo sifati fayli")
    p.add_argument("--shamol-fayl", default="data/public/wind_era5_180kun.csv", help="shamol fayli")
    p.add_argument("--modda", default="no2_ug_m3,pm2_5_ug_m3", help="ustunlar (vergul bilan)")
    p.add_argument("--qadam", type=float, default=15.0, help="burchak qadami (360 ning bo'luvchisi)")
    p.add_argument("--kamida", type=int, default=20, help="bin uchun minimal soat soni")
    p.add_argument("--lat", type=float, default=41.311, help="receptor kengligi")
    p.add_argument("--lon", type=float, default=69.240, help="receptor uzunligi")
    p.add_argument("--obyektlar", action="store_true",
                   help="cho'qqi burchakda reyestrdagi obyektlarni ko'rsatish")
    p.set_defaults(fn=cmd_profil)

    p = sub.add_parser("retseptorlar", parents=[umumiy],
                       help="retseptorlar reyestri — shahar nuqtalari bo'yicha alohida ekranlar")
    p.add_argument("--radius", type=float, default=30.0, help="yaqin obyektlar radiusi, km")
    p.set_defaults(fn=cmd_retseptorlar)

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
