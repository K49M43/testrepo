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

## Required loss-engine acceptance cases

1. Same-year short-term loss can offset short- or long-term capital gains but not ordinary coupon/dividend income. Test both allocations across different statutory-rate buckets unless an authoritative rule fixes the allocation order.
2. Same-year long-term loss cannot offset any short-term gain or ordinary income.
3. Carried-forward short-term and long-term loss enforce the distinct section 111 restrictions above.
4. A loss expires after eight succeeding tax years; an ineligible / late return cannot seed a carry-forward balance.
5. Old-Act losses preserve their original character, eligibility, and remaining carry-forward life through the section 536 transition.
6. Lots, event IDs, tax year, loss character, source basis, expenses, return filing/determination status, and original loss year remain traceable.
7. Annual loss use reconciles to gain buckets and cannot create negative taxable gains or cross the capital-gains head.
8. At least one independent tax-professional worked example must cover losses spanning differently taxed gain buckets before the integration gate can pass.

## Mixed special-income surcharge marginal relief — source review

Finance Act 2026 section 3(5) caps income tax plus surcharge near each surcharge threshold at the reference amount plus income above that threshold. The statutory formula does not provide a worked allocation for a threshold case with multiple ordinary and special-rate components. To make bounded progress, the calculator now uses a **provisional reference-composition convention**: hold dividend and special-rate income fixed, and reduce ordinary income to the threshold. It applies only when those held components fit within the threshold; otherwise it fails closed. This convention is tested at ₹50L and ₹1Cr but has not received professional review and must not be presented as a qualified legal interpretation.

Additional acceptance cases must cover ordinary income plus special gains immediately below and above ₹50L, ₹1Cr, and ₹2Cr, including the 15% special-income surcharge cap, basic-exemption adjustment, and section 198 annual deduction. Cess is computed after income tax and surcharge; the Finance Act says marginal relief does not apply to cess.

Primary source: [Finance Act 2026 section 3](https://indiacode.ecourtsindia.com/finance-act-2026/section/3/), especially subsections (4), (5), and (15); Department [Finance Bill Memorandum, marginal-relief notes](https://www.incometaxindia.gov.in/documents/81799/11848482/memo-2026.pdf/fe530cfa-9c49-fc5c-4bfa-fc96fd5e7b7a?t=1770008674037).

## Section 516 integration boundary

The `section516_round_rupees` primitive is covered by boundary cases and is applied to final payable/refundable balances after credits. Integration remains open for rounding statutory total income and specifying how the rounded total controls threshold selection while preserving distinct rate buckets. The final payable/refundable result is distinguished from the ledger's counterfactual incremental portfolio tax, which is not itself a statutory assessment amount.

## External Sprint 1 gates

- No qualified Indian tax professional has reviewed the worked cases; repository instructions prohibit assuming or making that contact without separate authorization.
- Actual security IDs, dates, charges, personal tax-year income/loss/return facts, and CPI base month have not been confirmed.
- Future tax-year rules through 2036 are not enacted today and must be refreshed for each modeled tax year; TY 2026–27 rates cannot be projected as law through 2036.
- GitHub CLI is installed but unauthenticated; this branch's local commits have not been pushed or checked remotely.

Sprint 1 remains in progress. Investment authorization remains **NO-GO**.
