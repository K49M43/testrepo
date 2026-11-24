# RBI 91-day T-bill source extension and rollover assumptions

**As of:** 2026-11-24  
**Scope:** Source qualification and conditional gross cashflow mechanics only. This is not a personal return history, a 2036 forecast, or investment authorization.

> **Correction:** The initial v1 rollover schedule below is retained for audit history only. Its successor selector used the next issue/settlement date and could treat an auction held before maturity as fundable from maturity proceeds. The v2 increment at the end of this report uses the bid/auction date and requires it to be strictly after maturity. Use the v2 audit and CSVs for current mechanics; v1 return figures are superseded.

## Result

The official RBI 91-day auction source panel is extended and reconciled across two windows:

| Window | Auction dates | Matched notices | Matched full results | Positive 91-day issue-price observations | Zero-issue exception |
|---|---:|---:|---:|---:|---|
| Table 217, 2024-07-03–2025-07-30 | 55/55 | 55/55 | 55/55 | 54 | 2025-02-20 |
| Table 218, 2025-07-02–2026-06-24 | 50/50 | 50/50 | 50/50 | 49 | 2026-03-25 |
| Combined, deduplicated | 100 unique | — | — | 98 | Both dates above |

The five shared auction dates (2025-07-02 through 2025-07-30) agree on issue date, notified amount, 91-day total issue, cutoff price/yield, result status, and 91-day weighted-average price/yield. There are no cross-window field mismatches.

For the 98 positive-issue observations, the conditional gross price-to-par holding return is `100 / weighted-average-price - 1` per ₹100 face. It ranges from **1.2943% to 1.6880%**, with a two-year sample mean of **1.4584% per bill**. This assumes a full retail non-competitive allotment at the published weighted-average price and redemption at par. It excludes tax, transaction costs, partial allocation, and any investor-specific settlement effects. The values describe 98 individual bill cashflows under those conditions; they do not form a continuous roll series or support a long-run forecast.

## Parser issue found and corrected

The 2025-02-20 Table 217 row reports zero issue for the 91-day tenor. The corresponding RBI full-result page contains dashes for both 91-day and 182-day results, but a valid result for the 364-day tenor. The old parser shifted the first non-empty tenor value into the 91-day field and falsely treated the 364-day result as a conflict. The corrected capture parser and independent auditor preserve tenor columns from the source table rows. They now verify that the 91-day fields are absent for a zero 91-day issue while retaining the other-tenor result. The Table 218 window was rerun through the independent audit after this change and still passes.

## What RBI sources establish about a rollover

The RBI Government Securities Market in India primer states that Treasury Bills are zero-coupon securities issued at a discount and redeemed at face value. It describes 91-day, 182-day, and 364-day tenors; T-bill auction settlement is T+1 (the next working day). It also says that when maturity falls on a Sunday or holiday, redemption proceeds are paid on the previous working day. The RBI non-competitive bidding FAQ states that retail investors may bid in eligible auctions through the prescribed route, receive the weighted-average competitive price, can be partially allotted, and face a minimum bid amount. These are scheme terms in the published FAQ, not verification of this investor's current account route, actual allotment, current service charges, or settlement.

Sources: [RBI Government Securities Market in India – A Primer, sections 1.3, 3.3, 4.3 and 16.1](https://www.rbi.org.in/commonperson/English/Scripts/FAQs.aspx?Id=711); [RBI publication on Saturday market closures](https://www.rbi.org.in/Scripts/PublicationsView.aspx?id=16436); [official RBI Mumbai holiday matrix](https://www.rbi.org.in/scripts/HolidayMatrixDisplay.aspx?regoff=Mumbai); [official RBI Table 217](https://www.rbi.org.in/scripts/PublicationsView.aspx?id=23391); [official RBI Table 218](https://www.rbi.org.in/Scripts/PublicationsView.aspx?id=24043).

The date diagnostic applies the RBI previous-working-day rule using the official Mumbai holiday matrix and the RBI rule that government-securities markets are closed on Saturdays. For each matched 91-day issue, it sets a nominal maturity of `issue_date + 91 calendar days`, then moves that date backward across weekends and listed Mumbai holidays. Nine nominal maturities move backward by one day. Of 86 transitions with a successor in the captured windows, 57 have a positive issue on the adjusted maturity date and 29 have the next positive issue 1–13 days later. Twelve observations remain right-censored at the end of the available history. This is a dated mechanics audit, not proof that a specific investor can receive maturity proceeds and settle the next purchase on the same day.

To quantify the remaining rollover mechanics without presenting them as an investor result, the audit also runs a deterministic gross scenario for an initial ₹10,000 cash balance. Using the ₹10,000 face-value lot described in the RBI NCB FAQ, it buys the largest whole number of lots at each observed weighted-average price, assumes full non-competitive allotment, holds each bill to the adjusted maturity date, earns 0% on idle cash, and continues until the first redemption on or after the 365-day target. The FAQ was updated in 2017; this lot rule is a model input until the current investor route is confirmed. Of the overlapping start cohorts, 56 complete within the source window and 42 are right-censored. Across the 56 complete paths, annualized gross returns range from **5.0820% to 6.3171%**, with median **5.6403%**. Cohorts overlap and represent a single two-year rate environment; this range is not an independent sample, long-run distribution, forecast, or probability. It excludes taxes, fees, actual partial allotment, investor access, and current settlement timing.

The audit marks source overlap, gross bill cashflow arithmetic, and the official date-calendar inputs **PASS**. Continuous investor rollover qualification remains **NOT PASSED**. Before a roll return can be used as an investor outcome, the model still needs:

1. Investor-specific confirmation of the applicable current participation route, bid limits, actual full/partial allocation, and whether maturity cash and the next auction settlement can be used on the same date.
2. Current fees and tax treatment, plus a supported return assumption for cash held between redemption and the next eligible issue.
3. Extend the deterministic event-level roll ledger to the actual funding schedule and evaluate zero-issue dates, delayed issues, partial allotments, end-of-window censoring, and 2036 exit timing. Keep its outputs conditional and gross until investor inputs are supported.

No equity–bond correlation, full covariance, long-run sovereign risk estimate, floor-success probability, or investment recommendation is derived from this short T-bill panel. G6.3 remains open; decision readiness remains **NOT READY** and investment authorization remains **NO-GO**.

## Reproduction

```powershell
python decision/audit_g6_3_rbi_tbill_window.py research/stage512/2026-11-19/g6_3/rbi_tbill_window_2024_2025 --table-path research/stage512/2026-11-24/g6_3/source_raw/table217_20261124.html --table-name 'Table 217' --window-tag 2024_2025 --expected-auctions 55 --first-date 2024-07-03 --last-date 2025-07-30
python decision/audit_g6_3_rbi_tbill_window.py research/stage512/2026-11-06/g6_3/rbi_tbill_window_2025_2026 --table-path research/stage512/2026-11-06/g6_3/source_raw/rbi_tbill_sample/table218_20260731.html --table-name 'Table 218' --window-tag 2025_2026 --expected-auctions 50 --first-date 2025-07-02 --last-date 2026-06-24
python decision/audit_g6_3_rbi_tbill_rollover.py
python decision/audit_g6_3_source_inventory.py --check
```

The initial v1 outputs are retained in this directory as historical audit artifacts and are superseded for roll timing by v2. The 24 monthly Mumbai maturity-holiday pages and manifest are retained under `rbi_mumbai_holidays_2024_2026/`. The additional settlement-calendar months and current RBI retail rules used in v2 are detailed below. Each auction window has its own per-file source manifest and hashes.

## Retail Direct rules and bid-date correction — v2, 2026-11-24

The current RBI Retail Direct FAQ and the RBI non-competitive bidding scheme circular were captured as official raw HTML with response metadata and SHA-256 hashes in `source_raw/rbi_retail_direct_rules_manifest_v1.json`. The independently checked public terms establish that eligible individuals can bid in primary T-bill auctions through Retail Direct's non-competitive segment; bids are single per security/auction; allotment uses the auction weighted-average price; partial allocation is pro-rata; and bids must be funded on the date submitted to RBI or are cancelled. The circular sets a ₹10,000 face-value minimum and multiples and caps retail NCB allocation collectively at up to 5% of the notified issue amount (subject to RBI changes). RBI's FAQ says settlement is typically one working day after auction, no RBI account-maintenance or primary-bid fee is charged, payment-gateway charges are borne by the investor, and excess bid markup is refunded within two business days. The FAQ presents minimum investment amounts as of 12-Nov-2021; the current portal rule must be checked before an actual bid. These sources do not prove this investor has an RDG account, route access, or any allocation.

The earlier v1 schedule had a timing error: it selected the next positive **issue/settlement date** on or after maturity, without checking whether the associated auction and funding date had already passed. In 71 of 86 previously completed transitions, that selected auction occurred on or before the adjusted maturity date. Since redemption proceeds cannot be assumed to fund a bid that must already have been funded/submitted, v2 selects the first positive auction date **strictly after** adjusted maturity. Same-day funding is excluded because intraday timing of maturity proceeds versus the bid-funding cutoff is not established.

Settlement dates for all 98 positive observations were checked against the official Mumbai holiday matrix. The three additional July–September 2024 monthly captures cover the first auctions; all 98 observed issue dates reconcile to the next working day after auction (89 one-calendar-day lags and 9 two-calendar-day lags due to intervening non-working days). Of 86 uncensored maturity-to-bid transitions, time until the next eligible auction is 5–21 calendar days (median 6); 12 remain right-censored.

The recalculated 365-day-target scenario has 59 complete overlapping cohorts and 39 censored cohorts. Conditional annualized gross values are 4.8466%–5.9502%, median 5.3678%, assuming full allotment and zero return on cash gaps. These values are not investor returns, forecasts or probabilities. The model uses the observed final weighted-average price for lot affordability but RBI requires upfront markup funding; the markup amount is not specified in the captured FAQ. Partial allotments, payment-gateway charges, markup cash lock/refund, investor-specific access and bank cash yield are also not modeled, so bid affordability and executable rollover remain **NOT QUALIFIED**.

Current outputs: `rbi_tbill_retail_route_qualification_v1.json`, `rbi_tbill_rollover_assumption_audit_v2.json`, `rbi_tbill_merged_roll_schedule_v2.csv`, and `rbi_tbill_conditional_365d_roll_scenarios_v2.csv`. The expanded settlement calendar is in `rbi_mumbai_holidays_2024_07_2024_09/`; raw RBI Retail Direct FAQ and circular captures are in `source_raw/`. G6.3 remains open and investment authorization remains **NO-GO**.
