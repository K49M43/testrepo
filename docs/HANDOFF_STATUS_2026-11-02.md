# Codex Handoff — State of the Actual 2036 Investment Decision (2 Nov 2026)

**Investor-facing program status: NO-GO / decision not yet supportable.** This is **not** a declaration that any proposed asset is unsuitable; the present evidence is not yet sufficient for an investment-ready ranked decision.

## Latest development update — 3 November 2026 (section 516 total-income integration)

- **Finding:** section 516 deems rounded total income to be total income. Official predecessor-Act ITR instructions show the total-income field rounded at the end of the computation and normal-rate tax calculated separately from special-rate income. The Department says TY 2026–27 forms under the new Rules 2026 will be notified before filing; the predecessor workflow is evidence for a provisional interpretation, not direct validation of the new form.
- **Implementation:** the tax component now preserves raw and rounded total income; uses rounded total for section 156, surcharge and marginal-relief thresholds; preserves reported dividend and special-rate components; and assigns the rounding residual to ordinary income. It fails closed if ordinary income would become negative. This mixed-bucket ordering remains unreviewed.
- **Validation:** section 516 component, event-ledger, loss-schedule and terminal-case audits pass locally. The synthetic no-loss event result changed to ₹473.564 incremental tax, ₹323.564 remaining after withholding, and ₹2,109.436 net fixture wealth. Terminal-case evidence was regenerated with rounded income bases. These are synthetic results, not an investor tax estimate.
- **Remaining gates:** qualified tax review, actual TY 2026–27 return-form confirmation, integrated capital-loss tax application, mixed-income surcharge review, investor-specific inputs, CPI anchor, and final remote CI on the published head. Sprint 1 remains **IN PROGRESS**; authorization remains **NO-GO**.

## Latest development update — 3 November 2026 (loss disposal economic reconciliation)

- **Executed:** the event ledger now records each non-zero disposal as a signed event/lot record including proceeds, basis removed, deductible transfer expenses, statutory bucket, holding character, and eligibility flags. A classified loss now completes cash, units, basis, ending valuation, and portfolio conservation instead of aborting before the sale is recorded.
- **Tax boundary:** when any realized loss is present, the ledger returns `ECONOMIC_PASS_TAX_UNQUALIFIED`; tax, incremental-tax, and after-tax-accessible-wealth fields are null. An audited adapter now consumes the ledger's source-linked gain/loss records and demonstrates an explicit offset while keeping coupons/dividends outside the schedule. The main ledger does not invoke that adapter and annual tax still does not consume the candidate schedule.
- **Validation:** the loss fixture reconciles to ₹490 gross terminal wealth, zero conservation residual, two units, and ₹200 remaining tax basis. Existing no-loss terminal economics and tax outputs are unchanged; its artifact was regenerated to include source-linked signed-disposal traces and the updated code hash. All four source/cashflow audits and the loss schedule, tax component, event/lot, and terminal reproducibility audits pass locally; module compilation passes.
- **Remaining closure gates:** allocation policy/review, the integrated taxpayer-year loss pipeline, statutory total-income rounding, qualified review of mixed surcharge/basic-exemption cases, actual investor instruments/dates/fees/tax facts/CPI anchor, and remote CI acceptance. GitHub CLI remains unauthenticated. Sprint 1 remains **IN PROGRESS**; authorization remains **NO-GO**.

## Latest development update — 3 November 2026 (Sprint 1 residual audit hardening)

- **Executed:** added a second same-lot partial-disposal case to `decision/audit_after_tax_event_ledger.py`. It sells two units from a three-unit lot in separate events and verifies ₹50 realized gain, ₹450 ending cash, ₹100 remaining market value/basis, and zero reconciliation residual within the declared ₹1e-12 arithmetic tolerance. The audit also asserts that a realized loss fails closed. The tax-component audit now asserts that ambiguous basic-exemption allocation and unqualified mixed-income surcharge marginal relief fail closed.
- **Local validation:** the tax-component, event/lot, and terminal-case audits passed; the 120/122 terminal artifact remains byte/reconciliation-consistent and original fixture totals did not change. The input-contract audit and all three CPI structure/source-capture audits also passed (123 schedule rows; 144 linked CPI values; 21 direct CPI values; 165 monthly levels). CPI investor-base alignment remains open. Relevant module compilation passed.
- **Limits:** Sprint 1 is still open. Capital-loss set-off/carry-forward, statutory rounding under section 516, mixed special-income surcharge relief and ambiguous basic-exemption allocation are not fully implemented. Independent tax-professional review is still required and no external reviewer was contacted. Investor-specific security/date/cost/tax/CPI inputs remain open.
- **Remote status:** GitHub CLI v2.103.3 is installed at `C:\Program Files\GitHub CLI\gh.exe`, but `gh auth status` has no authenticated host. Current PR/review/Actions checks were not verified. No push or merge was performed; investment authorization remains **NO-GO**.

## Latest development update — 3 November 2026 (Sprint 1 tax-source trace hardening)

- After Increment 4, an acceptance review found that annual tax-category inputs needed an explicit link back to taxable source events. `decision/after_tax_event_ledger.py` now emits event-level source records and per-tax-year event IDs by category; sale and lot-linked coupon records include acquisition dates, and withholding remains a separate credit. Annual tax remains calculated per year and is not fabricated as an event-specific amount.
- Input contract v1.3 and `research/stage512/2026-11-03/terminal_case_reconciliation.json` record the trace contract and reproducible source evidence. Local audits pass; on PR #12 head `7c8dacb`, source/cashflow run [41568107162](https://github.com/K49M43/testrepo/actions/runs/41568107162) and tax/ledger run [41568107287](https://github.com/K49M43/testrepo/actions/runs/41568107287) both succeeded, for 4/4 passing PR checks.
- PR #12 remains a draft, stacked on PR #11, and must not be merged until its review and base-PR state are resolved and the user decides. Sprint 1 remains open; actual investor inputs, CPI alignment, future-law validation, and qualified tax-professional review remain gates. Authorization stays **NO-GO**.
- `docs/SPRINT_01_INVESTOR_INPUT_WORKSHEET.md` is prepared as a blank, privacy-conscious intake template. It does not contain new investor values and does not close the open dates, holdings, costs, tax, CPI, risk-tolerance, or independent-review gates.

## Prior development update — 3 November 2026 (Sprint 1 Increment 4)

- Sprint 1 Increments 0–4 now pass only at their recorded fixture or research-source scope. Increment 4 reconciles the frozen 120/122-month schedules across one-year synthetic fund exit, staged liquidation, and direct-bond coupon/maturity cases. The independently audited artifact is `research/stage512/2026-11-03/terminal_case_reconciliation.json`; source/code/rule SHA256 values are pinned in its run manifest.
- Exact 120/122 contributions reconcile to ₹89,81,227.3803 / ₹91,10,914.503305. Outputs use invented 5% simple annual fund NAV appreciation and a 5% bond coupon, explicit synthetic ₹30 lakh other income, zero fixture fees, and TY 2026–27 tax rules held constant into the future. No real-wealth or investor tax conclusion follows.
- PR #12 (`https://github.com/K49M43/testrepo/pull/12`) contains the Sprint 1 tax/ledger work and is stacked on PR #11. Check its current review and Actions status before treating the submitted Increment 4 changes as accepted; neither PR is authorized for merge by this handoff.
- Remaining Sprint 1 gates: actual security identifiers and dates, actual fees and tax facts, an aligned CPI base, future tax-law revalidation at decision time, and independent qualified tax-professional review. No reviewer has been contacted. Until these are satisfied, no investor-specific after-tax/real-wealth output is qualified and authorization remains **NO-GO**.
- The detailed historical sections below predate this update and are retained as evidence snapshots; the current tracker is `docs/SPRINT_01_AFTER_TAX_LEDGER.md`.

## Latest development update — 2 November 2026 (after PR #8)

This section supersedes the old “where to begin” and blocker snapshots below wherever they conflict; earlier failure records remain historical.

- PR #5 merged as `da98bf8`, adding the deterministic pre-tax cashflow hurdle baseline. At 6% assumed CPI the ₹90L October 2026-real floor equates to about ₹1.612Cr in October 2036; its constant-return arithmetic hurdle is about 8.25% effective annually before taxes, fees and costs. This is not a forecast or feasibility result.
- The TY 2026–27 instrument map is in `decision/tax_rules_asof.md`. PR #7 corrected the surcharge interpretation; PR #8 added boundary/marginal-relief and mixed-income arithmetic examples. Both are merged on `main` (latest merge `4f03574`). PR #8 showed Checks (0); its examples were decimal-recomputed from the cited statutory schedule but have not received qualified tax-professional review. No tax engine or investor-level tax output is qualified.
- **Next sprint:** `docs/SPRINT_01_AFTER_TAX_LEDGER.md` defines the incremental/iterative scope, acceptance gates, dependencies, and tracker for the deterministic after-tax ledger. Audit CPI and input chronology, implement current-law tax components with boundary tests, build dated tax lots/events, then reconcile 120/122-month exits. Keep fixture outputs explicitly synthetic until investor-specific dates, holdings, tax facts, and charges are confirmed.
- **Government-security rule correction:** entries 13D/13E were added by the Taxation and Other Laws (Amendment) Act, 2026 for Foreign Institutional Investors and the Bank for International Settlements. Notification 137/2026 dated 19 October prescribed Rule 281A/Form 173A. These institutional exemptions are not assumed for a resident retail investor. A prior handoff line describing them as pending has been corrected in the decision log and baseline.
- **Current gates:** qualified tax-professional review; official CPI vintage/base-month reconciliation; security-level classification; deterministic tax-lot/event ledger; and source-linked costs. No after-tax real-wealth output is qualified.
- Investor authorization remains **NO-GO**.

## Post-merge update — 2 November 2026 (PR #4)

P0 Tasks 1–2 are now complete within the limits below. The merged main commit is `8eb9c20`.

- R9 full official AMFI NAV history: **PASS for historical research**, 2,867 observations over 24 six-month source segments from 26 Dec 2014 through 30 Oct 2026; independent segment/hash/artifact audit passed.
- Strict 129-month Nifty 500 TRI versus LIC ETF NAV-proxy bridge: **PASS for the 117 intervals whose current and prior month-end dates both match**; observed correlation 0.022541. Twelve intervals were excluded for date mismatch.
- Actions on source commit `1bdf2c6` passed: full AMFI run `41475006266`, bridge run `41475006330`, offline contract run `41475006356`.
- The LIC ETF remains a rolling-duration fund proxy, not the NSE G-Sec index or a direct 2036-maturity GoI bond. The bridge is historical and does not qualify a forward correlation.
- Next: CPI vintage and base-month reconciliation, then independent tax-lot / after-tax real-wealth accounting. The October 2026 CPI was not yet released as of this update; the latest published reference is September 2026.
- Investment authorization remains **NO-GO**.

The original snapshot below is preserved as historical handoff context; its R9 failure status predates the successful qualification and merge.

## Where to begin
Review `AGENTS.md` and `docs/INVESTMENT_DECISION_MANDATE_2036.md`. The existing `research/stage512/` tree represents an **evidence and computational workstream**, not a reason to keep the investor in research indefinitely. The objective is the actionable 2036 investment decision.

### Verified source and model evidence (scope-limited)
| Evidence | Status and precise meaning | Repository path |
|---|---|---|
| 2036 cashflow/simulation work | Prior conditional models and alternative assumptions exist. Their outcomes are **not validated 2036 real-world probabilities** | `research/stage512/2026-11-02/README.md`, relevant `stage512_*.py` |
| 2026-base linked historical Indian CPI | Reconstructed 165 contiguous CPI monthly observations Jan 2013–Sep 2026; some independent source-vintage review still open | `research/stage512/2026-11-02/stage512_source_resolution_report.md`, `research/stage512/2026-11-02/stage512_cpi_official_linked_2013_2026.csv` |
| Four actual fund NAVs | 3,046 official AMFI NAV prices (equity, gilt, gold ETF, silver ETF), 63 archived official cross-checks. Strict risk matrix uses **36 matched monthly return intervals** Nov 2023–Oct 2026 after quarantining mismatched first month-end | `research/stage512/data/amfi_official_36m/qualification_manifest.json`, `research/stage512/data/official_nav_independent_R7.json`, `research/stage512/data/official_nav_R7_CI_diagnostics.json` |
| Four-fund historic covariance | Strict-date-aligned 65/20/10/5 historic annualized vol about **11.41%**. Only a short-sample descriptive statistic, not a forecast | `research/stage512/2026-11-02/stage512_official_NAV_regime_horizon_R7.md` |
| Nifty500 official TRI | **129 published monthly** Nifty 500 total returns Jan 2015–Sep 2025, compared against SHA1-pinned third-party daily index; all match within 0.0051 percentage point | `research/stage512/data/nse500_official_tri_monthly_2015_2025q3_R8.csv`, `research/stage512/data/nse500_tri_validation_R8.json` |
| RBI-origin gold/silver | 437 consecutive monthly Mumbai **average** gold/silver prices Apr 1990–Aug 2026 from a THIRD-PARTY mirror. Seven official published month pairs (14 individual prices) match; entire mirror not first-party certified | `research/stage512/data/r8_rbi_origin_mirror/normalized_validation.json`, `research/stage512/data/r8_rbi_bullion_primary_spotcheck_manifest.json` |
| Direct official NSE G-Sec total return | NSE index identified, but primary index daily/monthly TR history **not obtained**; clean price must not replace TR | `research/stage512/2026-11-02/stage512_R8_benchmark_source_resolution.md` |
| LIC MF 8–13yr G-Sec ETF factsheets | Scheme 133307 / ISIN INF767K01MV5; 12 independently published LIC ETF vs benchmark 1/3/5-year return points pass arithmetic. These are overlapping tracking-difference snapshots, NOT full index returns | `research/stage512/data/r9_lic_gsec_factsheet_bridge.json` |
| LIC ETF AMFI sampled history | Four short windows (2015/2018/2022/2026) pass; four 6-month windows return **119,121,120,117** priced observations. These are discontinuous samples | `research/stage512/data/r9_lic_gsec_etf/short_window_probe.json`, `research/stage512/data/r9_lic_gsec_etf/medium_window_probe.json` |
| LIC ETF full 2014–2026 backfill | **FAIL_INCOMPLETE**: initial run 0/24 segments accepted due to AMFI `Option=null` false rejection and HTTP 429 rate limiting. Corrected code exists, but a new full-history PASS was **not** confirmed as of handoff | `research/stage512/data/r9_lic_gsec_etf/qualification_manifest.json`, `research/stage512/pipelines/r9_lic_gsec_official_amfi_history.py` |
| R9.3 parser correction | **4 offline regression tests passed** (null option, rejected explicit dividend, 429 fail-closed, cached SHA, segment continuity). This does NOT certify full NAV history | `research/stage512/data/r9_lic_gsec_etf/r93_offline_regression.json` |
| Equity vs bond ETF long risk bridge | `FAIL_NOT_QUALIFIED`, because official full LIC ETF input remains unqualified. Script includes a strict both-end date-alignment filter | `research/stage512/data/r9_nse_gsec_129m_source_bridge.json`, `research/stage512/pipelines/r9_nifty500_gsec_instrument_bridge.py` |

**Status is snapshot-based.** Codex must check latest files, GitHub Actions run results and branch HEAD; new evidence may have arrived after this document was written. Never promote a gate based solely on a planned script or uninspected CI job.

## Exact immediate blockers in priority order
1. **R9 official LIC 2014–2026 NAV backfill:** recheck the current manifest; source code now accepts null Option and rate-limits sequential requests. Evaluate successful raw segment caching, incremental progress, legal access and fail-closed outcomes. Respect 429 and stop; do not brute-force a service.
2. **Independent 129-month return bridge:** after R9 official-history PASS, cross-check equity TRI vs LIC ETF dates, source hashes and factsheet CAGRs; compute bond/equity correlation and sensitivity. Does not magically qualify official NSE bond index total-return levels.
3. **Reference vs investable product:** keep Nifty 8–13 Yr G-Sec index, LIC ETF, HDFC Gilt Fund and direct maturity-matched GoI bonds distinct (different risks, cash flows and taxation). Compare eligible alternatives.
4. **Joint cashflow/tax/inflation model:** validate historical linked CPI, yield and bullion observation timing, fund-vs-benchmark bridges and current tax rules; rerun gross/aftertax/real outcomes.
5. **Actual decision universe and investor-facing memo:** minimum 10 credible security/strategy candidates and a justified shortlist; quantify feasible 2036 plans and conditions to execute. Do not stop at a pretty simulation.

## Frequent errors already discovered
- Calling a first-party **sample** PASS equivalent to a complete-history PASS.
- Calling **129 monthly source-crosschecks** a complete daily official NSE index certification.
- Quarantining one fund's differing September 2023 month-end and subsequently reintroducing it via month-label-only alignment.
- Rejecting AMFI `Option:null` as `"none"` or hammering the service after HTTP 429.
- Mistaking a clean-price G-Sec series for total return, or rolling gilt ETF for a single 2036 maturity sovereign.
- Treating RBI monthly averages as month-end ETF prices.
- Subtracting mutual fund expenses again from returns already derived from NAV.
- Confusing a model's 85% aspiration with a guaranteed inflation-adjusted floor.
- Selecting an allocation based solely on a short recent-history 11.4% volatility and neglecting regime/tail risk.
- Concluding "ready to invest" from a code-test or source-import success.

## Current stage decision
**Data source engineering:** multiple PASS subgates, R9 full bond NAV backfill still OPEN/FAIL.  
**Validated complete joint ten-year return history:** OPEN.  
**Tax-adjusted portfolio decision feasibility:** not fully established.  
**Investor GO:** **NO-GO**.

Never erase the failed manifests. Write a new dated audit for new findings and update the gate ledger only with verified results.

## 2026-11-03 — Sprint 1 section 516 rounding primitive
- **Executed:** added `section516_round_rupees` as an isolated Decimal helper implementing the statutory rule to ignore paise and round total income/payable/refundable to the nearest ₹10, with ₹5 upward. Boundary cases and negative-input rejection pass in `decision/audit_ty2026_27_tax_components.py`.
- **Integration boundary:** tax outputs remain unrounded. Do not describe statutory rounding as implemented in the calculator; the order of total-income rounding and handling of mixed ordinary/special-income components remain to be audited before integration.
- **Validation:** tax-component and event-ledger audits passed; terminal reconciliation artifact regenerated and its `--check` passed with updated rule-source hashes; Python compilation and `git diff --check` passed. Terminal fixture economics did not change.
- **Next:** resolve mixed special-income surcharge relief and loss set-off/carry-forward with official-source worked cases, then integrate rounding and re-audit. External professional review, investor-specific facts, and remote GitHub checks remain open. Sprint 1 is **IN PROGRESS**; investment authorization remains **NO-GO**.

## 2026-11-03 — Sprint 1 tax-source and completion-gate audit
- **Official rules checked:** sections 108, 111 and 121 define same-year capital-loss set-off, carry-forward character limits, the eight-succeeding-year limit, and loss-return determination prerequisite. Section 536 preserves eligible pre-2026 loss character and old-law eligibility. Added the source review and required worked-case matrix in `decision/capital_loss_and_marginal_relief_review.md`.
- **Critical implementation boundary:** the calculator has multiple special-rate capital-gain buckets. Netting losses among them can change the tax rate, annual section 198 allowance, surcharge and tax relief; the official text alone does not establish a reviewed allocation convention for the model. Finance Act section 3(5) mixed-income relief likewise lacks a validated mixed-composition worked case in our evidence set. Both paths remain fail-closed.
- **Completion audit:** section 516 helper remains isolated; actual security/date/fee/tax/CPI confirmations are absent; future law through 2036 is unknown; no professional review is recorded or authorized; GitHub CLI is unauthenticated. These are open Sprint 1 gates, so Sprint 1 cannot be marked complete or produce an investor-specific qualified tax result.
- **Decision:** continue NO-GO. Next technical gate is reviewed worked-case specification for loss allocation, mixed surcharge relief, and rounding order; external signoff and investor inputs remain distinct gates.

## 2026-11-03 — Sprint 1 provisional mixed relief and settlement rounding
- **Implemented:** Finance Act section 3(5) marginal relief now calculates a reference tax composition at the active ₹50L/₹1Cr/₹2Cr threshold by holding dividends and special-rate gains fixed and reducing ordinary income to the threshold. This convention is explicit and provisional; if those components exceed the threshold, the calculator fails closed. New boundary fixtures at ₹50L and ₹1Cr pass.
- **Section 516:** final payable/refundable balances after credits now round to the nearest ₹10; pre-credit analytical tax remains precise for counterfactual portfolio-tax comparisons. Statutory total-income rounding and its effect on mixed-rate thresholds remain open.
- **Validation:** tax-component audit passes, including mixed relief and payment/refund rounding cases. Full ledger and terminal audits are being rerun against the updated component.
- **Limits:** no qualified tax professional reviewed the provisional composition method. Capital-loss bucket allocation remains unimplemented; personal inputs, CPI anchor, future-year law, and remote checks remain open. Sprint 1 stays **IN PROGRESS**; authorization remains **NO-GO**.
