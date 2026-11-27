# ICICI Prudential Silver ETF licensed history sources

**Checked** 25 November 2026

**Result** Exchange availability verified at four boundary dates across both symbols. The providers below are documented sources. Permission for the specified historical dataset and portfolio modelling remains pending.

## Request scope

Request a single dated export of official **NSE Capital Market EQ** daily history by ISIN `INF109KC1Y56`, from listing on **31 January 2022** through the existing AMFI comparison cutoff of **30 October 2026**.

| Dates inclusive | NSE symbol |
|---|---|
| 31 January 2022 to 19 December 2023 | `ICICISILVE` |
| 20 December 2023 to 30 October 2026 | `SILVERIETF` |

The exchange records a symbol change with the same ISIN. Request the original exchange symbols and date labels even if the provider stores a single series under the current symbol. [NSE quote and listing date](https://www.nseindia.in/get-quote/equity/SILVERIETF/ICICI-Prudential-Mutual-Fund---ICICI-Prudential-Silver-ETF) · [NSE circular CML59760](https://nsearchives.nseindia.com/content/circulars/CML59760.pdf)

## Official availability check

The [NSE Bhavcopy connector](https://www.nseindia.in/nse-mcp) documents a rolling five years of daily data, with up to three months per history response. Four initial single-date calls returned no usable date record. The documented history tool then returned the following four bounded samples.

| Symbol | Requested end date | Observed first and last date | Rows observed |
|---|---|---|---:|
| `ICICISILVE` | 31 January 2022 | 31 January 2022 | 1 |
| `ICICISILVE` | 19 December 2023 | 20 November to 19 December 2023 | 21 |
| `SILVERIETF` | 20 December 2023 | 20 December 2023 | 1 |
| `SILVERIETF` | 30 October 2026 | 30 September to 30 October 2026 | 21 |

These lookups establish sampled boundary availability. Complete history, missing sessions, and close-field equivalence still require delivery and audit. The [probe metadata](nse_bhavcopy_mcp_probe_v1.json) keeps dates, counts, retrieval timestamps and hashes. No raw responses or prices were retained. NSE describes the connector as informational and applies its website terms. A rolling window may also age out the first listing sessions. Use it as a source availability check while securing an agreed export and retention route. [MCP scope and disclaimer](https://www.nseindia.in/nse-mcp) · [NSE website terms](https://www.nseindia.in/static/nse-terms-of-use)

## Providers and evidence

| Route | Confirmed from primary sources | What still needs a written answer |
|---|---|---|
| **Global Financial Datafeeds LLP** | NSE lists it as an authorized real-time Capital Market vendor. Vendor documentation advertises NSE cash daily history since 2010, CSV delivery and a toggle for unadjusted prices. Its individual APIs are offered for personal use and its API terms limit simulation uses. [NSE vendor list](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Authorized_Realtime_Data_Vendors.pdf) · [History coverage](https://globaldatafeeds.in/global-datafeeds-apis/global-datafeeds-apis/introduction/type-of-data-available/) · [API and terms](https://globaldatafeeds.in/apis/) · [CSV format](https://globaldatafeeds.in/resources/API_Example_pdf/GFDL_REST_GetHistory_CSV_FORMAT.pdf) · [Unadjusted history option](https://globaldatafeeds.in/global-datafeeds-apis/global-datafeeds-apis/rest-api-documentation/function-gethistory/) | Legacy symbol availability, official close field, one-time price, coverage dates, retention period and explicit permission for offline portfolio modelling. Contact `sales@globaldatafeeds.in`. [Sales](https://globaldatafeeds.in/global-datafeeds-apis/global-datafeeds-apis/contact/contact-sales/) |
| **NSE Data & Analytics** | The exchange's own licensed source. The domestic tariff lists annual Capital Market Historical Trade Data at **₹1,10,000 per site** before taxes, for the listed product. The agreement defines use, handling and dissemination. [Historical products](https://www.nseindia.in/static/market-data/eod-historical-data-subscription) · [Domestic tariff](https://nsearchives.nseindia.com//web/mediaattachment/2026-04/Download_Pricing_file_-_Domestic_clients_20260424122229.pdf) · [Usage policy](https://www.nseindia.in/static/market-data/nse-data-policy) | Whether it offers a smaller single-ISIN daily bhavcopy extract or written permission for this use and what that costs. Contact `marketdata@nse.co.in`. [Contact](https://www.nseindia.in/static/nse-data-and-analytics/contact-us) |
| **TrueData Financial Information Private Ltd** | NSE lists it as an authorized real-time vendor. TrueData lists NSE Equity coverage and advertises over ten years of daily bars. Its terms describe personal and internal analysis and restrict virtual or simulated trading and public sharing. [NSE vendor list](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Authorized_Realtime_Data_Vendors.pdf) · [Daily history](https://feedback.truedata.in/knowledge-base/article/historical-data-availability-through-rest-api) · [Product and use terms](https://www.truedata.in/market-data-apis) | Availability of the retired symbol, unadjusted official closes, export format, pricing and permitted offline portfolio modelling. Use its [market data enquiry](https://www.truedata.in/products/marketdataapi). |

The NSE vendor list establishes real-time vendor status. The specific historical supply and usage rights come from the agreement for the export being offered. Global Financial Datafeeds is the first quote route because its cash-market coverage and unadjusted CSV fields are documented. NSE Data & Analytics is the direct route for written clarification or an exchange extract. No supplier has replied, and no subscription or trial was requested.

## Copy-ready enquiry

**To** `sales@globaldatafeeds.in` or `marketdata@nse.co.in`

**Subject** One-time licensed NSE daily history for ICICI Prudential Silver ETF, ISIN INF109KC1Y56

Hello,

Could you quote a one-time CSV export of official NSE Capital Market EQ daily history for ICICI Prudential Silver ETF, ISIN INF109KC1Y56, from 31 January 2022 to 30 October 2026 inclusive? The NSE symbols are ICICISILVE through 19 December 2023 and SILVERIETF from 20 December 2023. Please confirm that your dataset includes both segments and can preserve the exchange symbol on each date.

At minimum, please include exchange trade date, original symbol, ISIN, series, unadjusted official close and traded quantity. If available, please also include open, high, low, turnover and corporate actions with effective dates. Please state whether Close is the official reported exchange close, which sessions have no observation, and whether distributions or corporate actions are applied to either price or volume. Could you provide sample rows or confirmation of coverage for 31 January 2022, 19 and 20 December 2023, and 30 October 2026?

The use is an individual investor's own local historical risk analysis and portfolio scenario modelling in Python. This includes internal calculations and reproducible reruns using private storage, with raw prices kept private. Please confirm in writing whether that use is covered, including any limits on local retention after the subscription ends, reruns, automated retrieval, use with an independent reviewer, and publication of audit metadata or derived summaries. Please specify any separate exchange permission or approval and quote the total one-time or minimum subscription price including applicable fees.

Thank you.

## Acceptance before modelling

1. Get written permission covering the specified analysis and storage. Record permitted reporting, review and post-subscription retention. Keep licensed raw inputs private unless the applicable agreement permits sharing.
2. Verify one ISIN and the two dated symbols, with first and last sessions and both sides of the transition present. Require one record per trading session or a provider explanation for missing and no-trade sessions. Preserve gaps and exclude any pre-listing rows or backfilled proxies.
3. Reconcile unadjusted official closes and traded quantity to independent first-party daily-report observations across both symbols, with exact prices and volumes on at least one date in each segment. Keep any documented distribution or unit adjustment separate from the raw prices.
4. Record a file hash, date and row counts, timestamps, data fields, contract scope and the reconciliation results. Joint-risk or execution model admission still requires the separate alignment, cost and validation gates.

**Status** Source availability checked. Licensed delivery and permitted portfolio use remain open. The RBI payment timing issue remains open. Investment authorization remains **NO-GO**.
