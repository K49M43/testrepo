# G6.3 Silver NAV comparison

**Evidence cutoff** 30 October 2026. **Run date** 25 November 2026. **Disposition** `PROVISIONAL_NAV_COMPARISON_ONLY`.

The 5% switch from gold to silver helped in some historical replays and hurt in others. The shortfall improvement was modest in the worst observed replay and reversed in a hypothetical joint crash. This screen does not justify buying daily NSE history now. Keep the direct ETF outside the executable shortlist pending execution evidence and retain silver in the research universe. The Fund of Fund remains a separate route to evaluate if a larger or more robust benefit emerges. [Issuer Fund of Fund page](https://www.icicipruamc.com/mutual-fund/fund-of-funds/silver-etf-fund-of-fund/1837)

## Same dates, same cashflows

- The G5.4 checker reconstructed and hash-verified the four retained AMFI NAV histories. The inputs are Motilal Oswal Nifty 500 Index Fund Direct Growth (`147625`), SBI CRISIL IBX Gilt Index June 2036 Fund Direct Growth (`150681`), HDFC Gold ETF (`113049`) and ICICI Prudential Silver ETF (`149464`). The comparison begins after the documented HDFC Gold split. It uses NAV changes with fund expenses embedded and makes no exchange-return or total-return claim beyond the reported NAVs. [Source audit](README.md) · [Gold corporate-action audit](../../../2026-11-06/hdfcgold_execution_evidence/README.md)
- Select the latest **common observed NAV date** each calendar month from October 2022 to October 2026. Ten individual month-end labels otherwise had different observation dates. The 49 shared endpoints give 48 contiguous monthly intervals with both endpoints matched. The common dates support retrospective NAV analysis. Intra-day valuation clocks and executable marks are separate evidence.
- Compare **65% equity / 20% gilt / 15% gold** against the mandate's **65% equity / 20% gilt / 10% gold / 5% silver** research challenger. Allocate the same ₹42 lakh and 120 end-of-month contributions at the stated weights, starting at ₹25,000 and stepping up 10% after every 12 payments. Hold each sleeve between purchases and liquidate at the model endpoint. This isolates replacing gold with silver. Funding silver from a different sleeve can change the result.
- For each of the 37 overlapping 12-interval historical blocks, replay all four NAV paths together at the start and at the end of an illustrative 120-month horizon. The other 108 months use the same **8.2536% annualized nominal** return for every sleeve, the G3 arithmetic hurdle for a ₹90 lakh real target at the 6% inflation scenario. This is a conditional sequence test. It assumes equal asset returns outside the replay and establishes neither a forward return estimate nor odds of meeting the target.
- Subtract an illustrative incremental silver cost of 0, 25, 50, 100 or 200 basis points from each purchase budget and the same proportion from final silver proceeds. The tested cost is a haircut on the silver sleeve. Actual candidate costs and taxes require separate inputs. These pre-tax results use the ₹90 lakh figure as a diagnostic threshold. The mandate's floor requires net accessible after-tax wealth.

## Conditional results

Differences are in 2026 rupees at the 6% inflation scenario. Positive terminal differences favor the silver challenger.

| Historical block placement | Zero-cost replays with higher wealth | Median difference, 0 bps | Median difference, 100 bps per side | Worst zero-cost shortfall, baseline → silver |
|---|---:|---:|---:|---:|
| First 12 months | 20 of 37 | +₹6,519 | −₹3,222 | ₹5.03 lakh → ₹4.90 lakh |
| Last 12 months | 20 of 37 | +₹10,416 | +₹625 | ₹8.22 lakh → ₹7.99 lakh |

At zero cost, silver reduced the shortfall in five replay blocks and increased it in three, for each placement. In the worst historical exit replay (31 October 2025 to 30 October 2026), the reduction was ₹23,229 at zero cost and ₹3,462 at 200 bps per side. The median terminal difference turned negative for both placements at 200 bps. These bps are sensitivities. The full results include the breakeven cost for each zero-cost replay where silver increased terminal wealth.

Two challenges matter more than the favorable aggregate count:

- Of the 27 blocks ending in 2025 or earlier, silver increased terminal wealth in only 10, even at zero cost. The median exit-replay difference in that subset was −₹12,852. This sensitivity detects dependence on the most recent part of the sample, which also spans fund benchmark and valuation changes. It cannot attribute the change to either policy or market returns.
- In a separate hypothetical final-year shock of equity −25%, gilt −5%, gold −10% and silver −30%, the pre-tax real shortfall increased from ₹21.93 lakh to ₹22.74 lakh with the switch at zero trading cost. The synthetic shock probes protection when both metals fall and silver falls further.

One strong replay improved terminal wealth by ₹6.25 lakh, but large positive effects in individual windows do not establish robust floor protection. The 37 blocks share data, and the four funds overlap for four years. A wider regime check would require a separately qualified bullion benchmark and a stated link to the product since inception. Keep these results separate from any 2036 probability model.

## Reproduction and gate status

```powershell
py -B decision/audit_g6_3_silver_nav_comparison.py --check
```

The [frozen result](silver_nav_comparison_v1.json) records source segment hashes, matched dates, assumptions and each replay. The identical-return control reconciles to the existing G3 hurdle. A separate units-per-purchase calculation reconciled all 370 block-placement-cost outcomes to rounding precision. The experiment advances the candidate screen. Licensed exchange history, actual costs, independent decision validation and RBI payment timing remain open. Investment authorization remains **NO-GO**.
