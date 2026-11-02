# 2036 Investment Research | Stage 5.12 Predictive Validation

**Assessment:** 2 November 2026  
**Status:** PARTIAL predictive-testing pass; distributional tail-risk test FAIL; 2036 probability calibration NOT ESTABLISHED; investment NO-GO.

## 1. Mandate and non-negotiable decision rules

Initial ₹42 lakh; 120 end-month stepped-up SIPs starting at ₹25,000, with 10% increase every twelve instalments; total contributions ₹89.8123 lakh through October 2036. The target year is 2036, not a mandatory October exit. Real after-tax ₹90 lakh floor and desired ₹100 lakh, in 2026 purchasing power, remain the objectives. A modeled >=85% floor-achievement probability is a *statistical criterion*, not a contractual guarantee; neither has been demonstrated.

## 2. What was actually validated

The exercise independently fetched six pinned, third-party historical series using a read-only GitHub connector and computed **219 synchronized monthly returns, July 2006–September 2024**. The previous 2007–2024 risk panel contains 213 observations. Files are pinned by Git blob SHA; their historical coverage, derivation and source limitations are recorded in `stage512_independent_calibration.py` and the 2-Nov independent calibration report.

- **Equity:** historical Nifty 500 TRI copy, not officially downloaded NSE file. Cross-check NSE index methodology and historical TRI export before GO.
- **Fixed income:** India 10-year yield changes transformed by a hypothetical carry–duration–convexity equation. Neither an actual total-return series nor a directly held G-Sec.
- **Gold and silver:** USD metal prices multiplied by the within-month last USD/INR observation. Not RBI Mumbai bullion spot or Indian ETF NAV.
- **CPI:** compiled price-level index up to March 2025; the joint synchronized panel ends September 2024. The official MoSPI 2024=100 linked historical back series has NOT been independently reconciled.
- **Research portfolio:** hypothetical 65% equity / 20% bond proxy / 10% gold / 5% silver; rebalanced monthly for the simple out-of-sample return proxy. Not the actual no-rebalance monthly-SIP allocation used in the terminal historical replay.

The fixed-income and metals components are **still proxy inputs**, so the following results are historical-model diagnostics rather than investable product backtests.

## 3. Out-of-sample test design

For every forecast origin in 2016–2024, use **only the prior 60 months** to estimate sample mean and sample standard deviation of monthly log returns. Forecast h-month cumulative log return with mean `h * trailing_mean` and volatility `sqrt(h) * trailing_monthly_sd`. Score each observed return against two-sided 80%, 90% and 95% Gaussian predictive intervals. This is an intentionally simple baseline, not the fully tax-aware Stage 5.12 wealth model.

| Series | Horizon | Forecasts | Nominal target coverage | Observed coverage | Worst standardized forecast error |
|---|---:|---:|---:|---:|---:|
| Equity TRI | 1 month | 105 | 90% | 92.38% | -6.94 (Mar 2020) |
| Portfolio nominal proxy | 1 month | 105 | 90% | 94.29% | -6.86 (Mar 2020) |
| Real portfolio proxy | 1 month | 105 | 90% | 93.33% | -6.81 (Mar 2020) |
| Real portfolio proxy | 12 months | 94 | 90% | 89.36% | -2.76 (origin Apr 2019) |
| CPI log-change | 12 months | 94 | 90% | 88.30% | -2.63 (origin June 2016) |

**Decision:** An approximately correct overall 90% interval frequency does not validate the tail shape. A ~6.8-standard-deviation crash under the fitted Gaussian model is extraordinary, and reveals a severe downside-model miss. Twelve-month forecasts share 11 of 12 future months, so they **must not** be evaluated with independent-trial binomial confidence intervals. Three-year forecasts are more heavily overlapping still. Structural changes, clustering of crises, uncertainty in means, monthly CPI measurement and data revisions remain unresolved.

## 4. Ten-year historical objective replays

A separate analysis reused each 120-month historical sequence to replay ₹42 lakh initial and ₹25,000 stepped-up SIPs with fixed contribution allocation weights and no interim rebalancing. At each historical terminal date, apply a counterfactual **simplified 2026 tax formula**, fixed transaction-friction assumptions, and the actual historical CPI-proxy ratio from that sequence. Fund expense drag and differences between proxies and investable NAVs are not accounted for. **This is not a replay of the tax law actually applicable during the historical period.**

There are exactly 100 rolling 120-month windows beginning July 2006–October 2014, with last endings through September 2024. Every adjacent window overlaps by 119 of 120 monthly observations. Across the full available 219-month dataset there is only **one complete, mutually disjoint 120-month sequence**.

| Descriptive statistic | Real after-tax (illustrative ₹ lakh) |
|---|---:|
| Lowest rolling window | 69.15 |
| 5th percentile of overlapping windows | 74.54 |
| 15th percentile of overlapping windows | 79.62 |
| Median | 95.99 |
| 85th percentile | 120.65 |
| 95th percentile | 133.08 |
| Highest rolling window | 140.52 |
| Windows reaching ₹90 lakh | 53 / 100 |
| Windows reaching ₹100 lakh | 46 / 100 |

Example start–end windows (approx. real after-tax ₹ lakh): 2007–2016 ₹73.55L; 2008–2017 ₹73.92L; 2009–2018 ₹100.75L; 2010–2019 ₹83.28L; 2011–2020 ₹92.15L; 2012–2021 ₹121.62L; 2013–2022 ₹110.47L; 2014–2023 ₹131.32L; October 2014–September 2024 ₹140.52L.

**Critical interpretation:** 53 successes out of 100 near-identical rolling windows are NOT a 53% estimated probability of success in 2036. Such an estimate would have grossly exaggerated statistical confidence. The historical-replay 15th percentile of ₹79.62L is a descriptive fact about sampled overlapping paths, not a prospective risk-model quantile.

## 5. Updated model acceptance criteria

| Test | Evidence | Gate |
|---|---|---|
| Reproduced 2007–24 historical covariance | 213 monthly proxy observations | PROVISIONAL |
| No-lookahead rolling historical intervals | 105 monthly one-step tests | PARTIAL PASS |
| Correct tail-risk distributions | Mar 2020 ~6.8σ downside miss | FAIL |
| Independent validation of decade outcome | Only one nonoverlapping 120-month window in joint sample | INSUFFICIENT |
| Official 2024-base linked MoSPI CPI | Official linkage described, raw input not reconciled | OPEN |
| Official NSE G-Sec **total-return** benchmark and product NAV | NSE/AMFI confirm source availability; not retrieved into common panel | OPEN |
| RBI Mumbai gold and silver vs INR ETF NAV | RBI-sourced series documented; not incorporated | OPEN |
| Model-specific 2026–2036 85% target probability | No independently calibrated 10-year forward distribution | NOT ESTABLISHED |
| Actual contractual CPI-indexed real floor | No qualifying instrument / funding identified | NO-GO |

### Three-level qualification

1. **Technical replay**: arithmetic and no-lookahead sample splitting passed basic checks; intended tail distribution did not.
2. **Predictive model**: only partially validated for near-term historical intervals; not a calibrated future wealth probability.
3. **Investment authorization**: **NO-GO**. Do not optimize weights based on inadequately validated 2036 success probabilities.

## 6. Required work before predictive validation can pass

A. Reconstruct primary source panel using official NSE Nifty 500 TRI and actual NSE 10-year G-Sec **total-return** index, MoSPI CPI 2024=100 linked back series, RBI domestic Mumbai bullion prices and contemporaneous tax law / investable ETF NAV histories. AMFI offers NAV history (maximum 90-day download windows); benchmark series are not equivalent to ETF NAVs.

B. Run time-blocked, walk-forward checks with crisis and regime stratification, not randomly split months. For 10-year results disclose the *effective* number of independent observations; never treat 100 rolling windows as 100 independent trials.

C. Replace a sole Gaussian with explicit alternative predictive distributions (e.g. Student-t/mixtures), dependence regimes, parameter posterior or ambiguity sets; evaluate calibration with interval coverage, proper scoring rules, expected shortfall and tail-event diagnostics. Do not fit shock frequency based on one crash.

D. Reconcile end dates, yield/coupon taxation, SIP tax lots, execution spreads, fund charges and direct-bond cash flows. Compare 120 months (October 2036) with all January–December 2036 conditional decision dates.

E. Require the investment committee to decide whether the ₹90L floor is truly **contractual / hard** or a desired **probabilistic** planning floor. A 85% success test does not constitute a real guarantee; no amount of simulation can turn the two into equivalents.

## Source links (primary descriptions and source-proxy audit)

- NSE Total Return methodology: https://www.nseindia.com/static/products-services/indices-total-returns-index
- NSE Nifty 500 historical data: https://www.niftyindices.com/reports/historical-data
- NSE 10Y Benchmark G-Sec fixed-income methodology (true index differs from synthetic bond proxy): https://www.niftyindices.com/Methodology/Method_NIFTY_Fixed_Income_Indices.pdf
- AMFI NAV history / 90-day limitation: https://www.amfiindia.com/net-asset-value/nav-download
- MoSPI CPI 2024 base, linking factor and back-series: https://www.pib.gov.in/PressReleasePage.aspx?PRID=2227012&lang=1&reg=3 and https://www.pib.gov.in/PressReleasePage.aspx?PRID=2291051&lang=1&reg=1
- RBI Mumbai gold and silver original data made available via RBI DBIE: https://dbie.rbihub.in/tables?table=real_sector.r17_monthly_average_price_of_gold_and_silver_in_mumbai
- Third-party-source names, file blob SHAs and derivation: `stage512_independent_calibration.py` (included)

**Reproduction:** `python stage512_predictive_validation.py --fetch --out-dir .` requires internet access to download pinned files and verifies their Git blob SHAs before calculating results. Local `--self-test` confirms basic arithmetic, but complete historical reproduction requires data downloads. The figures in this report were calculated from the cited pinned source datasets in the connected GitHub read session on 2 November 2026.