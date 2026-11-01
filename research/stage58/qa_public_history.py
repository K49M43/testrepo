#!/usr/bin/env python3
"""Public NAV source/identity QA, extreme-change quarantine, aligned historical correlations.
Never auto-adjust unit splits without matching corporate-action evidence.
"""
import csv,json,math,statistics,hashlib,urllib.request,time
from datetime import datetime,date,timedelta
from pathlib import Path
from collections import defaultdict
BASE=Path("research/stage58"); RAW=Path("output/raw_json"); CUT=date(2026,10,31)
BASE.mkdir(parents=True,exist_ok=True)
def dt(x):return datetime.strptime(x,"%d-%m-%Y").date()
def wr(name,cols,rows):
 with (BASE/name).open("w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=cols,extrasaction="ignore");w.writeheader();w.writerows(rows)
def req(url,timeout=18):
 rq=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (public investment research; citation AMFI)"})
 with urllib.request.urlopen(rq,timeout=timeout) as r:return r.read().decode("utf-8-sig","replace")
def official():
 """Use latest AMFI daily text plus four historical week-window reports; parse both formats."""
 records=defaultdict(dict);reports=[]
 sources=[("latest","https://portal.amfiindia.com/spages/NAVAll.txt",6)]
 for label,a,b in [
   ("Oct26","26-Oct-2026","31-Oct-2026"),
   ("Jun26","25-Jun-2026","30-Jun-2026"),
   ("Sep25","25-Sep-2025","30-Sep-2025"),
   ("Sep23","25-Sep-2023","30-Sep-2023")]:
  sources.append((label,f"https://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?frmdt={a}&todt={b}",8))
 for label,url,colcount in sources:
  data=None;error=""
  for attempt in range(1):
   try:
    data=req(url)
    if data.lower().find("<html")>=0 or len(data)<20000:raise ValueError(f"stub_html_or_short_response size={len(data)}")
    break
   except Exception as exc:
    error=str(exc);data=None;time.sleep(attempt+1)
  if data is None:
   reports.append(dict(source=label,url=url,status="FAILED",rows=0,error=error));continue
  n=0
  for line in data.splitlines():
   chunks=line.strip().split(";")
   if len(chunks)<colcount or not chunks[0].strip().isdigit():continue
   try:
    code=chunks[0].strip()
    if colcount==6:
     isin=chunks[1].strip();name=chunks[3].strip();nav=float(chunks[4]);d=dt(chunks[5].strip())
    else:
     isin=chunks[2].strip();name=chunks[1].strip();nav=float(chunks[4]);d=dt(chunks[7].strip())
    if d<=CUT and math.isfinite(nav) and nav>0:
     records[code][d]=(nav,name,isin,url,label);n+=1
   except Exception:pass
  reports.append(dict(source=label,url=url,status="OK" if n else "NO_RECORDS",rows=n,error=""))
 wr("official_source_reports.csv",["source","url","status","rows","error"],reports)
 return records,reports
def monthly(ret,end):
 terminal=end.year*12+end.month
 return [ret.get(terminal-i) for i in range(35,-1,-1)]
def corr(a,b):
 ma=statistics.mean(a);mb=statistics.mean(b)
 num=sum((x-ma)*(y-mb) for x,y in zip(a,b))
 den=math.sqrt(sum((x-ma)**2 for x in a)*sum((y-mb)**2 for y in b))
 return num/den if den else None
rows=[];all_points={};all_breaks={};outliers=[]
for p in sorted(RAW.glob("*.json")):
 code=p.stem;obj=json.loads(p.read_text());meta=obj.get("meta") or {}
 vals={}
 for x in obj.get("data",[]):
  try:
   d=dt(x["date"]);v=float(x["nav"])
   if d<=CUT and v>0 and math.isfinite(v):vals[d]=v
  except:pass
 pts=sorted(vals.items())
 all_points[code]=(meta,pts)
 jumps=[]
 for i in range(1,len(pts)):
  prior,old=pts[i-1];day,new=pts[i]
  r=new/old
  if r<0.6 or r>1.66667:
   jumps.append((day,prior,old,new,r))
   outliers.append(dict(scheme_code=code,source_scheme_name=meta.get("scheme_name",""),
      previous_date=str(prior),event_date=str(day),previous_nav=old,event_nav=new,
      ratio=round(r,9),suspected_event=("SPLIT_OR_DENOMINATION_CHANGE" if r<.2 or r>5 else "EXTREME_MARKET_OR_DATA_MOVE"),
      disposition="QUARANTINE_EVENT_WINDOW_UNTIL_CORPORATE_ACTION_VERIFIED"))
 all_breaks[code]=jumps
wr("qa_daily_breaks.csv",["scheme_code","source_scheme_name","previous_date","event_date","previous_nav","event_nav","ratio","suspected_event","disposition"],outliers)
official_rows,reports=official()
checks=[];metric=[];usable={}
for code,(meta,pts) in all_points.items():
 if not pts:continue
 anchors=official_rows.get(code,{})
 exact=[];differ=[]
 for d,(nav,name,isin,url,label) in sorted(anchors.items()):
  if d not in dict(pts):continue
  got=dict(pts)[d];delta=got-nav
  match=abs(delta)<=max(0.0002,nav*0.0001)
  identity_ok=(name.strip().casefold()==str(meta.get("scheme_name","")).strip().casefold())
  checks.append(dict(scheme_code=code,date=str(d),source=label,api_nav=got,official_nav=nav,
   nav_difference=round(delta,6),nav_pass=match,api_name=meta.get("scheme_name",""),
   amfi_name=name,scheme_name_exact_match=identity_ok,amfi_isin=isin,
   source_growth_isin=meta.get("isin_growth",""),amfi_url=url))
  (exact if match else differ).append(d)
 # Recent correlations require 36 consecutive month-end observations with no unadjusted jumps.
 monthly_nav={}
 for d,v in pts:monthly_nav[d.year*12+d.month]=(d,v)
 ret={}
 for k in sorted(monthly_nav):
  if k-1 not in monthly_nav:continue
  prior_d,old=monthly_nav[k-1];now_d,new=monthly_nav[k]
  break_crossing=any(prior_d < j[0]<=now_d for j in all_breaks[code])
  if not break_crossing:ret[k]=new/old-1
 end=pts[-1][0];v36=monthly(ret,end)
 ok36=all(x is not None for x in v36)
 if ok36:usable[code]=v36
 def safe_metric(source,yrs):
  begin=pts[-1][0]-timedelta(days=round(yrs*365.2425))
  return all(j[0]<begin for j in all_breaks[code])
 dates=[j[0] for j in all_breaks[code]]
 eligible_end= max(dates) if dates else pts[0][0]
 post=[(d,v) for d,v in pts if d>=eligible_end]
 # Start after the jump itself: NAV is post-action NAV.
 peak=post[0][1];dd=0
 for d,v in post:peak=max(peak,v);dd=min(dd,v/peak-1)
 rec=dict(scheme_code=code,scheme_name=meta.get("scheme_name",""),source_isin=meta.get("isin_growth",""),
   nav_observations=len(pts),first_date=str(pts[0][0]),last_date=str(end),
   official_points_compared=len(exact)+len(differ),official_nav_matches=len(exact),
   official_nav_failures=len(differ),official_coverage=("MATCHED" if exact and not differ else "FAIL" if differ else "NOT_VERIFIED"),
   daily_break_count=len(dates),post_last_break_date=str(eligible_end),
   post_break_max_dd_pct=round(dd*100,5),
   full_history_dd_status="QUARANTINE_UNADJUSTED_SPLIT" if dates else "CLEAR",
   five_year_dd_status="CLEAR" if safe_metric(pts,5) else "QUARANTINE_UNADJUSTED_SPLIT",
   cagr_1y_status="CLEAR" if safe_metric(pts,1) else "QUARANTINE_UNADJUSTED_SPLIT",
   cagr_3y_status="CLEAR" if safe_metric(pts,3) else "QUARANTINE_UNADJUSTED_SPLIT",
   cagr_5y_status="CLEAR" if safe_metric(pts,5) else "QUARANTINE_UNADJUSTED_SPLIT",
   cagr_10y_status="CLEAR" if safe_metric(pts,10) else "QUARANTINE_UNADJUSTED_SPLIT",
   vol_36m_status="CLEAR" if ok36 else "UNAVAILABLE_OR_QUARANTINED",
   vol_36m_pct=round(statistics.stdev(v36)*math.sqrt(12)*100,5) if ok36 else "",
   risk_qa_status=("QA_PASS" if exact and not differ and ok36 and not any(d>=end-timedelta(days=365*3) for d in dates) else "PARTIAL_OR_BLOCKED"))
 metric.append(rec)
wr("official_nav_reconciliation.csv",["scheme_code","date","source","api_nav","official_nav","nav_difference","nav_pass","api_name","amfi_name","scheme_name_exact_match","amfi_isin","source_growth_isin","amfi_url"],checks)
wr("qa_metrics.csv",list(metric[0].keys()),metric)
corrows=[];eligible=sorted(usable)
for i,a in enumerate(eligible):
 for b in eligible[i:]:
  c=corr(usable[a],usable[b])
  if c is not None:corrows.append(dict(code_a=a,code_b=b,correlation=round(c,8),months=36,status="QA_SAMPLED_OFFICIAL_ONLY"))
wr("qa_correlations_36m.csv",["code_a","code_b","correlation","months","status"],corrows)
summary=dict(scheme_series=len(all_points),official_source_reports=reports,
 official_covered=sum(r["official_points_compared"]>0 for r in metric),
 official_reconciled=sum(r["official_nav_matches"]>0 and r["official_nav_failures"]==0 for r in metric),
 official_failed=sum(r["official_nav_failures"]>0 for r in metric),
 daily_breaks=len(outliers),schemes_with_breaks=len({a["scheme_code"] for a in outliers}),
 clean_36m_schemes=len(eligible),clean_corr_pairs=len(corrows),
 qa_pass_schemes=sum(r["risk_qa_status"]=="QA_PASS" for r in metric),
 status="PARTIAL_QA; ETF unit-split events not back-adjusted. OFFICIAL historical reconciliation required for every scheme.")
BASE.joinpath("qa_summary.json").write_text(json.dumps(summary,indent=2))
print(json.dumps({k:v for k,v in summary.items() if k!="official_source_reports"}))
