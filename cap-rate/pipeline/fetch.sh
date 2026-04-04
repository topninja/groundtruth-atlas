#!/usr/bin/env bash
# cap-rate-map data fetch — reproduces raw/ from public sources.
# Run from repo root: bash pipeline/fetch.sh
set -euo pipefail
mkdir -p raw
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

# 1. Zillow ZHVI — county, all-homes mid-tier, smoothed seasonally adjusted (SOURCED)
curl -sL -o raw/zhvi_county.csv \
  "https://files.zillowstatic.com/research/public_csvs/zhvi/County_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv"

# 2. Zillow ZORI — county, all-homes asking rent, smoothed (SOURCED)
curl -sL -o raw/zori_county.csv \
  "https://files.zillowstatic.com/research/public_csvs/zori/County_zori_uc_sfrcondomfr_sm_month.csv"

# 3. HUD FY2026 Fair Market Rents — county (SOURCED)
#    huduser.gov sits behind Akamai; needs a browser UA + referer or it returns 202.
curl -sL -A "$UA" -e "https://www.huduser.gov/portal/datasets/fmr.html" \
  -o raw/fmr.xlsx \
  "https://www.huduser.gov/portal/datasets/fmr/fmr2026/FY26_FMRs.xlsx"

# 4. ACS 2019-23 5-yr table-based summary files (no API key needed):
#    B25103 median real estate taxes paid, B25077 median home value (SOURCED)
for t in b25103 b25077; do
  curl -sL -A "$UA" -o "raw/acs_${t}.dat" \
    "https://www2.census.gov/programs-surveys/acs/summary_file/2023/table-based-SF/data/5YRData/acsdt5y2023-${t}.dat"
done

# 5. County insurance premiums — produced by the sibling premium-map repo
#    (Treasury FIO PCMI public subset 2018-22 SOURCED + S&P GMI rate-filing
#    anchors 2023-25 MODELED). Reproduce via premium-map/pipeline, or copy:
cp ../premium-map/data/processed/county_metrics.csv raw/premium_county_metrics.csv

echo "raw/ ready:"; ls -l raw
