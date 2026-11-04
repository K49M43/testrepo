# G4.4 — Independent policy audit and bounded disposition

**Current audit:** PASS for roadmap delivery G4.1–G4.3 within the scope below  
**Investment decision Gate G4:** BLOCKED  
**Investment authorization:** NO-GO

## Audited scope

G4.4 independently validates the superseding G4.1/G4.2 v1.1 contracts, the three predeclared research allocations, the 120/122 contribution arithmetic controls, and G4.3's integration with the accepted G2 SQLite schema v1. The original G4.1/G4.2 v1.0 files remain historical snapshots.

The audit checks accepted G2 and G3 versions, normalized source hashes, and merge commits. G3 outcome and terminal semantics are accepted and pinned to G3 v1.0.0. The investor's terminal date and exit/access choice remain unresolved; liquidation is not inferred. G5 product eligibility, reserve, actual funding dates, account constraints, drawdown tolerance, and investor policy confirmations remain open.

## Independent controls and results

- Three allocations pass exact Decimal weight and conservation checks: 65/20/10/5/0, 50/30/15/5/0, and 75/10/10/5/0 across equity/gilt-proxy/gold/silver/cash.
- Numeric duplicate allocations are detected after Decimal parsing, including equivalent values written with different trailing-zero precision.
- The 10% contribution increase follows each block of exactly 12 contributions. Gross contribution totals reconcile to **₹8,981,227.380300000** at 120 payments and **₹9,110,914.503305000** at 122 payments. These are before reserve, returns, taxes, costs, and inflation; they are not portfolio wealth.
- Nine malformed or unsafe negative cases reject. The audit independently reconstructs each database run key from its manifest using its own canonical JSON/SHA-256 calculation, and validates accepted G2/G3 identities in the run context. It does not publish ephemeral run keys in the stable evidence artifact.
- CI's `--check` mode compares the committed evidence byte-for-byte with a fresh audit result, preventing stale evidence from passing just because the audit script exits successfully.

## Disposition

G4 roadmap delivery is complete for bounded policy definition and G2 integration. This does not pass investment decision Gate G4 and does not establish returns, taxes, fees, real purchasing power, portfolio risk, probability, ranking, suitability, security eligibility, or authorization. The allocation cases remain research comparisons only.

## Next work

G3 is no longer a pending dependency. Continue with the planned G5 instrument and evidence qualification, including point-in-time security identity, availability, data convention, tax, fees, and execution checks. Keep investor-specific dates, reserve, policy choices, account constraints, and drawdown tolerance unresolved until confirmed. Deterministic investment outcome comparisons remain gated on qualified G5 evidence and required investor inputs.

## Evidence

- Machine audit: `research/stage512/2026-11-04/g4_independent_disposition_v1.json`
- Continuous Question & Challenge Engine: `research/stage512/2026-11-04/g4_qcsae_v1.json`
- Regenerate evidence: `python decision/audit_g4_independent_disposition.py --write`
- Verify committed evidence: `python decision/audit_g4_independent_disposition.py --check`
- Workflow: `.github/workflows/g4-disposition-audit.yml`
