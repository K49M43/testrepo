# G5 candidate disposition and initial comparison set

**As of 2026-11-05 · Research only · No ranking, allocation weights, suitability conclusion, or trade authorization**

## Classification rule

instrument-level research disposition only; INVESTABLE means a product identity/existence is supported by dated official disclosures, not that it is currently available, suitable, accessible through this investor's account, or authorized for purchase

## Disposition of 10 product hypotheses

| Candidate | Classification | Disposition | Fee evidence | Primary remaining blocker |
|---|---|---|---|---|
| MOTILAL_NIFTY500_ETF | INVESTABLE | RETAIN_AS_ALTERNATIVE; NOT_IN_INITIAL_NAV_PATH | Direct 0%; regular 0.39% (2026-10-31) | BLOCKED_EXECUTABLE_PRICE_PREMIUM_OR_MF_DEALING_TERMS_NOT_QUALIFIED |
| MOTILAL_NIFTY500_INDEX_FUND | INVESTABLE | RETAIN_IN_INITIAL_COMPARISON_SET | Direct 0.23%; regular 0.97% (2026-10-31) | BLOCKED_EXECUTABLE_PRICE_PREMIUM_OR_MF_DEALING_TERMS_NOT_QUALIFIED |
| LIC_GSEC_8_13_ETF | PROXY_ONLY | RETAIN_IN_INITIAL_COMPARISON_SET_AS_PROXY | Direct 0%; regular 0.17% (2026-10-31) | BLOCKED_EXECUTABLE_PRICE_PREMIUM_OR_MF_DEALING_TERMS_NOT_QUALIFIED |
| ICICI_GOLD_ETF | INVESTABLE | RETAIN_AS_ALTERNATIVE; DEFER_FULL_HISTORY | Direct 0%; regular 0.49% (2026-10-31) | BLOCKED_EXECUTABLE_PRICE_PREMIUM_OR_MF_DEALING_TERMS_NOT_QUALIFIED |
| ICICI_SILVER_ETF | INVESTABLE | RETAIN_IN_INITIAL_COMPARISON_SET | Direct 0%; regular 0.4% (2026-10-31) | BLOCKED_EXECUTABLE_PRICE_PREMIUM_OR_MF_DEALING_TERMS_NOT_QUALIFIED |
| SBI_NIFTY500_INDEX_FUND | INVESTABLE | RETAIN_AS_ALTERNATIVE; SHORT_HISTORY | Direct 0.34%; regular 0.81% (2026-10-31) | BLOCKED_EXECUTABLE_PRICE_PREMIUM_OR_MF_DEALING_TERMS_NOT_QUALIFIED |
| SBI_NIFTY10Y_GSEC_ETF | INVESTABLE | RETAIN_AS_ALTERNATIVE; DEFER_FULL_HISTORY | Direct 0%; regular 0.14% (2026-10-31) | BLOCKED_EXECUTABLE_PRICE_PREMIUM_OR_MF_DEALING_TERMS_NOT_QUALIFIED |
| SBI_GILT_JUNE2036_FUND | INVESTABLE | RETAIN_IN_INITIAL_COMPARISON_SET_AS_PROXY | Direct 0.28%; regular 0.49% (2026-10-31) | BLOCKED_EXECUTABLE_PRICE_PREMIUM_OR_MF_DEALING_TERMS_NOT_QUALIFIED |
| HDFC_GOLD_ETF | INVESTABLE | RETAIN_IN_INITIAL_COMPARISON_SET | Direct 0%; regular 0.59% (2026-10-31) | BLOCKED_EXECUTABLE_PRICE_PREMIUM_OR_MF_DEALING_TERMS_NOT_QUALIFIED |
| SBI_GILT_FUND | INVESTABLE | RETAIN_AS_ALTERNATIVE; DEFER_FULL_HISTORY | Direct 0.49%; regular 0.99% (2026-10-31) | BLOCKED_EXECUTABLE_PRICE_PREMIUM_OR_MF_DEALING_TERMS_NOT_QUALIFIED |

## Initial evidence comparison set

`MOTILAL_NIFTY500_INDEX_FUND`, `SBI_GILT_JUNE2036_FUND`, `LIC_GSEC_8_13_ETF`, `HDFC_GOLD_ETF`, `ICICI_SILVER_ETF`, `GOI_DIRECT_DATED_GSEC_718_2033`, `CASH_HOLD_91D_TBILL_ROLLING`. This is a comparison input set, not a portfolio selection. Direct GoI and rolling T-Bill remain blocked from numerical output until dated price/cashflow inputs exist. The Nifty TRI remains a separate rounded monthly benchmark. No weights are assigned.

## Cross-cutting gates

- Latest AMFI TER rows are audited as a snapshot; historical fees and all-in execution costs remain open.
- Candidate-specific tax classification, terminal-year tax, account access, settlement, and investor suitability are blocked for all actual products.
- Dated holdings coverage, stale snapshots, cash/derivative residuals, and unmatched identifiers remain governed by the G5.2 source evidence; missing weights are never converted to zero.
- ETF NAV is not traded price; fund NAV is not direct GoI cashflow; benchmark TRI is not an investable product return.

## Next decision

G5 closes only after the independent audit checks these classifications and the original acceptance gates. G6 fixture-first synthetic engineering may start. Decision-grade G6 and investment authorization remain NOT READY / NO-GO. See `g5_candidate_disposition_v1.json` for row-level identity, history, fee source hashes, holdings evidence, source references, and every explicitly blocked field.
