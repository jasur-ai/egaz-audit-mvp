"""Maishiy isitish hissasi — yoqilg'i asosidagi (bottom-up) baholash.

Bu modul isitish mavsumidagi kuzatilgan PM2,5 ortishini **yoqilg'i miqdori** bilan
bog'lashga urinadi. Uch bosqich:

  1. Faoliyat (activity data): uy xo'jaliklari soni → isitish uchun yoqilg'i
     energiyasi (GJ).
  2. Emissiya: EMEP/EEA 2023, 1.A.4.b.i (Residential plants) Tier 1 emission
     faktorlari × energiya.
  3. Konsentratsiya: quti modeli  C = Q / (L · H · u)  — oddiy, shaffof skrining.

Teskari masala ham bor (`talab_emissiya`): kuzatilgan ortishni tushuntirish uchun
qancha emissiya kerak → qancha ko'mir/gaz. Bu «isbotlanmaydi» degan chegarani
miqdoriy qiladi.

Manbalar (har biri darajasi bilan):
  [EF-A] EMEP/EEA air pollutant emission inventory guidebook 2023, 1.A.4 Small
         combustion, Tier 1 jadvallari (3-3 qattiq/ko'mir, gaz jadvali).
         https://www.eea.europa.eu/publications/emep-eea-guidebook-2023
         (qayta olindi 2026-10-01; EEA yangi saytida `@@download/file` vaqtincha
         ishlamaydi — qiymatlar qidiruv indeksidagi sahifa matnidan olindi)
  [EF-B] AP-42 §1.4 Natural Gas Combustion (EPA) — gaz uchun mustaqil tekshiruv.
  [NCV]  1 m³ tabiiy gaz ≈ 36 MJ (LHV) — umumiy konversiya, [D] daraja.
  [NCV]  Qattiq/ko'mir: 15–25 GJ/t (lignit→toshko'mir), bazaviy 20 GJ/t.

Chegara: quti modeli meteorologiyani (stagnatsiya, inversiya) va ikkilamchi
aerozol kimyosini **ichiga olmaydi**; shuning uchun natija oraliq bilan beriladi
va traser testi bilan kesishadi.
"""

from __future__ import annotations

import math
from typing import Any, Iterable

# --- Manbalar (kodda ham ko'rinib tursin) -----------------------------------
EFA_MANBA = "EMEP/EEA 2023, 1.A.4 Small combustion (Tier 1 jadvallar)"
EFA_SANA = "2026-10-01 (qayta olindi)"
AP42_MANBA = "EPA AP-42 §1.4 Natural Gas Combustion"

# Tier 1 emission faktorlari, g/GJ. [EF-A]
#  - "komir": 1.A.4.b.i, qattiq + qo'ng'ir ko'mir (Table 3-3) — SOx 900 g/GJ
#    ~1,1 % oltingugurtli ko'mirga mos keladi (tekshirilgan konversiya).
#  - "gaz": 1.A.4.b.i, tabiiy gaz; PM uchun jadvalda «total PM» noaniqligi bor
#    (izohda yozilgan) — shuning uchun PM oralig'i keng qabul qilinadi.
EMEP_1A4B_EF: dict[str, dict[str, float]] = {
    "komir": {"nox": 110.0, "co": 4600.0, "sox": 900.0, "pm25": 398.0, "pm10": 404.0, "tsp": 444.0},
    "gaz": {"nox": 51.0, "co": 26.0, "sox": 0.3, "pm25": 1.2, "pm10": 1.2, "tsp": 1.2},
}

# Energiya zichligi (NCV) — [D] daraja, umumiy konversiya
GAZ_NCV_GJ_M3 = 0.036  # 36 MJ/m³
KOMIR_NCV_GJ_T = 20.0  # 20 GJ/t (oralig'i 15–25)
KOMIR_NCV_ORALIQ = (15.0, 25.0)

# Uy xo'jaligi konvensiyalari
KISHI_UY_BAZA = 3.8  # Toshkent shahri uchun qabul qilingan o'rtacha (oralig'i 3,5–4,5)
M3_ISITISH_BAZA = 2500.0  # isitiladigan xususiy uy: 2 000–4 000 m³/yil (isitish qismi ~1 700–3 200)


def uy_xo_jaliklari(aholi_ming: float, kishi_uy: float = KISHI_UY_BAZA) -> float:
    """Uy xo'jaliklari soni = aholi / uy xo'jaligidagi o'rtacha kishi soni."""
    if kishi_uy <= 0:
        raise ValueError("kishi_uy > 0 bo'lishi kerak")
    return aholi_ming * 1000.0 / kishi_uy


def energiya_gj(gaz_m3: float = 0.0, komir_t: float = 0.0) -> float:
    """Yoqilg'i miqdorini energiyaga (GJ) o'tkazish."""
    return gaz_m3 * GAZ_NCV_GJ_M3 + komir_t * KOMIR_NCV_GJ_T


def emissiya_g(energiya: float, yoqilgi: str, modda: str) -> float:
    """Emissiya (gramm) = energiya (GJ) × EF (g/GJ)."""
    if yoqilgi not in EMEP_1A4B_EF:
        raise KeyError(f"noma'lum yoqilg'i: {yoqilgi!r} (bor: {sorted(EMEP_1A4B_EF)})")
    ef = EMEP_1A4B_EF[yoqilgi]
    if modda not in ef:
        raise KeyError(f"noma'lum modda: {modda!r} ({yoqilgi} uchun bor: {sorted(ef)})")
    return energiya * ef[modda]


def garmonik_shamol(tezliklar: Iterable[float | None], min_ms: float = 0.5) -> float | None:
    """Quti modeli uchun **garmonik** o'rtacha shamol.

    C = Q/(L·H·u) da o'rtacha konsentratsiya <1/u> ga proporsional; shuning uchun
    arifmetik emas, garmonik o'rtacha to'g'ri (yumshoq kunlar ko'proq vazn oladi).
    `min_ms` dan past (sokin) soatlar chiqarib tashlanadi.
    """
    u = [float(x) for x in tezliklar if x is not None and float(x) >= min_ms]
    if not u:
        return None
    return len(u) / sum(1.0 / x for x in u)


def quti_konstentratsiyasi(Q_g_s: float, L_m: float, H_m: float, u_ms: float) -> float:
    """Quti modeli: C [µg/m³] = Q / (L · H · u), o'lchovlar SI da.

    Q [g/s], L va H [m], u [m/s] → g/m³ = Q/(L·H·u) → µg/m³ uchun ×1e6.
    """
    if min(L_m, H_m, u_ms) <= 0:
        raise ValueError("L, H, u > 0 bo'lishi kerak")
    return Q_g_s / (L_m * H_m * u_ms) * 1e6


def talab_emissiya(delta_ug_m3: float, L_m: float, H_m: float, u_ms: float) -> float:
    """Teskari masala: kuzatilgan ortishni beradigan emissiya oqimi, g/s."""
    if min(L_m, H_m, u_ms) <= 0:
        raise ValueError("L, H, u > 0 bo'lishi kerak")
    return delta_ug_m3 * 1e-6 * L_m * H_m * u_ms


def mavsum_massasi_tonna(Q_g_s: float, soat: float) -> float:
    """Emissiya oqimidan mavsumiy massa: t = g/s × soat × 3600 / 1e6."""
    if soat < 0:
        raise ValueError("soat >= 0 bo'lishi kerak")
    return Q_g_s * soat * 3600.0 / 1e6


def yoqilgi_kerak(massa_t: float, yoqilgi: str, modda: str = "pm25") -> dict[str, float]:
    """`massa_t` moddani beradigan yoqilg'i miqdori (teskari: massa → energiya → yoqilg'i)."""
    ef = EMEP_1A4B_EF[yoqilgi][modda]
    energiya = massa_t * 1e6 / ef  # g / (g/GJ) = GJ
    return {
        "energiya_gj": energiya,
        "komir_t": energiya / KOMIR_NCV_GJ_T,
        "gaz_mln_m3": energiya / GAZ_NCV_GJ_M3 / 1e6,
    }


def gaz_kerak_pm(massa_t: float, modda: str = "pm25") -> dict[str, float]:
    """Shu moddani **gaz bilan** chiqarish uchun kerak bo'ladigan gaz hajmi.

    Gaz PM2,5 1,2 g/GJ bo'lgani uchun hajm juda katta chiqadi — bu «gaz bilan
    tushuntirib bo'lmaydi» degan xulosaning miqdoriy ko'rinishi.
    """
    energiya = massa_t * 1e6 / EMEP_1A4B_EF["gaz"][modda]
    m3 = energiya / GAZ_NCV_GJ_M3
    return {"energiya_gj": energiya, "gaz_m3": m3, "gaz_mlrd_m3": m3 / 1e9}


def traser_tekshiruvi(delta_pm: float, delta_co: float, delta_sox: float,
                      yoqilgi: str = "komir") -> dict[str, Any]:
    """Marjinal nisbat testi: qishki ortishning PM/CO va SO2/CO nisbatini
    yoqilg'i EF nisbatlari bilan solishtiradi.

    Kuzatuvda delta_pm/delta_co **kichik** bo'lsa — qo'shilgan yonish «gazsimon»
    (PM kam), katta bo'lsa — «ko'mirsimon». SO2/CO nisbati ko'mir uchun
    ~0,196, gaz uchun ~0,012 (EF dan).
    """
    if delta_co <= 0:
        raise ValueError("delta_co > 0 bo'lishi kerak")
    ef = EMEP_1A4B_EF[yoqilgi]
    kuz = {"pm_co": delta_pm / delta_co, "sox_co": delta_sox / delta_co}
    ef_n = {"pm_co": ef["pm25"] / ef["co"], "sox_co": ef["sox"] / ef["co"]}
    return {
        "kuzatuv": kuz,
        "ef_nisbat": ef_n,
        "komir_nisbati": {"pm_co": kuz["pm_co"] / ef_n["pm_co"],
                          "sox_co": kuz["sox_co"] / ef_n["sox_co"]},
        "gaz_nisbati": {"pm_co": kuz["pm_co"] / (EMEP_1A4B_EF["gaz"]["pm25"] / EMEP_1A4B_EF["gaz"]["co"]),
                        "sox_co": kuz["sox_co"] / (EMEP_1A4B_EF["gaz"]["sox"] / EMEP_1A4B_EF["gaz"]["co"])},
    }


def stsenariy(uy_soni: float, xususiy_ulush: float, gaz_ulush: float,
              m3_uy: float = M3_ISITISH_BAZA, soat: float = 2319.0,
              L_m: float = 20000.0, H_m: float = 300.0, u_ms: float = 3.16,
              modda: str = "pm25") -> dict[str, Any]:
    """Bitta ssenariy: xususiy uylarning bir qismi gaz, qolgani ko'mir bilan isitiladi.

    `gaz_ulush` — isitiladigan xususiy uylar ichida gaz ishlatadiganlar ulushi.
    Qolgani (1-gaz_ulush) ko'mir yoqadi (qattiq yoqilg'i model vakili).
    """
    isitiladigan = uy_soni * xususiy_ulush
    gaz_uy = isitiladigan * gaz_ulush
    komir_uy = isitiladigan * (1.0 - gaz_ulush)

    e_gaz = energiya_gj(gaz_m3=gaz_uy * m3_uy)
    # ko'mir uyiga energiya jihatidan ekvivalent miqdor (m³ → GJ → t)
    e_komir = energiya_gj(gaz_m3=komir_uy * m3_uy)
    komir_t = e_komir / KOMIR_NCV_GJ_T

    em = {y: emissiya_g(e_gaz if y == "gaz" else e_komir, y, modda) for y in ("gaz", "komir")}
    jami_t = sum(em.values()) / 1e6
    Q = jami_t * 1e6 / (soat * 3600.0)
    return {
        "uy_jami": uy_soni,
        "isitiladigan_uy": isitiladigan,
        "gaz_uy": gaz_uy,
        "komir_uy": komir_uy,
        "energiya_gj": {"gaz": e_gaz, "komir": e_komir},
        "komir_t": komir_t,
        "emissiya_t": {k: v / 1e6 for k, v in em.items()},
        "jami_t": jami_t,
        "oqim_g_s": Q,
        "konsentratsiya_ug_m3": quti_konstentratsiyasi(Q, L_m, H_m, u_ms),
    }


def kerak_qattiq_ulush(talab_t: float, isitiladigan_uy: float, m3_uy: float = M3_ISITISH_BAZA,
                       modda: str = "pm25") -> dict[str, float]:
    """Teskari masala #2: kuzatilgan ortishni **butunlay** tushuntirish uchun
    isitish energiyasining qancha qismi qattiq yoqilg'idan bo'lishi kerak.

    E_heat = uy × m³ × NCV;  PM(s) = (1-s)·E_heat·EF_gaz + s·E_heat·EF_ko'mir
    s = (Talab − E_heat·EF_gaz) / (E_heat·(EF_ko'mir − EF_gaz))
    """
    e_heat = energiya_gj(gaz_m3=isitiladigan_uy * m3_uy)
    ef_g = EMEP_1A4B_EF["gaz"][modda]
    ef_k = EMEP_1A4B_EF["komir"][modda]
    talab_g = talab_t * 1e6
    gaz_hissa_g = e_heat * ef_g
    s = (talab_g - gaz_hissa_g) / (e_heat * (ef_k - ef_g))
    return {
        "energiya_gj": e_heat,
        "gaz_only_g": gaz_hissa_g,
        "gaz_only_t": gaz_hissa_g / 1e6,
        "qattiq_ulush": s,
        "komir_t": s * e_heat / KOMIR_NCV_GJ_T,
    }


def sezgirlik(aholi_ming: float = 3164.0, xususiy_ulush: float = 0.352,
              delta_pm: float = 10.24, soat: float = 2319.0,
              u_baza: float = 3.16, modda: str = "pm25") -> dict[str, dict[str, float]]:
    """Asosiy noaniqliklar bo'yicha sezgirlik: natija (qattiq yoqilg'i ulushi) qanchalik o'zgaradi."""
    n = {}
    for nom, H_m, u, m3, xu in [
        ("baza (H=300, u=3,16, 2500 m³)", 300.0, u_baza, 2500.0, xususiy_ulush),
        ("sayoz aralashish H=200 m", 200.0, u_baza, 2500.0, xususiy_ulush),
        ("chuqur aralashish H=500 m", 500.0, u_baza, 2500.0, xususiy_ulush),
        ("shamol 2,5 m/s", 300.0, 2.5, 2500.0, xususiy_ulush),
        ("shamol 4,0 m/s", 300.0, 4.0, 2500.0, xususiy_ulush),
        ("kam gaz 1 700 m³/uy", 300.0, u_baza, 1700.0, xususiy_ulush),
        ("ko'p gaz 3 200 m³/uy", 300.0, u_baza, 3200.0, xususiy_ulush),
        ("xususiy uy 25%", 300.0, u_baza, 2500.0, 0.25),
        ("xususiy uy 45%", 300.0, u_baza, 2500.0, 0.45),
    ]:
        uy = uy_xo_jaliklari(aholi_ming) * xu
        talab = mavsum_massasi_tonna(talab_emissiya(delta_pm, 20000.0, H_m, u), soat)
        n[nom] = {**kerak_qattiq_ulush(talab, uy, m3, modda), "talab_t": talab}
    return n


def xulosa(delta_kuzatilgan: float, talab_t: float, kerak: dict[str, float],
           traser: dict[str, Any] | None = None,
           sez: dict[str, dict[str, float]] | None = None) -> list[str]:
    """Qisqa, halol xulosalar ro'yxati (raqamlar bilan)."""
    x: list[str] = []
    x.append(f"Kuzatilgan qishki ortish ΔPM2,5 = {delta_kuzatilgan:.2f} µg/m³ "
             f"(isitish 25,60 ↔ issiq 15,36 µg/m³).")
    x.append(f"Faqat emissiya bilan tushuntirish uchun mavsumda {talab_t:.0f} t PM2,5 kerak "
             f"(quti modeli, garmonik shamol).")
    x.append(f"Gaz bilan isitish bu talabning atigi {kerak['gaz_only_t']:.1f} t ini beradi "
             f"({kerak['gaz_only_t'] / talab_t:.1%}) → gaz **deyarli hissa qo'shmaydi** "
             f"(PM2,5 1,2 g/GJ).")
    x.append(f"Talabni to'liq qoplash uchun isitish energiyasining "
             f"**{kerak['qattiq_ulush']:.1%}** qismi qattiq yoqilg'idan bo'lishi kerak "
             f"(≈ {kerak['komir_t']:,.0f} t ko'mir/mavsum).".replace(",", " "))
    _g = gaz_kerak_pm(talab_t)
    x.append(f"Ayni shu massani **gaz** bilan chiqarish uchun {_g['gaz_mlrd_m3']:.1f} mlrd m³ gaz "
             f"kerak bo'lardi — O'zbekistonning butun yillik gaz qazib olishi (42,3 mlrd m³, 2025) "
             f"bilan bir tartibda ⇒ gaz strukturaviy jihatdan tushuntira olmaydi.")
    if sez:
        lo = min(v["qattiq_ulush"] for v in sez.values())
        hi = max(v["qattiq_ulush"] for v in sez.values())
        x.append(f"Sezgirlik (9 variant): {lo:.1%} – {hi:.1%} — kattalik darajasi barqaror.")
    if traser:
        k = traser["komir_nisbati"]
        x.append(f"Traser testi: kuzatilgan PM2,5/CO = {traser['kuzatuv']['pm_co']:.4f}; "
                 f"ko'mir EF nisbati {traser['ef_nisbat']['pm_co']:.4f} "
                 f"(kuzatuv/EF = {k['pm_co']:.2f}), gaz EF nisbati 0,0462 "
                 f"({traser['gaz_nisbati']['pm_co']:.2f}).")
        x.append("  → PM2,5/CO nisbati gazga yaqinroq, lekin qishda CO uzoq yashaydi "
                 "(OH radikali kamayadi) va quti modeli meteorologiyani olmaydi — "
                 "shuning uchun test **kuchsiz**: ko'mirni rad eta olmaydi, faqat cheklaydi.")
    x.append("Chegara: quti modeli stagnatsiya/inversiyani va ikkilamchi aerozol kimyosini "
             "hisobga olmaydi; natija — kattalik darajasi, aniq qiymat emas.")
    return x


def _fmt(v: float, n: int = 2) -> str:
    return f"{v:,.{n}f}".replace(",", " ")


def matn(natija: dict[str, Any]) -> str:
    """CLI uchun o'qishga qulay matn."""
    q: list[str] = []
    q.append("MAISHIY ISITISH HISSASI — yoqilg'i asosidagi baho")
    q.append(f"  Manba: {EFA_MANBA} · {EFA_SANA}")
    q.append(f"  Quti: L={_fmt(natija['L_m'], 0)} m · H={_fmt(natija['H_m'], 0)} m · "
             f"u={_fmt(natija['u_ms'], 2)} m/s (garmonik) · soat {_fmt(natija['soat'], 0)}")
    q.append(f"  Uy xo'jaliklari {_fmt(natija['uy_jami'], 0)} · isitiladigan xususiy "
             f"{_fmt(natija['isitiladigan_uy'], 0)} ({natija['xususiy_ulush']:.1%})")
    q.append("")
    q.append(f"  {'qattiq yoqilg\'i ulushi':28}{'ko`mir, t':>12}{'PM2,5, t':>10}{'µg/m³':>9}{'kuzatuvga':>11}")
    for nom, s in natija["ssenariylar"].items():
        q.append(f"  {nom:28}{_fmt(s['komir_t'], 0):>12}{_fmt(s['jami_t'], 1):>10}"
                 f"{_fmt(s['konsentratsiya_ug_m3'], 3):>9}{s['konsentratsiya_ug_m3'] / natija['delta']:>10.1%}")
    q.append("")
    _k = yoqilgi_kerak(natija['talab']['massa_t'], "komir", "pm25")
    _g = gaz_kerak_pm(natija['talab']['massa_t'])
    q.append(f"  TALAB: kuzatilgan Δ={_fmt(natija['delta'], 2)} µg/m³ ni qoplash uchun "
             f"{_fmt(natija['talab']['massa_t'], 0)} t PM2,5/mavsum")
    q.append(f"    · ko'mir bilan: {_fmt(_k['komir_t'], 0)} t (NCV 20 GJ/t) · energetik ekvivalenti "
             f"{_fmt(_k['gaz_mln_m3'], 0)} mln m³ gaz")
    q.append(f"    · gaz bilan: {_fmt(_g['gaz_mlrd_m3'], 1)} mlrd m³ kerak bo'lardi ⇒ mumkin emas")
    q.append("")
    for satr in natija["xulosalar"]:
        q.append(f"  {satr}" if not satr.startswith("  ") else "  " + satr)
    if natija.get("sezgirlik"):
        q.append("")
        q.append(f"  {'sezgirlik varianti':34}{'talab, t':>10}{'qattiq ulush':>13}{'ko`mir, t':>12}")
        for nom, v in natija["sezgirlik"].items():
            q.append(f"  {nom:34}{_fmt(v['talab_t'], 0):>10}{v['qattiq_ulush']:>12.1%}{_fmt(v['komir_t'], 0):>12}")
    return "\n".join(q)


def hisobot(aholi_ming: float = 3164.0, xususiy_ulush: float = 0.352,
            kishi_uy: float = KISHI_UY_BAZA, m3_uy: float = M3_ISITISH_BAZA,
            delta_pm: float = 10.24, delta_co: float = 238.05, delta_sox: float = 5.57,
            soat: float = 2319.0, L_m: float = 20000.0, H_m: float = 300.0,
            u_ms: float | None = None, shamol: Iterable[float | None] | None = None,
            modda: str = "pm25") -> dict[str, Any]:
    """To'liq hisob-kitob: uy soni → ssenariylar → talab → kerakli ulush → traser → xulosa."""
    if u_ms is None:
        u_ms = garmonik_shamol(shamol) if shamol is not None else 3.16
    uy = uy_xo_jaliklari(aholi_ming, kishi_uy)
    isitiladigan = uy * xususiy_ulush
    ssen = {}
    for ulush in (0.0, 0.10, 0.15, 0.25):
        ssen[f"qattiq {ulush:.0%} · gaz {1 - ulush:.0%}"] = stsenariy(
            uy, xususiy_ulush, 1.0 - ulush, m3_uy, soat, L_m, H_m, u_ms, modda)
    Q_talab = talab_emissiya(delta_pm, L_m, H_m, u_ms)
    talab_t = mavsum_massasi_tonna(Q_talab, soat)
    kerak = kerak_qattiq_ulush(talab_t, isitiladigan, m3_uy, modda)
    traser = traser_tekshiruvi(delta_pm, delta_co, delta_sox, "komir")
    sez = sezgirlik(aholi_ming, xususiy_ulush, delta_pm, soat, u_ms, modda)
    return {
        "uy_jami": uy, "isitiladigan_uy": isitiladigan, "xususiy_ulush": xususiy_ulush,
        "ssenariylar": ssen, "delta": delta_pm, "u_ms": u_ms, "soat": soat,
        "L_m": L_m, "H_m": H_m,
        "talab": {"oqim_g_s": Q_talab, "massa_t": talab_t, **{k: v for k, v in kerak.items() if k != "qattiq_ulush"}},
        "kerak_ulush": kerak,
        "traser": traser,
        "sezgirlik": sez,
        "xulosalar": xulosa(delta_pm, talab_t, kerak, traser, sez),
        "manba": {"ef": EFA_MANBA, "sana": EFA_SANA, "ap42": AP42_MANBA,
                  "gaz_ncv_gj_m3": GAZ_NCV_GJ_M3, "komir_ncv_gj_t": KOMIR_NCV_GJ_T},
    }
