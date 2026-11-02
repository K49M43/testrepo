#!/usr/bin/env python3
"""R9.1 AMFI scheme-133307 source check at four independent calendar eras.

Only official AMFI data, short windows; never substitute mirror results.
Results are diagnostics and do not qualify complete NAV history.
"""
import datetime as dt,hashlib,json,urllib.request,urllib.parse,time,concurrent.futures
from pathlib import Path
CODE="133307"
BASE="https://www.amfiindia.com/api/nav-history"
OUT=Path("research/stage512/data/r9_lic_gsec_etf/short_window_probe.json")
WINDOWS=[
 ("2015-01","2015-01-05","2015-01-09"),
 ("2018-06","2018-06-04","2018-06-08"),
 ("2022-03","2022-03-21","2022-03-25"),
 ("2026-03","2026-03-23","2026-03-31")
]
def probe(item):
    label,a,b=item
    url=BASE+"?"+urllib.parse.urlencode({"query_type":"historical_period","from_date":a,"to_date":b,"sd_id":CODE})
    report={"label":label,"url":url,"state":"FAIL","source":"AMFI_PRIMARY"}
    for attempt in range(2):
        try:
            headers={"User-Agent":"Mozilla/5.0 (Stage512 official-NAV research)","Accept":"application/json",
                     "Accept-Encoding":"identity","Referer":"https://www.amfiindia.com/net-asset-value/nav-history"}
            req=urllib.request.Request(url,headers=headers)
            with urllib.request.urlopen(req,timeout=24) as resp:
                raw=resp.read(200_001)
                report["response_code"]=resp.status
                report["content_type"]=resp.headers.get("Content-Type")
            if len(raw)>200_000:raise ValueError("Response exceeds bounded probe")
            doc=json.loads(raw)
            body=doc.get("data")
            if not isinstance(body,dict):raise ValueError("No data in API response")
            groups=body.get("nav_groups")
            if not isinstance(groups,list) or len(groups)!=1:raise ValueError("Ambiguous/missing plan")
            group=groups[0]
            vals=group.get("historical_records")
            if not isinstance(vals,list) or len(vals)<2:raise ValueError("Too few price records")
            series=[]
            for x in vals:
                d=dt.date.fromisoformat(x["date"]);nav=float(x["nav"])
                if d<dt.date.fromisoformat(a) or d>dt.date.fromisoformat(b) or nav<=0:
                    raise ValueError("Bad NAV or date range")
                series.append((d.isoformat(),nav))
            title=body.get("scheme_name","")+" "+group.get("nav_name","")
            if not ("nifty" in title.lower() and "g-sec" in title.lower() and ("8-13" in title or "8 - 13" in title)):
                raise ValueError("Unexpected scheme identity: "+title[:100])
            report.update(state="PASS_SOURCE_SAMPLE",sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),
                 title=title,records=len(series),min_date=min(x[0] for x in series),
                 max_date=max(x[0] for x in series),last_nav=series[-1][1],
                 observed_navs=series[:2]+series[-2:])
            break
        except Exception as exc:
            report["error"]=f"{type(exc).__name__}: {exc}"
            if attempt==0:time.sleep(1)
    return report
def main():
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        result=list(pool.map(probe,WINDOWS))
    body={"retrieved_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
          "status":"PASS_ALL_FOUR_QUALIFICATION_SAMPLES_ONLY" if all(x["state"]=="PASS_SOURCE_SAMPLE" for x in result) else "FAIL_INCOMPLETE",
          "index_total_return_history_qualified":False,
          "ETF_full_history_qualified":False,
          "investment_authorization":"NO_GO","windows":result}
    OUT.write_text(json.dumps(body,indent=2)+"\n")
    print(json.dumps({"status":body["status"],"windows":[{"label":x["label"],"state":x["state"],"error":x.get("error")} for x in result]},indent=2))
if __name__=="__main__":main()
