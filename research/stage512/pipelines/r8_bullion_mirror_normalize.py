#!/usr/bin/env python3
"""Stage 5.12 R8: qualify RBI-origin bullion MONTHLY AVERAGES from unverified DBIE mirror.

Source is RBI-origin report table redistributed by an independent DBIE mirror.
This is NOT first-party RBI source verification. Fail closed on schema, missing months,
index months, units, date ambiguity or invalid gold/silver. Preserve SHA provenance.
"""
from __future__ import annotations
import csv,io,hashlib,json,datetime as dt,urllib.request,calendar,re,math,statistics
from pathlib import Path
URL="https://data-api.dbie.rbihub.in/api/tables/real_sector/r17_monthly_average_price_of_gold_and_silver_in_mumbai/csv"
OUT=Path("research/stage512/data/r8_rbi_origin_mirror")
NAME="rbi_origin_mumbai_bullion_monthly_SECONDARY_MIRROR.csv"
def month_id(d):return d.year*12+d.month
def parse(text):
    r=csv.DictReader(io.StringIO(text))
    if r.fieldnames!=["src_file","tab","period","row_no","c1","c2","c3","c4"]:
        raise ValueError("Unexpected DBIE mirror CSV schema")
    obs={}; rejected=[]
    for row in r:
        date_string=row["c1"].strip()
        match=re.fullmatch(r"([A-Za-z]{3})\.\s+(\d{4})",date_string)
        if not match:
            if len(rejected)<15:rejected.append({"row_no":row["row_no"],"c1":date_string[:70]})
            continue
        name,year=match.groups()
        if name not in list(calendar.month_abbr):raise ValueError("Unexpected month label")
        date=dt.date(int(year),list(calendar.month_abbr).index(name),1)
        def val(s):
            raw=s.strip()
            if not re.fullmatch(r"[0-9][0-9,]*(?:\.[0-9]+)?",raw):raise ValueError(f"Invalid observed bullion price {raw}")
            v=float(raw.replace(",",""))
            if not math.isfinite(v) or v<=0:raise ValueError("Nonpositive/nonfinite bullion price")
            return v
        gold,silver=val(row["c2"]),val(row["c3"])
        if date in obs:raise ValueError(f"Duplicate reference month {date}")
        obs[date]=(gold,silver,row["row_no"])
    dates=sorted(obs)
    if len(dates)<400:raise ValueError(f"Only {len(dates)} monthly gold/silver pairs")
    if any(month_id(b)-month_id(a)!=1 for a,b in zip(dates,dates[1:])):
        raise ValueError("Missing month in secondary DBIE bullion source")
    if dates[0]<dt.date(1980,1,1) or dates[-1]>dt.date.today():
        raise ValueError("Unexpected reference period")
    return obs,dates,rejected
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    req=urllib.request.Request(URL,headers={"User-Agent":"Stage512 research monthly bullion verification","Accept":"text/csv,*/*","Accept-Encoding":"identity"})
    manifest={"status":"FAIL_UNQUALIFIED","distribution":"THIRD_PARTY_DBIE_MIRROR_OF_RBI_BULLETIN",
              "official_rbi_primary_verified":False,"2036_investment_authorized":False,
              "retrieved_utc":dt.datetime.now(dt.timezone.utc).isoformat(),"source_url":URL,
              "source_page":"https://dbie.rbihub.in/tables?table=real_sector.r17_monthly_average_price_of_gold_and_silver_in_mumbai",
              "units":{"gold":"INR per 10 grams","silver":"INR per kilogram"}}
    try:
        with urllib.request.urlopen(req,timeout=45) as rsp:
            raw=rsp.read(1_000_001)
            if rsp.status!=200 or len(raw)>1_000_000:raise ValueError("Invalid HTTP/size response")
            manifest["raw_source_sha256"]=hashlib.sha256(raw).hexdigest()
            manifest["bytes"]=len(raw)
        (OUT/"raw_mirror_monthly_bullion.csv").write_bytes(raw)
        obs,dates,unused=parse(raw.decode("utf-8-sig"))
        data=[["month","gold_inr_per_10g","silver_inr_per_kg","source_type","source_sha256"]]
        for d in dates:
            gold,silver,_=obs[d]
            data.append([d.strftime("%Y-%m"),gold,silver,"RBI_ORIGIN_THIRD_PARTY_MIRROR_NOT_PRIMARY",manifest["raw_source_sha256"]])
        with (OUT/NAME).open("w",newline="",encoding="utf8") as f:
            csv.writer(f).writerows(data)
        manifest.update(status="PASS_SECONDARY_MIRROR_INTEGRITY_ONLY",observations=len(dates),
            first_month=dates[0].strftime("%Y-%m"),last_month=dates[-1].strftime("%Y-%m"),
            unused_nonobservation_row_samples=unused,
            normalized_sha256=hashlib.sha256((OUT/NAME).read_bytes()).hexdigest(),
            gold_first=obs[dates[0]][0],gold_last=obs[dates[-1]][0],
            silver_first=obs[dates[0]][1],silver_last=obs[dates[-1]][1],
            official_rbi_source_reconciliation="OPEN")
    except Exception as exc:manifest["error"]=f"{type(exc).__name__}: {exc}"
    (OUT/"normalized_validation.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf8")
    print(json.dumps({k:manifest.get(k) for k in ["status","observations","first_month","last_month","error"]},indent=2))
    return 0 if manifest["status"]=="PASS_SECONDARY_MIRROR_INTEGRITY_ONLY" else 2
if __name__=="__main__":raise SystemExit(main())
