# Section 202 surcharge examples — TY 2026–27

**As of:** 2 November 2026  
**Purpose:** arithmetic examples for reviewing the TY 2026–27 rule map before implementing investor tax calculations. These are not tax advice, return calculations, or portfolio results.

## Statutory rules applied

- Finance Act 2026, section 3(4)(a)(ii) excludes a section 202 taxpayer from the general surcharge treatment in section 3(4)(a) for sections 196, 197, and 198. Section 3(4)(b), Table row 10 separately applies surcharge to section 202 taxpayers.
- Under Table row 10, surcharge is 10% when total income is above ₹50 lakh and up to ₹1 crore; 15% above ₹1 crore and up to ₹2 crore; and 25% when total income **excluding** specified dividend income and sections 196/197/198 gains exceeds ₹2 crore. If total income exceeds ₹2 crore but the exclusion test for 25% is not met, the rate is 15%. The surcharge on tax attributable to sections 196/197/198 gains is capped at 15%.
- The section 202 surcharge schedule is capped at 25%; the 37% tier does not apply to a section 202 taxpayer.
- Finance Act section 3(5) provides marginal relief for section 202 taxpayers. For each listed interval, tax plus surcharge cannot exceed the tax plus surcharge at the lower threshold plus the amount by which total income exceeds that threshold. The illustrated relevant thresholds are ₹50 lakh, ₹1 crore, and ₹2 crore.
- Finance Act section 3(15) adds 4% cess on income-tax plus surcharge. Section 3(5) marginal relief does not reduce the cess.
- For section 202 taxpayers, the Finance Bill Memorandum explains that the 37% surcharge above ₹5 crore does not apply; the surcharge is restricted to 25%.

## Example A — marginal relief immediately above thresholds

Assumptions: resident individual taxed under section 202; ordinary income only; no deductions, losses, rebate, or other special-rate income; slab tax calculated from section 202; rupee values below are unrounded to show the statutory relationship. Applicable return rounding is omitted.

Section 202 ordinary slab tax used:

| Income slice | Rate |
| --- | ---: |
| ₹0–4 lakh | 0% |
| ₹4–8 lakh | 5% |
| ₹8–12 lakh | 10% |
| ₹12–16 lakh | 15% |
| ₹16–20 lakh | 20% |
| ₹20–24 lakh | 25% |
| Above ₹24 lakh | 30% |

| Total income | Slab tax | Surcharge before relief | Marginal-relief ceiling on tax + surcharge | Cess | Illustrative total |
| ---: | ---: | ---: | ---: | ---: | ---: |
| ₹50,00,000 | ₹10,80,000.00 | ₹0.00 | — | ₹43,200.00 | ₹11,23,200.00 |
| ₹50,00,001 | ₹10,80,000.30 | ₹1,08,000.03 at 10% | ₹10,80,001.00 | ₹43,200.04 | ₹11,23,201.04 |
| ₹1,00,00,000 | ₹25,80,000.00 | ₹2,58,000.00 at 10% | — | ₹1,13,520.00 | ₹29,51,520.00 |
| ₹1,00,00,001 | ₹25,80,000.30 | ₹3,87,000.05 at 15% | ₹28,38,001.00 | ₹1,13,520.04 | ₹29,51,521.04 |
| ₹2,00,00,000 | ₹55,80,000.00 | ₹8,37,000.00 at 15% | — | ₹2,56,680.00 | ₹66,73,680.00 |
| ₹2,00,00,001 | ₹55,80,000.30 | ₹13,95,000.08 at 25% | ₹64,17,001.00 | ₹2,56,680.04 | ₹66,73,681.04 |

At each boundary plus ₹1, the raw surcharge would cause a discontinuous increase. The ceiling limits **income-tax plus surcharge** to the threshold amount plus ₹1; cess is then calculated on that reduced amount. For example, at ₹50,00,001, the ceiling is ₹10,80,000 + ₹1, not the raw ₹11,88,000.33.

## Example B — ordinary income plus section 198 long-term gain

Assumptions: resident individual taxed under section 202; ₹2.10 crore of ordinary taxable income; ₹1 crore of eligible section 198 LTCG; the full annual ₹1.25 lakh section 198 threshold is unused; STT and all statutory eligibility conditions are satisfied; no losses, deductions, rebate, or other income. Ordinary income is already above the basic-exemption and rebate ranges.

| Component | Calculation | Amount |
| --- | --- | ---: |
| Section 202 tax on ordinary income | Slabs on ₹2.10 crore | ₹58,80,000.00 |
| Section 198 tax | (₹1 crore − ₹1.25 lakh) × 12.5% | ₹12,34,375.00 |
| Income-tax before surcharge | Sum of tax components | ₹71,14,375.00 |
| Surcharge on ordinary-income tax | ₹58,80,000 × 25% (ordinary income exceeds ₹2 crore) | ₹14,70,000.00 |
| Surcharge on section 198 tax | ₹12,34,375 × 15% cap | ₹1,85,156.25 |
| Total surcharge | Sum of surcharge components | ₹16,55,156.25 |
| Cess | (₹71,14,375 + ₹16,55,156.25) × 4% | ₹3,50,781.25 |
| Illustrative total tax, surcharge, and cess | Sum | ₹91,20,312.50 |

At total income ₹3.10 crore, the excess over the ₹2 crore marginal-relief threshold is ₹1.10 crore. That excess alone is greater than the illustrative ₹87,69,531.25 income-tax-plus-surcharge amount; because the tax-plus-surcharge amount payable at the threshold cannot be negative, the example is below the section 3(5) ceiling regardless of the threshold tax composition, so no marginal relief is triggered.

## Reproduction notes and limitations

The slab calculations use piecewise multiplication of each income slice by the section 202 rate. Surcharge and marginal relief are applied before cess. The examples isolate the rule at issue; they do not implement all taxpayer-level interactions, tax rounding, set-offs, section 156 rebate eligibility, withholding credits, or all special-income combinations. The section 198 example assumes the capital-gain tax and surcharge components can be identified separately as prescribed by the Act. Validate these examples with an Indian tax professional before relying on them in the investor ledger.

## Primary sources

1. [Income-tax Act, 2025 — official Gazette](https://egazette.gov.in/WriteReadData/2025/265620.pdf), section 202 (default-regime slabs), sections 196 and 198.
2. [Finance Act, 2026 — official Gazette](https://egazette.gov.in/WriteReadData/2026/271439.pdf), section 3(4)(a)–(b), section 3(5), and section 3(15), including Table row 10 and marginal-relief table.
3. [Income Tax Department copy of Finance Act, 2026](https://www.incometaxindia.gov.in/documents/d/guest/finance-act-2026-pdf-1), section 3(4)(b), Table row 10, and section 3(5).
4. [Finance Bill 2026 Memorandum](https://www.incometaxindia.gov.in/documents/81799/11848482/memo-2026.pdf/fe530cfa-9c49-fc5c-4bfa-fc96fd5e7b7a?t=1770008674037), paragraph 4.3 (section 202 surcharge capped at 25%) and paragraphs 5 and 3.3 (marginal relief; cess treatment).

## Gate status

These worked examples support the correction in `tax_rules_asof.md`; they do not qualify a tax engine. Tax-professional review, an implementation with boundary checks, security-level classification, tax-year aggregation, and reconciliation to the actual investor remain open. Investment authorization remains **NO-GO**.
