# Codex Execution Plan — Move from Evidence Pipeline to Actual 2036 Investment Decision

**Priority order matters.** Build the minimum decision-grade system needed to make a real investment decision, not a generalized research/portfolio SaaS.

## Active sprint — S1 deterministic after-tax ledger

The tracked scope and completion criteria are in [Sprint 1 — Deterministic after-tax ledger](SPRINT_01_AFTER_TAX_LEDGER.md). Increments 0–4 pass at their documented research or synthetic-fixture scope; tax-source trace and repeated same-lot partial-disposal regression harden acceptance. Local audits pass on the current workspace. The tax component now applies a provisional mixed-income surcharge-relief composition and section 516 rounding to settlement balances, but both need professional review; capital losses and total-income rounding remain unimplemented. Sprint closure also requires qualified tax review, actual security/date/fee/tax inputs, aligned CPI base, future-law validation, and remote check verification. Do not claim investor-specific real wealth before the applicable gates pass.

**Latest increment (3 November 2026):** implemented and audited the section 3(5) surcharge-relief reference composition for mixed ordinary and special-rate income: hold nonordinary components fixed at the active threshold and reduce ordinary income to construct the reference tax. It is explicitly provisional and fails closed if nonordinary income exceeds the threshold. Section 516 now rounds final payable/refundable balances after credits; total-income rounding remains open. Mixed-income tests cover ₹50L and ₹1Cr boundaries.

**Latest tax-source audit (3 November 2026):** official sections 108/111/121 and the section 536 transition rule are mapped in `decision/capital_loss_and_marginal_relief_review.md`. Loss character, restrictions, eight-year expiry, and return-determination prerequisite are clear. Applying losses among differently taxed gain buckets still needs a reviewed method. Mixed-income section 3(5) relief now uses a tested provisional reference-composition convention; broader professional validation remains open. The TY 2026–27 calculator is not validated for future years.

**Next action:** implement capital-loss tracking/netting with an explicit, reviewed allocation among differently taxed gain buckets; audit statutory total-income rounding. Expand mixed-income cases across all surcharge thresholds and obtain professional validation. Sprint closure still requires that separate review, actual instrument/date/fee/tax inputs, aligned CPI base, and authenticated remote CI/PR verification. Do not infer these facts or contact a reviewer without separate authorization. Investment authorization remains **NO-GO**.

## Completed on 2 November 2026 — P0 Tasks 1–2
- **Task 1:** official AMFI scheme 133307 NAV history passed for research use: 2,867 observations across 24 source segments, 26 Dec 2014–30 Oct 2026; raw segment bytes and hashes independently audited; LIC 1/3/5-year factsheet arithmetic reconciled. Evidence: `research/stage512/2026-11-02/stage512_R93_live_backfill_and_129m_audit.md` and `research/stage512/data/r9_lic_gsec_etf/qualification_manifest.json`.
- **Task 2:** strict equity TRI / LIC ETF NAV proxy bridge passed for 117 of 129 intervals after both-end date alignment; sample correlation 0.022541. This does not qualify a direct G-Sec total-return index or a forward correlation. Evidence: `research/stage512/data/r9_nse_gsec_129m_source_bridge.json`.
- Merged as PR #4, merge commit `8eb9c20`. Source-commit Actions: R9 full AMFI `41475006266`, equity-bond bridge `41475006330`, offline contract `41475006356` all succeeded. Investment authorization remains NO-GO.

**Next incomplete work:** P1 Task 3–4, starting with audited linked-CPI vintage/anchor treatment and an independent deterministic, instrument-specific after-tax cashflow model. The arithmetic-only baseline is `research/stage512/2026-11-02/cashflow_hurdle_baseline.md`; it does not close the tax or real-wealth gates.

**Current substep (2 November 2026):** PR #6 added the initial Act 2025 / Finance Act 2026 instrument-tax map and its post-merge review found a P1 error in section 202 surcharge treatment. PR #7 corrected the map (`12af0d8`); PR #8 added source-based arithmetic boundary and mixed-income examples (`4f03574`). The examples have not been reviewed by a qualified tax professional. Sprint 1 is now planned in `docs/SPRINT_01_AFTER_TAX_LEDGER.md`: audit the released CPI vintage; implement and check current-law tax components; build the dated tax-lot/event ledger; reconcile 120/122-month deterministic exits. Actual investor dates, taxes, securities, and fees remain unconfirmed, so initial ledger fixtures must be explicitly synthetic and cannot be presented as investor results. Investment authorization remains NO-GO.

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

## P1: Complete accurate multi-asset financial inputs
**Task 3 — CPI and total-return evidence.** Re-audit MoSPI linked CPI; NSE TRI anchor and later updates; RBI bullion secondary mirror against official published prices. Obtain actual G-Sec total-return index if feasible, or label a LIC ETF return as product proxy and independently validate duration. Account for bullion monthly-average vs fund month-end pricing.

**Task 4 — Tax/real-wealth accounting.** Independently audit the ₹42L and stepped SIP cashflow engine, all holdings and tax lots under current Indian law, coupon reinvestment, ETF expense/price impacts, transaction costs, inflation-link basis and alternative 2036 exits. Demonstrate deterministic tests and produce nominal→tax→real result tables.
- **Tax-rule source map started:** `decision/tax_rules_asof.md` documents TY 2026–27 provisions and product-specific branches, including Act 2025 transition, equity STT conditions, specified debt-fund units, direct-security coupons/sales, and non-equity precious-metal funds. It is not a tax result; exact-security classification, the after-tax ledger and professional example review remain acceptance gates.

## P2: Optimize investor decision, not code volume
**Task 5 — Candidate screen.** Identify and verify **10+** legitimate investable candidates/strategies with current terms, source dates, identifiers, access via Groww/other lawful route, liquidity, risks and tax. Include direct GoI bond(s), rolling G-Sec alternatives, Nifty500/broad equity, gold **and silver**, and suitable alternatives. Reject candidates with reasons, not omission.

**Task 6 — Credible scenario model.** Define forward assumptions *independently* of desired result; run deterministic hurdles, long-history and recent-regime volatility/covariance, stress losses, Student-t / block bootstrap and inflation/tax uncertainties. Avoid false certainty. Compare at least multiple diversified portfolio allocations and defensive approaches for the ₹90L real after-tax floor and ₹1Cr real stretch.

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
