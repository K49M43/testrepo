# G6.3 ICICI Prudential Silver ETF source audit

The [licensed history follow-up](AUTHORIZED_NSE_HISTORY_SOURCES.md) verifies sampled availability across both symbols and identifies the parties that can confirm licensed delivery and use.

The [NAV comparison](SILVER_NAV_COMPARISON.md) tests the portfolio impact of switching 5% from gold to silver before deciding whether to pay for traded history.

**Evidence date** 25 November 2026

**Result** Historical AMFI NAV lineage passes for the declared window. The NSE pilot passes its sample checks. Full exchange price history, use rights and execution evidence remain open.

## Identify the candidate

ICICI Prudential Silver ETF is AMFI scheme `149464`, ISIN `INF109KC1Y56` and current NSE symbol `SILVERIETF`. ICICI Prudential records allotment on 24 January 2022. NSE lists 31 January 2022 as its first listing date and changed the symbol from `ICICISILVE` to `SILVERIETF` effective 20 December 2023. A full market panel must cover both symbols at the applicable dates with a constant ISIN. This gate covers the ETF. The Silver ETF Fund of Fund has its own holdings, fees and returns. [Issuer ETF page](https://www.icicietf.com/icici-prudential-silver-etf) · [NSE identity](https://www.nseindia.in/get-quote/equity/SILVERIETF/ICICI-Prudential-Mutual-Fund---ICICI-Prudential-Silver-ETF) · [NSE symbol change](https://nsearchives.nseindia.com/content/circulars/CML59760.pdf)

## AMFI NAV and issuer cross-check

The existing independent candidate NAV checker reconstructed **1,160 NAV observations** from ten hash-matched AMFI responses. The series spans **25 January 2022 to 30 October 2026** with unique positive observations and a maximum gap of five calendar days. The normalized CSV matches the reconstructed values. Its earliest three NAV dates precede NSE listing and have no role in the NSE traded price history.

| NAV date | Matching AMFI and AMC NAV per unit | Issuer source |
|---|---:|---|
| 31 December 2025 | ₹227.6864 | [December 2025 factsheet](https://digitalfactsheet.icicipruamc.com/passive/pdf/passive-fund-factsheet-december-2025.pdf) |
| 30 January 2026 | ₹329.5533 | [January 2026 factsheet](https://www.icicipruamc.com/blob/emailmedia/mutualfund/Passive%20Fund%20Factsheet%20January%202026%20_1.pdf) |
| 30 April 2026 | ₹237.5847 | [April 2026 factsheet](https://digitalfactsheet.icicipruamc.com/passive/pdf/passive-fund-factsheet-april-2026.pdf) |
| 30 October 2026 | ₹180.8909 | [October 2026 factsheet](https://www.icicipruamc.com/blob/downloads/Files/Historic%20Factsheets/2026-2027/Passive%20Simplified%20October%202026.pdf) |

The four comparisons are to the same named ETF and NAV date. The factsheets were reviewed online. The archive contains AMFI raw bytes and hashes, and this audit records the factsheet URLs and anchor values.

Keep two changes distinct in any evaluation. The AMC changed its benchmark from the LBMA AM fixing based measure to Domestic Prices of Silver on **30 January 2026**. SEBI changed the physical gold and silver portfolio valuation method to prescribed polled domestic spot prices from **1 April 2026**. These dates describe benchmark and valuation rules. This audit applies no unit adjustment and attributes no returns to either change. [AMC benchmark addendum](https://www.icicipruamc.com/blob/announcements/Notice%20cum%20Addendum.pdf) · [SEBI valuation circular](https://www.sebi.gov.in/sebi_data/attachdocs/feb-2026/1772102397057.pdf)

## NSE sample and rights

- The security history response contains **20 unique EQ dates from 1 to 30 October 2026**. OHLC, last price and volume passed consistency checks. Each of the 19 adjacent previous-close comparisons matched.
- The exchange daily bhavcopies for 30 September and 30 October each identify the same ISIN, symbol and series. The 30 October bhavcopy overlaps the October history and matches all nine compared fields (OHLC, last price, previous close, volume, turnover and trade count). The September report supplies a second identity observation outside the October sample.
- All **20 of 20** October close dates match an AMFI NAV date. This is pairing by date label. Exchange close and fund valuation can use different timestamps. Bid/ask spread, depth, execution costs and synchronized premium remain outside scope.
- Three bounded requests succeeded before the full terms review. NSE lists these report types as available for research, and separately restricts automated acquisition, publication and simulation use in its website terms. The [manifest](silver_etf_source_pilot_v1.json) retains response metadata, hashes and aggregate checks. Temporary market data payloads were removed after the audit. The published record supports review of the checks and re-acquisition through an authorized route. [Research data list](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Data%20list%20under%20NSE%20Data%20Sharing%20Policy%20for%20Research%20and%20Analysis_20250728.pdf) · [NSE terms](https://www.nseindia.in/static/nse-terms-of-use)

## Gate and reproduction

Rerun the existing offline G5.4 candidate NAV auditor for scheme 149464 with the repository inputs. The manifest lists the tested source hashes and acceptance checks. An authorized exchange history should cover all listing-date-to-cutoff sessions for both symbols, explain absent rows and corporate actions, check two independent daily-report anchors within the retained coverage, and permit the intended model use. The [NSE Data & Analytics route](https://www.nseindia.in/static/nse-data-and-analytics/contact-us) can confirm permitted acquisition, retention and use for the requested instrument. A licensed alternative must explicitly cover the same historical fields and intended use. Public code and evidence metadata can support reproducibility while licensed inputs remain private if required by the license.

The sample qualifies exchange source feasibility. Completeness, corporate actions, execution economics, costs, and portfolio model use remain open. The existing RBI payment timing gate remains open. G6.3 stays **OPEN / NOT READY**, with investment authorization **NO-GO**.

```powershell
@'
import runpy
module = runpy.run_path("research/stage512/2026-11-05/g5_4/audit_g5_candidate_nav_history.py")
print(module["audit"]("149464", module["SPECS"]["149464"]))
'@ | py -B -
```
