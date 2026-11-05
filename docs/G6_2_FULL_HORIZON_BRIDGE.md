# G6.2 — Full-horizon synthetic deterministic bridge

**Status:** implemented in draft [PR #43](https://github.com/K49M43/testrepo/pull/43), tracked by [issue #42](https://github.com/K49M43/testrepo/issues/42), on stacked branch `codex/g6-2-full-horizon-synthetic-bridge-20261105`. It depends on G6.1 draft PR #41 and must be reviewed after that parent is accepted. Exact-head checks are shown on PR #43.

## Objective and scope

Run the frozen G3 contribution schedule through the existing event/lot/tax ledger for both horizons: 120 recurring monthly contributions plus the initial month-0 investment (121 lots), and the 122-month sensitivity plus initial investment (123 lots). Each lot is acquired at a generated monthly synthetic mark and liquidated at the horizon's terminal mark.

Four deterministic cases combine two horizons with two mark paths: flat marks and a synthetic +0.3% monthly mark increase. Both are arbitrary mechanics fixtures, not return estimates. A synthetic account fee is deducted before units are acquired; a separate terminal cost is charged at sale. The synthetic CPI path applies 6% annual compound inflation from the G3 base month. These assumptions exist to test integration and are not forecasts.

## Multi-year tax boundary

The schedule spans eleven Indian tax years (2026–27 through 2036–37). The fixture explicitly supplies a resident-individual flag and synthetic ₹15 lakh ordinary income for every tax year. The bounded TY 2026–27 tax component is repeated in later years only to exercise the annual tax interface and terminal-year incremental tax plumbing. It is not a statement of 2036 law or a personal tax result. External tax is context only; only incremental synthetic portfolio tax is deducted from fixture portfolio wealth.

The independent tax check separately computes section 516 rounding, ordinary-rate slab tax and cess within the fixture's explicit income envelope. It fails outside the supported band. It does not independently validate the full statute. Losses fail closed under the existing loss schedule; distributions, reinvestment, flexible exits, product-specific costs and future tax rule changes are outside this increment.

## Measured fixture outputs

Amounts below are deterministic synthetic values. “After cost, pre-tax” includes the terminal sale cost; account fees already reduce invested principal and are reported separately, so they are not subtracted a second time.

| Horizon and mark path | Contributions | Gross terminal proceeds | Account fees / exit cost | Incremental fixture tax | Net nominal | Net real at synthetic CPI |
|---|---:|---:|---:|---:|---:|---:|
| 120 months, flat | ₹89,81,227.38 | ₹89,80,017.38 | ₹1,210 / ₹25 | ₹0.00 | ₹89,79,992.38 | ₹50,14,380.84 |
| 120 months, +0.3% monthly | ₹89,81,227.38 | ₹1,16,01,422.93 | ₹1,210 / ₹25 | ₹7,39,879.92 | ₹1,08,61,518.01 | ₹60,65,014.93 |
| 122 months, flat | ₹91,10,914.50 | ₹91,09,684.50 | ₹1,230 / ₹25 | ₹0.00 | ₹91,09,659.50 | ₹50,37,625.14 |
| 122 months, +0.3% monthly | ₹91,10,914.50 | ₹1,18,00,997.51 | ₹1,230 / ₹25 | ₹7,61,688.72 | ₹1,10,39,283.79 | ₹61,04,703.86 |

The ledger residual is at most ₹1e-12 (observed maximum magnitude 1e-42). Every scenario emits 121 or 123 complete acquisition/disposal lot records and traces all eleven tax years.

## Independent checks

The independent audit separately rebuilds the exact contribution totals, each monthly price mark, units, basis, disposal proceeds, costs, exit-year tax and CPI deflator. It independently maps each acquisition and disposal date to an Indian FY, including the March/April boundary, confirms that only the terminal year has incremental portfolio tax, and checks all lots against tax-event traces within the ledger's ₹1e-12 arithmetic tolerance. The result manifest hashes the transitive capital-loss schedule module used by the loss-path gate. Thirteen mutation cases reject actual data through both loader and direct scenario entry points, unsupported horizons, missing/extra tax-year input, missing or nonresident assumptions, future-law promotion, wrong CPI base, invalid inflation, missing scenario growth, and unallocated loss paths.

Reproduce from repository root:

```powershell
python decision/g6_2_full_horizon_bridge.py
python decision/audit_g6_2_full_horizon_bridge.py
```

GitHub Actions reruns G6.2, G6.1 regression audits and the G5.4 decision-gate audit, then checks that committed artifacts remain current.

## Decision limits and next work

This is a full-horizon cashflow and deterministic integration test, not an investment result. It has no sourced asset returns, official CPI bytes, validated future tax law, portfolio selection, probability, recommendation or transaction authorization. G6 remains **NOT READY** and authorization remains **NO-GO**. Next, qualify candidate-specific historical price/return paths and actual product cost/tax treatment, then add distributions, reinvestment, applicable loss allocation and flexible exit rules before any uncertainty or probability work.
