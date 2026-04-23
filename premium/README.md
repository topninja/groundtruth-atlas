# Insurance-risk data module

This directory contains the insurance side of the unified [Groundtruth Atlas](../README.md). The public application launches from [`../index.html`](../index.html); this folder preserves the insurance pipeline, browser-ready data, and original standalone interface for auditability.

## Contents

```text
premium/
├── data/
│   ├── counties.js                   # browser-ready county risk records
│   ├── national.js                   # national series, sources, and events
│   ├── topology.js                   # U.S. county/state geometry
│   └── processed/county_metrics.csv  # flat county export
├── pipeline/
│   ├── fetch.sh                      # source downloads
│   └── build.py                      # transformation pipeline
├── vendor/                           # local D3 + TopoJSON
└── index.html                        # archived standalone interface
```

The unified root application uses this module's topology and vendored browser libraries for both datasets.

## County record schema

Records are keyed by five-digit county FIPS code. Important fields include:

| Field | Meaning |
|---|---|
| `n`, `st` | County name and state abbreviation |
| `p` | Premium per policy, 2018–2022 |
| `m` | Modeled premium tail, 2023–2025 |
| `nr` | County non-renewal rate, 2018–2023 |
| `lr` | Paid loss ratio, 2018–2022 |
| `cf` | Paid-claim frequency, 2018–2022 |
| `cs` | Average paid-claim severity |
| `pf` | Policies in force |
| `dr` | FEMA declaration counts and recent events |
| `gw` | Premium escalation from 2018 to 2022 |
| `dx` | Modeled Repricing Index, 0–100 |
| `rk` | National percentile ranks |

## Sourced and modeled values

The Treasury FIO series through 2022, Senate non-renewal series through 2023, and FEMA declarations are sourced public records transformed for county aggregation.

The premium nowcast applies national approved-rate anchors to each county's 2022 value:

```text
2023: +12.7%
2024: +10.4%
2025:  +6.0%
```

The Repricing Index is a modeled screening gauge:

```text
35% premium-escalation percentile
25% 2023 non-renewal percentile
20% paid-loss-ratio percentile
20% recent-disaster-declaration percentile
```

Neither modeled artifact is an insurance quote or actuarial score.

## Rebuild

Run commands from this directory:

```bash
bash pipeline/fetch.sh
python pipeline/build.py
```

Requirements: Python 3 and `openpyxl`. The build emits the browser modules and processed CSV export under `data/`.

## Sources

- [U.S. Treasury FIO / NAIC PCMI](https://home.treasury.gov/news/press-releases/jy2791) — premiums, loss ratios, claim frequency, and severity
- [U.S. Senate Budget Committee](https://www.budget.senate.gov/chairman/newsroom/press/new-data-reveal-climate-change-driven-insurance-crisis-is-spreading) — county non-renewals and policies in force
- [OpenFEMA](https://www.fema.gov/openfema-data-page/disaster-declarations-summaries-v2) — county disaster declarations
- [Census ZCTA–county relationships](https://www.census.gov/geographies/reference-files/time-series/geo/relationship-files.html) — ZIP assignment
- [S&P Global Market Intelligence](https://www.spglobal.com/market-intelligence/en/news-insights/articles/2025/1/us-homeowners-rates-rise-by-double-digits-for-2nd-straight-year-in-2024-87061085) — modeled nowcast anchors
- [us-atlas](https://github.com/topojson/us-atlas) — county and state geometry

## Important limitations

- USPS ZIPs and Census ZCTAs are close but not identical.
- Treasury's public subset is composition-smoothed and does not cover the entire market.
- Premium per policy captures coverage and insured-value changes as well as price.
- FAIR plans, Citizens, and excess-and-surplus carriers are outside the FIO public dataset.
- County values can vary substantially from an individual household's premium and renewal outcome.

Use this module to compare broad geographic pressure, then verify coverage and price with property-specific insurance quotes.
