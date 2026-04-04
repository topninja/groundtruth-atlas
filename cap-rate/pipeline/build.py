#!/usr/bin/env python3
"""cap-rate-map build — joins county insurance premiums with rents, values,
and property taxes into an insurance-adjusted cap-rate dataset.

Outputs:
  data/processed/cap_rate_county.csv   (analysis-friendly)
  data/counties.js                     (JS module for the file://-friendly site)
  data/national.js                     (national aggregates + assumptions)

Every figure is tagged SOURCED or MODELED. See README methodology.
Run from repo root: python3 pipeline/build.py
"""
import csv, json, statistics
from pathlib import Path

import openpyxl

RAW = Path("raw")
OUT_PROC = Path("data/processed")
OUT_PROC.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- MODELED
# Operating-expense stack (standard SFR underwriting assumptions — MODELED):
VACANCY = 0.05      # 5% of gross rent
MANAGEMENT = 0.08   # 8% of gross rent
MAINT_CAPEX = 0.10  # 10% of gross rent (repairs + capital reserves)
OPEX_SHARE = VACANCY + MANAGEMENT + MAINT_CAPEX  # 23% of gross rent
# ----------------------------------------------------------------

def latest_zillow(path):
    """fips -> (latest_value, latest_month) from a Zillow county CSV."""
    out = {}
    with open(path, newline="") as fh:
        r = csv.reader(fh)
        hdr = next(r)
        months = hdr[9:]
        for row in r:
            fips = row[7].zfill(2) + row[8].zfill(3)
            # last non-empty month
            for i in range(len(row) - 1, 8, -1):
                if row[i]:
                    out[fips] = (float(row[i]), hdr[i][:7])
                    break
    return out

zhvi = latest_zillow(RAW / "zhvi_county.csv")
zori = latest_zillow(RAW / "zori_county.csv")

# HUD FY26 FMRs: fips col is 10-digit (county fips + 99999). Use 3BR as the
# SFR-comparable rent. Metro counties can appear once; some states (CT towns)
# repeat a county across HUD areas -> average.
fmr3 = {}
wb = openpyxl.load_workbook(RAW / "fmr.xlsx", read_only=True)
ws = wb["FY26_FMRs"]
rows = ws.iter_rows(values_only=True)
hdr = next(rows)
ix = {c: i for i, c in enumerate(hdr)}
acc = {}
for row in rows:
    f = str(row[ix["fips"]])[:5]
    v = row[ix["fmr_3"]]
    if v:
        acc.setdefault(f, []).append(float(v))
fmr3 = {f: statistics.mean(v) for f, v in acc.items()}

def acs_county(path, col):
    out = {}
    with open(path) as fh:
        r = csv.reader(fh, delimiter="|")
        hdr = next(r)
        i = hdr.index(col)
        for row in r:
            g = row[0]
            if g.startswith("0500000US") and row[i] not in ("", "."):
                try:
                    out[g[9:]] = float(row[i])
                except ValueError:
                    pass
    return out

acs_tax = acs_county(RAW / "acs_b25103.dat", "B25103_E001")   # median RE taxes paid
acs_val = acs_county(RAW / "acs_b25077.dat", "B25077_E001")   # median home value

counties = {}
with open(RAW / "premium_county_metrics.csv", newline="") as fh:
    for row in csv.DictReader(fh):
        f = row["fips"].zfill(5)
        if f not in zhvi:
            continue  # no value basis -> can't compute a cap rate
        value, vmonth = zhvi[f]
        if f in zori:
            rent, rmonth = zori[f]
            rbasis = "ZORI"
        elif f in fmr3:
            rent, rmonth = fmr3[f], "FY26"
            rbasis = "FMR3"
        else:
            continue
        # effective property-tax RATE from ACS (SOURCED), applied to ZHVI value
        if f in acs_tax and f in acs_val and acs_val[f] > 0:
            tax_rate = acs_tax[f] / acs_val[f]
            tax_src = "ACS"
        else:
            tax_rate = 0.011  # national median fallback (MODELED)
            tax_src = "MODELED"
        tax = tax_rate * value

        if not (row["prem2021"] and row["prem2022"] and row["prem2025_MODELED"]):
            continue  # county lacks FIO premium coverage
        p21 = float(row["prem2021"])                 # SOURCED (FIO)
        p22 = float(row["prem2022"])                 # SOURCED (FIO)
        p25 = float(row["prem2025_MODELED"])         # MODELED (S&P GMI anchors)

        gross = 12 * rent
        egi = gross * (1 - OPEX_SHARE)               # after vacancy/mgmt/maint
        noi21 = egi - tax - p21                      # NOI at 2021-era insurance
        noinow = egi - tax - p25                     # NOI at current insurance
        c = counties[f] = {
            "n": row["county"], "st": row["state"],
            "v": round(value), "vm": vmonth,
            "r": round(rent), "rb": rbasis, "rm": rmonth,
            "tx": round(tax_rate, 5), "ts": tax_src,
            "p21": round(p21), "p22": round(p22), "p25": round(p25),
            "gy": round(gross / value * 100, 2),                 # gross yield %
            "c21": round(noi21 / value * 100, 2),                # cap @2021 ins
            "cn": round(noinow / value * 100, 2),                # cap @current ins
            "dr": round((p25 - p21) / value * 1e4),              # drag, bps
            "is": round(p25 / gross * 100, 1),                   # ins % of rent
            "nr": round(float(row["nonrenew2023"]) * 100, 2),    # nonrenewal %
        }

# ---- national aggregates ----
vals = list(counties.values())
def med(k): return round(statistics.median(x[k] for x in vals), 2)
national = {
    "count": len(vals),
    "zori_count": sum(1 for x in vals if x["rb"] == "ZORI"),
    "med_gy": med("gy"), "med_c21": med("c21"), "med_cn": med("cn"),
    "med_drag": med("dr"), "med_is": med("is"),
    "worst_drag": sorted(((x["dr"], f, x["n"], x["st"]) for f, x in counties.items()), reverse=True)[:15],
    "assumptions": {"vacancy": VACANCY, "management": MANAGEMENT,
                    "maint_capex": MAINT_CAPEX, "tax_fallback": 0.011},
}

with open(OUT_PROC / "cap_rate_county.csv", "w", newline="") as fh:
    cols = ["fips", "county", "state", "value_zhvi", "value_month", "rent_mo",
            "rent_basis", "rent_month", "tax_rate", "tax_rate_source",
            "prem2021_SOURCED", "prem2022_SOURCED", "prem2025_MODELED",
            "gross_yield_pct", "cap_at_2021_ins_pct_MODELED",
            "cap_at_current_ins_pct_MODELED", "insurance_drag_bps",
            "ins_pct_of_rent", "nonrenew2023_pct"]
    w = csv.writer(fh); w.writerow(cols)
    for f in sorted(counties):
        x = counties[f]
        w.writerow([f, x["n"], x["st"], x["v"], x["vm"], x["r"], x["rb"],
                    x["rm"], x["tx"], x["ts"], x["p21"], x["p22"], x["p25"],
                    x["gy"], x["c21"], x["cn"], x["dr"], x["is"], x["nr"]])

Path("data/counties.js").write_text(
    "window.CR=window.CR||{};CR.counties=" + json.dumps(counties, separators=(",", ":")) + ";\n")
Path("data/national.js").write_text(
    "window.CR=window.CR||{};CR.national=" + json.dumps(national, separators=(",", ":")) + ";\n")

print(f"counties: {len(counties)}  (ZORI rents: {national['zori_count']}, "
      f"FMR fallback: {len(vals) - national['zori_count']})")
print(f"median gross yield {national['med_gy']}%  cap@2021ins {national['med_c21']}%  "
      f"cap@now {national['med_cn']}%  median drag {national['med_drag']} bps")
