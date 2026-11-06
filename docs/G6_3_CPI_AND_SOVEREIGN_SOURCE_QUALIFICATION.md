# G6.3 WP1 — CPI and sovereign-security source qualification

**As of:** 2026-11-06  
**Scope:** first-party historical CPI source qualification and the currently available RBI T-bill/sovereign source path. This does not close WP1 or G6.3 and does not authorize an investment.

## CPI — historical source gate passes

The qualified series is All India / Combined / CPI (General), base 2024=100:

| Segment | Official source identity | Observations | Coverage | Finding |
|---|---|---:|---|---|
| Linked back series | `Back` | 144 | 2013-01–2024-12 | All 144 observations are directly present in the retained official MoSPI API back-series responses. The 0.5267 factor is retained as methodological context from Annexure V, not asserted as an independently reproduced numeric cross-check: the staged legacy CSV did not retain its underlying historical source bytes in this source manifest. |
| Direct current series | `Current` | 21 | 2025-01–2026-09 | The strengthened checker parses all 21 month rows from the retained PIB release HTML; the parsed values match both the manifest-listed comparison capture and MoSPI API exactly at the source's two-decimal precision. Repeated monthly-table copies in the HTML must agree. |
| **Total** |  | **165** | **2013-01–2026-09** | Contiguous months; no duplicates or missing months. |

The first-party [MoSPI CPI API specification](https://esankhyiki.mospi.gov.in/layout/swagger_user_cpi.yaml) documents the open API and required filters. Original responses are preserved under `research/stage512/2026-11-06/g6_3/source_raw/` with URLs, retrieval times, byte counts and SHA-256 in `cpi_source_manifest_v1.json`. The qualifying executable history is `cpi_mospi_api_combined_general_2013_2026.csv`.

The primary [MoSPI CPI 2024 Annexure V](https://mospi.gov.in/uploads/documents/documents/1770891066052-Annexure_V.pdf) was downloaded as a PDF and independently inspected: page 5 documents the annual-overlap linking method, Combined factor 0.5267 and back-series scope. Its hash is `7720b6404da8508dbf0c99ed56eae066a88bf2b873c2113c121326ffb53d69c4` (273,029 bytes). The first-party [PIB September 2026 CPI release](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2322244&lang=1&reg=3) monthly table is parsed programmatically across Jan 2025–Sep 2026 and cross-checked row-by-row against the retained capture and direct API observation. September 2026 is provisional.

**Precision correction:** the earlier reconstructed CSV displays some historical linked values to five decimal places because it multiplied the old index by 0.5267. That is derived calculation precision, not official CPI source precision. The new normalized series retains the official API values. Do not imply extra historic precision.

**Limits:** this qualifies an observed deflator series, not future inflation. The investor's exact 2026 purchasing-power base month remains unconfirmed. September 2026 is provisional. Real-wealth output tied to a personal base month remains blocked until that investor input is explicit.

Reproduce with:

```powershell
python decision/audit_g6_3_cpi_qualification.py
python decision/audit_g6_3_cpi_qualification.py --check
```

The checker verifies the primary source PDF signature/hash, the PIB September anchor, response identities and pagination, month continuity, no duplicates, the 144 linked values at published precision, exact 21-month current-series values, and byte identity of the normalized CSV and deterministic result JSON.

## Sovereign security — auction source is identified, investment return path remains unqualified

The official [RBI Handbook of Statistics 2025–26 page](https://www.rbi.org.in/Scripts/AnnualPublications.aspx?head=Handbook%20of%20Statistics%20on%20Indian%20Economy) links [Table 218: Auctions of 91-Day Government of India Treasury Bills](https://www.rbi.org.in/Scripts/PublicationsView.aspx?id=24043), published 2026-07-31. The official page displays 50 auction observations from 2025-07-02 through 2026-06-24. It reports auction/issue dates, notified amounts, bids received/accepted, total issue, cut-off price and cut-off implicit yield (actual/365). The 2026-03-25 row reports zero accepted issue and no cutoff price/yield; it cannot be treated as an investment return observation.

The RBI document host returned HTTP 200 but `text/html` bodies for both the advertised XLSX and PDF download URLs. Their signatures were HTML, so they are recorded as failed acquisition metadata and deliberately not retained as table data. The official rendered table page was independently inspected. No interstitial, access control, or site protection was bypassed.

RBI's [Government Securities FAQ](https://m.rbi.org.in/commonman/english/scripts/FAQs.aspx?Id=711) states that retail noncompetitive bids are allotted at the weighted-average price/yield emerging from competitive bidding. The same FAQ explains that a uniform-price auction allots successful bids at the cutoff, while a multiple-price auction allots each competitive bidder at its bid. The cutoff and NCB price are therefore conditionally equal only if that specific auction used uniform-price allocation. Table 218 does not state the auction method or publish the weighted-average successful competitive price. The retained evidence cannot establish which price applies row by row; the historic RBI statement that 91-day T-bills used uniform-price auctions is not enough to qualify 2025–26 auctions.

The RBI FAQ also limits retail NCB to select auctions and describes a 5% allocation cap and a service charge that may be recovered by an aggregator. Those operational details, funding/refund timing, partial allotment, and a continuous sequence of issue/maturity dates all affect an investor-specific rolling path. A cutoff price alone is not a realized investment return.

- Table 218 is authoritative evidence about the displayed auction outcomes, but does not establish an investor's retail NCB execution price without auction-method evidence.
- Cutoff price may equal the NCB weighted-average price under uniform-price allocation; otherwise it must not be substituted. Table 218 alone does not identify the applicable method for its displayed rows.
- Even a qualified auction acquisition price would not by itself establish a rolling 2036 strategy return: issue and maturity cash dates, failed/partial allotments, idle-cash funding, redemption and reinvestment, service costs, investor eligibility, and tax must also be modeled.
- A one-year window of 50 auctions is not a long-history, fully executed 2036 rolling strategy.
- Direct dated GoI bonds require security-specific purchase price, accrued interest, coupon dates and reinvestment, maturity/exit, tax and fees. This table does not provide those inputs.
- Government-security fund NAV, an ETF's exchange price and a direct sovereign holding remain distinct return objects.

The exact source-path disposition and excluded acquisition hashes are in `research/stage512/2026-11-06/g6_3/sovereign_source_access_audit_v1.json`. Lawful next routes are an ordinary official RBI/DBIE download of Table 218, a first-party publication of weighted-average successful prices or actual investor allocation records, and separately licensed/private price evidence for dated bonds. CCIL restricted data will not be redistributed or used without rights.

## Gate result

| Gate | Result |
|---|---|
| CPI source values and published linking factor | **PASS — historical source series only** |
| Investor CPI base month | **OPEN — investor confirmation required** |
| RBI 91-day auction source identity and displayed fields | **PASS — source-page inspection only** |
| Hash-retained RBI XLSX/PDF bytes | **FAIL — endpoint returned HTML, not the requested format** |
| Retail T-bill executable price/return path | **OPEN — auction method/NCB price and full investor cashflow path not established** |
| Direct dated GoI security total-return path | **OPEN — price/cashflow/reinvestment evidence incomplete** |
| WP1 overall / G6.3 | **OPEN / NOT READY** |
| Investment authorization | **NO-GO** |

The source-inventory WP1 subtask remains passed. This update closes the historical CPI source gate and documents the verified RBI acquisition limitation; it does not make WP1 as a whole pass. The independent G6.3 audit found the fallback decision pack lacked a source-by-source evidence status ledger. The remediation is documented in `G6_3_UNAVAILABLE_EVIDENCE_LEDGER.md`; rows marked not acquired remain open evidence work, so G6.3 is still incomplete and issue #44 is reopened.
