# Stage 5.12 — Actual Source Reconciliation: Controlled Resolution R3

**Decision date:** 2 November 2026  
**Investment gate:** NO-GO (not automatically lifted by improved source integrity)  
**Scope:** ₹42 lakh at inception; ₹25,000/month increasing 10% annually; 2036 internal horizon; ₹90 lakh real after-tax floor / ₹100 lakh real target.

## Executive result

**CPI source gap substantially resolved:** We built a contiguous 165-month *all-India combined general* CPI 2024-base history from January 2013 through September 2026 using observed figures from the Government of India, not the formerly mislabeled unofficial CPI series. The original 2013–2024 monthly observations come from the Ministry of Statistics and Programme Implementation (MoSPI), December 2025 CPI press release, **Annexure VI (page 10)**. Their published 2012-base general index was converted using MoSPI's government-published 2024-base linked-series factor **0.5267**. For January 2025 onward, actual 2024-base CPI observations from previously government-verified release snapshots are used directly; the old-base series was **not** inappropriately multiplied through 2025.

**Other source gaps remain OPEN:** Neither the full authoritative Nifty 500 TRI download, nor the complete NSE G-Sec total-return series, nor full RBI Mumbai gold/silver monthlies, nor scheme-level AMFI historical NAV have been imported into the model in this execution. These official sources were identified and verified, but links and sample observations are not equivalent to a complete reconciled dataset. Hence the earlier forward success frequencies are still conditional calculations, not validated probabilities.

## Official inflation time series constructed

| Metric | Result |
|---|---:|
| Official older CPI records transcribed (2013–24) | 144 months |
| New-basket official CPI (2025–Sep 2026) | 21 months |
| Total contiguous CPI levels | **165 months** |
| CPI level January 2013, converted 2024 base | **55.09282** |
| CPI level December 2024, converted 2024 base | **102.91718** |
| CPI level September 2026, actual 2024 base | **109.49** |
| Annualized CPI growth January 2013–December 2024 | **5.3839%** |

**Audit:** The script passes contiguous-month tests, shows correct base/units and source URL for every observation, and reproduces published year-on-year rates for January 2014 (8.60%), January 2015 (5.19%), January 2016 (5.69%), January 2026 (~2.74%), and September 2026 (~5.54%) within rounding tolerance. The transcribed 2013–2024 historical table also agrees with MoSPI’s September 2025 independent publication of Annexure VI (https://mospi.gov.in/sites/default/files/press_release/CPI_PR_12sep25.pdf#page=10). A final line-by-line visual transcription audit and comparison to the separately downloadable NSO 2024-base back-cast remain desirable independent crosschecks.

Sources:
- MoSPI December 2025 original monthly table: https://cpi.mospi.gov.in/PDFile/Press/PR%20December%202025.pdf#page=10
- MoSPI 2024-base linkage: https://mospi.gov.in/uploads/documents/documents/1770891066052-Annexure_V.pdf#page=5
- MoSPI 2024 series official page: https://esankhyiki.mospi.gov.in/macroindicators?product=cpi
- Previously validated September 2026 official CPI snapshot: https://www.pib.gov.in/PressReleasePage.aspx?PRID=2322244&lang=1&reg=3

### Why the old CPI proxy is not acceptable

A same-month check of 144 observations (2013–2024) against the previous publicly hosted third-party CPI dataset found:

| Metric | MoSPI original linked series | Prior compilation |
|---|---:|---:|
| 2013–2024 annualized CPI rate | 5.384% | 5.406% |
| Standard deviation of monthly log inflation | 0.669 percentage point | 0.692 percentage point |
| Mean absolute difference in corresponding monthly log inflation | \- | **0.278 percentage point** |
| Maximum identified monthly difference | \- | **2.44 percentage points** (July 2018) |

**Interpretation:** The older compilation's multi-year inflation growth happened to be close to official series, but some individual monthly changes were materially different. That can distort correlations, volatility, inflation-tail testing and simulation month of 'lock-on-hit' events. The old proxy is now **REJECTED** for future CPI covariance calculations. The historical goal replays relying on it are quarantined; old success counts should not be reported as validated real-world probabilities. This comparison is between the *growth rates*, not arbitrary raw levels of differently scaled indexes.

Prior CPI source for controlled comparison: https://github.com/aswinv90/indian-market-historical-data/blob/main/data/MACRO/cpi_inflation.csv

## Required remaining source reconciliation

| Series | Primary source | Current state | Acceptance test |
|---|---|---|---|
| Nifty 500 total return index | NSE Indices | NOT IMPORTED | Actual TRI values 2013–2026, checks for consistent month-end observation and no price-index substitution |
| G-Sec total return | NSE Indices | NOT IMPORTED | Actual total-return bond benchmark; never substitute a static-duration price approximation as an actual index |
| Gold and silver, Mumbai INR | RBI DBIE | NOT IMPORTED IN FULL | Monthly-average gold per 10 g and silver per kg; correctly label as bullion, not ETF returns |
| Actual scheme NAV | AMFI | NOT IMPORTED | Direct-growth scheme-code-specific NAV, inception, tracking, expense/exit loads and missing-date checks |
| CPI 2024-base | MoSPI | **DERIVED PRIMARY SERIES AVAILABLE** | 165 contiguous values and published YoY crosschecks PASS; separate bytewise official backseries verification pending |

Primary-source endpoints:
- NSE: https://www.niftyindices.com/reports/historical-data
- RBI DBIE curated: https://dbie.rbihub.in/tables?table=real_sector.r17_monthly_average_price_of_gold_and_silver_in_mumbai
- RBI DBIE documented public data API: https://dev.dbie.rbihub.in/docs/using-the-site
- AMFI: https://www.amfiindia.com/net-asset-value/nav-download

## Engineering gate tested

The artifact `stage512_import_gate.py` expects an explicitly attributed monthly level for each of the relevant assets. It rejects missing sources, mixed price and total returns, non-primary source claims, missing months, duplicate months, mismatched fund metadata or invented pre-inception fund history. **Running with no authoritative market files exits with code 2 / `REJECT`**, as demonstrated in the supplied JSON log. Passing structural schema alone does not authenticate website bytes or validate forecasting performance.

For an actual fund NAV, the gate evaluates observed fund history from inception, allowing a shorter NAV record than the underlying benchmark (silver ETFs, for example, did not exist across the entire benchmark span). Never backfill a fund's pre-launch returns with synthetic values. NAVs already net out fund TER; no second TER subtraction.

## What is and is not resolved

- **Resolved to research-use standard:** Correct original CPI source found; 2013–2026 all-India general linked levels rebuilt; month-by-month inflation computed; multiple YoY tests passed; old corrupted/mislabeled CPI replaced. Next sensitivity rerun may use these CPI values.
- **Not resolved:** Joint five-variable official risk-covariance panel; actual investable fund returns; scheme-level taxes, tracking and execution; independent ten-year probability inference. The updated CPI series alone is insufficient to rerun the final investable portfolio forecast without still relying on three stale/non-investable proxies.
- **Unchanged:** The model's hypothetical 6% planning inflation; this is a scenario input, not the mean rate of the historical CPI series. ₹90 lakh floor at 85% modeling confidence is not a contractual CPI-linked payout guarantee.

**Next gate:** Import the four primary market histories, reconcile their units and calendars, compare actual product tracking errors, then repeat short-horizon tail tests and 2036 after-tax real-wealth simulations on the corrected panel. Keep an explicit parameter-uncertainty envelope, not one presumed 'true' success probability.