# Candidate history blocker investigation and resolution — 2026-11-05

## Executive disposition

The source-acquisition and lineage blocker is **partially resolved** for five decision-relevant product hypotheses. Five official AMFI Growth-option NAV histories now pass independent raw-to-normalized reconstruction. This is a source-history pass, not qualification of investable return paths, ETF execution prices, bond total-return benchmarks, covariance, probabilities, suitability, or an investment decision.

- G5 candidate breadth: **10 product hypotheses**, screen breadth only.
- Bounded AMFI NAV sample reconciliation: **44/44 exact**.
- Latest AMFI TER evidence: **10/10 scheme rows; 20/20 component sums**.
- Continuous product NAV histories independently reconstructed: **5 products, 63 raw source responses and 7,353 NAV observations**.
- Calendar-month overlap with published NSE Nifty 500 TRI: **72 Motilal Nifty 500 fund, 128 HDFC Gold, 44 ICICI Silver, 11 SBI Nifty 500 fund, and 35 target-maturity gilt fund months**. These are descriptive, mixed-asset overlaps; TRI values are published to two decimal places.
- G6 synthetic fixture-first engineering: **READY**.
- Decision-grade G6: **NOT READY**.
- Investment authorization: **NO-GO**.

The source response count is five acquisition histories with 63 accepted raw windows (15 + 24 + 10 + 5 + 9).

## Blocker decomposition and resolution

| Small blocker | Root cause | Action and evidence | Status / remaining condition |
|---|---|---|---|
| Candidate breadth | Prior register had fewer than 10 investable-product hypotheses after benchmark/cash/direct-security exclusions. | G5.4 adds five hypotheses; append-only register now contains 10 after exclusions. | **Closed for breadth only.** Candidate screening is not recommendation or suitability. |
| AMFI TER proof | Previous independent audit could not reparse original source bytes. | Retained official AMFI workbook and factsheets; exact NSDL scheme-code matching; 10/10 rows and 20/20 Decimal component sums. | **Closed for current snapshot.** Trading, custody, tax and investor-specific costs remain open. |
| Bounded NAV sample proof | Prior snapshots and new snapshots differed; validation did not verify all rows. | Reacquired official AMFI responses; 44/44 exact scheme/date/Decimal-NAV matches; keep changed raw hashes as separate snapshots. | **Closed for these samples only.** |
| Continuous candidate NAV history | Full histories had not been retained or independently reconstructed. | Five bounded, sequential acquisitions; each raw response has URL, SHA-256, byte length, dates and exact identity; audit reconstructs the normalized daily CSV from raw JSON. | **Partially closed.** Five histories pass; remaining candidates require an evidence-based shortlist before more acquisition. |
| AMFI product-name alias and response preservation | SBI target-maturity fund’s official nav name begins `SBI |CRISIL...`; initial parser expected `SBI CRISIL...`. The fetcher wrote raw bytes only after validation, so the rejected HTTP 200 response was not retained. | Matched alias to already-retained AMFI records for scheme 150681/ISIN INF200KA12Q9; changed parser to accept the stable scheme/ISIN and Growth/Direct identity tokens; changed fetcher to write raw response before parsing; reran nine windows. | **Resolved in current run.** The first unretained response is excluded from evidence; current 9/9 raw windows are retained and independently audited. CI must enforce early raw retention. |
| Strict monthly date alignment | Daily histories alone do not produce comparable monthly observations or reveal short fund windows. | For each product, take last available NAV in each month, calculate return only when prior-month NAV exists, and join on same calendar month to the 129 published NSE TRI monthly returns. No forward fill or pre-inception splice. | **Pass for descriptive joins only:** HDFC Gold 128 months (2015-02–2025-09); ICICI Silver 44 (2022-02–2025-09); SBI Nifty 500 fund 11 (2024-11–2025-09); SBI June 2036 gilt fund 34 (2022-12–2025-09). Not enough to claim stable dependence or forecast. |
| Bond return identity | A G-Sec ETF/fund NAV is not an index total-return series or a held-to-maturity sovereign cashflow. | Added SBI June 2036 target-maturity NAV as an actual product hypothesis and retain LIC G-Sec ETF separately as a duration-managed proxy. | **Open.** Qualify a sovereign total-return reference or model dated GoI security cashflows as a separate instrument; obtain ETF market prices/premiums for execution analysis. Never substitute NAV for traded price. |
| G6 deterministic path | Tax ledger, cashflow schedule and G3 hurdle logic pass separately; no candidate-to-ledger adapter reconciles them end-to-end. | G6 may start with synthetic fixtures. Use explicit product input schema, one lot, one tax year, dated cashflows, fees/taxes/exit and CPI labels. | **Open implementation gate**, not a reason to postpone bounded G6 engineering. |
| CPI basis and personal facts | CPI values are mechanically mapped, but original releases/base month and personal inputs are absent. | Keep CPI provisional and investor variables unconfirmed; no defaults. | **Open for personal real-wealth result.** Not needed for fixture-only bridge. |
| Probabilistic confidence | No qualified multi-asset history or adverse regime / parameter / sequence validation. | Defer probability until source universe and deterministic path pass; pre-register methods and falsification checks. | **Open; no probability claim.** |

## Independently verified histories

| Product | Scheme / ISIN | Window | NAV rows | Request windows | Maximum observed calendar gap | Monthly overlap to NSE TRI |
|---|---|---:|---:|---:|---:|---:|
| HDFC Gold ETF | AMFI 113049 / INF179KC1981 | 2015-01-01–2026-10-30 | 2,918 | 24/24 | 5 days | 128 months |
| ICICI Prudential Silver ETF | AMFI 149464 / INF109KC1Y56 | 2022-01-25–2026-10-30 | 1,160 | 10/10 | 5 days | 44 months |
| SBI Nifty 500 Index Fund Direct Growth | AMFI 152908 / INF200KB1381 | 2024-10-04–2026-10-31 | 520 | 5/5 | 4 days | 11 months |
| SBI CRISIL IBX Gilt Index–June 2036 Fund Direct Growth | AMFI 150681 / INF200KA12Q9 | 2022-10-10–2026-10-31 | 994 | 9/9 | 4 days | 35 months |
| Motilal Oswal Nifty 500 Index Fund Direct Growth | AMFI 147625 / INF247L01957 | 2019-09-11–2026-10-30 | 1,761 | 15/15 | 5 days | 72 months |

Gaps above are calendar-day gaps between published NAV observations, not missing trading-day counts. Growth-option NAV series include fund-level expenses and reinvestment convention, but are not ETF transaction prices. The 2036 gilt fund is not a principal guarantee or direct bond holding.

## Reproduction and acceptance

From repository root:

```powershell
python research/stage512/2026-11-05/g5_4/audit_g5_candidate_nav_history.py
python research/stage512/2026-11-05/g5_4/audit_g5_4.py
```

The independent audit checks raw-byte SHA-256 and length, sequential non-overlapping request windows, scheme/ISIN/name/plan/option, within-window date bounds, positive Decimal NAV, duplicates/conflicting dates, source-to-normalized CSV equality, maximum calendar gaps, exploratory SBI overlap equality, and strict common calendar-month joins. CI is wired to rerun this audit.

## Next exact work

1. The ten product hypotheses now have a documented screen disposition in `g5_candidate_disposition_v1.json`; the independent G5 exit audit passes all eight criteria with explicit remaining fee/tax/liquidity/settlement/access gaps.
2. Use the initial evidence set in `G5_CANDIDATE_DISPOSITION.md`; keep the direct GoI and T-Bill rows blocked from numeric output until actual date-linked price/cashflow inputs are qualified.
3. Qualify a comparable sovereign return/cashflow representation; acquire ETF market prices only where actual ETF execution is in scope.
4. Proceed with the fixture-first G6 deterministic bridge. Do not call it decision-grade until one chosen strategy path, tax lots, fees, exit cashflows and CPI reconcile end to end and adverse/mutation cases pass.
5. G5 acceptance evidence is complete for review, including explicit blocked outcomes. Reassess decision-grade G6 separately. Maintain investment NO-GO throughout.
