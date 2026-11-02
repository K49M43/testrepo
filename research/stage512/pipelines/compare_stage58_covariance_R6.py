#!/usr/bin/env python3
"""Independent, offline 36-month Stage 5.8 instrument-NAV covariance checkpoint.

Uses prior NAV histories from mfapi.in, spot-checked against official AMFI
at selected dates, with pre-existing quality quarantine. NOT a primary-source
full history qualification. Never label the estimates as 2036 probabilities.
"""
import csv, json, math, hashlib
from pathlib import Path

ROOT = Path("research")
BASE = ROOT / "stage58"
OUT = ROOT / "stage512/data/nav_stage58_comparison_R6.json"
CODES = {"equity": "147625", "gilt_fund": "119116",
         "gold_etf": "105463", "silver_etf": "150556"}
WEIGHTS = {"equity": .65, "gilt_fund": .20, "gold_etf": .10, "silver_etf": .05}
def read_rows(p):
    with p.open(newline="", encoding="utf8") as fh:
        return list(csv.DictReader(fh))
def sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def calculate():
    metric_path = BASE / "qa_metrics.csv"
    corr_path = BASE / "qa_correlations_36m.csv"
    records = read_rows(metric_path)
    corr_rows = read_rows(corr_path)
    by_code = {r["scheme_code"]: r for r in records}
    names=list(CODES)
    metrics={}
    for name in names:
        code=CODES[name]
        row=by_code[code]
        if row.get("risk_qa_status") != "QA_PASS" or row.get("vol_36m_status") != "CLEAR":
            raise ValueError("Unqualified Stage5.8 input for "+code)
        if row.get("official_coverage") != "MATCHED" or int(row["official_nav_failures"]) != 0:
            raise ValueError("Sampled official NAV reconciliation failed for "+code)
        metrics[name]={"code":code,"name":row["scheme_name"],
                       "volatility_percent_annualized":float(row["vol_36m_pct"]),
                       "observations_in_mirror":int(row["nav_observations"]),
                       "official_anchors_matched":int(row["official_nav_matches"]),
                       "historic_jumps_detected":int(row["daily_break_count"]),
                       "source_type":"mfapi.in NAV mirror with sampled official AMFI reconciliation"}
    pairs={}
    for row in corr_rows:
        if row["code_a"] in CODES.values() and row["code_b"] in CODES.values():
            if int(row["months"])!=36: raise ValueError("Correlation horizon mismatch")
            key=tuple(sorted([row["code_a"],row["code_b"]]))
            if key in pairs and abs(pairs[key]-float(row["correlation"]))>1e-8:
                raise ValueError("Duplicate disagreement for "+str(key))
            pairs[key]=float(row["correlation"])
    matrix=[]
    for n1 in names:
        out=[]
        for n2 in names:
            key=tuple(sorted([CODES[n1],CODES[n2]]))
            if key not in pairs:raise ValueError("Missing pair "+str(key))
            val=pairs[key]
            if not (-1-1e-9<=val<=1+1e-9):raise ValueError("Invalid correlation")
            if n1==n2 and abs(val-1)>1e-7:raise ValueError("Invalid diagonal")
            out.append(val)
        matrix.append(out)
    # Cholesky as an independent PSD matrix check
    L=[[0.0]*len(names) for _ in names]
    for i in range(len(names)):
        for j in range(i+1):
            t=matrix[i][j]-sum(L[i][k]*L[j][k] for k in range(j))
            if i==j:
                if t<=1e-10:raise ValueError("Non-positive-definite correlation matrix")
                L[i][j]=math.sqrt(t)
            else:L[i][j]=t/L[j][j]
    vols=[metrics[n]["volatility_percent_annualized"] for n in names]
    weights=[WEIGHTS[n] for n in names]
    variance=sum(weights[i]*weights[j]*vols[i]*vols[j]*matrix[i][j]
                 for i in range(4) for j in range(4))
    result={
        "status":"RESEARCH_ONLY_PROXY_MIRROR_SAMPLED_AMFI",
        "official_complete_series_qualified":False,
        "investment_gate":"NO_GO",
        "purpose":"Compare actual scheme NAV behavior to prior long-history asset-class proxies",
        "data_months":36,
        "instrument_order":names,
        "metrics":metrics,
        "correlation_matrix":matrix,
        "weights":WEIGHTS,
        "indicative_portfolio_annualized_volatility_percent":round(math.sqrt(variance),6),
        "caveats":["36 monthly returns are not 36 independent economic regimes",
                   "Data are mirrored NAV histories, sampled against official AMFI, not 36 months independently primary-source audited",
                   "Portfolio variance is a static approximation, excludes dynamic flows and cashflow sequencing",
                   "Historical 36-month covariance is not a 2036 probability forecast",
                   "Scheme NAV already reflects embedded fund TER; do not subtract the same fund TER twice"],
        "data_provenance":{
            str(metric_path):sha256(metric_path),
            str(corr_path):sha256(corr_path)
        }
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"status":result["status"],"portfolio_volatility_percent":result["indicative_portfolio_annualized_volatility_percent"],"sample_months":36}))
if __name__=="__main__":calculate()
