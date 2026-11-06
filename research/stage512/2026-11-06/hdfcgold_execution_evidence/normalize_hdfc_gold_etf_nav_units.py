#!/usr/bin/env python3
"""Apply HDFC Gold ETF's documented 2021 100:1 face-value rebase to AMFI NAV levels.

The raw source CSV is never modified. The output preserves raw NAV, adjustment factor,
adjusted NAV, source segment hash, and a per-row transformation label.
"""
import argparse, csv, hashlib, json, statistics
from collections import Counter
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

SCHEME='113049'
ISIN='INF179KC1981'
SPLIT_EFFECTIVE=date(2021,2,19)
FIRST_POST_SPLIT_NAV=date(2021,2,22)
HDFC_SOURCE='https://files.hdfcfund.com/s3fs-public/2026-06/Fund%20Facts%20-%20HDFC%20NIFTY%20Gold%20ETF_June%2026.pdf'


def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest().upper()

def text(d): return format(d,'f')
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--input',required=True,type=Path)
 ap.add_argument('--output-csv',required=True,type=Path)
 ap.add_argument('--output-manifest',required=True,type=Path)
 a=ap.parse_args()
 with a.input.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
 source=[r for r in rows if r['scheme_code']==SCHEME and r['isin']==ISIN]
 if len(source)!=len(rows): raise SystemExit('Input contains rows outside specified scheme/ISIN; refusing to discard them.')
 seen=set(); normalized=[]
 for r in source:
  d=date.fromisoformat(r['date'])
  if d in seen: raise SystemExit(f'duplicate source date: {d}')
  seen.add(d)
  raw=Decimal(r['nav'])
  if raw<=0: raise SystemExit(f'non-positive NAV on {d}')
  factor=Decimal(100) if d<FIRST_POST_SPLIT_NAV else Decimal(1)
  adjusted=raw/factor
  normalized.append({**r,'nav_raw_original_unit':text(raw),'unit_conversion_factor_raw_to_current':text(factor),'nav_current_1_rupee_face_value_basis':text(adjusted),'adjustment_rule':'divide by 100: pre-rebase ₹100 face-value units' if factor==100 else 'no adjustment: ₹1 face-value units'})
 normalized.sort(key=lambda r:r['date'])
 fields=list(normalized[0].keys())
 with a.output_csv.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(normalized)
 returns=[]
 for prev,cur in zip(normalized,normalized[1:]):
  ret=Decimal(cur['nav_current_1_rupee_face_value_basis'])/Decimal(prev['nav_current_1_rupee_face_value_basis'])-1
  returns.append((cur['date'],ret))
 before=next(r for r in normalized if r['date']=='2021-02-19')
 after=next(r for r in normalized if r['date']=='2021-02-22')
 prev=next(r for r in normalized if r['date']=='2021-02-18')
 returns_by_date=dict(returns)
 hdfc_start=Decimal(next(r['nav_current_1_rupee_face_value_basis'] for r in normalized if r['date']=='2021-05-31'))
 hdfc_end=Decimal(next(r['nav_current_1_rupee_face_value_basis'] for r in normalized if r['date']=='2026-05-29'))
 five_year=(hdfc_end/hdfc_start)**(Decimal(1)/Decimal(5))-1
 ret_outliers=[{'date':d,'return_pct':text(ret*100)} for d,ret in returns if abs(ret)>=Decimal('0.05')]
 manifest={
  'audit_id':'hdfc_gold_etf_amfi_unit_rebase_2026-11-06_v1',
  'source_identity':{'scheme_code':SCHEME,'isin':ISIN,'scheme_name':'HDFC Gold ETF'},
  'input':{'repo_path':'research/stage512/2026-11-05/source_retrieval_followup/candidates/nav_113049_daily.csv','sha256':sha(a.input),'observations':len(source),'first_date':normalized[0]['date'],'last_date':normalized[-1]['date']},
  'corporate_action_basis':{'source':'HDFC Mutual Fund June 2026 Fund Factsheet','url':HDFC_SOURCE,'reviewed_on':'2026-11-06','published_statement':'Face value per unit revised from ₹100 to ₹1 and allotment price from ₹1,800.3288 to ₹18.0033 effective 2021-02-19; HDFC states return computations were adjusted.','raw_pdf_bytes_and_hash_retained':False,'first_post_split_observation_in_input':'2021-02-22','mapping':'Input NAV rows before 2021-02-22 are in the pre-rebase ₹100 face-value basis and are divided by 100. From 2021-02-22 onward values remain unchanged in the ₹1 basis. This preserves raw values and is applied only to the derived output.'},
  'transition_reconciliation':{'2021-02-18_raw_nav':prev['nav'],'2021-02-19_raw_nav':before['nav'],'2021-02-19_adjusted_nav':before['nav_current_1_rupee_face_value_basis'],'2021-02-22_raw_and_adjusted_nav':after['nav'],'unadjusted_cross_denomination_return':'not computed; NAV unit bases differ','adjusted_return_pct_2021-02-19_to_2021-02-22':text((Decimal(after['nav_current_1_rupee_face_value_basis'])/Decimal(before['nav_current_1_rupee_face_value_basis'])-1)*100),'adjusted_return_pct_2021-02-18_to_2021-02-19':text(returns_by_date['2021-02-19']*100)},
  'integrity':{'output_observations':len(normalized),'unique_dates':len(seen),'duplicate_dates':0,'nonpositive_raw_nav':0,'adjusted_daily_returns_abs_ge_5pct':ret_outliers},
  'independent_fund_return_anchor':{'hdfc_reported_period':'5 years ending 2026-05-29','hdfc_reported_cagr_pct':'25.01','source':'https://files.hdfcfund.com/s3fs-public/2026-06/Fund%20Facts%20-%20HDFC%20NIFTY%20Gold%20ETF_June%2026.pdf','series_start_date':'2021-05-31','series_start_nav':text(hdfc_start),'series_end_date':'2026-05-29','series_end_nav':text(hdfc_end),'derived_cagr_using_exact_five_year_exponent_pct':text(five_year*100),'interpretation':'Close cross-check (24.9987% vs reported 25.01%); not exact reproduction because report-period and annualization conventions are not fully specified.'},
  'output':{'filename':a.output_csv.name,'bytes':a.output_csv.stat().st_size,'sha256':sha(a.output_csv)},
  'limits':['This is a unit-denomination normalization, not a return fill or price splice.','It does not convert AMFI NAV into NSE traded price.','The independent fund return anchor begins after the unit rebase and therefore checks later-series arithmetic but does not independently prove the split factor.','Other source-specific corporate actions would require separate evidence; none are inferred.','G6.3 remains OPEN; investment state remains NO-GO / NOT YET EVALUATED.']
 }
 a.output_manifest.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 print(json.dumps(manifest,indent=2,ensure_ascii=True))
if __name__=='__main__': main()
