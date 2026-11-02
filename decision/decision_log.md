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
