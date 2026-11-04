# G5.1 — 11.8% claim lineage and correction

**Date:** 5 November 2026  
**Disposition:** PASS for correcting the label and preserving the dependency lineage. The 11.8% input remains unverified; the scenario remains quarantined from investment-decision evidence. Investment authorization remains **NO-GO**.

## Finding

The former “Historical 11.8% replay” case did not replay historical returns. `stage512_risk_audit.py` assigns `0.118` as a fixed geometric equity-return assumption and generates monthly shocks from a seeded normal distribution. It does not load a dated Nifty 500 total-return series. The run contains 25,000 synthetic paths, 122 monthly steps, seed `20261102`, hypothetical asset means/volatilities/correlations, and simplified tax mechanics. Its path hit rates describe this model only.

The case and all six dependent outputs (three illustrative allocations × two horizons) now identify the case as a synthetic assumption, flag its provenance as unverified, and carry a machine-readable `QUARANTINED_NOT_FOR_INVESTMENT_DECISION` status plus a direct link to this lineage record. The numeric results were intentionally retained for traceability, compared to the pinned pre-correction rows, reproduced in a separately stored rerun, and quarantined. They must not be presented as historical performance, an empirical probability, forecast, or investment support.

## Source and coverage audit

The 2 November report cited a live third-party page but preserved neither a source snapshot nor the exact calculation endpoint supporting 11.8%. The value is therefore **UNVERIFIED**. The live Tipsheet page observed on 3 November 2026 reports 11.9% annualized since 1995; it is not the missing 2 November snapshot. NSE Indices' October 2025 whitepaper reports 12.39% annualized for the Nifty 500 TR Index from 1 January 1995 to 30 September 2025. Because the source, value and end dates differ, that official figure does not authenticate the exact 11.8% input.

The repository's official-published NSE monthly anchor panel has 129 observations from January 2015 through September 2025. Its validation explicitly says a complete official daily history and a full 2036 probability are not qualified. The anchors do not establish a since-1995 return path and do not feed the 11.8% simulation.

Sources: [NSE Indices October 2025 Nifty 500 whitepaper](https://www.niftyindices.com/docs/default-source/indices/nifty-500/nifty-500-whitepaper_2025.pdf?sfvrsn=7b2c6635_4); [Tipsheet Nifty 500 page](https://tipsheet.markets/indices/nifty-500/).

## Correction and reproducibility

The active scenario label now reads “Synthetic 11.8% equity geometric-return assumption.” Scenario outputs include classification and input-provenance fields. The runner requires a separate `--output-dir` to prevent accidental replacement of the dated baseline. The preserved rerun is under `research/stage512/2026-11-05/g5_1_118_assumption_rerun/`.

Reproduce with Python 3.13 and NumPy 2.3.2. The CI audit extracts the original four input artifacts from base commit `765b4c84cc006c98dd374b49b9dd324f82187123`, verifies their normalized SHA-256 hashes, regenerates the simulation into a fresh directory, and compares the six corrected result rows against the original and fresh outputs. The same audit scans repository text for the former claim outside this correction record.

```powershell
python -m pip install numpy==2.3.2
python research/stage512/2026-11-02/stage512_risk_audit.py --output-dir <fresh-output-directory>
python decision/audit_g5_1_claim_lineage.py --check --baseline-dir <pinned-baseline-directory> --reproduced-dir <fresh-output-directory>
```

The machine-readable lineage record stores verified pre-correction SHA-256 fingerprints, current artifact fingerprints, baseline main commit, source assessment, model trace, affected outputs, exact baseline comparison, and rerun status. `--write` regenerates that record; CI uses `--check` to enforce it.

## Limits and downstream use

G5.1 closes only the mislabeled-claim correction. It does not validate the 11.8% return, calibrate forward distributions, qualify candidate instruments, or establish success probabilities. The original numeric outputs remain unsuitable for candidate ranking or authorization. G5.2 must qualify actual candidate products and point-in-time evidence, including holdings coverage and look-through; G5.3 independently audits the evidence and resulting register. The portfolio decision remains **NO-GO** pending all applicable gates.
