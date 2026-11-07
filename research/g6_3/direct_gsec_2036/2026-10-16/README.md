# 6.94% GS 2036: archived primary-auction result

This bounded source increment preserves the Reserve Bank of India (RBI) full auction result published for 16 October 2026. It supplies one historical primary-market observation for a dated Government of India security with a stated repayment date of 11 May 2036.

## What the retained source says

- Security label: 6.94% GS 2036.
- Auction date: 16 October 2026; settlement date: 19 October 2026.
- Notified amount: ₹34,000 crore.
- Competitive cut-off: price ₹96.91 per ₹100 nominal; YTM 7.3955%.
- Competitive weighted average: price ₹96.93 per ₹100 nominal; weighted-average yield 7.3925%.
- Noncompetitive bids received and accepted: five bids, ₹39.291 crore total.
- The announcement says this was a multiple-price auction. RBI's rules state noncompetitive allotment uses the weighted-average price/yield of successful competitive bids. The attached result itself reports the accepted noncompetitive amount, not its allotment advice to any particular investor.

## Provenance

- RBI announcement page: <https://rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=63792>
- The page labels the attachment “Government Stock - Full Auction Results” (318 kb). The downloaded original is retained as `auction_result.pdf`.
- Retrieved: 2026-11-07 (Asia/Kolkata).
- Original attachment SHA-256: `4AA2AB8428124182CF0E4D9A875FA29FEC7B666C8D39E85485B6DC2E8F9366AF`.
- The full manifest is `source_manifest.json`.

## Limits and next qualification work

This is an auction-history observation, not a current or future executable price, a guaranteed allotment, or an investor-specific trade record. The award is not a validated all-in purchase cost. The exact security-specific notification and its coupon schedule, ISIN, accrued-interest convention, fees/payment costs, individual allocation terms, and tax cashflows still need source-level reconciliation. A CAPTCHA was returned when the RBI-hosted linked specific-notification PDF was opened through the available public route; it was not solved or bypassed, so that document is not claimed as captured here.

No secondary-market quote series, bid/ask spread, depth, early-sale proceeds, or exit liquidity is qualified. This single auction cannot support a return forecast, covariance estimate, terminal-value probability, or a strategy ranking. Model work must not treat 7.3925% as a guaranteed holding-period return: future coupon reinvestment, price paid, holding date, taxes and exit choice matter.

No transaction was placed. This evidence closes only the historical auction-result capture subtask; it does not close the direct-sovereign candidate gate, WP1, or G6.3. Investment status remains NO-GO / NOT YET EVALUATED.
## Additional official security terms located (source bytes not yet retained)

A Government of India Gazette notification dated 1 June 2026 is available at <https://egazette.gov.in/WriteReadData/2026/273050.pdf>. Its text identifies the 6.94% GS 2036, original issue 11 May 2026, maturity 11 May 2036, 6.94% coupon, half-yearly coupon dates of 11 May and 11 November, and repayment at par on maturity. It is a June 2026 reissue notification, not the specific October reissue's settlement notice. The June notification's accrued-interest cutoff (7 June 2026) applies to its June auction and is not applied to the October 2026 result above.

The Gazette PDF was reviewed through the official-source indexed text, but its original bytes could not be retained and hashed in this increment because Chrome's PDF page was unavailable to the automation session. Therefore the raw-source/hash gate for this supplementary notification remains open. Before building cashflows, capture and hash the Gazette PDF and obtain the specific October reissue's accrued-interest/payment terms. The captured terms do not establish the security ISIN.