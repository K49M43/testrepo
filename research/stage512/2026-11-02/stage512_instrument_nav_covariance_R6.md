# Stage 5.12 — R6 Independent Four-Fund Covariance Audit
**Audit date:** 2026-11-02  
**Source:** Existing Stage 5.8 36-month NAV history reconstructions with sampled AMFI checks  
**Model/Investment:** research-only; investment NO-GO.

## Executive result
The four specific fund histories previously passing Stage 5.8 risk QA were recovered and independently reprocessed using the same 36 monthly aligned return observations. The resulting **fixed-weight annualized historical NAV-volatility approximation is 11.352585%** for equity/gilt/gold/silver weights 65/20/10/5. This is **NOT** a 2036 predictive volatility estimate and does not account for contributions, realized taxation, or potential future regime changes.

### Qualified Stage 5.8 research inputs
| Sleeve | AMFI scheme code | Instrument | Annualized NAV volatility | Prior sampled official NAV matches | Historic jumps |
|---|---|---|---:|---:|---:|
| Equity | 147625 | Motilal Oswal Nifty 500 Index Fund — Direct Growth | 15.60532% | 15 | 0 |
| Gilt | 119116 | HDFC Gilt Fund — Direct Growth | 3.66962% | 16 | 0 |
| Gold | 105463 | UTI Gold ETF | 20.83795% | 16 | 1, outside recent clean window |
| Silver | 150556 | HDFC Silver ETF | 45.65748% | 16 | 0 |

These are **actual scheme NAV histories from a mirror** (mfapi.in), with sampled 2023–2026 AMFI observations independently reconciled. They are **not** wholly verified official daily histories. The older fund-level data has already been incorporated in our existing Stage 5.8 research archive.

### 36-month covariance correlations
|  | Equity | Gilt | Gold | Silver |
|---|---:|---:|---:|---:|
| Equity | 1.0000 | 0.5235 | 0.0308 | -0.0131 |
| Gilt | 0.5235 | 1.0000 | 0.0549 | -0.0077 |
| Gold | 0.0308 | 0.0549 | 1.0000 | 0.7639 |
| Silver | -0.0131 | -0.0077 | 0.7639 | 1.0000 |

The matrix was confirmed symmetric, with valid unit diagonal, and positive definite by Cholesky decomposition.

## Why this matters
The old longer-history **government bond yield-duration proxy** had a near-zero correlation with equity. This **observed gilt fund** shows a +0.5235 correlation with Nifty 500 fund returns in the recent 36-month sample. The measures represent different securities and windows and must not be treated as interchangeable.

The gold–silver fund correlation (0.7639) reinforces the concentration of precious-metal risk. Silver fund volatility of 45.66% in this window is materially higher than the earlier long-history silver bullion proxy estimate of ~29.85%. A fund NAV series can embody timing, exposures, product design and corporate-action history that differ from a bullion spot proxy. Verify splits, distribution treatment, fee inclusion and pricing methodology before attributing all differences to market regimes.

The 65/20/10/5 allocation's 11.35% recent-window volatility is **not evidence of floor protection**. Lower observed covariance is not a forecast, particularly under inflation and macro shocks.

## Provenance
- Archived source: [Stage 5.8 NAV quality metrics](../../stage58/qa_metrics.csv)
- Archived correlation source: [Stage 5.8 36-month NAV correlation rows](../../stage58/qa_correlations_36m.csv)
- Reproducible script: [R6 risk matrix reproduction](../pipelines/compare_stage58_covariance_R6.py)
- Machine-readable generated results: [R6 archived matrix and SHA256](../data/nav_stage58_comparison_R6.json)
- [New official-source full-history qualifier](../pipelines/amfi_four_sleeve_official.py) is a separate **unverified** acceptance gate.

## Decision / follow-on
**R6 historical-data comparison: research pass.** R6 verifies existing data handling and covariance arithmetic, not the truth or predictive applicability of the underlying mirrored history.

**Official full-series qualification: OPEN.** Do not promote the official four-sleeve calculation until the GitHub Actions qualifier returns a manifest with `PASS_36M_COHORT_ONLY` and the minimum synced-history criteria have been independently verified.

**Stage 5.12 investment decision: NO-GO.** Neither the 85% modeled 2036 floor probability nor a contractual ₹90 lakh inflation-indexed floor is established.
