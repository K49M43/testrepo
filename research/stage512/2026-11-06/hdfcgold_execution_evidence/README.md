# HDFCGOLD NSE five-year archive capture and AMFI comparison

**Scope:** bounded source qualification for the HDFC Gold ETF market-price evidence gate under G6.3. This package does not close G6.3 or authorize an investment.

## Captured source

- First-party source: [NSE Security-wise Archives](https://www.nseindia.com/report-detail/eq_security)
- Query selected in the public UI: Equity, `HDFCGOLD`, series `ALL`, `5Y`; displayed date window 06-Nov-2021 to 06-Nov-2026.
- Raw download: `hdfcgold_nse_5y.csv` (179,671 bytes; SHA-256 `B4F88AD9135F942DDD6E695E7B708C6A10AF1DA957AE3646C5474CF6E6A6C0D4`).
- Local file creation timestamp recorded at capture: 2026-11-06T17:39:43.9505271Z. This is workstation filesystem metadata, not an NSE server timestamp.
- The file has 1,241 observations, 1,241 unique dates, 0 duplicate dates, no non-positive closes, series `EQ` on every row, and a maximum five-calendar-day interval between trading rows. It contains 399 rows under legacy symbol `HDFCMFGETF` and 842 under `HDFCGOLD`.
- NSE circular [NSE/CML/57054](https://archives.nseindia.com/content/circulars/CML57054.pdf) records the symbol change `HDFCMFGETF` → `HDFCGOLD` effective 16-Jun-2023 for ISIN `INF179KC1981`. The observed transition date agrees. NSE's [2026 circular](https://nsearchives.nseindia.com/content/circulars/CML72944.pdf) records the later scheme-name update; it does not change the security identity used here.

## AMFI comparison

The comparison input is the retained normalized AMFI series for scheme `113049`, ISIN `INF179KC1981`, SHA-256 `66b5253e897a89fb0bfff1a44e83bc909c31373040389a32a561b5dbddd3ef0b`, with 2,918 observations from 2015-01-01 through 2026-10-30. Its source manifest and original AMFI segments remain under `research/stage512/2026-11-05/source_retrieval_followup/candidates/`.

The retained series has an observed 100x NAV-level discontinuity from 2021-02-19 to 2021-02-22. This audit does not establish whether the cause is a corporate action or a source/normalization issue. The NSE capture starts on 2021-11-08, after that point, so the reported overlap comparison does not cross the discontinuity.

Exact calendar-date matching produced 1,229 pairs. There are 12 NSE dates without an AMFI row in the retained series: seven inside its coverage window (special NSE sessions) and five after its final date (02-Nov through 06-Nov-2026). No values were forward-filled, interpolated, or otherwise imputed.

The descriptive statistic is `(NSE daily close / same-date AMFI NAV - 1) × 100`. Across 1,229 matches, the median is **+0.0583%**, median absolute difference **0.3151%**, linear-interpolated 5th/95th percentiles **-1.1634% / +0.7626%**, minimum **-3.7645%** (10-Mar-2022), and maximum **+6.4853%** (21-Jan-2026).

Large observations cluster across multiple dates: 09–14 Mar-2022 include several roughly -3% differences; 23–29 Jul-2024 include several +2.6% to +4.8% differences; 19–21 Jan-2026 rise from +1.7% to +6.5%, then return to about +0.3% on 22-Jan. These have not been explained or removed. Date-label close/NAV timing can differ, so they are not confirmed contemporaneous premiums/discounts.

## Interpretation and remaining gate

This package qualifies the captured NSE daily market-price/volume rows and a strictly date-aligned descriptive comparison against the retained AMFI NAV history. NSE quantity and trade count are historical activity indicators only. The archive does not provide historical bid/ask quotes or order-book depth; close and volume cannot establish spreads, slippage, market impact, executable prices, or investor-specific access. These execution-cost and suitability questions remain open, as do the wider candidate, sovereign-security, CPI-base-month and CCIL work packages. **G6.3 remains OPEN; decision remains NO-GO / NOT YET EVALUATED.**

## Reproduction

With Python 3 standard library only, run from the repository root:

```powershell
python research/stage512/2026-11-06/hdfcgold_execution_evidence/audit_hdfcgold_nse_amfi_bridge.py `
  --nse-csv research/stage512/2026-11-06/hdfcgold_execution_evidence/hdfcgold_nse_5y.csv `
  --amfi-csv research/stage512/2026-11-05/source_retrieval_followup/candidates/nav_113049_daily.csv `
  --output research/stage512/2026-11-06/hdfcgold_execution_evidence/hdfcgold_nse_amfi_bridge_v1.json
```

The committed JSON is the generated output. The script records source hashes, exact-date coverage, row checks, unmatched dates, yearly summaries, and largest absolute differences. It is a source audit and must not be read as a portfolio return, calibrated premium model, or execution-cost model.
