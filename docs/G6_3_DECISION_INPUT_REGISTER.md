# G6.3 Decision Input Register

**As of:** 6 November 2026  
**Controlling source:** `docs/INVESTMENT_DECISION_MANDATE_2036.md`; this register classifies its statements but does not amend them.  
**Purpose:** keep unknowns visible while source qualification and model audits proceed. No default is added for a mandate field marked unconfirmed.

## Status definitions

- **CONFIRMED:** investor-declared in the controlling mandate; still requires current evidence when it describes a dynamic fact.
- **MODEL CONVENTION:** permitted for a bounded fixture or sensitivity only; not an investor instruction.
- **PROVISIONAL:** usable only with an explicit label and sensitivity; not decision-grade evidence.
- **ASPIRATIONAL:** a desired outcome or model target, not a requirement to manipulate assumptions toward.
- **INVESTOR CONFIRMATION REQUIRED:** material investor fact that must be answered before an exact personal allocation or trade plan.
- **EVIDENCE BLOCKED:** must be sourced or independently verified before the associated output can pass its gate.
- **UNKNOWN BY NATURE:** future state cannot be known now; compare explicit scenarios rather than inventing a point value.

## Decision and funding inputs

| Input | Current value/status | Permitted use now | Resolution / owner |
|---|---|---|---|
| Decision objective | **CONFIRMED:** long-term wealth creation for a 2036 Indian investment decision; no current portfolio income required. | Governs candidate and outcome comparison. | Preserve in every G6 output. |
| Initial capital | **CONFIRMED:** ₹42,00,000. | Mandate input; do not treat as account-verified cash or authorize transfer. | Investor confirms availability at execution time. |
| Monthly contribution | **CONFIRMED amount:** ₹25,000 initially; **10% annual step-up** after every 12 contributions. | Model the stated schedule. | Keep dates and payment convention separate from these confirmed amounts. |
| Funding continuity | **CONFIRMED as investor expectation:** no expected interruption or funding insufficiency. | Baseline assumes continuous funding; interruption is a labeled sensitivity only. | Reconfirm if circumstances change. |
| Liabilities and income need | **CONFIRMED:** investor reports no outstanding liabilities and no need for current investment income. | Do not invent debt repayment or withdrawal requirements; distributions should be reinvested net of applicable tax in a modeled strategy. | Reconfirm only if facts change. |
| Initial investment month | **INVESTOR CONFIRMATION REQUIRED.** | Use dated fixture conventions only; do not report exact personal XIRR or dated wealth. | Investor, before personal result/final plan. |
| First SIP month and payment day | **INVESTOR CONFIRMATION REQUIRED.** End-of-month is only the mandate's pending model convention. | Continue source and formula work; label any dated illustration. | Investor, before exact personal cashflow result. |
| Payment count | **MODEL CONVENTION:** 120 payments is illustrative. The 122-payment path is a sensitivity, not a confirmed funding instruction. | Preserve both as separate schedules; never combine them silently. | Final schedule depends on confirmed initial/SIP dates and chosen 2036 endpoint. |
| 2036 measurement/withdrawal dates | **INVESTOR CONFIRMATION REQUIRED.** Mandate requires alternate 2036 month-ends, partial liquidation, and flexible exits rather than an assumed October-only forced sale. | Analyze the prescribed exit-policy sensitivities once the data and event model pass. | Investor selects the objective date/policy before final allocation. |

## Objectives, risk, tax and access

| Input | Current value/status | Permitted use now | Resolution / owner |
|---|---|---|---|
| Real purchasing-power floor | **CONFIRMED objective:** ₹90,00,000 in 2026 purchasing power by 2036. It is not a guarantee. | Report as the floor objective, distinct from nominal terminal wealth. | Retain; any change requires investor instruction. |
| Stretch objective | **CONFIRMED objective:** ₹1,00,00,000 in 2026 purchasing power. | Report separately from the floor. | Retain; do not use it to replace the floor. |
| Approximate success aspiration | **ASPIRATIONAL / UNVALIDATED:** about 85% modeled chance of meeting the floor. | Research target only; no claim until calibration and uncertainty gates pass. | G6 model validation and independent review; investor suitability is separate. |
| Risk tolerance | **INVESTOR CONFIRMATION REQUIRED:** specific tolerable interim drawdown/loss is not stated. | Show risk distributions and downside without declaring a portfolio suitable. | Investor before recommendation. |
| Residence and tax regime | **CONFIRMED at mandate level:** Indian resident taxpayer; currently new regime; approximate 30% marginal ordinary-income slab. | Source applicable law by instrument/date/event. Do not apply 30% universally to capital gains. | Taxable-income details and final status require investor confirmation before personal tax result. |
| Future tax rules | **UNKNOWN BY NATURE.** | Run explicit tax-policy scenarios; repeat current law only as a clearly labeled sensitivity, never as known 2036 law. | Refresh near decision/implementation dates. |
| Broker/platform | **CONFIRMED as stated route:** Groww. Specific instrument access, route, quantity, charges and operational eligibility are **EVIDENCE BLOCKED**. | Public product/source research only; no credentials or account access. | Verify current product-level evidence; investor confirms account/product constraints. |

## Source and model inputs

| Input | Current value/status | Permitted use now | Resolution / owner |
|---|---|---|---|
| CPI planning rate | **PROVISIONAL scenario:** 6% annually; not a forecast. | Sensitivity only; distinguish from realized CPI. | Replace/compare with the qualified linked official index and stress cases. |
| CPI series and base month | **EVIDENCE BLOCKED / INVESTOR CONFIRMATION REQUIRED.** Existing 165 linked/direct observations are transcribed and mechanically checked, but original release bytes are absent and the 2026 purchasing-power base date is not fixed. The mandate historically refers to October 2026, which still needs explicit confirmation and source support. | Provisional deflator only; no final personal real-wealth claim. | Preserve original official MoSPI release/linking evidence and hashes; investor confirms valuation/base month. |
| Candidate universe | G5 has a ten-hypothesis screen, five declared-window AMFI Growth NAV histories, holdings snapshots and bounded exit evidence. The separately reconciled LIC scheme 133307 history has 2,867 official AMFI NAV observations (2014-12-26–2026-10-30), but is a fund proxy rather than ETF traded-price or G-Sec total-return evidence. **Tradeability, full candidate-specific histories, tax, current costs and suitability are not universally qualified.** | Screen and classify; a hypothesis is not an eligible recommendation. | WP1 qualifies or rejects candidates with evidence; include direct GoI, broad equity, gold and silver as mandated. |
| Return identity | **EVIDENCE GATE:** NSE TRI, scheme NAV, ETF market price, government-security total return, direct sovereign cashflows and bullion benchmarks are distinct. | Use only the correct series for each strategy; retain inception and coverage limits. | WP1 source audit; never splice or backfill pre-inception periods. |
| Product costs/distributions | **EVIDENCE BLOCKED by candidate:** TER/tracking difference, market spread/premium, liquidity, coupons/distributions, withholding and reinvestment need product/date evidence. | Existing costs in G6.1/G6.2 are synthetic fixtures only. | WP2 event-level integration after WP1 sources pass. |
| Exit and portfolio policy | **PARTLY SPECIFIED:** long-term accumulation and no income withdrawals; rebalancing, partial liquidation, exact 2036 month and operational constraints remain to be specified or compared. | Explicit, versioned alternatives only; do not imply a policy was selected. | Define candidate strategies and exit cases under G6.3; investor confirms preferred endpoint/risk policy. |

## Gate 0 disposition

Source qualification, independent arithmetic audits, and bounded strategy research can proceed with these statuses. Do not block that work while investor confirmations are open. Exact investor-specific after-tax/real wealth, final suitability, a precise allocation, and GO/CONDITIONAL GO remain blocked until their required inputs and evidence pass. G6.1/G6.2 results remain synthetic mechanics checks and are not inputs to a decision-grade outcome distribution.