# R9.3 live AMFI backfill and risk bridge audit

**Audit date:** 2 November 2026. **Scope:** LIC MF Nifty 8–13 yr G-Sec ETF AMFI scheme 133307 / ISIN INF767K01MV5. **Investment authorization remains NO-GO.**

## Executed

- Refreshed `origin/main`; checked out branch was `main`, clean before execution, at `7930124` (`docs(codex): point copy-ready task to tracked investment decision GitHub issue #3`).
- Inspected the live source manifest, R9.3 parser, incident record, 24-window workflow, and recent GitHub Actions. The current committed full-history manifest still showed the earlier failure (zero accepted rows); the R9.3 four-test CI run passed, which covered parser behavior only. Several preceding live backfill runs failed.
- Ran the corrected pipeline once. It made sequential bounded requests to AMFI, persisted each byte-exact response, and stopped on a 429 if encountered. This run received all 24 requested periods without a rate-limit failure.
- Independently recomputed every raw segment SHA256 and byte count, parsed the original response bytes, checked API query scheme ID, exact LIC scheme/group names, record totals and option values, reconstructed every daily NAV, and recomputed each monthly return. The reproducible checker is `research/stage512/pipelines/audit_r9_live_backfill.py`; output is `research/stage512/data/r9_lic_gsec_etf/r93_independent_artifact_audit.json`.
- Ran the existing 129-month equity / gilt ETF bridge after the full NAV gate passed.
- Preserved the earlier zero-row unqualified partial CSV as historical failure evidence. On complete acquisition the pipeline writes canonical daily/monthly datasets without replacing that partial artifact with a complete copy under an `UNQUALIFIED` filename.

## Source and integrity results

| Check | Result |
|---|---:|
| AMFI six-month source segments | 24 / 24 accepted |
| Archived original response bodies | 24; hashes and byte sizes reproduced |
| Reconstructed priced NAV observations | 2,867, 26 Dec 2014–30 Oct 2026 |
| Sum of source-segment record counts | 2,867; equals daily CSV row count |
| Maximum consecutive priced-date gap | 6 calendar days |
| Daily NAV move range | −2.0991% to +2.0517%; no split-sized discontinuity under the configured screen |
| LIC March 2026 factsheet CAGR arithmetic | 1y difference 0.0047 pp; 3y 0.0080 pp; 5y 0.0054 pp |
| Monthly NAV return intervals | 142, Jan 2015–Oct 2026 |
| Annualized sample volatility of monthly log NAV returns | 3.82768% |

`Option` was null or absent for some API records. Those records were treated as unspecified; every explicit value was growth-compatible. The acquisition parser rejects explicit non-growth options. The original R9.3 four regression tests were recorded PASS in GitHub Actions (4/4). An initial sandboxed local rerun was blocked before assertions because fixture temporary directories were inaccessible; rerunning the same suite with temporary-fixture access passed **4/4**.

The first branch bridge workflow failed while the R9 qualification workflow was rewriting source CSVs on Linux. The Windows commit's manifest hashes had been computed over CRLF working bytes, but Git's default text normalization stored LF blobs, so the bridge's byte-hash check correctly rejected that checkout. The R9 workflow then refreshed the manifest from the committed cached source. To prevent repeat divergence, `.gitattributes` now disables line-ending conversion for every file under the R9 evidence directory. The independent audit and bridge were rerun against the refreshed manifest and both passed locally; the pushed follow-up bridge workflow will confirm the byte-stable commit.

## Strict 129-month return bridge

The pre-existing script passed its full 129-month label checks for Jan 2015–Sep 2025. It compared both dates that define each return interval, using AMFI daily NAV month ends and an independently cross-checked NSE daily mirror for index dates. Only 117/129 intervals had both month-end dates equal. The other 12 are excluded from the strict statistic.

- Strict sample correlation, official NSE Nifty 500 gross TRI vs LIC ETF NAV: **0.022541**.
- Strict annualized monthly log-return volatility: **17.02981% equity**, **3.72678% LIC ETF NAV**.
- For context, the unfiltered 129 month-label series gives correlation **−0.020016** and volatility **16.94893% / 3.84506%**. Those unfiltered figures are not the accepted aligned sample.
- In the separate common recent 36-month window (Nov 2023–Oct 2026), LIC ETF NAV volatility is **3.00403%**, compared with **3.65747%** for the HDFC Gilt Fund in R7. These are different funds and only descriptive, backward-looking volatility estimates.

This bridge does **not** qualify the NSE 8–13 Year G-Sec index's own total-return history. The comparison is a rolling LIC ETF NAV proxy and is distinct from a direct GoI bond held to 2036. The index month-end evidence uses a third-party daily mirror (independently cross-checked), not a complete first-party NSE daily export. 117 monthly observations do not establish a stable forward correlation; the sample mean is not a forecast. NAV already reflects fund expenses. Exchange ETF prices, premiums/discounts, tax, inflation, sequence risk and the real 2036 target remain outside this source gate.

The independent file-level validator's “corporate action” screen is limited to detecting split-sized daily NAV jumps. It is not a separately sourced full corporate-action event ledger. The three LIC factsheet CAGR checks provide independent published return anchors but do not prove every daily history point.

## Decision and next work

R9 full AMFI history and the strict ETF-proxy risk bridge now pass within their stated research scopes. No investment gate changes to GO. The source and bridge do not provide a verified direct sovereign or official G-Sec index return series, an after-tax real-wealth forecast, or execution-ready suitability evidence. Continue with independent audit of cashflow/tax/inflation accounting and candidate instruments; preserve the existing NO-GO until the decision gates and independent challenge pass.

**Rerun:**

```powershell
python research/stage512/pipelines/r9_lic_gsec_official_amfi_history.py
python research/stage512/pipelines/audit_r9_live_backfill.py
python research/stage512/pipelines/r9_nifty500_gsec_instrument_bridge.py
```
