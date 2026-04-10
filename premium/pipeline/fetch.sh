#!/usr/bin/env bash
# THE PREMIUM MAP — raw data fetch
# All sources are public. Re-run any time; then: python3 pipeline/build.py
set -euo pipefail
cd "$(dirname "$0")/../raw"

# 1. Treasury FIO / NAIC — PCMI Supporting Underlying Metrics (ZIP-level, 2018-2022)
curl -L -o fio-metrics.xlsx \
  "https://home.treasury.gov/system/files/311/Supporting_Underlying_Metrics_and_Disclaimer_for_Analyses_of_US_Homeowners_Insurance_Markets_2018-2022.xlsx"

# 2. Senate Budget Committee — county non-renewal data (2018-2023)
curl -L -o senate-nonrenewal.xlsx \
  "https://www.budget.senate.gov/download/2024-homeowners-insurance-non-renewal-data_senate-budget-committee&download=1"

# 3. Census 2020 ZCTA <-> county relationship file
curl -L -o zcta-county.txt \
  "https://www2.census.gov/geo/docs/maps-data/data/rel2020/zcta520/tab20_zcta520_county20_natl.txt"

# 4. OpenFEMA disaster declarations (county designations, 2000+)
curl -L -o fema-decl.csv \
  "https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries.csv?\$select=disasterNumber,declarationDate,incidentType,fipsStateCode,fipsCountyCode,designatedArea,declarationTitle&\$filter=declarationDate%20ge%20%272000-01-01T00:00:00.000z%27"

# 5. NOAA / NCEI billion-dollar disasters (final release, 1980-2024; product retired May 2025)
curl -L -o noaa-events.csv "https://www.ncei.noaa.gov/access/billions/events-US-1980-2025.csv"

# 6. Topology (US Census cartography via us-atlas)
curl -L -o counties-10m.json "https://cdn.jsdelivr.net/npm/us-atlas@3/counties-10m.json"

echo "done. now: python3 pipeline/build.py"
