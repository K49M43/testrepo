#!/usr/bin/env python3
"""Stage 5.12 R8 — RBI-origin monthly Mumbai bullion table, secondary DBIE mirror probe.

IMPORTANT: data-api.dbie.rbihub.in is a THIRD-PARTY mirror of RBI's DBIE.
Its rows MUST NOT be promoted to independently RBI-verified primary-source data.
No backfilling, financial forecasts, or portfolio selection is authorized.
"""
from __future__ import annotations
import datetime as dt
import hashlib, json, urllib.request, csv, io, re
from pathlib import Path
BASE="https://data-api.dbie.rbihub.in/api/tables/real_sector/r17_monthly_average_price_of_gold_and_silver_in_mumbai"
OUT=Path("research/stage512/data/r8_rbi_origin_mirror")
def fetch(endpoint):
    url=BASE+endpoint
    row={"url":url,"status":"FAIL","fetched_utc":dt.datetime.now(dt.timezone.utc).isoformat()}
    try:
        req=urllib.request.Request(url,headers={"Accept":"application/json,text/csv,*/*","User-Agent":"Stage512-reproducibility-audit/1.0","Accept-Encoding":"identity"})
        with urllib.request.urlopen(req,timeout=28) as r:
            b=r.read(5_000_001)
            row.update(http_status=r.status,content_type=r.headers.get("Content-Type"),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
        if r.status != 200 or len(b)>5_000_000 or len(b)<100:raise ValueError("Bad status, excessive size, or empty body")
        row["status"]="FETCH_OK_NOT_YET_QUALIFIED"
        return b,row
    except Exception as e:
        row["error"]=f"{type(e).__name__}: {e}"
        return None,row
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    results={}
    for name,endpoint in [
      ("metadata",""),
      ("sample_rows","/rows?limit=10&labels=1"),
      ("complete_csv","/csv")]:
        raw,diag=fetch(endpoint)
        results[name]=diag
        if raw:
            if name!="complete_csv":
                try:
                    obj=json.loads(raw)
                    diag["json_top_level_keys"]=list(obj)[:30] if isinstance(obj,dict) else ["array"]
                    diag["body_excerpt"]=raw[:1200].decode("utf8","replace")
                except ValueError: diag["status"]="FAIL_NON_JSON";diag["body_excerpt"]=raw[:250].decode("utf8","replace")
            else:
                txt=raw.decode("utf-8-sig","replace")
                rr=csv.reader(io.StringIO(txt))
                first=[]
                for i,x in enumerate(rr):
                    first.append(x[:12])
                    if i>=6:break
                diag["first_rows"]=first
                diag["line_count"]=len(txt.splitlines())
                diag["csv_headers"]=first[0] if first else []
                if "<html" in txt[:500].lower():diag["status"]="FAIL_HTML_NOT_CSV"
                else:(OUT/"rbi_origin_monthly_gold_silver_MIRROR_NOT_VERIFIED.csv").write_bytes(raw)
    results["governance"]={"data_origin":"RBI Database on Indian Economy","data_distribution":"unofficial third-party DBIE mirror",
      "official_RBI_primary_reconciled":False,"investment_gate":"NO_GO","full_portfolio_calibration":False,
      "source_documentation":"https://dev.dbie.rbihub.in/docs/using-the-site",
      "official_reference":"https://dbie.rbi.org.in/"}
    (OUT/"source_probe.json").write_text(json.dumps(results,indent=2)+"\n")
    print(json.dumps({k:{"status":v.get("status"),"rows":v.get("line_count"),"error":v.get("error")} for k,v in results.items() if k!="governance"},indent=2))
if __name__=="__main__":main()
