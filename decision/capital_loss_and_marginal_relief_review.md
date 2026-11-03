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

These cases intentionally do not calculate tax. A reviewer should return a signed disposition for each question, identify any governing return-form/rule instruction, and state whether the resulting rule is mandatory, taxpayer-elective, or still ambiguous. If ambiguity remains, the implementation must preserve explicit candidate scenarios and keep tax application unqualified until a compliant selection rule is established.

### Reviewer acceptance

1. Every permitted and prohibited loss-to-gain pair has a source-supported rule.
2. The allocation mechanism does not let capital losses offset coupons, dividends, withholding credits, or unrealized gains.
3. The reviewer decides the interaction with sections 76 and 198, the section 198 deduction, statutory total-income rounding, and surcharge/marginal relief.
4. The reviewer confirms the return and determination evidence needed for section 121 and the section 536 transition for legacy losses.
5. One independent hand calculation covers the full tax year with external income, portfolio gains, portfolio losses, credits, and a full-tax versus external-only comparison.

Until those five checks are signed off, the next implementation gate may validate arithmetic and candidate schedules but must not feed losses into the tax calculator.

## Mixed special-income surcharge marginal relief — source review

Finance Act 2026 section 3(5) caps income tax plus surcharge near each surcharge threshold at the reference amount plus income above that threshold. The statutory formula does not provide a worked allocation for a threshold case with multiple ordinary and special-rate components. To make bounded progress, the calculator now uses a **provisional reference-composition convention**: hold dividend and special-rate income fixed, and reduce ordinary income to the threshold. It applies only when those held components fit within the threshold; otherwise it fails closed. This convention is tested at ₹50L and ₹1Cr but has not received professional review and must not be presented as a qualified legal interpretation.

Additional acceptance cases must cover ordinary income plus special gains immediately below and above ₹50L, ₹1Cr, and ₹2Cr, including the 15% special-income surcharge cap, basic-exemption adjustment, and section 198 annual deduction. Cess is computed after income tax and surcharge; the Finance Act says marginal relief does not apply to cess.

Primary source: [Finance Act 2026 section 3](https://indiacode.ecourtsindia.com/finance-act-2026/section/3/), especially subsections (4), (5), and (15); Department [Finance Bill Memorandum, marginal-relief notes](https://www.incometaxindia.gov.in/documents/81799/11848482/memo-2026.pdf/fe530cfa-9c49-fc5c-4bfa-fc96fd5e7b7a?t=1770008674037).

## Section 516 integration boundary

The `section516_round_rupees` primitive is covered by boundary cases and is applied to final payable/refundable balances after credits. Integration remains open for rounding statutory total income and specifying how the rounded total controls threshold selection while preserving distinct rate buckets. The final payable/refundable result is distinguished from the ledger's counterfactual incremental portfolio tax, which is not itself a statutory assessment amount.

### Worked case for reviewer

Use raw computed total income of ₹50,00,004, which section 516 rounds to ₹50,00,000:

| Composition | Raw component tax arithmetic before surcharge/cess | If the ₹4 rounding residual reduces the ordinary-rate base | If the ₹4 residual reduces section 196 gain |
|---|---:|---:|---:|
| Ordinary income ₹50,00,004 | Section 202 tax = ₹10,80,001.20 | Section 202 tax on ₹50,00,000 = ₹10,80,000.00 | Not applicable |
| Ordinary income ₹49,00,004 + section 196 STCG ₹1,00,000 | Section 202 tax ₹10,50,001.20 + section 196 tax ₹20,000 = ₹10,70,001.20 | Section 202 tax ₹10,50,000 + section 196 tax ₹20,000 = ₹10,70,000.00 | Section 202 tax ₹10,50,001.20 + section 196 tax on ₹99,996 = ₹10,70,000.40 |

These are alternative arithmetic treatments to review, not a claim that both are legally available. They expose the precise question: does section 516's deemed total feed the section 202/196 component formula before tax, and does the special-rate formula determine the residual base as rounded total income less the special gain? The reviewer should extend this to sections 197/198, dividends, basic-exemption adjustment, section 198's annual deduction, rebate, surcharge, and marginal relief. Tests should then use the signed-off formula, not reverse-engineer one from current outputs.

## Section 156 mixed-income threshold review

The calculator now tests the section 156(2) ₹12 lakh threshold against total income while limiting the rebate amount to section 202(1) tax. This follows section 156(2)(b)'s explicit total-income test and section 156(3)'s cap, with section 198(7) separately specifying the treatment of qualifying long-term gains. Regression fixtures cover total income of ₹12,00,000, ₹12,00,010, and ₹12,20,000 with ordinary income held at ₹11,90,000. These fixtures are arithmetic probes of the statutory wording, not independent legal sign-off. The threshold basis, interaction with section 516 rounding, and any applicable treatment under other special-rate provisions remain for qualified review.

## External Sprint 1 gates

- No qualified Indian tax professional has reviewed the worked cases; repository instructions prohibit assuming or making that contact without separate authorization.
- Actual security IDs, dates, charges, personal tax-year income/loss/return facts, and CPI base month have not been confirmed.
- Future tax-year rules through 2036 are not enacted today and must be refreshed for each modeled tax year; TY 2026–27 rates cannot be projected as law through 2036.
- GitHub CLI 2.103.3 is installed and authenticated as K49M43. Draft PR #12 remains open and draft. Commit `d30b392` corrected a withholding-validation bypass; its first tax/ledger run failed because the committed terminal-case artifact still pinned the prior ledger hash. The artifact was regenerated, and all four checks passed at head `490d58f7d384b6461ac352731827aa879f96342f` (source runs [41641092334](https://github.com/K49M43/testrepo/actions/runs/41641092334), [41641103275](https://github.com/K49M43/testrepo/actions/runs/41641103275); tax/ledger runs [41641092340](https://github.com/K49M43/testrepo/actions/runs/41641092340), [41641103282](https://github.com/K49M43/testrepo/actions/runs/41641103282)). No review decision is recorded. Passing software checks do not close the tax-policy review gate.

Sprint 1 remains in progress. Investment authorization remains **NO-GO**.
