# Independent statutory tax review — 3 November 2026

**Review type:** source-based technical audit of the bounded TY 2026–27 resident-individual research component. This is not a qualified tax opinion, return review, or professional sign-off. No external tax professional was contacted.

**Status:** one section 156 implementation defect was identified and corrected with a regression fixture. The investor accepts this source-based review against enacted Act text as satisfying Sprint 1's review gate. This is not a tax-professional opinion. Provisional modeling conventions and incomplete features remain as listed below; investment authorization remains **NO-GO**.

## Scope and method

Compared the repository's tax rules, calculation component, loss-schedule boundary, and synthetic audit cases with the Income-tax Act, 2025 and Finance Act, 2026. Recomputed a mixed-income rebate example independently. The review was limited to provisions represented or explicitly deferred by the repository; it did not validate a taxpayer's facts, security classifications, return positions, or future-year tax treatment.

Primary sources: [Income-tax Act, 2025 (official Income Tax Department PDF)](https://incometaxindia.gov.in/Documents/Act/Income-tax-Act-2025.pdf), especially sections 108, 111, 121, 156, 196–198, 202, 263, 516 and 536; [Finance Act, 2026 (official Income Tax Department PDF)](https://www.incometaxindia.gov.in/documents/d/guest/finance-act-2026-pdf-1); and the Department's [Income-tax Act, 2025 and transition materials](https://www.incometax.gov.in/iec/foportal/help/all-topics/income-tax-act-2025).

## Findings

| ID | Severity | Finding | Disposition |
|---|---|---|---|
| T-01 | High | Section 156 mixed-income rebate formula used only section 202 slab tax to calculate marginal relief. Section 156(2) refers to income-tax payable on total income; subsection (3) separately caps the rebate at section 202(1) tax. Section 198(7) further excludes tax attributable to qualifying section 198 gains. | **Corrected and source-review gate accepted by investor.** The helper now accepts pre-rebate total income-tax, subtracts section 198 tax for the rebate base, and separately caps the result at section 202 tax. A section 196 case with ₹11.90L ordinary income and ₹0.50L qualifying STCG now calculates ₹29,000 rebate (₹59,000 section 202 tax; ₹10,000 section 196 tax), versus the prior ₹19,000. This is a source-based interpretation, not a tax-professional opinion. |
| T-02 | High | Section 516 requires statutory rounding of computed total income and amounts payable/refundable, but does not itself prescribe which income category absorbs a rounding residual among ordinary income, dividend income, and separately taxed gains. | **Accepted modeling convention for Sprint 1 research scope.** The engine preserves dividend and special-rate buckets, allocates residual to ordinary income, and fails closed on negative residual. Recheck against TY 2026–27 return forms when applicable; this allocation is not claimed to be prescribed by section 516. |
| T-03 | High | Finance Act 2026 section 3(5) states a tax-plus-surcharge ceiling for marginal relief. The calculator's mixed-income reference case holds dividend/special gains constant and changes ordinary income to reach the threshold. This composition is an implementation choice, not a directly specified statutory allocation algorithm. | **Accepted modeling convention for Sprint 1 research scope.** Keep the assumption visible and fail closed when the reference composition cannot fit. The investor accepts source-based review for this bounded research model; do not treat the convention as explicit statutory text or as investor-specific tax advice. |
| T-04 | Medium | Sections 108/111 set same-year and carried-forward capital-loss character rules; section 121 conditions carry-forward/set-off on the prescribed return; section 536(2)(n) preserves eligible legacy capital losses under the repealed Act's rules and remaining period. The repository's schedule is candidate-only and rejects unsupported pre-2026 treatment. | **Safe boundary; feature incomplete.** No candidate offset reaches tax. Before integration, validate original-year loss, character, timely section 263(1) filing, evidence/assessment status, expiry, and transition-year treatment. Preserve the original remaining carry-forward term. |
| T-05 | Medium | Section 76 specified-fund gains remain capital gains deemed short-term for tax treatment; describing them as ordinary-rate income is a rate-bucket shorthand and can be confused with the statutory income head. Scheme qualification must be proven from the applicable statutory definition and annual composition. | **Documentation clarification required before broad integration.** Keep section 76 gains in the capital-gains/loss schedule while applying the statutory rates in force. Do not infer that the LIC gilt ETF qualifies without security- and year-specific evidence. |
| T-06 | Medium | Supported code covers only a bounded resident-individual TY 2026–27 case. It excludes several taxpayer classes and interactions, including full taxpayer-year deductions/credits, complete losses, and verified investor-specific facts. | **Scope control passes; engine is not return-ready.** Inputs and omitted cases must remain explicit, with fail-closed behavior. |

## Statutory mechanics checked at bounded scope

- Sections 108 and 111 distinctions between current-year and carried-forward short/long-term capital losses, including the eight succeeding tax-year limit, are represented in the candidate schedule. Section 121's timely-return gate is enforced for carry-forward eligibility; actual filing and assessment evidence is not verified by the engine.
- Section 156's ₹12 lakh threshold, ₹60,000 cap, total-income formula, and section 202(1) cap are represented. The new mixed section 196 fixture specifically tests the formula/cap distinction. Section 198(7)'s special rebate rule is represented for eligible section 198 gains. Other mixed-rate interactions remain open.
- Sections 196, 197, and 198 rates/eligibility are gated by explicit input predicates. The code does not establish security identity, STT, holding period, or the taxpayer's eligibility.
- Section 202 surcharge tiers and the Finance Act 2026 special-income cap and cess order are exercised by synthetic boundary fixtures. Mixed-composition marginal relief remains provisional.
- Section 516 rupee-rounding arithmetic is exercised, but category allocation of total-income residual remains provisional.

## Validation performed

- `python decision/audit_ty2026_27_tax_components.py` — PASS, including the new mixed section 196 rebate regression.
- `python decision/audit_after_tax_event_ledger.py` — PASS; loss candidate stays barred from tax, and synthetic ledger outputs reconcile.
- `python decision/audit_capital_gain_loss_schedule.py` — PASS; candidate loss mechanics and evidence gates reconcile.
- `python decision/audit_terminal_case_reconciliation.py` — PASS; six synthetic cases and 120/122 month contribution totals reconcile.
- `python decision/audit_terminal_case_reconciliation.py --check` — PASS; committed terminal artifact matches regeneration.

These are software and arithmetic checks. They do not replace the Act text or establish investor-specific facts. After correcting a stale terminal-artifact hash discovered by CI, all four GitHub Actions checks passed on PR #12 head `b2943707c3367c49a4efc73f3642a97f3f5ab72f`: [source run 41680195664](https://github.com/K49M43/testrepo/actions/runs/41680195664), [source run 41680204595](https://github.com/K49M43/testrepo/actions/runs/41680204595), [tax/ledger run 41680195607](https://github.com/K49M43/testrepo/actions/runs/41680195607), and [tax/ledger run 41680204741](https://github.com/K49M43/testrepo/actions/runs/41680204741). The PR remains draft and unmerged.

## Required next gates

1. Implement the statutory loss rules and transition treatment from T-04 in the event-to-tax-year pipeline, preserving documented evidence and fail-closed states for unsupported cases.
2. Independently recalculate representative mixed-income and gain/loss cases outside the production functions; keep accepted T-02/T-03 conventions labeled and visible.
3. Confirm applicable TY 2026–27 return forms/instructions and security-level facts before producing any investor-specific estimate.
4. Run and verify the complete GitHub Actions suite on the final PR head, complete review, and merge the PR. Sprint 1 cannot close while its loss/tax pipeline and required reviewable delivery remain incomplete.

No investor-specific tax result is qualified. Investment authorization remains **NO-GO**.
