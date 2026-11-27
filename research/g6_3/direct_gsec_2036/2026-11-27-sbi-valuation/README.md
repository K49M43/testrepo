# G6.3 SBI June 2036 bond mark and accrued interest

## Accounting evidence reviewed on 27 November 2026

The fund's audited 31 March 2025 accounts show ₹5,985.43 lakh of accrued interest under other financial assets, separate from investments, for the same scheme. SEBI's 2026 accounting schedule requires daily income accrual and separate accounting for accrued interest bought or sold with a security. This supports treating the bond mark as clean and accounting for the coupon accrual separately. The dated October portfolio statement aggregates net receivables and payables, leaving the exact October posting and residual balances unconfirmed. [SBI scheme annual report, printed p. 393, Note 6](https://www.sbimf.com/docs/default-source/lists/scheme-annual-report-2024-25.pdf?sfvrsn=559ce3e3_0#page=398) · [SEBI regulations, Eighth Schedule (a) and (c), p. 81](https://www.sebi.gov.in/sebi_data/attachdocs/jul-2026/1783933012694.pdf#page=81)

The September half-year financial results independently match the 30 September holdings statement's ₹2,638.0092 crore AUM at published precision and the ₹13.3943 Direct Growth NAV. They also report 0.28% Direct Plan recurring expenses and ₹93.1605 crore of scheme interest income over the half year. The income is a period flow. The disclosure supplies no corresponding month-end bond accrued-interest balance or valuation calculation. The [input manifest](inputs_v1.json) identifies the source files, hashes, and cells. [September holdings](https://www.sbimf.com/docs/default-source/scheme-portfolios/all-schemes-monthly-portfolio---as-on-30th-september-2026.xlsx?sfvrsn=2a79126c_2) · [September financial results](https://www.sbimf.com/docs/default-source/default-library/half-yearly-unaudited-financial-results-as-on-september-30-2026ecd6614bdb154247a3601d5bb62f813a.xlsx?sfvrsn=2ac32336_0)

## Yield and price reconciliation

I repriced the 20 dated cashflows of ISIN IN0020220029 using both yield styles, Actual/365 and 30E/360 discounting, and both the statement date and the next calendar day. For each trial, I compared the reported mark with the modeled all-in price and the modeled price after subtracting 30E/360 accrued interest. RBI describes a nominal semiannual convention for government-bond market yields. Here the disclosure numbers give stronger support to interpreting the portfolio column as annual-effective with 30E/360. Treat the next-day calculation as a numerical diagnostic. The disclosure gives no source valuation worksheet, provider cutoff, or formula to establish whether SBI actually uses that date. [RBI government securities primer, Q24–25](https://m.rbi.org.in/CommonPerson/english/Scripts/FAQs.aspx?Id=711) · [October holdings](https://www.sbimf.com/docs/default-source/scheme-portfolios/all-schemes-monthly-portfolio---as-on-31st-october-2026.xlsx)

| Statement | Published mark per ₹100 face | Published holding yield | Modeled accrued per ₹100 at trial date | Modeled clean price with next-day effective 30E/360 | Reported minus modeled at position size |
|---|---:|---:|---:|---:|---:|
| 30 September | ₹102.23779950 | 7.34201618% | ₹2.68088889 | ₹102.23786465 | −₹15,798 |
| 31 October | ₹100.73609843 | 7.568006125% | ₹3.30922222 | ₹100.73609664 | +₹442 |

The October trial rounds to the disclosed ₹249,311.77 lakh. The September trial misses published precision. Discounting on 31 October itself gives ₹100.73595871 clean and ₹104.02423648 all-in. Its clean value is about ₹34,580 below the disclosure at position size. Across both months, every tested all-in interpretation misses disclosed precision. An exact-looking October price fit supports the clean-mark explanation, while the separate October accrual and the provider's actual convention remain unverified.

## After-tax comparison rerun

The model retains the 31 October reporting date and the original portfolio cashflows. When it treats accrual as separate, the model removes estimated 31 October accrued interest of ₹8,138.16 lakh from ₹8,059.96 lakh of net receivables before counting the full next coupon. This leaves a modeled ₹78.20 lakh net payable. The next-day yield diagnostic does not change the economic start date or those inputs. Both accounting cases and both residual-yield treatments are carried through the 40-case replay. The directly held 6.94% bond uses a ₹97.46 hypothetical clean entry, 10 bp entry cost and the same gross reinvestment rate in each row. The amounts use a ₹1 lakh budget, 31 October 2026 start, 30 June 2036 valuation and the established 30% slab plus cess tax scenario. [Baseline cost and tax assumptions](../2026-11-26-gilt-comparison/README.md)

| Gross reinvestment for both routes | SBI TER | SBI less direct bond after tax, separate accrual | SBI less direct bond after tax, accrued included in mark |
|---:|---:|---:|---:|
| 2% | 0.28% | −₹1,023 to −₹1,019 | +₹1,066 to +₹1,502 |
| 4% | 0.28% | +₹1,076 to +₹1,085 | +₹3,170 to +₹4,122 |
| 6% | 0.28% | +₹3,578 to +₹3,593 | +₹5,678 to +₹7,240 |
| 4% | 0.50% | −₹1,531 to −₹1,522 | +₹519 to +₹1,451 |

At 4% and 0.28% TER, the better-supported separate-accrual case ends at ₹1,54,532–₹1,54,541 after tax against ₹1,53,456 for the same-date direct case. Its gross result of 6.5200%–6.5208% is below the original 6.6069% hurdle for the **different 26 November** comparison. The comparable 31 October hurdle is 6.4235%. Both results are conditional on assumed entry price, reinvestment, costs and taxes. The 2% and higher-fee cases show why the allocation ranking remains sensitive.

**Disposition.** Prefer separate accrual for the research base case and retain the inclusive-mark case as a sensitivity. Full October reconciliation requires the dated security-level clean mark, accrued interest booked against the ISIN, the rest of net receivables and payables, and SBI's yield convention and cutoff. G6.3 remains open. Live quote and paid Silver ETF history stay deferred, RBI T-bill payment timing stays open, and investment authorization remains **NO-GO**.

## Reproduction

```text
python decision/audit_g6_3_sbi_gilt_valuation.py --check
python decision/audit_g6_3_sbi_gilt_valuation.py --check --september-holdings <source.xlsx> --september-financials <results.xlsx>
```

The offline check recomputes the frozen holdings audit, then reproduces the 16 price-yield diagnostics and after-tax ranges. The second run checks original spreadsheet hashes and cell values with `openpyxl`. The [audit output](valuation_audit_v1.json) includes a parallel comparison with the direct bond's reinvestment rate fixed at 4%.
