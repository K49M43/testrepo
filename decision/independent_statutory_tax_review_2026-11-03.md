# Independent statutory tax review — 3 November 2026

**Review type:** source-based technical audit of the bounded TY 2026–27 resident-individual research component. This is not a qualified tax opinion, return review, or professional sign-off. No external tax professional was contacted.

**Status:** one section 156 implementation defect was identified and corrected locally with a regression fixture. The interpretation still requires qualified review. Sprint 1 tax acceptance remains open; investment authorization remains **NO-GO**.

## Scope and method

Compared the repository's tax rules, calculation component, loss-schedule boundary, and synthetic audit cases with the Income-tax Act, 2025 and Finance Act, 2026. Recomputed a mixed-income rebate example independently. The review was limited to provisions represented or explicitly deferred by the repository; it did not validate a taxpayer's facts, security classifications, return positions, or future-year tax treatment.

Primary sources: [Income-tax Act, 2025 (official Income Tax Department PDF)](https://incometaxindia.gov.in/Documents/Act/Income-tax-Act-2025.pdf), especially sections 108, 111, 121, 156, 196–198, 202, 263, 516 and 536; [Finance Act, 2026 (official Income Tax Department PDF)](https://www.incometaxindia.gov.in/documents/d/guest/finance-act-2026-pdf-1); and the Department's [Income-tax Act, 2025 and transition materials](https://www.incometax.gov.in/iec/foportal/help/all-topics/income-tax-act-2025).

## Findings

| ID | Severity | Finding | Disposition |
|---|---|---|---|
| T-01 | High | Section 156 mixed-income rebate formula used only section 202 slab tax to calculate marginal relief. Section 156(2) refers to income-tax payable on total income; subsection (3) separately caps the rebate at section 202(1) tax. Section 198(7) further excludes tax attributable to qualifying section 198 gains. | **Corrected locally, pending independent sign-off.** The helper now accepts pre-rebate total income-tax, subtracts section 198 tax for the rebate base, and separately caps the result at section 202 tax. A section 196 case with ₹11.90L ordinary income and ₹0.50L qualifying STCG now calculates ₹29,000 rebate (₹59,000 section 202 tax; ₹10,000 section 196 tax), versus the prior ₹19,000. The change is deliberately classified as a statutory interpretation pending professional review, not a tax opinion. |
| T-02 | High | Section 516 requires statutory rounding of computed total income and amounts payable/refundable, but does not itself prescribe which income category absorbs a rounding residual among ordinary income, dividend income, and separately taxed gains. | **Open; provisional behavior retained.** The engine preserves dividend and special-rate buckets, allocates residual to ordinary income, and fails closed on negative residual. Confirm using TY 2026–27 return forms/instructions and qualified review. |
| T-03 | High | Finance Act 2026 section 3(5) states a tax-plus-surcharge ceiling for marginal relief. The calculator's mixed-income reference case holds dividend/special gains constant and changes ordinary income to reach the threshold. This composition is an implementation choice, not a directly specified statutory allocation algorithm. | **Open; provisional behavior retained.** Keep the assumption visible and fail closed when the reference composition cannot fit. Obtain a written professional disposition and build independently hand-calculated mixed-rate cases before using it for investor tax. |
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

These are software and arithmetic checks. They do not validate legal interpretation or constitute tax-professional review. After correcting a stale terminal-artifact hash discovered by CI, all four GitHub Actions checks passed on PR #12 head `ccf540a0401062fef85ddf63378f6bdfb123781f`: [source run 41680005503](https://github.com/K49M43/testrepo/actions/runs/41680005503), [source run 41680022949](https://github.com/K49M43/testrepo/actions/runs/41680022949), [tax/ledger run 41680005895](https://github.com/K49M43/testrepo/actions/runs/41680005895), and [tax/ledger run 41680023136](https://github.com/K49M43/testrepo/actions/runs/41680023136). The PR remains draft and unmerged.

## Required next gates

1. Obtain a written qualified tax-professional disposition for T-01 through T-05, particularly section 156 with section 196/197 gains, section 516 category allocation, mixed-income surcharge relief, and loss cross-bucket application.
2. Amend the tax component and worked cases only to implement the accepted dispositions; retain fail-closed states for unresolved cases.
3. Complete event-to-tax-year aggregation including supported loss offsets, withholding, credits, and tax payment timing; independently recalculate representative cases outside the production functions.
4. Confirm applicable TY 2026–27 return forms/instructions and security-level facts before producing any investor-specific estimate.
5. Run and verify the complete GitHub Actions suite on the resulting PR head. Sprint 1 cannot close on synthetic code checks alone.

No investor-specific tax result is qualified. Investment authorization remains **NO-GO**.
