# 2036 Personal Investment Decision — Dated Decision Log

This log records **actual investment authorization** separately from engineering/source qualification. Append new dated entries; preserve corrections and failed tests.

## 2026-11-02 — Mandate reset and Codex handoff
- **Program objective clarified:** deliver support for the investor's *actual real-money investment decisions*, not a general research study or a productized investment research platform.
- **Investor goal unchanged:** ₹42L upfront, ₹25k/month stepped 10% each year, 2036 year target, ₹90L 2026-real after-tax planning floor, ₹1Cr real stretch, about 85% aspirational modeled floor success.
- **Relevant investor context:** India resident, new tax regime, approx 30% marginal income slab (not a universal capital-gains tax rate), Groww, no outstanding liabilities, no current income need, no expected interruption in funding.
- **Current supporting evidence:** official Nifty500 TRI 129 months independently anchored, 36 strict-month actual-fund NAV covariance, RBI-origin bullion secondary mirror with sampled RBI published anchors, linked CPI provisional reconstruction, and R9 LIC G-Sec ETF 4/4 short and 4/4 six-month official AMFI probes.
- **Current blocking evidence:** R9 full LIC ETF 2014–2026 backfill last reported FAIL, despite passing parser regression; full NSE G-Sec TR index unavailable; comprehensive tax-and-inflation-aware 2036 decision forecast not qualified.
- **Investment authorization:** **NO-GO**; no portfolio, trade, or 85% floor probability endorsed.
- **Decision change requirements:** verified source/model/tax/implementation gates and an independently challenged investor decision memo, followed by explicit investor confirmation.
- **Next owner:** Codex executes engineering starting with R9 qualification; investor/independent reviewer controls actual investment decision.

**Do not edit this 2026-11-02 entry retroactively to claim an outcome that occurred later.** Append later dated entries with commit references.

## 2026-11-02 — R9.3 complete AMFI history and strict risk bridge
- **Executed:** sequential bounded AMFI request for all 24 half-year periods; archived original bytes; ran the independent raw-artifact validator and the existing 129-month TRI / ETF NAV bridge.
- **Source result:** 2,867 official AMFI NAV observations, 26 Dec 2014–30 Oct 2026; all 24 source hashes and byte counts independently reproduced; max observation gap 6 days; LIC March 2026 1/3/5-year published NAV CAGR differences are 0.0047/0.0080/0.0054 percentage points.
- **Risk bridge:** 117 of 129 month returns passed both-end date equality; strict TRI / LIC ETF NAV correlation 0.022541, sample annualized log volatility 17.02981% / 3.72678%. Month-end index dates rely on a cross-checked third-party mirror. The LIC ETF is not the index or a direct 2036 sovereign bond.
- **Comparison:** in the common recent 36-month sample LIC ETF NAV annualized volatility is 3.00403%, vs HDFC Gilt Fund 3.65747%; descriptive and backward-looking only.
- **Evidence:** `research/stage512/2026-11-02/stage512_R93_live_backfill_and_129m_audit.md`, `research/stage512/data/r9_lic_gsec_etf/qualification_manifest.json`, `research/stage512/data/r9_lic_gsec_etf/r93_independent_artifact_audit.json`, and `research/stage512/data/r9_nse_gsec_129m_source_bridge.json`.
- **Investment decision:** **NO-GO unchanged.** This advances source qualification only; cashflow/tax/inflation model, eligible candidate screen, forward uncertainty, suitability and independent challenge are still open.
- **CI hardening:** the first branch bridge check identified Git line-ending normalization changing hashed CSV bytes between Windows and Ubuntu. The R9 data directory is now marked byte-preserving in `.gitattributes`; subsequent bridge CI is expected to verify the correction.
