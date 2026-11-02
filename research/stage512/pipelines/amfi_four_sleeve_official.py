#!/usr/bin/env python3
"""Stage 5.12: official AMFI per-scheme 36-month NAV qualification.

Exploratory four-sleeve cohort, not a portfolio recommendation.
Fail closed: no returns derived if any identifier, spot check, or coverage check fails.
Archive official source SHA256 values and qualified rows. Third-party NAV mirrors
are used ONLY to identify a research cohort; validation anchors are previous
official AMFI snapshots already committed to Stage 5.8.
"""
from __future__ import annotations
import csv, datetime as dt, hashlib, json, math, statistics, time
import urllib.parse, urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path("research")
OUT = REPO / "stage512/data/amfi_official_36m"
OUT.mkdir(parents=True, exist_ok=True)
API = "https://www.amfiindia.com/api/nav-history"
START, END = dt.date(2023, 9, 25), dt.date(2026, 10, 30)
COHORT = {
    "147625": {"asset": "equity", "expected": "Nifty 500"},
    "119116": {"asset": "gilt_fund", "expected": "Gilt"},
    "105463": {"asset": "gold_etf", "expected": "Gold"},
    "150556": {"asset": "silver_etf", "expected": "Silver"},
}
DATE_FMT = "%Y-%m-%d"
def http_bytes(url, timeout=60):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Stage512 official-source research validation)",
        "Accept": "application/json", "Accept-Encoding": "identity",
        "Referer": "https://www.amfiindia.com/net-asset-value/nav-history"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read(5_000_001)
        if r.status != 200 or len(raw) > 5_000_000:
            raise ValueError(f"Unexpected HTTP status/size: {r.status}/{len(raw)}")
    return raw
def api_url(code, a, b):
    return API+"?"+urllib.parse.urlencode({
        "query_type": "historical_period",
        "from_date": a.isoformat(), "to_date": b.isoformat(), "sd_id": code})
def segments():
    # Capped API windows; all consecutive with no duplicate calendar days.
    return [(dt.date(2023,9,25),dt.date(2024,9,24)),
            (dt.date(2024,9,25),dt.date(2025,9,24)),
            (dt.date(2025,9,25),dt.date(2026,10,30))]
def get_segment(code,a,b):
    url=api_url(code,a,b);errors=[]
    for attempt in range(2):
        try:
            raw=http_bytes(url,timeout=65)
            raw_path=OUT/"raw"/code
            raw_path.mkdir(parents=True,exist_ok=True)
            (raw_path/(a.isoformat()+"_"+b.isoformat()+".json")).write_bytes(raw)
            x=json.loads(raw)
            if not isinstance(x,dict) or not isinstance(x.get("data"),dict):
                raise ValueError("Unexpected AMFI response schema")
            body=x["data"];groups=body.get("nav_groups")
            if not isinstance(groups,list) or len(groups)!=1 or not isinstance(groups[0],dict):
                raise ValueError("Ambiguous AMFI plan/option group")
            records=groups[0].get("historical_records")
            if not isinstance(records,list):
                raise ValueError("historical_records missing")
            out=[]
            for rec in records:
                date=dt.date.fromisoformat(str(rec["date"]))
                nav=float(rec["nav"])
                if not (a<=date<=b and math.isfinite(nav) and nav>0):
                    raise ValueError(f"Invalid or out-of-range NAV for {code}: {date}")
                out.append((date,nav))
            if len(out)<5: raise ValueError("Historical segment shorter than five priced days")
            return out,{"url":url,"start":str(a),"end":str(b),
                        "sha256":hashlib.sha256(raw).hexdigest(),
                        "bytes":len(raw),"records":len(out),
                        "mf_name":body.get("mf_name"),"scheme_name":body.get("scheme_name"),
                        "nav_name":groups[0].get("nav_name")}
        except Exception as exc:
            errors.append(f"{type(exc).__name__}: {exc}")
            if attempt==0:time.sleep(2)
    raise RuntimeError(" | ".join(errors))
def get_code(code, expected):
    rows=[];meta=[]
    for a,b in segments():
        records,source=get_segment(code,a,b)
        if expected.casefold() not in (str(source.get("scheme_name",""))+" "+str(source.get("nav_name",""))).casefold():
            raise ValueError(f"Unexpected official scheme identity for {code}")
        rows.extend(records);meta.append(source)
    m={}
    for date,nav in rows:
        if date in m and abs(m[date]-nav)>0.0002:raise ValueError("Conflicting NAV for same day")
        m[date]=nav
    data=sorted(m.items())
    if (data[-1][0]-data[0][0]).days<1000:
        raise ValueError("Less than 1000 days of source coverage")
    return data,meta
def anchors():
    p=REPO/"stage58/official_nav_reconciliation.csv"
    out=defaultdict(dict)
    with p.open(newline="",encoding="utf8") as fh:
        for r in csv.DictReader(fh):
            if r["scheme_code"] in COHORT and r["official_nav"]:
                out[r["scheme_code"]][dt.date.fromisoformat(r["date"])]=float(r["official_nav"])
    return out
def pct_vol(returns):
    return statistics.stdev(returns)*math.sqrt(12)*100
def monthly_close(series):
    out={}
    for d,p in series:
        out[d.year*12+d.month]=(d,p)
    return out
def compute():
    source_anchors=anchors()
    evidence=[];selected={}
    overall={"status":"FAIL_INCOMPLETE","asof_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
             "source":"Official AMFI per-scheme history JSON, not mfapi.in",
             "period":[START.isoformat(),END.isoformat()],
             "target_investment_gate":"NO_GO","full_10y_forecast_validated":False,
             "records":[],"source_manifest":[],"errors":[]}
    def fetch_one(item):
        code, identity = item
        try:
            return code, get_code(code, identity["expected"]), None
        except Exception as exc:
            return code, None, f"{type(exc).__name__}: {exc}"
    # At most two simultaneous official AMFI requests; bounded for access stability.
    with ThreadPoolExecutor(max_workers=2) as pool:
        fetched = list(pool.map(fetch_one, COHORT.items()))
    for code, payload, acquisition_error in fetched:
        identity = COHORT[code]
        row={"code":code,"asset":identity["asset"],"status":"FAIL"}
        try:
            if acquisition_error:
                raise RuntimeError(acquisition_error)
            series,meta=payload
            points=dict(series)
            checked=[(d,nav,points[d]) for d,nav in source_anchors.get(code,{}).items() if d in points]
            mismatches=[(str(d),a,b) for d,a,b in checked if abs(a-b)>max(.0002,abs(a)*.0001)]
            if len(checked)<3 or mismatches:
                raise ValueError(f"Official snapshot checks insufficient/mismatched {len(checked)}: {mismatches[:3]}")
            # Reject unknown large NAV changes; investigate splits/corporate actions separately.
            jumps=[(str(d),b/a) for (_,a),(d,b) in zip(series,series[1:]) if b/a<.6 or b/a>1.66667]
            if jumps:
                raise ValueError(f"Unadjusted unit split / anomalous NAV jump: {jumps[:3]}")
            month=monthly_close(series)
            month_returns={}
            for k in sorted(month):
                if k-1 in month:
                    month_returns[k]=math.log(month[k][1]/month[k-1][1])
            row.update(status="PASS_OFFICIAL_36M_COHORT",samples=len(series),
                       first=series[0][0].isoformat(),last=series[-1][0].isoformat(),
                       official_snapshot_checks=len(checked),mismatches=0,
                       months_of_return=len(month_returns),
                       annualized_volatility_pct=round(pct_vol(list(month_returns.values())),4))
            selected[identity["asset"]]=month_returns
            for d,nav in series:
                evidence.append([identity["asset"],code,d.isoformat(),f"{nav:.8f}"])
            overall["source_manifest"].extend([{"code":code,**m} for m in meta])
        except Exception as exc:
            row["error"]=f"{type(exc).__name__}: {exc}"
            overall["errors"].append(row)
        overall["records"].append(row)
    with (OUT/"official_nav_four_assets.csv").open("w",newline="",encoding="utf8") as fh:
        w=csv.writer(fh);w.writerow(["asset","amfi_code","date","nav"]);w.writerows(evidence)
    if len(selected)==4:
        common=set.intersection(*(set(m.keys()) for m in selected.values()))
        common=sorted(common)
        if len(common)>=30:
            names=list(selected)
            samples={name:[selected[name][k] for k in common] for name in names}
            correlations={}
            for i,a in enumerate(names):
                for b in names[i:]:
                    av,bv=samples[a],samples[b]
                    ma,mb=statistics.mean(av),statistics.mean(bv)
                    cov=sum((x-ma)*(y-mb) for x,y in zip(av,bv))/(len(av)-1)
                    den=statistics.stdev(av)*statistics.stdev(bv)
                    correlations[a+"__"+b]=round(cov/den,5) if den>0 else None
            overall["cross_asset_result"]={"months":len(common),
                "start_month":f"{(common[0]-1)//12}-{(common[0]-1)%12+1:02d}",
                "end_month":f"{(common[-1]-1)//12}-{(common[-1]-1)%12+1:02d}",
                "correlations":correlations,
                "annualized_volatility_pct":{k:round(pct_vol(v),4) for k,v in samples.items()}}
            overall["status"]="PASS_36M_COHORT_ONLY"
        else: overall["errors"].append({"error":f"Only {len(common)} aligned months of returns"})
    (OUT/"qualification_manifest.json").write_text(json.dumps(overall,indent=2),encoding="utf8")
    print(json.dumps({"status":overall["status"],"rows":overall["records"],"aligned":overall.get("cross_asset_result",{}).get("months")},indent=2))
    return overall["status"]=="PASS_36M_COHORT_ONLY"
if __name__=="__main__":
    raise SystemExit(0 if compute() else 2)
