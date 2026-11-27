# HDFCGOLD NSE, AMFI, and fund-economics evidence

**Scope:** bounded source qualification for HDFC Gold ETF under G6.3. This package does not close G6.3 or authorize an investment. `hdfcgold_nse_amfi_bridge_v1.json` preserves the first audit; `hdfcgold_nse_amfi_bridge_v2.json` adds the valuation, corporate-action, instrument-change, trading-activity and price-cost review.

## Captured NSE source

- First-party source: [NSE Security-wise Archives](https://www.nseindia.com/report-detail/eq_security).
- Query selected in the public UI: Equity, `HDFCGOLD`, series `ALL`, `5Y`; displayed window 06-Nov-2021 to 06-Nov-2026.
- Raw download: `hdfcgold_nse_5y.csv` (179,671 bytes; SHA-256 `B4F88AD9135F942DDD6E695E7B708C6A10AF1DA957AE3646C5474CF6E6A6C0D4`). Workstation filesystem creation time was 2026-11-06T17:39:43.9505271Z; this is not an NSE server timestamp.
- 1,241 rows and unique dates; no duplicate dates or non-positive closes; all rows series `EQ`; maximum five-calendar-day gap between observed trading rows. The file contains 399 rows under legacy `HDFCMFGETF` and 842 under `HDFCGOLD`.
- [NSE circular NSE/CML/57054](https://archives.nseindia.com/content/circulars/CML57054.pdf) records the symbol change `HDFCMFGETF` → `HDFCGOLD`, effective 16-Jun-2023, for ISIN `INF179KC1981`. The observed transition agrees. The later scheme-name update is in [NSE/CML/72944](https://nsearchives.nseindia.com/content/circulars/CML72944.pdf).

## AMFI history: documented 100:1 unit rebase

The retained AMFI history for scheme `113049`, ISIN `INF179KC1981`, contains 2,918 observations from 2015-01-01 to 2026-10-30. Raw normalized source CSV SHA-256 is `66b5253e897a89fb0bfff1a44e83bc909c31373040389a32a561b5dbddd3ef0b`; original source windows and hashes are in `research/stage512/2026-11-05/source_retrieval_followup/candidates/`.

HDFC's [June 2026 factsheet](https://files.hdfcfund.com/s3fs-public/2026-06/Fund%20Facts%20-%20HDFC%20NIFTY%20Gold%20ETF_June%2026.pdf) documents that unit face value changed from ₹100 to ₹1, with allotment price ₹1,800.3288 to ₹18.0033, effective 19-Feb-2021; it says its return computations were adjusted. In the retained AMFI input, NAV on 19-Feb is ₹4,120.0604 and the next observation, 22-Feb, is ₹41.5242. The separate derivative `nav_113049_current_unit_basis.csv` divides rows before 22-Feb-2021 by 100, leaves later rows unchanged, and preserves raw NAV, factor, and source-segment hash per row. It does not edit or replace the raw input.

Across the transition, adjusted NAV moves from ₹41.200604 on 19-Feb to ₹41.5242 on 22-Feb (+0.7854%); the raw values must not be treated as a -99% investment loss. The independently reported HDFC five-year CAGR is 25.01% for the period ending 29-May-2026. The derived current-unit-basis NAV from 31-May-2021 (₹43.494) to 29-May-2026 (₹132.7263) gives 24.9987% using an exact five-year exponent (25.00% rounded). This is a close cross-check, not exact reproduction because the fund's annualization convention is not fully specified. The NSE five-year window begins in Nov-2021 and does not cross this event.

## Exact-date AMFI comparison and valuation regimes

There are 1,229 exact-date NSE/AMFI pairs. Twelve NSE dates have no same-date NAV in the retained AMFI snapshot: seven within its coverage dates and five after its final date (02–06 Nov-2026). The seven in-window dates are not individually classified here. Nothing was filled, interpolated, or dropped from the raw series.

The descriptive metric is `(NSE daily close / same-date AMFI NAV - 1) × 100`. Across all matched dates, median +0.0583%, median absolute difference 0.3151%, linear-interpolated 5th/95th percentiles -1.1634%/+0.7626%, minimum -3.7645% (10-Mar-2022), maximum +6.4853% (21-Jan-2026). It is not a synchronized premium/discount.

HDFC's [June-2024 SID](https://files.hdfcfund.com/s3fs-public/SID/2024-06/SID%20-%20HDFC%20Gold%20Exchange%20Traded%20Fund%20dated%20June%2028%2C%202024.pdf) described the then-current LBMA AM fixing plus conversions, delivery costs and notional duties/taxes. [SEBI's Feb-2026 circular](https://www.sebi.gov.in/legal/circulars/feb-2026/valuation-of-physical-gold-and-silver-held-by-mutual-fund-schemes_100001.html) changed physical gold valuation effective 01-Apr-2026 to recognized-exchange polled spot prices. HDFC's [Apr-2026 SID](https://files.hdfcfund.com/s3fs-public/SID/2026-04/SID%20-%20HDFC%20Gold%20ETF%20dated%20April%2022%2C%202026.pdf?VersionId=.N7oTFaaYPc1Mm9b8jO.Fp0lk077FkFh) identifies MCX for the spot valuation. It also states day-end NAV is computed at business-day close and published by 11 p.m. (or 9 a.m.); iNAV is published intraday from the current portfolio and latest available gold price and may be static or dynamic. Thus, same-date close and AMFI NAV are not guaranteed to be synchronized clocks.

There is a second structural break: HDFC's [fundamental-attribute addendum](https://files.hdfcfund.com/s3fs-public/2026-03/2059-%20Notice-%20Change%20in%20Fundamental%20attributes%20-%20HDFC%20Gold%20ETF-%20ETCD-w.e.f-%20April%2022%2C%202026.pdf?VersionId=vqbMTvRC.oT_yPvSfogeDNdsg1p9lpSA) took effect 22-Apr-2026 and expanded permitted gold-related instruments, including gold ETCDs. Therefore the post-April close/NAV comparison is split at both the SEBI valuation change and the later HDFC mandate change:

| Window and regime | Matched dates | Median absolute close/NAV difference | Range |
|---|---:|---:|---:|
| 08-Nov-2021–31-Mar-2026: LBMA valuation; prior HDFC mandate | 1,084 | 0.3399% | -3.7645% to +6.4853% |
| 01–21-Apr-2026: new spot valuation; before HDFC mandate amendment | 13 | 0.0983% | -0.4675% to +0.3431% |
| 22-Apr–30-Oct-2026: new spot valuation and amended HDFC mandate | 132 | 0.1572% | -0.5280% to +0.8263% |

The 13-day middle window is too small for a robust inference. Lower absolute differences in the newer periods are descriptive and cannot be causally assigned to the valuation rule: calendar regimes differ and HDFC's asset mandate also changed on 22-Apr.

HDFC factsheets record snapshots after the mandate amendment: gold 98.62%/cash and net assets 1.38% as of 29-May; 98.44%/1.56% as of 31-Jul; and 98.51%/1.49% as of 30-Sep-2026. TER is reported at 0.59% p.a. and annualized tracking error at 0.39% in those factsheets. They show aggregate Gold and cash categories; they do not separately disclose whether any gold ETCD exposure existed. Inception is 13-Aug-2010. Sources: [HDFC June factsheet](https://files.hdfcfund.com/s3fs-public/2026-06/Fund%20Facts%20-%20HDFC%20NIFTY%20Gold%20ETF_June%2026.pdf), [July factsheet](https://files.hdfcfund.com/s3fs-public/2026-08/HDFC%20MF%20Index%20Solutions%20Factsheet%20-%20July%202026.pdf), [October factsheet](https://files.hdfcfund.com/s3fs-public/Others/2026-10/Fund%20Facts%20-%20HDFC%20NIFTY%20Gold%20ETF_Oct%2026.pdf?VersionId=Urji0l0XNDIBQJrIAuoj84IDXdJFPsm9).

## July 2024 customs-duty event alignment

The official Ministry of Finance document dated 23-Jul-2024 records gold-bar total customs duty falling from 15% to 6%, effective from midnight 23/24-Jul-2024. HDFC's June-2024 SID describes the then-current gold valuation as including notional customs duty, taxes and levies. The reproducible event window is in `hdfcgold_nse_amfi_bridge_v2.json`; the table below reports observed close-to-previous-NSE-row return, AMFI NAV-to-previous-AMFI-row return, and same-calendar-date close/NAV difference. The latter is not synchronized.

| Date | NSE close return | AMFI NAV return | Same-date close/NAV difference |
|---|---:|---:|---:|
| 19-Jul-2024 | -0.9402% | -1.7633% | -0.7638% |
| 22-Jul-2024 | -0.5913% | -0.4892% | -0.8657% |
| 23-Jul-2024 | -2.1287% | -6.2274% | +3.4674% |
| 24-Jul-2024 | -1.0235% | -0.6589% | +3.0876% |
| 25-Jul-2024 | +0.1454% | -1.5259% | +4.8373% |
| 26-Jul-2024 | -0.9197% | +0.1482% | +3.7194% |
| 29-Jul-2024 | -0.3745% | +0.6859% | +2.6271% |

This is a documented timing alignment, not causal attribution. Global gold prices, USD/INR, valuation timing and inputs, and ETF supply/demand can also explain the movements. Do not treat the observed July NAV/close divergence as the duty change's measured impact or as an executable premium/discount. Sources: [Ministry of Finance July 2024 customs-duty note](https://www.indiabudget.gov.in/budget2024-25/doc/cen/dojstru1.pdf), [HDFC June-2024 SID](https://files.hdfcfund.com/s3fs-public/SID/2024-06/SID%20-%20HDFC%20Gold%20Exchange%20Traded%20Fund%20dated%20June%2028%2C%202024.pdf).

## Daily trading diagnostics and limits

Across 1,241 NSE rows, the median intraday high-low range is 1.02% of reported daily average price; the 95th percentile is 3.98%. The maximum is 16.70% on 22-Jan-2026 (high ₹143.00, low ₹121.50, close ₹128.97, daily average ₹128.74, 34.36 million units, 80,965 trades). Median absolute close-versus-average difference is 0.1057%.

These are price-variation/activity diagnostics, not quoted spread, market depth, slippage, market impact or executable costs. The 22-Jan range is a serious stress flag; without timestamped quotes it cannot be decomposed into gold repricing, ETF premium/discount movement or order-book cost.

## Cost of historical quote evidence

NSE Data & Analytics' [domestic tariff effective 01-Apr-2026](https://nsearchives.nseindia.com//web/mediaattachment/2026-04/Download_Pricing_file_-_Domestic_clients_20260424122229.pdf) lists Historical Order & Trade Data for Capital Market at ₹12,50,000 per year per single site, before taxes/levies. The [specification](https://nsearchives.nseindia.com/web/mediaattachment/2026-05/NSE_Hist_Order_Trade_Data_1.18_20260518122214.pdf) describes timestamped order-book events and trades. Historical trade-only data is ₹1,10,000 per year per site but does not contain the order book needed for quoted depth. No inquiry or subscription was made. If bought solely for this ETF gate, the order/trade fee would equal about 29.8% of the ₹42 lakh initial capital before tax. Its value across all candidates has not been assessed; no purchase should occur without an investor-approved value case.

First-party methodology/tariff PDFs were reviewed via their URLs on 06-Nov-2026; raw PDF bytes and hashes were not retained in this PR. Tariff is published list pricing, not a negotiated quote.

## Gate disposition

**Qualified:** raw NSE archive and hash; row/date integrity; symbol alias continuity; explicit source-supported NAV denomination adjustment; exact-date descriptive NAV comparison; valuation and mandate regimes; current TER/portfolio snapshots; EOD activity/range diagnostics.

**Still not qualified:** synchronized historical premium/discount; bid/ask depth; slippage or execution cost; user-specific broker access/suitability. Actual ETF close-to-close prices can serve as a historical market-price return series over this captured window; do not substitute close/NAV gaps for trading costs. Keep future execution friction as an uncalibrated sensitivity or exclude the candidate from decision-grade implementation until a defensible lawful execution source exists.

Other G6.3 gates remain open: candidate coverage, direct sovereign-security economics, CPI base-month confirmation, tax/cashflow/uncertainty validation, and the expressly deferred CCIL route. **G6.3 remains OPEN; decision remains NO-GO / NOT YET EVALUATED.**

## Reproduction

From repository root with Python 3 standard library:

```powershell
python research/stage512/2026-11-06/hdfcgold_execution_evidence/normalize_hdfc_gold_etf_nav_units.py `
  --input research/stage512/2026-11-05/source_retrieval_followup/candidates/nav_113049_daily.csv `
  --output-csv research/stage512/2026-11-06/hdfcgold_execution_evidence/nav_113049_current_unit_basis.csv `
  --output-manifest research/stage512/2026-11-06/hdfcgold_execution_evidence/nav_113049_unit_rebase_audit_v1.json

python research/stage512/2026-11-06/hdfcgold_execution_evidence/audit_hdfcgold_nse_amfi_bridge.py `
  --nse-csv research/stage512/2026-11-06/hdfcgold_execution_evidence/hdfcgold_nse_5y.csv `
  --amfi-csv research/stage512/2026-11-05/source_retrieval_followup/candidates/nav_113049_daily.csv `
  --output research/stage512/2026-11-06/hdfcgold_execution_evidence/hdfcgold_nse_amfi_bridge_v2.json
```

The scripts preserve the raw AMFI input and use only the Python standard library. JSON manifests and outputs are generated from the supplied input bytes; source-PDF links are recorded, but PDF byte hashes are not claimed.
