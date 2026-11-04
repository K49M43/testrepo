# Independent statutory tax review — 3 November 2026

**Review type:** source-based technical audit of the bounded TY 2026–27 resident-individual research component. This is not a qualified tax opinion, return review, or professional sign-off. No external tax professional was contacted.

**Status:** one section 156 implementation defect was identified and corrected with a regression fixture. The investor accepts this source-based review against enacted Act text as satisfying Sprint 1's review gate. This is not a tax-professional opinion. Provisional modeling conventions and incomplete features remain as listed below; investment authorization remains **NO-GO**.

**Implementation update (4 November 2026):** explicit source-linked offsets now flow through the bounded event-to-tax-year adapter for supported current-year and carried-loss cases. A separate Decimal audit independently recalculates the supported tax and settlement arithmetic, and ledger fixtures cover loss application to sections 76/196/197/198. Pre-2026 transition losses and aggregate-only external capital gains remain unsupported and fail closed.

## Scope and method

Compared the repository's tax rules, calculation component, loss-schedule boundary, and synthetic audit cases with the Income-tax Act, 2025 and Finance Act, 2026. Recomputed a mixed-income rebate example independently. The review was limited to provisions represented or explicitly deferred by the repository; it did not validate a taxpayer's facts, security classifications, return positions, or future-year tax treatment.

Primary sources: [Income-tax Act, 2025 (official Income Tax Department PDF)](https://incometaxindia.gov.in/Documents/Act/Income-tax-Act-2025.pdf), especially sections 108, 111, 121, 156, 196–198, 202, 263, 516 and 536; [Finance Act, 2026 (official Income Tax Department PDF)](https://www.incometaxindia.gov.in/documents/d/guest/finance-act-2026-pdf-1); and the Department's [Income-tax Act, 2025 and transition materials](https://www.incometax.gov.in/iec/foportal/help/all-topics/income-tax-act-2025).

## Findings

| ID | Severity | Finding | Disposition |
|---|---|---|---|
| T-01 | High | Section 156 implementation omitted subsection (1)'s resident rebate up to ₹12,500 for total income ≤₹5 lakh. It also used only section 202 tax for subsection (2)'s mixed-income formula. Section 156(2) refers to tax payable on total income; subsection (3) separately caps that rebate at section 202(1) tax. Section 198(7) excludes tax attributable to qualifying section 198 gains. | **Both paths implemented; source-review gate accepted by investor.** Section 156(1) now applies its ₹12,500 limit to tax on total income, net of section 198 tax; when needed, it reduces non-section-198 special-rate tax after section 202 tax is exhausted. Section 156(2) uses pre-rebate total-income tax net of section 198 tax and separately caps at section 202 tax. Fixtures cover ₹4 lakh ordinary income plus ₹1 lakh section 196 gain (₹12,500 rebate; ₹7,800 final tax including cess) and ₹11.90 lakh ordinary income plus ₹0.50 lakh section 196 gain (₹29,000 rebate, versus the prior ₹19,000). This is source-based statutory implementation, not a tax-professional opinion. |
| T-02 | High | Section 516 requires statutory rounding of computed total income and amounts payable/refundable, but does not itself prescribe which income category absorbs a rounding residual among ordinary income, dividend income, and separately taxed gains. | **Accepted modeling convention for Sprint 1 research scope.** The engine preserves dividend and special-rate buckets, allocates residual to ordinary income, and fails closed on negative residual. Recheck against TY 2026–27 return forms when applicable; this allocation is not claimed to be prescribed by section 516. |
| T-03 | High | Finance Act 2026 section 3(5) states a tax-plus-surcharge ceiling for marginal relief. The calculator's mixed-income reference case holds dividend/special gains constant and changes ordinary income to reach the threshold. This composition is an implementation choice, not a directly specified statutory allocation algorithm. | **Accepted modeling convention for Sprint 1 research scope.** Keep the assumption visible and fail closed when the reference composition cannot fit. The investor accepts source-based review for this bounded research model; do not treat the convention as explicit statutory text or as investor-specific tax advice. |
| T-04 | Medium | Sections 108/111 set same-year and carried-forward capital-loss character rules; section 121 conditions carry-forward/set-off on the prescribed return; section 536(2)(n) preserves eligible legacy capital losses under the repealed Act's rules and remaining period. | **Supported path integrated; transition feature remains incomplete.** Explicit source-linked current-year and carried-forward allocations are validated for character, amount caps, tax year, timely-return evidence, and expiry, then applied before tax. No allocation priority is inferred. Pre-2026 transition losses remain fail-closed pending their distinct statutory representation and tests. |
| T-05 | Medium | Section 76 specified-fund gains remain capital gains deemed short-term for tax treatment; describing them as ordinary-rate income is a rate-bucket shorthand and can be confused with the statutory income head. Scheme qualification must be proven from the applicable statutory definition and annual composition. | **Documentation clarification required before broad integration.** Keep section 76 gains in the capital-gains/loss schedule while applying the statutory rates in force. Do not infer that the LIC gilt ETF qualifies without security- and year-specific evidence. |
| T-06 | Medium | Supported code covers only a bounded resident-individual TY 2026–27 case. It excludes several taxpayer classes and interactions, including full taxpayer-year deductions/credits, complete losses, and verified investor-specific facts. | **Scope control passes; engine is not return-ready.** Inputs and omitted cases must remain explicit, with fail-closed behavior. |

## Statutory mechanics checked at bounded scope

- Sections 108 and 111 distinctions between current-year and carried-forward short/long-term capital losses, including the eight succeeding tax-year limit, are represented in the candidate schedule. Section 121's timely-return gate is enforced for carry-forward eligibility; actual filing and assessment evidence is not verified by the engine.
- Section 156(1)'s ₹5 lakh/₹12,500 rebate, section 156(2)'s ₹12 lakh/₹60,000 total-income formula, the section 202(1) cap for subsection (2), and section 198(7)'s exclusion are represented. Fixtures exercise both rebate paths with section 196 gains. Other mixed-rate interactions remain outside the bounded supported cases.
- Sections 196, 197, and 198 rates/eligibility are gated by explicit input predicates. The code does not establish security identity, STT, holding period, or the taxpayer's eligibility.
- Section 202 surcharge tiers and the Finance Act 2026 special-income cap and cess order are exercised by synthetic boundary fixtures. Mixed-composition marginal relief remains provisional.
- Section 516 rupee-rounding arithmetic is exercised, but category allocation of total-income residual remains provisional.

## Validation performed

- `python decision/audit_ty2026_27_tax_components.py` — PASS, including the new mixed section 196 rebate regression.
- `python decision/audit_independent_loss_tax_reconciliation.py` — PASS; independently recomputes both section 156 paths, mixed surcharge relief, section 76/198 loss cases, and carried section 197 loss with section 516 rounding, cess, withholding, and settlement.
- `python decision/audit_after_tax_event_ledger.py` — PASS; explicit same-year and carried-loss offsets reach bounded tax for sections 76/196/197/198, with unsupported external gains failing closed.
- `python decision/audit_capital_gain_loss_schedule.py` — PASS; validated allocations, character/evidence gates, and ledger-to-tax application reconcile.
- `python decision/audit_terminal_case_reconciliation.py` — PASS; six synthetic cases and 120/122 month contribution totals reconcile.
- `python decision/audit_terminal_case_reconciliation.py --check` — PASS; committed terminal artifact matches regeneration.

These are software and arithmetic checks. They do not replace the Act text or establish investor-specific facts. The implementation and hand-reconciliation audit were pushed to PR #12 head `06c077a242a222489cca91c76579268e266ccee8`. Its source/cashflow PR run [41777179259](https://github.com/K49M43/testrepo/actions/runs/41777179259), tax/ledger push run [41777173912](https://github.com/K49M43/testrepo/actions/runs/41777173912), and tax/ledger PR run [41777179227](https://github.com/K49M43/testrepo/actions/runs/41777179227) all passed. PR #12 remains draft and unmerged with no review decision.

## Required next gates

1. Retain fail-closed behavior for pre-2026 transition losses and untraced outside gains; add those only as separately specified features with source evidence and tests.
2. Confirm applicable TY 2026–27 return forms/instructions and security-level facts before producing any investor-specific estimate.
3. Complete PR review and merge the PR. The bounded independent reconciliation and exact-head CI are complete; Sprint 1 delivery remains open until review and merge.

No investor-specific tax result is qualified. Investment authorization remains **NO-GO**.
