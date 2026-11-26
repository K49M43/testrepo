# G6.3 SBI June 2036 Gilt Fund holdings and cashflow audit

## Evidence qualified on 26 November 2026

SBI's 31 October monthly statement for the common scheme portfolio reconciles to ₹2,613.6001 crore. Its 95.39% government-security weight and ₹13.2860 Direct Growth NAV agree with the 30 October factsheet. The earlier factsheet AUM is ₹2,613.59 crore, a ₹1.01 lakh difference across the two reported dates. Source locations, original file byte counts, SHA-256 hashes and source cells are in [the snapshot](snapshot_v1.json). [SBI monthly disclosure](https://www.sbimf.com/docs/default-source/scheme-portfolios/all-schemes-monthly-portfolio---as-on-31st-october-2026.xlsx) · [SBI October factsheet, p. 83](https://www.sbimf.com/docs/default-source/scheme-factsheets/sbi-mf-passives-%28index-etf-fof%29-factsheet-october-2026.pdf)

| Portfolio line | ISIN | Market value (₹ crore) | % of AUM |
|---|---|---:|---:|
| 7.54% Government Stock, 23 May 2036 | IN0020220029 | 2,493.1177 | 95.39% |
| Tri-party repo (TREPS) | | 39.8828 | 1.53% |
| Net receivables less payables | | 80.5996 | 3.08% |
| Total | | 2,613.6001 | 100.00% |

The statement identifies a single bond and reports nil Treasury-bill and derivatives positions. The 6.94% direct comparison bond, ISIN IN0020260025, has zero weight in this dated snapshot. The quantities reconcile to a ₹100-face unit and an implied reported mark of ₹100.7361 per unit. The Gazette verifies the 7.54% coupon, semiannual payments on 23 May and 23 November, and redemption at par. RBI maps those terms to the fund's ISIN. At the disclosed quantity, the nominal schedule has 20 coupons of ₹93.30373 crore from 23 November 2026 through 23 May 2036, when ₹2,474.90 crore face principal also falls due. These are gross cashflows to the portfolio if it holds the disclosed quantity. The investor in Direct Growth receives redemption proceeds under the fund's scheme terms. [Gazette, p. 5, paragraphs 1 and 6](https://egazette.gov.in/WriteReadData/2022/239952.pdf) · [RBI security register](https://www.rbi.org.in/scripts/BS_ViewMasDirections.aspx?id=12765) · [SBI scheme information document](https://www.sbimf.com/docs/default-source/sif-forms/sid---sbi-crisil-ibx-gilt-index---june-2036-fund.pdf)

## Break-even test

The gross model scales the 31 October holdings to ₹1 lakh at disclosed AUM and carries the nominal coupon and principal cashflows to 30 June 2036. It applies effective annual reinvestment rates to TREPS and received bond cashflows. It tests a zero return and the same reinvestment rate on residual signed net assets, with their reported or allocated balance held at face. In the separate-accrual case, estimated accrued interest is removed from the net receivable balance before counting the full contractual coupon. This leaves a ₹78.20 lakh net payable. The accrual estimate uses 30E/360 and the returns use Actual/365. Exact cash availability, holidays, residual balance breakdown and the future investment path of the fund are outside this test.

The ₹100.7361 reported bond mark implies an all-in price of ₹100.7361 if it includes accrued interest, or ₹104.0244 if the coupon accrued separately. Pricing the nominal dated schedule at the published 7.5680% holding YTM using nominal semiannual compounding and Actual/365 gives ₹103.0789. Neither basis reproduces the disclosed holding YTM under that convention. SBI's valuation policy specifies averaged valuation-agency marks but gives no separate accrued-interest amount for this sheet. Keep both accounting treatments as sensitivities. The 7.54% factsheet portfolio YTM is a separate reported measure. [SBI valuation policy, §§9.3 and 13](https://www.sbimf.com/docs/default-source/disclosures/valuation-policy/valuation-policy6523ebaf60e84b3db60813a5951ad4a4.pdf)

| Coupon and TREPS reinvestment | Frozen portfolio annualized gross return | Compared with original 6.6069% hurdle |
|---:|---:|---|
| 0% | 5.48%–5.69% | Below in all modeled cases |
| 2% | 5.98%–6.22% | Below in all modeled cases |
| 4% | 6.52%–6.79% | Crosses the hurdle |
| 6% | 7.09%–7.40% | Above in all modeled cases |
| 7.54% | 7.56%–7.90% | Above in all modeled cases |

The original hurdle applies to a hypothetical 26 November purchase of the 6.94% bond at ₹97.46 clean, with 10 bp entry cost, 4% gross reserve, the 30% tax slab plus cess and SBI Direct TER of 0.28%. The frozen October portfolio needs **3.38%–4.31%** gross reinvestment to match that annual hurdle. This range is across four accounting and residual-yield scenarios. [Original conditional comparison](../2026-11-26-gilt-comparison/README.md)

A separate timing control applies the same hypothetical ₹97.46 clean price to a 31 October start for the direct bond. That clean price was observed at the later November auction and serves only as a held-constant comparison input. Accrued interest, units, and the extra November coupon change the direct terminal value to ₹1,53,456.31 and the matched-date hurdle to **6.4235%** at 0.28% TER. At 4% reinvestment, the fund produces **₹1,54,532–₹1,57,579 after costs and taxes per ₹1 lakh**, ₹1,076–₹4,122 above that same-date direct scenario. Raising fund TER to 0.50% lifts the matched hurdle to **6.6588%** and produces a difference of **−₹1,531 to +₹1,451** after tax. Both counterparts use the earlier section 76 tax scenario and 0.005% fund subscription stamp duty. The values are nominal and the pricing, tax and reinvestment assumptions remain conditional.

**Disposition.** The holdings and nominal coupon terms qualify for the dated cashflow sensitivity. Actual fund realization depends on future rebalancing, tracking difference, reinvestment, fees, and final NAV and payout timing. A matching portfolio accounting bridge for the mark, accrual and reported yield would narrow the 4% result. Retain both candidates for research. The live quote and paid Silver ETF history are deferred, the RBI T-bill payment timing gate is open, and investment authorization remains **NO-GO**.

## Reproduction

```text
python decision/compare_g6_3_gilt_routes.py --check
python decision/audit_g6_3_sbi_gilt_holdings.py --check
python decision/audit_g6_3_sbi_gilt_holdings.py --check --workbook <local-sbi-source.xlsx>
```

The first two checks run offline using Python's standard library. The optional third check requires `openpyxl` (verified with 3.1.5) and checks the exact downloaded workbook bytes, cited cells and sole disclosed ISIN. The audit reconciles source amounts and weights, coupon dates and event totals, chronological cash-account compounding, and the solved reinvestment rates. The [frozen output](cashflow_audit_v1.json) records all 40 scenarios, including a control that varies the direct bond's reinvestment rate alongside the fund's.
