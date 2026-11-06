from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLE218 = ROOT / "research/stage512/2026-11-06/g6_3/source_raw/rbi_tbill_sample/table218_20260731.html"


class Rows(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows, self.row, self.cell = [], None, None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.row = []
        elif tag in {"td", "th"} and self.row is not None:
            self.cell = []

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in {"td", "th"} and self.cell is not None and self.row is not None:
            self.row.append(re.sub(r"\s+", " ", " ".join(self.cell)).strip())
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.row = None


class Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style"} and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def visible(body):
    p = Text()
    p.feed(body.decode("utf-8", errors="replace"))
    return re.sub(r"\s+", " ", " ".join(p.parts)).casefold()


def table218(path):
    p = Rows()
    p.feed(path.read_text(encoding="utf-8", errors="replace"))
    out = {}
    for r in p.rows:
        if len(r) >= 12 and re.fullmatch(r"\d{1,2}-[A-Za-z]{3}-\d{4}", r[0]):
            d = datetime.strptime(r[0], "%d-%b-%Y").date().isoformat()
            out[d] = {"auction_date": d, "issue_date": datetime.strptime(r[1], "%d-%b-%Y").date().isoformat(), "notified_amount_crore": r[2].replace(",", ""), "total_issue_crore": r[-3].replace(",", ""), "cutoff_price": r[-2], "cutoff_yield_actual_365_pct": r[-1]}
    return out


def notice(body):
    p = Rows()
    p.feed(body.decode("utf-8", errors="replace"))
    r = next((x for x in p.rows if len(x) >= 5 and x[0] == "1" and x[1].casefold() == "91-day"), None)
    if r is None:
        raise ValueError("91-day notice row missing")
    a = re.search(r"([A-Za-z]+\s+\d{1,2},\s+\d{4})", r[3])
    i = re.search(r"([A-Za-z]+\s+\d{1,2},\s+\d{4})", r[4])
    if not a or not i:
        raise ValueError("notice auction/issue dates missing")
    t = visible(body)
    m = re.search(r"(price|yield) based using ([a-z -]+?) method", t)
    if not m:
        raise ValueError("notice auction method missing")
    return {"auction_date": datetime.strptime(a.group(1), "%B %d, %Y").date().isoformat(), "issue_date": datetime.strptime(i.group(1), "%B %d, %Y").date().isoformat(), "notified_amount_crore": r[2].replace(",", ""), "auction_method": m.group(0)}


def result(body):
    t = visible(body)
    d = re.search(r"date\s*:\s*([a-z]{3}\s+\d{1,2},\s+\d{4})", t)
    if not d:
        raise ValueError("result date missing")
    out = {"result_date": datetime.strptime(d.group(1).title(), "%b %d, %Y").date().isoformat()}
    c = re.search(r"cut-off price and implicit yield at cut-off price\s+([\d.]+)\s+\(ytm:\s*([\d.]+)%\)\s+([\d.]+)\s+\(ytm:\s*([\d.]+)%\)\s+([\d.]+)\s+\(ytm:\s*([\d.]+)%\)", t)
    w = re.search(r"weighted average price/yield\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+\(way:\s*([\d.]+)%\)\s+\(way:\s*([\d.]+)%\)\s+\(way:\s*([\d.]+)%\)", t)
    if c:
        out.update({"cutoff_price_91": c.group(1), "cutoff_yield_91": c.group(2), "cutoff_price_182": c.group(3), "cutoff_yield_182": c.group(4), "cutoff_price_364": c.group(5), "cutoff_yield_364": c.group(6)})
    if w:
        out.update({"weighted_price_91": w.group(1), "weighted_price_182": w.group(2), "weighted_price_364": w.group(3), "weighted_yield_91": w.group(4), "weighted_yield_182": w.group(5), "weighted_yield_364": w.group(6)})
    return out


def main():
    capture = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("rbi_tbill_window_capture")
    manifest = json.loads((capture / "manifest.json").read_text(encoding="utf-8"))
    ref = manifest["table218_reference"]
    if not TABLE218.is_file() or hashlib.sha256(TABLE218.read_bytes()).hexdigest() != ref["sha256"]:
        raise SystemExit("Table 218 reference hash mismatch")
    expected = table218(TABLE218)
    if len(expected) != 50 or min(expected) != "2025-07-02" or max(expected) != "2026-06-24":
        raise SystemExit("unexpected Table 218 panel coverage")
    records = {x["path"]: x for x in manifest["sources"]}
    if len(records) != len(manifest["sources"]):
        raise SystemExit("duplicate source paths in manifest")
    for path, rec in records.items():
        body = (capture / path).read_bytes()
        if rec["http_status"] != 200 or rec["bytes"] != len(body) or rec["sha256"] != hashlib.sha256(body).hexdigest():
            raise SystemExit(f"source integrity mismatch: {path}")
    month_rows = [r for r in records.values() if r["path"].startswith("archive/")]
    if len(month_rows) != 13 or any(r.get("method") != "POST" for r in month_rows):
        raise SystemExit(f"expected 13 official month POST captures, found {len(month_rows)}")
    notices = {}
    results = {}
    for p, rec in records.items():
        body = (capture / p).read_bytes()
        if p.startswith("notices/"):
            n = notice(body)
            notices.setdefault(n["auction_date"], []).append(n)
        elif p.startswith("results/"):
            r = result(body)
            results.setdefault(r["result_date"], []).append(r)
    with (capture / "auction_panel_2025_2026.csv").open(encoding="utf-8", newline="") as stream:
        panel = list(csv.DictReader(stream))
    if len(panel) != 50 or len({r["auction_date"] for r in panel}) != 50:
        raise SystemExit(f"normalized panel must contain 50 unique Table 218 dates; got {len(panel)}")
    if {r["auction_date"] for r in panel} != set(expected):
        raise SystemExit("normalized dates do not exactly equal Table 218 dates")
    exceptions = 0
    for row in panel:
        d = row["auction_date"]
        nlist = notices.get(d, [])
        if len(nlist) != 1:
            raise SystemExit(f"expected one official notice for {d}, found {len(nlist)}")
        n = nlist[0]
        t = expected[d]
        if n["issue_date"] != t["issue_date"] or n["notified_amount_crore"] != t["notified_amount_crore"]:
            raise SystemExit(f"notice/Table 218 date or notified-amount mismatch: {d}")
        if row["issue_date"] != t["issue_date"] or row["auction_method"] != n["auction_method"]:
            raise SystemExit(f"CSV notice fields mismatch: {d}")
        total = t["total_issue_crore"].replace("-", "0")
        rlist = results.get(d, [])
        if total in {"0", "0.00"}:
            exceptions += 1
            if row["result_status"] != "ZERO_ISSUE_EXCEPTION":
                raise SystemExit(f"zero-issue row not explicitly classified: {d}")
            continue
        if len(rlist) != 1:
            raise SystemExit(f"expected one full result for {d}, found {len(rlist)}")
        r = rlist[0]
        if not r.get("weighted_price_91") or r["cutoff_yield_91"] != t["cutoff_yield_actual_365_pct"]:
            raise SystemExit(f"full-result/Table 218 yield mismatch or missing weighted price: {d}")
        rounded = Decimal(r["cutoff_price_91"]).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if rounded != Decimal(t["cutoff_price"]):
            raise SystemExit(f"full-result/Table 218 cutoff-price rounding mismatch: {d}")
        for key in ("weighted_price_91", "weighted_yield_91", "cutoff_price_91", "cutoff_yield_91"):
            if row.get(key) != r[key]:
                raise SystemExit(f"CSV/source value mismatch {key} on {d}")
    print(json.dumps({"result":"PASS_RBI_TBILL_2025_2026_EXACT_DATE_PANEL","table218_dates":len(expected),"matched_notice_dates":len(notices),"matched_result_dates":len(results),"zero_issue_exceptions":exceptions,"captured_source_count":len(records)},indent=2))

if __name__ == "__main__":
    main()
