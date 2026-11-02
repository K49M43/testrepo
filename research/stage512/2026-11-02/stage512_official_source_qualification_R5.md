# Stage 5.12 — R5 Official Source Qualification Update

**As-of:** 2 November 2026. **Investment authorization:** NO-GO.

## Verified outcomes

1. **AMFI bulk-source parser fixed:** the initial parser rejected the live eight-column feed; the corrected current and historical parsers now accept live eight-column layouts and retain legacy six-column current-file compatibility.
2. **Official AMFI three-window pilot passed** (GitHub run UTC `2026-11-02T11:20:22.369276+00:00`):
   - Latest: **14,200** priced observations; **241 zero-NAV exclusions**; **0 unclassified rejections**.
   - January 2–5, 2024: **26,794** priced observations; **432 zero-NAV exclusions**; **0 unclassified rejections**.
   - October 19–23, 2026: **34,712** priced observations; **432 zero-NAV exclusions**; **0 unclassified rejections**.
   - Total accepted: **75,706 NAV observations**; excluded non-investable zero NAV: **1,105**; no unexplained parse rejects. This is **sample-file validation**, not complete historical certification.
   - Live manifest: [AMFI bulk pilot](../data/amfi_pilot/manifest.json). Source checksums and individual request times in the manifest. Raw responses archived in GitHub Actions artifacts, subject to retention.
3. **Overlap against prior Stage 5.8 AMFI sampled checks:** **27 distinct scheme-date records**, all NAV prices and ISINs matched exactly (file [cross-check](../data/amfi_pilot/reconciliation_vs_stage58.csv)). The extra, broader latest-feed observations had no prior Stage 5.8 official comparison dates; absence of an anchor is not a data mismatch.
4. **Official per-scheme API discovered:** `https://www.amfiindia.com/api/nav-history?query_type=historical_period&from_date=YYYY-MM-DD&to_date=YYYY-MM-DD&sd_id=<scheme ID>`.
   - Two early October 2026 five-day probes returned HTTP 200 with structured JSON and four observations each.
   - A September 2023–October 2026 probe for Motilal Oswal Nifty 500 (scheme code 147625) returned **763 records** with a date+NAV structure, whereas one gold ETF request timed out.
   - Full long-period API qualification is therefore **NOT yet complete**. [API probe output](../data/amfi_api_probe.json).

## Controlled four-asset qualification

New [official-source verifier](../pipelines/amfi_four_sleeve_official.py) and [workflow](../../../.github/workflows/stage512-amfi-four-sleeve-qualify.yml) attempt official API history for four schemes: Nifty 500 fund `147625`, HDFC gilt fund `119116`, UTI Gold ETF `105463`, HDFC Silver ETF `150556`.

Acceptance criteria: identity confirmation; date/positive NAV validation; duplicate rejection; source SHA256; minimum three matching Stage 5.8 official NAV anchors for each series; quarantine for unexplained large unit-price jumps; at least 30 fully synchronized observed monthly returns before publishing an official-source four-sleeve covariance matrix. A response or a source-probe HTTP 200 is never itself an acceptance pass.

**Do not claim full 10-year official market coverage or investment-grade 2036 forecast calibration from 36 months.**

## What remains blocked

- Full-series primary-source scheme NAV histories (not just the four-sleeve pilot), including historical unit split/scheme reorganization treatment.
- Official NSE total-return benchmark and government-security index, and independent RBI domestic bullion series.
- Robust tail/regime validation and corrected CPI integration, updated taxes/execution costs.
- 85% real-wealth-floor model adequacy, which remains distinct from a legal guarantee.

**Decision: source ingestion pilot GO; whole model and investment authorization NO-GO.**
