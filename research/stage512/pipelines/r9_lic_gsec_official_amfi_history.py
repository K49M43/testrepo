#!/usr/bin/env python3
"""Stage 5.12 R9: historical direct-AMFI ETF NAV for index-tracking government bonds.

LIC MF Nifty 8-13 yr G-Sec ETF: scheme code 133307, ISIN INF767K01MV5.
The ETF's own official NAV history is NOT the NSE index total-return history.
Source: first-party AMFI scheme NAV JSON API. Offline standard-library parser.
Acquires bounded, nonoverlapping periods with 2 simultaneous requests; archives
exact raw bytes through GitHub Actions artifacts; records SHA256 and rejects
inconsistent scheme names, invalid NAV, duplicate/conflicting dates, price jumps.
Verification vs first-party LIC factsheet return windows: 31 Mar 2026, 1/3/5 yr.
"""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
import csv,datetime as dt,hashlib,json,math,time
BASE=Path("research/stage512/data/r9_lic_gsec_etf")
URL="https://www.amfiindia.com/api/nav-history"
CODE="133307"
ISIN="INF767K01MV5"
START=dt.date(2014,12,26)
END=dt.date(2026,10,30)
EXPECTED="Nifty 8-13"
# Official 31 March 2026 LIC MF factsheet (annualized percent), plus published
# Nifty benchmark returns. The benchmark data is NOT generated from ETF NAV.
LIC_MARCH26={"1":3.18,"3":7.15,"5":5.49,"since":6.89}
NSE_MARCH26={"1":3.32,"3":7.33,"5":5.75,"since":7.21}
REFERENCE="https://www.licmf.com/assets/downloads/monthly_fact_sheet/2026-2027/04/lic-mf-factsheet-31st-March-2026.pdf"
def segments():
    out=[]
    a=START
    while a<=END:
        # Six calendar months: verified by R9.2 across 2015/2018/2022/2026.
        # Long 18-month AMFI requests can hang or timeout.
        y=a.year+(a.month+5)//12
        mo=(a.month+5)%12+1
        cap=dt.date(y,mo,1)-dt.timedelta(days=1)
        b=min(cap,END)
        out.append((a,b))
        a=b+dt.timedelta(days=1)
    return out
def get_one(t):
    a,b=t
    url=URL+"?"+urlencode({"query_type":"historical_period","from_date":a.isoformat(),"to_date":b.isoformat(),"sd_id":CODE})
    evidence={"start":str(a),"end":str(b),"url":url,"status":"FAIL"}
    errs=[]
    for attempt in range(2):
        try:
            req=Request(url,headers={"User-Agent":"Mozilla/5.0 (Stage512 primary source audit)",
              "Accept":"application/json","Accept-Encoding":"identity",
              "Referer":"https://www.amfiindia.com/net-asset-value/nav-history"})
            with urlopen(req,timeout=32) as rsp:
                raw=rsp.read(3_000_001)
                status=rsp.status
            if status!=200 or len(raw)>3_000_000 or not raw:
                raise ValueError(f"HTTP {status}, bytes={len(raw)}")
            rawdir=BASE/"raw"
            rawdir.mkdir(parents=True,exist_ok=True)
            (rawdir/f"{a}_{b}.json").write_bytes(raw)
            x=json.loads(raw)
            body=x.get("data") if isinstance(x,dict) else None
            if not isinstance(body,dict):raise ValueError("AMFI data is missing")
            scheme=str(body.get("scheme_name",""))
            groups=body.get("nav_groups",[])
            if not isinstance(groups,list) or len(groups)!=1:raise ValueError("Ambiguous AMFI scheme groups")
            group=groups[0]
            name=str(group.get("nav_name",""))
            title=(scheme+" "+name).lower()
            if "nifty" not in title or "8-13" not in title or "g-sec" not in title:
                raise ValueError(f"Incorrect scheme name: {title[:120]}")
            data=group.get("historical_records")
            if not isinstance(data,list) or len(data)<5:raise ValueError("Historical records missing/short")
            rows=[]
            for r in data:
                d=dt.date.fromisoformat(str(r["date"]))
                nav=float(r["nav"])
                if d<a or d>b or not math.isfinite(nav) or nav<=0:
                    raise ValueError(f"Invalid NAV or date: {d} {nav}")
                opt=str(r.get("Option","")).lower()
                if opt and "growth" not in opt:
                    raise ValueError(f"Unexpected option: {opt}")
                rows.append((d,nav))
            if len({d for d,v in rows})!=len(rows):raise ValueError("Duplicate date")
            evidence.update(status="PASS_SOURCE_SEGMENT",n=len(rows),
                sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),
                scheme_name=scheme,nav_name=name,
                first=str(min(d for d,v in rows)),last=str(max(d for d,v in rows)))
            return rows,evidence
        except Exception as exc:
            errs.append(f"{type(exc).__name__}: {exc}")
            if attempt<1:time.sleep(2)
    evidence["errors"]=errs
    return [],evidence
def check_history(rows):
    s=sorted(rows)
    first=s[0][0];last=s[-1][0]
    if first>dt.date(2015,1,5) or last<dt.date(2026,10,26):
        raise ValueError("ETF 11-year history endpoints not covered")
    if len(s)<2500:raise ValueError("Too few priced NAVs for 11-year history")
    for (d,v),(e,w) in zip(s,s[1:]):
        if (e-d).days>12:raise ValueError(f"Unexpected long NAV date gap {d} to {e}")
        if w/v<0.5 or w/v>2:
            raise ValueError(f"Potential unadjusted split or discontinuity {d} -> {e}")
    return s
def on_or_before(day,ordered,lookback=6):
    eligible=[(d,v) for d,v in ordered if d<=day]
    if not eligible:raise ValueError(f"No entry before {day}")
    d,v=eligible[-1]
    if (day-d).days>lookback:raise ValueError(f"Stale NAV anchor for {day}: {d}")
    return d,v
def compare_lic(ordered):
    lastDate=dt.date(2026,3,31)
    ed,ev=on_or_before(lastDate,ordered)
    comparison=[]
    for years in [1,3,5]:
        anchor=dt.date(2026-years,3,31)
        sd,sv=on_or_before(anchor,ordered)
        actual=(ev/sv)**(1/years)*100-100
        stated=LIC_MARCH26[str(years)]
        # Fund-house factsheet annualized return uses precise year daycount,
        # so this is an approximate cross-check only; not a guaranteed equality.
        comparison.append({"period_years":years,"source_start":str(sd),"source_end":str(ed),
            "calculated_nav_cagr_pct":round(actual,6),"lic_factsheet_cagr_pct":stated,
            "abs_difference_pp":round(abs(actual-stated),6),
            "published_gsec_benchmark_cagr_pct":NSE_MARCH26[str(years)]})
    return comparison
def main():
    BASE.mkdir(parents=True,exist_ok=True)
    tasks=segments()
    with ThreadPoolExecutor(max_workers=4) as exe:
        outcomes=list(exe.map(get_one,tasks))
    sources=[s for records,s in outcomes]
    manifest={"status":"FAIL_INCOMPLETE","research_source_gate":"NO_GO_UNTIL_QUALIFIED",
        "scheme_code":CODE,"isin":ISIN,"scheme_name":"LIC MF Nifty 8-13 yr G-Sec ETF",
        "official_amfi_history":True,"nse_index_historical_total_return_acquired":False,
        "nav_is_tradable_etf_market_price":False,"full_2036_forecast_validated":False,
        "investment_authorization":"NO_GO","retrieved_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
        "segments":sources,"lic_reference_factsheet":REFERENCE,
        "lic_factsheet_2026_03_31":LIC_MARCH26,
        "nse_benchmark_return_snapshots_from_LIC_factsheet":NSE_MARCH26}
    try:
        if any(x["status"]!="PASS_SOURCE_SEGMENT" for x in sources):
            raise ValueError("Not all official source segments retrieved")
        prices={}
        for records,source in outcomes:
            for d,v in records:
                if d in prices and abs(prices[d]-v)>0.0002:
                    raise ValueError(f"Conflicting duplicate NAV for date {d}")
                prices[d]=v
        s=check_history(list(prices.items()))
        checks=compare_lic(s)
        failures=[x for x in checks if x["abs_difference_pp"]>0.14]
        if failures:raise ValueError(f"Fund house published CAGR comparison differs >0.14 pp: {failures}")
        output=BASE/"lic_gsec_133307_amfi_daily.csv"
        with output.open("w",newline="",encoding="utf8") as fh:
            w=csv.writer(fh);w.writerow(["date","amfi_scheme_code","nav_inr","source_type"])
            for d,v in s:w.writerow([d.isoformat(),CODE,f"{v:.8f}","AMFI_OFFICIAL_NAV"])
        monthly={}
        for d,v in s:monthly[d.strftime("%Y-%m")]=(d,v)
        mm=sorted(monthly)
        series=[]
        for prior,cur in zip(mm,mm[1:]):
            pd,pv=monthly[prior];cd,cv=monthly[cur]
            if (cd.year*12+cd.month)-(pd.year*12+pd.month)!=1:
                raise ValueError(f"Missing calendar NAV month {prior}->{cur}")
            series.append([cur,cd.isoformat(),math.log(cv/pv),100*(cv/pv-1)])
        with (BASE/"lic_gsec_133307_monthly_returns.csv").open("w",newline="",encoding="utf8") as fh:
            w=csv.writer(fh);w.writerow(["month","end_nav_date","log_nav_return","simple_nav_return_pct"]);w.writerows(series)
        vol=__import__("statistics").stdev([x[2] for x in series])*math.sqrt(12)*100
        manifest.update(status="PASS_OFFICIAL_NAV_11YR_RESEARCH_ONLY",
          observations=len(s),first=str(s[0][0]),last=str(s[-1][0]),
          months_of_return=len(series),annualized_monthly_log_nav_volatility_pct=round(vol,5),
          official_lic_factsheet_cagr_comparisons=checks,
          daily_source_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
          monthly_source_sha256=hashlib.sha256((BASE/"lic_gsec_133307_monthly_returns.csv").read_bytes()).hexdigest())
    except Exception as e:manifest["error"]=f"{type(e).__name__}: {e}"
    (BASE/"qualification_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf8")
    print(json.dumps({k:manifest.get(k) for k in ["status","observations","first","last",
      "months_of_return","annualized_monthly_log_nav_volatility_pct","error"]},indent=2))
    return 0 if manifest["status"]=="PASS_OFFICIAL_NAV_11YR_RESEARCH_ONLY" else 2
if __name__=="__main__":raise SystemExit(main())
