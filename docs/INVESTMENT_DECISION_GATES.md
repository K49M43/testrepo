# 2036 Actual Investment Decision — Independent Acceptance Gates

**Principle:** Source gate, computation gate, forecast gate, portfolio gate, and investor authorization are **different**. The strongest previous source-level PASS is not a real-money investment GO. Default is **NO-GO / NOT YET EVALUATED** whenever a critical item is missing.

## G0 — Investor mandate and executable assumptions
PASS only when the written investment goal, cashflows, risk/liquidity preferences and tax status are explicit, versioned and consistent. Unconfirmed dates/drawdown tolerances can remain placeholders during engineering but must be resolved before an exact trade plan. The investor has reported no liabilities, no income need and no expected SIP interruption; do not invent adverse funding constraints.

## G1 — Instruments and qualified market data
Each candidate requires a stable identity (AMC/product, scheme ID/ISIN/security identifier), instrument class, eligible acquisition route, valuation/tradability, return convention, costs, tax treatment, history/inception, legal/credit structure and evidence timestamp.

- NSE Nifty500 **TRI** (dividends included), not price index;
- government-bond **total return**, not clean-price; direct GoI bonds separately modeled with yield/coupon/maturity/tax;
- AMFI scheme-level NAV after TER, with ETF market price distinct;
- RBI gold/silver Mumbai monthly averages not falsely treated as ETF month-end NAVs;
- linked MoSPI CPI with confirmed base/linking and complete source vintage;
- sources labeled as first-party, first-party-published sampled anchor, reconciled secondary mirror, hypothetical proxy, or rejected.

PASS when relevant data are complete enough for the proposed test, no unexplained gaps/outliers, correct units/dates, reproducing source checksums, independent anchors and source scope. Partial history may be acceptable for recent fund-tracking tests but **never** claimed to certify pre-inception years.

## G2 — Deterministic financial engine
PASS only if the cashflow, lot/tax, fee, inflation and XIRR engine satisfies independently written unit/property tests and reconciliations:
- at zero return and zero tax/cost, wealth equals initial capital plus contributions under consistent timing;
- no duplicated TER, coupon tax, transaction cost or inflation adjustment;
- no negative holdings/cash, impossible sales before purchases, or use of future observations;
- annual 10% SIP step occurs after precisely 12 contributions; date-resolved flow ledger;
- correct category-specific, vintage-specific Indian taxes; no global \`tax=30%\` shortcut;
- real wealth calculations use a *single anchored index* and published source linking;
- show gross nominal → after-tax nominal → real.
Tax tables/laws are sourced and date-stamped; unverified current taxation is a hard block for exact after-tax trade recommendation.

## G3 — Predictive uncertainty and stress acceptance
- Walk-forward / out-of-sample testing with leakage protection; record the score before selecting a model;
- both conventional and heavy-tail alternatives; consider skew, volatility regimes, crisis covariance, black-swan stress and uncertain inflation/tax;
- preserve equity, fixed income and gold/silver cross-asset risk, and **sequence-of-returns** impact with contributions;
- historical decade windows may overlap: effective independent sample count is small; never interpret 100 overlapping samples as 100 independent decades;
- use parameter uncertainty, bootstrap/blocks where appropriate, transparent yield/return assumptions, model risk and confidence bands; no invented chance of success;
- no hindsight fitting, no cherry-picked single scenario or best-possible tail model;
- a model that fits one short horizon does not validate 2036 goal probabilities.

G3 may PASS as a *conditional scenario engine* while **real-world probability claim remains unqualified**. Only publish probabilities with an explicit calibration claim and limitations.

## G4 — Real-world portfolio feasibility
- Evaluate **at least 10 credible securities/strategies** before narrowing;
- compare expected real wealth, floor likelihood (when supportable), expected shortfall/CVaR, worst-stress shortfall, drawdown, liquidity, interest-rate exposure, tax drag, tracking, diversification and implementation burden;
- test sensitivity to forward expected returns, covariance, inflation, tax changes, transaction spreads, entry and liquidation dates;
- verify current product identity, eligibility, availability through Groww or legitimate supported purchase route, minimum lots, fees, trading hours, market price/NAV differences, redemption and settlement;
- include direct government bonds, gold and silver rather than silently dropping them;
- assess whether investor objective is realistically achievable. A legitimate NO-GO may specify additional time, contributions, reduced target, reduced risk, or an alternative, without manipulating inputs.

## G5 — Independent decision review and investor confirmation
Only a **separately reviewed decision pack** with reproducible execution, up-to-date evidence, tax/suitability verification, remaining uncertainties and precise recommendation can be presented for approval.

The investor alone authorizes transactions. Until G0–G4 are sufficiently met and an independent challenge review supports the conclusion:
**Status = INVESTMENT NO-GO.**

## Gate ledger discipline
Every stage must write:
- \`gate_id\`, \`scope\`, \`status\` (PASS/FAIL/BLOCKED/PROVISIONAL), \`as_of\`, \`evidence_paths\`, \`tests\`, \`known_limitations\`, \`next_action\`, \`decision_implication\`.
- Do not modify gate criteria retroactively to obtain PASS; any revised acceptance condition requires rationale and recorded approval.
- Treat publication of a code file or initiation of GitHub Actions as **PENDING**, not PASS, until result outputs are verified.
- Keep failed results and root-cause records; append corrections rather than retroactive erasure.
