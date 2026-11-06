# G6.3 ETF execution-data source route review

**As of:** 2026-11-06 09:12 UTC  
**Scope:** first-party route and field audit for the four ETF candidates in the G5.2 register. This is source-route qualification only; no historical price panel or execution-cost series was acquired.

## Candidate identity and NSE route

| Candidate | NSE symbol / ISIN | First-party evidence | Route and present status |
|---|---|---|---|
| Motilal Oswal Nifty 500 ETF | `MONIFTY500` / `INF247L01BU1` | [NSE quote page](https://www.nseindia.com/get-quote/equity/MONIFTY500/Motilal-Oswal-Mutual-Fund---Motilal-Oswal-Nifty-500-ETF) | NSE page reports quote, order book, traded volume/value, impact cost, i-NAV, NAV, listing/trading status, and historical-data link. Point-in-time fields are available; historical rows not retrieved. |
| LIC MF Nifty 8–13 yr G-Sec ETF | `LICNETFGSC` / `INF767K01MV5` | [NSE quote page](https://www.nseindia.com/get-quote/equity/LICNETFGSC/LIC-MF---LIC-MF-G-sec-LT-ETF---GO) | Page reports price, order book, volume/value, impact cost, i-NAV and prior-date NAV. Current view shows a live/depth route, but no retained market-data bytes or history. |
| ICICI Prudential Gold ETF | `GOLDIETF` / `INF109KC1NT3` | [NSE circular confirming symbol and ISIN](https://nsearchives.nseindia.com/content/circulars/CML59760.pdf) | NSE ETF market watch provides price/volume/value/i-NAV/NAV fields for ETF listings. Candidate-specific quote history and date panel not acquired. |
| ICICI Prudential Silver ETF | `SILVERIETF` / `INF109KC1Y56` | [NSE quote page](https://www.nseindia.com/get-quote/equity/SILVERIETF/ICICI-Prudential-Mutual-Fund---ICICI-Prudential-Silver-ETF) | Page reports order-book depth, traded volume/value, impact cost, i-NAV, NAV, listing and trading status. Historical price panel not acquired. |

## Historical data and rights

- NSE's [Historical Reports index](https://www.nseindia.com/static/resources/historical-reports-capital-market-daily-monthly-archives) lists equity security-wise price-volume archives and ETF price, volume, and delivery-position archives.
- NSE's [ETF Market Watch](https://www.nseindia.com/market-data/exchange-traded-funds-etf) displays the market fields `open/high/low/previous close/LTP/volume/value/i-NAV/NAV/52-week range` for listed ETF securities.
- NSE's [Data Sharing Policy research-data list](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Data%20list%20under%20NSE%20Data%20Sharing%20Policy%20for%20Research%20and%20Analysis_20250728.pdf) places historical reports and daily security-wise OHLC/turnover among research data available on NSE's website. Separately, NSE's [paid EOD/historical-data page](https://www.nseindia.com/static/market-data/eod-historical-data-subscription) describes chargeable packaged EOD and order/trade products. The intended acquisition must use the public research-report route within its terms; do not assume that access to the paid historical trade feed is free.
- The configured local proxy currently refuses NSE requests, so no original archive files, response metadata, or hashes were retained in this review. Web-rendered pages establish source fields and route descriptions, not the actual historical panel.

## Required dataset and controls

1. For each listed ETF, retrieve official NSE daily OHLC, volume, traded value, delivery (if supplied), plus AMFI daily NAV for the exact scheme identity. Retain every original response/file, URL, retrieval timestamp, byte count, hash, symbol/ISIN mapping, and report schema version. Do not start the series before listing/inception; do not splice NAV into traded price.
2. Reconcile dates, symbol, ISIN, splits/face-value changes, suspensions, no-trade days, duplicate/revised rows, and closing price/volume to at least two official anchors. Preserve gaps and non-trading days rather than forward-fill market prices.
3. Calculate ex-post close-to-NAV premium/discount only on strictly date-matched records and label its timestamp limitation. Historical market depth/spread cannot be inferred from OHLCV. For current implementability, separately retain dated order-book bid/ask depth, i-NAV, NAV, traded volume/value, and impact-cost snapshots for representative sessions; calculate quoted spread and depth-at-size as separate measures.
4. Reconcile TER/other expenses and distributions from dated AMC/AMFI records; model personal brokerage and taxes only from investor-verified route/status and enacted rules for the run date. TER is not the complete execution cost.
5. Treat NSE daily price history as execution-price evidence, not as a substitute for total-return NAV/benchmark data. Treat scheme NAV as fund valuation, not an ETF execution price.

## Decision and next steps

The NSE route is documented and the four symbol mappings are supported by first-party pages/circulars. **No ETF source panel is yet qualified.** The local request to `https://www.nseindia.com/all-reports` failed through the configured proxy with connection refused; this is a local transport failure, not an NSE-origin denial. Do not bypass the proxy. Once the approved network route is restored, make a bounded download probe for one report and one ETF, verify bytes/schema/hash, then acquire complete candidate panels sequentially. If historical i-NAV is unavailable, report that execution-premium history as blocked and use the official traded-price series only for the scopes it supports.

The current G5.2 register contains eight candidates, while the G6.3/mandate screen calls for at least ten materially different strategies where appropriate. WP1 also needs at least two additional candidate hypotheses with stable identities and explicit qualify/reject rationale; do not pad the count with duplicate share classes or proxies that answer the same question.

**Disposition:** source-route research only. ETF traded-price/implementation costs, investor-specific product access, and two additional candidate hypotheses remain open. No allocation, return distribution, correlation, or probability was calculated. Investment status remains **NO-GO / NOT YET EVALUATED**.
