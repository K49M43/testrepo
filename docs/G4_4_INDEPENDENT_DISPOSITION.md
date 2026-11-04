# G4.4 — Independent policy audit and disposition

**As of:** 4 November 2026  
**Roadmap delivery G4:** PASS within the bounded policy-definition and database-adapter scope.  
**Investment decision Gate G4:** BLOCKED.  
**Investment authorization:** NO-GO.

## Scope audited

This audit covers the accepted G4.1 action-policy contract, G4.2 three-case set and zero-return cash control, and G4.3's G2 SQLite schema v1 adapter. It treats each allocation as a comparison hypothesis, not a recommendation or a feasible investment plan.

The audit independently recalculates the G4.1 and G4.2 canonical fingerprints, verifies their cross-reference, checks the immutable cashflow fixture hash, and recomputes all contribution totals using Decimal. It then runs the three policies through a temporary G2 database and independently reconciles each stored horizon total and sleeve allocation against the pinned cashflow and policy weights. Run keys are rebuilt from their manifests.

## Results

- Three predeclared, nonduplicate G4.2 policies pass: 65/20/10/5/0, 50/30/15/5/0, and 75/10/10/5/0 across equity/gilt-proxy/gold/silver/cash sleeves.
- All vectors sum exactly to 100%; initial, recurring, and step-up allocations match; negative cash/holdings and unknown asset references fail closed.
- The 10% SIP increase occurs after each block of exactly 12 contributions. The frozen gross cashflow totals reconcile to **₹8,981,227.380300000** at 120 payments and **₹9,110,914.503305000** at 122 payments. These are contribution arithmetic before any reserve decision, returns, tax, costs, or inflation; they are not portfolio wealth.
- Nine negative cases reject over-allocation, omitted cashflow, malformed/missing dates, a reserve falsely marked confirmed, duplicate-equivalent policies, invalid asset references, negative weights, and omitted allocation/cash weight.
- G2 schema v1 integration passes for all three cases. Each policy has a distinct run key; canonical policy and selected-case hashes and run identities reproduce independently.
- The reserve, actual dates, CPI anchor, drawdown tolerance, account/product constraints, outcome/exit semantics, and investor exit choice remain explicitly unknown or blocked. Net-of-tax reinvestment remains an analyst-proposed rule requiring investor confirmation. G3 terminal semantics and G5 product eligibility remain blocked.

## Disposition

The planned G4 work is complete for the bounded deliverable: a versioned, reproducible set of research policies with explicit unresolved decisions, run identity, and independent audit. That does **not** pass investment decision Gate G4. No return comparison, tax-real-wealth outcome, probability, ranking, security eligibility, suitability, or authorization follows from this closure.

The strongest counter-case is that none of the three weights is investor-confirmed, the reserve and actual dates remain unknown, and G3/G5 have not cleared their dependencies. Therefore the policies are comparison inputs only; their arithmetic says nothing about meeting either goal.

## Next dependency

Close G3 issue #18 by independently reviewing and accepting the already-check-green draft PR #19. G5's instrument/evidence register is the following planned work; it must verify point-in-time identifiers, availability, data convention, tax, fees, and execution, with G0/G3 dependencies explicit. Deterministic outcome comparison remains blocked until the accepted G3 outcome/exit semantics and required evidence are available.

## Evidence

- Machine audit: `research/stage512/2026-11-04/g4_independent_disposition_v1.json`
- Continuous Question & Challenge Engine: `research/stage512/2026-11-04/g4_qcsae_v1.json`
- Reproduction command: `python decision/audit_g4_independent_disposition.py`
- Workflow: `.github/workflows/g4-disposition-audit.yml`
