# 2036 decision log

## 2 November 2026 — Current authorization: NO-GO

**Decision:** No portfolio implementation or investment action is authorized by this research. Continue decision-grade analysis.

**Evidence available:**

- Official LIC MF Nifty 8–13 Yr G-Sec ETF NAV backfill and source-segment audit passed for 2,867 observations, 26 December 2014–30 October 2026; see `research/stage512/2026-11-02/stage512_R93_live_backfill_and_129m_audit.md`.
- Strictly endpoint-date-aligned Nifty 500 TRI / LIC ETF NAV proxy comparison passed for 117 of 129 monthly intervals, with observed correlation 0.022541; see `research/stage512/2026-11-02/stage512_R93_live_backfill_and_129m_audit.md` and `research/stage512/data/r9_nse_gsec_129m_source_bridge.json`. This is a rolling gilt ETF proxy, not a direct G-Sec total-return index.
- The 120/122-contribution arithmetic hurdle baseline is published in `research/stage512/2026-11-02/cashflow_hurdle_baseline.md`. It is pre-tax and pre-cost, assumes 4/6/8% CPI sensitivities, and does not establish attainable returns.
- An initial source-based Act 2025 / Finance Act 2026 investment-tax map is published in `decision/tax_rules_asof.md`. There is no qualified lot-level tax engine or after-tax real-wealth result yet.

**Why the gate stays closed:** the planned ₹90L floor and ₹1Cr stretch are framed in 2026 purchasing power, but the CPI anchor is still assumed rather than selected from the latest released observation; instrument-level returns, fees, trading friction, tax lots and terminal exit taxation have not been integrated; future 2036 tax law is uncertain; and the investor has not confirmed actual payment/exit dates or approved a portfolio.

**Next evidence that can change this status:** a reproducible deterministic cashflow/tax ledger, checked against independent examples; a source-pinned CPI origin and deflator; dated executable candidate terms; and a falsification review of goal feasibility and downside risk. A successful model or source gate alone will not change this authorization.

## 2026-11-25 — Defer paid Silver ETF history pending portfolio materiality

The [G6.3 NAV comparison](../research/stage512/2026-11-25/g6_3/icici_silver_etf_source_gate/SILVER_NAV_COMPARISON.md) isolated the mandate's 5% gold-to-silver switch over 48 matched monthly intervals. The worst pre-tax real shortfall in the historical exit replays improved by ₹23,229 before trading costs. In the hypothetical joint crash it widened by ₹81,321. Keep silver as a research candidate, defer paid traded history and revisit the ETF or Fund of Fund route if further evidence shows material benefit after costs and taxes. RBI payment timing remains open. Investment authorization remains **NO-GO**.

## 2026-11-25 — Second primary price for direct 6.94% GS 2036

The [November auction reconciliation](../research/g6_3/direct_gsec_2036/2026-11-13/README.md) adds a ₹97.46 weighted clean price and 7.3158% quoted nominal yield, compared with October's ₹96.93 and 7.3925%. Keep the May 2036 bond in research. A fresh price for the investor's lot remains necessary to compare its entry economics. Leave exact debit, coupon reinvestment and post-maturity cash deployment unqualified. Investment authorization remains **NO-GO**.

## 2026-11-25 — Direct bond exchange route verified, fresh quote pending

The [read-only retail check](../research/g6_3/direct_gsec_2036/2026-11-25-retail-quote/README.md) verifies the NSE `GS` listing and a displayed offer sufficient for 100 units. Refreshing the public book did not yield a newer timestamp. Keep the direct bond in research until current broker depth, account access and all-in charges are verified. Investment authorization remains **NO-GO**.

## 2026-11-26 — Compare the sovereign bond and target-maturity fund before seeking a quote

The [comparison](../research/g6_3/direct_gsec_2036/2026-11-26-gilt-comparison/README.md) tested 504 scenarios on the same ₹1 lakh budget and 30 June 2036 valuation date. Preserve both candidates. The reference SBI case leads by ₹10,800 after tax, and the bond leads under some lower fund-growth assumptions. Defer a live quote until the investment comparison requires it. Paid Silver ETF history remains deferred, the RBI T-bill timing issue remains open, and investment authorization remains **NO-GO**.

## 2026-11-26 — Challenge the June 2036 fund hurdle using official holdings

The [SBI holdings and cashflow audit](../research/g6_3/direct_gsec_2036/2026-11-26-sbi-holdings/README.md) verified a 95.39% holding in IN0020220029 and qualified its 20 nominal coupons and May 2036 par repayment at snapshot quantity. At 4% reinvestment the frozen case spans 6.52%–6.79% gross, either side of the 6.61% hurdle. Keep both candidates. The securities disclosure leaves the accrued-interest and reported-YTM reconciliation open. Live quote and paid Silver ETF history remain deferred, the RBI T-bill payment timing gate remains open, and investment authorization remains **NO-GO**.

## 2026-11-27 — Prefer separate SBI gilt accrual for research

The [valuation audit](../research/g6_3/direct_gsec_2036/2026-11-27-sbi-valuation/README.md) supports a clean mark with separate accrual using audited scheme precedent and September and October price-yield diagnostics. The exact October accounting and pricing cutoff remain unverified. Carry both cases. At 4% reinvestment and 0.28% TER the supported treatment gives SBI a ₹1,076–₹1,085 after-tax edge per ₹1 lakh in the common-date scenario. Lower modeled reinvestment or higher fees can reverse that edge. Investment authorization remains **NO-GO**.

## 2026-11-27 — Qualify matched-date windows for G6.3 research

The [WP1 audit](../research/g6_3/2026-11-27-exact-date-coverage/README.md) maps the ten G5 hypotheses, three sovereign/reserve comparisons and the Nifty benchmark to their defensible uses. The largest product-only three-sleeve set has 85 contiguous matching NAV intervals. The SBI gilt mix has 48 on common observed dates and 31 if every product uses its own last date. Carry both SBI forward accounting cases. Historical research coverage and conditional forward cashflows support the next deterministic comparison. Investment authorization remains **NO-GO**.

## 2026-11-27 — Run the funded 2036 portfolio scenarios

The [WP2 portfolio comparison](../research/g6_3/2026-11-27-wp2-portfolio/README.md) carries both SBI accrual cases into the full funding fixture and retains LIC and the direct GoI bond. At 6% illustration inflation and 120 payments, the reference cases deliver ₹78.21–₹78.45 lakh modeled real after-tax wealth, with a ₹11.55–₹11.79 lakh shortfall. The better-supported SBI accounting case leads the direct bond by only ₹892 nominal after tax in that reference case. The lower- and higher-growth cases change the order. Keep all routes as research candidates and leave full WP2 and G6.3 open. Investment authorization remains **NO-GO**.

## 2026-11-27 — Independently reconcile dated WP2 outcomes

The [dated reconciliation](../research/g6_3/2026-11-27-wp2-dated/README.md) exercises the cash release and fiscal-year boundaries, a 25% early sale and ₹5 lakh withdrawal, annual incremental tax under a hypothetical taxpayer profile, loss offsets, withholding credits and a tax-policy stress. The dated 120-payment full exits deliver ₹77.37–₹77.64 lakh real at 6% inflation after costs and modeled tax. The deterministic research scope passes independent reconciliation. Keep portfolio ranking conditional and retain the personal and executable evidence blocks in [issue #44](https://github.com/K49M43/testrepo/issues/44). WP3 probabilities remain unqualified, and investment authorization remains **NO-GO**.

## 2026-11-27 — Compare three allocations under a frozen stress protocol

The [WP3 comparison](../research/g6_3/2026-11-27-wp3-allocation-stress/README.md) adds 84 forward cases and 23 exact-date NAV replays. Growth leads the reference paths at ₹79.66–₹79.79 lakh real. Defensive leads after a late equity shock, with ₹64.98–₹66.04 lakh real versus ₹62.00–₹62.13 lakh for growth. The risk trade-off is conditional on instrument, stress and exit. Keep all three mixes in research, retain both SBI accrual cases, and require additional statistical assurance for probabilities and further evidence for execution. Investment authorization remains **NO-GO**.
