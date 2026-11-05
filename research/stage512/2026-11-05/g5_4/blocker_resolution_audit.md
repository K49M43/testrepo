# Blocker resolution audit — 2026-11-05

## Root cause
The earlier readiness record treated implementation entry, qualified decision data, personal facts and investor authorization as one gate. That carried already completed Sprint 1 fixture work forward as an unresolved blocker and incorrectly implied personal facts were needed before any G6 engineering. It also treated G3's arithmetic PASS as if the after-tax bridge were already integrated. The correct disposition is staged: synthetic engineering can begin; decision-grade results remain gated.

## Reproduced evidence from `main`

| Evidence | Result | Boundary |
|---|---|---|
| `research/stage512/2026-11-02/reconcile_after_tax_input_contract.py` | PASS: 123 rows; 120/122 months; totals ₹8,981,227.3803 / ₹9,110,914.503305; payment dates illustrative | Now checks schema v1.4 loss/rounding contract. Values are not investor-specific dated contributions. |
| `decision/audit_ty2026_27_tax_components.py` | PASS | TY 2026–27 statutory components and bounded surcharge/rounding fixtures only. |
| `decision/audit_independent_loss_tax_reconciliation.py` | PASS | Independent Decimal formula comparison, explicit bounded loss offsets. |
| `decision/audit_after_tax_event_ledger.py` | PASS: 9 events, 2 tax years; gross ₹2,433; incremental tax ₹473.564; net fixture wealth ₹2,109.436 | Synthetic fixture; no personal tax profile. |
| `audit_cpi_esankhyiki_back_capture.py` | PASS: 144/144 published values | Transcription hash, not original official download bytes. |
| `audit_cpi_pib_sep2026_annexure_iv.py` | PASS: 21/21 values and provisional flags | Transcription hash, not original release bytes. |
| `audit_cpi_linked_series.py` | PASS: 165 contiguous levels, link factor and derived rates | CPI base month for actual investor still unknown. |
| `decision/audit_g3_goal_hurdle.py` | PASS: 12 deterministic cases | Explicit pre-tax/fee arithmetic, not a forecast/probability or after-tax integration. |
| PR #39 checks at original G5.4 source commit | PASS: candidate register, lineage, independent candidate audit | These verify candidate evidence and artifacts, not continuous history. |

## Corrected status

1. **Resolved:** candidate breadth (10 product hypotheses), official TER raw retention and row identity (10/10), component arithmetic (20/20), and re-retrieved bounded AMFI NAV sample reconciliation (44/44).
2. **Resolved at synthetic scope:** Sprint 1 tax and loss pipeline, event/lot accounting, 120/122-month schedule and G3 hurdle arithmetic. The input contract was stale despite implementation/CI closure; it is now version 1.4 and states the explicit-offset/section 516 behavior and fail-closed cases. The cashflow schedule is unchanged. CI exposed a stale terminal-case manifest hardcoding contract v1.3; `terminal_case_reconciliation.py` now reads the version from the contract, and the six-case terminal artifact was regenerated with pinned hashes. Local `--check` passes.
3. **Open:** continuous scheme-level history for selected candidates, strict common-date instrument bridge, one joined deterministic after-tax path, original MoSPI source-byte capture/personal CPI base, and independent joined/adverse-case audit.
4. **Personal decision only:** suitability, platform access, tax-year income/losses, exact contributions, fees and exit choice. These must block personal results and recommendations, not synthetic engineering.
5. **Probability only:** cross-asset regimes, parameter uncertainty, sequence/tail calibration; no probability claim is currently validated.

## Bounded AMFI acquisition probe

A single scheme-specific official AMFI NAV API request for SBI Nifty 500 (scheme 152908, 2024-09-30 through 2026-10-31) did not yield a saved response, output status or artifact in the execution environment. It is recorded as **inconclusive transport/API attempt**, not as HTTP 429 and not as evidence that AMFI lacks the series. Do not retry blindly. Next attempt must use the existing importer’s bounded-window/checkpoint behavior, log status and response bytes before parsing, and halt at the first 429.

## Decision

- **G6 fixture-first engineering:** READY.
- **G6 decision-grade model / full candidate source gate:** BLOCKED on continuous selected histories and joined path validation.
- **Investment authorization:** NO-GO.

At the time of the original blocker audit, the next smallest item was bounded AMFI source-history acquisition. The follow-up section below records the subsequent acquisition and narrows the remaining work. CPI/source and investor input limits remain visible; no assumptions are promoted to confirmed facts.

## Source-history re-investigation — 2026-11-05

The acquisition and strict-month-join blocker is now **partially resolved**. Five AMFI Growth-option product histories pass raw-to-normalized lineage: 7,353 NAV observations across 63 retained windows for Motilal Nifty 500 Index Fund, HDFC Gold, ICICI Silver, SBI Nifty 500 index fund, and SBI June 2036 target-maturity gilt fund. The independent audit checks hashes, exact identities, non-overlapping windows, dates, positive Decimal NAV, duplicates, normalized CSV equality, and calendar gaps. It also reconciles the SBI Nifty 500 exploratory response exactly across 122 observations.

The published-NSE-TRI calendar-month joins are descriptive only: 72 months for Motilal Nifty 500 Index Fund (2019-10–2025-09), 128 for HDFC Gold (2015-02–2025-09), 44 for ICICI Silver (2022-02–2025-09), 11 for SBI Nifty 500 fund (2024-11–2025-09), and 35 for SBI June 2036 gilt fund (2022-11–2025-09). Fund NAV and ETF traded price remain different. NSE values are rounded monthly anchors; these joins do not establish continuous daily benchmark paths, long-run cross-asset dependence, covariance, or probability.

The first target-maturity AMFI parse identified a product-name alias and a fetcher defect that failed to preserve a rejected HTTP 200 body. The parser was corrected using the exact official AMFI name already present in retained raw samples; the fetcher now writes the raw body before validating it. The unretained initial response is excluded. The corrected nine-window acquisition and independent audit pass.

All 10 product hypotheses now have a row-level classification, keep/defer decision, evidence status and reason in `g5_candidate_disposition_v1.json`. The initial set is explicit in `G5_CANDIDATE_DISPOSITION.md`; direct GoI and cash remain blocked from numeric results rather than silently dropped. Remaining blockers are: (1) independent acceptance audit of the candidate disposition against every original G5 criterion, especially holdings and explicit costs/tax/liquidity/settlement/access gaps; (2) qualify direct-sovereign/T-Bill cashflows and ETF market-price execution where needed; (3) implement and independently reconcile the synthetic fixture-first G6 tax/cashflow/exit adapter; (4) preserve provisional CPI status and keep personal inputs unconfirmed; (5) defer probability until adverse/regime/parameter checks are supportable. G6 engineering start is READY; decision-grade G6 remains blocked; investment authorization remains NO-GO. Full evidence is in `CANDIDATE_HISTORY_BLOCKER_RESOLUTION.md`, `G5_CANDIDATE_DISPOSITION.md` and `candidate_nav_history_audit.json`.

### G5 exit audit result — 2026-11-05

The row-level candidate disposition, five retained histories, five new factsheet holdings extracts, and source/hash checks now pass an independent mapping to all eight G5 parent acceptance criteria. The earlier item (1) above is closed. The audit accepts explicit `BLOCKED`/insufficient-evidence rows without pretending the direct GoI security or T-Bill comparator has a qualified price path. This supports G5 acceptance review after PR #39 is reviewed and merged; it does not close G6 decision-grade or investor-specific gates.

The unresolved list in the earlier “Source-history re-investigation” paragraph is historical and is superseded by this result: the disposition audit, holdings coverage audit, and eight-criterion G5 exit audit have now run and passed locally. The remaining G5 action is review/merge of PR #39; no source-history acceptance work is outstanding for the declared five product NAV windows. Separate G6 decision-grade blockers remain unchanged.
