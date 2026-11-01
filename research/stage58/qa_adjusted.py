#!/usr/bin/env python3
"""Split-adjusted NAV risk metrics, verified dates/ratios, unresolved-event quarantine."""
import csv,json,math,statistics
from datetime import datetime,date,timedelta
from pathlib import Path
BASE=Path("research/stage58"); RAW=Path("output/raw_json"); CUT=date(2026,10,31)
# code, ex-date, split ratio (new units for old unit), public listing/depository source
SPLITS=[
 ("140088","2019-12-19",100,"https://www.msei.in/SX-Content/Circulars/2019/December/Circular-8430.pdf"),
 ("113076","2016-06-09",10,"https://www.msei.in/markets/equity/get-quotes/etf?series=EQ&symbol=GOLDIETF"),
 ("113076","2018-11-15",10,"https://www.msei.in/markets/equity/get-quotes/etf?series=EQ&symbol=GOLDIETF"),
 ("111954","2022-01-06",100,"https://www.msei.in/SX-Content/Circulars/2022/January/Circular-11335.pdf"),
 ("113049","2021-02-17",100,"https://www.nseindia.com/get-quote/equity/HDFCGOLD/HDFC-Gold-ETF"),
 ("106193","2015-04-13",10,"https://www.nseindia.com/companies-listing/corporate-filings-actions?symbol=GOLD1"),
 ("106193","2021-07-22",10,"https://www.nseindia.com/companies-listing/corporate-filings-actions?symbol=GOLD1"),
 ("113434","2020-07-23",100,"https://piickr.in/index.php/etfs/GOLDAXIS"),
 ("105463","2021-03-25",100,"https://www.nseindia.com/get-quote/equity/GOLDBETA/UTI-Mutual-Fund---UTI-Gold-Exchange-Traded-Fund"),
 ("151737","2026-08-28",10,"https://noticeblue.com/circulars/fea4cdf3-f639-4811-bc82-298e4160ff8a"),
 ("150948","2026-02-27",10,"https://nsearchives.nseindia.com/content/circulars/CML72916.pdf"),
 ("150523","2026-08-28",10,"https://noticeblue.com/circulars/fea4cdf3-f639-4811-bc82-298e4160ff8a")
]
bycode={}
for c,d,k,url in SPLITS:bycode.setdefault(c,[]).append((date.fromisoformat(d),k,url))
def write(n,rows,cols):
 with (BASE/n).open("w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=cols,extrasaction="ignore");w.writeheader();w.writerows(rows)
def get(pts,when):
 x=[(d,v) for d,v in pts if 0<=(when-d).days<=10]
 return x[-1] if x else None
def maxdd(pts):
 peak=pts[0][1];dd=0.
 for d,v in pts:peak=max(peak,v);dd=min(dd,v/peak-1)
 return round(100*dd,5)
official={}
p=BASE/"qa_metrics.csv"
if p.exists():
 for x in csv.DictReader(p.open()):official[x["scheme_code"]]=x
adjustments=[];res=[];risk={};monthly={}
for f in sorted(RAW.glob("*.json")):
 code=f.stem;obj=json.loads(f.read_text());meta=obj.get("meta") or {}
 vals={}
 for r in obj.get("data",[]):
  try:
   d=datetime.strptime(r["date"],"%d-%m-%Y").date();v=float(r["nav"])
   if d<=CUT and v>0 and math.isfinite(v):vals[d]=v
  except:pass
 pts=sorted(vals.items())
 if len(pts)<2:continue
 approved=[]
 for d,k,url in bycode.get(code,[]):
  # Match the *observed* discontinuity, whose NAV publication date can lag exchange ex-date.
  candidates=[]
  for ix in range(1,len(pts)):
   pday,pnav=pts[ix-1];day,nav=pts[ix]
   ratio=nav/pnav
   if abs((day-d).days)<=10 and (day-pday).days<=12 and abs(ratio*k-1)<0.30:
    candidates.append((day,ratio))
  if candidates:
   day,ratio=min(candidates,key=lambda z:abs((z[0]-d).days))
   approved.append((day,k))
   status="OBSERVED_NAV_BREAK_MATCHES_DOCUMENTED_SPLIT"
  else:
   ratio=None
   status="DOCUMENTED_SPLIT_BUT_NO_MATCHED_DAILY_BREAK"
  adjustments.append(dict(scheme_code=code,ex_date=str(d),factor=k,observed_ratio=round(ratio,8) if ratio else "",
       status=status,source_url=url))
 adjusted=[]
 for day,v in pts:
  mul=1
  for ex,k in approved:
   if day<ex:mul*=k
  adjusted.append((day,v/mul))
 bad=[]
 for i in range(1,len(adjusted)):
  pday,pnav=adjusted[i-1];day,nav=adjusted[i];rr=nav/pnav
  if rr<.60 or rr>1.66667:bad.append((day,rr))
 # Preserve only clean monthly change sequences.
 month={}
 for d,v in adjusted:month[d.year*12+d.month]=(d,v)
 rets={}
 for k in sorted(month):
  if k-1 not in month:continue
  prev,v0=month[k-1];cur,v1=month[k]
  if any(prev < day<=cur for day,rr in bad):continue
  rets[k]=v1/v0-1
 end=adjusted[-1][0];terminal=end.year*12+end.month
 vec=[rets.get(terminal-i) for i in range(35,-1,-1)]
 if all(v is not None for v in vec):
  risk[code]=vec
 cagr={}
 for yr in [1,3,5,10]:
  anchor=end-timedelta(days=round(365.2425*yr))
  start=get(adjusted,anchor)
  if not start or adjusted[0][0]>anchor or any(start[0]<day<=end for day,rr in bad):
   cagr[f"cagr_{yr}y_pct"]=""
  else:cagr[f"cagr_{yr}y_pct"]=round(100*((adjusted[-1][1]/start[1])**(365.2425/(end-start[0]).days)-1),5)
 last5=end-timedelta(days=round(365.2425*5))
 subset=[(d,v) for d,v in adjusted if d>=last5]
 clean5=adjusted[0][0]<=last5 and not any(day>=last5 for day,rr in bad)
 am=official.get(code,{})
 matches=int(am.get("official_nav_matches",0));fails=int(am.get("official_nav_failures",0))
 status=("PASS_SAMPLED_OFFICIAL" if matches>=1 and fails==0 else "OFFICIAL_RECONCILIATION_OPEN")
 item=dict(scheme_code=code,scheme_name=meta.get("scheme_name",""),n_obs=len(adjusted),
  corporate_actions_applied=len(approved),unresolved_daily_jumps=len(bad),
  first_date=str(adjusted[0][0]),last_date=str(end),last_nav=adjusted[-1][1],
  full_history_max_dd_pct=maxdd(adjusted) if not bad else "",
  dd_5y_pct=maxdd(subset) if clean5 and subset else "",
  vol_36m_pct=round(100*statistics.stdev(vec)*math.sqrt(12),5) if code in risk else "",
  official_nav_matches=matches,official_nav_failures=fails,
  official_status=status,history_status=("CLEAN" if not bad else "PARTIALLY_QUARANTINED"),
  correlation_status=("ELIGIBLE" if code in risk and matches and not fails else "BLOCKED"),
  **cagr)
 res.append(item)
write("adjusted_nav_metrics.csv",res,list(res[0]))
write("split_adjustment_audit.csv",adjustments,["scheme_code","ex_date","factor","observed_ratio","status","source_url"])
cleanrisk={c:v for c,v in risk.items() if int(official.get(c,{}).get("official_nav_matches",0))>=1 and int(official.get(c,{}).get("official_nav_failures",0))==0}
def corr(a,b):
 ma=statistics.mean(a);mb=statistics.mean(b)
 den=math.sqrt(sum((v-ma)**2 for v in a)*sum((v-mb)**2 for v in b))
 return sum((v-ma)*(w-mb) for v,w in zip(a,b))/den if den else None
cor=[]
cc=sorted(cleanrisk)
for i,a in enumerate(cc):
 for b in cc[i:]:
  v=corr(cleanrisk[a],cleanrisk[b])
  if v is not None:cor.append(dict(scheme_a=a,scheme_b=b,correlation=round(v,8),months=36,status="OFFICIAL_SAMPLED_AND_UNIT_ADJUSTED"))
write("adjusted_correlations_36m.csv",cor,["scheme_a","scheme_b","correlation","months","status"])
summary=dict(n_schemes=len(res),
 official_reconciled=sum(x["official_status"]=="PASS_SAMPLED_OFFICIAL" for x in res),
 corporate_action_events=len(adjustments),
 corporate_action_events_matched=sum(x["status"]=="EVENT_MATCHED" for x in adjustments),
 unresolved_scheme_jumps=sum(x["unresolved_daily_jumps"]>0 for x in res),
 clean_36m_n=len(risk),official_verified_clean_36m_n=len(cleanrisk),
 approved_pairs=len(cor),no_official=sum(x["official_status"]!="PASS_SAMPLED_OFFICIAL" for x in res),
 stage58_closed=(len(res)==96 and all(x["official_status"]=="PASS_SAMPLED_OFFICIAL" for x in res)
     and not any(x["unresolved_daily_jumps"] for x in res)),
 note="Full-history results are split-adjusted only for exchange-verified, raw-date-matched events. Unresolved jumps remain quarantined. NAV histories are third-party sourced and sampled against AMFI official NAVs.")
BASE.joinpath("stage58_final_gates.json").write_text(json.dumps(summary,indent=2))
print(json.dumps(summary))
