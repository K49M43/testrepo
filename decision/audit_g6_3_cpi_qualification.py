from __future__ import annotations
import argparse, csv, hashlib, json, io
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "research/stage512/2026-11-06/g6_3"
RAW = EVIDENCE / "source_raw"
BACK_FILES = ("mospi_back_general_p1.json", "mospi_back_general_p2.json")
CURRENT_FILE = "mospi_current_general_2025_2026.json"
NORMALIZED = EVIDENCE / "cpi_mospi_api_combined_general_2013_2026.csv"
STAGED = ROOT / "research/stage512/2026-11-02/stage512_cpi_official_linked_2013_2026.csv"
PIB = ROOT / "research/stage512/2026-11-02/cpi_pib_sep2026_annexure_iv_capture.csv"
LINK_PDF = RAW / "mospi_cpi_2024_base_linked_backseries_annexure_v.pdf"
PIB_HTML = RAW / "pib_cpi_sep2026.html"
OUTPUT = EVIDENCE / "cpi_qualification_v1.json"
SOURCE_MANIFEST = EVIDENCE / "cpi_source_manifest_v1.json"
FACTOR = Decimal("0.5267")

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def months(start: str, end: str):
    y, m = map(int, start.split("-")); ey, em = map(int, end.split("-"))
    while (y, m) <= (ey, em):
        yield f"{y:04d}-{m:02d}"
        m += 1
        if m == 13: y, m = y + 1, 1

def read_json(path: Path):
    d=json.loads(path.read_text(encoding="utf-8-sig"))
    assert d.get("statusCode") is True, f"API status failed: {path.name}"
    return d

def make_result():
    assert LINK_PDF.read_bytes().startswith(b"%PDF-") and sha(LINK_PDF)=="7720b6404da8508dbf0c99ed56eae066a88bf2b873c2113c121326ffb53d69c4", "MoSPI linking annexure PDF hash/signature mismatch"
    pib_html=PIB_HTML.read_text(encoding="utf-8",errors="replace")
    assert "109.49" in pib_html and "5.54%(Provisional)" in pib_html, "PIB Sep 2026 primary release anchor missing"
    records=[]
    sources=[]
    for name in BACK_FILES + (CURRENT_FILE,):
        path=RAW/name; d=read_json(path); records.extend(d["data"])
        sources.append({"file":name,"sha256":sha(path),"bytes":path.stat().st_size,"total_records":d["meta_data"]["totalRecords"],"page":d["meta_data"]["page"],"total_pages":d["meta_data"]["totalPages"]})
    assert len(records)==165, f"Expected 165 observations, got {len(records)}"
    indexed={}
    for r in records:
        assert r["base_year"]=="2024" and r["state"]=="All India" and r["sector"]=="Combined" and r["division"]=="CPI (General)"
        k=f"{int(r['year']):04d}-{int(r['month_code']):02d}"
        assert k not in indexed, f"duplicate month {k}"
        indexed[k]=r
    expected=list(months("2013-01","2026-09"))
    assert sorted(indexed)==expected, "month sequence has a gap or unexpected endpoint"
    back=[indexed[k] for k in expected if k<="2024-12"]
    current=[indexed[k] for k in expected if k>="2025-01"]
    assert len(back)==144 and len(current)==21
    staged={r["month"]:r for r in csv.DictReader(STAGED.open(encoding="utf-8-sig",newline=""))}
    assert set(staged)==set(expected)
    back_mismatches=[]
    for r in back:
        k=f"{int(r['year']):04d}-{int(r['month_code']):02d}"
        linked=(Decimal(staged[k]["old_2012base"])*FACTOR).quantize(Decimal("0.1"),rounding=ROUND_HALF_UP)
        if linked != Decimal(r["index"]): back_mismatches.append({"month":k,"factor_rounded_1dp":str(linked),"api_index":r["index"]})
    assert not back_mismatches, f"back series mismatch at published 1dp precision: {back_mismatches[:4]}"
    current_mismatches=[]
    for r in current:
        k=f"{int(r['year']):04d}-{int(r['month_code']):02d}"
        if Decimal(staged[k]["index_2024base"]) != Decimal(r["index"]):
            current_mismatches.append({"month":k,"staged":staged[k]["index_2024base"],"api":r["index"]})
    assert not current_mismatches, f"direct current series mismatches: {current_mismatches[:4]}"
    pib={r["month"]:r for r in csv.DictReader(PIB.open(encoding="utf-8-sig",newline=""))}
    assert set(pib)==set(k for k in expected if k>="2025-01")
    assert all(Decimal(pib[k]["index_2024base_combined_displayed"])==Decimal(indexed[k]["index"]) for k in pib)
    assert pib["2026-09"]["provisional"].lower()=="true"
    # Keep officially published precision explicit: history is one decimal, current is two.
    out=[]
    for k in expected:
        r=indexed[k]
        out.append({"month":k,"base_year":"2024","series":r["series"],"state":"All India","sector":"Combined","division":"CPI (General)","index_official":r["index"],"api_yoy_inflation_pct":r["inflation"],"provisional_crosscheck":pib[k]["provisional"] if k in pib else "not_applicable"})
    buffer=io.StringIO(newline="")
    w=csv.DictWriter(buffer,fieldnames=list(out[0]),lineterminator="\n"); w.writeheader(); w.writerows(out)
    normalized_bytes=buffer.getvalue().encode("utf-8")
    result={
        "schema_version":"1.0.0","qualification":"PASS_SOURCE_SERIES_ONLY","source_manifest":{"file":SOURCE_MANIFEST.name,"sha256":sha(SOURCE_MANIFEST),"bytes":SOURCE_MANIFEST.stat().st_size},"source":"MoSPI open CPI API, base_year 2024","identity":{"state":"All India","sector":"Combined","division":"CPI (General)"},
        "coverage":{"observations":165,"start":"2013-01","end":"2026-09","back_series":{"observations":144,"start":"2013-01","end":"2024-12","identity":"Back"},"current_series":{"observations":21,"start":"2025-01","end":"2026-09","identity":"Current"}},
        "checks":{"monthly_contiguous":True,"duplicate_months":0,"back_series_matches_factor_0_5267_at_1_decimal":True,"current_series_exactly_matches_existing_capture_at_source_precision":True,"current_series_matches_pib_annexure_values":True,"latest_month":"2026-09","latest_is_provisional":True},
        "precision_and_use":{"back_series_precision":"API returns a two-decimal string that matches the MoSPI linking-factor series when compared at one-decimal published CPI precision; do not treat the old-index multiplication's five decimal places as source accuracy.","current_series_precision":"two decimals as supplied by current API and MoSPI release","future_inflation":"not estimated; CPI observations are a historical deflator only","investor_real_wealth":"blocked until investor confirms 2026 purchasing-power base month"},
        "primary_release_crosschecks":[{"file":LINK_PDF.name,"bytes":LINK_PDF.stat().st_size,"sha256":sha(LINK_PDF),"manually_verified":"MoSPI Annexure V, PDF page 5: Combined linking factor 0.5267 and linked back series coverage Jan 2013-Dec 2024"},{"file":PIB_HTML.name,"bytes":PIB_HTML.stat().st_size,"sha256":sha(PIB_HTML),"machine_checked_anchor":"Sep 2026 combined CPI index 109.49; year-on-year inflation 5.54% (provisional)"}],
        "assets":sources+[{"file":"cpi_mospi_api_combined_general_2013_2026.csv","sha256":hashlib.sha256(normalized_bytes).hexdigest(),"bytes":len(normalized_bytes),"observations":len(out)}]
    }
    return result, normalized_bytes

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--check",action="store_true"); args=ap.parse_args()
    result, normalized_bytes=make_result(); rendered=(json.dumps(result,indent=2,ensure_ascii=False)+"\n").encode()
    if args.check:
        if not NORMALIZED.exists() or NORMALIZED.read_bytes()!=normalized_bytes:
            raise SystemExit("FAIL: normalized CPI CSV differs from official source data")
        if not OUTPUT.exists() or OUTPUT.read_bytes()!=rendered:
            raise SystemExit("FAIL: CPI qualification artifact differs; regenerate and review")
    else:
        NORMALIZED.write_bytes(normalized_bytes)
        OUTPUT.write_bytes(rendered)
    print("PASS: 165 contiguous CPI observations; 144 linked back-series matches at one-decimal precision; 21 current-series records match capture exactly; latest Sep 2026 provisional")
if __name__=="__main__": main()

