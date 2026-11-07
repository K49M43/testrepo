# G6.3 — Direct GoI 2036 security source review (bounded)

**Review date:** 2026-11-07  
**Disposition:** `OCTOBER_REISSUE_NOTICE_RESULT_PAIR_RECONCILED`; direct-security economic gate remains `OPEN`.  
**Decision state:** `NO_GO / NOT_YET_EVALUATED`.

## Scope

This note records primary-source terms for 6.94% GS 2036 and identifies what is still needed before it can enter a decision-grade cashflow comparison. It is not a security recommendation, executable quote, investor-specific return, or trade instruction. The investor supplied the October 2026 Gazette PDF; the exact bytes are retained in `specific_notification.pdf`, hashed, and text/visually reviewed. The machine-readable records are `source_manifest.json` and `auction_pair_reconciliation_v1.json`.

## Source-backed terms

| Field | Finding | Evidence status |
|---|---|---|
| Security | 6.94% GS 2036 | Official RBI auction announcement dated 12-Oct-2026; official Gazette reissue of the same security dated 01-Jun-2026 |
| ISIN | `IN0020260025` | RBI security listing identifies 06.94% GS 2036, issue 11-May-2026, maturity 11-May-2036 |
| Original issue / maturity | 11-May-2026 / 11-May-2036 | Official Gazette notification for the same security |
| Coupon | 6.94% p.a.; half-yearly on 11-May and 11-Nov | Official Gazette notification for the same security |
| Repayment | At par at maturity | Official Gazette notification for the same security |
| October reissue auction | Price-based, multiple-price; auction 16-Oct-2026; settlement/reissue 19-Oct-2026; notified ₹34,000 crore, optional additional subscription up to ₹2,000 crore | Official October Gazette PDF and RBI press release dated 12-Oct-2026 |
| Coupon accrual cutoff | Interest accrued through 18-Oct-2026; half-yearly coupon dates 11-May and 11-Nov; 6.94% coupon; par redemption at maturity | Official October Gazette PDF; day count mechanics separately supported by RBI G-Sec FAQ |
| Retail noncompetitive terms | Up to 5% allocation; minimum ₹10,000 face value and ₹10,000 multiples; maximum single bid ₹2 crore; one bid; allotment at competitive bids’ weighted-average price; up to ₹0.06 per ₹100 brokerage/commission/service fee; no funding-cost add-on | Official October Gazette PDF |
| Exact PDF bytes | 733,198 bytes; SHA-256 `D70A72BE3FC8CF411313F7DF3DBD5470ADFF1E7B2ABBFD5FA8C1C07DB3EAFDEB`; local retained copy hash matches supplied file | Official PDF downloaded from the supplied copy, eight pages, unencrypted; first page, English contract terms, coupon/accrual table, and fee terms visually reviewed |
| October auction result | Full RBI result dated 16-Oct-2026; 400 competitive bids, 113 accepted; cutoff ₹96.91 / YTM 7.3955%; weighted average ₹96.93 / WAY 7.3925%; all ₹39.291 crore noncompetitive bids accepted; no devolvement | Retained bytes SHA-256 `4AA2AB8428124182CF0E4D9A875FA29FEC7B666C8D39E85485B6DC2E8F9366AF`, matching the PR #65 source record |

Primary sources:

- [RBI, Auction of Government of India Dated Security, 12-Oct-2026](https://rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=63792)
- [Official Gazette notification for the same 6.94% GS 2036, 01-Jun-2026](https://egazette.gov.in/WriteReadData/2026/273050.pdf)
- [RBI security listing containing ISIN and issue/maturity dates](https://www.rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=12765)
- [October 2026 security-specific Gazette PDF](https://egazette.gov.in/WriteReadData/2026/277085.pdf) — publication `CG-DL-E-12102026-277085`; retained bytes and hash are recorded in the JSON manifest.
- [RBI G-Sec FAQ on accrued interest, settlement, clean/dirty price, and 30/360 basis](https://www.rbi.org.in/commonman/english/scripts/FAQs.aspx?Id=711)
- [PR #65 archived source evidence](https://github.com/K49M43/testrepo/pull/65) — RBI full auction-result PDF and its source manifest.

## Accrued-interest reconciliation

The Gazette says successful bidders pay on 19-Oct-2026, specifies accrued interest through 18-Oct-2026, and identifies this as a new security originally issued on 11-May-2026. RBI's G-Sec FAQ says accrued interest runs through the day before settlement and defines the Indian bond-market convention as 30/360. Applying that explicit convention gives 157 days from 11-May through 18-Oct and `6.94 × 157 / 360 = ₹3.026611...` per ₹100 face value, or `₹302.6611...` per ₹10,000 face value. **This is currently a conditional sensitivity, not a qualified settlement amount:** the same RBI FAQ's worked example for 25-Nov-2013 through 29-Jan-2014 reports 65 days, equal to actual elapsed days; 30/360 gives 64 days for those dates. This internal source inconsistency must be resolved before promoting the exact accrued-interest amount.

The matching RBI full auction result reports a weighted-average clean price of ₹96.93 per ₹100. The official retail noncompetitive rule uses this weighted-average price; it does not use the ₹96.91 cutoff price in this multiple-price auction. The resulting one-auction arithmetic is:

| Item | Per ₹100 face value | Per minimum ₹10,000 face value |
|---|---:|---:|
| Clean consideration at weighted-average price | ₹96.9300 | ₹9,693.00 |
| Accrued interest through 18-Oct-2026 | ₹3.0266 | ₹302.6611 |
| Dirty consideration before fees, 30/360 sensitivity only | ₹99.9566 | ₹9,995.6611 (₹9,995.66 rounded to paise) |
| Alternative actual/360 sensitivity | ₹100.0144 | ₹10,001.4444 |
| Maximum aggregator fee under the scheme | ₹0.0600 | ₹6.00 |

The 30/360 calculation is conditional because RBI FAQ Q22's worked example reports one more day than the formula while Q25 states 30/360. The specific Gazette notice does resolve the October auction cutoff as 18-Oct-2026. The computed ₹9,995.66 dirty amount per minimum lot is a historical auction arithmetic result, not proof of an individual award or actual collected cash. The ₹6 fee cap applies to an aggregator/facilitator; the investor's route and fee are not confirmed. The dirty-price arithmetic excludes that fee and any other separately applicable charges. Settlement rounding/collection practice has not been independently verified.

## Financial interpretation and controls

The 6.94% coupon is a contractual coupon rate on face value. It is not the bond's yield, expected portfolio return, or guaranteed after-tax wealth outcome. The RBI's Oct-12 notice says this is a price-based multiple-price reissue. For noncompetitive retail allotment, the governing scheme uses the weighted-average price emerging from competitive bids, not the cutoff price. Thus a model must use the correct auction price basis for its modeled route and keep coupon cashflows, accrued interest, fees, taxes, and reinvestment separate.

The auction's settlement is 19-Oct-2026 and the instrument matures 11-May-2036. This could only be an exact maturity match if the investor's terminal liquidation date and policy correspond to that maturity; those dates remain unconfirmed. Contributions after the auction date cannot be modeled as if they all bought at the October auction price. Later monthly or periodic purchases require dated market prices or explicitly labeled scenarios, and any position sold before maturity requires a source-qualified sale price. Do not splice a single auction price onto a decade-long bond return path.

## Remaining acceptance items for this security lane

1. **Completed in this increment:** integrate the official notification/result pair, hashes, conditional settlement calculation, nominal coupon schedule and deterministic audit into PR #65.
2. Build dated investor cashflows per modeled contribution lot with coupon reinvestment, current-law tax, fees, maturity/redemption or an explicitly priced early exit. Keep clean price, accrued interest, fees, taxes, and proceeds distinct.
3. Confirm the investor's terminal date and contribution dates before deciding whether this maturity is useful; later contributions and coupon reinvestment require separate dated assumptions/evidence.
4. Obtain a lawful, reproducible price path for acquisitions after the primary auction and any pre-maturity exits. A yield curve/model mark is not an executable retail quote.

The official notification-byte and auction-result pair are reconciled for this one reissue. RBI and FBIL sources support 30/360 as the general Indian G-Sec bond-market convention. The auction notice explicitly sets accrued interest as due through 18-Oct-2026 for the 19-Oct settlement; the 157-day amount is therefore correctly dated under 30/360. The RBI FAQ worked example remains inconsistent with the stated convention by one day, and exact settlement rounding is unverified. This is **not a qualified direct-bond return series** and does not close WP1, G6.3, or any investment decision gate.

## Nominal contractual cashflow schedule (new, bounded artifact)

The security terms imply 20 nominal semiannual coupon events after the 19-Oct-2026 reissue settlement, from 11-Nov-2026 through 11-May-2036. Each regular coupon is ₹3.47 per ₹100 face value (₹347 per ₹10,000 face value); the final nominal event also includes ₹100 principal redemption per ₹100 face. The event-by-event record is `direct_gsec_2036_nominal_cashflows_v1.json`.

This is a **contractual schedule skeleton**, not a price or return path. The RBI FAQ says coupon payments falling on Sunday or another holiday move to the next working day, while maturity redemption falling on Sunday or a holiday is paid on the previous working day. The nominal maturity date, 11-May-2036, is Sunday. Thus final coupon and principal may settle on different dates; the record keeps these dates unresolved pending the actual applicable holiday calendar and operational confirmation. Future public holidays have not been guessed. The regular coupon amount does not require a day-count calculation; primary-auction accrued interest is calculated only to the cutoff specified in its notice.

Schedule validation performed: JSON parses; 20 events are strictly chronological; first/last nominal dates are 11-Nov-2026 and 11-May-2036; each coupon amount is ₹3.47 per ₹100; only the last event includes ₹100 principal. This is a data-integrity check, not an investment return test.

RBI FAQ payment-date rule: [RBI G-Sec FAQ, questions on security terms and coupon/maturity dates](https://www.rbi.org.in/commonman/english/scripts/FAQs.aspx?Id=711) (lines 93–98 in the accessed page). The specific Gazette terms remain in the retained PDF and source manifest.

## Updated disposition

**Completed in this increment:** official auction notice/result pair reconciliation; source-byte preservation and hashes; notice-specific accrued-interest due-through date; conditional 30/360 calculation; nominal coupon/redemption schedule skeleton; deterministic source/arithmetic audit.

**Still open for G6.3:** resolve lawful data rights for a reproducible post-issue secondary-price series; if exact historical auction debit matters, obtain settlement advice to confirm amount rounding; qualify actual future acquisition and exit prices; compute investor-specific taxed, fee-adjusted cashflows after acquisition/contribution, terminal-date, tax, reinvestment and liquidation assumptions are confirmed. AMFI data must not be downloaded, retained, or published in this public repository unless written permission covers that use. This work does not qualify the direct-security lane or close G6.3.


## Governing general notification cross-check

The October-specific Gazette incorporates the Government of India’s General Notification F.No.4(2)-B(W&M)/2018 dated 26-Mar-2025. That notification says coupons are rounded to the nearest whole rupee, unless specified otherwise. At the minimum ₹10,000 face lot, this bond’s semiannual coupon is exactly ₹347, so the rounding provision does not change that modeled coupon amount. The general notification does not specify the accrued-interest day-count formula, so it does not resolve the FAQ illustration discrepancy. [Official Gazette, General Notification (2025)](https://egazette.gov.in/WriteReadData/2025/261972.pdf).


Price-source assessment: `direct_gsec_2036_price_source_qualification_v1.md`. Official CCIL and FBIL routes exist, but no direct-security historical price path is qualified: CCIL's published use restriction and public-repository redistribution are unresolved, while FBIL values are valuation marks and fee-liable live data, not executable retail prices.

NSE WDM price-source gate: see `direct_gsec_2036_price_source_qualification_v1.md` and unsent `nse_wdm_data_access_inquiry_draft.md`. NSE exposes WDM historical search/export, but its data policy and WDM EOD tariff require confirming use rights and fees; no price file was downloaded. The 6.94% GS 2036 itself was issued on 11-May-2026 and cannot supply a decade of instrument-specific price history. Any longer risk history must be a separately labeled sovereign yield/duration proxy.

## AMFI source-rights disposition

The official [AMFI transaction table](https://www.amfiindia.com/otherdata/transaction-in-debt) exposes security-level transaction fields and an Excel export. However, [AMFI Terms of Use](https://www.amfiindia.com/terms-of-use) permit personal, non-commercial access while prohibiting publication and electronic retention of a significant portion absent written approval. No transaction rows or export are retained in this evidence package; do not use AMFI observations in public-repository calculations until written rights cover export, retention, derived values, and publication. SEBI's [disclosure circular](https://www.sebi.gov.in/sebi_data/attachdocs/sep-2020/1598962540197.pdf) establishes the disclosure format and lag, but does not override AMFI's website-use terms for this repository. The immediate price-history gate is therefore a licensed CCIL/NSE route, AMFI written permission, or another independently licensed source.


## Primary-auction day-count cross-check

RBI Q23 on non-competitive bidding describes a price-based reissue and calculates accrued interest from 19-Oct-2001 to settlement on 06-Dec-2001 as 47 days, applying 47/360. This is a primary-auction example that directly supports 30/360 for accrued interest on a reissued dated Government security. It supports the 157-day date convention used for the October 2026 notice, whose specific cutoff is 18-Oct-2026 for settlement on 19-Oct-2026. The separate general-market FAQ Q22 example still reports 65 days where the 30/360 date difference is 64; that one-day inconsistency is disclosed and not silently normalized. The convention is supported, while the exact retail debit remains unverified because the actual settlement advice and rounding treatment are unavailable. [RBI FAQ on non-competitive bidding, Q23](https://www.rbi.org.in/scripts/FS_FAQs.aspx?Id=13).
