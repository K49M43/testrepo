# G5.2 — Point-in-time candidate and evidence register

**As of 2026-11-05 · Evidence increment v1 · Research only · Investment authorization NO-GO**

## Purpose and boundary

This is a candidate hypothesis register for later decision analysis. It does not rank products, forecast returns, estimate success probabilities, decide suitability, or authorize any transaction. Product existence is distinguished from investor-specific availability. Groww account access, risk constraints, terminal date and product suitability remain unverified. See [machine-readable register](g5_2_candidate_evidence_register_v1.json).

## Candidate inventory

| Candidate | Category | Class | Instrument identity | Dated evidence / primary gap |
|---|---|---|---|---|
| NIFTY500_TRI_BENCHMARK | equity | PROXY_ONLY | Nifty 500 TRI (index identifier as in official source files; exact vendor code not separately asserted) | 2025-09-30 (last qualified repository monthly anchor) / Exact current index identifier/code and current history beyond September 2025 not qualified in this increment. |
| MOTILAL_NIFTY500_ETF | equity | INVESTABLE | ISIN INF247L01BU1; AMFI 152106; scheme CMT 44332 | 2026-09-30 holdings / AMC page includes conflicting template content; official workbook and exact product identifiers govern holdings facts, while fee/page fields need independent current check. |
| MOTILAL_NIFTY500_INDEX_FUND | equity | INVESTABLE | ISIN INF247L01957; AMFI 147625; CMT 40785; Direct Growth | 2026-09-30 holdings / AMC page has contradictory copied marketing/risk text; rely on official statement for the exact dated holdings, resolve metadata from scheme information document. |
| GOI_DIRECT_DATED_GSEC_718_2033 | direct_government_security | BLOCKED | RBI security identifier IN0020230085; 7.18% Government of India dated security; maturity 2033-08-14 | 2026-11-05 evidence review; price/availability date unavailable / No current clean/dirty price, accrued interest, yield, bid/ask, outstanding balance vintage, or auction calendar. |
| LIC_GSEC_8_13_ETF | sovereign_bond_fund_or_etf_proxy | PROXY_ONLY | AMFI 133307; ISIN INF767K01MV5; NSE LICNETFGSC | 2026-09-30 holdings / Three sovereign holdings are reported by coupon/redemption date but factsheet omits ISINs; identifiers left null and no external mapping inferred. |
| ICICI_GOLD_ETF | gold | INVESTABLE | ISIN INF109KC1NT3; AMFI 113076; NSE GOLDIETF | 2026-10-30 NAV; holdings snapshot last evidenced 2026-03-31 factsheet / Holdings snapshot is 219 days old as of 2026-11-05; acquire newer monthly disclosure before use. |
| ICICI_SILVER_ETF | silver | INVESTABLE | ISIN INF109KC1Y56; AMFI 149464; NSE SILVERETF | 2026-10-30 NAV; holdings snapshot last evidenced 2026-03-31 factsheet / Holdings snapshot is 219 days old as of 2026-11-05; acquire newer monthly disclosure before use. |
| CASH_HOLD_91D_TBILL_ROLLING | cash_hold_comparator | BLOCKED | Policy comparator: successive RBI 91-day Treasury Bills, auction/reinvestment strategy; no single stable ISIN | 2026-11-05 comparator definition; rate as-of unavailable / No exact bill ISINs, auction cutoffs or reinvestment schedule collected. |

## Dated holdings evidence

### Motilal Oswal Nifty 500 products — 2026-09-30

Official AMC spreadsheets are retained byte-for-byte. Each lists 498 equity rows with 498 ISINs; 497 rows have numeric weights. MMTC is shown as “<$0.005%”; its weight remains null. No synthetic zero is assigned.

- ETF: equity 99.68%, net receivables 0.32%, grand total 100%; regular TER 0.18%. Top-10/top-20 reported equity weights are 28.49% / 38.74%.
- Index fund: equity 99.74%, Triparty Repo 0.28%, net receivables −0.02%, grand total 100%; direct TER 0.13%, regular TER 0.79%. Top-10/top-20 reported equity weights are 28.52% / 38.77%.
- Both name Nifty 500 TRI as primary benchmark. Product holdings remain distinct from benchmark constituents; ETF traded-price return remains distinct from mutual-fund NAV return.

All 498 equity ISINs are shared. Exact-ISIN overlap is 99.68% of numeric reported equity weights, calculated as Σ min(ETF weightᵢ, index-fund weightᵢ) over matched IDs with reported numeric weights. Source weights are rounded to 0.01 percentage point, and MMTC has no numeric weight, so this is approximate. It is holdings overlap, not return correlation. Actual AMFI industry weights are separately calculated and retained in [holdings diagnostics](g5_2_holdings_overlap_v1.json).

### LIC MF Nifty 8–13 Year G-Sec ETF — 2026-09-30

The official September 2026 factsheet states 99.50% sovereign holdings, 0.16% TREPS/repo, 0.35% net receivables (cash-and-other total rounds to 0.50%), and 100.00% grand total. It reports 0.14% BER, modified duration 6.71 years, YTM 7.24%, and tracking error 0.24%. Three bond labels and weights are given without ISINs: 6.94% GoI redeeming 2036-05-11 at 58.87%; 6.48% GoI redeeming 2035-10-06 at 25.51%; 7.18% GoI redeeming 2037-07-24 at 15.11%. IDs remain null. This changing bond-fund NAV is a proxy, not direct sovereign cashflows.

### Gold and silver ETF dated holdings — 2026-03-31

ICICI Prudential’s official passive factsheet reports Gold ETF: 98.21% Gold (995 Purity), 1.79% short-term debt/net current assets; Silver ETF: 99.08% silver, 0.92% short-term debt/net current assets. These snapshots are 219 days old as of register date. The factsheet provides aggregate exposures, not bar serials or itemized cash/debt constituents. These are explicitly stale, not current holdings. Official AMFI NAV samples through 2026-10-30 establish sampled source identity only; the repository's full-history metrics are from a third-party mirror and remain unqualified for return calculations.

### Direct GoI security and cash comparator

The direct candidate is a dated 7.18% GoI security, RBI identifier IN0020230085, maturity 2033-08-14. Historical issuance identity is evidence only; current price, availability, depth, settlement, tax and investor route are unverified. Maturity precedes 2036, so sale or reinvestment must be modeled. The cash-hold comparator is a rolling 91-day T-Bill policy; dated auctions, yields and reinvestments are not captured and the comparator remains BLOCKED.

## Sources and reproducibility

- [Motilal Oswal Nifty 500 ETF page](https://www.motilaloswalmf.com/mutual-funds/motilal-oswal-nifty-500-etf) and [official dated portfolio workbook](https://www.motilaloswalmf.com/content/dam/motilal-mf/sheets/fund-csvs/Month_End_Portfolio_September_2026/YO45.xlsx).
- [Motilal Oswal Nifty 500 Index Fund page](https://www.motilaloswalmf.com/mutual-funds/motilal-oswal-nifty-500-index-fund) and [official dated portfolio workbook](https://www.motilaloswalmf.com/content/dam/motilal-mf/sheets/fund-csvs/Month_End_Portfolio_September_2026/YO18.xlsx).
- [LIC MF September 2026 factsheet](https://www.licmf.com/assets/downloads/monthly_fact_sheet/2026-2027/10/lic-mf-factsheet-30th-September-2026.pdf); [LIC MF disclosure page](https://www.licmf.com/addendum-notice).
- [ICICI Prudential March 2026 passive factsheet](https://www.icicipruamc.com/blob/sebi-repo/Advertisements/2026/April/Filing%20date%2014-04-2026/Release%20date%2010-04-2026/Advertisements/Annexure%203%20-%20Passive%20Factsheet.pdf).
- [RBI security listing](https://systemhealth.rbi.org.in/Scripts/bs_viewcontent.aspx_Id%3D1956.html); [RBI Retail Direct FAQ](https://www.rbi.org.in/commonperson/english/Scripts/FAQs.aspx?Id=3550). Historical/source-family evidence only, not current purchase availability.
- Raw source byte lengths, SHA-256, retrieval metadata and normalized CSV hashes are in [holdings JSON](g5_2_holdings_overlap_v1.json). AMC workbook publication timestamps are not embedded; HTTP response headers were not preserved.
- Re-run: `python decision/audit_g5_2_candidate_register.py --check` (Python 3.13, openpyxl 3.1.5).

## Disposition

The six required categories are represented. G5.2 supplies a reproducible evidence baseline, not an investment decision. Newer gold/silver holdings, current execution, tax, direct-security tradability and Groww access remain blocked. G5.3 independent audit is required before G5 disposition. G6 remains blocked; investment authorization is **NO-GO**.
