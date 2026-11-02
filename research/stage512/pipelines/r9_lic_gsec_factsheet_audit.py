#!/usr/bin/env python3
"""Validate LIC MF published ETF vs Nifty 8–13yr G-Sec annualized return anchors.

NO claim that this supplies continuous NSE index levels or 12 independent trials.
Overlapping 1/3/5-year returns and 2026 adjacent-month factsheets are NOT independent.
"""
import csv,json,hashlib,datetime as dt,statistics
from pathlib import Path
P=Path("research/stage512/data/r9_lic_gsec_official_factsheet_anchors.csv")
O=Path("research/stage512/data/r9_lic_gsec_factsheet_bridge.json")
def main():
    with P.open(newline="") as f:a=list(csv.DictReader(f))
    out={"status":"FAIL","asof_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
         "investment_gate":"NO_GO","full_nse_gsec_index_monthly_history_acquired":False,
         "is_tracking_error_estimate":False,
         "provenance_sha256":hashlib.sha256(P.read_bytes()).hexdigest()}
    try:
        if len(a)!=12:raise ValueError("Expected four publication sets of 1/3/5yr")
        by={}
        for x in a:
            key=(x["report_month"],int(x["period_years"]))
            if key in by:raise ValueError("Duplicate publication anchor")
            if not x["source_url"].startswith("https://www.licmf.com/"):raise ValueError("Unofficial source")
            fund=float(x["ETF_NAV_CAGR_pct"]);index=float(x["Nifty_8_13_Yr_GSec_benchmark_CAGR_pct"])
            by[key]=round(index-fund,6)
        months=sorted({m for m,n in by})
        if months!=["2024-08","2026-02","2026-03","2026-04"] or set(n for m,n in by)!={1,3,5}:raise ValueError("Incomplete tenors/vintages")
        by_year={str(n):{"observations":len(months),
          "difference_pp_by_report_month":{m:by[(m,n)] for m in months},
          "mean_benchmark_minus_fund_annualized_percentage_points":round(statistics.mean(by[(m,n)] for m in months),6)}
          for n in (1,3,5)}
        out.update(status="PASS_PUBLISHED_RETURN_ANCHOR_ARITHMETIC_ONLY",
          official_factsheet_rows=len(a),published_report_months=months,
          annualized_tracking_difference_by_tenor=by_year,
          caveats=["Annualized *tracking difference* is not tracking error (variability of return differences).",
             "Four report months and three trailing windows overlap heavily; do not treat as 12 independent observations.",
             "ETF NAV includes TER but exchange market price adds premium/discount and spread.",
             "The ETF's published underlying benchmark total returns are point-in-time windows, not a continuous investable index series."])
    except Exception as exc:out["error"]=f"{type(exc).__name__}: {exc}"
    O.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps({"status":out["status"],"error":out.get("error")}))
    return 0 if out["status"].startswith("PASS_") else 2
if __name__=="__main__":raise SystemExit(main())
