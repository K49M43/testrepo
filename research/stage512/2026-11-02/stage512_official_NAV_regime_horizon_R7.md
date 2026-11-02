# Stage 5.12 — R7 Official Four-Fund Data, Regime and Horizon Integrity Audit

**Research date:** 2 November 2026  
**Official data gate:** PASS for sampled scheme histories **2023-09-25 to 2026-10-30**  
**2036 investment authorization:** **NO-GO** (separate decision).

## 1. What qualified

Official AMFI history was successfully retrieved for four named instruments. The original AMFI four-sleeve qualification manifest reports 12 official API response segments, 63 sampled official snapshot comparisons, **zero NAV mismatches**, and 3,046 accepted NAV observations.

| Research sleeve | AMFI scheme code | Observed official priced NAVs | Checks matching prior official snapshots |
|---|---|---:|---:|
| Nifty 500 index fund | 147625 | 763 | 15 |
| Gilt fund | 119116 | 751 | 16 |
| Gold ETF | 105463 | 766 | 16 |
| Silver ETF | 150556 | 766 | 16 |
| **Total** | | **3,046** | **63** |

Source: [official-source acceptance manifest](../data/amfi_official_36m/qualification_manifest.json), [official four-fund dated NAVs](../data/amfi_official_36m/official_nav_four_assets.csv).

## 2. Independently recomputed NAV covariance

An independent calculation directly on the 3,046 official archived NAV observations produced 37 complete, synchronized monthly returns, **Oct 2023–Oct 2026**, with no duplicate fund-date rows, no nonpositive NAVs, a largest inter-observation gap of four calendar days, and the same month-end observation date for every fund.

| Sleeve | Annualized log-return volatility |
|---|---:|
| Equity | 15.5730% |
| Gilt fund | 3.6211% |
| Gold ETF | 19.8497% |
| Silver ETF | 41.8173% |

Correlation matrix, in Equity/Gilt/Gold/Silver order:
```text
             Equity    Gilt     Gold    Silver
Equity       1.00000  0.53603  0.04046  0.02107
Gilt         0.53603  1.00000  0.05062  0.00041
Gold         0.04046  0.05062  1.00000  0.75938
Silver       0.02107  0.00041  0.75938  1.00000
```

Indicative static-weight annualized volatility for 65% equity, 20% gilt, 10% gold and 5% silver = **11.319344%**. Equivalent annualized monthly-rebalanced weighted-return volatility = **11.318305%**. These are historical descriptive measures, not forecasts, and assume constant weights for the moment calculations.

## 3. Nonstationarity within the source history

| Monthly-return sample | Observations | Equity vol | Gold vol | Silver vol | Equity–gilt correlation | Gold–silver correlation | Monthly-rebalanced portfolio vol |
|---|---:|---:|---:|---:|---:|---:|---:|
| Oct 2023–Sep 2024 | 12 | 10.67% | 12.89% | 24.97% | 0.194 | 0.407 | 6.27% |
| Oct 2024–Sep 2025 | 12 | 15.52% | 14.29% | 25.57% | 0.407 | 0.662 | 10.69% |
| Oct 2025–Oct 2026 | 13 | 17.88% | 28.61% | 63.62% | 0.670 | 0.838 | 14.46% |

Sample sizes are too small for a high-confidence time-series forecast or structural-break claim. This table **does not establish a continuing upward trend**. It demonstrates that a 37-month pooled covariance masks materially different observed subperiods.

The most adverse of 37 monthly rebalanced portfolio log returns occurred in March 2026, approximately **−9.87% log** (about **−9.40% simple return**), conditional on constant-sleeve weights and NAV-based pricing.

## 4. Structural ten-year-history limitation

Archived **earliest available** NAV points in the previous Stage 5.8 research:
- UTI Gold ETF: 2007-04-13
- HDFC Gilt Fund: 2013-01-01
- Motilal Oswal Nifty 500 Index Fund: 2019-09-11
- HDFC Silver ETF: 2022-09-02

The four-fund joint official (or mirrored) fund history **cannot reach ten years in 2026**, regardless of download reliability. Expecting a ten-year scheme-level sample is an impossible acceptance condition for this cohort.

**Corrected research design:** a two-layer evidence architecture:
1. **Long-run market/asset-class benchmarks**, separately verified from NSE official total-return, fixed-income total-return, domestic bullion, and MoSPI linked CPI history, provide historical regime coverage and scenario stresses. Such benchmarks must be called proxies, not fund-level realized returns.
2. **Actual scheme NAVs**, direct official AMFI where available, provide realized instrument-level expenses, tracking differences, product volatility and recent cross-asset relationships.
3. Explicit bridge models and sensitivity bands quantify fund-vs-benchmark discrepancies, inception/tracking risk, ETF NAV vs executable price, and gold/silver concentration. A splice must not be misrepresented as a ten-year realized portfolio record.

## 5. Next model gate

- Independent [R7 reproducibility script](../pipelines/independent_official_NAV_R7.py) and [CI workflow](../../../.github/workflows/stage512-official-nav-R7.yml) must independently replicate the official-source statistics. Its result file is [R7 calculation result](../data/official_nav_independent_R7.json) **only if the workflow has produced it**.
- Do **not** replace forward-return means with these short-window historical fund returns.
- Test 37-month pooled, 13-month recent, 2007–2024 long benchmark, and crisis covariance with the **same common forward-return assumptions**, then vary return assumptions separately.
- NAV values already include fund management expenses (TER); historical scheme NAV returns must not suffer a second TER subtraction. ETF bid–ask/spread, market premium, impact cost, taxation and tracking differences require separate study.
- Bring in official linked CPI and verify tax/investment flow convention before assigning forward real-wealth success probabilities.
- A contractual guarantee is distinct from even a well-calibrated 85% goal probability.

**Committee gate: historical instrument-source PASS; instrument-level long-horizon predictive-model NO-GO; overall investment NO-GO.**
