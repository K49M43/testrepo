# Sprint 1 tax mechanics: source review and implementation boundary

**Reviewed:** 3 November 2026  
**Scope:** TY 2026–27 resident-individual component model; research specification only. No personal tax result is qualified.

## Capital losses — statutory rules established

The official Income-tax Act, 2025 distinguishes loss netting in the same year from carry-forward:

| Case | Rule supported by statute | Source |
|---|---|---|
| Same-year short-term capital loss | Set off against income computed for any other capital asset in that year, including long-term gains. | Section 108(2)(a), [official Act PDF](https://www.incometaxindia.gov.in/Documents/Act/Income-tax-Act-2025.pdf) |
| Same-year long-term capital loss | Set off only against income computed for another long-term capital asset in that year. | Section 108(2)(b), [official Act PDF](https://www.incometaxindia.gov.in/Documents/Act/Income-tax-Act-2025.pdf) |
| Carried-forward short-term loss | Set off against capital-gains income from any other capital asset. | Section 111(1)(a)(i), [official Act PDF](https://www.incometaxindia.gov.in/Documents/Act/Income-tax-Act-2025.pdf), [Department section 111 page](https://www.incometaxindia.gov.in/w/section-111-102) |
| Carried-forward long-term loss | Set off only against long-term capital-gains income. | Section 111(1)(a)(ii), same sources |
| Carry-forward period | At most eight immediately succeeding tax years. | Section 111(2), same sources |
| Return / determination prerequisite | A loss must be determined in pursuance of a return filed under section 263(1) to be carried forward under section 111(1). | Section 121, [official Act PDF](https://www.incometaxindia.gov.in/Documents/Act/Income-tax-Act-2025.pdf) |
| Pre-1-April-2026 loss | Section 536 preserves its original character and the corresponding old-Act carry-forward/set-off treatment; eligibility is not revived if it was lost under the old Act. | Section 536; [Income Tax Department transition FAQ](https://www.incometax.gov.in/iec/foportal/help/all-topics/e-filing-services/set%20off/carry%20forward%20of%20losses%20-faq) |

These rules are enough to specify loss character, expiry, and return-status data. They are not enough to safely net losses into this calculator's separate section 76, 196, 197, and 198 tax buckets. A capital loss can change the amounts taxed at different rates, the section 198 annual allowance, surcharge, marginal relief, and the incremental tax comparison. The applicable computation and priority among those rate buckets need a reviewed worked case before implementation. Until then, realized losses must continue to fail closed.

## End-to-end integration finding

The current boundary is the source of the repeated blocker:

1. A disposal is valued from its lot basis and produces one signed economic gain.
2. Positive section 76 gain is folded into `YearIncome.ordinary_income`; positive sections 196/197/198 gains are placed in separate positive-only buckets.
3. A negative disposal raises before the event is completed in the lot/economic ledger.
4. The tax component receives only annual non-negative aggregates. There is no source-level gain/loss schedule between disposal classification and `TaxInput`.

That shape cannot support legally permitted loss set-off without either losing the original character or inventing an allocation. The minimal safe integration boundary is a **pre-tax capital-gains schedule** keyed by source event/lot and tax year. It must retain holding-period character (`short`/`long`) separately from the rate bucket (`section76`, `section196`, `section197`, `section198`). Coupon and dividend rows remain outside this schedule. A set-off allocation must identify both the loss source and gain destination; the calculator validates legal eligibility and arithmetic, then passes net positive buckets to the existing tax-component API. Unallocated/ambiguous offsets fail closed.

Compatibility invariants for that change:

- No-loss fixtures produce byte-for-byte equivalent tax inputs and the same terminal tax/wealth outputs.
- Economic disposal cash, residual units, basis, and portfolio conservation are computed whether the disposal produces a gain or loss; tax qualification is a separate result gate.
- Only realized capital-gain buckets participate in loss offsets; no loss reaches coupon, dividend, withholding, or unrealized-value fields.
- Gross gain, loss, offset, remaining taxable gain, and carried loss remain separately traceable to event and lot IDs.
- External-only taxpayer tax remains a separate calculation; portfolio incremental tax is still full-tax-with-portfolio minus external-only tax.
- The calculation does not choose an offset priority when law leaves a choice. It requires an explicit, auditable policy (or produces a clearly labeled sensitivity range once that range algorithm is independently validated).

The isolated schedule is implemented in `decision/capital_gain_loss_schedule.py` and audited by `decision/audit_capital_gain_loss_schedule.py`. Its trace adapter consumes the event ledger's gain and loss disposal records while excluding coupon/dividend rows. It accepts only source-linked, caller-selected offsets; validates same-year/carry-forward character, gain/loss caps, the eight-year window, and a declared section 263(1) return evidence reference; then returns separate gross, explicit-offset, candidate remaining-gain, and residual balances for each rate bucket. Its result explicitly sets `tax_application_allowed=false`. The main ledger does not yet invoke the adapter, and annual tax components do not consume its result. It does not select a priority, infer gain character, qualify tax inputs, or support pre-2026 transition losses. The integration gate remains closed until an independently reviewed allocation worked case establishes how offsets should be attributed among differently taxed gain buckets. The existing no-loss tax path and terminal-case builder remain untouched.

## Required loss-engine acceptance cases

1. Same-year short-term loss can offset short- or long-term capital gains but not ordinary coupon/dividend income. Test both allocations across different statutory-rate buckets unless an authoritative rule fixes the allocation order.
2. Same-year long-term loss cannot offset any short-term gain or ordinary income.
3. Carried-forward short-term and long-term loss enforce the distinct section 111 restrictions above.
4. A loss expires after eight succeeding tax years; an ineligible / late return cannot seed a carry-forward balance.
5. Old-Act losses preserve their original character, eligibility, and remaining carry-forward life through the section 536 transition.
6. Lots, event IDs, tax year, loss character, source basis, expenses, return filing/determination status, and original loss year remain traceable.
7. Annual loss use reconciles to gain buckets and cannot create negative taxable gains or cross the capital-gains head.
8. At least one independent tax-professional worked example must cover losses spanning differently taxed gain buckets before the integration gate can pass.

## Next gate — rate-bucket allocation review packet

The ledger-to-schedule trace adapter now passes synthetic integration. The next unresolved gate is not more adapter code: it is an approved rule for choosing or constraining loss allocations when the statute permits multiple capital-gain destinations. The examples below are arithmetic fixtures for review, not conclusions about a taxpayer's allowed choice or tax liability.

### Worked allocation cases

All amounts are ₹000. Tax buckets preserve the calculator's existing distinction: section 76 is deemed short-term but uses ordinary-rate tax treatment in this component model; sections 196, 197, and 198 retain their separate rate treatment. The official Act defines section 76 gains as short-term capital gains; its applicability and loss treatment still require product and legal confirmation. [Official section 76](https://www.incometaxindia.gov.in/w/section-76-102).

| Case | Gross gain buckets / loss | Allocation candidate 1 | Allocation candidate 2 | Reviewer must decide |
|---|---|---|---|---|
| A. Same-year STCL across rate buckets | §76 100; §196 100; §197 100; §198 250; STCL 150 | 100 to §76 + 50 to §196 → remaining 0 / 50 / 100 / 250 | 100 to §198 + 50 to §197 → remaining 100 / 100 / 50 / 150 | Are both allocations legally available, or is an ordering prescribed? What is the allowable selection basis? |
| B. Same-year LTCL | §76 100; §196 100; §197 100; §198 250; LTCL 150 | 100 to §197 + 50 to §198 → remaining 100 / 100 / 0 / 200 | 150 to §198 → remaining 100 / 100 / 100 / 100 | Confirm §76/§196 exclusions and whether section 197 vs 198 allocation is elective or ordered. |
| C. Carried STCL and LTCL | Use Case A gains; carried STCL 150 and LTCL 150 | Apply carried STCL to any eligible capital bucket; LTCL only to §197/§198 | Vary the explicit allocation while preserving character | Confirm section 111 use order, expiry by origin tax year, and return/determination evidence under sections 121 and 263(1). |
| D. Section 198 annual deduction interaction | §198 gross 250; STCL 100; compare offsets allocated to §198 vs another eligible bucket | Candidate §198 amount after offset = 150, then evaluate the annual deduction | Leave §198 at 250 and offset another eligible bucket | Confirm the legal order between capital-loss set-off and the section 198 annual deduction, including whether the deduction is once per taxpayer-year. |
| E. Section 76 negative result | Qualifying specified-fund unit with a computed negative result | Preserve as a short-term loss candidate under the applicable computation | Reject / separately classify if the section 76 formula or other provision disallows that result | Confirm whether and how a negative section 76 computation enters section 108 loss set-off. Do not assume ordinary treatment means ordinary-income loss. |
| F. Carry-forward eligibility | Residual current-year loss, one timely section 263(1) return case and one missing/late/ineligible case | Use only a loss determined in pursuance of qualifying return evidence | Reject carry-forward and preserve the source loss record | Define evidence fields: origin year, return type/date/due date, determination status, original character, balance and expiry. Test section 536 legacy losses separately. |

These cases intentionally do not calculate tax. For each question, record the statutory text, the chosen interpretation, whether the rule is mandatory or taxpayer-elective, and any remaining ambiguity. If ambiguity remains, preserve explicit candidate scenarios or fail closed rather than silently choosing an offset.

### Reviewer acceptance

1. Every permitted and prohibited loss-to-gain pair has a source-supported rule.
2. The allocation mechanism does not let capital losses offset coupons, dividends, withholding credits, or unrealized gains.
3. The audit records the interaction with sections 76 and 198, the section 198 deduction, statutory total-income rounding, and surcharge/marginal relief.
4. The implementation validates the return and determination evidence needed for section 121 and the section 536 transition for legacy losses.
5. One independent hand calculation covers the full tax year with external income, portfolio gains, portfolio losses, credits, and a full-tax versus external-only comparison.

Until those five checks are signed off, the next implementation gate may validate arithmetic and candidate schedules but must not feed losses into the tax calculator.

## Mixed special-income surcharge marginal relief — source review

Finance Act 2026 section 3(5) caps income tax plus surcharge near each surcharge threshold at the reference amount plus income above that threshold. The statutory formula does not provide a worked allocation for a threshold case with multiple ordinary and special-rate components. The calculator uses a **reference-composition convention**: hold dividend and special-rate income fixed, and reduce ordinary income to the threshold. It applies only when those held components fit within the threshold; otherwise it fails closed. This convention is tested at the statutory thresholds and is accepted by the investor for Sprint 1 research scope; it is not presented as a composition algorithm written in the Act.

Additional acceptance cases must cover ordinary income plus special gains immediately below and above ₹50L, ₹1Cr, and ₹2Cr, including the 15% special-income surcharge cap, basic-exemption adjustment, and section 198 annual deduction. Cess is computed after income tax and surcharge; the Finance Act says marginal relief does not apply to cess.

Primary source: [Finance Act 2026 section 3](https://indiacode.ecourtsindia.com/finance-act-2026/section/3/), especially subsections (4), (5), and (15); Department [Finance Bill Memorandum, marginal-relief notes](https://www.incometaxindia.gov.in/documents/81799/11848482/memo-2026.pdf/fe530cfa-9c49-fc5c-4bfa-fc96fd5e7b7a?t=1770008674037).

## Section 516 integration boundary

The component now records both raw computed total income and the deemed total income rounded under section 516. It uses the rounded total for the section 156 threshold, surcharge thresholds, and marginal-relief boundary. The normal-rate base is calculated as rounded total income less separately identified special-rate gains. Reported dividend income stays fixed and the rounding residual adjusts ordinary income; the component fails closed if this would make ordinary income negative.

This ordering is a provisional inference, not a bucket-allocation instruction in the Act. Section 516 deems the rounded computed total to be total income. The official ITR-2 instructions under predecessor section 288A direct rounding in the final total-income field, while their return structure calculates normal-rate tax separately from special-rate income. The Department says TY 2026–27 forms under the new Rules 2026 will be notified before filing, so the predecessor form is a workflow precedent only. The investor accepts the documented residual treatment for Sprint 1 research scope; recheck it against the applicable form before any return application. [Income-tax Act 2025, section 516](https://www.incometaxindia.gov.in/Documents/Act/Income-tax-Act-2025.pdf) · [Official ITR-2 instructions (predecessor Act)](https://incometaxindia.gov.in/Supporting%20Files/ITR2023/Instructions_ITR2_AY_2023_24.pdf/fe470b08-ceb7-340f-d2e3-d8fd1bf877b7?t=1765434371538&version=1.0) · [Income Tax Department return-form FAQ](https://www.incometax.gov.in/iec/foportal/help/all-topics/e-filing-services/%20income%20tax%20returns-faq)

Coverage now includes ₹10 rounding up/down, raw incomes one rupee above surcharge thresholds that round back to the threshold, the first rounded value above each ₹50L/₹1Cr/₹2Cr boundary, a mixed section 196 gain case, the section 156 threshold, and fail-closed dividend/negative-residual cases. This arithmetic coverage does not independently validate the statutory convention.

### Worked case: ₹50 lakh two-composition comparison

Use raw computed total income of ₹50,00,004, which section 516 rounds to ₹50,00,000. Under the current provisional convention, the special-rate gain remains ₹1,00,000 and the ₹4 residual reduces the normal-rate base:

| Composition | Raw component tax arithmetic before surcharge/cess | Provisional statutory component base used by the calculator |
|---|---:|---:|
| Ordinary income ₹50,00,004 | Section 202 tax = ₹10,80,001.20 | Section 202 tax on ₹50,00,000 = ₹10,80,000.00 |
| Ordinary income ₹49,00,004 + section 196 STCG ₹1,00,000 | Section 202 tax ₹10,50,001.20 + section 196 tax ₹20,000 = ₹10,70,001.20 | Section 202 tax on ₹49,00,000 = ₹10,50,000; section 196 tax on ₹1,00,000 = ₹20,000; total ₹10,70,000.00 |

The source audit records how this residual convention interacts with sections 197/198, dividends, basic-exemption adjustment, section 198's annual deduction, rebate, surcharge, and marginal relief. The investor accepts the convention for Sprint 1 research scope. The calculator fails closed if ordinary income would become negative after preserving dividend and special-rate buckets; revisit the handling if TY 2026–27 return forms specify another method.

## Section 156 mixed-income threshold review

The calculator tests the section 156(2) ₹12 lakh threshold against section 516 deemed total income. The statutory text distinguishes the formula base from the cap: section 156(2) refers to income-tax payable on total income, section 156(3) caps the deduction at section 202(1) tax, and section 198(7) excludes tax on qualifying section 198 gains from its rebate calculation. The helper therefore uses pre-rebate income-tax on total income (net of section 198 tax) for the formula, then caps the result at section 202 tax. A new section 196 mixed-income fixture covers the distinction. Regression fixtures also cover totals at ₹12,00,000, ₹12,00,010, and ₹12,20,000, including raw income that rounds across the threshold. The investor accepts this source-based interpretation for Sprint 1; broader taxpayer and special-rate combinations remain outside the supported fixture scope.

## External Sprint 1 gates

- No qualified Indian tax professional has reviewed the worked cases; repository instructions prohibit assuming or making that contact without separate authorization.
- Actual security IDs, dates, charges, personal tax-year income/loss/return facts, and CPI base month have not been confirmed.
- Future tax-year rules through 2036 are not enacted today and must be refreshed for each modeled tax year; TY 2026–27 rates cannot be projected as law through 2036.
- GitHub CLI 2.103.3 is installed and authenticated as K49M43. Draft PR #12 remains open and draft. Commit `d30b392` corrected a withholding-validation bypass; its first tax/ledger run failed because the committed terminal-case artifact still pinned the prior ledger hash. The artifact was regenerated, and all four checks passed at `490d58f7d384b6461ac352731827aa879f96342f`. Follow-up commit `4d05300` surfaces excess portfolio withholding as unvalued credit; all four checks passed at `4d0530068d5217a05ad72fde2ee5731e9b57fb35`. The section 516 integration commit `da81dd79687dc3e12918686d16f8f86ee410554e` also passed all four source/cashflow and tax/ledger checks (source runs [41657730366](https://github.com/K49M43/testrepo/actions/runs/41657730366), [41657742200](https://github.com/K49M43/testrepo/actions/runs/41657742200); tax/ledger runs [41657730109](https://github.com/K49M43/testrepo/actions/runs/41657730109), [41657742227](https://github.com/K49M43/testrepo/actions/runs/41657742227)). No review decision is recorded. Passing software checks do not close the tax-policy review gate.

Sprint 1 remains in progress. Investment authorization remains **NO-GO**.
