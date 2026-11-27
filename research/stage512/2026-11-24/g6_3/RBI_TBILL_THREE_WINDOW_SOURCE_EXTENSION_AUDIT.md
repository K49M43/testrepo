# G6.3 RBI 91-day T-bill three-window source extension

**Audit date:** 2026-11-24
**Scope:** qualify and deduplicate one earlier official RBI auction window. This is source and overlap work; it does not establish investor returns, portfolio risk, or investment readiness.

## Result

RBI's official [Table 213 publication](https://www.rbi.org.in/scripts/PublicationsView.aspx?id=22687) contains 60 dated rows from 2023-07-12 through 2024-08-28. All 60 rows pair to one RBI auction notice and one RBI full-result page. The 91-day cutoff yield matches Table 213 exactly, and the cutoff price rounds to its displayed two-decimal value on every row. All 60 rows have positive 91-day issue; no zero issue was imputed.

Together with the previously qualified Table 217 and Table 218 windows:

| Source window | Dated rows | Period | Matched notices and results |
|---|---:|---|---:|
| Table 213 | 60 | 2023-07-12 to 2024-08-28 | 60 / 60 |
| Table 217 | 55 | 2024-07-03 to 2025-07-30 | 55 / 55 |
| Table 218 | 50 | 2025-07-02 to 2026-06-24 | 50 / 50 |

The nine Table 213/Table 217 overlap dates and five Table 217/Table 218 overlap dates match across issue date, notified amount, total issue, cutoff and weighted prices/yields, method, and result status. Deduplication yields **151 auction dates** and **149 positive 91-day price observations** from 2023-07-12 through 2026-06-24. The two zero-issue exceptions are 2025-02-20 and 2026-03-25.

Across the 149 positive issues, the weighted-average 91-day yield levels range from **5.1916% to 7.0408%**, with median **6.4644%** and mean **6.2035%**. These are annualized auction quote levels. They are not realized return volatility, a chained investor return, or independent samples for a probability estimate.

## Four handbook/notice issue-date differences

Table 213's issue-date field differs from its auction notice on four dates:

| Auction date | Table 213 issue date | Auction notice issue date |
|---|---|---|
| 2023-09-27 | 2023-09-28 | 2023-09-29 |
| 2024-04-10 | 2024-04-11 | 2024-04-12 |
| 2024-05-22 | 2024-05-23 | 2024-05-24 |
| 2024-08-14 | 2024-08-15 | 2024-08-16 |

The source table and notice values are both retained in the Table 213 panel and manifest. The normalized `issue_date` follows the date in the contemporaneous auction notice; the original handbook value remains in `table_issue_date`. The 2024-08-14 notice date is also independently corroborated by the Table 217 window. The other three differences remain explicit notice-versus-handbook discrepancies, not silently corrected source rows. A separate extension of RBI's Mumbai holiday calendar is needed to check the date pattern against the settlement calendar before expanding the rollover-mechanics scenario.

## Capture and reproducibility

The source package is `research/stage512/2026-11-24/g6_3/rbi_tbill_window_2023_2024/`. It contains 136 manifest-listed raw responses (archive index, 15 archive months, 60 notices, and 60 full results); the Table 213 page is a separately referenced 137th raw body under `source_raw/`. All raw bodies have byte lengths and SHA-256 values.

The online acquisition wrote all bodies, then stopped before emitting a manifest when it detected a Table 213/notice issue-date difference. The saved bodies were reconciled offline; no second RBI retrieval was made. The manifest states that the acquisition code had checked HTTP 200 before writing each body, but the failed run did not persist `Content-Type` response headers. The `content_type` field is therefore marked `NOT_RETAINED_DURING_CAPTURE_ATTEMPT`; it is not guessed. Per-file UTC timestamps are filesystem write times, not asserted server timestamps. The independent audit verifies raw source hashes, exact Table dates, notice/result uniqueness, reported source conflicts, and the normalized CSV hash.

The separate corrected rollover v2 audit remains scoped to the 2024–2026 quote windows and its existing Mumbai holiday capture. This extension does not yet produce a three-year maturity/holiday-adjusted roll schedule. Neither this source panel nor the observed quote levels establish long-run T-bill risk, equity–bond covariance, a 2014–2026 history, or 2036 success probability.

## Reproduction commands

Reconstruct the manifest and normalized panel from the retained capture without network access:

```powershell
python research/stage512/2026-11-06/g6_3/reconcile_rbi_tbill_window_capture.py `
  --table-path research/stage512/2026-11-24/g6_3/source_raw/table213_20240913.html `
  --table-url https://www.rbi.org.in/scripts/PublicationsView.aspx?id=22687 `
  --output-dir research/stage512/2026-11-24/g6_3/rbi_tbill_window_2023_2024 `
  --table-name 'Table 213' --window-tag 2023_2024 --expected-auctions 60 `
  --first-date 2023-07-12 --last-date 2024-08-28
```

Independently audit the Table 213 panel and all three-window overlaps:

```powershell
python decision/audit_g6_3_rbi_tbill_window.py `
  research/stage512/2026-11-24/g6_3/rbi_tbill_window_2023_2024 `
  --table-path research/stage512/2026-11-24/g6_3/source_raw/table213_20240913.html `
  --table-name 'Table 213' --window-tag 2023_2024 --expected-auctions 60 `
  --first-date 2023-07-12 --last-date 2024-08-28
python decision/audit_g6_3_rbi_tbill_window_overlap.py --write
python decision/audit_g6_3_rbi_tbill_window_overlap.py --check
```

## Decision consequence

This closes one bounded earlier-source and deduplication gate. It does not close RBI holiday/maturity mechanics for the new dates, investor-specific Retail Direct access/allotment, bid funding liquidity, markup and payment-gateway costs, taxes, long-run risk, cross-asset exact-date overlap, candidate comparison, investor confirmations, or independent probability challenge. G6.3 remains **OPEN / NOT READY**. Investment authorization remains **NO-GO**.
