# 6.94% GS 2036 November primary-auction source check

**As of** 25 November 2026. **ISIN** `IN0020260025`. **Result** Second historical primary-auction reference verified. Exact retail debit and current executable quote remain open.

## What the auction establishes

Four archived RBI pages corroborate the security identity, auction and settlement terms, and results. The outstanding-security list maps the same issue and maturity to the ISIN. RBI specified 16 November for settlement of its 13 November multiple-price reissue. Competitive allotments of ₹33,947.718 crore and eight noncompetitive bids totaling ₹52.282 crore reconcile to ₹34,000 crore. The notice identifies the weighted-average competitive price as the noncompetitive pricing basis and specifies a ₹10,000 nominal lot. [Notice and auction rules](https://www.rbi.org.in/scripts/BS_PressReleaseDisplay.aspx?prid=63952) · [Full result](https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=63970) · [Cutoff release](https://www.rbi.org.in/SCRIPTS/BS_PressReleaseDisplay.aspx?prid=63969) · [Outstanding securities](https://www.rbi.org.in/scripts/bs_viewcontent.aspx?Id=1956)

| Auction | Weighted-average price per ₹100 face | Published weighted-average nominal yield | Cutoff price / nominal yield |
|---|---:|---:|---:|
| 16 October 2026 | ₹96.93 | 7.3925% | ₹96.91 / 7.3955% |
| 13 November 2026 | ₹97.46 | 7.3158% | ₹97.43 / 7.3203% |

The second reference is ₹0.53 higher per ₹100 of face and 7.67 basis points lower in quoted yield. These are separate historical auction observations. A new purchase still requires an available offer or reissue. [October reconciliation](../2026-10-16/auction_pair_reconciliation_v1.json)

## Accrued-interest challenge

The published Gazette text identifies a May 2026 original issue, a November reissue, 11 May and 11 November coupon dates, and interest due through 15 November. Its last-coupon cell reads “New Security.” The contractual schedule places the first nominal coupon on 11 November, before the 16 November settlement. The Gazette PDF was read through the web source. Byte-level retention and visual verification of the new Gazette are still pending after TLS and rendering failures. The retained RBI notice and results independently establish the auction and settlement facts above. [Gazette notification, paragraphs 5–6](https://egazette.gov.in/WriteReadData/2026/277814.pdf) · [Access record](source_access_v1.json)

Use the 19 remaining nominal coupons, adding par at maturity, discounted from 16 November on the semiannual 30/360 yield convention. Subtract each candidate accrual from the dirty present value and round the clean price to the publication's two decimal places. Both results match only in the five-day case among the tested conventions. This checks the yield quotation convention. The published yield and clean price cannot establish the exact amount debited to an investor. [RBI bond convention, Q22–25](https://www.rbi.org.in/scripts/FAQView.aspx?Id=79)

| Tested accrual | Reconstructed cutoff / weighted-average clean price | Illustrative debit on ₹10,000 face before fees, using published weighted price |
|---|---:|---:|
| Four elapsed 30/360 days, 11–15 November | ₹97.45 / ₹97.48 | ₹9,753.71 |
| Five 30/360 days, 11–16 November | **₹97.43 / ₹97.46** | **₹9,755.64** |
| 184 days from original issue to 15 November | ₹93.98 / ₹94.01 | ₹10,100.71 |

The five-day pricing case differs from the four-day calculation by ₹1.93 per ₹10,000 face. Starting accrual in May instead of November would materially overstate consideration in the diagnostic. Keep the actual coupon credit, accrual and final debit open until confirmed by an official transaction-level calculation or an appropriately redacted allotment/settlement advice. The October calculation remains separately conditional.

## Current retail price gate

CCIL's public Odd Lot Market Watch lists bid, offer, amounts and last trade fields. The checked public response showed the headers with no dated candidate quote, so it supplies a route lead. The wider NDS-OM ticker displays trades and cannot establish the retail bid/offer for a particular size. RBI documents the Retail Direct odd-lot and RFQ route. The investor's access and terms for this security require confirmation. No secondary price payload was retained and no retail quote request or order was submitted. [CCIL Odd Lot Watch](https://www.ccilindia.com/odd-lot-mkt.-watch) · [RBI Retail Direct market-making directions](https://www.rbi.org.in/scripts/FS_Notification.aspx?Id=12216) · [CCIL data policy](https://www.ccilindia.com/documents/d/ccil/CCIL_DATASHARING_POLICY_OCT24)

To pass the executable-price gate, require a fresh odd-lot offer for this ISIN with timestamp, visible quantity or RFQ response, settlement date, clean price, accrued interest, fees, all-in cash and investor-confirmed access. Checking an offer or redacted instrument preview requires no trade. A hold-to-maturity comparison can then use that entry price and sourced cashflows, subject to taxes, coupon reinvestment and treatment of May proceeds if the target date falls later in 2036. An early-exit comparison still needs liquidity and secondary-valuation evidence.

## Reproduce

```powershell
py -B decision/audit_g6_3_direct_gsec_2036.py
py -B decision/audit_g6_3_direct_gsec_november_auction.py --check
```

The [receipts](source_receipts.json) retain publication URLs, timestamps, byte lengths and SHA-256 hashes. The [frozen check](auction_reconciliation_v1.json) records the source and calculation scope. A separate annuity formula reproduced both November prices to publication precision. G6.3 remains **OPEN / NOT READY**. Paid silver history is deferred, RBI T-bill payment timing is open, and investment authorization remains **NO-GO**.
