#!/usr/bin/env python3
"""Stage 5.12 R7: independent qualified-source NAV covariance & regime audit.

Reads pinned archived official AMFI per-scheme NAV CSV from Stage 5.12.
NO fetch / third-party fallback / investment forecasts.
Pass means source lineage + arithmetic integrity, NOT 2036 model approval.
"""
from __future__ import annotations
import csv, datetime as dt, hashlib, json, math, statistics
from collections import defaultdict
from pathlib import Path

ROOT=Path("research/stage512/data")
INPUT=ROOT/"amfi_official_36m/official_nav_four_assets.csv"
MANIFEST=ROOT/"amfi_official_36m/qualification_manifest.json"
OUTPUT=ROOT/"official_nav_independent_R7.json"
FUNDS={"equity":"147625","gilt_fund":"119116","gold_etf":"105463","silver_etf":"150556"}
ORDER=list(FUNDS)
WEIGHTS={"equity":.65,"gilt_fund":.20,"gold_etf":.10,"silver_etf":.05}

def mean(x):return statistics.mean(x)
def stdev(x):return statistics.stdev(x)
def cov(a,b):
    ma,mb=mean(a),mean(b)
    return sum((x-ma)*(y-mb) for x,y in zip(a,b))/(len(a)-1)
def correlation(a,b):return cov(a,b)/(stdev(a)*stdev(b))
def vol(a):return stdev(a)*math.sqrt(12)*100
def month_of(d):return d.year*12+d.month
def month_str(m):return f"{(m-1)//12:04d}-{(m-1)%12+1:02d}"
def rows_csv(path):
    with path.open(newline="",encoding="utf-8") as f:return list(csv.DictReader(f))
def positive_definite(a):
    n=len(a); l=[[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1):
            v=a[i][j]-sum(l[i][k]*l[j][k] for k in range(j))
            if i==j:
                if v<=1e-12:raise ValueError("Correlation matrix not positive definite")
                l[i][j]=math.sqrt(v)
            else:l[i][j]=v/l[j][j]
def main():
    manifest=json.loads(MANIFEST.read_text())
    if manifest.get("status")!="PASS_36M_COHORT_ONLY" or manifest.get("errors"):
        raise ValueError("Source qualification gate not passed")
    if manifest.get("full_10y_forecast_validated") is not False:
        raise ValueError("Incorrect long-horizon qualification label")
    if len(manifest.get("source_manifest",[]))!=12:
        raise ValueError("Twelve source-segment hashes required")
    provenance={}
    for record in manifest["source_manifest"]:
        if len(record.get("sha256",""))!=64 or record["code"] not in FUNDS.values() or not record.get("url","").startswith("https://www.amfiindia.com/"):
            raise ValueError("Invalid official AMFI provenance segment")
        provenance[record["code"]]=provenance.get(record["code"],0)+1
    if any(provenance.get(code)!=3 for code in FUNDS.values()):
        raise ValueError("Every scheme needs three official source segments")
    recs={x["asset"]:x for x in manifest["records"]}
    if set(recs)!=set(FUNDS):raise ValueError("Missing scheme lineage")
    if any(recs[a].get("status")!="PASS_OFFICIAL_36M_COHORT" or int(recs[a]["mismatches"])!=0 for a in ORDER):
        raise ValueError("Missing source acceptance for at least one scheme")
    if sum(int(recs[a]["official_snapshot_checks"]) for a in ORDER)<60:
        raise ValueError("Insufficient official AMFI sampled crosschecks")
    observations=defaultdict(list)
    for r in rows_csv(INPUT):
        a=r["asset"]; d=dt.date.fromisoformat(r["date"]); nav=float(r["nav"])
        if a not in FUNDS or r["amfi_code"]!=FUNDS[a] or not (math.isfinite(nav) and nav>0):
            raise ValueError("Invalid or misassigned NAV")
        observations[a].append((d,nav))
    monthly={}
    checks={}
    for a in ORDER:
        pts=observations[a]
        if len(pts)!=int(recs[a]["samples"]):raise ValueError("Count mismatch for "+a)
        if pts!=sorted(pts):raise ValueError("Not chronological: "+a)
        if len({d for d,_ in pts})!=len(pts):raise ValueError("Duplicate NAV date")
        if pts[0][0].isoformat()!=recs[a]["first"] or pts[-1][0].isoformat()!=recs[a]["last"]:
            raise ValueError("Endpoint mismatch")
        days=[(pts[i][0]-pts[i-1][0]).days for i in range(1,len(pts))]
        if max(days)>7:raise ValueError("Unexpected business date gap")
        changes=[math.log(pts[i][1]/pts[i-1][1]) for i in range(1,len(pts))]
        if max(abs(x) for x in changes)>math.log(1.66667):raise ValueError("Unquarantined NAV discontinuity")
        by_month={}
        for d,n in pts:by_month[month_of(d)]=(d,n)
        monthly[a]=by_month
        checks[a]={"nav_count":len(pts),"month_count":len(by_month),
                   "first":pts[0][0].isoformat(),"last":pts[-1][0].isoformat(),
                   "max_gap_calendar_days":max(days),
                   "max_abs_daily_logreturn_pct":round(100*max(abs(x) for x in changes),4),
                   "official_snapshots_matched":int(recs[a]["official_snapshot_checks"])}
    allmonths=set.intersection(*(set(monthly[a]) for a in ORDER))
    keys=sorted(allmonths)
    if len(keys)<38 or any(keys[i]-keys[i-1]!=1 for i in range(1,len(keys))):
        raise ValueError("Incomplete joint month-end grid")
    mismatch_dates=[]
    for k in keys:
        if len({monthly[a][k][0] for a in ORDER})!=1:mismatch_dates.append(month_str(k))
    # A mismatched first month-end contaminates the immediately following return.
    # Source acceptance remains valid; quarantine that boundary before risk estimation.
    if mismatch_dates and mismatch_dates != [month_str(keys[0])]:
        raise ValueError("Unexpected cross-fund month-end mismatch "+str(mismatch_dates))
    published_months=keys[1:]
    published_samples={a:[math.log(monthly[a][k][1]/monthly[a][k-1][1]) for k in published_months] for a in ORDER}
    common_return_months=[k for k in keys[1:] if month_str(k-1) not in mismatch_dates and month_str(k) not in mismatch_dates]
    if len(common_return_months)<36:
        raise ValueError("Fewer than 36 strictly same-date monthly return observations")
    samples={a:[math.log(monthly[a][k][1]/monthly[a][k-1][1]) for k in common_return_months] for a in ORDER}
    n=len(common_return_months)
    corrs=[[correlation(samples[a],samples[b]) for b in ORDER] for a in ORDER]
    positive_definite(corrs)
    computed_vols={a:vol(samples[a]) for a in ORDER}
    stored=manifest["cross_asset_result"]
    # Verify the original 37 month-only aligned publication before applying strict date quarantine.
    if int(stored["months"])!=len(published_months) or stored["start_month"]!=month_str(published_months[0]) or stored["end_month"]!=month_str(published_months[-1]):
        raise ValueError("Published original 37-month window is inconsistent")
    for a in ORDER:
        if abs(vol(published_samples[a])-float(stored["annualized_volatility_pct"][a]))>0.00006:
            raise ValueError("Original published volatility audit mismatch for "+a)
    for i,a in enumerate(ORDER):
        for j,b in enumerate(ORDER):
            key=a+"__"+b if i<=j else b+"__"+a
            if abs(correlation(published_samples[a],published_samples[b])-float(stored["correlations"][key]))>0.000006:
                raise ValueError("Original published correlation mismatch "+key)
    weights=[WEIGHTS[a] for a in ORDER]
    static_var=sum(weights[i]*weights[j]*correlation(samples[ORDER[i]],samples[ORDER[j]])*
        (stdev(samples[ORDER[i]])*math.sqrt(12))*(stdev(samples[ORDER[j]])*math.sqrt(12))
        for i in range(4) for j in range(4))
    if static_var<=0:raise ValueError("Invalid static variance")
    subperiod=[]
    for label,start,end in [("2023-10_to_2024-09","2023-10","2024-09"),
                             ("2024-10_to_2025-09","2024-10","2025-09"),
                             ("2025-10_to_2026-10","2025-10","2026-10")]:
        ix=[i for i,k in enumerate(common_return_months) if start<=month_str(k)<=end]
        s={a:[samples[a][i] for i in ix] for a in ORDER}
        subperiod.append({"period":label,"n_months":len(ix),
            "annualized_volatility_pct":{a:round(vol(s[a]),3) for a in ORDER},
            "equity_gilt_correlation":round(correlation(s["equity"],s["gilt_fund"]),4),
            "gold_silver_correlation":round(correlation(s["gold_etf"],s["silver_etf"]),4)})
    result={"decision":"PASS_OFFICIAL_SOURCE_STRICT_DATE_ALIGNED_36M_R7_RESEARCH_ONLY",
            "investment_authorization":"NO_GO", "2036_probability_validated":False,
            "official_source_provenance_segments":len(manifest["source_manifest"]),
            "source_qualified_assets":ORDER,
            "observed_date_window":[month_str(keys[0]),month_str(keys[-1])],
            "monthly_return_window":[month_str(common_return_months[0]),month_str(common_return_months[-1])],
            "aligned_monthly_return_count":n,"source_checks":checks,
            "month_end_date_mismatches_quarantined":mismatch_dates,
            "affected_monthly_return_excluded":[month_str(keys[1])] if mismatch_dates else [],
            "original_37_month_window":[month_str(published_months[0]),month_str(published_months[-1])],
            "original_month_only_aligned_return_count":len(published_months),
            "source_csv_sha256":hashlib.sha256(INPUT.read_bytes()).hexdigest(),
            "qualification_manifest_sha256":hashlib.sha256(MANIFEST.read_bytes()).hexdigest(),
            "full_period_annualized_log_return_volatility_pct":{a:round(computed_vols[a],5) for a in ORDER},
            "correlation_matrix_order":ORDER,
            "correlation_matrix":[[round(x,7) for x in row] for row in corrs],
            "static_65_20_10_5_annualized_volatility_pct":round(100*math.sqrt(static_var),6),
            "subperiods":subperiod,
            "limitations":["36 strictly date-aligned monthly returns only after excluding mismatched September 2023 boundary; strong sampling uncertainty and nonstationarity",
                           "Selected four schemes are research proxies for risk sleeves, not selected portfolio",
                           "ETF NAVs are not necessarily executable market purchase/sale prices",
                           "NAV includes fund management expenses, so avoid TER double counting",
                           "Volatility/correlation do not independently validate forward expected returns, taxes, inflation or 2036 floor probability"] }
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"decision":result["decision"],"months":n,
        "static_volatility_pct":result["static_65_20_10_5_annualized_volatility_pct"],
        "subperiods":subperiod},indent=2))
if __name__=="__main__":main()
