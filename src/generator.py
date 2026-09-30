# -*- coding: utf-8 -*-
"""S1 — UZ-Proksi generator (TZ §6.3 pseudokodining implementatsiyasi).

Sektor taqsimoti: Energy 60%, Agriculture 18%, IPPU 15%, Waste 5%, Other 2%
Davr: 2021Q1–2026Q2 (22 kvartal).  A1–A8 anomaliyalari ssenariy bo'yicha kiritiladi.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

SECTORS = {"energy": 0.60, "agriculture": 0.18, "ippu": 0.15, "waste": 0.05, "other": 0.02}
PERIODS = pd.period_range("2021Q1", "2026Q2", freq="Q")
ANOMALY_TYPES = ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"]

# sektor parametrlari
SECTOR_P = {
    "energy":      dict(prod=120.0, eff=0.42, gas=0.86, coal=0.09, diesel=0.03, other=0.02,
                        ef_gas=53.06, ef_coal=94.6, ef_diesel=74.1, ef_other=60.0,
                        process=0.01, fugitive=0.030, seas=0.10, offsets=0.010),
    "agriculture": dict(prod=40.0, eff=0.55, gas=0.72, coal=0.02, diesel=0.24, other=0.02,
                        ef_gas=53.06, ef_coal=94.6, ef_diesel=74.1, ef_other=60.0,
                        process=0.02, fugitive=0.050, seas=0.28, offsets=0.005),
    "ippu":        dict(prod=80.0, eff=0.38, gas=0.60, coal=0.22, diesel=0.10, other=0.08,
                        ef_gas=53.06, ef_coal=94.6, ef_diesel=74.1, ef_other=60.0,
                        process=0.22, fugitive=0.015, seas=0.04, offsets=0.020),
    "waste":       dict(prod=25.0, eff=0.80, gas=0.30, coal=0.00, diesel=0.20, other=0.50,
                        ef_gas=53.06, ef_coal=94.6, ef_diesel=74.1, ef_other=25.0,
                        process=0.01, fugitive=0.180, seas=0.06, offsets=0.001),
    "other":       dict(prod=60.0, eff=0.50, gas=0.75, coal=0.05, diesel=0.10, other=0.10,
                        ef_gas=53.06, ef_coal=94.6, ef_diesel=74.1, ef_other=60.0,
                        process=0.05, fugitive=0.020, seas=0.08, offsets=0.008),
}


def generate(n_companies: int = 2300, injection_rate: float = 0.15, seed: int = 42) -> pd.DataFrame:
    """≈n_companies × 22 kvartal yozuv qaytaradi (label + anomaly_type bilan)."""
    rng = np.random.default_rng(seed)
    sectors = list(SECTORS)
    probs = np.array([SECTORS[s] for s in sectors])
    sizes = rng.lognormal(mean=0.0, sigma=0.8, size=n_companies)
    comp_sector = rng.choice(sectors, size=n_companies, p=probs)

    n_q = len(PERIODS)
    q_idx = np.arange(n_q)
    rows = []
    for ci in range(n_companies):
        p = SECTOR_P[comp_sector[ci]]
        base = p["prod"] * sizes[ci]
        growth = 1.015 ** (q_idx / 4.0)
        season = 1.0 + p["seas"] * np.sin(2 * np.pi * (q_idx % 4) / 4.0)
        production = base * growth * season * (1 + rng.normal(0, 0.03, n_q))
        energy = production / p["eff"] * (1 + rng.normal(0, 0.05, n_q))
        gas_share = np.clip(p["gas"] + rng.normal(0, 0.01, n_q), 0, 1)
        coal_share = np.clip(p["coal"] + rng.normal(0, 0.005, n_q), 0, 1 - gas_share)
        share_sum = gas_share + coal_share
        diesel = np.clip(p["diesel"] + rng.normal(0, 0.004, n_q), 0, 1)
        other = np.clip(1 - share_sum - diesel, 0, None)
        fuel_energy = energy[:, None] * np.stack([gas_share, coal_share, diesel, other], axis=1)
        ef = np.array([p["ef_gas"], p["ef_coal"], p["ef_diesel"], p["ef_other"]]) / 1000.0
        combustion = fuel_energy @ ef
        process = production * p["process"] * 0.25
        fugitive = production * p["fugitive"] * 0.18
        waste_ch4 = production * (0.02 if comp_sector[ci] == "waste" else 0.001)
        implied = combustion + process + fugitive + waste_ch4
        offsets = implied * p["offsets"] * (1 + rng.normal(0, 0.2, n_q))
        reported = (implied - offsets) * (1 + rng.normal(0.0, 0.06, n_q))
        rep_prod, rep_energy = production.copy(), energy.copy()
        rep_gas_share = gas_share.copy()
        rep_fugitive = fugitive.copy()
        rep_offsets = offsets.copy()
        label = np.zeros(n_q, dtype=int)
        atype = np.array([""] * n_q, dtype=object)

        # ---- injection ----
        k = int(round(injection_rate * n_q))
        if k > 0:
            sel = rng.choice(n_q, size=k, replace=False)
            for t, q in zip(rng.choice(ANOMALY_TYPES, size=k), sel):
                # A6 (4 davr takror) — blok sifatida belgilanadi
                if t == "A6":
                    start = max(0, min(q, n_q - 4))
                    block = slice(start, start + 4)
                    reported[block] = reported[start]
                    label[block] = 1
                    atype[block] = np.where(atype[block] == "", "A6", atype[block])
                    continue
                if t == "A1":
                    reported[q] *= rng.uniform(0.60, 0.85)
                elif t == "A2":
                    rep_gas_share[q] = float(np.clip(gas_share[q] * 0.7, 0, 1))
                    reported[q] *= 0.985          # EF yangilanmaganining kichik izi
                elif t == "A3":
                    rep_fugitive[q] = 0.0
                    reported[q] -= fugitive[q]
                elif t == "A4":
                    reported[q] *= 1000.0 if rng.random() < 0.5 else 1 / 1000.0
                elif t == "A5":
                    rep_prod[q] = production[q] * 1.18
                    rep_energy[q] = energy[q] * 1.01
                elif t == "A7":
                    rep_offsets[q] = offsets[q] * 2.0
                    reported[q] = (implied[q] - 2 * offsets[q]) * (1 + rng.normal(0, 0.02))
                elif t == "A8":
                    if q > 0:
                        reported[q] = 0.85 * implied[q] + 0.15 * implied[q - 1] - offsets[q]
                label[q] = 1
                atype[q] = t if atype[q] == "" else atype[q]

        rows.append(pd.DataFrame({
            "company_id": f"C{ci:05d}", "sector": comp_sector[ci],
            "quarter": PERIODS.astype(str), "q_index": q_idx,
            "production": production, "energy": energy,
            "reported_production": rep_prod, "reported_energy": rep_energy,
            "gas_share_reported": rep_gas_share,
            "reported_ghg": reported, "implied_ghg": implied,
            "fugitive_reported": rep_fugitive, "offsets_reported": rep_offsets,
            "label": label, "anomaly_type": atype,
        }))
    df = pd.concat(rows, ignore_index=True)
    return df


if __name__ == "__main__":
    d = generate()
    print(d.shape, "| anomaliya ulushi:", round(d["label"].mean(), 4))
    print(d["anomaly_type"].value_counts())
