# Codex Operating Instructions — 2036 Personal Investment Decision

**Read this file first.** These instructions apply throughout the repository, including all nested folders, unless a more specific `AGENTS.md` explicitly adds compatible constraints.

## Mission and decision owner
This repository supports an **actual Indian resident's investment decisions involving real money**, not a research publication, generic financial software product, or SaaS platform. The system's outcome is a traceable, appropriately risk-qualified, **implementable 2036 investment decision**. Engineering and research are tools to reach that outcome.

**Do not trade, place orders, access Groww credentials, move money, or assert investor authorization.** Only the investor may approve and execute any transaction after reviewing current prices, product suitability, taxes, and the final decision memo.

Read these authoritative files in order:
1. [Decision mandate](docs/INVESTMENT_DECISION_MANDATE_2036.md) — real investor facts, goals and constraints.
2. [Current state and evidence](docs/HANDOFF_STATUS_2026-11-02.md) — verified accomplishments, current NO-GO, evidence paths, active blockers.
3. [First Codex assignment and milestones](docs/CODEX_EXECUTION_PLAN.md) — work to perform immediately.
4. [Evidence and computational controls](docs/EVIDENCE_AND_MODEL_STANDARDS.md) — reproducibility and financial calculations.
5. [Decision and acceptance gates](docs/INVESTMENT_DECISION_GATES.md) — conditions for any recommendation.
6. [Deliverables and handoff format](docs/DECISION_DELIVERABLES.md).

The JSON configuration [investment_mandate_2036.json](config/investment_mandate_2036.json) is machine-readable, but the written mandate governs conflicts. Do not invent defaults for fields explicitly marked `unconfirmed`.

## Behavioral rules
- **Goal-oriented:** prioritize reducing uncertainty that could materially change the actual portfolio decision. Do not expand into platform-building, UI, SaaS, multiuser infrastructure, or unrelated features.
- **Truth over GO:** fail closed on unverified source series, inconsistent time conventions, underestimated downside risk, unexplained data adjustments, and missing taxes. Never modify assumptions to produce the desired outcome.
- **Audit independently:** review existing code, reports, schemas and historical decisions as though encountering them for the first time. A previous PASS proves only the exact gate recorded, not all adjacent claims.
- **Make the next concrete change:** inspect files, reproduce existing tests, identify a current blocking failure, implement/tests/commit a correction, then report actual measured status. Avoid generating more plans in place of execution.
- **Preserve source distinction:** official NSE TRI ≠ price index; government-security total-return index ≠ clean-price index; actual AMFI fund NAV ≠ tradeable ETF price; RBI Mumbai monthly bullion average ≠ ETF month-end NAV; bond fund ≠ held-to-maturity GoI sovereign bond; linked CPI ≠ nominal expected inflation.
- **Official and reproducible:** maintain raw source URL, timestamps, byte hashes, index identity, date alignment, rounding, rate-limit handling and first-party checks. Never fabricate observations, return paths, probabilities, prices or booking/trading availability.
- **Observe service limits:** respect AMFI HTTP 429 and access restrictions; use sequential, bounded, cached requests and lawful published exports. Do not bypass CAPTCHA, site protection, or API terms.
- **Validate money math:** model initial ₹42 lakh, specified escalating SIPs, cashflow timing, actual investor taxation, fees, lot-level holding periods, reinvestment, and inflation. Report gross nominal → taxes/fees → net nominal → real purchasing power; also provide appropriately timed money-weighted returns and shortfall risk.
- **Test out-of-sample and adverse cases:** historical and recent covariance/regime variation, fat tails, parameter uncertainty, sequence risk, tax/regulatory sensitivity, liquidity/ETF premium, and near-2036 forced vs flexible liquidation.
- **Don't conflate targets and guarantees:** ₹90 lakh real after-tax floor is an investor objective, not a protected capital guarantee; approximately 85% modeled floor success is aspirational, not established; a model PASS does not authorize trading.
- **No cherry-picking:** evaluate at least 10 materially different eligible investable candidates/strategies where appropriate; include gold **and silver**, government securities including direct sovereign bonds, and alternative risk controls. Document why each candidate survives or fails.
- **Public repository caution:** never commit identity, account numbers, statements, broker exports with personally identifying data, trade credentials, or API secrets. Financial amounts and tax assumptions are present because they are required to reproduce the stated mandate; propose a private repository for sensitive extensions.
- **Do not assume a past obligation exists:** investor explicitly reports no outstanding liabilities and no need for current investment income; do not invent home-loan repayments or liquidity needs.
- **Question only consequential unknowns:** work ahead on evidence collection and computation; identify material investor confirmations (risk tolerance, desired terminal date, future tax details, implementation suitability) for final signoff, without repeatedly asking known questions.

## Working convention
- Make targeted Git commits with understandable messages. Prefer feature branches/PRs for material financial logic; never silently rewrite accepted reports or source data.
- Keep a dated decision log, evidence manifest, clear experiment ID, code version, dependencies, random seeds and rerun instructions.
- On each response to the investor report: **what was executed**, test/source evidence, what changed quantitatively, remaining blockers, decision implication, code/PR link. Do not describe intended work as completed.
- If external access fails, commit a failure manifest and a bounded remediation route; don't label a download or parser test a full-history statistical validation.
- No irreversible real-money actions without explicit investor instruction and confirmation.

## Start now
Open [docs/CODEX_EXECUTION_PLAN.md](docs/CODEX_EXECUTION_PLAN.md) and execute **P0 / Task 1** against the current GitHub code and test evidence. Continue toward an actual decision memo; do not wait for further prompts when safe engineering work can proceed.
