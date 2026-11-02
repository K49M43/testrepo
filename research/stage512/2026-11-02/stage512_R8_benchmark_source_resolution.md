# Stage 5.12 — R8 Benchmark Source Resolution (Equity TRI + RBI-origin Bullion)

**Date:** 2026-11-02 | **Research gate:** PARTIAL PASS | **Investment authorization:** **NO-GO**

## Executive finding

R8 has materially advanced beyond a blocked NSE application endpoint. Two separate source-resolution paths now have independently executed GitHub CI checks:

1. **Equity:** Official NSE Nifty 500 **TOTAL RETURN** monthly published returns, Jan 2015–Sep 2025, were manually transcribed from Exhibit 12 (printed p. 12, PDF page index 12) of NSE's Oct 2025 Nifty 500 whitepaper. They were cross-checked against the pre-existing daily-level third-party Nifty 500 TRI dataset with the input source protected by its exact Git blob SHA1.
2. **Bullion:** A mirror of RBI's published monthly Mumbai gold/silver table yielded 437 consecutive monthly observations Apr 1990–Aug 2026. Seven months (14 prices) were checked against published RBI bullion tables and all matched. The source is an **unofficial mirror**; 430 other months were not independently primary-source validated.

These findings support historical calibration, **not** an independently calibrated ten-year real-wealth goal probability.

## 1. Official NSE Nifty 500 total-return validation

Source document: https://www.niftyindices.com/docs/default-source/indices/nifty-500/nifty-500-whitepaper_2025.pdf  
Index identity: **NIFTY 500 TR / TRI**, monthly total-return figures, not price index.
- Date range: **2015-01 through 2025-09**, **129 contiguous months**.
- Official published figures are to **two decimal places**. Compounded within-year figures reconcile to publication calendar-year returns within **0.055 percentage point** across 2015–2025 (2025 Jan–Sep only).
- Daily mirror used solely as independently cross-checked historical input: GitHub repo `Sams3pi01/SIP-Calculator`, file `NIFTY 500 TRI.csv`, Git blob SHA1 `89f0bb076ce6a733197e89416830203c6f3ddd8a`.
- **129/129 months match within 0.0051 percentage point**, maximal absolute difference **0.0049783161 pp**, mean absolute difference **0.0024927713 pp**; all values consistent with two-decimal publication rounding.
- Not proven: every daily value of the third-party dataset from 1995–2026 is first-party validated. The original NSE direct TRI application POST still returns an HTML homepage redirect in the GitHub environment.

Primary NSE monthly data: [published monthly matrix](../data/nse500_official_tri_monthly_2015_2025q3_R8.csv).  
Independent audit: [code](../pipelines/r8_nse_whitepaper_monthly_verify.py), [CI result](../data/nse500_tri_validation_R8.json).  
NSE failed direct endpoint diagnostics: [source access record](../data/nse_tri_source_probe_R8.json).

**Qualification: PASS_129_OFFICIAL_MONTHLY_ANCHORS; complete NSE daily PRIMARY source: NOT QUALIFIED.**

## 2. RBI-origin Mumbai bullion monthly reference

RBI-origin publication: `Monthly Average Price of Gold and Silver in Mumbai`. Gold INR/10 grams, silver INR/kg. 

Distribution and extraction: The public *third-party* DBIE mirror's read-only API, `https://data-api.dbie.rbihub.in/api/tables/real_sector/r17_monthly_average_price_of_gold_and_silver_in_mumbai/csv`. This is not the RBI-owned primary DBIE API. We preserve its source URL, download SHA256 and original CSV as audit artifacts.

Validated secondary data-integrity properties:
- **437 contiguous monthly reference periods, 1990-04 to 2026-08**.
- No missing months or duplicate monthly observations in the accepted normalized CSV, and all observed gold/silver values are positive.
- Input raw SHA256: `b170913646b0bd95096f200d03474b1401cb6b409e661a8253b6ed476cbf5337`.
- Seven official-publication monthly anchors: Jan/Feb 2021, Mar/Apr 2023, Apr/May/Jun 2024; **7/7 month pairs / 14/14 individual gold and silver prices matched**.

RBI source publications:
- 2021 Table 20: https://www.rbi.org.in/hindi1/Upload/Bulletin/PDFs/20T_H26042021C0ED73889751447BA4174445F3375163.PDF
- 2023 Table 20: https://www.rbi.org.in/hindi1/Upload/Bulletin/PDFs/20T_H23062023823C72126B78423F918CE474D1891B0E.PDF
- 2024 RBI Bulletin Table 166: https://systemhealth.rbi.org.in/Scripts/PublicationsView.aspx_id%3D22640.html

Caveat: RBI PDF numerical anchors were cross-checked using extracted textual tables; PDF screenshot rendering was unavailable during this run, so formal visual proof for those specific PDF rows remains open.

Primary validation CSV: [7 RBI-published anchors](../data/r8_rbi_bullion_official_published_anchors.csv).  
Secondary normalized history: [437 monthly price pairs](../data/r8_rbi_origin_mirror/rbi_origin_mumbai_bullion_monthly_SECONDARY_MIRROR.csv).  
Provenance manifests: [secondary mirror integrity](../data/r8_rbi_origin_mirror/normalized_validation.json); [official-sampled verification](../data/r8_rbi_bullion_primary_spotcheck_manifest.json).  
Scripts: [normalize](../pipelines/r8_bullion_mirror_normalize.py), [independent primary anchor checks](../pipelines/r8_rbi_bullion_primary_anchor_check.py).

**Qualification: PASS_SECONDARY_MIRROR_INTEGRITY_ONLY + PASS_OFFICIAL_RBI_SAMPLED_ANCHORS_ONLY. Full 437-month first-party RBI extraction: OPEN.**

## 3. Government-security total-return benchmark selection

NSE official index **Nifty 8–13 Yr G-Sec** factsheet, October 31, 2025: https://www.niftyindices.com/Factsheet/Nifty_8-13_G-Sec.pdf  
Official NSE fixed-income methodology, February 2026: https://www.niftyindices.com/Methodology/Method_NIFTY_Fixed_Income_Indices.pdf

- Published factsheet explicitly lists **Total Returns** methodology, base date Jan 3, 2011 and monthly index review; it holds a liquid three-security GOI basket with ~8–13 years remaining maturity.
- Factsheet October 2025 gross index reported 1y return 8.31%, 5y annualized 5.75%, inception annualized 7.57%. These are **dated historical index facts**, not 2026 prospective rates.
- **NOT YET QUALIFIED:** historical monthly/annual total-return index observations. Bond-yield-based proxies and this actual rolling total-return index are distinct. Neither represents direct ownership of a 2036-maturity sovereign bond or the identical risk of a particular gilt mutual fund.
- **Not suitable substitute:** Nifty 10 Year Benchmark G-Sec (**Clean Price**) because it excludes the coupon-return component; NSE explicitly distinguishes total-return from clean price.

**Qualification: official index methodology identified; historical total-return data remains OPEN.**

## 4. Recalibration constraints (must be enforced)

- NSE monthly **total-return** figures can validate equity historical returns, subject to two-decimal publication rounding and the explicit 2015–Sep2025 coverage. Use third-party daily series outside anchor period only with provisional provenance labels.
- RBI Mumbai **monthly AVERAGE bullion** observations cannot be treated as market month-end gold/silver ETF price returns. Direct return covariances against month-end equity or fund NAV would introduce observation-timing distortions. No splicing without bridging / frequency convention correction.
- Actual fund NAV histories incorporate TER; do not double-subtract management expenses. ETF NAVs are not tradeable market prices; market spread and premium/discount matter.
- No extrapolation of recent 2025–26 gold/silver returns into a deterministic expected-return forecast.
- 2026-endpoints must be updated as official releases are published and carefully source-vintaged.
- 2036 after-tax inflation-adjusted floor requires current instruments, execution, investor taxation, correlated forward regime stress and credible return-parameter uncertainty.

## 5. Research gate and next work

| Gate | Current decision |
|---|---|
| Official AMFI 4-fund 36mo strict NAV covariance R7 | PASS, research only |
| Official NSE 129-month TRI return anchor crosscheck R8 | PASS |
| RBI-origin 437-month mirror integrity | PASS, secondary origin |
| Official RBI 7 published month anchors | PASS, sampled only |
| Government-security total-return historical series | **OPEN** |
| Whole joint benchmark monthly alignment | **OPEN** |
| Real-world 85% probability or guaranteed ₹90L real floor | **NOT ESTABLISHED** |
| Final investment authorization | **NO-GO** |

**Next priority:** obtain official NSE 8–13 Yr G-Sec total-return historical observations and reconcile the government-bond series, followed by inflation-linked joint market alignment. The goal is not to force a GO by lowering the acceptance criterion.
