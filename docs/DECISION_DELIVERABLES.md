# Required Investor Decision Pack — Not an Academic Research Report

The final output is a **real-world investable 2036 portfolio decision**, with supporting auditable models. Use succinct investor-facing language and rigorous appendices.

## Primary artifact: decision/2036_DECISION_MEMO.md

Required sections in this order:

1. **Decision in 1 page.** Date, investor mandate, exact current gate status (GO/CONDITIONAL GO/NO-GO), what to do or not do, why, top risk and conditions for authorization. A scientifically calibrated model is not a guarantee.
2. **Goal and feasibility.** ₹42L plus dated escalating monthly contributions; total contributions and gross nominal wealth; all taxes and costs; **2026-real after-tax ₹90L floor** and ₹1Cr stretch by calendar year 2036; scenario inflation and dates; need for changes in goal, risk, contributions or deadline if necessary.
3. **10+ security/strategy universe.** Dated name, ISIN/scheme/security identifier, availability at Groww/legitimate route, asset type, duration/benchmark/credit, liquidity, fees, spread, tax treatment, official source, history quality, thesis and rejection reason.
4. **Ranked shortlist with alternative portfolios.** Include a conservative floor-seeking approach, a diversified baseline, a more growth-oriented approach, and the existing 65/20/10/5 as a **non-preferred candidate until tested**. Show why selection is rational and explicit exposure to silver and government bonds, including direct vs rolling fund differences.
5. **Actual money.** For each portfolio: entry rupees and percentages of ₹42L, SIP allocation/annual increases, rebalancing logic, fees/tax, expected distributions/interest handling, and whole-unit/lot rounding if implementable. Do not pretend index notional units equal ETF tradable market units.
6. **Decision distribution, not single expected return.** Model-based nominal, post-tax nominal and real end-2036 wealth; median/p10/p5 and severe adverse stress; \(P\)(real ≥ ₹90L), \(P\)(real ≥ ₹1Cr) only where justified, with uncertainty and important model disclaimers. Shortfall severity / expected shortfall, interim max drawdown and risk of needing money at a bad time.
7. **Tax and inflation calculations.** India-specific instrument- and lot-level tax, taxable coupons, reinvestment, exit taxes and fees, with tax law sources as of decision date. Explicit linked CPI anchor and inflation scenarios; 6% is not a fact.
8. **Execution checklist.** Security identity, Groww route, NAV vs market quote, spreads, creation/redemption/market hours, order type and sizing, fiscal/tax interactions and whether legal purchase is possible. No automated execution; investor confirmation required.
9. **Investment-risk challenge.** Inflation spike, 2008/2020-style shocks, equity–gilt correlation increase, gold/silver co-crash, silver tail volatility, bond duration shock/rising yields, issuer/instrument liquidity, ETF premiums, taxes/regulatory changes, plan funding and delayed terminal exit.
10. **Monitoring and change control.** Check cadence, drift/rebalance triggers, target probability/shortfall warning thresholds with caveats, source refresh schedule, exit planning nearer 2036, decision log and what new evidence would reverse the recommendation.
11. **Unresolved investor confirmations and approval box.** Exact contribution/terminal dates, risk tolerances, operational eligibility, tax/account details not already provided. Never imply the investor has signed off.

## Supporting artifact contract
- `decision/candidate_universe.csv` — 10+ instrument/strategy rows with source and screening status.
- `decision/portfolio_comparison.csv` — alternative portfolios and comparable output metrics with common assumption/date convention.
- `decision/decision_summary.json` — model version, as-of, status, central metrics, confidence/uncertainty designation, blocking gates.
- `decision/assumption_register.json` — every financial assumption, source/date, base/low/high scenarios, owner, qualification.
- `decision/source_manifest.json` — provenance & exact source scopes.
- `decision/tax_rules_asof.md` — verified Indian instrument-specific taxation by product and acquisition/realization vintage, primary citations.
- `decision/model_validation_report.md` — tests, calibration, failure modes, tail/regime robustness and independently reproduced checkpoints.
- `decision/execution_pretrade_checklist.md` — no passwords or automated brokerage access.
- `decision/decision_log.md` — prior and new NO-GO/CONDITIONAL/GO judgments with clear reasons and evidence.

The code may generate further files as needed, but do not spend investor time building a generic platform.

## Acceptance and communications
- Every deliverable states whether it is **verified historical**, **modeled scenario**, **tentative recommendation**, or **investor-approved action**.
- Cite exact live source or repository evidence paths; do not invent prices, metrics, instruments or executed investments.
- If enough evidence for a fully justified GO is unavailable, deliver a useful ranked *conditional* shortlist with specific blockers and a clear NO-GO, rather than an ungrounded GO or a never-ending research agenda.
- Independent reviewer actively tries to falsify the conclusion before investor-facing recommendation.
