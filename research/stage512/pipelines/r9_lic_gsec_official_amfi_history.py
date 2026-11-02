#!/usr/bin/env python3
"""Stage 5.12 R9: historical direct-AMFI ETF NAV for index-tracking government bonds.

LIC MF Nifty 8-13 yr G-Sec ETF: scheme code 133307, ISIN INF767K01MV5.
The ETF's own official NAV history is NOT the NSE index total-return history.
Source: first-party AMFI scheme NAV JSON API. Offline standard-library parser.
Acquires bounded, nonoverlapping six-month periods sequentially with rate limits; archives
exact raw bytes through GitHub Actions artifacts; records SHA256 and rejects
inconsistent scheme names, invalid NAV, duplicate/conflicting dates, price jumps.
Verification vs first-party LIC factsheet return windows: 31 Mar 2026, 1/3/5 yr.
"""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from urllib.error import HTTPError
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
    rawdir=BASE/"raw"
    rawdir.mkdir(parents=True,exist_ok=True)
    rawfile=rawdir/f"{a}_{b}.json"
    for attempt in range(3):
        try:
            cached=rawfile.is_file()
            if cached:
                raw=rawfile.read_bytes()
            else:
                req=Request(url,headers={"User-Agent":"Mozilla/5.0 (Stage512 primary source audit)",
                  "Accept":"application/json","Accept-Encoding":"identity",
                  "Referer":"https://www.amfiindia.com/net-asset-value/nav-history"})
                with urlopen(req,timeout=35) as rsp:
                    raw=rsp.read(3_000_001)
                    status=rsp.status
                if status!=200 or len(raw)>3_000_000 or not raw:
                    raise ValueError(f"HTTP {status}, bytes={len(raw)}")
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
                raw_opt=r.get("Option")
                opt=str(raw_opt).strip().lower() if raw_opt is not None else ""
                # API versions can omit/return null for the option. The named
                # ETF is a growth-only scheme; reject only an explicit non-growth option.
                if opt and "growth" not in opt:
                    raise ValueError(f"Unexpected non-growth option: {opt}")
                rows.append((d,nav))
            if len({d for d,v in rows})!=len(rows):raise ValueError("Duplicate date")
            if not cached:
                rawfile.write_bytes(raw)
            evidence.update(status="PASS_SOURCE_SEGMENT",n=len(rows),
                retrieved_from_committed_cache=cached,
                sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),
                scheme_name=scheme,nav_name=name,
                first=str(min(d for d,v in rows)),last=str(max(d for d,v in rows)))
            return rows,evidence
        except HTTPError as exc:
            errs.append(f"HTTPError: {exc.code} {exc.reason}")
            if exc.code==429 and attempt<2:
                time.sleep([15,30][attempt])
            elif attempt<2:
                time.sleep(3)
            else:
                break
        except Exception as exc:
            errs.append(f"{type(exc).__name__}: {exc}")
            if attempt<2:time.sleep(3)
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
    # Avoid simultaneous large AMFI queries (prior R9 received HTTP 429).
    # Commit every successful raw segment and resume on later runs.
    outcomes=[]
    for i,segment in enumerate(tasks):
        records,source=get_one(segment)
        outcomes.append((records,source))
        if source.get("status")!="PASS_SOURCE_SEGMENT" and any("429" in e for e in source.get("errors",[])):
            # Stop rather than repeatedly pressure a rate-limited official service.
            for remaining in tasks[i+1:]:
                a,b=remaining
                outcomes.append(([],{"start":str(a),"end":str(b),
                 "status":"SKIPPED_RATE_LIMIT","errors":["Earlier segment hit HTTP 429; halt and preserve partial evidence"]}))
            break
        if not source.get("retrieved_from_committed_cache"):
            time.sleep(3)
    sources=[s for records,s in outcomes]
    # Always retain sourced partial observations, even when some segments fail;
    # never promote these rows to a continuous qualified return history.
    partial_file=BASE/"partial_official_AMFI_NAV_UNQUALIFIED.csv"
    partial_rows=[]
    for rows,source in outcomes:
        if source.get("status")=="PASS_SOURCE_SEGMENT":
            for d,nav in rows:
                partial_rows.append((d.isoformat(),CODE,f"{nav:.8f}",
                     source.get("start",""),source.get("end",""),source.get("sha256","")))
    acquisition_incomplete = any(x.get("status") != "PASS_SOURCE_SEGMENT" for x in sources)
    # Keep a historical unqualified partial artifact when acquisition is
    # incomplete. Once full qualification succeeds, the daily/monthly outputs
    # are canonical; do not overwrite the prior failure's partial artifact with
    # a complete duplicate that still carries an UNQUALIFIED filename.
    if acquisition_incomplete:
        with partial_file.open("w",newline="",encoding="utf8") as fh:
            wr=csv.writer(fh,lineterminator="\n")
            wr.writerow(["date","scheme_code","nav","segment_start","segment_end","segment_sha256"])
            wr.writerows(sorted(partial_rows))
    partial_rows_in_file = len(partial_rows) if acquisition_incomplete else 0
    retrieved_utc=dt.datetime.now(dt.timezone.utc).isoformat()
    # Replaying only committed response bodies verifies the same source data;
    # keep its original acquisition timestamp so CI does not create a needless
    # data commit on every code or workflow change.
    if sources and all(x.get("retrieved_from_committed_cache") for x in sources):
        try:
            prior=json.loads((BASE/"qualification_manifest.json").read_text(encoding="utf8"))
            signature=lambda items: [(x.get("start"),x.get("end"),x.get("sha256"),x.get("status")) for x in items]
            if (prior.get("status")=="PASS_OFFICIAL_NAV_11YR_RESEARCH_ONLY"
                and prior.get("retrieved_utc")
                and signature(prior.get("segments",[]))==signature(sources)):
                retrieved_utc=prior["retrieved_utc"]
        except (OSError,ValueError,TypeError):
            pass
    manifest={"status":"FAIL_INCOMPLETE","research_source_gate":"NO_GO_UNTIL_QUALIFIED",
        "scheme_code":CODE,"isin":ISIN,"scheme_name":"LIC MF Nifty 8-13 yr G-Sec ETF",
        "official_amfi_history":True,"nse_index_historical_total_return_acquired":False,
        "nav_is_tradable_etf_market_price":False,"full_2036_forecast_validated":False,
        "investment_authorization":"NO_GO","retrieved_utc":retrieved_utc,
        "partial_observation_rows":partial_rows_in_file,
        "partial_source_file_sha256":hashlib.sha256(partial_file.read_bytes()).hexdigest() if partial_file.is_file() else None,
        "partial_not_eligible_for_return_calibration":True,
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
            w=csv.writer(fh,lineterminator="\n");w.writerow(["date","amfi_scheme_code","nav_inr","source_type"])
            for d,v in s:w.writerow([d.isoformat(),CODE,f"{v:.8f}","AMFI_OFFICIAL_NAV"])
        monthly={}
        for d,v in s:monthly[d.strftime("%Y-%m")]=(d,v)
        mm=sorted(monthly)
        series=[]
        for prior,cur in zip(mm,mm[1:]):
            pd,pv=monthly[prior];cd,cv=monthly[cur]
            if (cd.year*12+cd.month)-(pd.year*12+pd.month)!=1:
                raise ValueError(f"Missing calendar NAV month {prior}->{cur}")
            # Round derived CSV values so one-ulp libm differences across
            # Windows and Ubuntu do not change the byte-level source hash.
            series.append([cur,cd.isoformat(),round(math.log(cv/pv),12),
                           round(100*(cv/pv-1),12)])
        with (BASE/"lic_gsec_133307_monthly_returns.csv").open("w",newline="",encoding="utf8") as fh:
            w=csv.writer(fh,lineterminator="\n");w.writerow(["month","end_nav_date","log_nav_return","simple_nav_return_pct"]);w.writerows(series)
        vol=__import__("statistics").stdev([x[2] for x in series])*math.sqrt(12)*100
        manifest.update(status="PASS_OFFICIAL_NAV_11YR_RESEARCH_ONLY",
          research_source_gate="PASS_FULL_OFFICIAL_NAV_RESEARCH_ONLY",
          observations=len(s),first=str(s[0][0]),last=str(s[-1][0]),
          months_of_return=len(series),annualized_monthly_log_nav_volatility_pct=round(vol,5),
          official_lic_factsheet_cagr_comparisons=checks,
          daily_source_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
          monthly_source_sha256=hashlib.sha256((BASE/"lic_gsec_133307_monthly_returns.csv").read_bytes()).hexdigest())
    except Exception as e:manifest["error"]=f"{type(e).__name__}: {e}"
    with (BASE/"qualification_manifest.json").open("w",encoding="utf8",newline="\n") as fh:
        fh.write(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps({k:manifest.get(k) for k in ["status","observations","first","last",
      "months_of_return","annualized_monthly_log_nav_volatility_pct","error"]},indent=2))
    return 0 if manifest["status"]=="PASS_OFFICIAL_NAV_11YR_RESEARCH_ONLY" else 2
if __name__=="__main__":raise SystemExit(main())
