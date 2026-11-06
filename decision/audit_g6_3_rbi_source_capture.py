from __future__ import annotations

import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPTURE = ROOT / "research/stage512/2026-11-06/g6_3/source_raw/rbi_tbill_sample"
EXPECTED = {
    "table218_20260731.html": ("table 218", "treasury bills"),
    "auction_notice_20261030.html": ("retail direct", "individual investors"),
    "full_result_20261104.html": ("weighted average price", "98.5535"),
    "cutoff_result_20261104.html": ("cut-off price", "98.5511"),
    "retail_ncb_faq.html": ("weighted average", "non-competitive"),
    "press_release_archive.html": ("press release", "treasury bills", "2025"),
    "archive_month_202511.html": ("treasury bills", "2025"),
}


class VisibleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def visible_text(body: bytes) -> str:
    parser = VisibleText()
    parser.feed(body.decode("utf-8", errors="replace"))
    return re.sub(r"\s+", " ", " ".join(parser.parts)).casefold()


def main() -> None:
    manifest_path = CAPTURE / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    records = {item["path"]: item for item in manifest["sources"]}
    if set(records) != set(EXPECTED):
        raise SystemExit(f"manifest file set mismatch: {sorted(records)}")
    month = records["archive_month_202511.html"]
    if month.get("method") != "POST" or month.get("parameters") != {"hdnYear": "2025", "hdnMonth": "11"}:
        raise SystemExit("archive month request metadata mismatch")
    month_text = visible_text((CAPTURE / "archive_month_202511.html").read_bytes())
    dates = re.findall(r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{1,2},\s+2025\b", month_text)
    if not dates or not any(date.startswith("nov ") for date in dates) or any(not date.startswith("nov ") for date in dates):
        raise SystemExit(f"archive month does not contain only November 2025 dates: {dates}")
    results = []
    for filename, snippets in EXPECTED.items():
        path = CAPTURE / filename
        body = path.read_bytes()
        actual_hash = hashlib.sha256(body).hexdigest()
        record = records[filename]
        if record["http_status"] != 200 or record["bytes"] != len(body) or record["sha256"] != actual_hash:
            raise SystemExit(f"manifest integrity mismatch: {filename}")
        text = visible_text(body)
        missing = [snippet for snippet in snippets if snippet not in text]
        if missing:
            raise SystemExit(f"source identity/content anchor missing for {filename}: {missing}")
        results.append({"path": filename, "bytes": len(body), "sha256": actual_hash, "content_anchors": list(snippets)})
    print(json.dumps({"result": "PASS_RBI_SOURCE_CAPTURE_INTEGRITY", "sources": results}, indent=2))


if __name__ == "__main__":
    main()