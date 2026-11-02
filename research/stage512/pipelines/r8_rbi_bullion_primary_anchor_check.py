#!/usr/bin/env python3
"""R8 source-provenance gate: check seven primary RBI bulletin anchors against
437-month RBI-origin third-party DBIE mirror CSV. Not complete RBI validation.
"""
import csv, json, hashlib, datetime as dt, math
from pathlib import Path
BASE=Path("research/stage512/data")
SRC=BASE/"r8_rbi_origin_mirror/rbi_origin_mumbai_bullion_monthly_SECONDARY_MIRROR.csv"
PROVENANCE=BASE/"r8_rbi_origin_mirror/normalized_validation.json"
ANCHOR=BASE/"r8_rbi_bullion_official_published_anchors.csv"
OUTPUT=BASE/"r8_rbi_bullion_primary_spotcheck_manifest.json"
def csvrows(path):
    with path.open(newline="",encoding="utf8") as f:return list(csv.DictReader(f))
def main():
    out={"status":"FAIL", "timestamp_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
        "data_classification":"RBI_ORIGIN_437_MONTH_MIRROR_WITH_OFFICIAL_SAMPLED_ANCHORS",
        "entire_rbi_primary_data_verified":False,
        "2026_investment_gate":"NO_GO","primary_PDF_visual_review":"PENDING — text values checked, screenshot rendering unavailable in this environment"}
    try:
        manifest=json.loads(PROVENANCE.read_text())
        if manifest.get("status")!="PASS_SECONDARY_MIRROR_INTEGRITY_ONLY" or manifest.get("official_rbi_primary_verified"):
            raise ValueError("Source integrity/primary qualification flags invalid")
        if hashlib.sha256(SRC.read_bytes()).hexdigest()!=manifest["normalized_sha256"]:
            raise ValueError("Normalized CSV does not match manifest checksum")
        allRows=csvrows(SRC)
        monthly={z["month"]:z for z in allRows}
        if len(allRows)!=437 or len(monthly)!=437:raise ValueError("Expected 437 unique months")
        if min(monthly)!="1990-04" or max(monthly)!="2026-08":raise ValueError("Wrong data endpoints")
        published=csvrows(ANCHOR)
        if len(published)!=7:raise ValueError("Expected 7 independently sourced RBI reference months")
        comparisons=[]
        for row in published:
            m=row["month"];now=monthly.get(m)
            if now is None:raise ValueError("Missing official reference month: "+m)
            actualG=float(now["gold_inr_per_10g"]);actualS=float(now["silver_inr_per_kg"])
            knownG=float(row["gold_inr_per_10g"]);knownS=float(row["silver_inr_per_kg"])
            matches=actualG==knownG and actualS==knownS
            comparisons.append({"month":m,"gold_source":knownG,"gold_mirror":actualG,
                "silver_source":knownS,"silver_mirror":actualS,"both_match":matches,
                "official_rbi_publication_url":row["official_rbi_publication_url"]})
        if not all(x["both_match"] for x in comparisons):raise ValueError("Official RBI sampled anchor mismatch")
        out.update(status="PASS_OFFICIAL_RBI_SAMPLED_ANCHORS_ONLY",monthly_mirror_observations=437,
            official_months_checked=7,official_price_numbers_checked=14,
            official_matches=7,source_raw_sha256=manifest["raw_source_sha256"],
            normalized_source_sha256=manifest["normalized_sha256"],
            official_anchor_file_sha256=hashlib.sha256(ANCHOR.read_bytes()).hexdigest(),
            observation_window=["1990-04","2026-08"],checks=comparisons,
            caveats=["RBI source only spot-checked in seven published months; full 437-month primary validation outstanding",
                     "Two referenced RBI PDFs were read via extracted table text; a screenshot visual check was not obtained",
                     "Monthly AVERAGE Mumbai physical bullion prices are not ETF NAVs or end-of-month spot prices",
                     "Gold INR per 10g; silver INR per kg; no bullion taxes, exchange spreads or duties modeled",
                     "Do not splice monthly averages with last-trading-day fund NAV for comovement without timing reconciliation"])
    except Exception as exc:
        out["error"]=f"{type(exc).__name__}: {exc}"
    OUTPUT.write_text(json.dumps(out,indent=2)+"\n",encoding="utf8")
    print(json.dumps({k:out.get(k) for k in ["status","official_months_checked","official_matches","error"]}))
    return 0 if out["status"]=="PASS_OFFICIAL_RBI_SAMPLED_ANCHORS_ONLY" else 2
if __name__=="__main__":raise SystemExit(main())
