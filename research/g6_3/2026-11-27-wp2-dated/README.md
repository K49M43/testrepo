# G6.3 WP2 dated cashflow and tax reconciliation

The deterministic research gate covers independently reconciled dated cashflows, both frozen funding schedules and a staged 2036 exit. The earlier [WP2 result](../2026-11-27-wp2-portfolio/README.md) remains the record of the initial comparison. This increment checks what happens when settlement, lot sizing and annual tax are enforced. Personal results and probability inputs remain blocked as required by [issue #44](https://github.com/K49M43/testrepo/issues/44).

## Funding and reference outcomes

The schedule starts with ₹42 lakh and adds a ₹25,000 monthly SIP with a 10% increase after each 12 payments. Total contributions are ₹89.81 lakh through 31 October 2036 and ₹91.11 lakh through 31 December 2036. The reference mix is 65% Motilal Nifty 500 Index Fund, 20% in the sovereign sleeve shown below and 15% HDFC Gold ETF. The scenarios use the G3 October 2026 purchasing-power convention and 4%, 6% and 8% illustrative compound inflation.

| Sovereign sleeve | 120-payment nominal after modeled tax | 120-payment real at 6% | 122-payment real at 6% | 120-payment real remaining at 6% after staged withdrawal |
| --- | ---: | ---: | ---: | ---: |
| LIC G-Sec ETF | ₹138.55 lakh | ₹77.37 lakh | ₹78.14 lakh | ₹74.37 lakh |
| Direct 6.94% GoI 2036 | ₹139.04 lakh | ₹77.64 lakh | ₹78.37 lakh | ₹74.62 lakh |
| SBI June 2036 Gilt Fund, accrued coupon carried separately in net receivables | ₹138.76 lakh | ₹77.48 lakh | ₹78.22 lakh | ₹74.50 lakh |
| SBI June 2036 Gilt Fund, accrued coupon included in the bond mark | ₹138.99 lakh | ₹77.61 lakh | ₹78.35 lakh | ₹74.63 lakh |

All four 120-payment full exits miss the ₹90 lakh real floor by ₹12.36–₹12.63 lakh at 6% inflation. With the dated assumptions, the direct route leads the SBI separate-accrual case by ₹27,610 nominal. The gap to SBI's included-accrual case is ₹4,507. Entry yield, costs, taxpayer context and the fund's reinvestment rate can change the order. The staged fixture trades approximately 25% of each sleeve on 24 March 2036, rounds exchange units down, releases those proceeds on 27 March and withdraws ₹5 lakh on 1 April. The early withdrawal is worth about ₹2.89 lakh on the illustrative real base and is reported separately from remaining terminal wealth. Staged XIRR carries an ambiguity flag because the cashflows have multiple sign changes.

For the direct bond in the 120-payment reference, the nominal sequence is ₹150.31 lakh before explicit costs and tax, ₹150.24 lakh after explicit costs, and ₹139.04 lakh after modeled tax. At 6% inflation that leaves ₹77.64 lakh in October 2026 purchasing power. In separate sensitivities, increasing cess from 4% to 6% reduces nominal wealth by about ₹21,204, and lowering the annual equity NAV rate from 8% to 7.5% reduces it by about ₹3.12 lakh.

## Evidence and model limits

- **48 matched NAV intervals.** Four replays map the WP1 common-date marks to the first 48 funding dates for the LIC and SBI mixes, with 0% and 5% silver. Marks predate the target funding series. These are deterministic sequences, and they are unsuitable for estimating 2036 outcome probabilities. Traded ETF prices remain unqualified.
- **Costs and custody.** Trace terminal nominal wealth before explicit costs and tax, after explicit costs before tax, after tax set-aside, and after inflation. The control uses the same cashflow policy. NAV marks already embed ongoing product expenses and tracking, while the SBI forward sleeve separates the hypothetical TER. Equity NAV tracking drag, ETF all-in friction, bond friction and entry yield, reserve rate, SBI TER and reinvestment, and SBI release lag are separate sensitivities. Round exchange acquisitions to whole units and keep unused cash in reserve. Fund units can be fractional. No executed quotes or broker terms are used.
- **Receipt timing.** For conditional forward scenarios, ordinary sales enter cash after three calendar days, bond par after three calendar days and SBI maturity proceeds after seven calendar days, with a 14-day SBI alternative. The direct coupon fixture uses nominal coupon dates and coupons of ₹3.47 per ₹100 unit. The historical replays use same-day marks and exit cash. Actual exchange business days, fund redemptions, bank credit timing and coupon entitlement dates remain to be verified. The last SIP stays in cash. RBI T-bill cashflows are excluded.
- **Tax and withholding.** The base uses hypothetical resident taxable ordinary income outside this portfolio of ₹30 lakh per tax year, with ₹45 lakh as a sensitivity. Reuse the audited TY 2026–27 component for the annual tax estimate, including the incremental effect on external income. Treat 4% cess as the enacted baseline, 6% as an explicit policy stress, and 10% direct coupon withholding as a cash-timing and credit stress. The latter gives credit for exactly the modeled cash withheld within that tax year. Securing an actual credit, the direct bond's accrued-interest basis, specific expense deductibility, fiscal payment dates and future legislation require further evidence. Set-asides use each 31 March or the final valuation date. They are simulated reductions in available cash. [Finance Act 2026](https://www.incometaxindia.gov.in/documents/d/guest/finance-act-2026-pdf-1) · [Income-tax Act as amended in 2026](https://www.incometaxindia.gov.in/documents/d/guest/income_tax_act_2025_as_amended_by_fa_act_2026-pdf)
- **Tax losses and marginal relief.** Match current-year losses to eligible gains. Apply long losses first, preserve eligible short-term matches, and keep every offset tied to the sale IDs and real tax buckets. No external gain or filing is assumed. Opening carryforward requires timely-return evidence and the audited eight-year limit. An unsupported mixed marginal-relief reference can only be bypassed if the uncapped bill is no greater than income above the threshold, so the statutory cap cannot bind even if reference tax were zero. Other unsupported computations fail closed. [Tax department transition guidance](https://www.incometaxindia.gov.in/documents/81799/11848482/Updated-FQAs-on-Interplay%26Transitions.pdf)

## Acceptance record

| Gate | Evidence and disposition |
| --- | --- |
| WP2 dated events, fees and receipts | Research PASS. Reconcile 50 traces and 79,824 events. Independently reconstruct each lot, fee, sale, coupon, placement into cash, withdrawal and terminal balance. Reject pre-sale receipt, post-horizon funding, duplicate funding dates and instruments exiting before funding. Verify an April receipt preserves the March trade's tax year. |
| WP2 tax and losses | Research PASS. Independently recompute slab tax, rates by gain bucket, surcharge with marginal relief where applicable, cess, rounding and withholding credit for the stated fixture. Test long-loss restrictions, eight-year expiry and missing filing evidence. |
| WP2 wealth and XIRR | Research PASS. Reconcile INR balances within half a paisa plus a numerical margin of ₹0.00001, independently discount real balances, test a zero-return and zero-cost path, and verify reported XIRR with an NPV residual bound based on its display precision. |
| WP2 personalized or execution-grade output | Blocked. Require confirmed personal tax, terminal dates and purchasing-power base, actual cost and execution data, and product-specific settlement and tax rules. Catch unsupported paths before decision use. |
| WP3 probability | Directional design may reference these deterministic checks. All WP2 fixtures retain `eligible_probability_input=false`. A probability claim needs a separately registered protocol, qualified data and independent calibration checks. |

Keep both SBI accrual cases. The live direct bond quote and paid Silver ETF history remain deferred. RBI T-bill timing remains open. G6.3 is open and investment authorization remains **NO-GO**.

## Reproduce

```sh
python decision/g6_3_wp2_dated.py --check --trace-dir tmp/g63-wp2-traces
python decision/audit_g6_3_wp2_dated.py tmp/g63-wp2-traces
```

[Inputs](inputs_v2.json) and [frozen results](results_v2.json) list the run assumptions, normalized source hashes, and event trace digests. The regeneration and independent check use Python 3.13 and standard-library dependencies, without random draws. JSONL files are generated locally or within CI and each event includes a date, fiscal year, cash delta and running cash balance.
