# RBI T-bill 2018 terms and redemption-route audit

**Audit date:** 2026-11-25

**Scope:** retain and inspect the RBI-hosted 2018 GoI T-bill general notification; reconcile its source identity with the terms cited by RBI for 2024; review first-party redemption-route wording.

**Decision status:** NO-GO; G6.3 remains open and not ready.

## Finding

The [official RBI-hosted PDF](https://rbidocs.rbi.org.in/rdocs/content/pdfs/GOI27032018_TBill.pdf) retained at research/stage512/2026-11-25/g6_3/source_raw/GOI27032018_TBill.pdf is 1,845,463 bytes, six pages, SHA-256 896e1f66fce128014769be977ccb3f9e22132289a1c936205d6802aa53abade2. Pages 4–6 were text-extracted and visually reviewed.

The 27 March 2018 General Notification states:

- Clause 2(i): RBI sells bills with maturities up to 364 days and announces auction particulars.
- Clause 2(iv): bills are issued at a discount and redeemed at face value.
- Clause 5(v): successful bidders fund by the specified cut-off on auction settlement day.
- Clause 7: bills are issued as a Promissory Note or credited to an SGL account.
- Clause 9: bills are repaid at par on expiration of their tenor at the RBI office where they are registered.

Clause 9 does not specify how a maturity date on a holiday is adjusted. It also does not state an intraday time for proceeds availability or whether those funds can fund an auction on the same date.

## Applicable amendment package and provenance

The [RBI 15 March 2024 auction notice](https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=57510) says 2024 T-bill auctions are governed by the 27 March 2018 General Notification together with amendments dated 5 April 2018 and 23 December 2021. Its linked attachment paths are:

- GOI27032018_A.pdf
- GOI05042018_A.pdf
- GOI23122021_A.pdf

The locally retained base document came from the official RBI-hosted URL GOI27032018_TBill.pdf; the relationship between that file and the notice's differently named GOI27032018_A.pdf attachment has not been byte-verified. The two amendment URLs returned verification/rejection HTML in online retrieval. No access control was bypassed, and those HTML responses are not treated as legal-source bytes.

Therefore this captures useful wording from the official 2018 base document, but it does not yet qualify the complete set of terms applicable to the 2024 sample.

## Redemption proceeds route

The [RBI Retail Direct FAQ](https://www.rbi.org.in/scripts/FS_FAQs.aspx?Id=145) identifies T-bills as available through Retail Direct and says purchase/sale settlement uses the linked rupee savings bank account, to which redemption amounts are credited. It does not specify the exact date or intraday time of a T-bill redemption credit.

A separate [RBI Government Securities FAQ](https://www.rbi.org.in/commonman/english/scripts/FAQs.aspx?Id=380) says automatic-redemption proceeds for eligible SC, BLA, SGL/CSGL holdings are credited to the bank account on the due date, subject to account details being furnished. This supports a general due-date expectation; it is not a date-specific T-bill redemption record, an investor-specific account confirmation, or evidence of same-day intraday availability.

The evidence supports excluding same-day maturity proceeds from auction-funding calculations. It does not resolve holiday maturity adjustment, exact investor credit timing, or whether proceeds are available before any same-day auction payment cut-off.

## Gate disposition

| Acceptance point | Status |
|---|---|
| Official 2018 base terms text retained and reviewed | PASS_WITH_PROVENANCE_CAVEAT |
| Complete amendment package governing the 2024 sample | NOT_QUALIFIED |
| T-bill-specific holiday adjustment | NOT_QUALIFIED |
| Retail Direct redemption destination account | QUALIFIED_AT_DESTINATION_LEVEL |
| Exact Retail Direct credit date and intraday availability | NOT_QUALIFIED |
| Same-day maturity proceeds used for auction funding | EXCLUDED |

No historic return panel or rollover schedule was recalculated from these sources. The prior-working-day schedule remains a conditional sensitivity only.

## Next source gate

Obtain the exact official amendment attachments dated 5 April 2018 and 23 December 2021 and reconcile the 27 March 2018 attachment identity. Then search for first-party, date-specific T-bill redemption evidence for one of the four 2024 holiday-maturity events. Keep the investor-route credit-time question separate: if RBI documentation stops at “due date,” exact intraday timing requires a route-specific first-party record or remains excluded from same-day cash assumptions.

G6.3 remains OPEN / NOT READY. Investment authorization remains NO-GO.

## Reproduction

Verify the PDF hash with:

~~~powershell
Get-FileHash research/stage512/2026-11-25/g6_3/source_raw/GOI27032018_TBill.pdf -Algorithm SHA256
~~~

Verify the source manifest is valid JSON with:

~~~powershell
Get-Content research/stage512/2026-11-25/g6_3/rbi_tbill_2018_terms_and_route_evidence_manifest_v1.json -Raw | ConvertFrom-Json
~~~