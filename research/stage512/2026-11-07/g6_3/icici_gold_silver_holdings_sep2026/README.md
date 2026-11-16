# ICICI Prudential Gold and Silver ETF holdings — 30 September 2026

This evidence adds a later 30 September 2026 holdings snapshot for ICICI Gold and Silver ETF. The earlier 31 March 2026 rows remain preserved as historical evidence in the candidate register; the newer snapshot is linked separately in `research/stage512/2026-11-05/g5_4/g5_candidate_disposition_v1.json` under `latest_holdings_snapshot`. This qualifies disclosed composition only.

## Source and byte integrity

- AMC disclosure index: https://www.advisorkhoj.com/form-download-centre/Mutual/ICICI-Prudential-Mutual-Fund/Monthly-Portfolio-Disclosures
- Direct official AMC archive: https://www.icicipruamc.com/blob/downloads/Files/Monthly%20Portfolio%20Disclosures/2026/Sep/Monthly-Portfolio-Disclosure-September-2026.zip
- Downloaded official ZIP: 25,879,936 bytes; SHA-256 D40FE596247479B4DA3A9CA613A7D19C1773B0A06E866543EE8753352D29DAD7.
- The original ZIP contains 151 entries. To keep the repository focused, this package retains the exact two original XLSX member byte streams rather than the entire archive:
  - ICICI Prudential Gold ETF.xlsx: 182,629 bytes; SHA-256 CB232F1D29F42FFDD4D17B29BCA8F6AB7A4DEF038CC9F4A42741798845B1467A.
  - ICICI PRUDENTIAL SILVER ETF.xlsx: 160,341 bytes; SHA-256 81D3C10FCE48D393ABF2B7290CE13C80EC4F5225D2F9DE5459BBEF9866AC7DF8.
- Raw workbooks are retained unchanged. Source details and exact values are in source_manifest.json.

## Composition results

All percentages below are percentages of scheme NAV. Source monetary amounts are in ₹ lakh.

| Scheme | Physical holding | Physical weight | TREPS | Net current assets | Total net assets |
|---|---:|---:|---:|---:|---:|
| ICICI Prudential Gold ETF | Gold (995 Purity): ₹2,708,993.78 lakh | 98.097201% | ₹689.99 lakh; 0.024986% | ₹51,856.585795 lakh; 1.877814% | ₹2,761,540.355795 lakh |
| ICICI Prudential Silver ETF | Silver: ₹1,419,233.84 lakh | 98.963952% | ₹48.75 lakh; 0.003399% derived | ₹14,809.126552 lakh; 1.032648% | ₹1,434,091.716552 lakh |

The silver workbook displays the TREPS weight as a caret and explains that this marker means a value below 0.01% of NAV in absolute terms. The reported ₹48.75 lakh divided by total net assets yields 0.003399%, consistent with that disclosure.

Each workbook contains both a metal-category roll-up and a matching physical-metal detail row. Those rows carry equal values; the audit counts the detailed physical holding once and does not sum the duplicate roll-up. Value totals and weights reconcile to 100% for both schemes.

## Reproduction

With Python 3.13 and openpyxl 3.1.5:

    python research/stage512/2026-11-07/g6_3/icici_gold_silver_holdings_sep2026/audit_icici_gold_silver_holdings.py

The script validates the workbook dates, metal roll-up/detail equality, footnote handling, value reconciliation, and weight reconciliation, then regenerates holdings_audit.json.

## Limits

This is a holdings snapshot, not an investment return series. It does not qualify ETF traded prices, premiums/discounts, spreads, depth, slippage, fees, taxes, investor execution, covariance, suitability, or expected outcomes. The reported quantity field is preserved without inferring its unit. The physical-metal rows do not provide bar serials or lot-level custody data.

G6.3 remains open; this closes only the bounded September 2026 Gold/Silver holdings-evidence refresh. Investment status remains NO-GO / NOT YET EVALUATED.