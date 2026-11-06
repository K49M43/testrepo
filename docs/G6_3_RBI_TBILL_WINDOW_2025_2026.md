# RBI 91-day T-bill source qualification — 2025–26 window

**Status:** Exact-date one-year descriptive panel qualified; not a long-run risk history.  
**Retrieved:** 2026-11-06 UTC in GitHub Actions run [42230796363](https://github.com/K49M43/testrepo/actions/runs/42230796363).  
**Durable bytes:** [`rbi_tbill_window_2025_2026/`](../research/stage512/2026-11-06/g6_3/rbi_tbill_window_2025_2026/) stores the exact RBI HTML captures, source manifest and normalized CSV.  
**Independent result:** `PASS_RBI_TBILL_2025_2026_EXACT_DATE_PANEL`.

## Verified coverage

- Official RBI Table 218 91-day auction window: 2025-07-02 through 2026-06-24; 50 unique dated rows.
- 50/50 corresponding auction notices and 50/50 corresponding full-result pages captured from the official RBI press-release archive.
- 114 raw source captures total: initial archive index, 13 month-filtered archive pages, 50 auction notices and 50 full-result pages. Every retained file has byte length and SHA-256 in `manifest.json`.
- For 49 positive-issue dates, full-result 91-day cut-off yield matches Table 218 exactly; full-result cut-off price rounds to the two-decimal Table 218 price using half-up rounding.
- 2026-03-25 is kept as a zero-issue exception: Table 218 has no investable price/yield; it is not imputed.
- Missing 182-day and 364-day values on some 91-day auctions remain unavailable; they are not filled or used to reject a valid 91-day observation.

## Reproduce the independent audit

From the repository root:

```powershell
python decision/audit_g6_3_rbi_tbill_window.py research/stage512/2026-11-06/g6_3/rbi_tbill_window_2025_2026
```

The audit rehashes each raw capture, requires exact Table 218 date coverage, matches notices and result pages by date, and reconciles issue/settlement fields, 91-day cut-off yields and rounded prices.

## Interpretation and limits

This qualifies an official 91-day T-bill auction data route and a one-year observed panel. It is short-duration cash-equivalent evidence and is **not** a duration-matched government-bond return series. It does not estimate long-run equity–sovereign correlation, 2036 return distributions, investor-specific Retail Direct allotment or fill, rolling reinvestment economics, fees, taxes, CPI-adjusted wealth, or investment readiness. G6.3 remains open; decision remains **NO-GO / NOT YET EVALUATED**.
