# RBI T-bill amendment and listed maturity audit

**Review date** 25 November 2026 (India)

**Scope** The RBI notification package cited for the March 2024 auction and the four 91-day bills flagged by the 2024 holiday sensitivity.

**Disposition** The historical notification package passes. Holiday payment dates and Retail Direct bank credit timing remain unqualified. G6.3 remains open and investment authorization remains NO-GO.

## Historical notification check

The [15 March 2024 auction notice](https://rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=57510) and [RBI circular RBI/2021-22/143](https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=12212&Mode=0) identify the 27 March 2018 notification and both amendments. All three browser-saved PDFs have valid PDF headers, readable pages and recorded SHA-256 digests. The copy from the linked `GOI27032018_A.pdf` URL matches the already retained `GOI27032018_TBill.pdf` byte for byte, so both URLs point to one retained artifact for this review. Both amendment pages were visually checked in each language. The 2021 clauses also agree with the [official Gazette copy](https://egazette.gov.in/WriteReadData/2021/232091.pdf), identifier CG-DL-E-23122021-232091. The browser download route supplied no captured HTTP headers or independently verified digital-signature status.

| Document | Page and clauses | What changed |
|---|---|---|
| 27 March 2018 base notification | Page 5, paragraph 9 | Repays bills at par when the tenor expires, at the RBI office where registered. |
| 5 April 2018 amendment | Page 2, paragraphs 4(ii) and 5(iii) | Removes the reference to Vnesheconom Bank from 4(ii) and requires the application to state the bid price to up to four decimal places in 5(iii). |
| 23 December 2021 amendment | Page 2, paragraphs 3 and 4(ii) | Adds Union Territories with legislatures to paragraphs 3 and 4(ii) and lists the 91-, 182- and 364-day tenors for Nepal Rastra Bank in 4(ii). |

Paragraph 9 is untouched by either amendment. The complete cited text establishes repayment at par. A T-bill holiday payment convention and the time when proceeds become usable through Retail Direct still require operational evidence.

## Listed maturity and actual payment

The NSE listing circulars identify the exact securities for all four dates in the [conditional holiday sensitivity](rbi_tbill_holiday_maturity_sensitivity_v1.csv). The NSE maturity dates independently match the issue date plus 91 calendar days in all four cases.

| RBI auction date | NSE listed maturity | ISIN | NSE listing circular, page 2 |
|---|---|---|---|
| 10 January 2024 | 11 April 2024 | IN002023X427 | [CML60218](https://nsearchives.nseindia.com/content/circulars/CML60218.pdf), row 15 |
| 21 February 2024 | 23 May 2024 | IN002023X492 | [CML60818](https://nsearchives.nseindia.com/content/circulars/CML60818.pdf), row 21 |
| 15 May 2024 | 15 August 2024 | IN002024X086 | [CML62065](https://nsearchives.nseindia.com/content/circulars/CML62065.pdf), row 9 |
| 14 August 2024 | 15 November 2024 | IN002024X219 | [CML63407](https://nsearchives.nseindia.com/content/circulars/CML63407.pdf), row 9 |

CML60218 prints January 11, 2023 in its heading while carrying a 2024 reference and twice specifying an effective date of January 12, 2024. The audit uses its ISIN and listed maturity row and preserves that header discrepancy.

NSE circular [CML63038](https://nsearchives.nseindia.com/content/circulars/CML63038.pdf), page 1 row 12, schedules the suspension of trading in IN002024X086 on 12 August 2024 with redemption as the reason. Its date field is the trading suspension date. Actual holiday redemption dates verified from cash payment records total **0 of 4**. Identifying the four securities makes a request to RBI Public Debt Office or Retail Direct support specific to the instruments. The next evidence is an applicable T-bill payment rule or a record naming the ISIN and actual redemption payment date. Credited and available funds before an auction funding cutoff require separate evidence for the relevant retail route. Same-day funding stays excluded and all rollover estimates keep their conditional status.

## Reproduce the evidence check

Read the [capture manifest](rbi_tbill_amendments_and_nse_maturity_manifest_v1.json). Rehash the listed files from the repository root and compare their byte counts and digests. Use PDF page 2 for the English amendment clauses and the four listing annexures. Compare the listed dates with the four dates in the sensitivity CSV. The previous [automated access failure](rbi_tbill_amendment_access_probe_v1.json) remains part of the dated acquisition record.

```powershell
$manifest = Get-Content research/stage512/2026-11-25/g6_3/rbi_tbill_amendments_and_nse_maturity_manifest_v1.json -Raw | ConvertFrom-Json
foreach ($source in $manifest.rbi_files + $manifest.nse_files) {
    if ((Get-Item -LiteralPath $source.file).Length -ne $source.bytes -or
        (Get-FileHash -LiteralPath $source.file -Algorithm SHA256).Hash -ne $source.sha256) {
        throw "Evidence mismatch in $($source.file)"
    }
}
```
