# Stage 5.12 — Independent forward-return calibration and decision audit
**As of:** 2 November 2026  
**Status:** Conditional scenario foundation established. Forward probabilities NOT market-calibrated. Investment authorization NO-GO.

## Executive finding
The research now distinguishes market-observed starting values from forward hypotheses and simulated outcome frequencies. The previous central risk specification is replaced by empirical historical proxy covariance for January 2007–September 2024, with a 2013–2024 sensitivity. The test does **not** qualify a contractual real-wealth floor.

For the research-only 65% Indian equity / 20% rolling gilt-fund proxy / 10% gold ETF / 5% silver ETF portfolio, the central 6% CPI scenario at December 2036 delivers median gross nominal ₹171.987 lakh, median after-investor-tax nominal ₹159.059 lakh, median after-tax real ₹88.427 lakh, and 15th-percentile real ₹62.232 lakh. The modeled frequency of exceeding ₹90 lakh real is **48.20%**, far short of the reference 85% criterion. Medians of gross, tax and net are individual marginal statistics and need not sum exactly.

## Mandate, timing and assumptions
Initial ₹42 lakh, plus monthly contributions of ₹25,000, stepped up 10% every 12 months, at month end beginning November 2026. 120 months ends October 2036 (₹89.8123 lakh contributions including the lump sum); 122 months ends December 2036 (₹91.109 lakh contributions). Target: ₹90 lakh *real after-tax* floor and ₹100 lakh desired purchasing-power outcome in 2026 rupees. The 85% model-frequency reference does NOT substitute for a guaranteed floor. The calendar year 2036 is the monitoring window, not a mandatory October exit. This experiment evaluates months 120/122, not full year window first-hit policies.

## Independent forward drivers and evidence quality

### 1 — Equity valuation and earnings model
Starting Nifty 500 trailing P/E approximately 21 on 30 Oct 2026 (published secondary index-valuation trackers). Official NSE market-data page displays P/E ~21.3 and dividend yield ~1.31% on 22 Oct 2026. Use **21 and 1.31%** as nearby-date reference anchors pending download and reconciliation of official 30 Oct index feed. Historical index earnings growth of 13.21% over the preceding five years from a secondary tracker is descriptive, **not** a projection or distributable cash-flow growth guarantee.

Ten-year approximate nominal equity total-return model:
`(1+annual EPS growth) * (2036 PE / 21)^(1/10) * (1+0.0131) - 1`.
This approximates dividends and is not a full fundamental cash-flow model: dividend-yield evolution, issuance, buybacks, constituent changes, free float and index earnings measurement error are unresolved.

- Adverse hypothesis: 6% EPS growth, terminal 16× P/E → gross equity geometric return **4.508%**.
- Central hypothesis: 9% EPS growth, terminal 19× P/E → **9.328%**.
- Favorable hypothesis: 11% EPS growth, terminal 23× P/E → **13.482%**.

There is **no empirically justified probability weight** for these cases. `stage512_equity_return_grid.csv` supplies the wider 7×7 combination grid to guard against selecting only favorable assumptions.

### 2 — Direct Government of India securities
CCIL tenor table, **30 Oct 2026**: benchmark 6.94% GS 2036 ISIN IN0020260025 had 7.3977% indicative pre-tax YTM. The trade report showed weighted-average **clean** price ₹96.91 per ₹100 face and 2,744 transactions on that date. This proves wholesale trading occurred, **not** that a retail investor may obtain the same ask, accrued-interest, clean/dirty quote, or quantity. ISIN matures **11 May 2036**, before a December-2036 outcome date, creating a reinvestment period. Coupon is semiannual (11 May and 11 November) and **6.94% is not the YTM**.

A separate per-₹100-face synthetic cash-flow audit uses ₹96.91 clean + ₹3.2437 estimated accrued = ₹100.1537 approximate dirty purchase, 31.2% coupon-income tax, 13% illustrative capital gain tax, and no surcharge or transaction fees. The resulting exploratory investor IRR is **5.223% nominal**, with approximate tax treatment of the first accrued coupon. This is neither official taxation advice nor an executable retail after-tax YTM. Reinvestment of coupons and all future SIP yields are NOT locked by this rate. A rolling gilt-fund sleeve is an entirely different duration-risk instrument and cannot inherit a held-to-maturity G-Sec yield as an assured fund return.

### 3 — Gold
World Gold Council's October 2024 *GLTER* framework estimated **5.2% annual USD gold returns for 2025–2040** from then-current global growth and portfolio assumptions; WGC explicitly does not present this as a guaranteed forecast. This model precedes the substantial 2025–2026 bullion movement and requires updating before use as a 2026 entry-point market expectation. We use 5.2% USD **only as a structural placeholder** and independently assume 2% nominal annual INR depreciation in the central hypothesis, generating `(1.052)*(1.02)-1` = **7.304% nominal INR gold** before illustrative fund cost of 0.4%. This is a sensitivity parameter, not an INR FX forecast; stress cases test no USD appreciation and adverse gold returns. ETF tracking and domestic tax require instrument-level validation.

### 4 — Silver
Silver Institute / Metals Focus (World Silver Survey 2026) describe physical deficits, industrial thrifting/substitution, jewelry price sensitivity and investment-flow instability. They do **not** supply a dependable 10-year nominal INR expected return. Central **4.5%**, adverse **−2%**, and favorable **10%** are explicitly **unweighted hypotheses**, not implied by a market yield or fundamental valuation. Previous historical-proxy silver annualized log volatility was ~29.85%, and observed gold–silver correlation 0.738 over 2007–Sep 2024. It should not be modeled as an independent low-risk diversification asset.

### 5 — Inflation
March 25 2026 Gazette: RBI framework targets **4%** annual CPI with 2–6% band for 1 Apr 2026–31 Mar 2031. It does not bind realized CPI, does not extend to December 2036, and is not a government inflation guarantee. CPI's 2024 base and historical back-series require careful official linkage. Prior historical secondary CPI proxy CAGR was 6.87% 2007–Sep 2024 and 5.54% 2013–Sep 2024; neither is a forward forecast. Preserve the investment mandate's **6%** primary purchasing-power assumption, with **4%** and **8%** sensitivities and stochastic CPI shocks. Inflation volatility is taken from historical proxy and annualized; monthly shocks assume no long-run persistence, so the risk of sustained inflation remains underrepresented.

## Fixed research-only forward cases (gross nominal geometric returns)

| Case | Equity | Rolling gilt fund* | Gold INR | Silver INR | CPI mean | Annual risk proxy |
|---|---:|---:|---:|---:|---:|---|
| Central | 9.328% | 7.0% | 7.304% | 4.5% | 6% | Full history 2007–24 |
| Adverse joint | 4.508% | 6.0% | 0% | −2% | 8% | Full history 2007–24 |
| Favorable joint | 13.482% | 7.4% | 9.408% | 10% | 4% | Full history 2007–24 |

*The gilt-fund growth hypotheses are **not** the observed G-Sec YTM or guaranteed fund returns.* All scenarios include asset-specific assumed fund expense drag (0.2%, 0.2%, 0.4%, 0.7% in equity, gilt, gold and silver); do not double-deduct if subsequently using published net-of-TER fund NAV returns.

## Results: 18,000 common-random-number paths, December 2036
Current 2026 investor tax rates: equity-oriented fund LTCG 13% including cess above annual ₹1.25 lakh allowance; equity STCG 20.8%; specified debt fund gain 31.2% at assumed marginal slab; listed gold/silver ETF LTCG 13% and STCG 31.2%. Simplified lots and no loss carry-forward, tax law changes, surcharge or external LTCG transactions. Terminal redemption friction assumed 0.1%, with modeled equity MF STT. No guaranteed fund or inflation hedge.

| Scenario | Median gross nominal ₹L | Median net nominal ₹L | Median real ₹L | 15th pct real ₹L | % real ≥ ₹90L | % real ≥ ₹100L |
|---|---:|---:|---:|---:|---:|---:|
| Central 6% CPI, full covariance | 171.99 | 159.06 | 88.43 | 62.23 | 48.20 | 37.80 |
| Central 6% CPI, recent covariance | 169.75 | 157.30 | 87.32 | 67.44 | 45.34 | 31.46 |
| Central 4% CPI | 171.99 | 159.06 | 107.32 | 75.53 | 68.77 | 57.54 |
| Central 8% CPI | 171.99 | 159.06 | 73.12 | 51.46 | 30.06 | 22.01 |
| Adverse joint regime | 125.52 | 118.82 | 54.72 | 39.59 | 10.02 | 6.38 |
| Favorable joint regime | 221.33 | 201.78 | 136.08 | 92.04 | 86.43 | 78.61 |
| Higher rolling-fund carry 7.4% | 172.90 | 159.71 | 88.76 | 62.58 | 48.68 | 38.17 |
| Zero USD gold growth + FX 2% | 166.29 | 154.16 | 85.77 | 59.93 | 44.84 | 35.18 |

Under the central hypothesis the 15th percentile is **₹27.77 lakh below** the ₹90 lakh required floor. The favorable joint regime's apparent 86.43% chance of crossing the floor **DOES NOT justify GO**; it has no validated likelihood and a materially adverse rival regime. The 85% benchmark is a modeled distribution criterion, NOT an inflation-linked guarantee.

For the central 6% scenario, October 2036 month 120: median real ₹87.346 lakh, 15th percentile ₹61.715 lakh, modeled floor frequency 46.94%; December month 122: ₹88.427 lakh, ₹62.232 lakh and 48.20%. This difference arises from time, contributions and return risk, not from a mandatory sale decision.

## Independent check and model governance
- 18,000 Gaussian log-return paths each scenario; seed 20261102; identical standard-normal draws reused across cases for controlled comparisons. No resampling-derived probability weights for economic regimes.
- Historical covariance matrices are based on *secondary price proxies* through Sep 2024, not updated fund NAV return history. Full-history CPI proxy data are old-base composites, not confirmed linked 2024-base official series.
- Regime persistence, volatility clustering, heavy tails, model drift uncertainty and crisis correlation jumps are **not quantified** by this run; thus 15th percentile is still likely too precise as a prospective statement.
- Data and tax classification of the exact chosen funds/ETF/direct securities, retail executable quotes and monitoring dates are unverified.
- No optimization or candidate approval was performed: 65/20/10/5 and two comparison mixes are research test policies only.

## Findings and next gate
| Gate component | Outcome | Action |
|---|---|---|
| Equity valuation mechanism | Conditional analytical PASS | Validate primary index dividend, earnings methodology and terminal valuation distribution |
| Direct G-Sec yield and single-purchase cashflows | Conditional analytical PASS | Reconcile quote/dirty price, accrued interest, tax and retail access; model future SIP/reinvestment risk |
| Gold INR forward return | PARTIAL | Refresh WGC-style model inputs as of 2026; independently model FX |
| Silver INR forward return | OPEN | Do not pretend there is a calibrated 10-year point forecast; use bounded/adversarial regimes |
| CPI projection 2026–2036 | PARTIAL | Link MoSPI 2024-base back series, persistence model; 6% planning anchor intact |
| Joint probability model | OPEN | Include uncertain economic regime probabilities, stress covariances, fat-tail bootstrap and validation against genuine fund NAVs |
| 85% real floor success | **NO-GO** | 15th-percentile gap unresolved under central assumptions |
| Strict guaranteed real floor | **NO-GO** | No eligible qualifying CPI-linked guarantee funded |

**Conclusion:** This stage produces a defensible *scenario architecture*, not an independently established future market distribution. The next blocker is to validate instrument-specific investable histories, CPI linkage and tax-sensitive multi-regime simulations, then quantitatively test whether any feasible allocation clears the floor across plausible uncertainties. Do not alter the goal or its criteria to force an approval.

## Direct source links
- CCIL tenor indicative yields: https://www.ccilindia.com/en/tenorwise-indicative-yields
- CCIL 30 Oct outright trade: https://dr.ccilindia.com/web/ccil/volumewise-outright-trade
- NSE index valuation: https://www.nseindia.com/market-data/index-performances
- Nifty 500 valuation series: https://equitytimer.com/market-data/pe-ratio/nifty-500/
- Government Gazette on inflation target: https://egazette.gov.in/WriteReadData/2026/271285.pdf
- MoSPI CPI methodology: https://mospi.gov.in/faq
- World Gold Council GLTER: https://www.gold.org/goldhub/research/golds-long-term-expected-returns/building-block-approach
- Silver Institute WSS: https://silverinstitute.org/global-silver-investment-to-remain-strong-in-2026-against-the-backdrop-of-a-sixth-consecutive-annual-market-deficit/
- Income Tax Department: https://www.incometaxindia.gov.in/en/sale-of-shares