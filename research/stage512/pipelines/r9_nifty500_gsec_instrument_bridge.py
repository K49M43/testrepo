#!/usr/bin/env python3
"""Stage 5.12 R9: independently qualify two-asset long-run bond/equity comparison.

NSE Nifty500 gross TRI official whitepaper 2015-2025 (published monthly to 0.01%).
LIC MF Nifty 8-13 yr G-Sec ETF AMFI official NAV 2014-2026.
Instrument benchmark != ETF NAV; fund returns already embed TER.
Gold/silver and CPI are NOT automatically a same-time joint benchmark panel.
"""
from __future__ import annotations
import csv,json,hashlib,math,statistics
from pathlib import Path
BASE=Path("research/stage512/data")
NSE=BASE/"nse500_official_tri_monthly_2015_2025q3_R8.csv"
NAV=BASE/"r9_lic_gsec_etf/lic_gsec_133307_monthly_returns.csv"
MAN=BASE/"r9_lic_gsec_etf/qualification_manifest.json"
OUT=BASE/"r9_nse_gsec_129m_source_bridge.json"
def read(p):
    with p.open(newline="",encoding="utf8") as f:return list(csv.DictReader(f))
def mean(a):return statistics.mean(a)
def sd(a):return statistics.stdev(a)
def corr(a,b):
    ma,mb=mean(a),mean(b)
    return sum((x-ma)*(y-mb) for x,y in zip(a,b))/((len(a)-1)*sd(a)*sd(b))
def main():
    report={"status":"FAIL_NOT_QUALIFIED","investment_gate":"NO_GO",
       "full_nse_8_13_gsec_index_monthly_history_qualified":False,
       "silver_or_gold_same_time_multi_asset_covariance_qualified":False,
       "etf_is_index_not_true":True,"nse_equity_monthly_precision":"rounded 0.01 percentage point"}
    try:
        manifest=json.loads(MAN.read_text())
        if manifest.get("status")!="PASS_OFFICIAL_NAV_11YR_RESEARCH_ONLY":
            raise ValueError("LIC ETF raw official AMFI NAV and factsheet qualified history unavailable")
        if len(manifest.get("segments",[]))<6 or any(v.get("status")!="PASS_SOURCE_SEGMENT" for v in manifest["segments"]):
            raise ValueError("Incomplete original AMFI primary-source segment metadata")
        if hashlib.sha256(NAV.read_bytes()).hexdigest()!=manifest["monthly_source_sha256"]:
            raise ValueError("Official monthly ETF return source altered")
        eftrows=read(NAV)
        etf={z["month"]:float(z["log_nav_return"]) for z in eftrows}
        equityrows=read(NSE)
        official={z["month"]:math.log1p(float(z["nifty500_tri_monthly_return_pct"])/100) for z in equityrows}
        months=sorted(set(official)&set(etf))
        if len(months)!=129 or months[0]!="2015-01" or months[-1]!="2025-09":
            raise ValueError("129 continuous official joint equity/bond fund months required")
        for p,q in zip(months,months[1:]):
            y,m=map(int,p.split("-")); yy,mm=map(int,q.split("-"))
            if (yy*12+mm)-(y*12+m)!=1:raise ValueError("Joint calendar month gap")
        eq=[official[m] for m in months];g=[etf[m] for m in months]
        report.update(status="PASS_129_MONTH_EQUITY_TR_VS_BOND_ETF_NAV_RESEARCH_ONLY",
          first_month=months[0],last_month=months[-1],
          monthly_observations=len(months),
          nifty500_tri_monthly_log_vol_annualized_pct=round(sd(eq)*math.sqrt(12)*100,5),
          lic_gsec_etf_monthly_log_vol_annualized_pct=round(sd(g)*math.sqrt(12)*100,5),
          observed_equity_gsec_etf_correlation=round(corr(eq,g),6),
          annualized_geometric_equity_tr_return_pct=round(math.expm1(mean(eq)*12)*100,5),
          annualized_geometric_bond_etf_nav_return_pct=round(math.expm1(mean(g)*12)*100,5),
          correlation_source_identification="NSE official published Nifty500 gross TRI MONTHLY values vs AMFI official LIC ETF monthly NAV",
          source_hashes={"nifty500_official_whitepaper":hashlib.sha256(NSE.read_bytes()).hexdigest(),
                         "lic_etf_official_monthly":hashlib.sha256(NAV.read_bytes()).hexdigest()},
          caution=["Fund ETF NAV is not the 8-13-year G-Sec benchmark total-return index itself",
                   "Ten-year overlapping windows will not be independent samples",
                   "2015-2025 historical mean is not a forward-expected CAGR",
                   "NSE published monthly values rounded to two decimal return points",
                   "Direct 2036-maturity sovereign bond has fundamentally different maturity roll-down exposure",
                   "ETF exchange prices and market spread may diverge from observed NAVs",
                   "Fund NAV already includes TER: do not subtract fund expense twice"])
    except Exception as exc:
        report["error"]=f"{type(exc).__name__}: {exc}"
    OUT.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:report.get(k) for k in ("status","monthly_observations",
       "observed_equity_gsec_etf_correlation","error")},indent=2))
    return 0 if report["status"].startswith("PASS_") else 2
if __name__=="__main__":raise SystemExit(main())
