# Sprint 1 — Investor input worksheet

**Status:** Blank intake template prepared; no new investor values supplied or inferred
**Purpose:** identify the facts required to replace synthetic dates, instruments, costs, and tax inputs with an investor-specific event ledger. This worksheet does not qualify a result or authorize a trade.

## Privacy and completion

The repository is public. Do not enter investor name, account number, broker statement, tax return, bank details, credentials, or other identifying documents here. Keep actual personal amounts and source documents in a private user-controlled record. If inputs are later provided for modeling, use only the minimum necessary figures and do not commit them to this repository.

For each response, record the value, who confirmed it, confirmation date, source or basis, and whether it is a fact, an assumption, or still unknown. Leave unresolved items blank. Do not replace blanks with the research fixture defaults.

## Existing declarations to reconfirm only if changed

The mandate already records: ₹42,00,000 available initial capital; ₹25,000 initial monthly contribution with 10% annual step-up; no liabilities; no current portfolio-income need; no expected funding interruption; Indian tax residence and current new regime with approximate 30% marginal ordinary-income slab; Groww as broker; and the ₹90 lakh real-after-tax floor / ₹1 crore stretch objective in 2026 purchasing power. See `docs/INVESTMENT_DECISION_MANDATE_2036.md`. These declarations are not exact trade dates, a personal tax computation, or risk-tolerance approval.

If any declaration changed, identify the field and updated value privately. Do not repeat unchanged personal facts in this public file.

## 1. Dated contribution and goal schedule

| Required input | Investor response | Confirmed on / source | Status |
|---|---|---|---|
| Date the initial ₹42 lakh is available to invest |  |  | UNKNOWN |
| Initial investment execution date or permitted execution window |  |  | UNKNOWN |
| First monthly contribution date |  |  | UNKNOWN |
| Monthly contribution timing and holiday/weekend treatment |  |  | UNKNOWN |
| Whether the 10% step-up remains every 12 paid contributions |  |  | UNKNOWN |
| Final planned contribution date / contribution count |  |  | UNKNOWN |
| Measurement or withdrawal month(s) in calendar 2036 |  |  | UNKNOWN |
| Full liquidation, partial liquidation, or flexible exit policy |  |  | UNKNOWN |
| Need for cash withdrawals before 2036 |  |  | UNKNOWN |

## 2. Risk, liquidity, and account constraints

| Required input | Investor response | Confirmed on / source | Status |
|---|---|---|---|
| Maximum tolerable peak-to-trough portfolio loss (₹ or %) |  |  | UNKNOWN |
| Loss duration / recovery period the investor can tolerate |  |  | UNKNOWN |
| Any liquidity reserve or minimum balance outside this portfolio |  |  | UNKNOWN |
| Account type, ownership, or product restrictions relevant to eligibility |  |  | UNKNOWN |
| Constraints on direct bonds, funds, ETFs, demat holdings, or order sizes |  |  | UNKNOWN |

## 3. CPI and real-value anchor

| Required input | Investor response | Confirmed on / source | Status |
|---|---|---|---|
| Purchasing-power base month for the ₹90 lakh / ₹1 crore objectives |  |  | UNKNOWN |
| Preferred official CPI series / geography / population definition, if different from the mandate |  |  | UNKNOWN |
| Whether to compare several 2036 exit months instead of one fixed month |  |  | UNKNOWN |

The current CPI research series is provisional for investor use. Do not report real wealth until its official source vintage is qualified and the anchor and cashflow dates are aligned.

## 4. Candidate holdings and transaction events

Complete one row per actual holding or intended instrument after the candidate screen. Do not substitute a benchmark, ETF NAV proxy, or synthetic fixture for a purchased security.

| Holding/event | Issuer / AMC / exact product name | ISIN / scheme / security ID | Route and account eligibility | Acquisition date | Units / face value | Price / accrued interest | Source and as-of | Status |
|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  | UNKNOWN |

Record all reinvestments and disposals as separate dated events, linked to the original lot. For a direct bond, also record coupon rate, coupon dates, maturity, purchase yield/price, settlement date, accrued interest, and whether principal will be held to maturity or sold earlier.

## 5. Fees and execution costs

| Cost field, by product and event | Investor response / source | Status |
|---|---|---|
| Brokerage and order charges |  | UNKNOWN |
| Exchange, clearing, STT, GST, stamp duty, and other statutory levies |  | UNKNOWN |
| Demat / DP debit or custody charges |  | UNKNOWN |
| Exit load, redemption fee, bid-ask spread, premium/discount, or market impact |  | UNKNOWN |
| Product expense already embedded in NAV or yield |  | UNKNOWN |
| Deductible transfer expenses and source evidence |  | UNKNOWN |

Distinguish costs already reflected in NAV/yield from separately charged amounts; do not subtract an embedded cost a second time.

## 6. Tax facts needed for an investor-specific calculation

Actual tax details are sensitive. Keep the completed figures outside the public repository. The ledger needs the following by relevant tax year, with source or confirmation date:

- Tax residence and taxpayer type; chosen tax regime for each modeled year; any regime change expected or elected.
- Other ordinary income and dividend income that affects marginal slabs, rebates, surcharge, and cess.
- Capital gains or losses from outside the modeled portfolio; loss carry-forwards, set-offs, and other relevant tax credits.
- Taxable distributions, coupons, withholding/TDS credits, and any advance-tax cashflows already paid or expected.
- Deductions/rebates and other facts that materially affect the applicable computation.
- For each instrument/lot: statutory classification, acquisition date, holding period, STT/security eligibility where applicable, and supporting product/legal evidence.
- Which tax year and tax-law vintage should apply to each modeled transaction. Future-year law must remain an explicit scenario until enacted and revalidated.

| Tax year | Regime / taxpayer status | Other income / gains / losses / credits supplied privately? | Source date | Status |
|---|---|---|---|---|
|  |  |  |  | UNKNOWN |

## 7. Independent tax review and sign-off

| Review field | Value / evidence | Status |
|---|---|---|
| Worked example reviewed by a qualified independent tax professional |  | NOT PROVIDED |
| Review scope includes current statutory treatment, instrument eligibility, losses/set-offs, and rounding |  | NOT PROVIDED |
| Review date, reviewer qualification, and recorded comments |  | NOT PROVIDED |
| Outstanding reviewer findings and disposition |  | NOT PROVIDED |

No reviewer has been contacted. This worksheet does not authorize contact; the investor must separately arrange and provide any review evidence.

## Acceptance impact

| Gate | Input needed | Current status |
|---|---|---|
| Exact dated cashflow ledger | Sections 1 and 4 | OPEN — synthetic dates only |
| Candidate-specific nominal results | Sections 3–5 | OPEN — product terms, dates, and costs unconfirmed |
| Investor-specific after-tax result | Section 6 plus qualified review in section 7 | OPEN — no personal computation qualified |
| Real purchasing-power result | Section 3 plus qualified CPI vintage and dated flows | OPEN — no investor-aligned CPI anchor |
| Investment authorization | All applicable gates, suitability, and investor approval | **NO-GO** |
