# 2036 Research | Independent historical calibration — Stage 5.12

Assessment: 2 November 2026  
Status: **EMPIRICAL RISK BASELINE PRODUCED; FORWARD MARKET CALIBRATION NOT COMPLETE; CAPITAL DEPLOYMENT NO-GO.**

## Executive judgment

The previous 17% equity, 5% gilt-fund, 16% gold and 28% silver annual volatility assumptions were *hypotheses*, not historical estimates. The new historical proxy exercise reports materially higher longer-window equity risk and a stronger gold–silver relationship. This alone prevents treating the earlier Monte Carlo frequencies as decision-grade probabilities.

Measured risk does not imply the historical realized growth rate is the appropriate *forward* drift. We must not raise assumed equity return to 13.19% merely because that occurred over the calibration window, particularly when the 2007–2012 subperiod earned 7.54% and the 2020–2024 subperiod 22.10% on the same method.

## Source manifest and security classification

1. Indian equity: **NIFTY 500 TRI** copied from a public sample CSV (`Sams3pi01/SIP-Calculator`; file SHA `89f0bb076ce6a733197e89416830203c6f3ddd8a`), calendar-month last available index value. Coverage January 1995–February 2026. Third-party copy of the NSE total-return index: validate primary NSE output before deployment.
2. Fixed-income *proxy*: third-party daily Indian 10Y nominal government-security yield series (`aswinv90/indian-market-historical-data`, SHA `4d23a6d8cf033b0cf06b1c630a18b787ebcba5ef`), 2000–September 2026. Synthetic monthly simple return = prior monthly 10Y yield/12 – 7.5 × yield change + 30 × change squared (yield units in decimals); log(1+return) used for statistics. This is a **carry–duration–convexity approximation**, NOT a real government-security total-return index, not actual gilt mutual-fund NAV, and not a 2036 maturity-matched sovereign bond.
3. Gold and silver *proxies*: USD gold and silver daily quotes through September 2024 (`vasco-duarte-oikosofy/gold-data-set`, file SHAs `d6b8fd880311a0c711c33f2c5655f0237632ca5d` and `3ecb1baf9d00edf815b6754390eb9e624b636a1c`), multiplied by USD/INR last available monthly rate from `aswinv90` (SHA `5ae709244837e16281ba256f603aaea24caa56a9`). Omit domestic duties, bullion spreads/premiums, and ETF tracking/taxes. FX quote date may differ from bullion quote date within the month. Thus *not a fund benchmark or investable realized return*.
4. CPI: secondary historical series (`aswinv90`; file SHA `508ebbda8b48a66c8f3e2588d3088f03dfc45bd5`) through March 2025. The CPI labeling/linked-level provenance has NOT been independently validated against original MoSPI releases. Treat joint historical price level growth as a proxy until reconciliation.
5. Joint overlap ends **September 2024**, because the silver/gold source ends then. This omits the 2025–2026 precious-metal regime. The **213** usable monthly log-return observations from January 2007 to September 2024 are synchronized by calendar month but not necessarily by identical intramonth market timestamp.

All observations, signatures and calculations use the datasets as retrieved on 2 November 2026. Exact URLs are in the accompanying `stage512_independent_calibration.py` source manifest; every main-branch fetch is checked against the observed **Git blob SHA**, so a subsequent source revision fails rather than silently changing the result.

## Observed calibrated measures

Annualized historical compound growth is `exp(12 * mean monthly log return) - 1` and log-return volatility is `sqrt(12) * standard deviation(log monthly return, ddof=1)`.

| Panel | Months | Equity CAGR / vol | Govt-bond proxy CAGR / vol | Gold INR CAGR / vol | Silver INR CAGR / vol | CPI CAGR / vol |
|---|---:|---:|---:|---:|---:|---:|
| 2007–Sep 2024 | 213 | 13.19 / 22.45% | 8.12 / 7.06% | 12.41 / 16.72% | 9.18 / 29.85% | 6.87 / 2.68% |
| 2013–Sep 2024 | 141 | 16.19 / 16.70% | 8.38 / 4.98% | 7.89 / 15.12% | 4.21 / 26.90% | 5.54 / 2.40% |
| 2007–2012 | 72 | 7.54 / 30.84% | 7.61 / 9.99% | 21.84 / 19.37% | 19.61 / 34.98% | 9.51 / 3.05% |
| 2013–2019 | 84 | 12.34 / 14.15% | 9.63 / 5.79% | 2.39 / 16.35% | −3.73 / 24.42% | 6.03 / 2.55% |
| 2020–Sep 2024 | 57 | 22.10 / 19.93% | 6.58 / 3.47% | 16.52 / 12.91% | 17.13 / 30.09% | 4.82 / 2.15% |

### Monthly contemporaneous correlation, full 2007–Sep 2024

| | Equity | Bond proxy | Gold | Silver | CPI |
|---|---:|---:|---:|---:|---:|
| Equity | 1.000 | −0.028 | −0.090 | 0.158 | 0.087 |
| Bond proxy | −0.028 | 1.000 | −0.082 | −0.079 | −0.097 |
| Gold | −0.090 | −0.082 | 1.000 | 0.738 | −0.062 |
| Silver | 0.158 | −0.079 | 0.738 | 1.000 | −0.031 |
| CPI | 0.087 | −0.097 | −0.062 | −0.031 | 1.000 |

Gold–silver correlation: 2013–2019 **0.863**; 2020–Sep 2024 **0.649**. Equity–gold correlation: 2013–2019 **−0.312**; 2020–Sep 2024 **−0.070**. No single matrix adequately represents every market regime.

## Implications for existing Stage 5.12 assumptions

| Item | Earlier central assumption | Independent historical observation | Committee action |
|---|---|---|---|
| Equity annualized volatility | 17% | 22.45% full / 16.70% recent | Use both full and recent risk specifications; introduce crisis model |
| Bond annualized volatility | 5% | 7.06% full / 4.98% recent, **synthetic proxy** | Replace proxy with verified NSE G-Sec TRI / actual fund returns before GO |
| Gold annualized volatility | 16% | 16.72% full / 15.12% recent, **FX spot proxy** | Tentatively retain as risk reference, not ETF validation |
| Silver annualized volatility | 28% | 29.85% full / 26.90% recent, **FX spot proxy** | Tentatively retain as risk reference, not ETF validation |
| Gold–silver correlation | 0.60 | 0.738 full / 0.763 recent | Raise correlated-metals stress; preserve regime variation |
| Inflation mean | 6% mandate | 6.87% full / 5.54% recent, historical | Keep 6% primary and 4%, 8% inflation stresses; **do not tune inflation to hit target** |
| Equity annual return | 9.296% illustrative | 13.19% *historical*, 7.54–22.10% subperiod divergence | Historical 13.19% MUST NOT replace forward earnings/valuation-based scenarios |

Approximate constant-weight 65/20/10/5 volatility: old central 11.65%, 2007–2024 measured covariance 14.98%, 2013–2024 measured covariance 11.03%. This does not incorporate the no-rebalancing drift of actual portfolio holdings or tax effects.

## Forward calibration policy (controlled, not an invented point forecast)

1. **Drift / return:** Retain independently specified valuation-conditioned Indian equity scenarios, not historical return fitted to target. The previous 4.48% / 9.30% / 13.45% geometric equity scenarios for EPS + terminal P/E assumptions are exploratory hypotheses requiring valuation, earnings, corporate-actions and dividend cross-check. Direct G-Sec's observed 30-Oct-2026 ~7.40% YTM is a bond-specific market reference **before tax**, not expected gilt-fund return or locked SIP rate. Gold and silver have no earnings/YTM anchor: set materially wide, explicitly unweighted drift scenarios and validate physical/FX drivers rather than regress past means into future forecasts.
2. **Volatility:** full/long-run (2007–24) covariance; recent (2013–24) covariance; separate crisis covariance; annual geometric drift and annual log volatility must remain mathematically distinct.
3. **Correlations:** empirical 5×5 matrix only for the panel from which it came; introduce correlated equity/bond risk-off shocks, correlations under inflation regimes, and estimation error. Test correlations robustly with bootstrap/leave-one-crisis-out rather than selecting the matrix with highest success rate.
4. **Inflation:** primary 6% and 4%, 8% plus stochastic inflation, including **negative real asset returns during inflation surprises**. CPI measurement/release delay must be modeled for real-time trigger policies.
5. **Resampling:** monthly contiguous blocks rather than independent months, and explicit 2008/2020 event replay. In this panel, overlapping 10-year historical windows are NOT independent sample paths; never present bootstrap frequencies as calibrated probabilities.
6. **Taxes:** keep scheme-level FIFO lots, gilt-fund versus directly held bond cash flows, interim coupon taxation and evolving law separate; verify India asset-class tax classification and primary security/fund data before investment decisions.
7. **External validation:** reconcile raw NSE TRI, official MoSPI CPI, RBI Mumbai gold/silver spot, verified NSE 10-year benchmark G-Sec total-return index, and scheme NAV tracking; update joint dataset through October 2026 where sources allow and exclude preliminary unpublished months.

## Gate assessment

- **Historical proxy covariance and regime comparison:** PARTIAL PASS; calculations reproducible against the pinned third-party datasets.
- **Current/forward investable assets, future drift distributions and evidence of 85% floor success:** NOT VALIDATED.
- **Stage 5.12 decision:** **NO-GO**, unchanged. An attractive investment probability based on only the strong growth regime would be scenario selection bias.

The next controlled experiment is to rerun the prior Stage 5.12 tax-aware Monte Carlo with (i) long-run empirical *proxy* covariance, (ii) recent covariance, (iii) stress correlation and structural breaks, at common *explicit* forward-drift scenarios, holding the objective and SIP schedule fixed. This is a model-sensitivity exercise, not the final investment decision.

## Controlled Stage 5.12 model sensitivity (25,000 shared random paths)

A targeted rerun changed **only** the annualized log volatility and 5×5 contemporaneous correlation matrix, holding prior central geometric return hypotheses (equity 9.296%, gilt fund 7%, gold 5.5%, silver 6%), annual fee assumptions, 6% CPI drift, ₹42L initial wealth, ₹25,000 stepped-up monthly SIPs, simplified tax logic and implementation assumptions unchanged. Random seed `20261102`; Gregorian December 2036 is month 122. Same independent random normals were reused across comparisons for paired control. This experiment should not be mistaken for a market-calibrated forecast.

| Risk specification | December 2036 median real wealth (₹L) | 5th percentile (₹L) | 15th percentile (₹L) | Model frequency reaching ₹90L | Model frequency reaching ₹100L |
|---|---:|---:|---:|---:|---:|
| Old central matrix | 86.393 | 55.631 | 64.716 | 44.56% | 32.24% |
| Full 2007–2024 historical proxy covariance | 87.555 | 51.451 | 61.614 | 47.16% | 36.99% |
| Recent 2013–2024 historical proxy covariance | 86.506 | 58.296 | 66.782 | 44.02% | 30.40% |

**Interpretation:** the full-period covariance *broadens* the model distribution. A higher chance of crossing the floor can coexist with a materially worse lower tail. The correct evaluation criterion combines model floor frequency, loss-severity distribution, 5th/15th percentiles, and structural stress rather than maximizing probability alone.

Reproduction: `stage512_calibrated_sensitivity.py` imports the exact 5×5 matrices/annualized volatility arrays in `stage512_empirical_calibration.json` into the earlier Stage 5.12 tax-aware simulation; writes `stage512_empirical_sensitivity_results.csv` and the assumptions. Its inherited tax and lot model is simplified. No empirical historical calibration resolves its remaining fiscal, cost, liquidity or mandate-qualification deficiencies.