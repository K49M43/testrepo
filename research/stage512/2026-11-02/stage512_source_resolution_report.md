# Stage 5.12 — Actual Source Reconciliation: Controlled Resolution R3

**Decision date:** 2 November 2026  
**Investment gate:** NO-GO (not automatically lifted by improved source integrity)  
**Scope:** ₹42 lakh at inception; ₹25,000/month increasing 10% annually; 2036 internal horizon; ₹90 lakh real after-tax floor / ₹100 lakh real target.

## Executive result

**CPI observation mapping and published-value reconciliation now pass:** The contiguous 165-month *All India Combined General* CPI 2024-base history from January 2013 through September 2026 uses official MoSPI values. The January 2013–December 2024 old-base observations were converted using the published linked-series factor **0.5267**; all 144 linked levels match MoSPI e-Sankhyiki's rendered Back series to the one-decimal precision of the source inputs. For January 2025–September 2026, all 21 direct 2024-base values and the September provisional flag match the September 2026 MoSPI/PIB release, Annexure IV. Reproducible audit scripts and dated transcriptions are in this directory. These captures are transcriptions, not preserved original release/download bytes, so byte-level provenance remains open.

**Market-series identity status (updated 3 November 2026):** Official NSE Nifty 500 TRI monthly anchors, full official AMFI LIC G-Sec ETF NAV history, and an RBI-origin secondary bullion history are now present in the research repository with distinct qualifications. The continuous NSE 8–13 Year G-Sec total-return index history and complete first-party RBI bullion history remain unavailable. These unlike series must not be presented as interchangeable investable returns; earlier forward success frequencies remain conditional calculations, not validated probabilities.

## Official inflation time series constructed

| Metric | Result |
|---|---:|
| Official older CPI records transcribed (2013–24) | 144 months |
| New-basket official CPI (2025–Sep 2026) | 21 months |
| Total contiguous CPI levels | **165 months** |
| CPI level January 2013, converted 2024 base | **55.09282** |
| CPI level December 2024, converted 2024 base | **102.91718** |
| CPI level September 2026, actual 2024 base | **109.49** |
| Annualized CPI growth January 2013–December 2024 | **5.3839%** |

**Audit:** `audit_cpi_linked_series.py` passes continuity, source-label, link-factor, and rate-reproduction checks. `audit_cpi_esankhyiki_back_capture.py` reports 144/144 2013–2024 values matching at source input precision; `audit_cpi_pib_sep2026_annexure_iv.py` reports 21/21 2025–September 2026 direct values and provisional flags matching the release table. The captures' hashes identify our transcription files, not official source bytes. Investor base-month alignment also remains unresolved.

Sources:
- MoSPI December 2025 original monthly table: https://cpi.mospi.gov.in/PDFile/Press/PR%20December%202025.pdf#page=10
- MoSPI 2024-base linkage: https://mospi.gov.in/uploads/documents/documents/1770891066052-Annexure_V.pdf#page=5
- MoSPI 2024 series official page: https://esankhyiki.mospi.gov.in/macroindicators?product=cpi
- Previously validated September 2026 official CPI snapshot: https://www.pib.gov.in/PressReleasePage.aspx?PRID=2322244&lang=1&reg=3

### Why the old CPI proxy is not acceptable

A same-month check of 144 observations (2013–2024) against the previous publicly hosted third-party CPI dataset found:

| Metric | MoSPI original linked series | Prior compilation |
|---|---:|---:|
| 2013–2024 annualized CPI rate | 5.384% | 5.406% |
| Standard deviation of monthly log inflation | 0.669 percentage point | 0.692 percentage point |
| Mean absolute difference in corresponding monthly log inflation | \- | **0.278 percentage point** |
| Maximum identified monthly difference | \- | **2.44 percentage points** (July 2018) |

**Interpretation:** The older compilation's multi-year inflation growth happened to be close to official series, but some individual monthly changes were materially different. That can distort correlations, volatility, inflation-tail testing and simulation month of 'lock-on-hit' events. The old proxy is now **REJECTED** for future CPI covariance calculations. The historical goal replays relying on it are quarantined; old success counts should not be reported as validated real-world probabilities. This comparison is between the *growth rates*, not arbitrary raw levels of differently scaled indexes.

Prior CPI source for controlled comparison: https://github.com/aswinv90/indian-market-historical-data/blob/main/data/MACRO/cpi_inflation.csv

## Market-series identity and current qualification

| Series identity | Observed type and scope | Current qualification | Remaining limit |
|---|---|---|---|
| CPI All India Combined General | Monthly price index; 2012-base 144 observations linked by 0.5267, then 21 direct 2024-base observations; Jan 2013–Sep 2026 | **PASS — provisional source-qualified deflator.** All 144 linked levels match MoSPI e-Sankhyiki at the old-base published input precision; all 21 direct levels and September provisional flag match the MoSPI/PIB September 2026 Annexure IV. See the two dated capture audits above. | Actual investor cashflow/base month is unknown; no final real-wealth output. Captures are transcriptions rather than preserved release/response bytes. |
| Nifty 500 | Gross total-return index (TRI), not price index; 129 monthly observations Jan 2015–Sep 2025 | **PASS — 129 official monthly published anchors.** Monthly figures were transcribed from NSE's 2025 whitepaper and independently reconciled to a protected daily mirror. | Not a complete official daily history; daily month-end date bridge uses independently cross-checked mirror data. |
| LIC MF Nifty 8–13 yr G-Sec ETF (scheme 133307; ISIN INF767K01MV5) | Fund NAV, not exchange-traded market price and not the NSE G-Sec index; 2,867 AMFI daily observations, 26 Dec 2014–30 Oct 2026 | **PASS — official AMFI NAV research history.** Full source segments, manifest, independent audit, and published factsheet anchors are recorded under `research/stage512/data/r9_lic_gsec_etf/`. | ETF NAV is a rolling sovereign-duration proxy; not a direct bond, not a benchmark TRI, and not tradable ETF price. Fees/tax/market spread and investor instrument are separate. |
| Mumbai gold and silver reference | Monthly-average bullion spot reference; gold INR/10 g and silver INR/kg; 437 observations Apr 1990–Aug 2026 | **PARTIAL — secondary mirror integrity plus seven RBI-published anchor months.** | Complete first-party RBI extraction and anchor validation remain open; not ETF or investable-product return history. |
| NSE Nifty 8–13 Year G-Sec index | Official index factsheet identifies total-return methodology; selected factsheet return windows only | **NOT QUALIFIED as a continuous monthly return series.** | Do not substitute LIC ETF NAV or clean-price G-Sec index observations for this total-return history. |

Primary-source endpoints:
- NSE: https://www.niftyindices.com/reports/historical-data
- RBI DBIE curated: https://dbie.rbihub.in/tables?table=real_sector.r17_monthly_average_price_of_gold_and_silver_in_mumbai
- RBI DBIE documented public data API: https://dev.dbie.rbihub.in/docs/using-the-site
- AMFI: https://www.amfiindia.com/net-asset-value/nav-download

## Engineering gate tested

The artifact `stage512_import_gate.py` expects an explicitly attributed monthly level for each of the relevant assets. It rejects missing sources, mixed price and total returns, non-primary source claims, missing months, duplicate months, mismatched fund metadata or invented pre-inception fund history. **Running with no authoritative market files exits with code 2 / `REJECT`**, as demonstrated in the supplied JSON log. Passing structural schema alone does not authenticate website bytes or validate forecasting performance.

For an actual fund NAV, the gate evaluates observed fund history from inception, allowing a shorter NAV record than the underlying benchmark (silver ETFs, for example, did not exist across the entire benchmark span). Never backfill a fund's pre-launch returns with synthetic values. NAVs already net out fund TER; no second TER subtraction.

## What is and is not resolved

- **Resolved to research-use standard:** CPI observations and series types are mapped; 2013–2026 official published observations reconcile as described above. Official Nifty 500 monthly TRI anchors and complete official LIC ETF NAV history are available with scope limits recorded. A provisional deflator may be used for nominal-to-real fixture calculations only after its CPI base month is stated.
- **Not resolved:** Actual investor cashflow/base dates and selected security identifiers; full continuous NSE G-Sec TRI; first-party complete RBI bullion history; scheme-level transaction costs and personal tax facts; independent ten-year probability inference. Do not relabel the mixed-source panel as a fully official investable covariance panel.
- **Unchanged:** The model's hypothetical 6% planning inflation; this is a scenario input, not the mean rate of the historical CPI series. ₹90 lakh floor at 85% modeling confidence is not a contractual CPI-linked payout guarantee.

**Next gate for the after-tax ledger:** confirm which actual instruments and transaction dates belong in the model before treating any reference series as an investable holding. Preserve the recorded distinction between official TRI anchors, fund NAV, secondary bullion reference, and direct G-Sec benchmark. Use the provisional CPI series only with an explicitly stated measurement month; keep real-wealth claims open until the investor's dates are aligned.
