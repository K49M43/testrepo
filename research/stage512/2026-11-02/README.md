# 2036 Investment Decision — Stage 5.12 Evidence Archive (2 November 2026)

> **Program purpose updated:** This directory is historical research evidence supporting an **actual personal investment decision**, not the final deliverable or a separate research platform. Follow repository [AGENTS.md](../../../AGENTS.md), [investor mandate](../../../docs/INVESTMENT_DECISION_MANDATE_2036.md), [Codex execution plan](../../../docs/CODEX_EXECUTION_PLAN.md) and [decision gates](../../../docs/INVESTMENT_DECISION_GATES.md). Current status remains investment NO-GO. Historic code-test/source PASS statuses do not authorize purchases.

**Status: RESEARCH ONLY — INVESTMENT NO-GO.** This archive contains scenario models, historical-proxy analysis, calibration reports, source-reconciliation work, and preliminary validation. Neither an 85% real-world success probability nor a contractual inflation-adjusted ₹90 lakh floor has been established.

**G5.1 evidence correction:** The former 11.8% scenario is now classified as a synthetic fixed-return assumption, not a historical path replay. The 2 November numeric results are unchanged and quarantined from decision evidence; see the [G5.1 lineage and correction report](../2026-11-05/G5_1_118_CLAIM_LINEAGE.md) and [machine-readable dependency map](../2026-11-05/g5_1_118_claim_lineage_v1.json) before using the blocker report, assumption register, or scenario CSV.

## Scope and conventions
- Historical mandate: ₹42 lakh upfront; ₹25,000 monthly SIP increasing 10% annually; flexible target year 2036.
- Reporting: gross nominal wealth → taxes and costs → net nominal wealth → real after-tax wealth → floor/target success analysis.
- Endpoints and inflation vary by experiment. Do **not** compare simulations without reconciling assumptions and dates.
- 6% is a planning inflation scenario, **not** a forecast or CPI guarantee.
- Historical data proxies (especially bond and bullion returns) must not be represented as verified scheme-level NAV returns.
- The prior third-party CPI history was challenged and superseded by a reconstructed official-linked historical series, which retains explicit source/provisional flags.
- Statistical tests challenged a Gaussian-only downside model; the Student-t variant is a research challenger rather than a qualified 2036 probability forecast.

## G5 instrument evidence

- [G5.2 point-in-time candidate/evidence register](../2026-11-05/G5_2_CANDIDATE_EVIDENCE_REGISTER.md) and [machine-readable candidate records](../2026-11-05/g5_2_candidate_evidence_register_v1.json).
- [Dated holdings, NAV reconciliation, concentration and same-date holdings overlap](../2026-11-05/g5_2_holdings_overlap_v1.json); raw official AMC workbooks/factsheets are in `../2026-11-05/source_raw/`.
- [G5.2 QCSAE](../2026-11-05/g5_2_qcsae_v1.json), [audit script](../../../decision/audit_g5_2_candidate_register.py), and [GitHub Actions workflow](../../../.github/workflows/g5-2-candidate-register.yml).

## Reports in chronological research order
1. [Blocker resolution](stage512_blocker_resolution_report.md)
2. [Independent historical calibration](stage512_independent_calibration_report.md)
3. [Forward-looking scenario calibration](stage512_forward_calibration_report.md)
4. [Model and parameter uncertainty](stage512_model_uncertainty_report.md)
5. [Predictive-validation audit](stage512_predictive_validation_report.md)
6. [Tail validation and source gates](stage512_validation_resolution_v2.md)
7. [Official CPI and market-source reconciliation](stage512_source_resolution_report.md)
8. [Stage 5.12 R4: recover Stage 5.8 official AMFI evidence and source-quality gate](stage512_source_reuse_audit_R4.md)
9. [R5: verified live AMFI ingestion and four-sleeve qualification contract](stage512_official_source_qualification_R5.md)
10. [R6: independently reproduced actual-fund 36-month covariance and source limits](stage512_instrument_nav_covariance_R6.md)
11. [R7: fully sourced four-fund NAV covariance, subperiod risk and the impossibility of ten-year simultaneous fund history](stage512_official_NAV_regime_horizon_R7.md)
12. [R8: two-layer benchmark evidence contract and official NSE TRI source-access audit](stage512_two_layer_benchmark_gate_R8.md)
13. [R8 source resolution: official NSE 129-month TRI checks and RBI bullion 437-month mirror with sampled primary checks](stage512_R8_benchmark_source_resolution.md)
14. [R9 government-bond long-history fund audit, LIC benchmark anchors and source gate](stage512_R9_gsec_long_history_source_audit.md)
15. [R9.3: corrected AMFI null-option and HTTP429 incident; six-month verified source windows](stage512_R93_AMFI_backfill_incident_resolution.md)

## Reproducibility artifacts
Scripts: `stage512_risk_audit.py`, `stage512_forward_calibration.py`, `stage512_model_uncertainty.py`, `stage512_predictive_validation.py`, `stage512_tail_validation_v2.py`, `stage512_import_gate.py`.

Structured results: `stage512_risk_scenarios.csv`, `stage512_empirical_sensitivity_results.csv`, `stage512_forward_calibration_scenarios.csv`, `stage512_model_uncertainty_results.csv`, `stage512_predictive_validation_key_metrics.csv`, `stage512_equity_return_grid.csv`, `stage512_bond_cashflow_example.csv`, `stage512_cpi_official_linked_2013_2026.csv`, `stage512_empirical_calibration.json`, `stage512_assumption_register.json`.

**Limitations:** This is a curated archive of 23 identified primary Stage 5.12 artifacts plus this index, not a representation that all intermediate files, datasets, historic Stage 4 and Stage 5 experiments or dependencies have been committed. Some scripts may require datasets and Python dependencies not stored in this archive. Do not regard numerical outputs as independently reproduced in the GitHub environment unless CI verification is added.

## Outstanding blockers
1. Obtain and reconcile NSE/AMFI investable index and actual fund returns, RBI domestic bullion prices, and complete official CPI history.
2. Repeat risk calibration and walk-forward tests with qualified data and tail/regime uncertainty.
3. Validate tax rules and realistic purchase/sale execution at specific candidate-security levels.
4. Reassess floor protection (probabilistic criterion distinct from a contractual guarantee).
5. Conduct investment committee review before any GO decision.

All report figures and modeled probabilities are research hypotheses, not guaranteed investor outcomes or an investment instruction.

## Official AMFI source pilot — November 2026
- [Primary-source retrieval script](../pipelines/amfi_source_pilot.py)
- [Offline parser contract tests](../tests/test_amfi_source_pilot.py)
- [Automated public-source acquisition workflow](../../../.github/workflows/stage512-amfi-primary-source-pilot.yml)
- [Pilot manifest (status may remain FAIL until corrected rerun)](../data/amfi_pilot/manifest.json)

**Important:** A successful ingestion pilot qualifies only the downloaded sample windows, not the full 10-year investable-product history or the investment decision. Prior Stage 5.8 official NAV spot-check results were recovered; see R4.

## Official historical NAV qualification results
- [Live official AMFI bulk-sample manifest](../data/amfi_pilot/manifest.json) — 75,706 valid priced NAVs across three windows, 1,105 zero-NAV exclusions, no unexplained parse rejects.
- [27 exact overlapping official NAV / ISIN crosschecks](../data/amfi_pilot/reconciliation_vs_stage58.csv).
- [Per-scheme official API probe manifest](../data/amfi_api_probe.json) — response and retrieval diagnostics; not itself qualified history.
- [Four-asset official historical NAV qualification source](../pipelines/amfi_four_sleeve_official.py) and [corresponding workflow](../../../.github/workflows/stage512-amfi-four-sleeve-qualify.yml).
- [Four-sleeve qualification manifest](../data/amfi_official_36m/qualification_manifest.json) — only if produced by the workflow; absence or FAIL means no promotion of investable-return estimates.

## R6 NAV covariance reproducibility
- [R6 reproducible NAV cross-asset correlation script](../pipelines/compare_stage58_covariance_R6.py)
- [Source-pinned 36-month covariance results](../data/nav_stage58_comparison_R6.json)
- **Provisional:** full official AMFI history remains required before replacing the model's benchmark proxy with scheme-level return probabilities.

## R7 validation artifacts
- [Four-fund official source qualification](../data/amfi_official_36m/qualification_manifest.json) — PASS_36M_COHORT_ONLY; not a forward 2036 probability.
- [Exact official AMFI NAV time series for four instruments](../data/amfi_official_36m/official_nav_four_assets.csv).
- [Independent R7 checker](../pipelines/independent_official_NAV_R7.py) and [CI diagnostics](../data/official_nav_R7_CI_diagnostics.json) (the latter exists only after workflow output is committed).
- [Machine-reproducible R7 result](../data/official_nav_independent_R7.json) — only qualified if produced with a passing CI record.

## R8 benchmark layer initial probe
- [NSE Nifty500 TRI official-site request script](../pipelines/nse_tri_source_probe_R8.py)
- [NSE official source access manifest](../data/nse_tri_source_probe_R8.json) — HTTP 200 but redirected HTML rather than TRI rows; this is **FAIL_UNQUALIFIED**, not a price-series approval.
- [NSE source CI probe](../../../.github/workflows/stage512-nse-tri-probe-R8.yml).

## R8 independently source-reconciled benchmark panels
- [Official NSE Nifty 500 TRI return matrix (129 months)](../data/nse500_official_tri_monthly_2015_2025q3_R8.csv)
- [Official TRI vs blob-pinned daily mirror CI acceptance manifest](../data/nse500_tri_validation_R8.json) — 129/129 within publication rounding.
- [RBI-origin bullion monthly history (437 months, **secondary mirror**)](../data/r8_rbi_origin_mirror/rbi_origin_mumbai_bullion_monthly_SECONDARY_MIRROR.csv)
- [Secondary source integrity record](../data/r8_rbi_origin_mirror/normalized_validation.json) and [seven-month official RBI publication cross-check](../data/r8_rbi_bullion_primary_spotcheck_manifest.json).
- [R8 detailed audit and remaining sovereign total-return index blocker](stage512_R8_benchmark_source_resolution.md).

## R9 government-bond index tracking evidence
- [LIC MF official 1/3/5-year ETF vs G-Sec benchmark performance](../data/r9_lic_gsec_official_factsheet_anchors.csv).
- [Published-return validation CI result](../data/r9_lic_gsec_factsheet_bridge.json) — 12 official lookback anchor pairs, not 12 independent trials.
- [AMFI 133307 historical backfill program](../pipelines/r9_lic_gsec_official_amfi_history.py) and [live qualification workflow](../../../.github/workflows/stage512-r9-lic-gsec-history.yml).
- [Official 2014–2026 NAV qualification manifest](../data/r9_lic_gsec_etf/qualification_manifest.json): promote only when `PASS_OFFICIAL_NAV_11YR_RESEARCH_ONLY` exists.
- [Conditional 129-month official Nifty 500 TRI and G-Sec ETF NAV risk bridge](../pipelines/r9_nifty500_gsec_instrument_bridge.py) and [workflow](../../../.github/workflows/stage512-r9-equity-bond-risk-bridge.yml).

## R9.3 staged evidence (2 November 2026)
- [Four era-specific official AMFI short-window source checks](../data/r9_lic_gsec_etf/short_window_probe.json) — **4/4 passed**, includes March 31, 2026 INR 28.4282 NAV matching LIC.
- [Four six-month official AMFI fetches](../data/r9_lic_gsec_etf/medium_window_probe.json) — **4/4 passed**, 477 priced observations in discontinuous samples.
- [Original 24-window source backfill manifest](../data/r9_lic_gsec_etf/qualification_manifest.json) — initial FAIL from handling null Option and AMFI HTTP429; supersede only when a later successful source qualification is committed.
- [Resumable, rate-limit-aware official AMFI source qualifier](../pipelines/r9_lic_gsec_official_amfi_history.py).
- [129-month official Nifty500 TRI date-only mirror anchors](../data/nse500_tri_month_end_dates_R9.csv) — independently sourced **dates**, not direct NSE daily price verification.
- [Strict date-aligned equity–bond ETF risk bridge](../pipelines/r9_nifty500_gsec_instrument_bridge.py); [bridge status manifest](../data/r9_nse_gsec_129m_source_bridge.json) is non-qualifying while full LIC data is unqualified.
- All R9 source, analysis and investing gates are **separate**. Full 2036 investment authorization remains **NO-GO**.
