# Stage 5.12 — Source Reuse and Primary-Source Import Gate (R4)
**Date:** 2026-11-02  
**Decision:** Research validation progress; 2036 investment authorization remains **NO-GO**.

## 1. Recover validated work rather than resimulating proxies
The existing repository contains a Stage 5.8 official AMFI reconciliation:
- `research/stage58/qa_summary.json`: 96 scheme histories examined; 96 matched at sampled official AMFI NAV dates; no mismatched sampled NAV values reported.
- 73 histories marked `QA_PASS` by existing checks; 15 large daily price discontinuities identified across 12 schemes, with unresolved denomination changes quarantined rather than treated as ordinary returns.
- Historical daily series themselves were downloaded from **mfapi.in**, a third-party AMFI history mirror. Official AMFI checks verified **samples**, not entire daily histories. Do not label the full mirror data as independently primary-source validated.
- Prior AMFI source checks recorded 13,498 current scheme NAV observations and open-ended historical download window counts of 44,768 (Oct 26–31, 2026), 27,281 (Jun 25–30, 2026), 34,489 (Sep 25–30, 2025), and 30,323 (Sep 25–30, 2023). The numbers are observations from the previous Stage 5.8 source run, not newly fetched today.
- The sampled historical NAV dates demonstrate access to official AMFI feeds through the repository's GitHub Actions environment, subject to independent retrieval in each run.

## 2. Existing QA cohort composition
The 96 reviewed records can be organized by **name keyword only**, not formal SEBI scheme classification:
| Heuristic name group | Sampled official NAV matches | Previous QA_PASS | With daily discontinuity |
|---|---:|---:|---:|
| Equity index named | 38 | 21 | 0 |
| Gold named | 10 | 8 | 8 |
| Silver named | 7 | 5 | 2 |
| Gilt/GoI named | 2 | 2 | 0 |
| Cash-like named | 2 | 2 | 1 |
| Other names | 37 | 35 | 1 |
| **Total** | **96** | **73** | **12** |

Counts are from existing `research/stage58/qa_metrics.csv`. Name groups are descriptive and **not a product taxonomy**.

## 3. Newly committed Stage 5.12 official-source ingestion pilot
- `research/stage512/pipelines/amfi_source_pilot.py`: retrieves current official AMFI NAV and two historical sample windows.
- `research/stage512/tests/test_amfi_source_pilot.py`: parser contracts, invalid-data rejection, date-window limit, and class-label tests.
- `.github/workflows/stage512-amfi-primary-source-pilot.yml`: performs tests, downloads samples, stores raw response artifacts, commits a source SHA256/date-coverage manifest and filtered public observations.
- First live pilot captured HTTP 200 text from official AMFI but rejected all rows because it assumed an outdated column layout. This **failed closed**, and produced `research/stage512/data/amfi_pilot/manifest.json` with `FAIL_INCOMPLETE`, not a false success. The newer code recognizes live **8-column current** and **8-column historical** official AMFI formats, as evidenced in Stage 5.8, while retaining legacy 6-column support for current NAV.
- The pilot is an access-and-format test, **not full backfill, not complete scheme identity reconciliation, and not investment risk approval**.

## 4. Source qualification acceptance contract
For any asset eligible for full 2036 Monte Carlo recalibration:
1. Record exact official source URL, retrieval timestamp, byte SHA256, file schema/version, period, market/business-date conventions and fund scheme code+ISIN.
2. Preserve raw official evidence; reject empty HTML, date gaps beyond acceptable market holidays, duplicate scheme-date rows, invalid NAV, split/merger or dividend discontinuities without corporate action proof.
3. For third-party mirrors, require independently sourced AMFI spot checks **and** a controlled full-history qualification standard. A handful of spot checks alone does not qualify years of return statistics.
4. Distinguish scheme NAV (already net of TER) from external friction, taxes, ETF market price/liquidity, tracking differences and distributions.
5. Use a 10-year assessment only when adequate uninterrupted historical coverage and effective sample-size caveats are documented. Overlapping windows do not yield independent forecast trials.
6. Do not infer `P(W_2036 >= 90L)` from a source-ingestion pass.

## 5. Remaining gates (hard NO-GO)
- Primary-source full-range AMFI backfill and named scheme mapping for candidate instruments **not completed**.
- NSE Nifty 500 TRI and genuine traded government-security total return series **not fully reconciled**.
- RBI domestic monthly gold/silver observed series **not yet fully reconciled**.
- CPI linked series has a draft reconstruction; release alignment and independently verified series remain required.
- Risk and tail model need rerun on qualified investable return histories.
- Floor protection is unproved; an 85% modeled success criterion remains separate from an actual legally guaranteed floor.

**Audit conclusion:** The data blocker is narrower than earlier reports implied, because Stage 5.8 already official-verified 96 scheme NAV histories at sampled dates. It is nevertheless **not closed**; the live AMFI pilot must pass and full-span data still must be qualified before 2036 probability claims.
