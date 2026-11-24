# RBI T-bill early-window settlement and calendar audit

**As of:** 2026-11-25

**Scope:** Table 213 auctions from 2023-07-12 through 2024-08-28

**Result:** Notice settlement dates reconciled; historical maturity adjustment and rollover remain unqualified.

**Decision status:** NO-GO; no investment authorization.

## Question audited

Can the older Table 213 issue/settlement dates be reconciled against first-party notices, and can its 91-day nominal maturities be safely adjusted for holidays before calculating maturity-to-auction rollover timing?

The first question passes for this bounded sample. The second does not: the available Mumbai holiday matrix is an NI Act holiday source, while one captured RBI release demonstrates a G-Sec market-open exception on such a date. Therefore the matrix cannot be mechanically treated as a complete G-Sec business calendar.

## Evidence and result

- The retained official RBI Mumbai holiday packages cover July 2023–September 2026 continuously (39 months, 70 distinct listed dates). Raw HTML pages are independently parsed and rehashed against their manifests. The packages include 15 newly captured months for July 2023–September 2024, with overlap checks against existing coverage.
- All 60 Table 213 auction notices/results and the handbook table reference are rehashed by the audit. The normalized notice issue date is retained alongside the handbook issue date. Four differences remain explicit: auction dates 2023-09-27, 2024-04-10, 2024-05-22 and 2024-08-14.
- For the 2023-09-27 auction, Table 213 lists 2023-09-28 while the contemporaneous notice sets settlement to 2023-09-29. RBI's [27 September 2023 press release](https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=56455) states that the Government-securities market would operate on 29 September despite the Maharashtra NI Act public holiday and explicitly sets this T-bill auction's settlement for 29 September. The source body is retained and hash-pinned in `source_raw/rbi_gsec_market_open_exception_2023_09_29.html` with metadata in `rbi_gsec_calendar_exceptions_v1.json`. The normalized date therefore follows the official notice, not Table 213.
- The other 59 notice settlement dates are not weekends or listed Mumbai NI Act holidays. The one holiday settlement date has the specific RBI G-Sec operational override above. No claim is made that this single exception defines other holiday dates.
- Four nominal `notice issue date + 91 calendar days` maturities fall on dates listed as Mumbai NI Act holidays: 2024-04-11, 2024-05-23, 2024-08-15 and 2024-11-15. No backward date adjustment, successor auction, cash wait, or rollover return is calculated in this audit.

RBI's [Government Securities Market in India primer](https://www.rbi.org.in/commonperson/English/Scripts/FAQs.aspx?Id=711) describes redemption on the previous working day when maturity falls on Sunday or a holiday. That establishes the general rule, but the evidence assembled here does not establish which G-Sec operational dates govern every historical holiday or investor credit timing. The four specific maturity-date applications must therefore be resolved against applicable first-party operational evidence before producing an adjusted schedule.

## Reproducibility

Run:

```powershell
python decision/audit_g6_3_rbi_tbill_early_calendar.py
python decision/audit_g6_3_source_inventory.py --check
```

The audit writes `rbi_tbill_early_settlement_calendar_audit_v1.json` and `rbi_tbill_early_window_settlement_reconciliation_v1.csv` beside the raw captures. CI runs this audit in the G6.3 RBI T-bill workflow. The separate three-window checker independently reparses notices and results.

## Next acceptance gate

For each of the four nominal holiday maturities, locate and retain the applicable official RBI G-Sec/T-bill operational or redemption evidence; determine the prior working date and whether proceeds are credited that day. If RBI does not publish a date-specific source, document the exact rule and calendar scope that justifies the fallback, or leave the maturity gate blocked. Only after this can a 2023–2024 maturity-to-next-bid event panel be calculated. Any resulting mechanics scenario remains conditional on investor access, allotment, funding, fees, tax, and maturity-credit timing.

The sample remains a short series of auction quote levels, not a long-run risk distribution, equity–bond covariance estimate, or 2036 floor-success probability. G6.3 remains open and the investment decision remains NO-GO.
