# Stage 5.12 — R8 Data-bridge and Official Benchmark Qualification Gate

**As of:** 2 November 2026. **Investment authorization: NO-GO.**

## Completed independently checked asset observations
- Direct official AMFI four-fund NAV histories: 3,046 dated NAV records, 63 earlier AMFI snapshot checks; 12 source segments with SHA256.
- Original 37 calendar-month-based returns contained an **initial September 2023 date mismatch**: gilt NAV 30 Sep versus 29 Sep for equity/gold/silver. The first (October 2023) return was quarantined.
- Re-run and CI-verified **36 strictly date-aligned returns** from Nov 2023–Oct 2026. R7 full-sample annualized fixed-weight vol **11.413711%** and independent checker status `PASS_OFFICIAL_SOURCE_STRICT_DATE_ALIGNED_36M_R7_RESEARCH_ONLY`.
- Recent (Oct 2025–Oct 2026, 13 observations) monthly-rebalanced 65/20/10/5 portfolio volatility **14.46%**, gold/silver correlation **0.838**. This is a short-period observation and not a forecast.

## New independently evidenced source blocker: NSE gross total-return history

- Publisher's official index source: https://www.niftyindices.com/reports/historical-data
- Selected index: `NIFTY 500`, **Total Return Index** (dividend-reinvested), *not* price-only index.
- Controlled source probe: `research/stage512/pipelines/nse_tri_source_probe_R8.py`, manifest `research/stage512/data/nse_tri_source_probe_R8.json`.
- On 2026-11-02, two requests for crisis (Feb–Apr 2020) and recent (Aug–Oct 2026) periods returned HTTP 200 but `text/html` rather than structured TRI observations.
- The diagnostic retry captured final endpoint redirection to `https://www.niftyindices.com/?ReturnUrl=...` after an ordinary historical-data-page session warm-up. The host did **not** provide qualified TRI rows in this environment.
- **Classification: SOURCE ACCESS NOT QUALIFIED**, not "index values verified", and not proof that the official data is nonexistent. Do not silently replace with a price index or third-party series.
- The official NSE page states its fixed-income series are total-return series **except Nifty 10 yr Benchmark G-Sec (Clean Price)**. The clean-price index is unsuitable as a total-return government-bond proxy without coupon treatment.

## Two-layer 2036 model contract (R8)

| Sleeve | Long historical macro/market benchmark (not scheme NAV) | Recent investable-product evidence |
|---|---|---|
| Indian broad equity | Official Nifty 500 **gross TRI** history from NSE | Motilal Oswal Nifty 500 Index Fund NAV, official AMFI |
| Government security interest-rate risk | Official government-security **total-return** index matched by duration; no clean-price substitution | HDFC Gilt Fund NAV; duration/cash-flow model also required for direct GS2036 |
| Gold | RBI Mumbai monthly-average INR gold bullion history | UTI Gold ETF NAV, scheme/market tracking differences |
| Silver | RBI Mumbai monthly-average INR silver bullion history | HDFC Silver ETF NAV; inception-limited |
| Inflation | Official MoSPI linked CPI series, explicit rebasing/source revisions | Not applicable |

RBI DBIE published monthly-average Mumbai bullion reference (not daily tradeable ETF total return): https://dbie.rbihub.in/tables?table=real_sector.r17_monthly_average_price_of_gold_and_silver_in_mumbai.
Prices in rupees per 10g gold and per kg silver; calendars/monthly-average observations are **not same timestamp** as month-end ETF NAVs, and must not be naively paired to estimate daily or month-end tracking error.

## Required reconciliation controls
1. Record source URLs, original download time, raw body checksums, index names, index type (price/TRI/NTR), dates and exact units.
2. Confirm monthly continuity, matching date conventions, issue rebasing, zero/duplicate/non-trading-date handling, and official-versus-mirror checks at sampled dates.
3. For instruments postdating the benchmark history, never label pre-inception benchmark returns as realized fund returns.
4. Evaluate fund tracking differential only in a properly overlapping **like-for-like** total-return and NAV window. Do not subtract TER twice from NAV series, which already reflect ongoing fund expenses.
5. For ETF purchases, separate the fund's **NAV** from exchange market price, bid–ask spread, premiums/discounts, brokerage, taxes and market impact.
6. Use multiple risk regimes (long-window, crisis, recent 36-month, recent 13-month), calibrated as **conditional alternatives**, not an unearned probability distribution over regimes.
7. Independent stress, bootstrap and parameter uncertainty must be reassessed before giving a decision-grade 2036 floor likelihood.

## Decision & remediation route

- **AMFI official sampled four-fund history:** QUALIFIED for its observed window (R7 source CI PASS).
- **Official 36-month covariance:** CALCULATION PASS, not forward-model approval.
- **NSE official Nifty 500 TRI programmatic acquisition:** BLOCKED by returned HTML redirect; requires other officially supplied historical CSV/export or independently verifiable exchange source.
- **Official market benchmark full source panel:** OPEN.
- **RBI bullion monthly official bulk panel:** OPEN for machine-readable independent import and calendar harmonization.
- **2036 85% real-floor probability:** NOT independently established.
- **Investment authorization:** **NO-GO**.

Do not claim that extra simulations resolve missing or unreliable primary-source returns. Continue source ingestion or explicitly quantify model uncertainty with provisional labels.
