from __future__ import annotations
import hashlib,json,pathlib
from decimal import Decimal

try:
    import pymupdf
except ImportError as exc:
    raise SystemExit('PyMuPDF is required only to reproduce the retained official PDF text extracts.') from exc

ROOT=pathlib.Path(__file__).resolve().parents[4]
SRC=ROOT/'research/stage512/2026-11-05/source_retrieval_followup/candidates'
OUT=pathlib.Path(__file__).with_name('g5_4_factsheet_holdings_pages.txt')
JSON_OUT=pathlib.Path(__file__).with_name('g5_4_factsheet_holdings_snapshots.json')
SPECS=[
 {'id':'SBI_NIFTY10Y_GSEC_ETF','file':'sbi_passives_factsheet_2026-03.pdf','page':28,'as_of':'2026-03-31','items':[('Government of India', '96.83'),('Cash, cash equivalents and others','3.17')],'coverage':'Asset allocation total; top-holdings table names Government of India but does not identify individual bond securities.','reported_sum':'100.00'},
 {'id':'SBI_NIFTY500_INDEX_FUND','file':'sbi_passives_factsheet_2026-03.pdf','page':34,'as_of':'2026-03-31','items':[('HDFC BANK LTD.','6.39'),('RELIANCE INDUSTRIES LTD.','5.18'),('ICICI BANK LTD.','4.92'),('BHARTI AIRTEL LTD.','3.12'),('INFOSYS LTD.','2.50'),('LARSEN & TOUBRO LTD.','2.35'),('STATE BANK OF INDIA','2.32'),('AXIS BANK LTD.','1.90'),('ITC LTD.','1.58'),('MAHINDRA & MAHINDRA LTD.','1.51'),('Top-ten reported total','31.77'),('Cash, cash equivalents and others','-0.09')],'coverage':'Top ten equity positions only, plus reported cash line; mechanically unreported portfolio residual is 68.32% (100 - 31.77 - (-0.09)); do not assign residual to individual securities.','reported_sum':None},
 {'id':'SBI_GILT_JUNE2036_FUND','file':'sbi_passives_factsheet_2026-03.pdf','page':46,'as_of':'2026-03-31','items':[('Government securities','96.27'),('Cash, cash equivalents and others','3.73')],'coverage':'Asset-allocation total; top-holdings row is generic Government of India at 96.27%; individual ISINs are not shown.','reported_sum':'100.00'},
 {'id':'SBI_GILT_FUND','file':'sbi_gilt_fund_factsheet_2026-02.pdf','page':1,'as_of':'2026-02-28','items':[('GOI 7.24% 18.08.2055','29.50'),('GOI 6.01% 21.07.2030','9.56'),('GOI 7.18% 14.08.2033','6.57'),('GOI 6.48% 06.10.2035','5.70'),('GOI 6.9% 15.04.2065','4.31'),('GOI 6.79% 07.10.2034','3.16'),('GOI 7.02% 18.06.2031','1.91'),('GOI 6.68% 07.07.2040','0.95'),('GOI 6.28% 14.07.2032','0.36'),('State Government of Karnataka 7.47% 25.08.2036 SDL','4.82'),('State Government of Kerala 7.66% 18.02.2039 SDL','3.12'),('State Government of Bihar 7.86% 11.02.2039 SDL','1.50'),('State Government of Haryana 7.83% 11.02.2043 SDL','1.05'),('State Government of Mizoram 7.85% 11.02.2042 SDL','0.10'),('91 Day T-Bill 27.03.26','7.03'),('91 Day T-Bill 23.04.26','5.73'),('182 Day T-Bill 16.04.26','4.14'),('182 Day T-Bill 05.03.26','3.43'),('364 Day T-Bill 07.05.26','2.91'),('91 Day T-Bill 05.03.26','1.96'),('Cash, cash equivalents and others','2.19')],'coverage':'Factsheet itemized coupon/maturity labels and issue names, but no ISINs. The AMC reports totals of Government Securities 62.02%, SDL 10.59%, T-Bills 25.20%, cash/others 2.19%; no identifier is inferred.','reported_sum':'100.00'},
 {'id':'HDFC_GOLD_ETF','file':'hdfc_gold_etf_factsheet_2026-09.pdf','page':2,'as_of':'2026-08-31','items':[('Gold and gold related: Gold','98.59'),('Cash, cash equivalents and net current assets','1.41')],'coverage':'Reported portfolio allocation totals 100.00%; gold purity stated as 0.995 in product labelling.','reported_sum':'100.00'},
]

pages=[];snapshots=[]
for spec in SPECS:
    path=SRC/spec['file']; raw=path.read_bytes(); doc=pymupdf.open(path); text=doc[spec['page']-1].get_text(); doc.close()
    pages.append(f"===== {spec['file']} | PDF page {spec['page']} | {spec['id']} | source SHA-256 {hashlib.sha256(raw).hexdigest()} =====\n{text}\n")
    total=sum((Decimal(v) for _,v in spec['items'] if _ not in ('Top-ten reported total',)),Decimal(0))
    if spec['id']=='SBI_NIFTY500_INDEX_FUND':
        top=Decimal('31.77'); cash=Decimal('-0.09'); residual=Decimal('100')-top-cash
        assert top==sum((Decimal(v) for n,v in spec['items'][:10]),Decimal(0)) and residual==Decimal('68.32')
        check={'top10_sum_pct':str(top),'cash_pct':str(cash),'unreported_residual_pct':str(residual),'total_pct':str(top+cash+residual)}
    else:
        assert total==Decimal(spec['reported_sum']), (spec['id'],total,spec['reported_sum'])
        check={'reported_allocation_sum_pct':str(total),'expected_sum_pct':spec['reported_sum'],'passes':True}
    snapshots.append({'candidate_id':spec['id'],'as_of':spec['as_of'],'source_path':f"research/stage512/2026-11-05/source_retrieval_followup/candidates/{spec['file']}",'source_sha256':hashlib.sha256(raw).hexdigest(),'pdf_page':spec['page'],'extraction_method':f"PyMuPDF {pymupdf.VersionBind}; manually transcribed labeled source rows and independently reconciled Decimal sums",'rows':[{'label':n,'reported_pct':v} for n,v in spec['items']],'coverage_and_limitations':spec['coverage'],'arithmetic_check':check})
OUT.write_text('\n'.join(pages),encoding='utf-8')
report={'schema_version':1,'record_id':'g5-4-factsheet-holdings-2026-11-05-v1','source_cutoff':'2026-11-05','extracted_text_path':'research/stage512/2026-11-05/g5_4/g5_4_factsheet_holdings_pages.txt','extracted_text_sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'snapshots':snapshots,'boundary':'Dated snapshots only. No historical holdings are inferred. ETF/fund weight snapshots are not benchmark weights and do not establish executable returns.'}
JSON_OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'status':'PASS','snapshots':len(snapshots),'extracted_text_sha256':report['extracted_text_sha256'],'checks':[{'candidate_id':s['candidate_id'],'check':s['arithmetic_check']} for s in snapshots]},indent=2))
