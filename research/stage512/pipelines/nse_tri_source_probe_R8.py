#!/usr/bin/env python3
"""Stage 5.12 R8 bounded official Nifty Indices TRI source probe.

The website's historical-data interface changes frequently. A 200 response
is never enough for qualification: enforce schema/date/positive TRI checks.
No change to forward investment approval or statistical assumptions.
"""
from __future__ import annotations
import datetime as dt
import hashlib, json, math, time
from urllib.request import Request, urlopen
from pathlib import Path

API="https://www.niftyindices.com/Backpage.aspx/getTotalReturnIndexString"
OUTPUT=Path("research/stage512/data/nse_tri_source_probe_R8.json")
WINDOWS=[
    ("2020-02", "01-Feb-2020", "30-Apr-2020"),
    ("2026-08", "01-Aug-2026", "30-Oct-2026"),
]
def probe(label,first,last):
    name="NIFTY 500"
    params={"cinfo":f"{{'name':'{name}','startDate':'{first}','endDate':'{last}','indexName':'{name}'}}"}
    data=json.dumps(params).encode("utf8")
    result={"window":label,"start":first,"end":last,
            "source_url":API,"index_name":name,
            "status":"FAIL_UNQUALIFIED","retrieved_utc":dt.datetime.now(dt.timezone.utc).isoformat()}
    errors=[]
    for attempt in range(2):
        try:
            request=Request(API,data=data,method="POST",headers={
                "Content-Type":"application/json; charset=UTF-8",
                "X-Requested-With":"XMLHttpRequest",
                "Referer":"https://www.niftyindices.com/reports/historical-data",
                "User-Agent":"Mozilla/5.0 (research, NSE historical index verification)",
                "Accept":"application/json, text/plain, */*",
                "Accept-Encoding":"identity"})
            with urlopen(request,timeout=45) as response:
                raw=response.read(3_000_001)
                if response.status!=200 or len(raw)>3_000_000:
                    raise ValueError("Bad status or excessively large payload")
                result.update(http_status=response.status,bytes=len(raw),
                              content_type=response.headers.get("content-type",""),
                              source_sha256=hashlib.sha256(raw).hexdigest())
            obj=json.loads(raw)
            if not isinstance(obj,dict) or "d" not in obj:
                raise ValueError("Unexpected NSE response wrapper")
            rows=json.loads(obj["d"]) if isinstance(obj["d"],str) else obj["d"]
            if not isinstance(rows,list) or len(rows)<5:
                raise ValueError("Missing or short NIFTY 500 TRI table")
            good=[];samples=[]
            for x in rows:
                if not isinstance(x,dict):raise ValueError("Invalid data row type")
                date_text=x.get("Date") or x.get("HistoricalDate")
                price_text=x.get("TotalReturnsIndex") or x.get("Total Return Index")
                if date_text is None or price_text is None:raise ValueError("Missing TRI/date column")
                day=dt.datetime.strptime(str(date_text).strip(),"%d %b %Y").date()
                price=float(str(price_text).replace(",",""))
                if not(math.isfinite(price) and price>0):raise ValueError("Invalid TRI")
                if not(dt.datetime.strptime(first,"%d-%b-%Y").date()<=day<=dt.datetime.strptime(last,"%d-%b-%Y").date()):
                    raise ValueError("Out of requested date window")
                good.append((day,price))
                if len(samples)<3:samples.append({"date":str(day),"tri":price,"row_keys":sorted(x)})
            if len({d for d,v in good})!=len(good):
                raise ValueError("Duplicate official TRI index-date rows")
            result.update(status="PASS_SAMPLE_TRI_ONLY",observations=len(good),
                          first_observation=str(min(d for d,v in good)),
                          last_observation=str(max(d for d,v in good)),
                          original_keys=sorted(rows[0].keys()),samples=samples)
            break
        except Exception as exc:
            errors.append(f"{type(exc).__name__}: {exc}")
            if attempt==0:time.sleep(2)
    if result["status"]!="PASS_SAMPLE_TRI_ONLY":result["errors"]=errors
    return result
def main():
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    result={"research_gate":"SOURCE_DISCOVERY_ONLY","investment_gate":"NO_GO",
            "NIFTY500_TR_INDEX_HISTORY_QUALIFIED":False,
            "source_owner":"NSE Indices","probes":[probe(*x) for x in WINDOWS]}
    OUTPUT.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"statuses":[x["status"] for x in result["probes"]],"rows":[x.get("observations") for x in result["probes"]]},indent=2))
if __name__=="__main__":main()
