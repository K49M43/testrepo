#!/usr/bin/env python3
"""Stage 5.12 R8: independently validate third-party Nifty500 TRI daily history
against 129 monthly returns printed in the NSE October 2025 whitepaper.

This is official NSE MONTHLY-RETURN SEGMENT + independently CROSS-CHECKED MIRROR,
not certification that every daily value from 1995 onward is official.
"""
from __future__ import annotations
import csv, datetime as dt, hashlib, json, math, urllib.request
from pathlib import Path
SRC=Path("research/stage512/data/nse500_official_tri_monthly_2015_2025q3_R8.csv")
OUT=Path("research/stage512/data/nse500_tri_validation_R8.json")
DAILY_URL="https://raw.githubusercontent.com/Sams3pi01/SIP-Calculator/main/NIFTY%20500%20TRI.csv"
EXPECTED_GIT_BLOB_SHA1="89f0bb076ce6a733197e89416830203c6f3ddd8a"
EXPECTED_ANNUAL={2015:.22,2016:5.12,2017:37.65,2018:-2.14,2019:8.97,
                 2020:17.89,2021:31.60,2022:4.25,2023:26.91,2024:16.24,2025:2.50}
def git_blob_sha1(data):
    return hashlib.sha1(b"blob "+str(len(data)).encode("ascii")+b"\0"+data).hexdigest()
def main():
    report={"status":"FAIL_UNQUALIFIED","asof_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
        "primary_official_NSE_document":"https://www.niftyindices.com/docs/default-source/indices/nifty-500/nifty-500-whitepaper_2025.pdf",
        "source_page_label":"printed page 12, Exhibit 12 (PDF index 12)",
        "benchmark":"NIFTY 500 Total Return Index (gross TRI)",
        "mirror_owner":"Sams3pi01/SIP-Calculator; not NSE",
        "mirror_url":DAILY_URL,"mirror_git_blob_sha1_expected":EXPECTED_GIT_BLOB_SHA1,
        "complete_official_NSE_daily_history_qualified":False,
        "full_2036_probability_qualified":False,"investment_gate":"NO_GO"}
    try:
        with SRC.open(newline="",encoding="utf8") as f:
            official=list(csv.DictReader(f))
        if len(official)!=129:raise ValueError(f"Official table rows {len(official)} != 129")
        official_month={r["month"]:float(r["nifty500_tri_monthly_return_pct"]) for r in official}
        if len(official_month)!=129:raise ValueError("Duplicate whitepaper months")
        months=sorted(official_month)
        if months[0]!="2015-01" or months[-1]!="2025-09":raise ValueError("Wrong whitepaper period")
        annual={}
        for month,v in official_month.items():
            y=int(month[:4]);annual[y]=annual.get(y,1.0)*(1+v/100)
        annualChecks={str(y):{"whitepaper_return_pct":target,"compounded_rounded_months_pct":round((annual[y]-1)*100,5)}
                      for y,target in EXPECTED_ANNUAL.items()}
        if any(abs((annual[y]-1)*100-target)>.055 for y,target in EXPECTED_ANNUAL.items()):
            raise ValueError("Publication calendar-year reconciliation failed")
        req=urllib.request.Request(DAILY_URL,headers={"User-Agent":"Stage512-independent-NSE-whitepaper-audit","Accept":"text/csv"})
        with urllib.request.urlopen(req,timeout=40) as resp:
            raw=resp.read(1_000_000)
        sha=git_blob_sha1(raw)
        if sha!=EXPECTED_GIT_BLOB_SHA1:raise ValueError(f"Mirror source revision changed: {sha}")
        (OUT.parent/"nse_mirror_raw_sha.txt").write_text(sha+"\n")
        dates={}
        for item in csv.DictReader(raw.decode("utf-8-sig").splitlines()):
            day=dt.datetime.strptime(item["Date"],"%d-%m-%Y").date()
            level=float(item["Price"])
            if not math.isfinite(level) or level<=0:raise ValueError("Bad daily index level")
            key=day.strftime("%Y-%m")
            if key not in dates or day>dates[key][0]:
                dates[key]=(day,level)
        mismatches=[]
        delta=[]
        for month,v in official_month.items():
            yy,mm=map(int,month.split("-"))
            if mm==1:prior=f"{yy-1}-12"
            else:prior=f"{yy}-{mm-1:02d}"
            if month not in dates or prior not in dates:raise ValueError(f"Missing daily month anchor {month}")
            mir=(dates[month][1]/dates[prior][1]-1)*100
            diff=mir-v
            delta.append(abs(diff))
            if abs(diff)>.0051:mismatches.append({"month":month,"nse_official_pct":v,"mirror_pct":mir,"difference_pp":diff})
        report.update(status="PASS_129_OFFICIAL_MONTHLY_ANCHORS",
            verified_months=len(delta),max_abs_diff_pp=max(delta),
            mean_abs_diff_pp=sum(delta)/len(delta),violations=mismatches,
            independent_mirror_source_blob_sha1=sha,
            official_table_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),
            annual_published_reconciliation=annualChecks,
            limitation="Official NSE report verifies rounded MONTHLY TRI returns 2015-2025Q3; other months and all daily prices remain unverified against first-party daily feed.")
        if mismatches:raise ValueError(f"{len(mismatches)} NSE official monthly comparisons failed")
    except Exception as exc:
        report["status"]="FAIL_UNQUALIFIED"
        report["error"]=f"{type(exc).__name__}: {exc}"
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:report.get(k) for k in ("status","verified_months","max_abs_diff_pp","error")},indent=2))
    return 0 if report["status"]=="PASS_129_OFFICIAL_MONTHLY_ANCHORS" else 2
if __name__=="__main__":raise SystemExit(main())
