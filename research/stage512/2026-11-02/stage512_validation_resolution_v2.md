# Stage 5.12 — Source Reconciliation and Predictive-Tail Validation, controlled resolution

**Date:** 2 November 2026  
**Release:** R2 / independent audit  
**Scope:** ₹42 lakh initial, ₹25,000 SIP stepped 10% annually; 2036 target year; ₹90 lakh real after-tax floor and ₹100 lakh ambition.  
**Gate decision: CONDITIONAL RESEARCH PASS (tail alternative), INVESTMENT NO-GO.**

## Executive decision

This work resolves two methodological ambiguities and creates a tested reproducible tail-model challenger. It **does not** complete final official-source reconciliation, prove an 85% forward success probability or qualify the strict CPI-linked floor. Pretending otherwise would defeat the independent review.

**Specific corrected issues**

1. CPI integrity: previous purported '2012=100' third-party compilation has approximately 75–80 index units around 2012, inconsistent with its declared base. MoSPI's official *2024=100* combined general index uses published linking factor **0.5267** for the **2012-base general CPI**. March 2025 official CPI 2024-base = 101.39, implying about 192.50 on the appropriately defined old 2012-base index. The older third-party compiled March 2025 index was 157.55. Its units/base are not reconciled; **do not transform 157.55 by 0.5267**. Underlying official linked back series must be imported. The original long-run CPI-derived correlations and 10-year history replays are to be treated as provisional.
2. Monthly forecast distribution: earlier rolling Gaussian one-month predictions understated the observed March-2020 left-tail shock (~−6.8 model standard deviations in the real research portfolio proxy). A variance-matched Student-t with five degrees of freedom gave a better **historical** out-of-sample predictive log score. This is a defensible *model challenger*, **not a certified probability distribution for 2036**.

## New verified government CPI facts

- The all-India CPI 2024-base monthly combined index was **109.49 for September 2026 (provisional)**, with **5.54%** year-on-year inflation, published October 12.
- The published general CPI combined linkage factor is **0.5267** (old 2012 base -> new 2024 base) for earlier general CPI records, and MoSPI provides the linked all-India general-index back series for 2013–2024.
- A verified *partial* CPI JSON snapshot now includes 2025 January to 2026 September. Not a substitute for the missing full linked back series.

Government releases: https://www.pib.gov.in/PressReleasePage.aspx?PRID=2227012&lang=1&reg=3 and https://www.pib.gov.in/PressReleasePage.aspx?PRID=2322244&lang=1&reg=3

## Tail challenger — no lookahead, rolling test

**Input:** previous pinned synchronized July 2006–September 2024 5-variate **proxy** return panel (219 months). All wealth and correlation findings based on it are provisional pending official replacement. **Evaluation:** 105 strictly chronological predictions January 2016–September 2024; each forecast uses only the preceding 60 months for mean and sample standard deviation. Predictive densities are Gaussian and variance-normalized Student t with degrees of freedom 3/5/8/12, fixed before evaluation. All log scores are summed over months; higher is better.

| Out-of-sample series | Gaussian log score | Student-t(5) | Difference | Gap after excluding March 2020 |
|---|---:|---:|---:|---:|
| Equity | 154.58 | 171.26 | +16.68 | approx +0.93 |
| Portfolio nominal research proxy | 199.21 | 215.19 | +15.98 | approx +0.69 |
| Portfolio real research proxy | 202.54 | 218.56 | +16.02 | approx +1.06 |
| CPI previous compilation | 372.70 | 377.37 | +4.67 | not used for endorsement; CPI integrity failed |

The score advantage is dominated by the 2020 shock, which Student-t assigns a considerably less implausible tail likelihood. For a real-portfolio-proxy normalized residual of approximately −6.81, Gaussian one-sided event probability is ~4.88e-12; standardized Student-t(5) ~1.58e-4. **These are conditional model tail probabilities, not empirical frequencies or odds of another pandemic.** One observation cannot calibrate the true frequency of crises.

The real-portfolio proxy breached Gaussian 1% monthly VaR twice and Student-t(5) 1% VaR once across 105 months. The difference is not sufficient to validate an extreme quantile. Selection of Student-t(5) after comparing fixed alternatives on the same period adds *model-selection bias*. Require a fresh holdout or predeclared independent validation before graduation.

## Source promotion register

| Required series | Authoritative source verified exists | Full raw observations loaded / reconciled here | Model status |
|---|---|---|---|
| Nifty 500 TRI | NSE historical total-return index | **No** (third-party copy used) | PROVISIONAL |
| Nifty 10-year Benchmark G-Sec total return | NSE Indices | **No** (carry-duration synthetic proxy used) | PROVISIONAL |
| Mumbai standard gold and silver INR monthly | RBI DBIE | **No** (USD metal × USD/INR used) | PROVISIONAL |
| Linked official 2013–2024 2024-base CPI | MoSPI | **No** (verified 2025–Sep 2026 partial records only) | NOT RECONCILED |
| Actual equity, gilt, gold, silver MF / ETF NAVs | AMFI historical NAV | **No** | NOT RECONCILED |

**Correction to earlier language:** 'Official source identified' is NOT the same as 'official source reconciled.' Neither historical annualized returns nor correlation estimates from the old proxy panel should be reported as calibrated investable-portfolio risk without caveats.

## Accept / reject rules from now on

- **Data acceptance:** Every time series must identify exact instrument/index, source, as-of, units, pricing convention (month end vs monthly average), corporate actions, revisions, and data gaps. Assert complete index-to-index overlap before joint modeling. Do not forward-fill returns or mix price index and TRI.
- **Inflation acceptance:** Reproduce the official 2024-base linked CPI general back-series and September 2026 continuation. Confirm year-on-year monthly changes against MoSPI. Use October 2026 baseline after official October CPI release, not an invented number; the 6% model remains hypothetical.
- **Tail model acceptance:** Student-t and regime-switching/block-bootstrap challenger family, fixed before out-of-sample tests. Compare one-sided 5% and 1% exceedances, scoring rules, crisis log-scores, correlation regime behavior and shortfall severity. Do not choose by the best in-sample or same-holdout score alone.
- **10-year gate:** Do not claim a calibrated 85% wealth-success probability from only 219 monthly joint proxy data points or 100 overlapping ten-year histories. Use parameter/regime ambiguity and explicit stress limits. Always report 15th-percentile after-tax real wealth and probability/size of shortfall conditional on each fully labeled scenario.
- **Guarantee gate:** If the ₹90 lakh real floor must be contractual, it requires independently verified, cash-flow/credit/option-backed CPI-linked protection, not a probabilistic portfolio simulation. If it is only an 85% statistical goal, that is a distinct investor mandate requiring an explicit mandate change.
- **Execution gate:** Actual instrument ISIN/scheme code, retail executable quantity, spreads, expense/exit load, and FIFO tax lots required before GO.

## Deliverables and reproduction

- `stage512_tail_validation_v2.py`: executable Student-t challenger with declared degrees of freedom and fixed 60-month rolling forecasts; includes unit checks. Fully rerunning historical scores requires six pinned old proxy source files or internet access via `--fetch` and previous Stage 5.12 historical scripts. This file **does not** falsely assert the raw observations were written into the package.
- `stage512_official_cpi_2024base_verified.json`: precisely dated partial official CPI 2025–Sep 2026.
- `stage512_source_qualification_manifest.json`: source promotion tests and explicit failure states.
- `stage512_validation_resolution_v2.md`: this report.
- Existing Stage 5.12 baseline code is unchanged and can be used to reproduce earlier proxy-model results.

**Final decision:** tail-risk modeling improvement = research PASS as a challenger. Primary historical data reconciliation = **OPEN**. Ten-year forecast probability validation = **OPEN**. Stage 5.12 investment authorization remains **NO-GO**. The next executable gate is to source and reconcile official monthly histories and actual scheme NAVs; no honest statistical method can substitute for missing raw evidence.