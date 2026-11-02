# 2036 Personal Investment Decision Program

**Purpose:** support a real Indian investor's decisions about deploying ₹42 lakh upfront and a planned 10%-annually-escalating monthly contribution program to meet an **after-tax, inflation-adjusted financial objective by 2036**.

This is **not an academic research repository or an investment SaaS/platform development project**. Existing code and historical analysis are supporting evidence. The required end product is a defensible, implementable investment decision, or a documented finding that the target is not achievable at acceptable risk.

**Current investor decision status: NO-GO — supporting data/model/tax/portfolio qualification incomplete.** No code or simulated outcome authorizes a trade.

## Start here — Codex
1. **[CODEX_START_HERE.md](CODEX_START_HERE.md)** — ready-to-paste task for Codex to continue directly in this repository; [tracked GitHub issue #3](https://github.com/K49M43/testrepo/issues/3).
2. **[AGENTS.md](AGENTS.md)** — repository-wide operating rules that Codex should follow.
3. **[Actual investment mandate](docs/INVESTMENT_DECISION_MANDATE_2036.md)** — investor objective, cashflows, real after-tax floor, constraints and assumptions.
4. **[Dated handoff and current blockers](docs/HANDOFF_STATUS_2026-11-02.md)** — R9 source qualification is complete within its documented research scope; remaining decision gates are listed.
5. **[Codex execution plan](docs/CODEX_EXECUTION_PLAN.md)** — P0 engineering and subsequent route to a portfolio decision.
6. **[Decision gates](docs/INVESTMENT_DECISION_GATES.md)** — when a finding or strategy may be promoted.
7. **[Evidence and model rules](docs/EVIDENCE_AND_MODEL_STANDARDS.md)** — source provenance, financial accuracy, audit and regression checks.
8. **[Required investor decision outputs](docs/DECISION_DELIVERABLES.md)** — investment memo, 10+ candidate screen, real after-tax feasibility and execution checklist.
9. **[Machine-readable mandate](config/investment_mandate_2036.json)** and **[decision log](docs/DECISION_LOG.md)**.

## Actual investor objective
- **Initial investment:** ₹42,00,000.
- **Planned SIP:** ₹25,000 monthly initially, escalating 10% every year; 120-month illustrative contribution schedule. No funding interruptions expected.
- **2036 goal:** at least **₹90 lakh after tax in 2026 purchasing power**, with **₹1 crore real** as stretch. The aspirational ~85% modeled floor probability is **not validated or guaranteed**. 2036 is the target year; complete liquidation in October is **not mandatory**.
- **Working assumptions:** 6% inflation scenario (not forecast), Indian resident using new income-tax regime and approximate 30% income marginal slab (not a universal investment tax rate), Groww, no reported outstanding liabilities, no need for investment income.
- **Financial report order:** gross nominal value → all applicable investor taxes/costs → net nominal value → inflation-adjusted real value → 2036 risk and decision.
- **Decision universe:** at least 10 serious tradeable candidates/strategies; include equity, direct sovereign bonds and rolling gilt alternatives, gold **and silver**, and defensive alternatives. Existing 65/20/10/5 is research-only.

## Current engineering status
- Historical Stage 5.12 work is indexed at **[research/stage512/2026-11-02/README.md](research/stage512/2026-11-02/README.md)**.
- R7 strictly aligned four-fund official AMFI NAV covariance is a **36-month historical statistic**, not a ten-year forecast.
- R8 NSE Nifty 500 TRI has 129 officially published monthly return crosschecks; bullion has 437 consecutive monthly RBI-origin prices from a secondary mirror with sampled RBI matches.
- R9 LIC 8–13y G-Sec ETF AMFI history and the strict date-aligned ETF-proxy bridge passed within their stated research scope; neither is a direct-sovereign forecast or investment authorization.
- The next work is deterministic tax/real-wealth accounting, with timing and CPI-anchor limits recorded in **[CODEX_START_HERE.md](CODEX_START_HERE.md)**.
- The initial TY 2026–27 instrument tax-rule map is in **[decision/tax_rules_asof.md](decision/tax_rules_asof.md)**. It is a model specification only; lot-level tax calculations and real-wealth outputs remain unqualified. The current authorization remains **NO-GO**.

## Safety and privacy
This repository was **public** at the Codex handoff. The investment mandate and scenario amounts are visible publicly. **Make the repository private before uploading personally identifying financial records**, account data, trading credentials, investment statements or sensitive tax files. Do not perform investment orders automatically.

Model results are decision-support estimates with uncertainty, not guaranteed investment returns or capital protection.
