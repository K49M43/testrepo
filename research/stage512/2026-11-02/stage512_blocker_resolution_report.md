# Stage 5.12 — Blocker 3/4/5 quantitative audit
**Date:** 2 November 2026. **Authority:** Analytical research only; no instrument or portfolio trade approval.

> **G5.1 correction (5 November 2026):** The 11.8% equity row below was generated from a fixed return assumption and synthetic random shocks, not a replay of a dated historical return path. Its original result values are preserved, but the scenario is quarantined from investment-decision evidence. See the [G5.1 claim-lineage and correction record](../2026-11-05/G5_1_118_CLAIM_LINEAGE.md). The 11.8% input itself remains unverified.

## Mandate
₹42 lakh upfront at October 2026 model inception. ₹0.25 lakh monthly contributed November 2026–December 2036, +10% each 12-month block. No funding interruption assumed. Main 2026 rupee value is after tax and inflation. ₹90 lakh real floor, ₹100 lakh real desired target; modeled 85% floor success acceptance criterion is *not* a contractual CPI guarantee. Total contributions ₹89.8123 lakh through October 2036 (120 months); ₹91.109 lakh through December 2036 (122 months).

## Sources observed as of research date
- NSE Nifty 500 index characterization and broad market representation: https://www.nseindia.com/static/products-services/indices-nifty500-index
- Nifty 500 on 30 Oct 2026: trailing P/E about 21, dividend yield about 1.28–1.31%, past average/typical volatility about 17%; the cited third-party page was reported as giving about 11.8% annualized since 1995. The exact source snapshot and calculation endpoint were not preserved; treat that return input as **UNVERIFIED**, not as an official NSE calculation. The separate NSE page supported the valuation snapshot: https://tipsheet.markets/indices/nifty-500/ and https://www.nseindia.com/market-data/index-performances (NSE 22 Oct snapshot P/E 21.30).
- CCIL indicative 30 Oct 2026 6.94% GS 2036 YTM 7.3977%: https://www.ccilindia.com/en/tenorwise-indicative-yields . **This is not a forecast of rolling gilt fund returns, nor an executable retail offer**.
- MoSPI CPI series changes from 2012 base to 2024 base effective Jan 2026; historical series require official linking/back series: https://www.pib.gov.in/PressReleasePage.aspx?PRID=2291051&lang=1&reg=48
- Current investor capital-gains tax rules: https://www.incometaxindia.gov.in/w/capital-gain and https://www.amfiindia.com/investor/knowledge-center-info?zoneName=TaxRegimeForMutualFunds . The 2036 tax rules are unknown.
- India's gold-equity diversification is state-dependent: https://www.gold.org/goldhub/research/why-gold-2025-building-indian-portfolio-resilience

## Model controls
- Recreated 25,000 synthetic paths per scenario, one fixed published seed (`20261102`); evaluated at months 120 and 122, monitored Jan–Dec 2036. Six scenarios are deliberately *not* assigned probabilities. The 11.8% row uses a constant geometric-return assumption with synthetic monthly shocks; it is neither a historical replay nor a forecast.
- Full portfolio liquidation-equivalent value at each observation month. Each sleeve is a synthetic single fund; new monthly contributions do not force rebalancing; the allocation remains a *fixed purchase split*, not a constant market-weight portfolio.
- Equity returns are valuation-linked *assumptions*: `(1+EPS growth)*(terminal PE / starting PE)^(1/10)*(1+dividend yield)-1`; low/central/strong P/E/EPS pairs: (6%,16), (9%,19), (11%,23), from earlier Stage 4.6 experiment.
- Base equity log-return volatility 17% (historical context, not forward inference); 22%/25% stress. Base CPI center 6%, stress 7% and 8%; CPI and return shocks explicitly correlated (unlike earlier independent-CPI models). Gilt, gold and silver expected returns, volatilities, and correlations remain *unvalidated hypotheses*.
- Input index-style returns are before the modeled explicit annual NAV expense drags. Taxes are simplified **current-law** liquidation estimates: equity LT 13% (including 4% cess on 12.5%) above assumed remaining ₹1.25L annual exemption; equity ST 20.8%; debt specified MF gains 31.2%; listed metal ETF LT 13%, ST 31.2% as modeled; no surcharge, investor external sales, asset class capital losses set-off or future tax change. Assumed redemption friction 0.10%, plus equity sleeve STT 0.001%. These are simplifications rather than an investable tax engine.
- The current run's Monte Carlo sampling uncertainty is much smaller than **parameter** uncertainty. It cannot validate market probabilities.

## 65/20/10/5 research mix — December 2036 (month 122)
| Assumption regime | Median gross nominal (₹L) | Median after-tax real (₹L) | 15th %ile real (₹L) | Model floor >=₹90L (%) | Model target >=₹100L (%) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Adverse valuation, CPI 7% | 130.56 | 62.07 | 42.82 | 18.13 | 12.72 |
| Central, CPI 6% | 168.74 | 86.39 | 64.72 | 44.56 | 32.24 |
| Synthetic 11.8% equity-return assumption, CPI 6% (unverified input; quarantined) | 191.71 | 97.45 | 71.42 | 59.77 | 46.89 |
| Central, student-t monthly shocks | 168.04 | 86.23 | 64.86 | 44.26 | 31.59 |
| Strong earnings/valuation, CPI 4.5% | 214.62 | 125.20 | 90.72 | 85.59 | 75.78 |
| Stagflation, CPI 8% | 137.11 | 59.23 | 38.81 | 18.47 | 13.56 |

Do **not** assign relative likelihoods to regimes without evidence. The favorable scenario *passing* 85% cannot be treated as a GO because its EPS, P/E, CPI and asset return inputs are selectively favorable and its 2036 realizability is not substantiated. Normal and student-t models do not account fully for regime persistence or extreme joint losses.

**85% rule:** passing a specified *model's* 85% terminal-wealth success criterion requires the 15th percentile of its wealth distribution to be at least ₹90L. Central 15th percentile is ₹64.72L, a ₹25.28L gap at December 2036. This is a scenario-model gap, not a contractual required external contribution or a guaranteed future outcome.

**Window semantics:** A paper valuation reaching a goal at any month in 2036 is not a safely locked real payout; CPI publication lags, price slippage, future tax and cash reinvestment risk remain.

## Stage 5.12 gate status
1. **Financial baseline: analytical pass** (consistent 120 versus 122 months, contribution schedules, CPI and month-specific taxes). Official October 2026 CPI index still to be recorded and linked; until then normalized CPI index=1.
2. **Tax: partial** (current broad rules verified, actual instrument and historical 2036 tax rates unverified, loss netting and surcharge omitted).
3. **Return and risk calibration: partial/no GO** (market snapshot observed; forward means, volatilities, crisis correlations, inflation linkages and regime probabilities not calibrated).
4. **Monte Carlo mechanics: partial pass, decision calibration NO GO** (reproducible, common random seed; assertions on contributions, quantiles, correlation matrices, zero-gain taxation, inflation factors. Independent implementation and empirical backtesting remain outstanding).
5. **Real floor: NO GO** (central/historical/stress simulation variants miss the 85% modeling threshold. No CPI-indexed after-tax guarantee verified; if hard contract protection applies it is independently unsatisfied).
6. **Execution: NO GO** (Stage 5.2 screened 24 direct GoI securities, no verified executable retail quotes and no qualifying CPI-linked guarantee; current fund expense, spreads and liquidity still need instrument evidence).

## Next mandatory work before any GO
- Establish synchronized, source-licensed India equity TRI, government bond total returns (and distinguish direct G-Sec maturity cash flows from gilt fund prices), INR gold and silver prices including ETF tracking, and CPI-linked/back-series monthly history with consistent dates and investable transaction adjustments.
- Estimate rolling return windows, volatility and volatility clustering, drawdowns, cross correlations including stress periods, data coverage, regime switching, and validation uncertainty. Fit competing models without using post-2026 observations.
- Run out-of-sample/pseudo-live backtests, bootstrap uncertainty by *effective* independent regimes, and test parameter robustness. Never turn path frequency into verified probability without model validation.
- Independently replicate NAV, exact FIFO lots, fiscal-year tax exemptions and loss offsets, interest and withholding, surcharge, STT, transaction costs, and the official annual CPI publication lag.
- Only then evaluate an instrument-specific portfolio, 85% floor criterion, ₹1Cr aspiration and any separate contractual floor requirement.

## Files
- `stage512_risk_audit.py` — rerunnable code
- `stage512_risk_scenarios.csv` — full output, 3 illustrative mixes, 6 regimes, 2 endpoints
- `stage512_assumption_register.json` — all scenario parameters and provenance caveats
