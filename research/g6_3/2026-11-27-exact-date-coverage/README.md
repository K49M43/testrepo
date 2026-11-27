# G6.3 WP1 exact-date return coverage

## Date rule and results

Use retained observations through 30 October 2026 for this comparison. A return interval requires an observed start and end in adjacent calendar months. The start date and the end date must each be identical across the included series. The **individual last dates** column keeps each product's last eligible observation in its month. The **shared dates** column uses the latest date in the month actually observed by every included product. Missing endpoints drop both adjoining intervals. The audit neither interpolates observations nor bridges gaps. Date matching leaves valuation times, dealing cutoffs, and executable prices separate.

| Products with observed NAVs | Prior month-label count | Both individual last dates match | Both shared dates match | Shared start → end | Longest contiguous shared run |
|---|---:|---:|---:|---|---:|
| Motilal Nifty 500 / LIC G-Sec / HDFC Gold | 85 | 83 | 85 | 2019-09-30 → 2026-10-30 | 85 |
| Same mix with ICICI Silver | 57 | 57 | 57 | 2022-01-31 → 2026-10-30 | 57 |
| Motilal Nifty 500 / SBI June 2036 / HDFC Gold | 48 | 31 | 48 | 2022-10-31 → 2026-10-30 | 48 |
| Same mix with ICICI Silver | 48 | 31 | 48 | 2022-10-31 → 2026-10-30 | 48 |
| Previous mix and SBI Nifty 500 for substitution tests | 24 | 11 | 24 | 2024-10-31 → 2026-10-30 | 24 |

The nine shifted month-end observations for the SBI gilt mix under the uniform cutoff affect 17 intervals. For example, the shared mark on 28 June 2024 uses SBI's observed 28 June NAV instead of its 30 June NAV. The longest contiguous run on unchanged individual last dates is 19 months for that mix. The shared dates reproduce all 49 endpoints of the prior silver NAV replay. That replay recorded ten moved month ends before applying the cutoff to the individual comparison observations. Here the common cutoff excludes the later 31 October 2026 SBI observation from the individual endpoints too. [Prior silver NAV replay](../../stage512/2026-11-25/g6_3/icici_silver_etf_source_gate/SILVER_NAV_COMPARISON.md)

The official NSE whitepaper has 129 rounded monthly Nifty 500 TRI returns. Endpoint dates are independently cross-checked secondary mirror dates. The original R9 test reproduces **117/129** intervals with identical individual last dates against LIC. Matching LIC to the benchmark's mapped dates where a real NAV exists yields **121/129**, with a longest run of **58 months**. Adding HDFC Gold gives **120** matched intervals, also with a longest run of **58**. These are separate benchmark diagnostics with a weaker date-source class than first-party product NAV dates. No benchmark values extend a product's pre-inception history. [R9 bridge](../../stage512/data/r9_nse_gsec_129m_source_bridge.json)

The HDFC Gold NSE close archive has 1,236 observations within the common cutoff. HDFC NAV and traded closes share 59 contiguous monthly intervals using observed common dates, and 53 using independently selected last dates. The close archive supplies a price-only cross-check. NAV already reflects fund expenses. HDFC's NAV history uses the documented 100:1 unit rebase to put both periods on the same units. Same-date close and NAV values can still have different valuation times. [HDFC Gold source and rebase audit](../../stage512/2026-11-06/hdfcgold_execution_evidence/README.md)

## Candidate inclusion

These are research inclusion decisions. None of the screened candidates qualifies for an executable shortlist or a probability estimate in this increment.

| Candidate | Observed history available for this work | Inclusion |
|---|---|---|
| Motilal Nifty 500 Index Fund Direct Growth · AMFI 147625 | 1,761 NAVs, 85 monthly intervals | Retain as the equity product for matched NAV replay. |
| SBI Nifty 500 Index Fund Direct Growth · AMFI 152908 | 519 NAVs, 24 intervals | Compare as a shorter equity substitution on equal dates. Both funds represent Nifty 500 exposure. |
| LIC MF Nifty 8–13 Yr G-Sec ETF · AMFI 133307 | 2,867 NAVs, 142 intervals | Retain as a fund NAV duration proxy for replay. A direct bond or ETF trade requires its own price and cashflows. |
| SBI June 2036 Gilt Fund Direct Growth · AMFI 150681 | 993 NAVs, 48 intervals through the cutoff | Retain for NAV replay and conditional forward modeling. Carry separate accrued interest in net receivables and accrued interest included in the mark. Both use the same observed NAV history. |
| HDFC Gold ETF · AMFI 113049 | 2,918 rebased NAVs, 141 intervals. Separate NSE close data as above. | Retain as the gold NAV sleeve. Keep price-only analysis separate from NAV replay. |
| ICICI Prudential Silver ETF · AMFI 149464 | 1,160 NAVs, 57 intervals | Use as a gold-to-silver NAV sensitivity. Paid traded history across the symbol change stays deferred. |
| Motilal Nifty 500 ETF · ISIN INF247L01BU1 | Dated holdings, traded return path unqualified | Retain on the screen as an equity alternative. Exclude from the return panels. |
| ICICI Prudential Gold ETF · ISIN INF109KC1NT3 | Dated holdings, return path unqualified | Exclude from replay pending a decision-relevant separate history. |
| SBI Nifty 10 Year G-Sec ETF · ISIN INF200KA1JT1 | Product identity and holdings, return path unqualified | Retain as a gilt alternative outside the return panels. |
| SBI Gilt Fund Direct Growth · AMFI 119707 | Product identity, return path unqualified | Retain as an active-duration alternative outside the return panels. |
| 6.94% GoI 2036 · ISIN IN0020260025 | Scheduled nominal cashflows and historical auction anchors | Include only in forward cashflow scenarios. Live quote stays deferred. |
| 7.18% GoI 2033 · ISIN IN0020230085 | Candidate identity, 2033-to-2036 reinvestment unqualified | Retain on the screen. Exclude from numerical comparisons until its cashflow and rollover path qualifies. |
| Rolling RBI 91-day T-bills | Historical auction quotes and conditional rollover cohorts | Use those cohorts to test mechanics. Exclude from observed product-return panels. Payment timing stays open and same-day funding stays excluded. |
| Nifty 500 TRI | 129 official monthly returns with mirror endpoint dates | Benchmark diagnostics only. |

The next portfolio calculation can use these exact-date NAV windows for explicitly historical scenarios and use the direct bond and both SBI accrual cases for separate forward cashflow sensitivities. The joint windows support descriptive comparison. They leave long-horizon risk, investor-specific costs and taxes, real purchasing power and implementability open. WP1's coverage and inclusion increment passes. G6.3 remains open and investment authorization remains **NO-GO**. [Evidence ledger](../../../docs/G6_3_UNAVAILABLE_EVIDENCE_LEDGER.md)

## Reproduction

```text
python decision/audit_g6_3_exact_date_coverage.py --check
```

The [machine-readable coverage](coverage_v1.json) records input paths and normalized hashes, both date methods, exact common NAV endpoints for portfolio groups, continuous interval bands, all 15 NAV pairs, benchmark and close diagnostics, and all inclusion decisions. The checker reuses the raw-source inventory audits and verifies the retained silver and R9 controls. The source cutoff is fixed for reproducibility. This increment adds neither market data nor statistical estimates.
