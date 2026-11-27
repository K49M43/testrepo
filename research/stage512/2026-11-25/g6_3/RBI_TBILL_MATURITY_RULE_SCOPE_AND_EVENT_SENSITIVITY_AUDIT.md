# RBI T-bill holiday-maturity rule scope and event sensitivity

**Audit date:** 2026-11-25
**Scope:** clarify the source scope of the holiday-maturity rule and map the four affected 91-day T-bill events to the retained auction panel.
**Decision status:** `NO-GO`; actual T-bill holiday redemption and proceeds-credit timing remain unqualified.

## Finding

The retained RBI Government Securities primer defines T-bills as 91-, 182-, and 364-day discounted instruments redeemed at face value. The same page contains the statement that redemption proceeds are paid on the previous working day when maturity falls on a Sunday or holiday. On the page, however, that sentence follows the subsection headed **Dated G-Secs**. The captured passage does not say that this adjustment applies to T-bills. The 2018 GoI general notification for T-bills is linked from RBI's [notification page](https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=11250&Mode=0), but its linked attachment triggered a human-verification challenge in the browser tool. Its raw bytes have not been retained; no access control was bypassed.

The 2025 [Gazette of India general notification](https://egazette.gov.in/WriteReadData/2025/261972.pdf) expressly covers Treasury Bills and says it supersedes the two 2018 general notifications. Its general repayment clause says securities are repaid on the redemption date specified in the specific notification; it does not state a holiday adjustment. This later notification does not by itself establish the terms or actual payment dates for bills issued in 2024. The browser-accessible Gazette text was not captured as repository raw bytes, so it is not treated as a hashed qualification source.

Therefore the RBI source package supports a **conditional previous-day sensitivity**, not a T-bill-specific maturity rule. The official Mumbai holiday matrix remains a bank-holiday source, not a complete T-bill operations calendar. RBI's 2023-09-29 G-Sec market-open exception is retained separately and prevents mechanically equating every listed holiday with a market closure.

## Four event sensitivity

Each nominal maturity is calculated from the contemporaneous RBI notice's issue/settlement date plus 91 calendar days. For the sensitivity only, the candidate prior date is the preceding weekday that is not listed in the captured Mumbai holiday matrix. The next auction is selected strictly after each date; same-day redemption proceeds are not assumed to fund an auction.

| Nominal maturity | RBI Mumbai holiday | Conditional prior date | Positive auction on conditional date? | Next positive auction after either date | Observed issue/settlement | Date gap from nominal / conditional date |
|---|---|---|---:|---|---|---:|
| 2024-04-11 | Ramzan-Id (Id-Ul-Fitr) | 2024-04-10 | Yes | 2024-04-18 | 2024-04-19 | 7 / 8 days |
| 2024-05-23 | Buddha Pournima | 2024-05-22 | Yes | 2024-05-29 | 2024-05-30 | 6 / 7 days |
| 2024-08-15 | Independence Day / Parsi New Year | 2024-08-14 | Yes | 2024-08-21 | 2024-08-22 | 6 / 7 days |
| 2024-11-15 | Guru Nanak Jayanti / Karthika Purnima | 2024-11-14 | No; that date is an issue/settlement date from the prior auction | 2024-11-21 | 2024-11-22 | 6 / 7 days |

The candidate next bid date is unchanged under the nominal-date and prior-day scenarios in all four rows. If the previous-day rule applies and cash is credited that day, the calendar interval to the next strictly later auction increases by one day. This is date arithmetic only: neither actual redemption date, credited-funds timing, ability to fund a bid, nor cash return has been established.

## Reproduction and evidence

Run:

```powershell
python decision/audit_g6_3_rbi_tbill_maturity_rule_scope.py
python decision/audit_g6_3_source_inventory.py --check
```

The audit rehashes all raw records for the retained Table 213, 217, and 218 windows and the relevant RBI Mumbai holiday packages; it independently reparses monthly holiday pages; it confirms the four source notice dates and nominal maturities; and it writes `rbi_tbill_maturity_rule_scope_audit_v1.json` plus `rbi_tbill_holiday_maturity_sensitivity_v1.csv` beside this report. The panel contains 151 unique auction dates and 149 positive 91-day issue-price observations. It remains a short descriptive auction-price panel, not a long-run return history or risk distribution.

The earlier 2024–2026 v2 roll calculation remains explicitly conditional on the previous-working-day convention. This audit does not upgrade that convention to a qualified T-bill rule. It also does not calculate any realized T-bill return or investor outcome.

## Next resolvable gate

Retain and review the applicable 2018 GoI T-bill general notification or a first-party date-specific T-bill redemption/settlement record that establishes holiday-maturity treatment. Separately obtain first-party evidence for when proceeds are credited through the relevant investor holding route. If neither source establishes those facts, retain the conditional schedule and keep actual rollover qualification blocked.

G6.3 remains **OPEN / NOT READY**. Investment authorization remains **NO-GO**.
