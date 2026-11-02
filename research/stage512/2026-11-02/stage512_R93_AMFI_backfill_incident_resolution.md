# Stage 5.12 — R9.3 LIC G-Sec ETF Official-Source Backfill Incident & Correction

**Audit date:** 2026-11-02. **Investment authorization:** NO-GO. **Source-validation status:** short-window and six-month AMFI access verified; full 2014–2026 backfill not yet qualified.

## Independent AMFI primary-source access evidence

Code `133307` / ISIN `INF767K01MV5`, LIC MF Nifty 8–13 Yr G-Sec ETF.

### R9.1: four isolated historical spot windows

| Official AMFI sample | Number of NAVs | Last observed NAV |
|---|---:|---:|
| 2015-01-05 to 2015-01-09 | 5 | INR 13.5386 |
| 2018-06-04 to 2018-06-08 | 5 | INR 16.6209 |
| 2022-03-21 to 2022-03-25 | 5 | INR 22.2286 |
| 2026-03-23 to 2026-03-31 | 6 | INR 28.4282 |

All four responded from AMFI's scheme-specific primary API. The **31 March 2026 NAV INR 28.4282** independently agrees with the LIC Mutual Fund March 2026 published ETF factsheet: https://www.licmf.com/assets/downloads/monthly_fact_sheet/2026-2027/04/lic-mf-factsheet-31st-March-2026.pdf.

Evidence: [R9.1 source checksums and dates](../data/r9_lic_gsec_etf/short_window_probe.json).

### R9.2: four six-month windows, spread over 12 years

| Era | AMFI NAV observations | Status |
|---|---:|---|
| 2015 H1 | 119 | PASS_SOURCE_SAMPLE |
| 2018 H1 | 121 | PASS_SOURCE_SAMPLE |
| 2022 H1 | 120 | PASS_SOURCE_SAMPLE |
| 2026 H1 | 117 | PASS_SOURCE_SAMPLE |
| **Total** | **477** | **4 / 4 passed** |

Evidence: [R9.2 six-month source checksums and dates](../data/r9_lic_gsec_etf/medium_window_probe.json).

These 477 observations are **source-sampled evidence across four discontinuous windows**, not a synchronized 12-year return history. R9.1 spot observations may overlap with R9.2, so adding 21+477 would double-count observations.

## Full backfill: initial controlled failure and correction

The first full backfill wrote `FAIL_INCOMPLETE` for **24** intended six-month periods, accepting zero segments. The manifest exposed two **implementation/access defects**:

1. The AMFI JSON API sometimes emits `"Option": null`. The original parser did `str(None).lower() → "none"`, then rejected it as if the public ETF had an explicitly non-growth option. This was **a false rejection**, not evidence the ETF had a distribution or corporate-action problem.
2. Four simultaneous requests to the official AMFI service induced `HTTP 429 Too Many Requests`. Repeating large synchronized jobs would be inappropriate; respectful bounded access and backoff are required.

**Fixes committed to the original acquisition pipeline:**
- Accept absent/null Option as unspecified for the separately verified growth-only product; still reject an explicit incompatible option.
- Replace four simultaneous queries by **sequential 6-month requests**.
- Bounded retries with 429-specific delays, plus a rate-limit circuit breaker; do not bypass source protection.
- Cache each byte-exact successfully fetched official response and record SHA256; commit raw public API segments for resumable future runs.
- Always persist partial observations as `partial_official_AMFI_NAV_UNQUALIFIED.csv`; never pass them through continuous-history return calculations.
- A full-history pass still requires date continuity, no conflicting NAVs, >=2,500 priced dates, pricing-discontinuity checks, and March 2026 LIC official published 1-, 3-, and 5-year CAGR reconciliation.

The failed manifest is **preserved** until a corrected run commits a later result. R9 is not a GO merely because errors were explained and code fixed.

## Independent forward-model protection

A separate official NSE Nifty500 TRI versus AMFI LIC ETF historical risk bridge can execute **only** after full source qualification. The NSE whitepaper's 129 official monthly TRI return observations (Jan 2015–Sep 2025) are already pinned from R8.

R9's independent bridge now verifies both:
- all 129 calendar-month return labels match; **and**
- ETF monthly closing observation dates align with a separately pinned, NSE-monthly-validated daily mirror's index observation dates **at both ends of each return interval**.

The date-only reference has 130 entries (Dec 2014–Sep 2025). A mismatched monthly endpoint is quarantined; the bridge requires at least 100 strictly matching return intervals before publishing source-qualified joint correlation. Month-end date evidence comes from a historically cross-checked third-party index file, **not direct daily NSE primary publication**.

## Finance / risk caution

The LIC ETF is a **rolling 8–13-year duration strategy**, distinct from a direct G-Sec held to 2036 maturity, and actual ETF market prices may differ from its daily NAV.

LIC's March 2026 fund factsheet reports modified duration **6.57 years**, yield-to-maturity **7.11%**, total expense ratio **0.17%**, and published one-year tracking error **0.14%** as dated figures. These are not investor guarantees or forward return estimates. Annualized *tracking difference* from LIC's four published factsheets is a different statistical quantity from tracking error.

## Decision

| Gate | Result |
|---|---|
| Official historical scheme identity: sampled 2015, 2018, 2022, 2026 | PASS |
| Official six-month request reliability: four periods | PASS |
| Full 24-segment continuous 2014–2026 official NAV series | **OPEN — corrected source pipeline** |
| Published LIC 1/3/5-year NAV–benchmark arithmetic | PASS on 12 published lookbacks |
| Strict 129-month equity/TRI versus gilt ETF NAV covariance | **NOT YET COMPUTED** |
| Complete NSE government-security total-return index levels | OPEN |
| Investment authorization | **NO-GO** |

The correct next proof is **a single complete, source-pinned, no-gap 2014–2026 LIC NAV history**, not more speculative simulation or an unsupported 2036 success percentage.
