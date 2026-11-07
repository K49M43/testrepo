# 6.94% GS 2036: October 2026 reissue evidence

This bounded source package reconciles the official Government of India security-specific Gazette notification with the RBI full auction result for the 16-Oct-2026 reissue. It establishes one historical auction observation and nominal contractual cashflows. It does not qualify a long-run return series, an executable retail price, or an investment recommendation.

## Reconciled terms and auction outcome

- Security: 6.94% GS 2036, ISIN `IN0020260025`.
- Original issue: 11-May-2026; maturity: 11-May-2036; coupon: 6.94% p.a., payable half-yearly on 11-May and 11-Nov; principal redeemed at par.
- Auction: 16-Oct-2026; issue/settlement date: 19-Oct-2026; multiple-price auction; notified amount ₹34,000 crore.
- Competitive cutoff: clean price ₹96.91 per ₹100; YTM 7.3955%.
- Competitive weighted-average: clean price ₹96.93 per ₹100; yield 7.3925%.
- Noncompetitive bids: five accepted, ₹39.291 crore. The scheme uses the competitive weighted-average price for noncompetitive allotment; this is not an investor-specific allotment advice.
- The specific Gazette says accrued interest for this reissue is due through **18-Oct-2026**.

## Conditional settlement arithmetic

RBI FAQ Q25 and FBIL methodology state the general Indian G-Sec market day-count convention is 30/360. The specific notification fixes the accrual cutoff at 18-Oct. Applying 30/360 from the previous coupon date, 11-May, through 18-Oct gives 157 days:

`6.94 × 157 / 360 = ₹3.026611 accrued interest per ₹100 face value`.

At the noncompetitive weighted-average clean price of ₹96.93, clean plus accrued is ₹99.956611 per ₹100 face value, or **₹9,995.66 per ₹10,000 face value**, before any applicable fee. The Gazette permits an aggregator/facilitator charge up to ₹0.06 per ₹100 (₹6 per ₹10,000 face). Actual investor route, fee and settlement rounding are not verified. RBI FAQ Q22's worked example reports one day more than the explicit 30/360 formula, so the amount remains labeled a conditional calculation pending settlement-level confirmation.

## Preserved sources and reproducibility

- RBI full auction result: [`auction_result.pdf`](auction_result.pdf), SHA-256 `4AA2AB8428124182CF0E4D9A875FA29FEC7B666C8D39E85485B6DC2E8F9366AF`.
- Government of India specific notification: [`specific_notification.pdf`](specific_notification.pdf), SHA-256 `D70A72BE3FC8CF411313F7DF3DBD5470ADFF1E7B2ABBFD5FA8C1C07DB3EAFDEB`.
- [Source manifest](source_manifest.json) records URLs, identifiers, byte counts and hashes.
- [Auction pair reconciliation](auction_pair_reconciliation_v1.json), [day-count review](day_count_reconciliation_v1.json), [nominal cashflow schedule](nominal_cashflows_v1.json) and [detailed source review](source_review.md) retain scope limits and arithmetic.

The deterministic audit is `decision/audit_g6_3_direct_gsec_2036.py`; it rechecks source hashes, security/date alignment, conditional calculation fields and the 20-event nominal coupon schedule. It does not validate a future price path or investor-specific return.

## Remaining G6.3 gates

- Qualify lawful, reproducible post-issue acquisition and exit-price evidence. AMFI transaction data must not be retained or published in this public repository without written permission under its [Terms of Use](https://www.amfiindia.com/terms-of-use). The source assessment and unsent rights inquiries are in the parent directory.
- Use separately labeled sovereign duration/yield proxies for longer early-exit stress history; this bond only has post-issue history since May 2026.
- Model investor-specific acquisition dates, contributions, coupon reinvestment, tax, fees, terminal date, and early-exit or hold-to-maturity paths after the necessary inputs are confirmed.
- Obtain settlement advice only if exact historical rounded auction debit is required.

This evidence closes the October notice/result source-pair and contractual-schedule subtask only. It does not close the direct-sovereign candidate gate, WP1, or G6.3. Investment status remains **NO-GO / NOT YET EVALUATED**. No transaction was placed.
