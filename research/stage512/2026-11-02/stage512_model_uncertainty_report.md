# Stage 5.12 — Model and Parameter Uncertainty Audit
**Date:** 2 November 2026  
**Decision:** CONDITIONAL RESEARCH PASS (controlled stress-design and reproducible computational checks); NO-GO for claiming a calibrated probability, satisfying the 85% floor gate, or purchasing a final portfolio.

## Executive decision
The previously evaluated research allocation (65% Indian equity, 20% rolling gilt-fund proxy, 10% gold, 5% silver) does not clear the numerical investment mandate under any of the 13 controlled scenarios in this audit. The 20,000-path baseline reaches the ₹90 lakh real, after-tax floor in **48.13% of simulated December 2036 outcomes**, while the **15th percentile is ₹62.223 lakh**, versus the required ₹90 lakh. The corresponding baseline October 2036 test is 46.96%. The 85% modeled acceptance criterion is unachieved in these scenarios; it is separate from the stricter contractual or sovereign-backed purchasing-power guarantee (none identified).

This is a scenario sensitivity audit, **not an empirical 2036 forecast**. No weights have been assigned to alternate models, no posterior distribution or real-world probabilities have been calibrated, and no portfolio is approved. A hypothetical 48.13% is not a measured chance of the actual future outcome.

## Mandate, units, and alignment
- All amounts in ₹ lakh. ₹42 initial at model inception; ₹0.25 monthly SIP at end of each month beginning November 2026; SIP increases 10% after each 12-month block. No SIP funding interruptions. Total contribution **₹89.8123L at 120 months**, **₹91.109L at 122 months**.
- Reference purchasing-power baseline is the planned 2026 starting month. For actual implementation use the **official October 2026 CPI** and a consistent base/link across 2012 and 2024 CPI rebasing. October 2036 (120 months) and December 2036 (122 months) are independent endpoints; they cannot share one deflator.
- At each endpoint full hypothetical sale: gross nominal wealth -> current-rule simplified taxes and sales friction -> net nominal wealth -> CPI-adjusted net real wealth -> floor/target tests.
- Research allocation is contributions split at fixed 65/20/10/5 weights, then held without rebalancing. The weights of actual holdings therefore drift with relative asset performance.

## Starting assumptions, not forecasts
- Annual nominal **geometric** return hypotheses before annual expense drag: equity 9.328%, gilt-fund proxy 7%, gold INR 7.304%, silver INR 4.5%.
- Annual expense drags applied once to modeled fund NAV: equity 0.2%, gilt 0.2%, gold 0.4%, silver 0.7%. Actual fund TER is already reflected in historical NAV returns and must not be deducted again when switching to actual fund histories.
- Annual log-return volatility estimated from 2007–September 2024 joint proxy panel: equity 22.45%, gilt duration proxy 7.06%, gold INR 16.72%, silver INR 29.85%, CPI monthly log index 2.68% annualized. Five-variable proxy correlation matrix from `stage512_empirical_calibration.json`; alternate 2013–2024 covariance tested.
- CPI annual *center* 6%, monthly Gaussian log-CPI disturbances; baseline assumes independent innovations over time, with return/CPI contemporaneous covariance matching historical proxy panel.
- Current-rule simplified investor tax assumptions: equity long-term 13% (12.5% + 4% cess) above one unused ₹1.25L LTCG threshold, short-term 20.8%, gilt fund overall positive gains at 31.2%, metals 13% long / 31.2% short; no surcharge, loss harvesting, change of tax laws, cash coupon fund distributions, or tax-return integration. Redemption 0.10% assumed friction plus illustrative equity STT. SIP tax lots held not more than 12 months are treated as short-term. Actual product classifications must be independently verified.
- Historical bond is **a carry-duration-convexity proxy**, not a bond index/fund actual NAV or a 2036 cash-matched security. Metals are world USD bullion quotes multiplied by available INR FX, not domestic ETF returns or executable prices.

## Controlled design
All 13 cases reuse the same seed `20261102` and the same generated innovations (`20,000` paths each, `122` months; October and December both tested). Changes are not simultaneously bundled unless explicitly named. The changes are not calibrated risk factors:
1. Gaussian baseline with long-sample covariance.
2. Recent 2013–2024 covariance only.
3. Equity expected geometric CAGR reduced 2 percentage points.
4. Equity expected geometric CAGR reduced 4 percentage points.
5. Equity, gold, and silver returns each reduced 2 percentage points.
6. Gilt fund return reduced 1 percentage point.
7. Inflation drift 7% annually.
8. Inflation drift 8% annually.
9. CPI monthly deviations follow stationary AR(1), phi 0.85, preserving baseline marginal monthly CPI volatility and approximating longer-lived inflation deviations. Phi is a hypothesis, not an empirical estimate.
10. Multivariate Student-t with five degrees of freedom, unit marginal variance, using a common monthly scale to introduce fatter joint return tails; arbitrary degrees of freedom is explicitly stress-only.
11. A forced August 2036 simultaneous shock: equity -35%, bond proxy -4%, gold -5%, silver -25%, superimposed on normal monthly returns for **every path**. It is conditional stress, not a probabilistic event.
12. Equity -2pp combined with inflation 7% and persistence.
13. Stagflation: annual return hypotheses [5%,5.5%,3%,-2%], CPI 8%, and persistence.

## December 2036: scenario sensitivity results
| Variant | Median real ₹L | 15th percentile ₹L | Meet ₹90L % | Expected shortfall at ₹90L ₹L |
|---|---:|---:|---:|---:|
| Baseline | 88.367 | 62.223 | 48.13 | 10.603 |
| Recent covariance | 87.274 | 67.421 | 45.34 | 8.868 |
| Equity -2pp | 80.880 | 57.995 | 38.62 | 13.677 |
| Equity -4pp | 74.352 | 54.198 | 29.38 | 17.113 |
| Risky assets -2pp | 79.129 | 56.666 | 36.54 | 14.626 |
| Gilt -1pp | 87.534 | 61.421 | 47.12 | 11.019 |
| CPI 7% iid | 80.321 | 56.558 | 38.75 | 14.295 |
| CPI 8% iid | 73.073 | 51.454 | 30.02 | 18.348 |
| Persistent CPI phi .85 | 89.831 | 56.911 | 49.82 | 12.313 |
| Student-t df5 | 88.127 | 62.501 | 47.51 | 10.576 |
| Forced Aug2036 shock | 67.210 | 48.719 | 20.74 | 22.041 |
| Equity -2pp + CPI7 persistent | 74.600 | 47.903 | 34.09 | 18.877 |
| Stagflation + CPI8 persistent | 57.306 | 37.054 | 15.74 | 30.361 |

**Interpretation:** CPI persistence can worsen tails without materially reducing medians: the fifth-percentile real wealth drops from 52.065L to 44.442L and the bottom-5% average from 46.744L to 37.995L. Equities -2pp cut modeled floor-success frequency from 48.13% to 38.62%, which establishes substantial assumption sensitivity. A forced late crash drops it to 20.74%, but this is explicitly not a 20.74% forecast of the scenario occurring.

### Statistical versus epistemic uncertainty
- **Monte Carlo sampling noise:** the baseline share above ₹90L is 48.13% with binomial path standard error approximately 0.35 percentage points **conditional on the model**. That precision does **not** validate the model itself.
- **Parameter uncertainty:** 213 monthly observations are not 213 independent forecasts of a ten-year horizon. As an illustration, 22.45% equity annual log volatility over ~17.75 years implies a naive iid standard error of annual log drift ~5.33 percentage points, even before structural changes. This is **not** a rigorous confidence interval for future equity returns.
- **Structural/model uncertainty:** dependence, conditional tail behavior, regime persistence, tax shifts, future inflation, issuer/fund structure and executable prices remain unknown. Assigning precise scenario weights without evidence would produce a false sense of forecast confidence.
- **No probability aggregation:** do not average favorable and adverse scenario success percentages or treat them as frequencies of future regimes.

## Tests and independent-quality controls
1. Contribution sums and initial/monthly timing checked at both endpoints.
2. In a zero-return/zero-inflation test, every SIP is returned at cost, taxes are zero and only modeled transaction friction applies.
3. Holding return paths fixed, higher CPI mechanically reduces real wealth.
4. An additional equity shock strictly reduces terminal wealth in identical paired paths.
5. Percentile monotonicity and positive real terminal wealth validated.
6. Old forward scenario central model comparison: 18,000-path 48.20% floor attainment and 88.427L median versus this independent 20,000-path rerun 48.13% and 88.367L. Difference is consistent with Monte Carlo sampling variability and seeds/path counts.

These are **software integrity and arithmetic tests**; they do not establish empirical backtest accuracy, realistic tax filings, or out-of-sample forecast validity.

## Current gate decisions
| Research requirement | Outcome | Residual |
|---|---|---|
| Controlled model uncertainty exploration | PASS (research only) | Need primary-data and model comparison |
| Controlled parametric sensitivity | PASS (research only) | Need forward parameter distributions backed by evidence |
| Reproducible arithmetic/simulation | PASS basic invariants | Independent code review and longer-tail diagnostics still necessary |
| Model-calibrated success probability | NO-GO | No empirical scenario probabilities, time-series validation, or investable-data confirmation |
| 85% modeled floor success under central assumptions | FAIL | Model ~48%, p15 ~₹62L |
| Strict contractual CPI-linked ₹90L guarantee | NO-GO | No qualifying hedge, guarantee or dedicated funding |
| Candidate ranking or investment authorization | NO-GO | Do not advance on unverified model frequencies |

## Dependencies for the next controlled stage
1. Replace third-party historical time series with official index total returns, direct/scheme-specific investable bond/mutual-fund NAV histories and consistent CPI back-series using MoSPI's 2024-base linking method.
2. Validate regime and tail parameters **out-of-sample** via rolling windows, crisis periods, time-series bootstrap with meaningful blocks, and predictive calibration tests. Historical bootstrap alone is insufficient because there are very few independent ten-year regimes.
3. Define explicit epistemic uncertainty ranges or posterior distributions for earnings growth, terminal valuation, bond carry/reinvestment, domestic gold/silver USD/INR, inflation persistence and cross-asset dependencies. Record expert judgments independently, before seeing portfolio acceptance metrics.
4. Use separate liability-matching analysis for any true real floor. Nominal sovereign cash flows and low-risk debt-fund portfolios do not guarantee CPI-indexed 2036 wealth.
5. Recalculate investor-specific taxes for each actual ISIN/scheme and tax lot. No double deduction of fund TER or fictitious realization of taxes solely in 2036.
6. Only after these steps should robust feasibility and candidate screening resume. No changes to mandate without explicit decision.

## Source references / provenance
- NSE Indices Nifty 500 Index Whitepaper (October 2025) reports historical since-1995 TRI annual volatility ~22.18%: https://www.niftyindices.com/docs/default-source/indices/nifty-500/nifty-500-whitepaper_2025.pdf
- MoSPI / PIB (12 Feb 2026) documents CPI rebase 2024=100: https://www.pib.gov.in/PressReleasePage.aspx?PRID=2227012&lang=1
- MoSPI / PIB (29 July 2026) explains CPI back-series and linking method: https://www.pib.gov.in/PressReleasePage.aspx?PRID=2291051&lang=1
- CCIL 30 Oct 2026 benchmark GS 2036 YTM 7.3977% is indicative: https://www.ccilindia.com/en/tenorwise-indicative-yields
- Input covariance from `stage512_empirical_calibration.json` (saved joint 2007–24 secondary-source proxy panel) and return hypotheses from `stage512_forward_calibration_assumptions.json`. Secondary source SHA and formulas are available in `stage512_independent_calibration.py`.

## Files
- `stage512_model_uncertainty.py` runnable analysis.
- `stage512_model_uncertainty_tests.py` deterministic integrity tests.
- `stage512_model_uncertainty_results.csv` 26 scenario/endpoint results.
- `stage512_model_uncertainty_assumptions.json` scenario inputs and limitations.
- `stage512_model_uncertainty_log.txt` run log.