# Cap-rate data module

This directory contains the return side of the unified [Groundtruth Atlas](../README.md). The public application launches from [`../index.html`](../index.html); this folder remains self-contained so its source data can be rebuilt and audited independently.

## Contents

```text
cap-rate/
├── data/
│   ├── counties.js                    # browser-ready county records
│   ├── national.js                    # national summary statistics
│   ├── topology.js                    # original standalone-app geometry
│   └── processed/cap_rate_county.csv  # flat county export
├── pipeline/
│   ├── fetch.sh                       # source downloads
│   └── build.py                       # transformation pipeline
├── raw/                               # source extracts
├── vendor/                            # standalone-app dependencies
└── index.html                         # archived standalone interface
```

The unified root application currently reads `data/counties.js` and `data/national.js`. Shared map geometry and browser libraries come from the sibling [`premium/`](../premium/README.md) module to avoid loading them twice.

## County record schema

Records are keyed by five-digit county FIPS code. Important fields include:

| Field | Meaning |
|---|---|
| `n`, `st` | County name and state abbreviation |
| `v`, `vm` | Zillow Home Value Index and vintage |
| `r`, `rb`, `rm` | Monthly rent, rent basis, and vintage |
| `tx`, `ts` | Effective property-tax rate and source status |
| `p21`, `p22`, `p25` | 2021/2022 sourced premium and 2025 modeled premium |
| `gy` | Gross annual rent yield |
| `c21`, `cn` | Modeled cap rate at 2021 and current insurance |
| `dr` | Insurance drag in cap-rate basis points |
| `is` | Insurance as a percentage of gross rent |

## Model

```text
gross income = 12 × monthly rent
operating stack = gross income × 23%
property tax = effective county tax rate × home value
NOI = gross income − operating stack − property tax − insurance
effective cap rate = NOI ÷ home value
insurance drag = (current premium − 2021 premium) ÷ home value × 10,000
```

The 23% operating assumption comprises 5% vacancy, 8% management, and 10% maintenance/capital expenditures. It is a screening convention, not a property-level operating statement.

## Rebuild

Run commands from this directory:

```bash
bash pipeline/fetch.sh
python pipeline/build.py
```

Requirements: Python 3 and `openpyxl`. The build emits browser modules under `data/` and the processed CSV export.

## Sources

- [Zillow Research](https://www.zillow.com/research/data/) — ZHVI values and ZORI rents
- [HUD Fair Market Rents](https://www.huduser.gov/portal/datasets/fmr.html) — three-bedroom fallback rent
- [U.S. Census ACS](https://data.census.gov/) — effective property-tax inputs
- [U.S. Treasury FIO / NAIC](https://home.treasury.gov/news/press-releases/jy2791) — county premium basis

## Important limitations

- ZHVI is a mid-tier owner-home index, not an investor acquisition price.
- ZORI is asking rent; HUD FMR is a 40th-percentile fallback.
- County averages do not capture property condition, exact tax assessment, coverage, financing, or micro-market rent.
- The unified UI rejects impossible cap-rate artifacts and uses the documented 1.1% tax fallback when an upstream county tax value is invalid.

Use this module for reproducible market screening. Use property-level inputs for an actual underwrite.
