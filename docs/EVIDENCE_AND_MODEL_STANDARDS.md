# Evidence, Data Pipeline, Finance Model & Independent Audit Standards

This code supports **actual personal investment**, so traceability, timely instrument identity, source quality and model honesty are mandatory. Favor a concise and executable decision-support engine over an elaborate platform.

## Source contract
For each series keep:
\`source_owner\`, \`source_url\`, \`source_publisher\`, \`retrieved_utc\`, \`released_at/as_of\`, \`series_id\`, \`security_id/ISIN\`, \`currency\`, \`unit\`, \`price_type\`, \`return_type\`, \`raw_sha256\`, \`schema_version\`, \`date_basis\`, \`coverage\`, \`adjustment\`, \`known_missing\`, \`qualification_scope\`.

Keep original raw observations **unchanged**, cleaned normalized observations separately, adjustment logs and executable tests. Never treat a blob hash or HTTP 200 alone as data qualification.

Qualification levels: (A) verified official data, (B) official-published partial return/price anchors with independent reconciliation, (C) independently sampled/verified secondary mirror, (D) synthetic/market proxy, (E) invalid/rejected. Only (A) or explicitly justified (B) data qualify a claim within their recorded coverage; a (C) mirror may support sensitivity cases but cannot silently become (A).

## Asset-specific rules
1. **Equity:** Nifty 500 TR/TRI (with reinvested distributions), official NSE 129-month 2015–2025Q3 table; ETF/index-fund net NAV comparisons use overlapping identical dates and account for tracking.
2. **G-Sec:** distinguish full total-return index (coupon + price + rebalancing), synthetic constant-duration price sensitivity, actual ETF NAV, real ETF market execution and a direct fixed-maturity sovereign's contractual coupons/principal. 2036 maturity cashflow modeling must account for coupon timing, taxes, purchase price, redemption, reinvestment and maturity risk.
3. **Gold and silver:** RBI Mumbai averages in INR are publication-series physical bullion averages, not month-end tradable spot or mutual fund/ETF NAV. Correct price units INR/10g gold and INR/kg silver, expense and liquidity. Silver is a required candidate; not automatically required at positive portfolio weight.
4. **CPI:** reconstruct MoSPI's documented link across 2012/2024 bases with official 2025–2026 releases, publication vintages, rounding and revisions. Avoid linking a mismatched third-party CPI compilation.
5. **Fund NAV:** includes ongoing TER. ETF NAV vs exchange execution price: verify premium/discount, bid–ask spread, impact cost and volume. Understand scheme plan/option, payouts vs growth, dividend adjustments and corporate actions.

## Time-series controls
- Identify trading-day vs calendar month and last actual priced NAV day. To estimate *joint* correlation, both the start and end dates of each compared monthly interval must match, or the mismatch must be explicitly quarantined / methodologically corrected.
- Match **frequency, currency, units, index bases, and total-return conventions** before merging. CPI and RBI averages have different measurement dates; do not pretend they are same-time close prices.
- Prohibit look-ahead, ffill across unexplained missing months, accidental survivorship/selection bias, and division by nominal series with inconsistent date windows.
- Don't confuse overlapping ten-year historical walks with independent return trials; use effective sample-size cautions.

## Financial computation
Define a dated monthly ledger for the ₹42L initial deployment and ₹25k/month SIP increasing 10% after every 12 contributions, initially modeled for 120 contributions. Preserve amounts, dates, roundings and taxes actually paid (whether inside/outside portfolio).
- Calculate transaction-level tax lots, instrument-acquisition-specific Indian LTCG/STCG/debt fund/ETF rules, direct sovereign coupons, taxable dividends, withholding/advance tax, account expenses, capital gains realization timing, tax paid/reinvested cashflows. Tax tables must be refreshed for the relevant fiscal year and not hard-coded globally.
- Model both real and nominal after-tax terminal wealth, alternate exit schedules in 2036, money-weighted XIRR and portfolio IRR with correct sign/time convention.
- Reinvest coupons/distributions after applicable taxes; test whether a modeled instrument can actually do so at reasonable denomination.
- Use 6% as one scenario, plus realistic linked-CPI statistical and stressed cases. Express real 2026 purchasing-power value using one explicitly grounded inflation factor.
- Compare required real-floor goal, not merely ₹90L **nominal** terminal account value.

## Statistical modeling
- Maintain a transparent baseline deterministic valuation, conservative market-parameter assumptions, empirical volatility/covariance, serial/volatility clustering, cross-asset dependencies, stress events and fat-tailed alternatives. Historical means alone are not prospective expected returns.
- Use walk-forward/out-of-sample calibration, sensitivity to regime shifts, modeling uncertainty, inflation shocks, stock-bond correlation shifts, gold/silver concentration, adverse liquidation timing, rising/rate-cut duration shocks, tracking/microstructure loss, adverse tax changes.
- Distinguish **observed historic frequency**, **model-based subjective probability**, **parameter/model uncertainty interval**, **possible extreme loss** and a **legal capital guarantee**.
- Monte Carlo: fixed documented seeds, path count, convergence tests, independent rerun code. Benchmark against analytical or deterministic controls. Do not select only the tail distribution that improves apparent floor-success probability.
- Do not optimize to an 85% success probability by silently raising return assumptions, shrinking tail risk, assuming perfect rebalancing, or removing silver/gold/direct securities without documenting the comparative analysis.

## Testing contract
At minimum provide and automate:
- source SHA, schema, types, date continuity, duplicate/missing/zero NAV, negative/fractional index and rebasing assertions;
- earliest/latest and previous/current month close alignment;
- inflation link and source-published YoY inflation spot checks;
- zero-return no-cost exact cashflow wealth;
- SIP step-up after 12 contributions; one initial corpus, no double-counted fees/taxes;
- per-lot capital gains and coupon-tax tests including cross-2024 rule variations as appropriate;
- XIRR root/convergence and known-money-flow examples;
- weight sum and allocation rounding;
- static covariance mathematical symmetry/positive-semidefiniteness; scenario shock correlation checks;
- statistical simulation convergence/replicability, out-of-sample reporting and sensitivity consistency;
- documented source access failures and retries respecting 429.
All test PASS statuses include source/code commit SHA and as-of date. Keep negative-case tests.

## Decision-language rules
For every computed result state whether it is **source fact, historical observation, conditional model output, sensitivity, assumption, or recommended action**. A modeled annual return is not a promised CAGR. A short-run low volatility does not protect an inflation-linked floor. Do not back-calculate an aspirational return and present it as likely.

## Privacy/security
Repository is public at handoff. No investor name, personal identifiers, account balances from broker statements, tax filing documents, bank details, auth tokens, credentials or nonpublic holdings. Use anonymous portfolio parameters from mandate; advise repository privatization before adding detailed sensitive investment records.
