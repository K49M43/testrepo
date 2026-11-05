# Codex Execution Plan — Move from Evidence Pipeline to Actual 2036 Investment Decision

**Priority order matters.** Build the minimum decision-grade system needed to make a real investment decision, not a generalized research/portfolio SaaS.

## Current status — 5 November 2026

### Sprint 1 — closed for the bounded research and synthetic-fixture scope

The controlling close record is [Sprint 1 — Deterministic after-tax ledger](SPRINT_01_AFTER_TAX_LEDGER.md), closed 4 November 2026. Its bounded tax-component, loss-allocation, event/lot and 120/122-month cashflow checks pass; the source-based review against the enacted Income-tax Act was accepted for this research scope. The independent Decimal loss/tax reconciliation, event-ledger audit and input-contract audit were rerun from `main` during the G5.4 blocker investigation and passed. This does not establish an investor-specific tax result, actual transaction schedule, 2036 law, or final real-wealth outcome. Those facts remain explicit inputs, not Sprint 1 closure conditions.

### Current work — Sprint 5 / G5 candidate and source qualification

G5 parent issue [#29](https://github.com/K49M43/testrepo/issues/29) remains open. G5.4 is tracked in [#38](https://github.com/K49M43/testrepo/issues/38) and draft [PR #39](https://github.com/K49M43/testrepo/pull/39). The candidate screen has 10 product hypotheses; the refreshed official AMFI bounded observations reconcile 44/44; and exact latest AMFI TER rows/component sums reconcile for all ten product hypotheses (20/20 component sums). Candidate breadth, sampled-data reconciliation, TER retention and the latest PR checks pass. The continuous candidate/asset-class series qualification remains incomplete, and a sample-window pass must not be presented as a full return history.

### Source and model status

- CPI: 165 contiguous linked/direct observations pass source-value checks (144/144 historical linked values and 21/21 direct values) plus mechanical continuity/link/rate checks. The values are transcriptions, not preserved original release bytes; investor-aligned base month is unconfirmed. Use only as a provisional research deflator, not a final personal real-wealth result.
- Equity: 129 monthly official-published Nifty 500 TRI anchors through 2025-09 are qualified within their documented coverage.
- Government bonds: 2,867 official AMFI LIC G-Sec ETF NAV observations are qualified as a fund NAV proxy. The continuous official NSE G-Sec TRI is not qualified; NAV is neither traded ETF price nor a direct sovereign bond return.
- Gold/silver: RBI-origin secondary monthly bullion observations and a limited set of official-published anchors are available; full first-party vintage and instrument-level histories are not qualified. Do not substitute bullion averages for ETF month-end NAVs.
- Tax/cashflows: synthetic TY 2026–27 tax and event/lot fixtures pass. Personal-year tax facts, actual securities/dates/costs and 2036 exit choice remain unknown; exact personal output is blocked until supplied.
- G3: deterministic pre-tax/fee hurdle and independent reconstruction audits pass. This is not a forecast or probability and has not yet been reconciled through the after-tax event ledger.

### Next concrete work

Resolve the remaining G5 source-history gate with a versioned source-selection register: qualify actual AMFI NAV history from inception for selected Growth-plan instruments, use strict common-date joins, and preserve the distinct Nifty TRI, fund NAV, ETF market-price, bullion and direct-bond conventions. In parallel, implement only the deterministic after-tax bridge using synthetic dated fixtures and the passed Sprint 1/G3 contracts. Keep actual personal results, probabilistic claims and any recommendation blocked until their separate evidence gates pass. See the G5.4 blocker audit and readiness matrix under `research/stage512/2026-11-05/g5_4/`.

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
