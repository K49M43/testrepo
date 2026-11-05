from __future__ import annotations
import argparse,csv,datetime as dt,decimal,hashlib,json,pathlib,time,urllib.error,urllib.request
from urllib.parse import urlencode
D=decimal.Decimal
CANDIDATES={
 'SBI_GILT_JUNE2036_FUND':{'scheme_code':'150681','isin':'INF200KA12Q9','scheme_name':'SBI CRISIL IBX Gilt Index - June 2036 Fund','nav_name_tokens':['CRISIL IBX Gilt Index - June 2036 Fund','Direct Plan','Growth'],'start':'2022-10-04','end':'2026-10-31','analysis_scope':'from product inception 2022-10-04 through 2026-10-31; no pre-inception rows'},
 'HDFC_GOLD_ETF':{'scheme_code':'113049','isin':'INF179KC1981','scheme_name':'HDFC Gold ETF','nav_name_tokens':['HDFC Gold ETF','Growth Option'],'start':'2015-01-01','end':'2026-10-31','analysis_scope':'2015-01 through 2026-10 common-analysis window; not full product lifetime (inception 2010-08-13)'},
 'ICICI_SILVER_ETF':{'scheme_code':'149464','isin':'INF109KC1Y56','scheme_name':'ICICI Prudential Silver ETF','nav_name_tokens':['ICICI Prudential Silver ETF'],'start':'2022-01-24','end':'2026-10-31','analysis_scope':'from product allotment 2022-01-24 through 2026-10-31; no pre-inception rows'}
}
ROOT=pathlib.Path('research/stage512/2026-11-05/source_retrieval_followup/candidates')

def windows(a,b):
 out=[];cur=a
 while cur<=b:
  y=cur.year+(cur.month+5)//12;m=(cur.month+5)%12+1;end=min(dt.date(y,m,1)-dt.timedelta(days=1),b);out.append((cur,end));cur=end+dt.timedelta(days=1)
 return out

def run(name,cfg):
 code=cfg['scheme_code']; start=dt.date.fromisoformat(cfg['start']);end=dt.date.fromisoformat(cfg['end']);segments=windows(start,end);allrows={};sources=[];halt=None
 manifest_path=ROOT/f'nav_{code}_manifest.json'; old=json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
 for i,(a,b) in enumerate(segments):
  rawpath=ROOT/f'nav_{code}_{a}_{b}.json'
  url='https://www.amfiindia.com/api/nav-history?'+urlencode({'query_type':'historical_period','from_date':a.isoformat(),'to_date':b.isoformat(),'sd_id':code})
  cached=rawpath.exists()
  response_evidence=None
  try:
   if cached:raw=rawpath.read_bytes();status=200
   else:
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (G5.4 bounded official source qualification)','Accept':'application/json','Accept-Encoding':'identity','Referer':'https://www.amfiindia.com/net-asset-value/nav-history'})
    with urllib.request.urlopen(req,timeout=35) as rsp:status=rsp.status;raw=rsp.read(3_000_001)
    if raw:
     rawpath.write_bytes(raw)
     response_evidence={'response_status':status,'response_bytes':len(raw),'response_sha256':hashlib.sha256(raw).hexdigest(),'raw_path':str(rawpath)}
    if status!=200 or not raw or len(raw)>3_000_000:raise ValueError(f'HTTP {status}, bytes={len(raw)}')
   body=json.loads(raw).get('data'); groups=body.get('nav_groups') if isinstance(body,dict) else None
   if not isinstance(body,dict) or not isinstance(groups,list) or len(groups)!=1:raise ValueError('missing/ambiguous AMFI scheme response')
   if cfg['scheme_name'].lower() not in body.get('scheme_name','').lower():raise ValueError(f'wrong scheme group {body.get("scheme_name")}')
   group=groups[0]; nav_name=group.get('nav_name','')
   if any(tok.lower() not in nav_name.lower() for tok in cfg['nav_name_tokens']):raise ValueError(f'wrong option/plan {nav_name}')
   records=group.get('historical_records');
   if not isinstance(records,list) or not records:raise ValueError('empty historical_records')
   parsed=[]
   for r in records:
    day=dt.date.fromisoformat(r['date']);nav=D(str(r['nav']));opt=r.get('Option');opt=str(opt).strip().lower() if opt is not None else ''
    if day<a or day>b or not nav.is_finite() or nav<=0:raise ValueError(f'invalid date/NAV {day} {nav}')
    if opt and 'growth' not in opt:raise ValueError(f'unexpected option {opt}')
    parsed.append((day,nav))
   if len({x[0] for x in parsed})!=len(parsed):raise ValueError('duplicate date within segment')
   if not cached and not rawpath.exists():rawpath.write_bytes(raw)
   prior=next((x for x in old.get('segments',[]) if x.get('start')==a.isoformat() and x.get('end')==b.isoformat() and x.get('sha256')==hashlib.sha256(raw).hexdigest()),None)
   m={'start':a.isoformat(),'end':b.isoformat(),'url':url,'http_status':status,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'retrieved_utc':prior.get('retrieved_utc') if prior else (dt.datetime.now(dt.timezone.utc).isoformat() if not cached else 'cached; original timestamp unavailable'),'cached':cached,'records':len(parsed),'first':min(x[0] for x in parsed).isoformat(),'last':max(x[0] for x in parsed).isoformat(),'scheme_name':body['scheme_name'],'nav_name':nav_name}
   for day,value in parsed:
    if day in allrows and allrows[day]!=value:raise ValueError(f'conflicting duplicate date {day}')
    allrows[day]=value
   sources.append(m);print(f'{name} PASS {a}..{b}: {len(parsed)} rows, {m["sha256"]}',flush=True)
  except urllib.error.HTTPError as e:
   halt={'start':a.isoformat(),'end':b.isoformat(),'http_status':e.code,'error':str(e),'stop_no_retry':True};print(f'{name} HALT {json.dumps(halt)}',flush=True);break
  except Exception as e:
   halt={'start':a.isoformat(),'end':b.isoformat(),'error':f'{type(e).__name__}: {e}','stop_no_retry':True,**(response_evidence or {})};print(f'{name} HALT {json.dumps(halt)}',flush=True);break
  if not cached and i<len(segments)-1:time.sleep(3)
 ordered=sorted(allrows.items());gaps=[(x[0].isoformat(),y[0].isoformat(),(y[0]-x[0]).days) for x,y in zip(ordered,ordered[1:]) if (y[0]-x[0]).days>12]
 csvpath=ROOT/f'nav_{code}_daily.csv'
 with csvpath.open('w',newline='',encoding='utf8') as f:
  w=csv.writer(f,lineterminator='\n');w.writerow(['date','scheme_code','isin','scheme_name','nav_name','nav','segment_sha256'])
  for day,value in ordered:
   src=next(x for x in sources if x['start']<=day.isoformat()<=x['end']);w.writerow([day.isoformat(),code,cfg['isin'],src['scheme_name'],src['nav_name'],str(value),src['sha256']])
 complete=len(sources)==len(segments) and not gaps and bool(ordered)
 manifest={'schema_version':1,'record_id':f'g5-4-amfi-nav-{code}-2026-11-05-v1','candidate_id':name,'scheme_code':code,'isin':cfg['isin'],'analysis_scope':cfg['analysis_scope'],'source':'official AMFI scheme-specific historical NAV API','request_protocol':'sequential <=6-calendar-month source windows, saved raw responses, 3-second inter-request delay, stop immediately on first 429/error, no retry','status':'PASS_COMPLETE_DECLARED_WINDOW' if complete else 'PARTIAL_UNQUALIFIED','requested_segments':len(segments),'retrieved_segments':len(sources),'observations':len(ordered),'first_observation':ordered[0][0].isoformat() if ordered else None,'last_observation':ordered[-1][0].isoformat() if ordered else None,'gaps_over_12_days':gaps,'segments':sources,'halt':halt,'normalized_csv_sha256':hashlib.sha256(csvpath.read_bytes()).hexdigest()}
 manifest_path.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8');print(f'{name} RESULT '+json.dumps({'status':manifest['status'],'segments':len(sources),'requested':len(segments),'rows':len(ordered),'first':manifest['first_observation'],'last':manifest['last_observation'],'gap_count':len(gaps),'halt':halt}),flush=True)
 return manifest
p=argparse.ArgumentParser();p.add_argument('--candidate',choices=list(CANDIDATES),required=True);args=p.parse_args();run(args.candidate,CANDIDATES[args.candidate])
