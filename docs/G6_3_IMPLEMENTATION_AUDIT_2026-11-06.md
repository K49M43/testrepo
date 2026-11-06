# G6.3 implementation audit — 2026-11-06

## Scope

Reviewed the G6.3 source inventory, CPI qualification checker and artifacts, sovereign-source disposition, G5.4 candidate/source lineage, and the bounded G6.1/G6.2 event/lot bridge and independent audits. This is a Codex review of repository evidence; it is not an external independent investment or tax opinion.

## Findings and resolution

| Severity | Finding | Resolution / residual status |
|---|---|---|
| High | The generated G6.3 source inventory still described original CPI bytes as unavailable after the CPI qualification PR added and verified those first-party artifacts. That made the machine-readable status stale and contradicted the CPI qualification report. | Corrected the inventory generator to report the CPI source-series gate as passed while leaving the investor-selected base month open; regenerated `source_inventory_v1.json`. |
| High | Joint-history overlap counts were constructed by intersecting calendar-month labels. The output did not say endpoint observation dates were not required to match. Treating these counts as strict date-aligned return intervals would create inconsistent month windows. | Added explicit `alignment_basis` and `eligible_for_joint_return_statistics: false` to each generated overlap. Updated the report: 57/48/24 are calendar-month-label counts only, not covariance inputs. Exact date-aligned counts remain to be computed before any joint-return statistics. |
| High | The sovereign note implied that Table 218's cutoff price and retail NCB weighted-average price were inherently different. RBI rules make their relationship conditional on the auction method: the FAQ states NCB uses weighted-average successful price and defines cutoff-price allocation for uniform-price auctions. Table 218 does not state row-level method or NCB weighted average. | Corrected the source note and machine record. No row is promoted to an investor price; the retail rollover path remains blocked pending auction-method, NCB allotment, and cashflow evidence. |
| Medium | CPI source qualification relied on Python `assert` for source identity and integrity checks; optimized Python removes assertions. The checker also did not validate every file recorded in the CPI source manifest against its byte count/hash. | Replaced assertions with explicit `require` checks and added manifest validation for each retained asset (unique filename, existence, HTTPS URL, HTTP 200, byte count and SHA-256). Normal and `python -O` qualification checks pass. |

## Reproduced checks

- `python decision/audit_g6_3_cpi_qualification.py --check` — PASS: 165 contiguous CPI observations, 144 linked observations reconcile at one-decimal source precision, 21 current observations match the source capture, September 2026 provisional.
- `python -O decision/audit_g6_3_cpi_qualification.py --check` — PASS with the same qualification.
- `python decision/audit_g6_3_source_inventory.py --check` — PASS after the stale CPI and overlap disclosure corrections.
- G5.4 manifest/source, five NAV histories, G5 exit acceptance, R9 history reconstruction, G5.1 lineage and G5.3 candidate evidence audits — PASS within their recorded bounded scope.
- G6.1 and G6.2 independent deterministic audits — PASS within synthetic fixture scope; lot/cash/tax reconciliation and declared mutation cases pass. Both explicitly report G6 `NOT_READY` and authorization `NO_GO`.

## Scope limits and residual blockers

1. G6.1/G6.2 validate accounting mechanics using synthetic marks, CPI and tax contexts. They do not validate actual candidate-specific economics, coupons/distributions, fees, execution, future law, XIRR, or probabilities.
2. The source inventory does not yet compute exact endpoint-date-aligned common returns. This must be implemented before any covariance, regime, or joint-risk result is consumed.
3. CPI source-series qualification is a pass; the investor's CPI base month and future inflation remain unresolved.
4. Retail T-bill acquisition/rollover and direct dated GoI bond paths remain unqualified; no current market execution inputs or product-specific account access are established.
5. The G6.3 issue's full WP0–WP4 gates have not passed. This audit supports the fallback NO-GO / NOT YET EVALUATED closeout pack but does not establish decision readiness or an investment recommendation.

## Audit disposition

No defect was found in the bounded G6.1/G6.2 fixture reconciliations during this review. The four G6.3 evidence-integrity/disclosure findings above are corrected in this closeout increment. Overall investment decision status remains **NO-GO / NOT YET EVALUATED**. Reopen decision-grade work only when the evidence and investor-confirmation gates listed in `docs/G6_3_FINAL_DECISION_PACK.md` can be satisfied.


## Post-merge verification

PR #48 head `f08242ab6fb68b4387363338b7019a87262bdc31` merged as `a44d13f44a82c0ca91cd09bc9f3e5212e14d51d0`. The Git tree IDs match, so the reviewed code/data tree is the merged tree. All eight exact-head workflows passed on both PR events; all eight merged-main workflows passed. The post-merge local rerun repeated CPI normal/optimized checks, source inventory, G5.4/NAV/exit/R9 audits, G5.1 and G5.3 audits, and both G6 deterministic audits. No new finding appeared. G6 remains `NOT_READY`; investment authorization remains `NO_GO`.
