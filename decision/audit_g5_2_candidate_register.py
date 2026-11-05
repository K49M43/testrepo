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
  require(prod.get('retrieved_at') and 'publication_date_status' in prod,f"retrieval/publication metadata missing for {prod['candidate_id']}")
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
  ROOT/'research/stage512/data/amfi_pilot/manifest.json':'8df56254c5351ea155f188e0a295a697f65375badcf4f1ffe5f2a3a48009cac9',
  ROOT/'research/stage58/public_nav_metrics.csv':'9c5bb3678fde02bd35d67cddfbbeb667d7f73a356f0cf8b984b76b92f07a89ed',
  ROOT/'research/stage59/amfi_ter_matched_96_v14.csv':'8606de60e951eb8716aad18932d6ad0e3a838125a9ab5d06bb78384b67fb9bdf',
  ROOT/'research/stage59/amfi_ter_export_diagnostic.json':'c74f07e8d042f4c06ef0a8c665f775ae2e065c610df49880d77e45a10e5a0d36',
  ROOT/'research/stage59/amfi_ter_oct2026_export_latest.csv':'5d4b0b4a6ee306cedddad0b4470c3efd5fe76ffcbdb0e96c7fd38455b8df8e77',
 }
 for path,expected in supporting.items():require(path.exists() and sha(path)==expected,f'upstream G5.1 evidence hash mismatch: {path}')
 amfi=loadcsv(ROOT/'research/stage512/data/amfi_pilot/named_scheme_observations.csv')
 ter=loadcsv(ROOT/'research/stage59/amfi_ter_matched_96_v14.csv')
 # Independently join sample rows to the first-party AMFI retrieval manifest.
 manifest=json.loads((ROOT/'research/stage512/data/amfi_pilot/manifest.json').read_text(encoding='utf-8'))
 windows={w['label']:w for w in manifest['windows']}
 expected_events={
  'latest':('https://portal.amfiindia.com/spages/NAVAll.txt','2026-11-02T11:19:52.484200+00:00','584d0519e605b2aba0d1a218eb3099f18b7592e933fa712ab4b07062e9cec73a',1528600),
  'history_2024-01-02_2024-01-05':('https://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?tp=1&frmdt=02-Jan-2024&todt=05-Jan-2024','2026-11-02T11:20:03.976661+00:00','00d367d0d760beab6c7380c92357e8fd071c8742b6666fc7ae5957066cf55dd3',3687487),
  'history_2026-10-19_2026-10-23':('https://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?tp=1&frmdt=19-Oct-2026&todt=23-Oct-2026','2026-11-02T11:20:22.083957+00:00','cceb34cff86617f2c0925aaaf9c20a11687ea636ae175c079de6df4e5ae04d24',4660562),
 }
 require(set(windows)==set(expected_events),'AMFI manifest window set changed')
 for label,(url,retrieved,digest,nbytes) in expected_events.items():
  w=windows[label]
  require(w['status']=='PASS' and w['http_status']==200 and (w['source_url'],w['retrieved_utc'],w['sha256'],w['response_bytes'])==(url,retrieved,digest,nbytes),f'AMFI retrieval metadata mismatch for {label}')
 expected_dates=['2024-01-02','2024-01-03','2024-01-04','2024-01-05','2026-10-19','2026-10-21','2026-10-22','2026-10-23','2026-10-30']
 for isin,code,tervalue,symbol,allotment in [('INF109KC1NT3','113076','0.49','GOLDIETF','2010-08-24'),('INF109KC1Y56','149464','0.4','SILVERIETF','2022-01-24')]:
  candidate=next(x for x in reg['candidates'] if x['candidate_id']==('ICICI_GOLD_ETF' if code=='113076' else 'ICICI_SILVER_ETF'))
  require(candidate['instrument_or_benchmark_id']==f'ISIN {isin}; AMFI {code}; NSE {symbol}',f'official identity/symbol mismatch for {isin}')
  require(candidate['inception_date']==allotment,f'official allotment date mismatch for {isin}')
  sample_spec=candidate['history_coverage']['official_AMFI_sample_observations']
  require(sample_spec['dates']==expected_dates and sample_spec['continuity'].startswith('No;'),f'AMFI sample date/continuity mismatch for {isin}')
  recorded=sample_spec['retrieval_events']
  require(len(recorded)==3,'AMFI retrieval event count mismatch')
  for event in recorded:
   require(event['window'] in expected_events and event['source_url']==windows[event['window']]['source_url'] and event['retrieved_at_utc']==windows[event['window']]['retrieved_utc'] and event['response_sha256']==windows[event['window']]['sha256'] and event['response_bytes']==windows[event['window']]['response_bytes'],f'candidate AMFI provenance diverges from manifest for {isin}')
  metalrows=[r for r in amfi if r['isin']==isin]
  require([r['date'] for r in metalrows]==expected_dates,f'official AMFI observation dates mismatch for {isin}')
  require(all(r['source_sha256']==windows[r['source_window']]['sha256'] for r in metalrows),f'AMFI row/source hash linkage mismatch for {isin}')
  require(len({r['date'] for r in metalrows})==len(metalrows),'duplicate AMFI sample observation')
  hist=json.dumps(candidate.get('history_coverage',{})).lower()
  require('not a continuous interval' in hist and 'third_party_mirror_limitation' in hist and 'not qualified for return calculations' in hist,f'full-history caveat missing for {isin}')
 # The official TER raw XLSX was not retained; audit the preserved diagnostic,
 # normalized export, bounded workflow interval, and independently matched rows.
 diagnostic=json.loads((ROOT/'research/stage59/amfi_ter_export_diagnostic.json').read_text(encoding='utf-8'))
 require(diagnostic['export_url']=='https://www.amfiindia.com/api/populate-te-rdata-revised?MF_ID=All&Month=10-2026&strCat=-1&strType=-1&excel=true' and diagnostic['sha256']=='ec512c338263e41f3d8c520d764965758817a670edce8e4a92caad26d9fc46b2' and diagnostic['download_size']==4397825,'AMFI TER raw-export diagnostic mismatch')
 ter_evidence=next(c for c in reg['candidates'] if c['candidate_id']=='ICICI_GOLD_ETF')['primary_evidence']
 te=next(x for x in ter_evidence if x.get('source_export_url'))
 require(te['source_export_sha256']==diagnostic['sha256'] and te['source_export_bytes']==diagnostic['download_size'] and te['source_diagnostic_sha256']==sha(ROOT/'research/stage59/amfi_ter_export_diagnostic.json') and te['normalized_export_sha256']==sha(ROOT/'research/stage59/amfi_ter_oct2026_export_latest.csv'),'candidate TER provenance/hash mismatch')
 interval=te['retrieval_window_utc']
 require(interval['workflow_run_id']==41284958349 and interval['workflow_url']=='https://github.com/K49M43/testrepo/actions/runs/41284958349' and interval['precision'].startswith('Bounded by the Actions log; exact HTTP response completion timestamp was not recorded.'),'TER acquisition interval overstated or unlinked')
 normalized=loadcsv(ROOT/'research/stage59/amfi_ter_oct2026_export_latest.csv')
 for nsdl,expected in [('ICIC/O/O/GET/10/04/0038','0.49'),('ICIC/O/O/OET/21/12/0137','0.4')]:
  rr=[r for r in normalized if r['NSDL Scheme Code']==nsdl]
  require(len(rr)==1 and rr[0]['Regular Plan - Total TER (%)']==expected and rr[0]['TER Date']=='46324',f'AMFI official normalized TER row mismatch for {nsdl}')
 for isin,code,tervalue in [('INF109KC1NT3','113076','0.49'),('INF109KC1Y56','149464','0.4')]:
  sample=[r for r in amfi if r['isin']==isin and r['source_window']=='latest' and r['date']=='2026-10-30']
  require(len(sample)==1 and sample[0]['source_sha256']=='584d0519e605b2aba0d1a218eb3099f18b7592e933fa712ab4b07062e9cec73a',f'AMFI latest sample mismatch for {isin}')
  fee=[r for r in ter if r['scheme_code']==code and r['ter_date']=='2026-10-29']
  require(len(fee)==1 and fee[0]['R_TER']==tervalue and fee[0]['TER_TOTAL_MATH_CHECK']=='PASS',f'AMFI TER row mismatch for {isin}')
 # Re-extract the factsheet tables from the preserved PDFs, not only their CSVs.
 import pymupdf
 lic=pymupdf.open(RAW/'lic_gsec_factsheet_2026-09.pdf')
 lictext='\n'.join(page.get_text() for page in lic)
 require('PORTFOLIO as on 30/09/2026' in lictext,'LIC September 2026 portfolio page missing')
 for token in ['6.94% GOVT OF INDIA RED 11-05-2036','58.87%','6.48% GOVT OF INDIA RED 06-10-2035','25.51%','7.18% GOVT OF INDIA RED 24-07-2037','15.11%','TREPS / Repo','0.16%','Net Receivables/(Payables)','0.35%']:
  require(token in lictext,f'LIC PDF extraction missing {token}')
 icici=pymupdf.open(RAW/'icici_passive_factsheet_2026-03.pdf')
 goldpage=' '.join(icici[44].get_text().split())
 silverpage=' '.join(icici[45].get_text().split())
 for text,allotment,symbol,isin in [(goldpage,'24-Aug-10','GOLDIETF','INF109KC1NT3'),(silverpage,'24-Jan-22','SILVERIETF','INF109KC1Y56')]:
  require(f'Inception/Allotment date: {allotment}' in text and f'NSE : {symbol}' in text and f'ISIN : {isin}' in text,f'ICICI official factsheet identity/allotment mismatch for {isin}')
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


