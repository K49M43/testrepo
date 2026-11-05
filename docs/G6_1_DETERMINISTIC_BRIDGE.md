# G6.1 — Fixture-first deterministic after-tax bridge

**Status:** implementation and local audits pass. PR #41 remains draft and unmerged; consult its live checks for current CI status. This is a first engineering increment, not decision-grade G6.

## Purpose

Connect three already-audited components through one reproducible path:

1. the dated cashflow schedule validated against the G3 outcome contract;
2. the Sprint 1 event/lot and bounded TY 2026–27 tax ledger; and
3. a CPI ratio that converts the resulting nominal value to a base-month value.

The adapter creates contribution, fee, acquisition, and terminal-disposal events. Every purchase is a separate lot, and all lots are liquidated at one explicitly synthetic terminal mark. The input fixture hashes itself together with the schedule, contract, bridge, ledger, tax, and G3 code into a deterministic run key.

## Bounded scope

- One synthetic specified-debt-fund tax branch, one Indian tax year (2026–27), six dated schedule rows from October 2026 through March 2027.
- Two deterministic mark paths: flat marks and a synthetic 1% monthly price rise.
- Explicit account fees, terminal transaction cost, synthetic external ordinary income of ₹30 lakh, an explicit synthetic resident-individual tax assumption, and synthetic CPI levels (100 to 102).
- Full forced liquidation, one-year tax calculation, event/lot trace, ledger residual, net nominal value, and net real value.
- No personal facts, sourced prices, official CPI, probability, candidate ranking, investment recommendation, or trade authority.

The terminal fee is explicitly non-deductible in this fixture; account fees are kept separate from tax basis. The synthetic tax input explicitly selects the resident-individual branch supported by the component. The independent audit separately recomputes section 516 rounding, ordinary-rate slabs, and cess only inside this fixture's income envelope (above the rebate threshold and at or below the surcharge threshold); it does not independently validate the full tax law. These conventions are mechanics inputs and must not be carried into a real product result without product-specific tax review.

## Measured fixture result

Each path uses ₹42,00,000 initial capital plus five scheduled ₹25,000 contributions (₹43,25,000 total contributions). Across six contributions, account fees total ₹60; terminal transaction cost is ₹25.

| Synthetic path | Gross terminal sale proceeds | Recorded fees | After-cost, pre-tax | Incremental fixture tax | Net nominal | Net real at synthetic CPI factor 1.02 |
|---|---:|---:|---:|---:|---:|---:|
| Flat price | ₹43,24,940.00 | ₹85.00 | ₹43,24,915.00 | ₹0.00 | ₹43,24,915.00 | ₹42,40,112.75 |
| 1% monthly price rise | ₹45,41,705.82 | ₹85.00 | ₹45,41,680.82 | ₹67,632.24 | ₹44,74,048.58 | ₹43,86,322.13 |

Both event ledgers reconcile with zero residual. The independent audit reproduces units, sale proceeds, costs, every lot disposal (including zero-gain lots), tax-event-to-lot mappings, the fixture-bounded tax increment using a separate slab/cess calculation, and CPI deflation. Mutations reject actual-data labels, non-synthetic price-basis labels, missing price marks, nonpositive CPI, missing external-income or residency assumptions, unsupported nonresident input, a cross-tax-year path, and an unallocated realized-loss path.

## Reproduction

```powershell
python decision/g6_deterministic_bridge.py
python decision/audit_g6_deterministic_bridge.py
```

The workflow reruns both commands and requires committed `result.json` and `audit.json` to remain current.

## What remains open

This does not model the complete 120/122-month horizon, a qualified product NAV/ETF market-price path, multiple asset classes, direct sovereign cashflows, distributions, rolling/flexible exits, transaction-cost schedules by product, investor-specific income/losses, actual CPI source bytes or a confirmed investor CPI base month. The loss mutation is deliberately blocked pending explicit G6 loss-allocation integration. Cross-asset uncertainty and probability remain unqualified. Investment authorization remains **NO-GO**.
