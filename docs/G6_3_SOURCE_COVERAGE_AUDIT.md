# G6.3 WP1 — Source coverage and candidate inventory

**As of:** 2026-11-06  
**Disposition:** `PASS_SOURCE_INVENTORY_ONLY`; G6 decision-grade remains `NOT_READY`; investment authorization remains `NO_GO`.

## Scope and method

This increment reconciles source identity, retained raw bytes, normalized histories, candidate dispositions, date overlap, and external source leads. It does not estimate portfolio outcomes or probability. The reproducible entry point is `decision/audit_g6_3_source_inventory.py`; the frozen record is `research/stage512/2026-11-06/g6_3/source_inventory_v1.json`.

The audit independently re-hashes every file listed in the G5.4 source-reacquisition manifest; reconciles five AMFI scheme NAV histories and their date bounds; checks the official monthly NSE Nifty 500 TRI anchor coverage; reconstructs the retained R9 LIC scheme 133307 NAV series from all 24 AMFI raw segments; verifies normalized daily/monthly outputs and factsheet CAGR checks; and intersects month-end returns only where all listed candidate histories overlap. No data are downloaded or silently filled by this audit.

## Reproduced coverage

| Evidence set | Reproduced result | Interpretation |
|---|---:|---|
| G5.4 raw source manifest | 94 files, 22,481,950 bytes; 0 missing and 0 hash/byte mismatches | Retained bytes match the manifest. This verifies integrity, not each source's investment suitability. |
| Continuous G5 candidate NAV series | Five series; 7,353 observations total | Official AMFI scheme NAVs. NAVs are not ETF traded prices. Coverage begins between 2015 and 2024 depending on product. |
| LIC 8–13 Yr G-Sec scheme (AMFI code 133307) | 24/24 raw segments; 2,867 daily NAV observations from 2014-12-26 to 2026-10-30; 142 monthly returns; maximum observed date gap 12 days or less | Reproduces a long official fund-NAV history. It is a fund proxy, not ETF market price, a G-Sec total-return index, or direct sovereign-bond cashflow. |
| LIC normalized outputs | Daily and monthly CSV hashes and rows exactly reconcile to raw segments | Reproducibility of this source transformation only. |
| LIC factsheet anchors | 1/3/5-year CAGR differences remain below the predeclared 0.14 percentage-point tolerance | A bounded cross-check, not proof that every NAV is correct. |
| NSE Nifty 500 TRI | 129 monthly anchors, 2015-01 through 2025-09 | Monthly anchors are not a daily total-return path. |
| Candidate universe | Ten product hypotheses retain explicit dispositions and open evidence gates | Meets the screen-count inventory only; it does not mean ten candidates are fully eligible or comparable. |

The five G5 normalized NAV series are Motilal Nifty 500 Index Fund, SBI Gilt June 2036 Fund, HDFC Gold ETF, ICICI Silver ETF, and SBI Nifty 500 Index Fund. Their observation counts, exact date ranges, maximum gaps and source classifications are captured in the machine-readable record.

## Joint-history constraint

| Common monthly-return set | Shared returns | Dates | What it permits |
|---|---:|---|---|
| Motilal Nifty 500 Index Fund + LIC G-Sec ETF + HDFC Gold ETF + ICICI Silver ETF | 57 | 2022-02 to 2026-10 | Descriptive recent co-movement only. |
| Motilal Nifty 500 Index Fund + SBI Gilt June 2036 Fund + HDFC Gold ETF + ICICI Silver ETF | 48 | 2022-11 to 2026-10 | Descriptive recent co-movement only. |
| Previous mix plus SBI Nifty 500 Index Fund | 24 | 2024-11 to 2026-10 | Too short for decision-grade long-horizon tail estimation. |

These are overlapping monthly observations, not independent annual outcomes. The records are not a calibrated distribution of future 2036 results. Product return coverage is uneven and mostly much shorter than the target horizon; the silver and SBI Nifty 500 histories are especially short. The official Nifty TRI has only 44 common months with the silver series, so extending history by splicing indexes, funds or proxies would change the return-generating process and is not accepted here.

## Candidate disposition and unresolved source gates

The ten candidate hypotheses and their detailed statuses are embedded in `source_inventory_v1.json`; the controlling G5 dispositions remain in `g5_candidate_disposition_v1.json`. Several identities have continuous NAV histories, but the quantitative candidate set is not yet implementation-ready.

- **ETF execution:** official NAV histories and holdings do not establish exchange traded prices, bid/ask spreads, premium/discount, depth, settlement, current availability or investor access through the stated platform.
- **Direct GoI bonds:** a bond must be modeled by dated dirty price/accrued interest, coupon cashflows, reinvestment, maturity and executable availability. The retained 7.18% security `IN0020230085` matures 2033-08-14, before the 2036 objective, so it cannot be represented as a 2036 held-to-maturity position without a reinvestment policy and replacement evidence.
- **91-day Treasury bills:** RBI Handbook Table 218 offers official auction and issue information, but the retained evidence does not establish a complete investor-executable rolling series or retail noncompetitive-allocation price path. Auction cut-off yields cannot automatically be treated as the investor's realized price.
- **CCIL historical trades and marks:** the public MTM archive distinguishes traded prices from CCIL model marks for securities without qualifying trades. Historical trade access and redistribution terms remain unresolved; no sign-in, restricted dataset or permission request was used.
- **Inflation:** the original official MoSPI release bytes and investor-selected 2026 purchasing-power base month remain open gates. The 6% planning assumption remains a sensitivity, not a forecast.
- **Instrument economics and personal suitability:** taxes by event/lot, current TER and other fees, ETF spreads, distributions/coupons, loss treatment, investor dates, tax facts, drawdown tolerance and product access remain WP2 / investor-confirmation gates.

## Official-source leads retained for bounded follow-up

These are leads only; this WP did not acquire or normalize new data from them.

- RBI, [Handbook of Statistics on the Indian Economy](https://www.rbi.org.in/Scripts/AnnualPublications.aspx?head=Handbook%20of%20Statistics%20on%20Indian%20Economy), including Table 218 for 91-day Treasury-bill auctions.
- RBI, [Government Securities: FAQs](https://m.rbi.org.in/commonman/english/scripts/FAQs.aspx?Id=711), for retail/noncompetitive bidding mechanics that must be reflected when constructing an executable price path.
- CCIL, [MTM Prices](https://www.ccilindia.com/mtm-prices), with traded-price versus model-mark provenance retained as a required distinction.
- CCIL, [Historical G-Sec Trades](https://www.ccilindia.com/g-sec-historical-trades) and [Data Sharing Policy](https://www.ccilindia.com/documents/d/ccil/CCIL_DATASHARING_POLICY_OCT24); access and redistribution rights must be resolved before relying on or publishing restricted evidence.

## Acceptance result and next dependency

**WP1 source-inventory subtask passes** because all retained source hashes and transformations audited here reconcile, the ten hypotheses remain dispositioned, joint-history limits are explicit, and blocked evidence is not promoted. **WP1 as a whole does not pass.** ETF execution inputs, direct sovereign-bond economics, T-bill rollover, original CPI bytes/base month, and sufficient validated joint histories remain unqualified.

Next: build a source-specific acquisition decision for each strategy that could materially affect allocation. First prioritize evidence capable of changing the decision: (1) CPI primary release and base-date confirmation route; (2) lawful and reproducible direct-GoI/T-bill total-return construction; (3) ETF market-price/execution and cost series for any candidate retained after the screen. Do not start a probability model on these short joint samples. Any sensitivity using them must be explicitly descriptive and must not be presented as 2036 success odds.

## Reproduction

Run from repository root with Python 3.13:

```powershell
python research/stage512/2026-11-05/g5_4/audit_g5_4.py
python research/stage512/2026-11-05/g5_4/audit_g5_candidate_nav_history.py --check
python research/stage512/2026-11-05/g5_4/audit_g5_exit_acceptance.py --check
python research/stage512/pipelines/r9_lic_gsec_official_amfi_history.py
python decision/audit_g6_3_source_inventory.py --check
```

The G6.3 checker reconstructs the inventory and requires byte-identical JSON. The artifact records the audit version and source evidence; no random seed is used because this is a deterministic source-validation task.
