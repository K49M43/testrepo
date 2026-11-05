# Codex Execution Plan — Move from Evidence Pipeline to Actual 2036 Investment Decision



**Priority order matters.** Build the minimum decision-grade system needed to make a real investment decision, not a generalized research/portfolio SaaS.



## Current status — 5 November 2026



### Sprint 1 — closed for the bounded research and synthetic-fixture scope



The controlling close record is [Sprint 1 — Deterministic after-tax ledger](SPRINT_01_AFTER_TAX_LEDGER.md), closed 4 November 2026. Its bounded tax-component, loss-allocation, event/lot and 120/122-month cashflow checks pass; the source-based review against the enacted Income-tax Act was accepted for this research scope. The independent Decimal loss/tax reconciliation, event-ledger audit and input-contract audit were rerun from `main` during the G5.4 blocker investigation and passed. This does not establish an investor-specific tax result, actual transaction schedule, 2036 law, or final real-wealth outcome. Those facts remain explicit inputs, not Sprint 1 closure conditions.



### Current work — Sprint 6 / G6 deterministic integration

G5 is **CLOSED**. PR #39 merged on 5 November 2026 as `99c93aeee43b685ae43abcbbfffbc888f0803b9e`; issues #38 and #29 are closed. Its five official AMFI Growth-option NAV windows, 10-row product disposition, holdings snapshots, and eight-criterion exit audit are merged. These are bounded declared-window product histories, not proof of full-universe investability, long-run dependence, or probability.

G6.1 is tracked in [issue #40](https://github.com/K49M43/testrepo/issues/40) on draft PR [#41](https://github.com/K49M43/testrepo/pull/41), branch `codex/g6-1-deterministic-after-tax-bridge-20261105`. Its strengthened audit makes synthetic residency explicit, independently checks the fixture's ordinary slab/cess arithmetic, and reconciles every disposal lot including zero-gain lots. All workflows passed on implementation commit `36b3a7872eb8643436061ada20ae4c11ca4bcd5d`; PR #41 remains draft/unmerged.

G6.2 is tracked by [issue #42](https://github.com/K49M43/testrepo/issues/42) and draft [stacked PR #43](https://github.com/K49M43/testrepo/pull/43), based on PR #41. It implements the frozen 120-month and 122-month schedules with 121/123 synthetic lots, four deterministic full-liquidation cases, explicit inputs for eleven FYs, and a clearly non-statutory repeated TY 2026–27 fixture rule. The review findings were fixed: the direct scenario entry point now enforces synthetic provenance; FY assignment is independently reconstructed at each date; and the run manifest pins the transitive loss-schedule module. Local independent reconciliation and 13 fail-closed mutations pass; exact-head Actions are tracked on PR #43. This validates full-horizon plumbing only.

### Source and model status

- CPI: 165 contiguous linked/direct observations pass source-value checks (144/144 historical linked values and 21/21 direct values) plus mechanical continuity/link/rate checks. They remain source-linked transcriptions without original release bytes; the investor base month is unconfirmed. Use only as a provisional research deflator.
- Equity/bond/precious metals: five declared-window AMFI Growth NAV histories pass raw-to-normalized lineage (7,353 observations in 63 request windows). Strict month joins to rounded monthly NSE Nifty 500 TRI are descriptive only. Direct GoI/T-bill cashflows and relevant ETF market-price execution inputs remain blocked.
- Tax/cashflows: Sprint 1 bounded synthetic tax and event/lot fixtures pass. G6.1 links six dated contributions in a single tax year to explicit synthetic prices, costs, liquidation, incremental tax, and CPI deflation. This does not qualify actual product tax rules or 2036 law.
- G3: deterministic pre-tax/fee hurdle and independent reconstruction audits pass. G6.1 demonstrates one bounded bridge scenario family, not target feasibility or forecast accuracy.
- G6 decision-grade status: **NOT READY**. G6.2 exercises the full schedule only with synthetic marks, costs, inflation, and a repeated tax-component fixture. Candidate-specific source returns, applicable future tax rules, distributions/loss allocation, flexible exits, original CPI bytes/base month, and full-horizon adverse-case review remain open. Cross-asset probability remains unqualified.

### Next concrete work

Review exact-head checks on stacked PR #43, then accept its G6.1 parent PR #41 before merging the dependent increment. Next, qualify candidate-specific dated price/return inputs and actual product tax/cost treatment; then add distributions, reinvestment, applicable loss allocation, and forced/flexible exit rules. Keep future-law claims, investor-specific results, probability, recommendations, and transactions blocked until their independent evidence gates pass.

**Decision status:** NO-GO. Nothing in this status authorizes transactions.

## Completed on 2 November 2026 — P0 Tasks 1–2

- **Task 1:** official AMFI scheme 133307 NAV history passed for research use: 2,867 observations across 24 source segments, 26 Dec 2014–30 Oct 2026; raw segment bytes and hashes independently audited; LIC 1/3/5-year factsheet arithmetic reconciled. Evidence: `research/stage512/2026-11-02/stage512_R93_live_backfill_and_129m_audit.md` and `research/stage512/data/r9_lic_gsec_etf/qualification_manifest.json`.

- **Task 2:** strict equity TRI / LIC ETF NAV proxy bridge passed for 117 of 129 intervals after both-end date alignment; sample correlation 0.022541. This does not qualify a direct G-Sec total-return index or a forward correlation. Evidence: `research/stage512/data/r9_nse_gsec_129m_source_bridge.json`.

- Merged as PR #4, merge commit `8eb9c20`. Source-commit Actions: R9 full AMFI `41475006266`, equity-bond bridge `41475006330`, offline contract `41475006356` all succeeded. Investment authorization remains NO-GO.



**Historical next-step note (2 November 2026):** The CPI and Sprint 1 work described below has since been completed at the bounded scope recorded above and in `docs/SPRINT_01_AFTER_TAX_LEDGER.md`. The remaining personal-result, source-history and integration gates are not closed by that completion.



**Historical state (2 November 2026):** This paragraph records the original Sprint 1 setup and the sequence of PRs #6–#8. It was superseded by the 4 November Sprint 1 close; current status is given above and in the controlling Sprint 1 close record.



## P0 task definitions and acceptance gates (completed on this branch; retained for traceability)

**Task 1 — Independently inspect and repair the R9 official bond-fund history gate.**

1. Read `AGENTS.md`, mandate, handoff, prior R9.3 incident report and the latest live manifest. Check current branch, repository status and existing GitHub Actions results before assuming source failure persists.

2. Execute offline regression, parser, finance and data-contract tests. Audit the most recent source-qualification code *as new code*, especially scheme ID 133307, `Option:null`, growth-only identity, start/end dates, calendar continuity, 429 retry semantics, byte SHA256 and cache/resume.

3. Diagnose whether requests are rate-limited and whether half-year segments can be fetched respectfully and persisted. Implement incremental bounded recovery rather than all-or-nothing repeated 24-window concurrency; honor API terms. **Do not bypass 429, captchas or access controls.**

4. For each original time segment save source URL, raw SHA256, start/end dates, accepted records, failures, full raw artifact and checkpoint. Keep failed data visibly unqualified. Qualify a contiguous monthly ETF NAV dataset only after complete test coverage and independent LIC factsheet 1/3/5-year NAV CAGR reconciliation.

5. If full API access fails, produce a precise failure manifest, usable verified short segments, and an alternative lawful official bulk export / fund-house NAV plan. Do not waste investor time with repeated blind retry.

6. Commit tests, code, new status evidence and the decision implication; create PR for material changes.



**P0 acceptance:** official history source is demonstrably qualified within stated coverage OR blocked with a source-verifiable reason, reproducible checkpoint and compliant alternative. A code edit or a passing offline test is not sufficient.



**Task 2 — Date-aligned 129-month equity–bond risk baseline.**

- Only if R9 official NAV passes, compare with the 129 official-published NSE Nifty500 TRI months (Jan 2015–Sep 2025).

- Validate both current and preceding close dates, fund NAV source hashes and 1/3/5y official fund returns. Quarantine month-end mismatch as R7 taught us.

- Publish observed volatility, correlation, confidence/sample-size caveat, different regimes, and sensitivity versus the existing 36-month HDFC Gilt + Nifty500 analysis. Do **not** substitute LIC ETF for actual NSE G-Sec total-return index without identifying the proxy.



## P1: Complete accurate multi-asset financial inputs (status updated 5 November 2026)

**Task 3 — CPI and total-return evidence. Status: PARTIAL.** Linked CPI value and mechanical audits pass across 165 months; the investor base month and raw MoSPI response/release bytes are still absent. Nifty 500 TRI and LIC ETF NAV are qualified only within documented coverage and source type. Gold/silver bullion remains a secondary mirror with limited official anchors; direct continuous NSE G-Sec TRI remains unavailable. Next: acquire and audit first-party instrument NAV series from inception where available; do not splice unlike series or fabricate pre-inception returns.



**Task 4 — Tax/real-wealth accounting. Status: PASS for bounded Sprint 1 synthetic fixtures; BLOCKED for investor-specific output.** The audited input contract, tax components, loss schedule, event/lot ledger and deterministic hurdle audits pass. Strategy-specific returns/fees, actual investor tax-year facts, dates, security classifications and exit choice are still required before personal nominal→tax→real results. Do not label the synthetic fixture as a personal estimate.

- **Tax-rule source map started:** `decision/tax_rules_asof.md` documents TY 2026–27 provisions and product-specific branches, including Act 2025 transition, equity STT conditions, specified debt-fund units, direct-security coupons/sales, and non-equity precious-metal funds. It is not a tax result; exact-security classification, the after-tax ledger and professional example review remain acceptance gates.



## P2: Optimize investor decision, not code volume

**Task 5 — Candidate screen. Status: BREADTH PASS / EVIDENCE PARTIAL.** The G5.4 append-only screen has 10 product hypotheses and exact TER identity/arithmetic evidence. Investor access, executable prices/spreads, product-specific tax, qualified long histories and full candidate disposition remain open. See #29/#38 and PR #39. A candidate count is not a suitability or source-history pass.



**Task 6 — Credible scenario model. Status: NOT STARTED FOR DECISION-GRADE INFERENCE.** A bounded deterministic after-tax bridge using the existing synthetic event/tax and G3 hurdle contracts can start as an implementation increment. Full historical/regime comparisons, parameter uncertainty, cross-asset dependence, sequence risk and stress analysis must wait for qualified source series. No probability is currently validated; never backfill pre-inception history.



**Task 7 — Decision alternatives and investor suitability.** Provide candidate shortlist, scenario-weighted comparisons, terminal real aftertax wealth distributions, severe shortfall probabilities, expected shortfalls, drawdowns, capital market and policy risks, and feasibility. Identify the minimum additional investor confirmations needed. If an acceptable plan does not support a defensible GO, recommend NO-GO and concrete viable modifications; do **not** silently relax the target.



## P3: Deliver decision pack for investor review

**Task 8 — Produce `decision/2036_DECISION_MEMO.md` and associated artifacts** per `docs/DECISION_DELIVERABLES.md`: bottom-line decision, specific executable instruments/ISIN, allocation ₹ and %, funding calendar, taxes, justified alternatives, gross/aftertax/real outcomes, uncertainty, downside and execution checks.

**Task 9 — Independent challenge and signoff.** Separate reviewer should try to refute data, model, taxes, constraint consistency, real execution and target feasibility. Maintain unresolved conditions. Final approval and execution belong to the investor.



## Development delivery rules

- First response in Codex: concise diagnosis of current R9 manifest and explicit next files/actions; then **perform the work**, don't produce a new 20-page plan.

- Prefer focused code/tests/PRs and one dated decision-log entry per meaningful milestone. Show failure evidence and causes, not just "fixed".

- Change scope only if tied directly to the investment decision; skip unnecessary UI, database, SaaS product, chat, AI agent orchestration or generalized platforms.

- Never treat a source PASS or backtest PASS as investment GO.

- Use up-to-date primary data at decision date; code and references from Nov 2026 can become stale.

- If a source is rate limited, stop respectfully, record state, choose alternate approved sources; don't run unrestricted retries.

- When complete, provide a concrete investor briefing, not only code.



## Expected progress report

`Executed | Findings and numbers | Independent checks and links | Investment relevance | Remaining gated risks | Next single work item | Investor GO/NO-GO status`.



An acceptable **conditional** result may be "the real aftertax target is not achievable at suitably bounded risk"; do not assume a portfolio must exist that hits 85%.

