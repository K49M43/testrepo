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

## 2. Independent validation found and quarantined a month-end boundary mismatch

The first official AMFI qualification produced 37 calendar-month-aligned returns (Oct 2023–Oct 2026), but a stricter independent review found that **the starting Sep 2023 fund NAV date is Sep 29 for equity/gold/silver and Sep 30 for the gilt fund**.

Because the Oct 2023 return uses the September closing NAV as its denominator, R7 explicitly excludes **Oct 2023** from the strictly synchronized risk sample. All remaining common monthly closing dates agree. This is a **controlled correction**, not a reason to invalidate the underlying 3,046 official NAV records.

The strict R7 research risk window is therefore **36 actual date-aligned monthly returns, Nov 2023–Oct 2026**. [Independent CI source/acceptance result](../data/official_nav_independent_R7.json) and [PASS diagnostics](../data/official_nav_R7_CI_diagnostics.json).

| Sleeve | Strict annualized log-return volatility |
|---|---:|
| Equity | 15.6535% |
| Gilt fund | 3.6575% |
| Gold ETF | 19.9857% |
| Silver ETF | 42.4028% |

**Strict matrix** (Equity / Gilt / Gold / Silver):
```text
             Equity    Gilt     Gold    Silver
Equity       1.00000  0.53089  0.05735  0.01871
Gilt         0.53089  1.00000  0.06215 -0.00131
Gold         0.05735  0.06215  1.00000  0.76735
Silver       0.01871 -0.00131  0.76735  1.00000
```

- Strict **fixed-weight risk approximation (65/20/10/5)**: **11.413711% annualized volatility**.
- Strict monthly-rebalanced portfolio-return approximation: **11.410895% annualized volatility**.
- For audit comparison only: the *unadjusted, month-label-aligned* 37-month output was 11.319344%; this remains in the original source manifest as its historical output, **not** the strict accepted risk statistic.

## 3. Regime instability within the strict sample

| Monthly-return sample | Observations | Equity vol | Gold vol | Silver vol | Equity–gilt correlation | Gold–silver correlation | Monthly-rebalanced portfolio vol |
|---|---:|---:|---:|---:|---:|---:|---:|
| Nov 2023–Sep 2024 | 11 | 9.10% | 12.62% | 26.17% | −0.146 | 0.449 | 5.22% |
| Oct 2024–Sep 2025 | 12 | 15.52% | 14.29% | 25.57% | 0.407 | 0.662 | 10.69% |
| Oct 2025–Oct 2026 | 13 | 17.88% | 28.61% | 63.62% | 0.670 | 0.838 | 14.46% |

Subperiods contain only 11–13 observations and do **not** establish statistically reliable structural breaks or future volatility trends. They are explicit scenario-evidence regimes, not forecast probabilities.

The worst month in the strict sample remains **March 2026**, with a reconstructed 65/20/10/5 monthly simple return near **−9.40%**. This is based on scheme NAVs, not executable ETF trade prices.

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
- Test 36-month strictly aligned pooled, 13-month recent, 2007–2024 long benchmark, and crisis covariance with the **same common forward-return assumptions**, then vary return assumptions separately.
- NAV values already include fund management expenses (TER); historical scheme NAV returns must not suffer a second TER subtraction. ETF bid–ask/spread, market premium, impact cost, taxation and tracking differences require separate study.
- Bring in official linked CPI and verify tax/investment flow convention before assigning forward real-wealth success probabilities.
- A contractual guarantee is distinct from even a well-calibrated 85% goal probability.

**Committee gate: historical instrument-source PASS; instrument-level long-horizon predictive-model NO-GO; overall investment NO-GO.**
