# G5.3 — Independent candidate evidence audit and G5 disposition

**As of 2026-11-05 · Audited G5.2 subject: PR #36 at 85e0157a964164f8423e2eda4bcc3635fecdcc44 · Investment authorization: NO-GO**

## Disposition

**G5.3 audit: PASS for the bounded checks below, with one material fee-basis correction made and independently reproduced.** The G5.2 evidence increment is not a complete investment-universe screen. **Overall G5 disposition remains BLOCKED / INSUFFICIENT_EVIDENCE.** The register contains 8 candidate hypotheses; the mandate requires at least 10 serious candidate securities or strategies before narrowing. Official source-response bytes needed for independent re-parsing of the sampled metal NAV and AMFI TER exports are also missing. G6 and any investment recommendation remain blocked.

The G5.3 audit does not treat G5.2's own audit PASS as evidence. It re-reads the retained first-party holdings workbooks and factsheets, independently recalculates equity coverage and overlap, traces fee rows to the retained AMFI normalized export, and verifies the G5.1 correction lineage and negative cases using a separate audit program.

## Material finding corrected — Motilal Total TER

The G5.2 draft used September AMC workbook figures of 0.18% for the ETF and 0.13% / 0.79% for the Index Fund as its latest TER values. The October 2026 AMFI export shows those figures match the BER fields, while its separately published Total TER includes brokerage and statutory levies. The earlier candidate register had not reconciled the source and date basis. Using those values as current all-in costs would understate the October AMFI Total TER.

| Instrument | Earlier September AMC figure | AMFI Total TER, 30 Oct 2026 | Reconciliation |
|---|---:|---:|---|
| Motilal Oswal Nifty 500 ETF, AMFI Regular Plan row | 0.18% | **0.39%** | 0.18% BER + 0.02% brokerage + 0.00% transaction cost + 0.19% statutory levies |
| Motilal Oswal Nifty 500 Index Fund, Direct | 0.13% | **0.23%** | 0.13% BER + 0.02% brokerage + 0.00% transaction cost + 0.08% statutory levies |
| Motilal Oswal Nifty 500 Index Fund, Regular | 0.79% | **0.97%** | 0.79% BER + 0.02% brokerage + 0.00% transaction cost + 0.16% statutory levies |

The register and human report now use the dated AMFI Total TER values. The September source values remain preserved in the holdings evidence as the figures reported in that workbook; the audit does not silently rewrite that historical source. The original AMFI XLSX bytes were not retained, so the audit reproduces the component arithmetic from AMFI's committed normalized export and checks the export diagnostic/hash, but cannot re-parse the original workbook.

The independent audit explicitly recomputes the Index Fund Direct-plan total as 0.13% BER + 0.02% brokerage + 0.00% transaction cost + 0.08% statutory levies = 0.23%, using the Direct-plan columns in the retained normalized AMFI export. It separately checks that these source values map to the dated scheme row in the candidate evidence; the mapping file's precomputed arithmetic flag is not used as the proof of the sum.

## Independently reproduced evidence

### Equity holdings and overlap

The September 2026 Motilal AMC workbooks were independently read from the retained XLSX bytes. Each product has 498 unique equity ISINs; 497 rows carry numeric displayed weights and MMTC's suppressed weight remains unknown. The ETF's displayed equity weights sum to 99.68%; the Index Fund's sum to 99.74%. Top-10 equity weights reproduce to 28.49% and 28.52%. Exact-ISIN matched-date overlap independently reproduces as **99.68%** using Σ min(ETF weightᵢ, Index Fund weightᵢ) over 497 numeric matched ISINs. This is approximate overlap on rounded weights, not return correlation.

The Index Fund also holds 0.28% Triparty Repo and −0.02% net receivables; the ETF has 0.32% net receivables. These residuals are visible and not converted into equity or zero-weight securities. Source and normalized holdings hashes matched the record.

### Bond and metal identity / holdings

- The September LIC factsheet identifies LIC MF Nifty 8–13 Year G-Sec ETF, NSE code LICNETFGSC, allotment 24 December 2014, and Nifty 8–13 Year G-Sec Index as benchmark. The dated portfolio reports 99.50% sovereign holdings and 0.50% cash/other. The three sovereign rows have no ISIN in the source; none was inferred. The product remains a changing-duration ETF proxy, not direct sovereign cashflows.
- The March ICICI factsheet identifies gold as NSE GOLDIETF / ISIN INF109KC1NT3, allotment 24 August 2010; silver as NSE SILVERIETF / ISIN INF109KC1Y56, allotment 24 January 2022. Their March holdings snapshots re-extract to 98.21% gold and 99.08% silver, with the stated cash/debt residuals. Those holdings are 219 days old as of the register date and cannot represent current exposure.
- The [Motilal Nifty 500 ETF page](https://www.motilaloswalmf.com/mutual-funds/motilal-oswal-nifty-500-etf) and [Nifty 500 Index Fund page](https://www.motilaloswalmf.com/mutual-funds/motilal-oswal-nifty-500-index-fund), reviewed on 5 November, report the ETF's ISIN, AMFI code, CMT code and 29 September 2023 allotment, and the Index Fund's Direct Growth ISIN, AMFI code, CMT code and 6 September 2019 allotment. The official product pages are dynamic and were not archived or hashed in the repository; that limits later byte-level reproduction. Current Groww access, listing/trading status and investor suitability remain blocked in the register.

### AMFI samples and provenance limits

The two metal schemes each have the nine recorded dates: 2–5 January 2024, 19/21/22/23 October 2026, and 30 October 2026. The independent check matched each row's source hash/window to the committed AMFI manifest and confirmed the register says the samples are non-contiguous. No full metal NAV history or pre-inception proxy splice is qualified.

The original [AMFI NAV history](https://www.amfiindia.com/nav-history-download) response bodies for these sample windows are absent from the repository. Consequently the source URL, retrieval time, byte count and hash are internally linked, but the audit cannot hash the original bodies or independently parse the raw responses back into the nine observations. The original [AMFI TER export](https://www.amfiindia.com/ter-of-mf-schemes) XLSX is similarly absent. These are reproducibility gaps, not proof the retained normalized rows are wrong. Restore the raw artifacts or perform a fresh bounded official retrieval and preserve the bytes before using these series in a return calculation.

### G5.1 — former 11.8% replay lineage

The lineage map's 14 current artifact fingerprints were independently recomputed. The active scenario code assigns 0.118 as a fixed geometric-return assumption and creates synthetic shocks; it does not replay an observed Nifty 500 return path. All six dependent rows (three illustrative allocations × 120/122-month horizons) carry the corrected synthetic label, unverified input provenance, explicit lineage link and `QUARANTINED_NOT_FOR_INVESTMENT_DECISION` status. The committed rows match the preserved G5.1 rerun exactly. The blocker report and assumption register also carry the corrected wording and a visible correction notice.

The exact 11.8% input remains unverified: its original third-party source snapshot and endpoint were not preserved. The official NSE whitepaper's since-1995 TRI figure has a different endpoint and does not validate the exact 0.118 input. The six synthetic outputs remain unsuitable for ranking or decision probabilities.

## Negative-case results

The independent audit rejects all five mutated cases:

1. Investor platform/access unknown promoted to verified.
2. Nifty 500 TRI benchmark reclassified as an investable product.
3. Metal NAV observation moved to a date before product allotment.
4. Source artifact hash mismatch.
5. Candidate return convention removed.

The audit also enforces the distinction between the direct dated GoI security (blocked pending live price/availability evidence) and the LIC ETF (proxy-only), and preserves null holdings identifiers and weights rather than imputing them.

## Open G5 findings and next dependency

1. **Candidate breadth remains incomplete:** 8 hypotheses are present, not the mandate's 10+ serious candidate securities/strategies. Four are labeled actual products, two are proxy-only records, and two remain blocked comparators/security hypotheses; investor-specific access and suitability remain unverified. Do not close parent G5 or begin G6 ranking on this universe.
2. **Raw source retention remains incomplete:** AMFI NAV response bodies and the original TER XLSX must be retained and revalidated before these observations support return or cost calculations. Motilal live product-page metadata also lacks an archived response hash.
3. **Execution/tax evidence remains open:** no current exchange spread/depth, Groww route, investor eligibility/suitability or candidate-specific qualified tax result is established. These are later acceptance gates, not inferred facts.

**G5.3 is complete as an independent audit record once reviewed and merged. Overall G5 remains BLOCKED / INSUFFICIENT_EVIDENCE until the candidate-universe breadth and material provenance gates are resolved or explicitly dispositioned under the gate ledger. G6 remains blocked. Investment authorization remains NO-GO.**

## Reproduction

From repository root, with Python 3.13, `openpyxl==3.1.5`, and `pymupdf==1.28.2`:

```powershell
python decision/audit_g5_3_independent_candidate_evidence.py
python decision/audit_g5_2_candidate_register.py --check
```

The first command imports no G5.2 audit code. It re-extracts the source workbook data independently and includes fail-closed mutation checks. All source paths, dates, and hashes are recorded in the G5.2 register/holdings manifest; AMFI raw-response omissions are explicitly stated above.
