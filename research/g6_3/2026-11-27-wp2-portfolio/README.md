# G6.3 WP2 matched NAV replay and 2036 funding comparison

This increment reuses the frozen October 2026 funding convention. The initial contribution is ₹42 lakh, followed by ₹25,000 a month with a 10% increase after each 12 payments. The 120- and 122-payment cases contribute ₹89.81 lakh and ₹91.11 lakh in total. The dates, inflation base, allocation weights and exit policy are research conventions awaiting investor confirmation. [Funding contract](../../stage512/2026-11-04/g3_outcome_contract_v1.json) · [WP1 evidence](../2026-11-27-exact-date-coverage/README.md)

## What the 48 matched intervals show

The replay uses all 49 shared NAV endpoints from 31 October 2022 to 30 October 2026 across Motilal Nifty 500, LIC G-Sec, SBI June 2036, HDFC Gold and ICICI Silver. Each observed monthly move is applied once, in order, to the first 48 intervals of the illustrative October 2026 funding schedule. This places the contributions and taxes on the scenario's October 2026–October 2030 dates. Historical returns and actual historical taxes are distinct. The contributing portfolio totals ₹55.923 lakh at month 48. Both SBI accounting treatments share the same observed SBI NAV history.

| Gilt sleeve | Gold / silver weights | Implicit fund expenses reflected in NAV, before additional costs and investor tax | After modeled costs and tax | After-tax nominal XIRR |
|---|---:|---:|---:|---:|
| LIC | 15% / 0% | ₹83.94 lakh | ₹79.87 lakh | 10.65% |
| SBI June 2036 | 15% / 0% | ₹84.24 lakh | ₹80.10 lakh | 10.74% |
| LIC | 10% / 5% | ₹84.81 lakh | ₹80.62 lakh | 10.94% |
| SBI June 2036 | 10% / 5% | ₹85.11 lakh | ₹80.85 lakh | 11.03% |

Equity is 65% and gilt is 20% of each contribution. There are no intra-horizon rebalancing sales. In the gold-only replay, SBI leads LIC by ₹23,315 after modeled costs and tax. Replacing 5% gold with silver increases the replay endpoint by about ₹75,100 for either gilt. That comparison uses NAVs and hypothetical dealing costs and does not qualify silver for execution. Prior rolling-block and adverse tests show the result can reverse. [Silver sensitivity audit](../../stage512/2026-11-25/g6_3/icici_silver_etf_source_gate/SILVER_NAV_COMPARISON.md)

## Separate 2036 deterministic scenarios

The 48 historical moves stop at month 48. The 120/122-payment results independently apply predeclared annual growth assumptions to the 65% equity, 20% gilt and 15% gold baseline. Each contribution buys the assigned sleeves. The final contribution stays in cash at the endpoint and is still included in the funding total. October and December 2036 are full-liquidation illustrations with 120 and 122 payments respectively. They do not imply the investor chose between them.

| Scenario | Equity NAV growth | Gold NAV growth | LIC NAV growth | Gross reinvestment | SBI annual fee |
|---|---:|---:|---:|---:|---:|
| Lower growth | 4% | 2% | 4% | 2% | 0.50% |
| Reference | 8% | 5% | 6% | 4% | 0.28% |
| Higher growth | 12% | 8% | 7% | 6% | 0.28% |

Equity, gold and LIC growth assumptions are NAV-basis rates with fund expenses implicit. SBI uses the separate-accrual and accrual-in-mark gross annual equivalents from the holdings audit with zero return on residual signed assets in both. The annual rates are applied as constant paths to each lot until the 30 June 2036 maturity, with TER applied once. This is a shortcut for future NAV paths and does not recreate SBI's future rebalancing or accrued interest per lot. The model applies the disclosed short-holding exit load as a sensitivity at maturity, assumes seven calendar days before redemption cash can earn reserve interest and routes the gilt allocation from maturity onward to reserve cash. The seven-day lag is illustrative. The scheme describes proceeds within three working days subject to its terms. [SBI scheme document](https://www.sbimf.com/docs/default-source/sif-forms/sid---sbi-crisil-ibx-gilt-index---june-2036-fund.pdf) · [SBI accrual and yield audit](../direct_gsec_2036/2026-11-27-sbi-valuation/README.md)

The 6.94% direct bond buys whole units up to nominal maturity. For every hypothetical purchase the model calculates a clean price from contractual cashflows and a constant 7.3158% nominal yield, adds accrued interest and applies 10 bp entry friction. The yield anchors to the November RBI auction. The model uses the clean amount as gain basis, charges ordinary-rate tax on gross coupons and reinvests net coupon proceeds in a scenario cash reserve. The contractual dates exclude later holiday or settlement adjustments. At maturity par and the final coupon flow to reserve, and new gilt funding stays there. Assume no reserve interest funded by same-day T-bill payments. [Direct bond and tax assumptions](../direct_gsec_2036/2026-11-26-gilt-comparison/README.md) · [November primary auction](../direct_gsec_2036/2026-11-13/README.md)

### 120-payment reference results

These are conditional wealth values at modeled liquidation using 6% annual inflation, a 30% ordinary marginal rate, 4% cess, no surcharge and a fully available section 198 annual threshold. The CPI calculation uses the assumed October 2026 reference.

| Gilt route | Before separately modeled costs and investor tax | After costs before investor tax | After modeled tax | Real after tax | Gap to ₹90 lakh real floor |
|---|---:|---:|---:|---:|---:|
| LIC NAV assumption | ₹149.50L | ₹149.40L | ₹140.06L | ₹78.21L | ₹11.79L |
| Direct GoI 6.94% | ₹150.40L | ₹150.33L | ₹140.24L | ₹78.31L | ₹11.69L |
| SBI separate accrual | ₹150.30L | ₹149.68L | ₹140.25L | ₹78.31L | ₹11.69L |
| SBI accrued interest included in mark | ₹150.66L | ₹150.03L | ₹140.49L | ₹78.45L | ₹11.55L |

The SBI separate-accrual route leads the direct bond by ₹892 in modeled nominal after-tax wealth in the 120-payment reference case. The direct bond leads SBI separate accrual by ₹53,619 in the lower-growth case, and LIC leads in the higher-growth case. At 6% inflation the full grid spans ₹62.24–₹99.34 lakh real after modeled tax. The 122-payment reference results are ₹78.99–₹79.19 lakh real. These are scenario outcomes with no probability weights. A higher-growth outcome can cross the floor. The reference outcomes leave a material shortfall.

## Cost, tax and settlement boundaries

- Fund and ETF growth exposures are modeled with fractional units. Equity and SBI apply 0.005% subscription stamp duty. Motilal equity uses the disclosed short-window load and assumed applicable redemption STT. Hypothetical ETF friction is 10 bp per side and assumes no specific execution route, lot rounding, spread or current quote. With no remaining holding period at the final date, the terminal SIP stays in cash. Observed NAVs already include TER. [Motilal Oswal scheme terms](https://www.motilaloswalmf.com/content/dam/motilal-mf/downloads/mf/sid/2025/nov/08f19-sid_motilal-oswal-nifty-500-index-fund-.pdf)
- Gain by acquisition lot uses the appropriate modeled disposal date and a strict greater-than-12-calendar-month test for the included equity and listed assets. Equity sections 196/198 assume continuing eligibility and STT, with the section 198 threshold applied once across modeled qualifying equity gains in the exit year. Listed metals and eligible direct bond gains use section 197 for long holdings and ordinary marginal rates for short holdings. The debt funds use section 76 where the statutory composition test remains satisfied. Separate positive gains and losses are tracked. The scenario assigns zero benefit to losses and does not assert investor carryforward, available deductions, or actual income thresholds. The second tax case uses hypothetical 10% surcharge and an already-used equity threshold. It is a sensitivity and does not recompute the taxpayer-level surcharge, rebate or marginal-relief thresholds. [Enacted Income-tax Act](https://www.incometaxindia.gov.in/documents/d/guest/income_tax_act_2025_as_amended_by_fa_act_2026-pdf) · [Finance Act 2026](https://www.incometaxindia.gov.in/documents/d/guest/finance-act-2026-pdf-1)
- Nominal XIRR uses actual calendar days on the funding convention and the endpoint liquidation value. XIRR has no outside contribution for tax. The after-tax line reflects modeled taxes deducted from the portfolio on income/exit paths, including their effect on subsequent reserve growth. Reserve growth stands in for a cash allocation. Neither its available rate nor actual exit settlement is established. Table values do not establish settled personal wealth. Real values use 4%, 6% and 8% compound inflation sensitivities. Exact investor inputs, product execution, disposition expenses and losses, partial/flexible exits, source-specific forward returns and independent portfolio assurance remain open for full WP2.

## Reproduction

```text
python decision/audit_g6_3_exact_date_coverage.py --check
python decision/g6_3_wp2_portfolio.py --check
```

The [input record](inputs_v1.json) defines the scenarios. The [frozen output](portfolio_v1.json) reports 4 matched NAV replays and 48 forward cases with input hashes, funding totals, gain buckets, lot counts, contributions held in reserve, stage-by-stage wealth and before/after-tax XIRRs. No random inputs are used. The live quote and paid Silver ETF history remain deferred. RBI T-bill payment timing stays open. G6.3 remains open and investment authorization remains **NO-GO**.
