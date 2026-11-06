from __future__ import annotations
import argparse, csv, hashlib, json, io
from html.parser import HTMLParser
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

class TableParser(HTMLParser):
    """Extract table rows from the retained first-party PIB HTML without dependencies."""
    def __init__(self):
        super().__init__(); self.in_row = False; self.in_cell = False
        self.cell = ""; self.cells = []; self.rows = []
    def handle_starttag(self, tag, attrs):
        if tag == "tr": self.in_row = True; self.cells = []
        elif tag in ("td", "th") and self.in_row: self.in_cell = True; self.cell = ""
    def handle_data(self, data):
        if self.in_cell: self.cell += data
    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.in_cell:
            self.cells.append(" ".join(self.cell.split())); self.in_cell = False
        elif tag == "tr" and self.in_row:
            self.rows.append(self.cells); self.in_row = False

class TextParser(HTMLParser):
    def __init__(self): super().__init__(); self.parts = []
    def handle_data(self, data):
        if data.strip(): self.parts.append(" ".join(data.split()))

MONTHS = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
          "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}

def pib_monthly_combined_values(html: str) -> dict[str, str]:
    parser = TableParser(); parser.feed(html)
    copies = []; provisional_marks = []
    rows = parser.rows
    for i, row in enumerate(rows):
        if len(row) < 3 or row[0] != "Rural" or row[1] != "Urban" or row[2] != "Combined":
            continue
        values = {}; latest_is_marked_provisional = False
        for data in rows[i + 2:]:
            if len(data) < 4 or not data[0]:
                if values: break
                continue
            raw_label = data[0]; label = raw_label.rstrip("*")
            try:
                mon, year = label.split("-"); numeric_year = int(year)
                if numeric_year < 100: numeric_year += 2000
                key = f"{numeric_year:04d}-{MONTHS[mon]}"
                Decimal(data[3])
            except (ValueError, KeyError, ArithmeticError):
                if values: break
                continue
            require(key not in values, f"duplicate month within PIB table: {key}")
            values[key] = data[3]
            if key == "2026-09": latest_is_marked_provisional = raw_label.endswith("*")
        if values:
            copies.append(values); provisional_marks.append(latest_is_marked_provisional)
    require(len(copies) >= 1, "PIB monthly CPI table not found in archived HTML")
    require(all(copy == copies[0] for copy in copies[1:]), "duplicate PIB table copies disagree")
    require(all(provisional_marks), "PIB September 2026 monthly row lacks its provisional marker")
    expected = list(months("2025-01", "2026-09"))
    require(sorted(copies[0]) == expected, "PIB monthly CPI table does not cover Jan 2025-Sep 2026 contiguously")
    return copies[0]

def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)

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
    require(d.get("statusCode") is True, f"API status failed: {path.name}")
    return d

def validate_source_manifest() -> list[dict]:
    manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    require(manifest.get("schema_version") == "1.0.0", "unsupported CPI source manifest schema")
    assets = manifest.get("assets")
    require(isinstance(assets, list) and assets, "CPI source manifest has no assets")
    seen = set()
    for asset in assets:
        name = asset.get("file")
        require(isinstance(name, str) and Path(name).name == name and name not in seen,
                "CPI source manifest file names must be unique basenames")
        seen.add(name)
        path = RAW / name
        require(path.is_file(), f"manifest source file missing: {name}")
        data = path.read_bytes()
        require(len(data) == asset.get("bytes") and sha(path) == asset.get("sha256"),
                f"source-manifest hash/byte mismatch: {name}")
        require(isinstance(asset.get("url"), str) and asset["url"].startswith("https://"),
                f"source URL missing or not HTTPS: {name}")
        require(asset.get("http_status") == 200, f"source HTTP status not successful: {name}")
    captures = manifest.get("supporting_captures", [])
    require(isinstance(captures, list), "supporting_captures must be a list")
    for asset in captures:
        rel = Path(asset.get("path", ""))
        require(rel.parts and not rel.is_absolute() and ".." not in rel.parts,
                "supporting capture path must stay inside repository")
        path = ROOT / rel
        require(path.is_file(), f"supporting capture missing: {rel}")
        require(path.stat().st_size == asset.get("bytes") and sha(path) == asset.get("sha256"),
                f"supporting capture hash/byte mismatch: {rel}")
        require(asset.get("role") == "derived_capture", f"supporting capture role missing: {rel}")
    require(any(a.get("path") == str(PIB.relative_to(ROOT)).replace("\\", "/") for a in captures),
            "PIB comparison capture is absent from the source manifest")
    return assets

def make_result():
    source_assets = validate_source_manifest()
    require(LINK_PDF.read_bytes().startswith(b"%PDF-") and sha(LINK_PDF)=="7720b6404da8508dbf0c99ed56eae066a88bf2b873c2113c121326ffb53d69c4", "MoSPI linking annexure PDF hash/signature mismatch")
    pib_html=PIB_HTML.read_text(encoding="utf-8",errors="replace")
    pib_table = pib_monthly_combined_values(pib_html)
    pib_text = TextParser(); pib_text.feed(pib_html); pib_text = " ".join(pib_text.parts)
    require("September, 2026 (Provisional)" in pib_text and "5.54%(Provisional)" in pib_text,
            "PIB release summary does not verify September 2026 provisional status and 5.54% YoY anchor")
    records=[]
    sources=[]
    for name in BACK_FILES + (CURRENT_FILE,):
        path=RAW/name; d=read_json(path); records.extend(d["data"])
        sources.append({"file":name,"sha256":sha(path),"bytes":path.stat().st_size,"total_records":d["meta_data"]["totalRecords"],"page":d["meta_data"]["page"],"total_pages":d["meta_data"]["totalPages"]})
    require(len(records)==165, f"Expected 165 observations, got {len(records)}")
    indexed={}
    for r in records:
        require(r["base_year"]=="2024" and r["state"]=="All India" and r["sector"]=="Combined" and r["division"]=="CPI (General)", "unexpected CPI series identity")
        k=f"{int(r['year']):04d}-{int(r['month_code']):02d}"
        require(k not in indexed, f"duplicate month {k}")
        indexed[k]=r
    expected=list(months("2013-01","2026-09"))
    require(sorted(indexed)==expected, "month sequence has a gap or unexpected endpoint")
    back=[indexed[k] for k in expected if k<="2024-12"]
    current=[indexed[k] for k in expected if k>="2025-01"]
    require(len(back)==144 and len(current)==21, "back/current partition count changed")
    pib={r["month"]:r for r in csv.DictReader(PIB.open(encoding="utf-8-sig",newline=""))}
    current_keys = set(k for k in expected if k >= "2025-01")
    require(set(pib)==current_keys, "PIB CPI capture coverage differs from current series")
    require(set(pib_table)==current_keys, "PIB parsed table coverage differs from current series")
    require(all(Decimal(pib[k]["index_2024base_combined_displayed"])==Decimal(indexed[k]["index"])==Decimal(pib_table[k]) for k in pib), "PIB table/capture/API CPI values disagree")
    require(pib["2026-09"]["provisional"].lower()=="true", "latest CPI release provisional flag changed")
    # Keep officially published precision explicit: history is one decimal, current is two.
    out=[]
    for k in expected:
        r=indexed[k]
        out.append({"month":k,"base_year":"2024","series":r["series"],"state":"All India","sector":"Combined","division":"CPI (General)","index_official":r["index"],"api_yoy_inflation_pct":r["inflation"],"provisional_crosscheck":pib[k]["provisional"] if k in pib else "not_applicable"})
    buffer=io.StringIO(newline="")
    w=csv.DictWriter(buffer,fieldnames=list(out[0]),lineterminator="\n"); w.writeheader(); w.writerows(out)
    normalized_bytes=buffer.getvalue().encode("utf-8")
    result={
        "schema_version":"1.0.0","qualification":"PASS_SOURCE_SERIES_ONLY","source_manifest":{"file":SOURCE_MANIFEST.name,"sha256":sha(SOURCE_MANIFEST),"bytes":SOURCE_MANIFEST.stat().st_size,"assets_verified":len(source_assets)},"source":"MoSPI open CPI API, base_year 2024","identity":{"state":"All India","sector":"Combined","division":"CPI (General)"},
        "coverage":{"observations":165,"start":"2013-01","end":"2026-09","back_series":{"observations":144,"start":"2013-01","end":"2024-12","identity":"Back"},"current_series":{"observations":21,"start":"2025-01","end":"2026-09","identity":"Current"}},
        "checks":{"monthly_contiguous":True,"duplicate_months":0,"historical_api_back_series_directly_qualified":True,"current_series_exactly_matches_pib_table_capture_and_api_at_source_precision":True,"pib_html_table_copies_identical":True,"latest_month":"2026-09","latest_is_provisional":True},
        "precision_and_use":{"back_series_precision":"MoSPI API back-series values are qualified directly. The 0.5267 linking factor is a methodological cross-reference only; the prior staged legacy CSV is not used as independent numeric validation because its original observation-level source bytes were not retained in this evidence package.","current_series_precision":"two decimals as supplied by current API and MoSPI PIB release","future_inflation":"not estimated; CPI observations are a historical deflator only","investor_real_wealth":"blocked until investor confirms 2026 purchasing-power base month"},
        "primary_release_crosschecks":[{"file":LINK_PDF.name,"bytes":LINK_PDF.stat().st_size,"sha256":sha(LINK_PDF),"manually_verified":"MoSPI Annexure V, PDF page 5: Combined linking factor 0.5267 and linked back series coverage Jan 2013-Dec 2024; method corroboration only"},{"file":PIB_HTML.name,"bytes":PIB_HTML.stat().st_size,"sha256":sha(PIB_HTML),"machine_checked":"Parsed all 21 monthly combined-index values Jan 2025-Sep 2026 from each retained monthly table copy; identical copies and every value agrees with the manifest-listed comparison capture and MoSPI API"}],
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
    print("PASS: 165 contiguous MoSPI API observations; 21 current-series values also match parsed PIB tables/capture; latest Sep 2026 provisional")
if __name__=="__main__": main()

