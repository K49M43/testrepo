# G5.4 blocker investigation and G6 readiness — 2026-11-05

## Disposition

- **G5 parent #29:** OPEN. The breadth and TER issues are resolved by this increment; source-history qualification and end-to-end candidate evidence are not.
- **G6 engineering start:** READY for a bounded deterministic after-tax cashflow bridge using explicitly synthetic inputs and existing contracts.
- **Decision-grade G6 output:** NOT READY. Continuous candidate histories and the joined path validation still fail the original entry gate.
- **Investment authorization:** NO-GO.

This separation prevents a closed synthetic tax gate from being described as a personal tax result, and prevents a sample-data pass from being described as a qualified return history.

## Root-cause finding

The apparent long blocker list combined four different conditions: (1) acceptance criteria already met in Sprint 1's synthetic scope; (2) incomplete source series; (3) personal values that are intentionally unconfirmed; and (4) final recommendation gates. The first category was carried forward incorrectly in the prior readiness matrix. Current `CODEX_EXECUTION_PLAN.md` now points to the controlling Sprint 1 close and records the new status.

### Independent re-runs from `main`

| Audit | Result | What it proves / does not prove |
|---|---|---|
| 120/122-month cashflow contract | PASS; 123 rows | The illustrative ₹42 lakh + stepped-SIP schedule reconciles. Payment dates remain placeholders. |
| Income-tax components and independent loss/tax reconciliation | PASS | Bounded TY 2026–27 synthetic calculations, source-traced offsets and settlement checks. No personal tax answer or 2036-law forecast. |
| Event/lot ledger | PASS; 9 events, 2 tax years | Synthetic contributions, units, gains/losses, withholding and incremental tax reconcile. No investor-specific lot schedule. |
| CPI linked-series audit | PASS; 165 contiguous months | 144/144 linked and 21/21 direct values match official published precision; transformation and rates reproduce. Original official bytes were not retained; personal CPI base month is unknown. |
| G3 deterministic hurdle audit | PASS; 12 cases | Independent pre-tax/fee nominal/real hurdle reconstruction and sensitivities. No return prediction or probability. |
| G5.4 source checks | PASS | 10 product hypotheses, 10/10 latest TER rows, 20/20 component sums, 44/44 bounded NAV samples; CI checks pass on PR #39. None of these sample checks creates continuous history. |

### Remaining blockers, with smallest acceptance actions

| Blocker | Status | Root cause | Smallest next action / acceptance |
|---|---|---|---|
| Continuous candidate histories | **OPEN — primary G5 blocker** | Ten product hypotheses exist, but newly added candidates have bounded sample NAV only. Existing qualified market inputs cover Nifty 500 TRI monthly anchors (129 observations through 2025-09) and LIC G-Sec ETF NAV (2,867 days, a rolling-duration fund proxy). Gold/silver have a 437-month RBI-origin secondary mirror with limited first-party-published anchors. Continuous NSE G-Sec TRI is not qualified. | Choose a decision-relevant Growth-plan subset; acquire AMFI scheme-specific NAV from each product's true inception, retain URL/UTC/bytes/hash and stop-on-429 checkpoints, validate identifier/date continuity, then strict-common-date join. Keep ETF NAV distinct from market price; never backfill before launch. If no first-party G-Sec TRI, retain LIC only as proxy and direct bonds as dated-cashflow instruments. |
| Joined deterministic after-tax path | **OPEN — G6 implementation increment** | Passing tax/event and G3 modules have separate contracts; no strategy-path adapter ties candidate prices/fees, lots, tax years, exit, and CPI together. | Implement a fixture-first adapter; independently reconcile one lot, one annual tax result and terminal gross→fees/tax→net→provisional real. Fail closed on unknown product tax classification. |
| CPI byte provenance and personal anchor | **PARTIAL, not a synthetic-engine blocker** | Published values match; source captures are transcriptions, and the investor's measurement/base month is not confirmed. | Preserve available official release/export bytes and hash them; retain provisional CPI status until byte provenance is improved. Keep personal real wealth blocked until actual base/measurement dates are confirmed. |
| Access, suitability and personal tax facts | **FOLLOW-ON — blocks personal result/recommendation** | Account availability, risk constraints, tax-year income/losses/regime, actual dates/fees and exit choice are not supplied. | Collect only at investor-specific decision stage; no credentials or trade activity. Do not invent defaults. |
| Cross-asset uncertainty and probability | **NOT STARTED / BLOCKED ON HISTORY** | No qualified common-date multi-asset dataset or validated walk-forward/sequence/tail calibration. | Start only after source series and deterministic bridge pass; then pre-register methods, use adverse/regime and parameter uncertainty, and publish no probability until calibration is supported. |

## G6 entry levels

| Level | Status | Allowed scope |
|---|---|---|
| G6 engineering start | **READY** | Deterministic fixture-first bridge only, with synthetic dates/taxes/returns clearly labeled; use component contracts and fail closed on unknown fields. |
| G6 decision-grade output | **NOT READY** | Requires selected continuous source histories, joined after-tax event path, CPI source/base disposition, and independent end-to-end/adverse-case audit. |
| Investor-specific recommendation / trading | **NO-GO** | Requires actual investor facts, current instrument access/execution/suitability and separate investor approval. No trading is authorized. |

## Next execution sequence

1. G5 source-history lane: qualify a bounded set of actual AMFI Growth products from inception; do not retrieve an unbounded universe. Use published official source endpoints and respect 429 by pausing/checkpointing.
2. G6 deterministic bridge lane: start from the 120/122-month synthetic schedule and passed Sprint 1 ledger; map one qualified candidate path and explicitly modeled fee/tax/exit events; use provisional CPI only with its status attached.
3. Independent audit the joined result and mutation cases (date misalignment, pre-inception fill, wrong plan, duplicate fee/tax, missing classification, unknown CPI base).
4. Only after these pass, reassess decision-grade G6 entry. Probabilistic work remains a later gate, not implied by G6 start.

## Evidence

- [Sprint 1 closure record](https://github.com/K49M43/testrepo/blob/main/docs/SPRINT_01_AFTER_TAX_LEDGER.md)
- [Execution plan status](https://github.com/K49M43/testrepo/blob/codex/g5-4-candidate-screen-g6-readiness-20261105/docs/CODEX_EXECUTION_PLAN.md)
- [G5.4 candidate and TER evidence](candidate_expansion_v1.json), [TER audit](ter_row_audit.json), [NAV reconciliation](nav_sample_reconciliation.json)
- [R9 source-resolution report](https://github.com/K49M43/testrepo/blob/main/research/stage512/2026-11-02/stage512_source_resolution_report.md)
- [G3 outcome contract](https://github.com/K49M43/testrepo/blob/main/research/stage512/2026-11-04/g3_outcome_contract_v1.json)

## Source-history blocker update — 2026-11-05

Five official AMFI Growth-option NAV histories now pass an offline raw-to-normalized audit: Motilal Nifty 500 Index Fund Direct Growth (1,761 rows; 15/15 windows), HDFC Gold ETF (2,918; 24/24), ICICI Prudential Silver ETF (1,160; 10/10), SBI Nifty 500 Index Fund Direct Growth (520; 5/5), and SBI June 2036 target-maturity Gilt Index Fund Direct Growth (994; 9/9). The audit checks each raw SHA-256 and byte count, exact scheme/ISIN/plan/option, window partitions, positive Decimal NAV, no duplicates, CSV reconstruction, and no >12-day observed gap. Total: 7,353 observations in 63 retained raw windows.

Strict calendar-month joins to the existing 129 published NSE Nifty 500 TRI monthly observations have 72 common months for Motilal Nifty 500 fund, 128 for gold, 44 for silver, 11 for SBI Nifty 500 fund, and 35 for SBI June 2036 gilt fund. These are descriptive, rounded-month overlaps only. They do not qualify daily covariance, market-price execution, sovereign total-return equivalence, or probabilistic confidence.

The first June 2036-fund parse exposed AMFI’s `SBI |CRISIL...` naming alias and a fetcher defect: a rejected HTTP 200 body was not saved before parsing. The alias was confirmed against previously retained AMFI rows for scheme 150681 and ISIN INF200KA12Q9; the fetcher was corrected to persist raw responses immediately, and a bounded 9-window rerun then passed. The first rejected response is explicitly excluded from the evidence set.

Reproduce using `python research/stage512/2026-11-05/g5_4/audit_g5_candidate_nav_history.py` followed by `python research/stage512/2026-11-05/g5_4/audit_g5_4.py`. See [candidate history blocker resolution](CANDIDATE_HISTORY_BLOCKER_RESOLUTION.md) and `candidate_nav_history_audit.json` for exact evidence and next gates.

**Current distinction:** the 10 product hypotheses now have a documented disposition, and G6 fixture-first deterministic engineering remains READY. Decision-grade G6 and investment authorization remain NOT READY / NO-GO. Remaining source gates are direct GoI/T-Bill dated cashflows and ETF market-price execution where selected, followed by the joined after-tax cashflow path.

