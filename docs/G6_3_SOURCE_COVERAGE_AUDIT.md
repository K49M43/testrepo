# G6.3 WP1 â€” Source coverage and candidate inventory

**As of:** 2026-11-06  
**Disposition:** `PASS_SOURCE_INVENTORY_ONLY`; G6 decision-grade remains `NOT_READY`; investment authorization remains `NO_GO`.

## Scope and method

This increment reconciles source identity, retained raw bytes, normalized histories, candidate dispositions, date overlap, and external source leads. It does not estimate portfolio outcomes or probability. The reproducible entry point is `decision/audit_g6_3_source_inventory.py`; the frozen record is `research/stage512/2026-11-06/g6_3/source_inventory_v1.json`.

The audit re-hashes the 92 immutable source/evidence assets listed in the G5.4 source-reacquisition manifest; reconciles five AMFI scheme NAV histories and their date bounds; checks the official monthly NSE Nifty 500 TRI anchor coverage; reconstructs the retained R9 LIC scheme 133307 NAV series from all 24 AMFI raw segments; verifies normalized daily/monthly outputs and factsheet CAGR checks; and intersects month-end returns only where all listed candidate histories overlap. The manifest also lists two generated audit JSON reports. Their upstream writers use platform-native newlines, so this audit excludes their bytes from source hashing and instead verifies their regenerated semantic PASS/NO-GO fields. No data are downloaded or silently filled by this audit.

## Reproduced coverage

| Evidence set | Reproduced result | Interpretation |
|---|---:|---|
| G5.4 manifest | 94 entries: 92 immutable source/evidence assets totaling 22,452,710 bytes, plus two regenerated audit reports; 0 missing and 0 immutable-source hash/byte mismatches | Raw/evidence bytes match their manifest. The reports are semantically revalidated after regeneration because their Windows/Linux newline bytes differ. This verifies integrity, not each source's investment suitability. |
| Continuous G5 candidate NAV series | Five series; 7,353 observations total | Official AMFI scheme NAVs. NAVs are not ETF traded prices. Coverage begins between 2015 and 2024 depending on product. |
| LIC 8â€“13 Yr G-Sec scheme (AMFI code 133307) | 24/24 raw segments; 2,867 daily NAV observations from 2014-12-26 to 2026-10-30; 142 monthly returns; maximum observed date gap 12 days or less | Reproduces a long official fund-NAV history. It is a fund proxy, not ETF market price, a G-Sec total-return index, or direct sovereign-bond cashflow. |
| LIC normalized outputs | Daily and monthly CSV hashes and rows exactly reconcile to raw segments | Reproducibility of this source transformation only. |
| LIC factsheet anchors | 1/3/5-year CAGR differences remain below the predeclared 0.14 percentage-point tolerance | A bounded cross-check, not proof that every NAV is correct. |
| NSE Nifty 500 TRI | 129 monthly anchors, 2015-01 through 2025-09 | Monthly anchors are not a daily total-return path. |
| Candidate universe | Ten product hypotheses retain explicit dispositions and open evidence gates | Meets the screen-count inventory only; it does not mean ten candidates are fully eligible or comparable. |

The five G5 normalized NAV series are Motilal Nifty 500 Index Fund, SBI Gilt June 2036 Fund, HDFC Gold ETF, ICICI Silver ETF, and SBI Nifty 500 Index Fund. Their observation counts, exact date ranges, maximum gaps and source classifications are captured in the machine-readable record.

## Joint-history constraint

| Common calendar-month label set | Shared month labels | Dates | What it permits |
|---|---:|---|---|
| Motilal Nifty 500 Index Fund + LIC G-Sec ETF + HDFC Gold ETF + ICICI Silver ETF | 57 | 2022-02 to 2026-10 | Descriptive recent co-movement only. |
| Motilal Nifty 500 Index Fund + SBI Gilt June 2036 Fund + HDFC Gold ETF + ICICI Silver ETF | 48 | 2022-11 to 2026-10 | Descriptive recent co-movement only. |
| Previous mix plus SBI Nifty 500 Index Fund | 24 | 2024-11 to 2026-10 | Too short for decision-grade long-horizon tail estimation. |

These are calendar-month label intersections only. The inventory code does not require each series actual observation date at either endpoint to match another series, so these counts are not strict date-aligned return intervals and must not be used for covariance or joint-return statistics. They are overlapping months, not independent annual outcomes; they are not a calibrated distribution of future 2036 results. Product return coverage is uneven and mostly shorter than the target horizon. The official Nifty TRI has only 44 common month labels with the silver series, so extending history by splicing indexes, funds or proxies would change the return-generating process and is not accepted here.

## Candidate disposition and unresolved source gates

The ten candidate hypotheses and their detailed statuses are embedded in `source_inventory_v1.json`; the controlling G5 dispositions remain in `g5_candidate_disposition_v1.json`. Several identities have continuous NAV histories, but the quantitative candidate set is not yet implementation-ready.

- **ETF execution:** official NAV histories and holdings do not establish exchange traded prices, bid/ask spreads, premium/discount, depth, settlement, current availability or investor access through the stated platform.
- **Direct GoI bonds:** a bond must be modeled by dated dirty price/accrued interest, coupon cashflows, reinvestment, maturity and executable availability. The retained 7.18% security `IN0020230085` matures 2033-08-14, before the 2036 objective, so it cannot be represented as a 2036 held-to-maturity position without a reinvestment policy and replacement evidence.
- **91-day Treasury bills:** the official RBI Table 218 page exposes 50 auction records through 2026-06-24, including cut-off prices/yields and allotment quantities. The XLSX/PDF download URLs returned HTML interstitials in this environment, so raw bytes were not accepted as data. RBI says retail noncompetitive allotment is at the weighted average of successful competitive bids; its FAQ explains that this equals cutoff only for a uniform-price auction. Table 218 omits auction method and weighted-average price. A later RBI 4 Nov 2026 notice/result pair shows an official route for those fields (multiple-price method; 91-day weighted-average price 98.5535), but it postdates this table’s window and raw bytes are not hash-retained. The historical retail-executable path therefore remains unqualified.
- **CCIL historical trades and marks:** the public MTM archive distinguishes traded prices from CCIL model marks for securities without qualifying trades. Historical trade access and redistribution terms remain unresolved; no sign-in, restricted dataset or permission request was used.
- **Inflation:** official CPI source qualification now passes for 165 all-India combined CPI-General observations (Jan 2013–Sep 2026); 144 linked back-series observations qualify directly from the MoSPI API. The prior factor-based numerical cross-check is withdrawn because its legacy source observations were not retained in the hash manifest. All 21 current values now match the parsed PIB monthly table, manifest-listed comparison capture, and direct MoSPI API. September 2026 remains provisional. The investor-selected 2026 purchasing-power base month is still open; 6% remains a scenario, not a forecast.
- **Instrument economics and personal suitability:** taxes by event/lot, current TER and other fees, ETF spreads, distributions/coupons, loss treatment, investor dates, tax facts, drawdown tolerance and product access remain WP2 / investor-confirmation gates.

## Official-source leads retained for bounded follow-up

These are leads only; this WP did not acquire or normalize new data from them.

- RBI, [Handbook of Statistics on the Indian Economy](https://www.rbi.org.in/Scripts/AnnualPublications.aspx?head=Handbook%20of%20Statistics%20on%20Indian%20Economy), including Table 218 for 91-day Treasury-bill auctions.
- RBI, [Government Securities: FAQs](https://m.rbi.org.in/commonman/english/scripts/FAQs.aspx?Id=711), for retail/noncompetitive bidding mechanics that must be reflected when constructing an executable price path.
- CCIL, [MTM Prices](https://www.ccilindia.com/mtm-prices), with traded-price versus model-mark provenance retained as a required distinction.
- CCIL, [Historical G-Sec Trades](https://www.ccilindia.com/g-sec-historical-trades) and [Data Sharing Policy](https://www.ccilindia.com/documents/d/ccil/CCIL_DATASHARING_POLICY_OCT24); access and redistribution rights must be resolved before relying on or publishing restricted evidence.

## Acceptance result and next dependency

**WP1 source-inventory subtask passes** because all retained source hashes and transformations audited here reconcile, the ten hypotheses remain dispositioned, joint-history limits are explicit, and blocked evidence is not promoted. The CPI historical series/source gate now passes, but its investor-selected purchasing-power base month remains unconfirmed. **WP1 as a whole does not pass.** ETF execution inputs, direct sovereign-bond economics, retail T-bill rollover prices, and sufficient validated joint histories remain unqualified.

Next: (1) obtain hashable RBI Table 218 and per-auction notice/full-result evidence through official routes (the later single-sample route probe is in `research/stage512/2026-11-06/g6_3/rbi_tbill_result_route_probe_v1.json`); (2) qualify lawful direct-GoI bond price/cashflow evidence with reinvestment rules; (3) source ETF traded-price, spread/premium and cost evidence for candidates retained after screening; (4) obtain investor confirmation of the 2026 CPI purchasing-power base month. The linked/current CPI data are now source-qualified. Do not start a probability model on short calendar-month overlaps. Any sensitivity using them must be explicitly descriptive and must not be presented as 2036 success odds.

## Reproduction

Run from repository root with Python 3.13:

```powershell
python research/stage512/2026-11-05/g5_4/audit_g5_4.py
python research/stage512/2026-11-05/g5_4/audit_g5_candidate_nav_history.py --check
python research/stage512/2026-11-05/g5_4/audit_g5_exit_acceptance.py --check
python research/stage512/pipelines/r9_lic_gsec_official_amfi_history.py
python decision/audit_g6_3_source_inventory.py --check
python decision/audit_g6_3_cpi_qualification.py --check
```

The G6.3 checker reconstructs the inventory and requires byte-identical JSON. The artifact records the audit version and source evidence; no random seed is used because this is a deterministic source-validation task.


## WP1 addendum — CPI and sovereign source qualification (2026-11-06)

The exact evidence, source URLs, retrieval metadata, SHA-256 hashes, normalized CPI file and deterministic checker are in `research/stage512/2026-11-06/g6_3/`; see [`G6_3_CPI_AND_SOVEREIGN_SOURCE_QUALIFICATION.md`](G6_3_CPI_AND_SOVEREIGN_SOURCE_QUALIFICATION.md). `decision/audit_g6_3_cpi_qualification.py --check` reproduces the CPI qualification.

The CPI checker has since been strengthened: it parses the PIB monthly table and validates the archived comparison capture; the old-base staged CSV is explicitly excluded from independent validation. This closes the historical CPI source-data gate only. It does not select an investor purchasing-power anchor, forecast future inflation, or make an investor-specific real-wealth output available. The RBI table identity/contents are verified on the official page, but raw machine-readable table bytes, row-level auction method, and a complete retail NCB price path are not. Direct dated GoI security total-return evidence remains separate from T-bills and from government-security fund NAVs. **Issue #44 was initially closed by PR #48 and is now reopened after the independent audit identified an incomplete fallback evidence ledger. G6.3 remains incomplete; WP1 as a whole is not complete.**
## Post-audit evidence update — 2026-11-06

The official RBI T-bill source lead is partially acquired since this source-coverage snapshot: the public archive month form was verified for November 2025, and one linked Full Auction Result was retained with exact bytes/hash and 91/182/364-day prices/yields. This proves a reproducible source route, not a long-run rolling strategy series. All other coverage conclusions in this audit remain unchanged; no joint covariance or tail-probability use is qualified. See `G6_3_CPI_AND_SOVEREIGN_SOURCE_QUALIFICATION.md` and the manifest under `source_raw/rbi_tbill_sample/`.

## Historical pair cross-check — 2026-11-06

The RBI T-bill evidence now includes one matched 26-Nov-2025 auction notice/full result/cut-off result and Table 218 reconciliation. Source hashes, paired dates, auction method, weighted-average price/yield, rounded Table 218 price and exact cutoff yield are verified by the G6.3 source capture audit. This remains a single descriptive auction sample; no long-run sovereign return series or joint risk use is qualified.

## Direct GoI 2036 security update — 2026-11-07

The official October 2026 specific reissue notice and RBI full auction result for 6.94% GS 2036 (`IN0020260025`) are now retained with byte counts and SHA-256 hashes in `research/g6_3/direct_gsec_2036/2026-10-16/`. The notice fixes accrued interest as due through 18-Oct-2026 for 19-Oct settlement. The 157-day 30/360 calculation produces ₹3.026611 accrued interest per ₹100 face and ₹9,995.66 clean-plus-accrued consideration per minimum ₹10,000 face lot at the historical ₹96.93 weighted-average clean price, before charges. This remains conditional because RBI FAQ Q22's example conflicts by one day with its explicit Q25 convention; exact settlement rounding/collection is not evidenced. A nominal 20-event coupon/redemption schedule is included, with holiday-adjusted dates unresolved.

The new `decision/audit_g6_3_direct_gsec_2036.py` checks both official source hashes, the auction/security/cutoff match, the conditional arithmetic and nominal cashflow schedule. No security-specific secondary-price series, retail spread/depth, executable entry/exit, coupon reinvestment, tax, or investor-specific return is qualified. The exact bond was issued in 2026 and cannot provide a decade of instrument-specific history. AMFI's transaction table may be researched only after rights permit the intended repository retention and publication; its current terms do not authorize us to retain/publish its transaction data here without written permission.

This update closes the October notice/result capture subtask only. Direct-sovereign economics and the G6.3/WP1 source gates remain open; investment authorization remains NO-GO / NOT YET EVALUATED.
## Historical sovereign-yield proxy source captured — 2026-11-07

The official RBI DBIE report “Month-end Yield of SGL Transactions in Government Dated Securities for Various Maturities” was exported from the RBI DBIE interface to an XLSX workbook. The local capture is 74,921 bytes with SHA-256 `3C9C5C851CD233961967524FE03408C228D74E819B5916D10C9386DB561A2F4F`. It remains in the investor's local Downloads folder; the raw workbook is not committed to this public repository while data-reuse and redistribution terms are being checked.

A deterministic structural inspection found one sheet (`New Format`), 30 term-to-maturity columns (1 through 30 years), units of percent per annum, and 367 distinct monthly labels with no duplicate or skipped calendar month from April 1996 through October 2026. Of 11,010 maturity-month cells, 9,537 are numeric and 1,473 are explicit `-` missing markers. Missing values are concentrated in longer residual-maturity buckets and increase toward older dates. They are preserved as missing; no interpolation or carry-forward is allowed. The source file's workbook row count includes headers and footer and is not the observation count.

A sample reconciliation against RBI Handbook Table 178 for March 2024 passed at the handbook's four-decimal display precision: 1-year 7.144065 → 7.1441; 5-year 7.045748 → 7.0457; 10-year 7.066724 → 7.0667; and 30-year 7.116281 → 7.1163 percent per annum. This is a bounded cross-check of four cells, not a full row-by-row or vintage reconciliation. See the [RBI Handbook Table 178](https://rbi.org.in/Scripts/PublicationsView.aspx?id=24003).

**Coverage discrepancy remains open:** while navigating the current DBIE catalog, its metadata displayed a start date of 20-Aug-2021 and end date of 31-Oct-2026; the exported report itself contains monthly rows back to April 1996. RBI's [DBIE brochure](https://dbieold.rbi.org.in/DBIE/doc/Brochure%20on%20DBIE%20-2022%20English.pdf) describes the series as available since April 1996, which supports the longer history, but does not explain why the current catalog metadata starts in 2021. The exact report/table lineage, vintage/revision behavior, and catalog discrepancy need a documented reconciliation before treating the full 1996–2026 panel as a qualified statistical series.

**Use boundary:** this is a long-run sovereign-yield regime proxy that may help define early-exit rate-stress scenarios. It is not the 6.94% GS 2036's own price or total-return history, not a zero-coupon curve, and not executable retail bids, spreads, depth, or investor-specific fills. Month-end average yields for whole-year residual-maturity buckets cannot be converted directly into the return of a particular bond or portfolio without a separately specified security/portfolio construction, cashflow repricing, coupon reinvestment, and validation method. Keep it distinct from observed security trades, fair-value marks, ETF NAVs, and direct-bond cashflows.

**Qualification status:** raw source bytes captured and hashed locally; structure, monthly continuity, missingness, and four published sample cells audited. Full-history statistical use remains **NOT QUALIFIED** pending DBIE metadata/lineage reconciliation, permitted-retention determination, broader cross-vintage/value reconciliation, and a prespecified method for any use in rate-stress analysis. No yield-history return or early-exit return calculation is qualified by this capture. The exact security was first issued on 11-May-2026 and cannot supply a decade of its own realized price history.

This source capture narrows the lawful search for a historical rate proxy; it does not close the direct-bond price, retail execution, coupon reinvestment, tax, joint-risk, or G6.3/WP1 gates. Investment authorization remains **NO-GO**.
