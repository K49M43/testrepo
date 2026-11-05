from __future__ import annotations
import argparse, csv, hashlib, json, math, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'research/stage512/2026-11-05'
RAW=BASE/'source_raw'

def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def require(ok:bool,msg:str)->None:
 if not ok: raise AssertionError(msg)
def loadcsv(path:Path):
 with path.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args()
 reg=json.loads((BASE/'g5_2_candidate_evidence_register_v1.json').read_text(encoding='utf-8'))
 h=json.loads((BASE/'g5_2_holdings_overlap_v1.json').read_text(encoding='utf-8'))
 q=json.loads((BASE/'g5_2_qcsae_v1.json').read_text(encoding='utf-8'))
 cats={x['category'] for x in reg['candidates']}
 require({'equity','direct_government_security','sovereign_bond_fund_or_etf_proxy','gold','silver','cash_hold_comparator'}<=cats,'required candidate category missing')
 require(reg['investment_authorization']=='NO_GO','authorization must remain NO_GO')
 require(all(c['classification'] in {'INVESTABLE','PROXY_ONLY','EXCLUDED','BLOCKED'} for c in reg['candidates']),'invalid classification')
 require(all(c.get('exact_as_of') is not None for c in reg['candidates']),'candidate missing dated classification basis')
 require(q['investment_authorization']=='NO_GO' and 'G5.3' in q['next_dependency'],'QCSAE status/dependency invalid')
 # Preserve and hash-check every source and normalized holdings snapshot.
 for prod in h['products']:
  src=RAW/prod['source_file']; norm=BASE/prod['normalized_csv']
  require(src.exists() and norm.exists(),f"missing holdings source for {prod['candidate_id']}")
  require(sha(src)==prod['source_sha256'],f"raw source hash mismatch: {src.name}")
  require(sha(norm)==prod['normalized_csv_sha256'],f"normalized holdings hash mismatch: {norm.name}")
 # Independently parse the two official xlsx files and compare normalized rows.
 import openpyxl
 specs=[('motilal_nifty500_etf_2026-09.xlsx','MOTILAL_NIFTY500_ETF'),('motilal_nifty500_indexfund_2026-09.xlsx','MOTILAL_NIFTY500_INDEX_FUND')]
 parsed={}
 for fn,cid in specs:
  ws=openpyxl.load_workbook(RAW/fn,read_only=True,data_only=True).active
  got=[]
  for row in ws.iter_rows(min_row=13,values_only=True):
   num,name,sid,industry,qty,mv,wt=row[:7]
   if not name or not isinstance(num,(int,float)) or not isinstance(mv,(int,float)):continue
   equity=bool(sid and str(sid).startswith('INE'))
   got.append((str(sid).strip() if sid else '',str(name).strip(),str(industry).strip() if industry else '',str(round(float(mv),2)),'' if not isinstance(wt,(int,float)) else str(float(wt)), 'EQUITY' if equity else ('MONEY_MARKET' if not sid and 'Repo' in str(name) else 'OTHER_OR_RECONCILIATION')))
  rows=loadcsv(BASE/(cid.lower()+'_holdings_2026-09-30.csv'))
  parsed[cid]=rows
  rec=[(r['security_id'] or '',r['name'],r['classification'] or '',str(round(float(r['market_value_inr_lakh']),2)),r['weight_pct_source'],r['position_type']) for r in rows]
  require(got==rec,f"XLSX to normalized CSV mismatch for {cid}")
  eq=[r for r in rows if r['position_type']=='EQUITY']
  require(len(eq)==498 and all(r['security_id'] for r in eq),f"equity count/ISIN coverage mismatch for {cid}")
  require(sum(r['weight_pct_source']=='' for r in eq)==1,f"suppressed-weight row not preserved for {cid}")
  require(abs(sum(float(r['weight_pct_source']) for r in eq if r['weight_pct_source'])-(99.68 if cid.endswith('ETF') else 99.74))<1e-8,f"equity displayed weight total mismatch for {cid}")
 a={r['security_id']:r for r in parsed['MOTILAL_NIFTY500_ETF'] if r['position_type']=='EQUITY'}
 b={r['security_id']:r for r in parsed['MOTILAL_NIFTY500_INDEX_FUND'] if r['position_type']=='EQUITY'}
 common=sorted(set(a)&set(b)); numeric=[x for x in common if a[x]['weight_pct_source'] and b[x]['weight_pct_source']]
 overlap=sum(min(float(a[x]['weight_pct_source']),float(b[x]['weight_pct_source'])) for x in numeric)
 diag=h['exposure_diagnostics']
 require(len(common)==498 and len(numeric)==497,'ISIN match/weight coverage unexpected')
 require(abs(overlap-diag['overlap_pct_reported_weight_subset'])<1e-8,'overlap calculation mismatch')
 require(abs(overlap-99.68)<1e-8,'unexpected overlap result')
 for cid,expected in [('ICICI_GOLD_ETF',100.0),('ICICI_SILVER_ETF',100.0),('LIC_GSEC_8_13_ETF',100.0)]:
  prod=next(p for p in h['products'] if p['candidate_id']==cid)
  rows=loadcsv(BASE/prod['normalized_csv'])
  val=sum(float(r['weight_pct_source']) for r in rows if r['weight_pct_source'])
  require(abs(val-expected)<0.011,f"dated snapshot weights do not reconcile within 0.01 pct pt for {cid}: {val}")
  require(all(not r['security_id'] for r in rows),f"factsheet omitted identifiers must remain null for {cid}")
 # Verify G5.1-era official AMFI sample and TER source files reused by G5.2.
 supporting={
  ROOT/'research/stage512/data/amfi_pilot/named_scheme_observations.csv':'6b08b10f469ffeb9523b0f4c06f2be87cdbd0fc50f931234d180b0fefb8d0005',
  ROOT/'research/stage58/public_nav_metrics.csv':'9c5bb3678fde02bd35d67cddfbbeb667d7f73a356f0cf8b984b76b92f07a89ed',
  ROOT/'research/stage59/amfi_ter_matched_96_v14.csv':'8606de60e951eb8716aad18932d6ad0e3a838125a9ab5d06bb78384b67fb9bdf',
 }
 for path,expected in supporting.items():require(path.exists() and sha(path)==expected,f'upstream G5.1 evidence hash mismatch: {path}')
 amfi=loadcsv(ROOT/'research/stage512/data/amfi_pilot/named_scheme_observations.csv')
 ter=loadcsv(ROOT/'research/stage59/amfi_ter_matched_96_v14.csv')
 for isin,code,tervalue in [('INF109KC1NT3','113076','0.49'),('INF109KC1Y56','149464','0.4')]:
  sample=[r for r in amfi if r['isin']==isin and r['source_window']=='latest' and r['date']=='2026-10-30']
  require(len(sample)==1 and sample[0]['source_sha256']=='584d0519e605b2aba0d1a218eb3099f18b7592e933fa712ab4b07062e9cec73a',f'AMFI latest sample mismatch for {isin}')
  fee=[r for r in ter if r['scheme_code']==code and r['ter_date']=='2026-10-29']
  require(len(fee)==1 and fee[0]['R_TER']==tervalue and fee[0]['TER_TOTAL_MATH_CHECK']=='PASS',f'AMFI TER row mismatch for {isin}')
  candidate=next(x for x in reg['candidates'] if x['instrument_or_benchmark_id'].startswith('ISIN '+isin))
  hist=json.dumps(candidate.get('history_coverage',{})).lower()
  require('not complete' in hist and 'third-party' in hist,f'full-history caveat missing for {isin}')
 # Re-extract the factsheet tables from the preserved PDFs, not only their CSVs.
 import pymupdf
 lic=pymupdf.open(RAW/'lic_gsec_factsheet_2026-09.pdf')
 lictext='\n'.join(page.get_text() for page in lic)
 require('PORTFOLIO as on 30/09/2026' in lictext,'LIC September 2026 portfolio page missing')
 for token in ['6.94% GOVT OF INDIA RED 11-05-2036','58.87%','6.48% GOVT OF INDIA RED 06-10-2035','25.51%','7.18% GOVT OF INDIA RED 24-07-2037','15.11%','TREPS / Repo','0.16%','Net Receivables/(Payables)','0.35%']:
  require(token in lictext,f'LIC PDF extraction missing {token}')
 icici=pymupdf.open(RAW/'icici_passive_factsheet_2026-03.pdf')
 icicitext=' '.join(' '.join(page.get_text().split()) for page in icici)
 for token in ['Portfolio as on March 31, 2026','Gold (995 Purity)','Gold 98.21%','Short Term Debt and net current assets 1.79%','Silver 99.08%','Short Term Debt and net current assets 0.92%']:
  require(token in icicitext,f'ICICI PDF extraction missing {token}')
 # Recompute AMFI industry weights and top concentration from the normalized holdings.
 for cid in ['MOTILAL_NIFTY500_ETF','MOTILAL_NIFTY500_INDEX_FUND']:
  rows=parsed[cid]; sums={}
  for row in rows:
   if row['position_type']=='EQUITY' and row['weight_pct_source']:
    sums[row['classification']]=sums.get(row['classification'],0)+float(row['weight_pct_source'])
  record=next(x for x in h['products'] if x['candidate_id']==cid)
  weights=sorted((float(x['weight_pct_source']) for x in rows if x['position_type']=='EQUITY' and x['weight_pct_source']),reverse=True)
  require(abs(sum(weights[:10])-record['top10_equity_weight_pct_reported'])<1e-8,'top-10 concentration mismatch')
  require(abs(sum(weights[:20])-record['top20_equity_weight_pct_reported'])<1e-8,'top-20 concentration mismatch')
  saved=h['exposure_diagnostics']['industry_concentration_pct'][cid]['reported_industry_weight_pct']
  require(set(saved)==set(sums) and all(abs(saved[k]-sums[k])<1e-8 for k in sums),'industry concentration mismatch')
 print('G5.2 candidate register audit PASS')
 print(f"Candidates: {len(reg['candidates'])}; categories: {', '.join(sorted(cats))}")
 print('Nifty 500 holdings: 498 equity ISINs each; 497 numeric weights each; same-date overlap 99.68% (rounded source inputs)')
 print('Bond/gold/silver dated snapshots reconcile; missing ISINs remain null; AMFI NAV data remains sample-only for metals')
 print('Investment authorization: NO-GO; G5.3 independent audit remains required')
 return 0
if __name__=='__main__':
 try:raise SystemExit(main())
 except Exception as e:
  print(f'G5.2 audit FAIL: {e}',file=sys.stderr);raise


