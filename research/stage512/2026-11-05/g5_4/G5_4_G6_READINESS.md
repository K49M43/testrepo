# G5.4 candidate breadth and G6 entry assessment — 2026-11-05

## Decision

**G5 parent remains OPEN / BLOCKED. G6 is NOT READY TO START. Investment decision remains NO-GO.** This increment expands the screen to ten actual product/strategy hypotheses after excluding the benchmark, cash comparator and one specifically identified but currently blocked direct sovereign security. It establishes screen breadth only. It does not establish ten comparable, fully qualified investments or investor suitability.

## What changed

Five first-party product hypotheses were appended without rewriting the accepted G5.2/G5.3 registers: SBI Nifty 500 Index Fund Direct Growth; SBI Nifty 10 Year Benchmark G-Sec ETF; SBI CRISIL IBX Gilt Index – June 2036 Fund Direct Growth; HDFC Gold ETF; and SBI Gilt Fund Direct Growth. They broaden domestic equity, government-bond duration/target-maturity, active gilt, and gold exposure. Existing register remains the historical baseline. `candidate_expansion_v1.json` carries identity, exposure, dated evidence, known risks and explicit unknowns.

The refreshed official AMFI NAV snapshots were parsed against the existing named sample register. **44 of 44** matched by AMFI scheme code, ISO-normalized date, and decimal NAV. The 19–23 October raw response has a different SHA-256 from the prior snapshot. Sample values reconcile; the bytes are retained as a separate snapshot and neither the old hash nor source record is overwritten. This proves bounded sample consistency only.

The October AMFI TER workbook and three official factsheets are retained with byte lengths, hashes, source URLs and approximate local retrieval timestamps in `source_reacquisition_manifest.json`. TER values in the candidate descriptions are documented as source observations; an independent workbook parser/checksum audit is still required before those values can be treated as an accepted normalized fee ledger. The workbook opens as ZIP/XLSX but its worksheet dimension is absent to the existing read-only parser, so this pass does not pretend that independent row-level reconciliation succeeded.

## Candidate breadth

| Screen component | Count | Disposition |
|---|---:|---|
| Existing G5.2 register rows | 8 | Includes benchmark, cash comparator and one blocked direct security |
| New product hypotheses | 5 | Added in this append-only increment |
| Total register rows | 13 | Includes comparators and blocked direct security |
| Product hypotheses after the three exclusions | 10 | Meets the breadth floor; qualification is incomplete |

The products are not interchangeable. In particular, a G-Sec ETF or gilt mutual fund is not equivalent to owning a sovereign bond to maturity; NAV is not an ETF exchange execution price; an index TRI is not an investable product; and a factsheet YTM is a dated metric, not a forecast.

## G6 entry gate matrix

| Gate | Current status | Evidence needed to pass |
|---|---|---|
| Candidate screen breadth (10+) | **PASS, breadth only** | Ten identified product hypotheses; full comparable screening still pending |
| Candidate identity and dated evidence | **PARTIAL** | Complete identity, plan/option, holdings, fee and benchmark reconciliation for all candidates |
| TER raw source retention | **PASS, retained** | Independent robust parser and exact scheme/plan/date component reconciliation remains open |
| AMFI bounded NAV observations | **PASS, 44/44 re-reconciled** | Does not substitute for continuous point-in-time history |
| Qualified comparable historical return series | **BLOCKED** | Source-complete, date-aligned returns for all decision-relevant asset classes, with total-return treatment and survivorship/launch-date limits explicit; direct-GSec and bullion bridge especially unresolved |
| Equity–bond/gold/silver covariance and uncertainty | **BLOCKED** | Qualified common-date series, regime/subperiod sensitivity, uncertainty and stress validation |
| Investor-specific access/suitability/execution | **BLOCKED / UNCONFIRMED** | Current platform/product availability, executable prices/spreads/liquidity, constraints and suitability inputs; no account credentials or trades |
| Tax engine and lot-level liquidation | **BLOCKED / PROVISIONAL** | Close Sprint 1 unresolved loss allocation/surcharge composition convention; validate investor-year flows, lots, holding periods, fees and 2036 liquidation cases |
| Dated cashflow integration | **BLOCKED** | Mandate cashflow schedule integrated with candidate return paths and timing conventions; reconcile pre-tax/fee, after-tax nominal and real results |
| CPI base and real purchasing power | **BLOCKED / NOT INTEGRATED** | Audited linked official CPI, exact base-month/index linkage, forecast uncertainty and purchasing-power reporting |
| G3 hurdle/outcome and exit contracts | **PARTIAL** | Reconcile G3 pre-tax/fee outcome interface to after-tax/real cashflows, forced/flexible exit behavior, and shortfall definition |
| Independent end-to-end reproducibility and adverse cases | **BLOCKED** | Rerunnable evidence manifest/code/seeds, independent audit, stress/parameter/sequence/tax sensitivity, no fabricated probabilities |

## Minimum work before G6 starts

1. Independently parse the retained AMFI TER workbook, identify each candidate’s exact AMFI/NSDL code and plan, and reconcile BER + brokerage + transaction cost + statutory levies to Total TER.
2. Decide the G5 candidate universe and create candidate-by-candidate evidence disposition: qualified history, proxy-only, comparator, or excluded with reason. Do not count a name as a qualified history.
3. Close the unresolved Sprint 1 tax composition/loss-allocation defects and run dated investor cashflows through taxes/fees and plausible 2036 exit cases. Preserve any statutory uncertainty as an explicit model limitation.
4. Complete the official CPI base/linkage audit and quantify nominal versus real values.
5. Define and verify multi-asset source bridges and strict common-date return conventions before any covariance or probability calculation. Keep the government bond and bullion proxy limits visible.
6. Reconcile all of the above with G3 hurdle/outcome/exit contracts and pass independent rerun plus adverse-case review.

**G6 entry rule:** G6 may begin only after the required input contracts and validation gates above are explicitly accepted. This report does not authorize probabilistic success claims or investment implementation. No allocation recommendation is produced.
