"""Fail-closed data source qualification for 2036 portfolio calibration.
Usage:
 python stage512_import_gate.py --cpi stage512_cpi_official_linked_2013_2026.csv \
    --equity official_nifty500_tri.csv --gsec official_gsec_total_return.csv \
    --gold rbi_mumbai_gold.csv --silver rbi_mumbai_silver.csv \
    --nav amfi_nav_monthly.csv
Columns in data series: month (YYYY-MM), value (>0), source_url, source_type,
  series_id, price_convention, return_basis.
For NAV: additionally scheme_code, plan, option, nav_date.
Verification of provenance/source metadata is a human audit; script enforces
structural integrity and fails safely if required observations are missing.
"""
import argparse
import csv
import json
import math
import sys
from pathlib import Path

def read_csv(path):
    with open(path,newline='',encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

def qualify(path, name, start='2013-01', end='2024-09', expected_basis=None):
    q=Path(path)
    assert q.is_file(), f'{name} missing: {q}'
    rows=read_csv(q)
    assert rows, f'{name}: empty file'
    req={'month','value','source_url','source_type','series_id','price_convention','return_basis'}
    assert req.issubset(rows[0]), f'{name}: required fields missing: {req-set(rows[0])}'
    dates=[r['month'] for r in rows if start<=r['month']<=end]
    for r in rows:
        assert r['month'] and len(r['month'])==7 and r['month'][4]=='-', f'{name}: invalid month'
        assert r['source_url'].startswith('https://'), f'{name}: missing source URL'
        assert r['source_type'].upper()=='PRIMARY', f'{name}: non-primary series flagged: {r["source_type"]}'
        assert r['series_id'] and r['price_convention'] and r['return_basis'], f'{name}: missing provenance'
        assert math.isfinite(float(r['value'])) and float(r['value'])>0, f'{name}: invalid level'
        if expected_basis:
            assert r['return_basis'].upper()==expected_basis.upper(),f'{name}: wrong basis: {r["return_basis"]}'
    assert len(dates)==len(set(dates)), f'{name}: duplicates'
    assert len(set((r['series_id'],r['return_basis']) for r in rows))==1, f'{name}: multiple series/bases in one input'
    periods=[]
    for y in range(int(start[:4]),int(end[:4])+1):
        for m in range(1,13):
            ym=f'{y}-{m:02d}'
            if start<=ym<=end:periods.append(ym)
    missing=sorted(set(periods)-set(dates))
    assert not missing, f'{name}: missing {len(missing)} months: {missing[:10]}'
    return {'name':name,'source_path':str(q),'n_months':len(dates),'start':start,'end':end,
            'series_id':rows[0]['series_id'],'source_url':rows[0]['source_url'],
            'return_basis':rows[0]['return_basis'],'status':'STRUCTURE_PASS_PROVENANCE_SUBJECT_TO_INDEPENDENT_AUDIT'}

def qualify_nav(path):
    q=Path(path)
    assert q.is_file(), f'NAV input missing: {q}'
    rows=read_csv(q)
    req={'scheme_code','month','value','source_url','source_type','series_id','price_convention','return_basis','plan','option','nav_date'}
    assert rows and req.issubset(rows[0]),f'NAV missing required fields: {req-set(rows[0]) if rows else req}'
    groups={}
    for r in rows:
        assert r['source_url'].startswith('https://') and r['source_type'].upper()=='PRIMARY','NAV provenance missing'
        assert r['scheme_code'] and r['series_id'],'scheme code not present'
        assert r['plan'].strip().upper()=='DIRECT' and r['option'].strip().upper()=='GROWTH','NAV must be Direct-Growth'
        assert r['return_basis'].upper()=='NAV_GROWTH','NAV return basis invalid'
        assert len(r['month'])==7 and r['month'][4]=='-' and float(r['value'])>0, 'NAV date or value invalid'
        assert r['nav_date'][:7]==r['month'], 'NAV as-of and price month differ'
        groups.setdefault(r['scheme_code'],[]).append(r)
    details=[]
    for code,records in groups.items():
        m=sorted(r['month'] for r in records)
        assert len(m)==len(set(m)),f'duplicate NAV month for {code}'
        dates=[int(x[:4])*12+int(x[5:7]) for x in m]
        assert dates==list(range(dates[0],dates[-1]+1)),f'NAV data gap for {code}'
        assert len(m)>=24,f'NAV fewer than 24 monthly observations for {code}'
        details.append({'scheme_code':code,'start':m[0],'end':m[-1],'n_months':len(m),
                        'status':'TRACKING_ANALYSIS_ELIGIBLE_ONLY; never backfill pre-inception returns'})
    return {'name':'AMFI Actual Fund NAV','schemes':details,'status':'STRUCTURE_PASS_PROVENANCE_SUBJECT_TO_INDEPENDENT_AUDIT'}

def main():
    p=argparse.ArgumentParser()
    for f in ['cpi','equity','gsec','gold','silver','nav']:
        p.add_argument('--'+f,required=False)
    args=p.parse_args()
    data=vars(args)
    if not all(data.values()):
        print(json.dumps({'status':'REJECT','reason':'All six qualified source inputs required; no substitute/proxy accepted',
                         'missing':[k for k,v in data.items() if not v]},indent=2))
        return 2
    # The linked CPI is reconstructed from official reported observations and
    # intentionally has a special input schema; it is never mislabeled as
    # a downloaded official data export.
    ci=read_csv(data['cpi'])
    assert len(ci)>=144 and {'month','index_2024base','source_label','source_url'}.issubset(ci[0]), 'CPI linked schema missing'
    assert sum(r['month']<='2024-12' for r in ci)==144, 'CPI linked 2013-24 incomplete'
    assert all(float(r['index_2024base'])>0 for r in ci), 'CPI nonpositive'
    checks=[qualify(data['equity'],'Nifty500 TRI',expected_basis='TRI'),
            qualify(data['gsec'],'GSec Total Return',expected_basis='TRI'),
            qualify(data['gold'],'Domestic Gold',expected_basis='MUMBAI_MONTHLY_AVERAGE'),
            qualify(data['silver'],'Domestic Silver',expected_basis='MUMBAI_MONTHLY_AVERAGE'),
            qualify_nav(data['nav'])]
    print(json.dumps({'status':'STRUCTURAL_DATA_GATE_PASS','qualified':checks,
                      'disclaimer':'Does not yet validate forecasts, actual trades, candidate suitability or investor floor.'},indent=2))
    return 0

if __name__=='__main__':sys.exit(main())