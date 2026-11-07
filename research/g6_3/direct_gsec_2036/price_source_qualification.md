# G6.3 — Direct GoI 2036 price-source qualification assessment

**Assessment date:** 2026-11-07  
**Instrument:** 6.94% GS 2036, ISIN IN0020260025  
**Disposition:** Official data routes identified; no long-run price series qualified.

## Source routes assessed

| Source | What it provides | Suitability | Gate / limitation |
|---|---|---|---|
| CCIL Volumewise Outright Trade report | Security-wise reported outright trade summary by date, including trade count, volume, high/low and weighted-average price/yield. The page says it summarizes outright trades reported to CCIL for settlement. | Potential source for historical observed market trade-price series and liquidity context. | CCIL page states it does not authorize commercial use without written permission. This repository is public; permission/licensing for redistribution is unresolved. The daily weighted-average statistic is not an executable retail quote, order-book bid/ask, or investor-specific fill. Exact price basis and aggregation methodology must be pinned before cashflow use. |
| CCIL G-Sec Historical Trades | Trade-by-trade outright government-security transactions. | Could support price/volume distributions, execution-size analysis and source cross-checks. | Current page requires sign-in and carries the same use restriction. No authenticated data was accessed. |
| AMFI consolidated debt transaction disclosures | Settlement-date-wise MF debt-security transactions; table includes trade date, settlement date, quantity, face value, traded price, accrued interest, trade/valuation yields, and trade type. Searchable by ISIN, with Excel export. SEBI requires disclosures with a 15-calendar-day lag in downloadable, machine-readable format. | Potential limited source for MF-reported observed transactions, if AMFI grants use/retention rights suitable for this public repository. | AMFI Terms of Use permit personal, non-commercial site access but prohibit publishing site content and electronically storing a significant portion without written approval. Do not export, retain, automate, or publish transaction rows in this repository without written permission or a qualified rights determination. Even with permission, it is not the full market, order book, or retail quote; MF trades are not investor-executable fills. |
| FBIL daily GOI valuation prices/yields | Daily security valuation benchmarks and curves, including archived files. | Possible mark-to-market source where a security is covered; useful for valuation/model inputs. | These are valuation marks, not necessarily executed or executable prices. FBIL states valuation benchmark data is fee-liable for live use; published fee schedule distinguishes valuation from other purposes. Current public historical download rights and terms for this personal research/public repository were not established. Do not automate or redistribute without resolving license. |
| RBI market summary | Current G-Sec market-trend yield on RBI homepage. | Context only. | The observed 6.94% GS 2036 figure is a market-trend yield, not a security price, trade, historical series, or retail quote. Excluded from any cashflow price path. |
| NSE/BSE debt segment | Exchange-negotiated trade/market data may provide retail-segment evidence. | Possible comparison for accessible smaller-lot prices if historical records are available. | No lawful, reproducible full-history export for this ISIN was qualified in this assessment. A displayed or delayed quote must not be treated as execution proof. |

## Official references

- [CCIL Volumewise Outright Trade](https://www.ccilindia.com/volumewise-outright-trade) — security-wise trade summary description and commercial-use notice.
- [CCIL G-Sec Historical Trades](https://www.ccilindia.com/g-sec-historical-trades) — trade-by-trade source and use notice.
- [RBI G-Sec FAQ](https://www.rbi.org.in/commonman/english/scripts/FAQs.aspx?Id=711), Q14/Q32 — RBI identifies CCIL traded-price information and FBIL as a price-information source; Q12 explains why market-lot liquidity matters.
- [FBIL GOI Prices archive](https://www.fbil.org.in/) — daily archive entry point.
- [FBIL G-Sec valuation benchmark pricing notice](https://www.fbil.org.in/uploads/Pricing_of_FBIL_G_Sec_Valuation_and_SDL_Valuation_benchmarks_c4832dcaaa.pdf) — pricing and fee-liability terms effective 1-Apr-2022.
- [RBI Financial Markets Watch](https://rbi.org.in/scripts/financialmarketswatch.aspx) — links to CCIL outright-trade data.
- [AMFI Transaction in Debt and Money Market Instruments](https://www.amfiindia.com/otherdata/transaction-in-debt) — official searchable transaction table and Excel export, currently reporting through 23-Oct-2026.
- [SEBI circular on debt-transaction disclosure](https://www.sebi.gov.in/sebi_data/attachdocs/sep-2020/1598962540197.pdf) — prescribes daily disclosure with a 15-calendar-day lag in comparable, downloadable, machine-readable format.
- [AMFI Terms of Use](https://www.amfiindia.com/terms-of-use) — personal, non-commercial access is permitted; publication and electronic retention of a significant portion are prohibited absent written agreement.

## Data gate and next action

Do not start the direct-security return series from one auction price or a benchmark yield. AMFI's public transaction table is a possible source only after written permission clarifies whether the investor may export, retain, calculate from, and publish derived transaction evidence in this public repository; its current terms do not authorize those actions. Do not download or preserve AMFI rows pending that clarification. The immediate repository-compatible route is to resolve allowed use and reproducibility for CCIL or NSE data, or identify an independently licensed source. Keep the existing bounded NSE inquiry as an unsent draft; do not send it without authorization. Once a source is licensed, preserve bytes/hash, pin trade/settlement dates and price basis, detect duplicates/reversals, quantify no-trade gaps, and reconcile samples across permitted sources. If rights permit only private use, keep raw data outside the public repository and publish no derived values unless the written terms allow it.

After source qualification, distinguish (a) observed secondary-market prices for realized-market research, (b) noncompetitive auction weighted-average prices for primary issues, (c) fair-value marks for mark-to-market valuation, and (d) investor-specific executable quotes. Historical return research can use an appropriately sourced and dated observed-price series or valuation series, but must keep their meanings separate; neither a fair-value mark nor a historical trade summary establishes a future executable quote.

**Current evidence status:** one primary auction observation is qualified for its auction outcome and clean-price basis. AMFI's interface and field definitions were reviewed, but no transaction rows were exported or retained because its published Terms of Use do not authorize publishing or significant electronic retention without written permission. No post-issue transaction dataset, retail execution spread, or investor-specific future contribution/exit price series is qualified. G6.3 remains open; investment authorization remains NO-GO.


## NSE exchange-data route (new finding)

NSE’s historical-report catalogue lists WDM historical security-wise price/volume data, and the WDM Historical page exposes security/date filters and a CSV export. NSE’s formal Data Sharing & Usage Policy says the rules apply to debt-segment market data, covers historical data, states ownership remains with NSE/NSE Data, and generally prohibits redistribution unless the relevant agreement permits it. It also describes non-commercial research access as agreement-based, with confidentiality terms; possible reduced fees/waivers are discretionary. The posted WDM End-of-Day data tariff is ₹44,000 per medium. Therefore, the web form’s apparent availability is not enough to establish permission to download, retain, automate, or publish a dataset. No NSE price file has been downloaded in this assessment.

Official sources: [NSE WDM Historical report](https://www.nseindia.com/report-detail/historical-wdm), [NSE Data Sharing & Usage Policy](https://www.nseindia.com/static/market-data/nse-data-policy), [NSE End-of-Day/Historical Data page](https://www.nseindia.com/static/market-data/eod-historical-data-subscription), [WDM EOD tariff PDF](https://nsearchives.nseindia.com//web/mediaattachment/2026-04/Download_End_of_the_Day_Data_Tariff_20260424120810.pdf).

### Security-history limit

6.94% GS 2036 was originally issued on 11-May-2026. As of this assessment date, it has less than six months of possible instrument-specific market history. No lawful source can produce a 2015–2026 realized price history for this security itself. The model must separate: (1) exact bond contractual cashflows and acquisition price, (2) actual observed price history since issue for calibration/checks, and (3) longer historical sovereign-rate or duration-proxy scenarios for early-exit risk. A proxy must be labeled as such and cannot be presented as the bond’s own realized history.

### Draft rights inquiries (not sent)

`nse_wdm_data_access_inquiry_draft.md` requests limited non-commercial access terms for a narrowly scoped WDM history sample. `amfi_transaction_data_rights_inquiry_draft.md` asks whether AMFI would permit a limited private export and specified non-identifying derived summaries. Neither draft represents the investor or transmits personal data. Neither request has been sent.

### Bounded CCIL live-source probe — 2026-11-07

CCIL's public [Tenorwise Indicative Yields](https://www.ccilindia.com/tenorwise-indicative-yields) page showed the 9Y–10Y tenor on 06-Nov-2026 assigned to 6.94% GS 2036 at 7.1816% YTM. CCIL labels this a security of indicative tenor and describes the page as indicative yield movement. It is a dated market-context observation, not an executed trade, clean/dirty price, executable bid, investor fill, or guaranteed return. It is not used in the cashflow model.

The official [Volumewise Outright Trade](https://www.ccilindia.com/volumewise-outright-trade) page describes a security-wise summary of outright trades reported to CCIL for settlement and exposes trade count, volume in ₹ crore, high/low price, weighted-average price and yields. This appears to be a candidate source for the observed-market-price-history gate. CCIL's pages state that CCIL does not authorize commercial use of website data without written permission. No trade series was downloaded, hashed, retained, or republished in this increment; no authenticated trade-by-trade access was used. Rights and permitted public-repository use remain unresolved.

**Result:** a public first-party route exists for a summary of settled/reported outright trade activity, but it does not itself establish retail execution conditions, bid/ask depth, actual investor access, or rights to reproduce the series. Until lawful use and exact aggregation/price-basis semantics are resolved, do not add CCIL observations to public raw-source files or use a single indicative yield as the bond's price. The current indicative observation does not change the G6.3 decision gate.
