# Groundtruth Atlas

**One county dashboard for housing return and homeowners-insurance risk.**

**Live site:** <https://topninja.github.io/groundtruth-atlas/>

Groundtruth Atlas combines the original **CAP//RATE** and **The Premium Map** projects into one responsive, static site. A county selected in one dataset stays selected in the other, making it possible to move directly from rental economics to insurance pressure without changing sites or losing context.

Open [`index.html`](index.html) to launch the atlas. There is no application build and no package install.

## What changed

- One top-level **Cap Rate / Insurance Premium** switch
- One shared county map, state filter, search, ranking, tooltip, and URL state
- Five return lenses and six insurance lenses
- A joined **Risk / Return** view plotting effective cap rate against the Repricing Index
- A combined county dossier that surfaces metrics from both datasets
- The original editable deal calculator, now connected to the shared county selection
- A compact cobalt product UI with card-based summaries, a floating county dossier, and responsive drawers
- Local, vendored D3 and TopoJSON; no runtime CDN dependency

The two original projects remain in their folders as data and methodology sources:

```text
.
├── index.html                         # unified application
├── README.md                          # this guide
├── cap-rate/                          # return data + source pipeline/app
│   ├── data/
│   ├── pipeline/
│   └── index.html
└── premium/                           # insurance data + source pipeline/app
    ├── data/
    ├── pipeline/
    ├── vendor/
    └── index.html
```

## Run locally

The simplest option is to open `index.html` directly in a modern browser. For a local HTTP server:

```bash
python -m http.server 8000
```

Then visit <http://localhost:8000>.

The atlas loads these existing local modules:

- `premium/data/topology.js`
- `premium/data/counties.js`
- `premium/data/national.js`
- `cap-rate/data/counties.js`
- `cap-rate/data/national.js`

Do not move or rename either source folder without updating the script paths near the bottom of `index.html`.

## Using the atlas

Choose **Cap Rate** or **Insurance Premium** in the header, then select a lens from the left rail. Click a county—or find one by search or ranking—to open its dossier.

The **Risk / Return** view is the actual join between the datasets:

- horizontal axis: modeled Insurance Repricing Index, from lower to higher pressure;
- vertical axis: modeled current effective cap rate;
- dot color: cap-rate basis points lost to insurance escalation;
- state filter and county selection: shared with the map.

Selections are encoded in the URL hash and can be bookmarked or shared. Supported parameters are:

| Parameter | Meaning | Example |
|---|---|---|
| `m` | dataset mode | `cap`, `premium` |
| `l` | active lens | `cn`, `dr`, `prem`, `nr`, `dx` |
| `y` | year for time-based insurance lenses | `2022` |
| `s` | state abbreviation | `FL` |
| `c` | five-digit county FIPS | `12086` |
| `v` | visualization | `matrix` |

Example:

```text
#m=premium&l=prem&y=2022&s=FL&c=12086
```

Keyboard shortcuts: `/` focuses county search; `Esc` closes search results and mobile drawers.

## Map lenses

### Cap rate

| Lens | Meaning | Status |
|---|---|---|
| Effective cap rate | NOI after current estimated insurance, divided by home value | Modeled |
| Insurance drag | Cap-rate basis points lost versus the county's 2021 premium | Modeled |
| Gross yield | Annual rent divided by Zillow home value | Source-derived |
| Insurance share of rent | Current estimated premium divided by gross annual rent | Modeled |
| Cap at 2021 insurance | Comparison cap rate using the 2021 premium | Modeled |

### Insurance premium

| Lens | Meaning | Status |
|---|---|---|
| Premium per policy | Annual average premium, 2018–2022 plus a 2023–2025 estimated tail | Sourced / modeled tail |
| Premium escalation | Change in premium per policy from 2018 to 2022 | Source-derived |
| Non-renewal rate | Share of policies insurers declined to renew, 2018–2023 | Sourced |
| Paid loss ratio | Paid losses divided by written premium, 2018–2022 | Sourced |
| Claim frequency | Paid claims divided by policies in force, 2018–2022 | Sourced |
| Repricing Index | Composite county pressure score from 0 to 100 | Modeled |

## Methodology

### Effective cap rate

The screening model uses:

```text
gross income = 12 × monthly rent
operating stack = gross income × 23%
property tax = county effective tax rate × home value
NOI = gross income − operating stack − property tax − premium
effective cap rate = NOI ÷ home value
insurance drag = (estimated current premium − 2021 premium) ÷ home value × 10,000
```

The 23% operating stack combines 5% vacancy, 8% management, and 10% maintenance/capital expenditure assumptions. The calculator scales the county premium with the entered price and keeps the county property-tax rate.

### Premium nowcast

The sourced Treasury FIO series ends in 2022. The modeled 2023–2025 tail applies national approved-rate anchors to each county's 2022 premium:

```text
2023: +12.7%
2024: +10.4%
2025:  +6.0%
```

These estimates are a national nowcast, not county quotes. Real filings and household premiums vary substantially.

### Repricing Index

```text
0.35 × premium-escalation percentile
+ 0.25 × 2023 non-renewal percentile
+ 0.20 × paid-loss-ratio percentile
+ 0.20 × recent-disaster-declaration percentile
```

The result is an editorial screening gauge, not an actuarial score.

## Data lineage

| Source | Vintage | Used for |
|---|---|---|
| [Zillow Research](https://www.zillow.com/research/data/) | May 2026 files in the source project | County ZHVI values and ZORI rents |
| [HUD Fair Market Rents](https://www.huduser.gov/portal/datasets/fmr.html) | FY 2026 | Three-bedroom rent fallback outside ZORI coverage |
| [U.S. Census ACS](https://data.census.gov/) | Source-project extract | County effective property-tax rate |
| [U.S. Treasury FIO / NAIC PCMI](https://home.treasury.gov/news/press-releases/jy2791) | Released January 2025; data through 2022 | Premium, loss ratio, claim frequency and severity |
| [U.S. Senate Budget Committee](https://www.budget.senate.gov/chairman/newsroom/press/new-data-reveal-climate-change-driven-insurance-crisis-is-spreading) | Released December 2024; data through 2023 | County non-renewal rates and policies in force |
| [OpenFEMA Disaster Declarations Summaries](https://www.fema.gov/openfema-data-page/disaster-declarations-summaries-v2) | Source-project pull | County disaster history |
| [Census ZCTA–county relationship file](https://www.census.gov/geographies/reference-files/time-series/geo/relationship-files.html) | 2020 | ZIP-to-county assignment |
| [S&P Global Market Intelligence](https://www.spglobal.com/market-intelligence/en/news-insights/articles/2025/1/us-homeowners-rates-rise-by-double-digits-for-2nd-straight-year-in-2024-87061085) | 2023–2025 anchors | Modeled premium tail |
| [us-atlas](https://github.com/topojson/us-atlas) | counties-10m | County and state geometry |

See the original project documentation for the complete acquisition and transformation notes:

- [`cap-rate/README.md`](cap-rate/README.md)
- [`premium/README.md`](premium/README.md)

## Rebuild the source data

Each source project retains its own pipeline. Run it from that project's directory so relative paths resolve correctly.

Cap-rate data:

```bash
cd cap-rate
bash pipeline/fetch.sh
python pipeline/build.py
```

Insurance data:

```bash
cd premium
bash pipeline/fetch.sh
python pipeline/build.py
```

Python 3 and `openpyxl` are required by the source pipelines. Review generated changes before publishing; upstream schemas and public download URLs can change.

## Data-quality guardrails

The unified UI computes choropleth scales from the 3rd–97th percentile so extreme values do not flatten the map. It also suppresses impossible cap-rate values caused by malformed upstream tax rows. When a county tax rate is missing or invalid, the deal calculator uses the source model's 1.1% fallback and labels that fallback in the dossier.

Other important limitations:

- ZHVI is a mid-tier owner-home index, not an investor purchase price.
- ZORI is asking rent; HUD FMR is a 40th-percentile fallback and is not directly equivalent.
- FIO public records are composition-smoothed ZIP means and exclude parts of the market.
- Premium per policy reflects changes in coverage and insured value as well as rate.
- FAIR plans, Citizens, and excess-and-surplus carriers are outside the FIO public data.
- County aggregation hides property-level differences in condition, hazard, taxes, and coverage.

Use the atlas to screen and compare markets. Verify any investment decision with property-level rent, tax, insurance, condition, and financing information.

## Deploy

The project is static and can be published from the repository root with GitHub Pages, Netlify, Cloudflare Pages, or any ordinary web server. For GitHub Pages, select the repository's default branch and `/ (root)` as the publishing source. No build command is required.

## Attribution and data terms

Underlying datasets remain subject to their publishers' terms. Zillow Research data require attribution; U.S. federal datasets are generally public domain. Original instruments and methodology by William Brewer.
