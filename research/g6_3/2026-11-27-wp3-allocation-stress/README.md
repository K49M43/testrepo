# G6.3 WP3 allocation stress comparison

The [protocol](protocol_v1.json) was frozen at commit `9cb2a3b` before generating results. It compares defensive **35/50/15**, diversified **65/20/15**, and growth **80/10/10** equity/gilt/gold funding policies. Each invests ₹42 lakh initially and ₹25,000 monthly with a 10% annual step-up, using the frozen WP2 calendar. The weights apply to new funding. Holdings drift with returns and are liquidated under the applicable policy. The grid carries LIC G-Sec ETF, the direct 6.94% GoI 2036 bond, and both SBI June 2036 gilt accrual cases. [Parent scope and acceptance gates](https://github.com/K49M43/testrepo/issues/44)

## Forward stress results

Ranges span the four gilt routes for each allocation. Terminal wealth is after modeled costs and tax and in the October 2026 purchasing-power convention. The scenarios use 6% compound inflation except the low-growth/high-inflation case at 8%. Values are lakh rupees.

| Stress | Defensive | Diversified | Growth |
| --- | ---: | ---: | ---: |
| October reference | 72.70–73.38 | 77.37–77.64 | 79.66–79.79 |
| Low growth and 8% inflation | 50.63–53.66 | 51.47–52.55 | 52.06–52.60 |
| 30% equity shock in month 12 | 67.86–68.54 | 68.37–68.64 | 68.59–68.72 |
| Same equity shock in month 115 | 64.98–66.04 | 63.02–63.27 | 62.00–62.13 |
| Joint shock in month 96, October exit | 64.42–67.81 | 66.58–67.94 | 67.63–68.31 |
| Same joint shock, December exit with two additional SIPs | 65.08–68.39 | 67.33–68.65 | 68.42–69.08 |
| Higher costs, tax and SBI cash release lag | 71.93–72.84 | 76.25–77.15 | 78.64–78.86 |

Across the reference cases, after-tax nominal wealth spans ₹130.20–₹131.42 lakh for defensive, ₹138.55–₹139.04 lakh for diversified and ₹142.66–₹142.90 lakh for growth. The best real reference case still falls ₹10.21 lakh short of ₹90 lakh. None of the 84 forward scenarios reaches the floor or the ₹1 crore stretch. The scenarios are design cases with no assigned probabilities.

The late equity shock reverses the reference ordering. Defensive ends ₹2.98–₹3.99 lakh above growth on a matched-route basis, with 11.62–16.63% modeled monthly drawdown versus 24.78–25.40% for growth. Both shock timings apply the same permanent 30% reduction to the equity level against the reference path. The later shock gives the plan fewer remaining purchases at the lower mark. The joint shock combines weaker equity and gold prices with higher yields. Its worst defensive outcome comes from the LIC duration sleeve. The direct bond reprices to a 1.50 percentage-point higher yield from the shock date, with its contractual coupons and par held fixed. SBI's hypothetical NAV shock tapers as maturity approaches. The small benefit from December exit combines extra time and two SIPs.

## What the observed NAV replays add

All source dates and jointly observed endpoints come from WP1. The 85-interval LIC core tape shows monthly drawdowns of 13.90%, 16.71%, and 21.64%, respectively. On the common 48-interval tape, diversified has the highest ending wealth in both gilt variants. Growth leads on both first-half comparisons, with the SBI growth and diversified figures close, and defensive leads on both last-half comparisons. Because the same two SBI accounting cases share one realized NAV tape, the historical SBI replay uses that tape once. Both accrual cases remain distinct in the forward grid.

The 5% silver-for-gold swap on the 48-interval tape raises real terminal value by roughly ₹0.58–₹0.59 lakh while increasing observed-tape drawdown by roughly 4.56–4.65 percentage points. Relative performance across these short samples does not establish future ranking or tradable ETF performance.

## Measurement, audit and evidence limits

- Drawdown measures month-end marked wealth after removing external funding flows. It includes modeled dealing costs, taxes charged on their simulated dates, and net unsettled receivables in marked wealth. The WP2 ledger prevents use of those receivables before release. It covers month-end observations, so losses inside a month can be larger. Late tax set-asides can contribute to drawdown.
- The forward paths inherit WP2's hypothetical taxpayer context, reserve, tax rules, cost and settlement assumptions. The adverse-cost case widens modeled ETF friction, raises both modeled external income and cess, raises direct-bond friction, and stresses SBI TER and release lag. Product access, settlement, personal tax and CPI base confirmation remain open.
- The stress grid exposed a sub-paisa rounding overshoot when several losses hit the same gain. Allocation and validation now use enough precision to sum the input decimals exactly. All 50 WP2 results reproduced with identical financial outputs at reported precision. Event digests changed to reflect the exact ledger arithmetic. The prior record is preserved in Git at `73e3802`.
- The audit verifies the frozen protocol hash, grid completeness, date guards, drawdown and settlement examples, the direct-bond coupon and yield invariants, independently calculated real and shortfall amounts, XIRR residuals and the four WP2 diversified reference anchors.
- The deterministic comparison passes within this scope. Walk-forward forecasting, parameter and model uncertainty, and tail calibration remain separate. With only 85 contiguous monthly observations for the core and 48 for the common SBI panel, the analysis supports conditional historical replay and stress findings. It does not establish a calibrated 2036 probability.

Live direct-bond quote and paid Silver ETF history remain deferred. RBI T-bill payment timing remains open and T-bill rollover is excluded. The scenarios support a conditional trade-off discussion. G6.3 remains open and investment authorization remains **NO-GO**.

## Reproduce

```text
python decision/g6_3_wp3_allocation_stress.py --check
python decision/audit_g6_3_wp3_allocation_stress.py
```

[Frozen case results](results_v1.json) include the source manifest, 84 forward rows and 23 NAV replays. Python 3.13 and the standard library reproduce the artifact without random draws.
