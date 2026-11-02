# 2036 Investment Research — Stage 5.12 audit archive (2 November 2026)

**Status: RESEARCH ONLY — INVESTMENT NO-GO.** This archive contains scenario models, historical-proxy analysis, calibration reports, source-reconciliation work, and preliminary validation. Neither an 85% real-world success probability nor a contractual inflation-adjusted ₹90 lakh floor has been established.

## Scope and conventions
- Historical mandate: ₹42 lakh upfront; ₹25,000 monthly SIP increasing 10% annually; flexible target year 2036.
- Reporting: gross nominal wealth → taxes and costs → net nominal wealth → real after-tax wealth → floor/target success analysis.
- Endpoints and inflation vary by experiment. Do **not** compare simulations without reconciling assumptions and dates.
- 6% is a planning inflation scenario, **not** a forecast or CPI guarantee.
- Historical data proxies (especially bond and bullion returns) must not be represented as verified scheme-level NAV returns.
- The prior third-party CPI history was challenged and superseded by a reconstructed official-linked historical series, which retains explicit source/provisional flags.
- Statistical tests challenged a Gaussian-only downside model; the Student-t variant is a research challenger rather than a qualified 2036 probability forecast.

## Reports in chronological research order
1. [Blocker resolution](stage512_blocker_resolution_report.md)
2. [Independent historical calibration](stage512_independent_calibration_report.md)
3. [Forward-looking scenario calibration](stage512_forward_calibration_report.md)
4. [Model and parameter uncertainty](stage512_model_uncertainty_report.md)
5. [Predictive-validation audit](stage512_predictive_validation_report.md)
6. [Tail validation and source gates](stage512_validation_resolution_v2.md)
7. [Official CPI and market-source reconciliation](stage512_source_resolution_report.md)

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
