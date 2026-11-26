# G6.3 comparison of two 2036 sovereign investment routes

**As of 26 November 2026.** The SBI June 2036 Gilt Fund leads in the case anchored to its published portfolio yield. The 6.94% GoI bond leads in some lower fund-return cases. The rates and prices that change the ranking are measured below. This is a conditional comparison on an equal ₹1,00,000 lump sum, with investment authorization **NO-GO**.

## Evidence and common endpoint

| Input | Direct GoI bond | SBI June 2036 Gilt Fund Direct Growth |
|---|---|---|
| Identity | `IN0020260025`, NSE `694GS2036` series `GS` | `INF200KA12Q9`, AMFI `150681` |
| Source anchor | October and November RBI auction weighted prices of ₹96.93 and ₹97.46 per ₹100 face | October 30 factsheet portfolio YTM 7.54%, direct total expense ratio 0.28%, government securities 95.39%, modified duration 6.43 years and Direct Growth NAV ₹13.2860 |
| Maturity mechanics | 19 nominal ₹3.47 coupons per ₹100 face after modeled entry. Principal repaid at par on the nominal 11 May 2036 maturity. | Expected 30 June 2036 maturity, subject to index and scheme terms. Automatic redemption at maturity NAV with payment within three working days, subject to the scheme's conditions. |

The cutoff is the common **30 June 2036 valuation date**, not the investor's confirmed exit date or a cash-availability promise. The bond uses the same assumed reserve rate for interim coupons and for the 50 days between nominal maturity and the common endpoint. The fund is measured at modeled redemption value after the tax liability. A payout delay would affect when that money is available. The reserve rate is a scenario and has no dependency on RBI T-bill proceeds. [October auction](../2026-10-16/auction_pair_reconciliation_v1.json) · [November auction](../2026-11-13/README.md) · [SBI factsheet, p. 83](https://www.sbimf.com/docs/default-source/scheme-factsheets/sbi-mf-passives-%28index-etf-fof%29-factsheet-october-2026.pdf) · [SBI scheme document](https://www.sbimf.com/docs/default-source/sif-forms/sid---sbi-crisil-ibx-gilt-index---june-2036-fund.pdf)

## Modeling choices

- **Entry and costs.** Both receive ₹1,00,000 on the same hypothetical 26 November 2026 date. Direct clean prices range from ₹95 to ₹102.50 per ₹100 face. The model adds 15 days of 30/360 accrued interest, buys whole units and keeps residual cash. Direct purchase friction is 0, 10 or 50 bps of dirty consideration. If using an NSE Capital Market quote later, take the already-dirty price and add charges only. The fund includes 0.005% entry stamp duty, ongoing annual TER of 0.28% or 0.50%, and nil exit load after the disclosed 30-day window. [NSE price convention](https://www.nseindia.in/static/products-services/traded-on-cm) · [SBI scheme document](https://www.sbimf.com/docs/default-source/sif-forms/sid---sbi-crisil-ibx-gilt-index---june-2036-fund.pdf)
- **Growth.** The direct bond uses the contractual coupon and principal amounts, with nominal reserve return cases of 0%, 4%, 6% and 7.54% before ordinary tax. The last rate challenges the comparison by allowing direct coupons the same gross reinvestment rate as the fund's reference case. The fund has effective annual gross growth scenarios of 6.54%, 7.54% and 8.54%, multiplied each year by one minus TER. A dated portfolio YTM is a reference for this grid. Realized growth depends on prices, reinvestment and tracking. Absolute fund entry NAV scales the units purchased. The gross growth scenarios vary the return from entry NAV to the eventual redemption NAV. [SBI portfolio and tracking disclosures](https://www.sbimf.com/docs/default-source/scheme-factsheets/sbi-mf-passives-%28index-etf-fof%29-factsheet-october-2026.pdf)
- **Tax.** Carry the current-law treatment forward only as a sensitivity. Tax direct coupons and modeled reserve interest at ordinary marginal rates. Apply the section 197 long-term rate to positive redemption gain, assuming the listing and relevant statutory conditions continue at maturity. Compare a clean-only acquisition basis with a dirty-price basis and tax the full coupon in both. Deduct no entry fees from the modeled gains, and credit no capital losses. The fund pays no investor distributions in the Growth model. Its gain is deemed short term under section 76 if the fund continues to qualify as a Specified Mutual Fund. The statutory test uses annual average daily closing allocations. The scheme's investment mandate and observed debt allocation support this scenario, while the relevant 2036 classification requires verification. Basis for the fund is the amount invested after stamp duty. [Income-tax Act 2025, ss. 2(101), 76, 92, 197 and 202](https://www.incometaxindia.gov.in/documents/d/guest/income_tax_act_2025_as_amended_by_fa_act_2026-pdf) · [Finance Act 2026](https://www.incometaxindia.gov.in/documents/d/guest/finance-act-2026-pdf-1)
- **Tax timing and inflation.** The no-tax case is an arithmetic control. Other cases apply 20% or 30% ordinary marginal tax, 4% cess, and one 30% case with an additional 10% surcharge on tax. They assume no taxpayer-level threshold crossing, marginal relief, unused exemption or offsets. Coupon tax reduces the amount reinvested at each modeled payment. Reserve growth uses gross annual rate times one minus the effective ordinary rate. Fund tax is deducted at redemption. These are incremental sensitivities, with no exact personal filing/withholding calculation. Report purchasing power in modeled November 2026 rupees at 4%, 6% and 8% inflation. It is a common deflator rather than the confirmed investor CPI anchor.

## Reference case per ₹1,00,000 initial budget

The direct inputs are ₹97.46 clean, a 10 bp entry cost and 4% gross reserve interest. The fund inputs are 7.54% gross annual growth and a 0.28% TER. Both use the 30% ordinary rate with cess, without surcharge. The bond uses clean-only tax basis.

| 30 June 2036 value | Direct bond | SBI Direct Growth |
|---|---:|---:|
| Nominal before fees and investor tax | ₹1,84,229 | ₹2,00,943 |
| Nominal after fees, before investor tax | ₹1,84,046 | ₹1,95,596 |
| Nominal after fees and investor tax | ₹1,54,968 | ₹1,65,769 |
| After-tax purchasing power at 6% inflation | ₹88,574 | ₹94,747 |
| After-cost nominal annualized return before investor tax | 6.56% | 7.24% |
| After-cost nominal annualized return after investor tax | 4.67% | 5.41% |

The annualized values use the single opening contribution and an ending value with all interim proceeds retained or reinvested. The modeled fund advantage is **₹10,800 nominal after tax** or **₹6,173 at 6% inflation**. In the no-tax control it is ₹11,550 nominal after fees. At the 20% marginal slab it is ₹11,513. At the 30% slab with the 10% surcharge assumption it is ₹10,554. The 30% reference therefore does not determine the ranking by itself.

## What changes the ranking

| Direct clean entry per ₹100 face | Bond after-tax nominal with 4% reserve | Fund gross growth needed to match, at 0.28% TER |
|---:|---:|---:|
| ₹95.00 | ₹1,58,622 | 6.93% |
| ₹96.93 | ₹1,55,728 | 6.67% |
| ₹97.46 | ₹1,54,968 | 6.61% |
| ₹100.00 | ₹1,51,371 | 6.28% |
| ₹102.50 | ₹1,47,676 | 5.93% |

- At **6.54%** fund growth and 0.28% TER, SBI gives ₹1,54,225 after tax. The ₹97.46 bond case leads by **₹744**. At 0.50% TER, the fund's break-even gross growth against that bond moves from 6.61% to **6.84%**.
- Raising bond reserve growth to **7.54%** raises the ₹97.46 bond case to ₹1,61,753 after tax. At ₹95 clean with the same reserve rate the bond gives ₹1,65,590, within **₹179** of the fund reference. That comparison depends on access to the assumed reinvestment rate across the coupon dates.
- Changing direct entry friction from 0 to 50 bps moves the reference-price bond from ₹1,55,123 to ₹1,54,329 after tax at 4% reserve growth. Changing its basis from clean to dirty at 10 bps raises after-tax terminal value by ₹39. By comparison, increasing the fund TER from 0.28% to 0.50% reduces its reference after-tax value by ₹2,823.
- Nominal bond maturity falls on a Sunday. Applying a Monday–Friday-only calendar with the RBI prior-working-day rule for principal and following-working-day rule for coupons moves the reference by ₹13.16. Confirm the actual 2036 calendar and credit timing before relying on specific days. [RBI primer, Q1](https://www.rbi.org.in/scripts/FAQView.aspx?Id=79)

Carry both candidates forward. The direct route's ranking turns on entry price and realizable coupon reinvestment. The fund's ranking turns on achieved portfolio return, TER and tax at redemption. Its maturity-month NAV and eventual payment can differ from this model. To support a decision-grade ranking, qualify the dated fund holdings and cashflow path, then confirm applicable investor tax and current execution only for retained instruments. The ₹1 lakh sleeve analysis supplies no whole-portfolio result, personal suitability conclusion or 2036 floor probability.

## Reproduce

```powershell
py -B decision/compare_g6_3_gilt_routes.py --check
```

The [inputs](inputs_v1.json) give the source URLs and checked AMC PDF hashes. The [frozen result](comparison_v1.json) contains 480 bond cases and 24 fund cases. A separate forward cash recurrence and split fund growth calculation reproduced all 504 before- and after-tax amounts to rounding precision. The break-even growth formula is checked by valuing the fund at that rate and reconciling it to the corresponding bond case. Live quote remains deferred and open. Paid Silver ETF history remains deferred. RBI T-bill payment timing remains open. Investment authorization remains **NO-GO**.
