# 6.94% GoI 2036 retail quote route and freshness check

**Checked** 25 November 2026. **Disposition** `NSE_RETAIL_ROUTE_AND_SIZED_OFFER_SAMPLE_VERIFIED_LIVE_BROKER_QUOTE_OPEN`.

## Exchange route

NSE admitted `IN0020260025` to its Capital Market segment as `694GS2036`, series `GS`, from 13 May 2026. The exchange market lot is one unit of ₹100 face. This listing provides a retail route alongside RBI Retail Direct. A 100-unit test represents ₹10,000 face and does not select a portfolio order size. [Listing circular CML74143](https://nsearchives.nseindia.com/content/circulars/CML74143.pdf) · [NSE Capital Market bond specifications](https://www.nseindia.in/static/products-services/traded-on-cm)

NSE Capital Market uses dirty price, with accrued interest included. The observed ask in rupees per unit multiplied by units gives before-fee consideration. Add only applicable transaction charges to that amount. Under NSE Clearing's November normal-market T+1 schedule, a trade on 25 November would have settled on 26 November 2026. This was a read-only check. No trade took place. [NSE normal settlement calendar, Annexure A, M 2026222](https://nsearchives.nseindia.com/content/circulars/CMPT76729.pdf)

## What was observable

| Venue and field check | Result |
|---|---|
| NSE public bond quote, Bonds → All Securities → Trade Info | The exact symbol, series, ISIN and maturity matched. The rendered book showed an ask and a visible quantity sufficient for 100 units. Its displayed timestamp was **14:13:05 IST**. The table and quote refresh controls still showed that timestamp at **14:39:57 IST**. The capture demonstrates earlier same-day sell-side depth. Quote freshness at the time of viewing remains unverified. [NSE bond quote](https://www.nseindia.in/get-quote/bonds/694GS2036/Government-of-India) |
| CCIL public NDS-OM Odd Lot Market Watch | The rendered government-securities table contained dated rows, but the checked snapshot at **14:40:55 IST** contained no row for this bond by description or maturity. This finding applies to the public snapshot. An authenticated retail book or a dealer quote may differ. [CCIL Odd Lot Market Watch](https://www.ccilindia.com/odd-lot-mkt.-watch) |
| Groww public documentation | Groww describes access to listed bonds generally. Public sources did not confirm account-level availability, live order depth or fees for this exact ISIN. The account was not opened or used. [Groww bonds](https://groww.in/bonds) |

The [observation receipt](observations_v1.json) retains identifiers, timestamps and qualification outcomes. Exchange prices, quantities, screenshots and account data are excluded from the public repository. No snapshot was imported into a portfolio run. [NSE site terms](https://www.nseindia.in/static/nse-terms-of-use)

## Acceptance for a current all-in quote

1. In the investor's broker, look up `694GS2036` on **NSE Capital Market**, series `GS`, and match ISIN `IN0020260025`. Record the current timestamp, best bid/ask and available ask quantity. Calculate cost for the intended quantity across enough visible ask levels. A spot bond, a derivative and a negotiated trade print each have different execution semantics.
2. Verify the applicable settlement date, dirty consideration, broker/market fees and all-in amount in a read-only preview. For RBI Retail Direct, use the odd-lot quote and the venue's accrued-interest and settlement fields. Compare all-in consideration on the same face amount before comparing yield. [RBI Retail Direct market-making route](https://www.rbi.org.in/scripts/FS_Notification.aspx?Id=12216)
3. Record the time, venue and verified fields privately where use is permitted. Keep credentials and account details out of evidence. A displayed offer can expire or change. The gate requires a current, size-qualified price with verified access and charges before it can feed a hold-to-maturity comparison.

The NSE route and earlier displayed offer are available evidence. A fresh broker-confirmed quote and all-in cash remain open. G6.3 is **OPEN / NOT READY**. Paid Silver ETF history stays deferred, RBI T-bill payment timing stays open, and investment authorization remains **NO-GO**.
