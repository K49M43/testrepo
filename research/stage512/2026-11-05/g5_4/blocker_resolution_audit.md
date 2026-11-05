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
2. **Resolved at synthetic scope:** Sprint 1 tax and loss pipeline, event/lot accounting, 120/122-month schedule and G3 hurdle arithmetic. The input contract was stale despite implementation/CI closure; it is now version 1.4 and states the explicit-offset/section 516 behavior and fail-closed cases. The cashflow schedule is unchanged.
3. **Open:** continuous scheme-level history for selected candidates, strict common-date instrument bridge, one joined deterministic after-tax path, original MoSPI source-byte capture/personal CPI base, and independent joined/adverse-case audit.
4. **Personal decision only:** suitability, platform access, tax-year income/losses, exact contributions, fees and exit choice. These must block personal results and recommendations, not synthetic engineering.
5. **Probability only:** cross-asset regimes, parameter uncertainty, sequence/tail calibration; no probability claim is currently validated.

## Bounded AMFI acquisition probe

A single scheme-specific official AMFI NAV API request for SBI Nifty 500 (scheme 152908, 2024-09-30 through 2026-10-31) did not yield a saved response, output status or artifact in the execution environment. It is recorded as **inconclusive transport/API attempt**, not as HTTP 429 and not as evidence that AMFI lacks the series. Do not retry blindly. Next attempt must use the existing importer’s bounded-window/checkpoint behavior, log status and response bytes before parsing, and halt at the first 429.

## Decision

- **G6 fixture-first engineering:** READY.
- **G6 decision-grade model / full candidate source gate:** BLOCKED on continuous selected histories and joined path validation.
- **Investment authorization:** NO-GO.

The next smallest substantive item is the bounded, checkpointed AMFI source-history acquisition for the explicitly selected candidate subset, then the deterministic ledger bridge. The CPI/source and investor input limits remain visible; no assumptions are promoted to confirmed facts.
