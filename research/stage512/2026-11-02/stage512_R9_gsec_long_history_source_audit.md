# Stage 5.12 — R9 Government-Security Total-Return Benchmark Resolution Attempt
**Date:** 2 November 2026  
**Investment approval:** **NO-GO**  
**Source classification:** LIC ETF product-level NAV backfill pending; published LIC benchmark performance windows verified.

## 1. Source discovery resolves an incorrect assumption

The actual **LIC MF Nifty 8–13 Yr G-Sec ETF** has a NAV series from **26 December 2014**, enabling an ~11.8-year, actual government-bond ETF **product history** if its archived AMFI observations pass independent validation. This does **not** mean the official NSE 8–13 yr G-Sec **index total-return daily series** is now available.

First-party identification:
- NSE exchange-hosted LIC scheme summary: https://nsearchives.nseindia.com/trading_security/mf/pdf/LIC_09042026153022_LICMFNifty813yrGSecETF.pdf
- AMFI scheme code **133307**; ISIN **INF767K01MV5**; NSE symbol **LICNETFGSC**.
- The scheme replicates/tracks the **Nifty 8–13 yr G-Sec Index**, subject to tracking error. It is a rolling-duration ETF, **not** a direct 2036-maturing, held-to-maturity government bond.
- The NSE benchmark is based on a monthly-reconstituted liquid Government of India bond basket and is explicitly a **total-return** index. Index methodology: https://www.niftyindices.com/Methodology/Method_NIFTY_Fixed_Income_Indices.pdf

## 2. Independently published first-party ETF-versus-index return comparisons

Four LIC factsheet reporting months provide 12 retrospective, published comparison pairs:

| Factsheet month | ETF 1Y | Index 1Y | ETF 3Y | Index 3Y | ETF 5Y | Index 5Y |
|---|---:|---:|---:|---:|---:|---:|
| Aug 2024 | 8.77% | 8.95% | 5.38% | 5.65% | 5.73% | 6.06% |
| Feb 2026 | 6.66% | 6.82% | 8.31% | 8.49% | 6.02% | 6.27% |
| Mar 2026 | 3.18% | 3.32% | 7.15% | 7.33% | 5.49% | 5.75% |
| Apr 2026 | 1.60% | 1.79% | 6.75% | 6.94% | 5.36% | 5.61% |

Reporting documents are linked in [the structured source table](../data/r9_lic_gsec_official_factsheet_anchors.csv).

LIC ETF has lagged the benchmark over each of these published trailing windows by approximately:
- 1Y trailing annualized return difference: **0.14–0.19 percentage point**.
- 3Y annualized return difference: **0.18–0.27 percentage point**.
- 5Y annualized return difference: **0.25–0.33 percentage point**.

These are historical **tracking differences**, not the standard deviation of tracking errors. Windows overlap heavily and are not 12 independent observations. The fund NAV includes the scheme's expense burden and tracking; ETF purchase/sale prices add market premium/discount and brokerage. The published index window returns are **not a contiguous monthly index history**.

The published-return file and independent arithmetic validation have been committed:
- [Official LIC factsheet return anchors](../data/r9_lic_gsec_official_factsheet_anchors.csv)
- [Independent reproduction script](../pipelines/r9_lic_gsec_factsheet_audit.py)
- [Results manifest — if workflow has produced it](../data/r9_lic_gsec_factsheet_bridge.json).

## 3. Controlled 11-year primary-AMFI product backfill — in verification

The new source qualifier [official AMFI historic acquisition and validation code](../pipelines/r9_lic_gsec_official_amfi_history.py) and [GitHub Actions workflow](../../../.github/workflows/stage512-r9-lic-gsec-history.yml) retrieve segmented official scheme-NAV observations for **2014-12-26 through 2026-10-30**.

Acceptance requires:
1. Named AMFI scheme identity and single matching growth-plan group; exact AMFI scheme code **133307**.
2. Positive, timestamped priced NAVs with no contradictions, duplicated dates, unexplained NAV jumps or excessive gaps.
3. Source SHA-256 provenance for every fetch segment; full input archived in Actions artifacts.
4. At least 2,500 priced observations spanning more than 11 years.
5. Matching published LIC **March 2026 1-, 3-, and 5-year NAV CAGRs**, with explicitly recorded tolerance and date-window assumptions.
6. A separate [129-month NSE published Nifty 500 TRI vs LIC G-Sec ETF NAV bridge](../pipelines/r9_nifty500_gsec_instrument_bridge.py), which is blocked until the AMFI NAV result passes.

**Qualification remains OPEN until a `PASS_OFFICIAL_NAV_11YR_RESEARCH_ONLY` manifest is committed.** A pending workflow is not evidence that the history passed. Neither the ETF's data nor LIC's published benchmark windows fully replace a primary NSE daily 8–13y government-security total-return series.

## 4. Modeling implications

- **Improve the interest-rate risk model:** once qualified, this is a real product's historic duration-sensitive NAV history covering some major historical regimes.
- **Do not splice it into direct sovereign bond cash flows:** ETF constantly rolls 8–13 year bonds; an individual 2036-maturity bond loses duration over time and has different coupon tax treatment.
- **No TER double charging:** NAV is after ongoing fund expenses; only external transaction costs and tax should be layered on an NAV-based return model.
- **Do not extrapolate the trailing index or ETF CAGR as the expected 2026–2036 return.** Yield curve, term premium, fund duration, index rebalancing, tracking, inflation and regime changes must be modeled.
- **Do not treat an 85% model hit as a guaranteed real ₹90 lakh floor.** No principal or purchasing-power floor is established by a gilt ETF.

## 5. Status

| Gate | Decision |
|---|---|
| Official scheme identification and index methodology | PASS |
| LIC published ETF-versus-index tracking comparison | PASS for 12 stated lookback snapshots |
| Official AMFI 2014–2026 complete NAV history | **PENDING LIVE QUALIFICATION** |
| Direct NSE 8–13yr government-security index monthly TR history | OPEN |
| Multiasset joint 2015–2025/2026 risk calibration | OPEN |
| 2036 investment authorization | **NO-GO** |

The R9 source discovery makes the bond evidence more attainable, but does not itself warrant promoting the entire Stage 5.12 system to GO.
