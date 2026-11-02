# Deterministic 2036 cashflow and goal hurdle baseline

**As of:** 2 November 2026  
**Status:** arithmetic baseline only; not a forecast, probability estimate, security recommendation, or authorization to invest.  
**Code:** [`cashflow_hurdle_baseline.py`](cashflow_hurdle_baseline.py)

## Inputs and convention

- Initial capital: INR 4,200,000 at the October 2026 model origin.
- First end-of-month SIP: INR 25,000 in November 2026; it rises 10% after each 12 contributions.
- Horizon: 120 contributions through October 2036, and a separate 122-contribution sensitivity through December 2036.
- Planning floor: INR 9,000,000 in October 2026 purchasing power.
- CPI sensitivities: 4%, 6%, and 8% annual compound rates, applied from the October 2026 origin to each horizon.
- A single constant monthly portfolio return is solved to make the pre-tax, pre-fee terminal balance equal the nominalized floor. The initial amount compounds for the full horizon; every SIP is an end-of-month contribution. Cashflows preserve mathematical precision and do not assert a broker/bank payment-rounding rule.

The actual first investment date, SIP date, and exact 2036 measurement date remain unconfirmed. Accordingly, the schedule is explicitly indexed by calendar month and uses the illustrative date convention above.

## Arithmetic result

The 120 mathematical SIP schedule totals INR 4,781,227.38; with initial capital, total contributed principal is INR 8,981,227.38. Extending the same schedule to 122 contributions produces INR 4,910,914.50 of SIPs and INR 9,110,914.50 combined principal. The monthly schedule retains sub-paise arithmetic to match the mandate's estimate; an actual recurring-payment ledger must apply the broker/bank's rounding convention once the real SIP is specified.

At 6% assumed CPI, INR 9,000,000 in October 2026 purchasing power becomes about INR 16,117,629 nominal at month 120 (October 2036), and about INR 16,274,918 at month 122 (December 2036). With the stated contributions and end-of-month timing, the corresponding constant nominal gross-return hurdle is 8.25% effective annually to October 2036 and about 8.10% to December 2036. These are before every tax, fee, spread, and other cost; they are not expected returns and do not show that an eligible portfolio can achieve the goal.

Full scenario rows are in [`cashflow_hurdle_sensitivity.csv`](cashflow_hurdle_sensitivity.csv). The monthly ledger is in [`cashflow_hurdle_monthly_2026-10_base.csv`](cashflow_hurdle_monthly_2026-10_base.csv).

## CPI source timing limitation

As of 2 November 2026, MoSPI had published the September 2026 CPI release on 12 October; its official macro-indicator page reports September CPI inflation of 5.54%. October 2026 CPI was not yet published. Therefore this baseline does **not** claim to use an observed October 2026 CPI anchor. It retains the mandate’s October reference month as an assumed origin and presents 4/6/8% sensitivities. Before a final real-wealth result, choose and record an observed CPI base month and compare it with the actual investment date.

MoSPI’s official method links pre-2025 combined general 2012-base observations using the 2024-base factor 0.5267, based on the geometric annual average over the overlapping year 2025. The linked historical series is a general-index link and should not be interpreted as newly observed 2024-base values or used for group-level linking. Sources: [MoSPI CPI 2024-series FAQ](https://mospi.gov.in/uploads/documents/documents/1770891066052-Annexure_V.pdf), [MoSPI September 2026 release listing](https://mospi.gov.in/latest-releases), and [MoSPI official macro indicators](https://esankhyiki.mospi.gov.in/dashboard/nss77/).

## Scope and next gate

This addresses only deterministic contribution timing and the nominal return needed under selected CPI assumptions. It does not model taxes, fee drag, instrument returns, tax lots, coupons, brokerage/friction, portfolio rebalancing, return sequence, or uncertainty. The investment decision remains **NO-GO**. Next, independently audit the instrument-specific tax and after-tax accounting engine, then reconcile its real-value deflator to a released, source-pinned CPI month.

### Tax-law transition found during the next-gate review

The Income-tax Act, 2025 came into force on 1 April 2026. Tax-year 2026–27 modeling therefore needs to be checked against the 2025 Act and Finance Act 2026 framework; the old 1961 Act still governs earlier tax years under transition provisions. Existing repository simulations use simplified flat tax proxies and their statutory references cannot be treated as a current, instrument-specific tax determination. The 2036 law is unknown and must be a separate sensitivity.

The Income Tax Department reported on 27 October 2026 that CBDT had **proposed** rules and Form 173A for furnishing information to claim specified interest and capital-gains exemptions for Government securities under Schedule IV of the 2025 Act. This was a proposal as of this audit, not an enacted rule to assume in the model. Direct GoI holdings therefore need a security- and eligibility-specific tax branch; do not apply their treatment to gilt funds or ETFs. Sources: [official text of the Income-tax Act, 2025](https://egazette.gov.in/WriteReadData/2025/265620.pdf), [Income Tax Department: transition and commencement explanation](https://www.incometax.gov.in/iec/foportal/help/all-topics/e-filing-services/objective-and-scope-new-act), and [CBDT proposal notice](https://www.incometax.gov.in/iec/foportal/latest-news).
