# Codex Handoff — State of the Actual 2036 Investment Decision (2 Nov 2026)

**Investor-facing program status: NO-GO / decision not yet supportable.** This is **not** a declaration that any proposed asset is unsuitable; the present evidence is not yet sufficient for an investment-ready ranked decision.

## Post-merge update — 2 November 2026 (PR #4)

P0 Tasks 1–2 are now complete within the limits below. The merged main commit is `8eb9c20`.

- R9 full official AMFI NAV history: **PASS for historical research**, 2,867 observations over 24 six-month source segments from 26 Dec 2014 through 30 Oct 2026; independent segment/hash/artifact audit passed.
- Strict 129-month Nifty 500 TRI versus LIC ETF NAV-proxy bridge: **PASS for the 117 intervals whose current and prior month-end dates both match**; observed correlation 0.022541. Twelve intervals were excluded for date mismatch.
- Actions on source commit `1bdf2c6` passed: full AMFI run `41475006266`, bridge run `41475006330`, offline contract run `41475006356`.
- The LIC ETF remains a rolling-duration fund proxy, not the NSE G-Sec index or a direct 2036-maturity GoI bond. The bridge is historical and does not qualify a forward correlation.
- Next: CPI vintage and base-month reconciliation, then independent tax-lot / after-tax real-wealth accounting. The October 2026 CPI was not yet released as of this update; the latest published reference is September 2026.
- Investment authorization remains **NO-GO**.

The original snapshot below is preserved as historical handoff context; its R9 failure status predates the successful qualification and merge.

## Where to begin
Review `AGENTS.md` and `docs/INVESTMENT_DECISION_MANDATE_2036.md`. The existing `research/stage512/` tree represents an **evidence and computational workstream**, not a reason to keep the investor in research indefinitely. The objective is the actionable 2036 investment decision.

### Verified source and model evidence (scope-limited)
| Evidence | Status and precise meaning | Repository path |
|---|---|---|
| 2036 cashflow/simulation work | Prior conditional models and alternative assumptions exist. Their outcomes are **not validated 2036 real-world probabilities** | `research/stage512/2026-11-02/README.md`, relevant `stage512_*.py` |
| 2026-base linked historical Indian CPI | Reconstructed 165 contiguous CPI monthly observations Jan 2013–Sep 2026; some independent source-vintage review still open | `research/stage512/2026-11-02/stage512_source_resolution_report.md`, `research/stage512/2026-11-02/stage512_cpi_official_linked_2013_2026.csv` |
| Four actual fund NAVs | 3,046 official AMFI NAV prices (equity, gilt, gold ETF, silver ETF), 63 archived official cross-checks. Strict risk matrix uses **36 matched monthly return intervals** Nov 2023–Oct 2026 after quarantining mismatched first month-end | `research/stage512/data/amfi_official_36m/qualification_manifest.json`, `research/stage512/data/official_nav_independent_R7.json`, `research/stage512/data/official_nav_R7_CI_diagnostics.json` |
| Four-fund historic covariance | Strict-date-aligned 65/20/10/5 historic annualized vol about **11.41%**. Only a short-sample descriptive statistic, not a forecast | `research/stage512/2026-11-02/stage512_official_NAV_regime_horizon_R7.md` |
| Nifty500 official TRI | **129 published monthly** Nifty 500 total returns Jan 2015–Sep 2025, compared against SHA1-pinned third-party daily index; all match within 0.0051 percentage point | `research/stage512/data/nse500_official_tri_monthly_2015_2025q3_R8.csv`, `research/stage512/data/nse500_tri_validation_R8.json` |
| RBI-origin gold/silver | 437 consecutive monthly Mumbai **average** gold/silver prices Apr 1990–Aug 2026 from a THIRD-PARTY mirror. Seven official published month pairs (14 individual prices) match; entire mirror not first-party certified | `research/stage512/data/r8_rbi_origin_mirror/normalized_validation.json`, `research/stage512/data/r8_rbi_bullion_primary_spotcheck_manifest.json` |
| Direct official NSE G-Sec total return | NSE index identified, but primary index daily/monthly TR history **not obtained**; clean price must not replace TR | `research/stage512/2026-11-02/stage512_R8_benchmark_source_resolution.md` |
| LIC MF 8–13yr G-Sec ETF factsheets | Scheme 133307 / ISIN INF767K01MV5; 12 independently published LIC ETF vs benchmark 1/3/5-year return points pass arithmetic. These are overlapping tracking-difference snapshots, NOT full index returns | `research/stage512/data/r9_lic_gsec_factsheet_bridge.json` |
| LIC ETF AMFI sampled history | Four short windows (2015/2018/2022/2026) pass; four 6-month windows return **119,121,120,117** priced observations. These are discontinuous samples | `research/stage512/data/r9_lic_gsec_etf/short_window_probe.json`, `research/stage512/data/r9_lic_gsec_etf/medium_window_probe.json` |
| LIC ETF full 2014–2026 backfill | **FAIL_INCOMPLETE**: initial run 0/24 segments accepted due to AMFI `Option=null` false rejection and HTTP 429 rate limiting. Corrected code exists, but a new full-history PASS was **not** confirmed as of handoff | `research/stage512/data/r9_lic_gsec_etf/qualification_manifest.json`, `research/stage512/pipelines/r9_lic_gsec_official_amfi_history.py` |
| R9.3 parser correction | **4 offline regression tests passed** (null option, rejected explicit dividend, 429 fail-closed, cached SHA, segment continuity). This does NOT certify full NAV history | `research/stage512/data/r9_lic_gsec_etf/r93_offline_regression.json` |
| Equity vs bond ETF long risk bridge | `FAIL_NOT_QUALIFIED`, because official full LIC ETF input remains unqualified. Script includes a strict both-end date-alignment filter | `research/stage512/data/r9_nse_gsec_129m_source_bridge.json`, `research/stage512/pipelines/r9_nifty500_gsec_instrument_bridge.py` |

**Status is snapshot-based.** Codex must check latest files, GitHub Actions run results and branch HEAD; new evidence may have arrived after this document was written. Never promote a gate based solely on a planned script or uninspected CI job.

## Exact immediate blockers in priority order
1. **R9 official LIC 2014–2026 NAV backfill:** recheck the current manifest; source code now accepts null Option and rate-limits sequential requests. Evaluate successful raw segment caching, incremental progress, legal access and fail-closed outcomes. Respect 429 and stop; do not brute-force a service.
2. **Independent 129-month return bridge:** after R9 official-history PASS, cross-check equity TRI vs LIC ETF dates, source hashes and factsheet CAGRs; compute bond/equity correlation and sensitivity. Does not magically qualify official NSE bond index total-return levels.
3. **Reference vs investable product:** keep Nifty 8–13 Yr G-Sec index, LIC ETF, HDFC Gilt Fund and direct maturity-matched GoI bonds distinct (different risks, cash flows and taxation). Compare eligible alternatives.
4. **Joint cashflow/tax/inflation model:** validate historical linked CPI, yield and bullion observation timing, fund-vs-benchmark bridges and current tax rules; rerun gross/aftertax/real outcomes.
5. **Actual decision universe and investor-facing memo:** minimum 10 credible security/strategy candidates and a justified shortlist; quantify feasible 2036 plans and conditions to execute. Do not stop at a pretty simulation.

## Frequent errors already discovered
- Calling a first-party **sample** PASS equivalent to a complete-history PASS.
- Calling **129 monthly source-crosschecks** a complete daily official NSE index certification.
- Quarantining one fund's differing September 2023 month-end and subsequently reintroducing it via month-label-only alignment.
- Rejecting AMFI `Option:null` as `"none"` or hammering the service after HTTP 429.
- Mistaking a clean-price G-Sec series for total return, or rolling gilt ETF for a single 2036 maturity sovereign.
- Treating RBI monthly averages as month-end ETF prices.
- Subtracting mutual fund expenses again from returns already derived from NAV.
- Confusing a model's 85% aspiration with a guaranteed inflation-adjusted floor.
- Selecting an allocation based solely on a short recent-history 11.4% volatility and neglecting regime/tail risk.
- Concluding "ready to invest" from a code-test or source-import success.

## Current stage decision
**Data source engineering:** multiple PASS subgates, R9 full bond NAV backfill still OPEN/FAIL.  
**Validated complete joint ten-year return history:** OPEN.  
**Tax-adjusted portfolio decision feasibility:** not fully established.  
**Investor GO:** **NO-GO**.

Never erase the failed manifests. Write a new dated audit for new findings and update the gate ledger only with verified results.
