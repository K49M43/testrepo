# Sprint 1 — Deterministic after-tax ledger

**Status:** In progress — Increment 0 input contract passed; Increment 1 CPI audit open
**Plan date:** 2 November 2026  
**Program status:** Investment authorization remains **NO-GO**.

## Sprint goal

Produce one reproducible, deterministic, event-by-event ledger for the mandate cashflows that separates gross nominal value, fees and taxes, net nominal value, and (only after the CPI source/base is qualified) real purchasing power. The first output is a model qualification fixture, not a return forecast, strategy recommendation, or investor tax estimate.

## Delivery style

Use an **incremental build with iterative review**. Each increment must produce a reviewable artifact and pass its own source, arithmetic, and data-contract checks before the next increment is added. Review findings feed back into the current increment; do not accumulate unreviewed assumptions until the end.

## Increments and checkpoints

| Increment | Deliverable | Acceptance checkpoint |
| --- | --- | --- |
| 0. Freeze the input contract | Dated cashflow/event schema; explicit source and assumption register; distinguish confirmed facts from unconfirmed dates, actual tax regime, security identity, and charges. Use the existing 120/122-month hurdle schedule only as a mathematical fixture. | Initial ₹42L and stepped SIP rows reconcile to `cashflow_hurdle_monthly_2026-10_base.csv`; no transaction rounding or payment date is silently invented. |
| 1. Qualify price and inflation inputs | Re-audit the official linked CPI vintage and recorded latest released month; document the index splice, observation date, units, raw source, and proposed purchasing-power base. Reconfirm exact asset-series identity and whether each price series is NAV, TRI, or a proxy. | An independent rerun reproduces every CPI observation used. If the investor’s actual base month is still unknown, publish a source-qualified provisional deflator but do not claim final real wealth. |
| 2. Implement current-law tax components | Add isolated TY 2026–27 functions using decimal arithmetic for section 202 ordinary slabs, eligible section 196/198 gains and thresholds, section 76 specified-fund treatment, coupon/distribution income, section 202 surcharge and marginal relief, cess, and withholding credits. Keep eligibility predicates explicit. | Boundary and worked examples reproduce `decision/tax_surcharge_examples_ty2026-27.md`; tests cover thresholds, surcharge caps, marginal relief, and cess. A qualified tax professional’s review remains a separate acceptance gate. |
| 3. Build the event and lot ledger | Represent contributions, lot acquisition/basis, units, transaction costs, coupons, distributions, reinvestment, withholding, and disposal/maturity as dated events. Aggregate taxable income by tax year; track lots through each disposal. | Cash in = cash out + ending holdings at each checkpoint; unrealized gains are not taxed as realized; coupons/distributions are counted once and withholding is a credit, not final tax. |
| 4. Reconcile terminal cases | Run deterministic 120- and 122-month cases and compare one-year liquidation, staged liquidation across tax years, and direct-bond maturity/coupon treatment against the applicable fund-redemption case. Use clearly labeled synthetic/fixture returns until candidate terms and dated market inputs are qualified. | Independent hand calculation reconciles one representative lot and one full tax year. Outputs reconcile gross nominal → fees/tax → net nominal; real results appear only when the CPI base is qualified and aligned. |

## Sprint definition of done

- Source manifest pins the legal rule version, CPI vintage, and every market/input series actually used.
- The 120/122 contribution schedules reconcile to the existing arithmetic baseline; all actual payment and terminal dates remain marked unconfirmed until supplied.
- Deterministic tests and a separate reconciliation reproduce the published surcharge examples and the selected event-ledger cases.
- Every tax line traces to a realized event, tax year, instrument classification, acquisition lot, and applicable rule; unknown eligibility fails closed.
- A qualified tax professional’s worked-example review is recorded. Until then, label tax outputs **provisional research calculations** and do not present an investor-specific after-tax result as qualified.
- If the released CPI anchor is not aligned with the investor’s actual contribution/base dates, report nominal outputs only and keep real purchasing-power claims open.
- Update the run manifest, decision log, handoff, and execution plan; create a focused PR and review its checks.
- Investment authorization remains **NO-GO** regardless of a passing model gate.

## Out of scope for Sprint 1

- Selecting or recommending an allocation; accessing brokerage credentials; placing trades.
- Treating the LIC G-Sec ETF proxy as a direct bond or as an official G-Sec total-return index.
- Forward return forecasts, Monte Carlo/bootstraps, portfolio optimization, probability-of-goal claims, or a final GO/NO-GO feasibility memo.
- Guessing the investor’s exact tax regime, other income/losses, transaction dates, security classifications, or broker charges.

## Dependencies and open inputs

- Latest released official CPI vintage and an investor-aligned base/measurement month.
- Security identifiers, listing and tax status, purchase/disposal dates, actual fees, and final exit choice.
- Investor tax-year income, losses, regime election, and other facts needed for a personal calculation.
- Independent tax-professional review of the statutory examples. No contact is authorized or implied by this plan.

## Sprint tracker

| Work item | Status | Evidence / next update |
| --- | --- | --- |
| Sprint plan | Active | Incremental delivery with iterative review; record changes in `docs/DECISION_LOG.md`. |
| Increment 0 input contract and cashflow reconciliation | **PASS** | `research/stage512/2026-11-02/after_tax_ledger_input_contract.json`; rerun `python research/stage512/2026-11-02/reconcile_after_tax_input_contract.py`. 123 rows reconcile across 120/122 months; dates and transaction rounding remain explicitly unconfirmed. |
| CPI vintage and anchor audit | In progress — mechanical audit PASS; source qualification open | `research/stage512/2026-11-02/audit_cpi_linked_series.py` reproduces 165 rows, 144 linked levels, 21 direct levels, and all stored monthly/YoY rates. MoSPI confirms an official 2013–2024 back-series is available on e-Sankhyiki, but original downloaded bytes and 2025–Sep 2026 observation-level source mapping are not yet pinned and reconciled. Investor base-month alignment also remains open. |
| Tax component implementation | Not started | Source map: `decision/tax_rules_asof.md`; arithmetic examples: `decision/tax_surcharge_examples_ty2026-27.md`. |
| Event/lot ledger | Not started | Existing baseline is pre-tax and pre-cost; do not treat it as an after-tax result. |
| Independent tax-professional review | Open dependency | No reviewer or sign-off recorded. |
