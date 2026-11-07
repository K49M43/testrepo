# G6.3 closeout decision pack — evidence-based NO-GO

**As of:** 2026-11-06  
**Decision state:** `NO_GO / NOT_YET_EVALUATED` for an implementable 2036 portfolio.  
**Investment authorization:** `NO_GO`. No instrument ranking, allocation, trade, or suitability conclusion is made.

This pack applies the fallback closure clause in GitHub issue #44: when decision-grade gates cannot pass, document each unavailable input, source evidence and lawful alternative, quantify its decision consequence where possible, and conclude NO-GO / NOT YET EVALUATED. Closing the engineering issue under that clause means the present work has established that the evidence is insufficient; it does not mean WP0–WP4 passed or that a portfolio has been validated.

## Decision mandate retained

The mandate remains ₹42 lakh initial capital, ₹25,000 monthly SIP with 10% annual step-up, a ₹90 lakh floor and ₹1 crore stretch goal in 2026 purchasing power by 2036, no current investment-income need, and no reported liabilities. The floor and 85% modeled-success aspiration are objectives, not guarantees or assumptions to fit. The G3 schedules remain two fixtures: 120 and 122 monthly contribution cases; recorded contributions are ₹89,81,227.3803 and ₹91,10,914.503305 respectively. Contributions are not portfolio values. Exact first contribution date, SIP day, base CPI month, terminal date, risk tolerance, and platform-specific product access remain unconfirmed or unverified.

As an explicitly illustrative sensitivity only, at 6% annual inflation for ten years, the ₹90 lakh real floor corresponds to about ₹161.18 lakh nominal in 2036 and the ₹1 crore stretch to about ₹179.08 lakh. Six percent is not a forecast, and these values are not personal outcomes. The qualified CPI history supplies an observed deflator through September 2026; it does not determine future inflation or the investor's selected 2026 anchor.

## Work-package disposition

| Package | Evidence established | Blocking evidence / source-verifiable limitation | Lawful alternative | Decision consequence |
|---|---|---|---|---|
| WP0 — decision contract | Mandate/register and G3 120/122 schedules are versioned; prior synthetic integrations preserve the schedule. | Payment dates and selected 2036 valuation/liquidation date are not confirmed by the investor. The 122-payment path is sensitivity only. | Investor confirms the dates/policy; keep both schedules as separate illustrations until then. | Exact personal dated cashflows, XIRR and final liquidation value unavailable. |
| WP1 — candidates and sources | Ten candidate hypotheses are dispositioned; five AMFI Growth NAV histories and the LIC 8–13 year G-Sec fund NAV history have source lineage. CPI MoSPI API series covers 165 months (Jan 2013–Sep 2026); the 21 current observations match the parsed PIB monthly table and September remains provisional. The previously staged old-base comparison is not counted as independent numeric validation. | The candidate screen does not establish ten eligible/comparable products. Fund NAV is not ETF execution price, a government total-return index, or direct bond cashflows. Joint overlaps (57/48/24) are calendar-month label counts only; endpoint dates are not verified equal and these counts cannot support covariance. RBI Table 218 contains 50 displayed 91-day auction rows (2025-07-02 to 2026-06-24), but raw XLSX/PDF attempts returned HTML; Table 218 omits auction method and NCB weighted-average prices; a later official notice/result sample confirms those fields exist, but no historical 2025–26 paired panel is retained. Direct GoI price/coupon/reinvestment data and current product access/cost evidence remain unqualified. | Preserve official raw exports when lawfully obtainable; use RBI per-auction notices and Full Auction Result releases for T-bills, reconcile to Table 218, and retain exact-date source pairs; use official security cashflows and public first-party or separately licensed data for dated bonds; use exchange price/depth and AMC/AMFI sources for eligible products. Do not redistribute data beyond source terms. | No comparable investable-return panel or defensible joint-risk matrix exists. A NAV proxy cannot select a sovereign allocation. CPI can deflate historical values only after investor base-month confirmation. |
| WP2 — economics, tax, cashflows | G6.1/G6.2 deterministic ledger mechanics independently reconcile synthetic events, lots, tax components and CPI arithmetic. The event ledger rejects unsupported loss cases. | Marks, fees, tax context and CPI path are fixtures. No candidate-specific execution, TER/spread, coupons/distributions, withholding/reinvestment, direct bond maturity cashflows, investor-level tax inputs, partial exit, or real XIRR is qualified. Current tax-law fixtures do not forecast 2036 law. | Integrate source-qualified instrument event paths and contemporaneous statutory rules; compare enacted-law and explicit future-law sensitivities. Confirm personal tax inputs and exact cashflow dates before personal calculation. | No actual post-fee/post-tax nominal value, real purchasing power, or money-weighted return may be reported. The synthetic G6.2 totals are expressly excluded. |
| WP3 — uncertainty and comparison | The repository quarantines a prior synthetic-return claim; G5 reports the sample coverage and no calibrated tail probability. | At most 57 shared calendar-month labels (under half of a 120-month horizon), 48 (40%), or 24 (20%) are observed in the listed multi-asset mixes, before exact endpoint-date screening. These are not independent annual outcomes. No pre-registered, evidence-qualified, out-of-sample model protocol or independent replication of a probability claim exists. | First qualify longer source series and exact date alignment; preregister regimes, estimation, resampling and adverse cases; report numerical, sampling, parameter, model and investor-input uncertainty separately. If history remains short, report conditional sensitivities and no real-world success probability. | No probability of meeting the floor, including the aspirational 85%, is supportable. No strategy ranking is valid. |
| WP4 — independent challenge and decision pack | G5 source/candidate audits and G6.1/G6.2 bounded independent formula audits pass their declared scopes; this Codex review separately inspected G6.3 source/checker integration. | No complete strategy comparison, implementation memo or independent external review of an actual portfolio exists. This audit does not substitute for that review. | After WP1–WP3 evidence exists, commission or perform a separately identified reviewer challenge against frozen data/code and publish the resolved finding log. | No GO or conditional GO. This pack records a present NO-GO / NOT YET EVALUATED conclusion only. |

## Quantitative limits and why the objective remains unassessed

- The two contribution totals differ by ₹1,29,687.123005 because the 122-payment case includes two additional modeled monthly contributions. This is a schedule sensitivity, not an ending-wealth difference.
- The largest listed joint return overlap is 57 calendar-month labels, versus 120 months in the primary schedule: 47.5% of its month count. The 48- and 24-label sets represent 40% and 20%. Exact date matching may reduce these counts further.
- The 50 RBI Table 218 rows span less than one year of auctions; they cannot alone build a 2014–2036 rollover history. One zero-accepted auction row has no cutoff price/yield and cannot be treated as a return observation.
- CPI data qualify a historical series, not future inflation. The historical source passes but personal real-value outputs remain blocked pending the chosen base month.
- No G6.1/G6.2 fixture output is an estimate of this investor's terminal wealth. Therefore no numerical shortfall probability or probability confidence interval is supplied; inventing one would overstate evidence.

The source-by-source inventory, including exact retained failure metadata, evidence status, lawful route and decision consequence, is in [`G6_3_UNAVAILABLE_EVIDENCE_LEDGER.md`](G6_3_UNAVAILABLE_EVIDENCE_LEDGER.md). That ledger distinguishes verified acquisition failures from evidence not yet acquired and investor confirmations; it does not relabel all missing evidence as a failed source.

## Lawful next routes if the investor later reopens decision-grade work

1. Confirm the purchasing-power base month and exact funding/terminal dates; retain all schedule alternatives.
2. Retrieve official RBI Table 218 data through a supported official download or DBIE route and pair each used auction with its auction method, allotment price and settlement/maturity evidence. Otherwise do not model a retail T-bill path.
3. Obtain dated GoI bond cashflows and prices from first-party public sources or a separately authorized data source. For CCIL, obey its current data-sharing policy, distinguish qualifying trade prices from model marks, and do not publish restricted raw data.
4. For each surviving product, qualify point-in-time access, exchange execution prices/spreads/depth, fees, distributions/coupons, tax classification and reinvestment inputs.
5. Reconcile actual event/lot taxes and dated XIRR, then preregister and independently challenge the uncertainty protocol before any strategy comparison.

## Reproduction and traceability

- CPI: `python decision/audit_g6_3_cpi_qualification.py --check`
- Source inventory: `python decision/audit_g6_3_source_inventory.py --check`
- G5.4, NAV and exit audits: see the reproduction commands in `docs/G6_3_SOURCE_COVERAGE_AUDIT.md`.
- G6.1/G6.2: `python decision/audit_g6_deterministic_bridge.py` and `python decision/audit_g6_2_full_horizon_bridge.py`.
- Official CPI and sovereign artifacts, their source URLs and hashes: `research/stage512/2026-11-06/g6_3/`.

PR #48 merged as `a44d13f44a82c0ca91cd09bc9f3e5212e14d51d0`; its eight exact-head workflows passed on both PR events and eight workflows passed on merged main. The subsequent audit found that the closure pack did not include a source-by-source unavailable-evidence ledger and that the CPI checker did not parse the PIB monthly table. The issue is reopened for remediation; NO-GO remains in force. PR #49 metadata-only checks and the original merge record remain historical evidence, not acceptance of this remediation.

## Evidence addendum — official RBI archive/result route (2026-11-06)

After this decision-pack snapshot, PRs #55–#58 captured the RBI archive index, a November 2025 month page, and one November 26, 2025 T-bill full result with hash-verified raw bytes. This confirms a lawful official route and one historical auction-result data point. It does not supply the full Table 218 date-matched historical panel, direct GoI bond cashflows, ETF market execution inputs, personal tax/base-month confirmations, aligned joint-return history, or the required strategy comparison. Accordingly, the prior **NO-GO / NOT YET EVALUATED** disposition remains unchanged.

## Historical sovereign sample update — 2026-11-06

PR #60 adds one matched RBI T-bill auction cycle: notice, method, auction/settlement dates, full result, cut-off result and Table 218 all reconcile for 26-Nov-2025. This verifies one sample rule-based weighted-average NCB price input and exact source lineage. It does not establish complete historical paired coverage, actual retail fills, direct dated-bond cashflows, the strategy comparison, or an investable rolling return. Therefore the **NO-GO / NOT YET EVALUATED** conclusion is unchanged.


## Evidence update — candidate holdings and HDFCGOLD price history (2026-11-07)

Draft PR #64 consolidates an official HDFCGOLD daily-close archive (1,241 observations, 08-Nov-2021–06-Nov-2026) and official 30-Sep-2026 ICICI Gold/Silver holdings snapshots. The G5.4 candidate disposition now links the HDFCGOLD market-price history and the two later holdings snapshots separately from prior evidence. All reported candidate-register, independent-candidate-audit, lineage and source-inventory checks pass on PR #64 head `25be95f2c03ddd85cb6ecb27fcb71572509c2c89`; the PR remains draft and unmerged.

This closes only those bounded evidence increments. It does not produce a comparable execution-cost panel, direct sovereign cashflow path, after-tax candidate comparison, exact date-aligned joint history, investor-specific CPI result or calibrated probability. The October 6.94% GS 2036 terms/cutoff have since been source-qualified in draft PR #65 as detailed below; current execution price and investor-specific economics remain blocked. The decision remains **NO-GO / NOT YET EVALUATED**.

## Direct sovereign source-pair update — 2026-11-07

Draft PR #65 now retains the official October-specific Gazette reissue notice and RBI full auction result for 6.94% GS 2036 (ISIN `IN0020260025`). The Gazette terms confirm 11-May/11-Nov coupon dates, maturity on 11-May-2036, and accrued interest due through 18-Oct-2026 for 19-Oct settlement. The RBI result records weighted-average price/yield 96.93 / 7.3925%; cutoff price/yield 96.91 / 7.3955%. These are distinct auction values. RBI auction FAQ Q23 independently supports 30/360 accrued interest for a price-based reissue. The notice-specific amount ₹3.026611 per ₹100 is a convention-based calculation; exact retail settlement rounding remains unverified.

This supersedes the earlier statement that the October notice bytes and cutoff were unqualified. The new work qualifies the source pair and nominal coupon/redemption skeleton, not an executable quote, continuous traded-price history, investor tax/fee result, coupon reinvestment path, or direct-bond risk distribution. PR #65 remains draft and unmerged; consequently the 2036 source files are not yet in the main branch. Decision remains NO-GO / NOT YET EVALUATED.