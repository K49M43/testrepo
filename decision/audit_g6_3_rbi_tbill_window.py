from __future__ import annotations

import csv
import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timedelta
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
    r = next((x for x in p.rows if len(x) >= 5 and x[0] == "1" and re.sub(r"[^a-z0-9]", "", x[1].casefold()) in {"91day", "91days"}), None)
    if r is None:
        raise ValueError("91-day notice row missing")
    a = re.search(r"([A-Za-z]+\s+\d{1,2},\s+\d{4})", r[3])
    i = re.search(r"([A-Za-z]+\s+\d{1,2},\s+\d{4})", r[4])
    if not a or not i:
        raise ValueError("notice auction/issue dates missing")
    t = visible(body)
    m = re.search(r"(price|yield) based using ([a-z -]+?) metho\s*d", t)
    if not m:
        raise ValueError("notice auction method missing")
    method = f"{m.group(1)} based using {m.group(2).strip()} method"
    return {"auction_date": datetime.strptime(a.group(1), "%B %d, %Y").date().isoformat(), "issue_date": datetime.strptime(i.group(1), "%B %d, %Y").date().isoformat(), "notified_amount_crore": r[2].replace(",", ""), "auction_method": method}


def result(body):
    t = visible(body)
    d = re.search(r"date\s*:\s*([a-z]{3}\s+\d{1,2},\s+\d{4})", t)
    if not d:
        raise ValueError("result date missing")
    out = {"result_date": datetime.strptime(d.group(1).title(), "%b %d, %Y").date().isoformat()}
    rows = Rows()
    rows.feed(body.decode("utf-8", errors="replace"))
    cutoff, weighted = [], []
    for index, row in enumerate(rows.rows[:-1]):
        label = " ".join(row).casefold()
        target = cutoff if "cut-off price" in label and "yield" in label else weighted if "weighted average price" in label and "yield" in label else None
        if target is None:
            continue
        for price_cell, yield_cell in zip(row[-3:], rows.rows[index + 1][-3:]):
            price_match = re.search(r"(?<![\d.])[\d]+\.[\d]{1,4}(?![\d.])", price_cell)
            yield_match = re.search(r"([\d.]+)%", yield_cell)
            target.append((price_match.group(0) if price_match else "", yield_match.group(1) if yield_match else ""))
    for tenor, slot in (("91", 0), ("182", 1), ("364", 2)):
        if len(cutoff) > slot:
            if cutoff[slot][0]: out[f"cutoff_price_{tenor}"] = cutoff[slot][0]
            if cutoff[slot][1]: out[f"cutoff_yield_{tenor}"] = cutoff[slot][1]
        if len(weighted) > slot:
            if weighted[slot][0]: out[f"weighted_price_{tenor}"] = weighted[slot][0]
            if weighted[slot][1]: out[f"weighted_yield_{tenor}"] = weighted[slot][1]
    return out


def main():
    parser = argparse.ArgumentParser(description="Independently audit an official RBI 91-day T-bill auction window.")
    parser.add_argument("capture", nargs="?", type=Path, default=Path("rbi_tbill_window_capture"))
    parser.add_argument("--table-path", type=Path, default=TABLE218)
    parser.add_argument("--table-name", default="Table 218")
    parser.add_argument("--window-tag", default="2025_2026")
    parser.add_argument("--expected-auctions", type=int, default=50)
    parser.add_argument("--first-date", default="2025-07-02")
    parser.add_argument("--last-date", default="2026-06-24")
    args = parser.parse_args()
    capture = args.capture
    manifest = json.loads((capture / "manifest.json").read_text(encoding="utf-8"))
    ref = manifest.get("table_reference") or manifest.get("table218_reference") or manifest.get("table217_reference")
    table_path = args.table_path.resolve()
    if not table_path.is_file() or hashlib.sha256(table_path.read_bytes()).hexdigest() != ref["sha256"]:
        raise SystemExit(f"{args.table_name} reference hash mismatch")
    if ref.get("path") != table_path.relative_to(ROOT).as_posix():
        raise SystemExit(f"{args.table_name} reference path mismatch")
    expected = table218(table_path)
    if len(expected) != args.expected_auctions or min(expected) != args.first_date or max(expected) != args.last_date:
        raise SystemExit(f"unexpected {args.table_name} panel coverage")
    records = {x["path"]: x for x in manifest["sources"]}
    if len(records) != len(manifest["sources"]):
        raise SystemExit("duplicate source paths in manifest")
    for path, rec in records.items():
        body = (capture / path).read_bytes()
        if rec["http_status"] != 200 or rec["bytes"] != len(body) or rec["sha256"] != hashlib.sha256(body).hexdigest():
            raise SystemExit(f"source integrity mismatch: {path}")
    normalized_meta = manifest.get("normalized_panel")
    if normalized_meta:
        normalized_path = (capture / normalized_meta["path"]).resolve()
        if not normalized_path.is_relative_to(capture.resolve()) or not normalized_path.is_file():
            raise SystemExit("normalized panel path is missing or escapes the capture directory")
        normalized_bytes = normalized_path.read_bytes()
        if normalized_meta["bytes"] != len(normalized_bytes) or normalized_meta["sha256"] != hashlib.sha256(normalized_bytes).hexdigest():
            raise SystemExit("normalized panel byte count or hash mismatch")
    month_rows = [r for r in records.values() if r["path"].startswith("archive/")]
    first_month = datetime.strptime(args.first_date, "%Y-%m-%d").date().replace(day=1)
    first_month = (first_month - timedelta(days=1)).replace(day=1)
    last_month = datetime.strptime(args.last_date, "%Y-%m-%d").date().replace(day=1)
    expected_months = set()
    cursor = first_month
    while cursor <= last_month:
        expected_months.add((cursor.year, cursor.month))
        cursor = (cursor.replace(day=28) + timedelta(days=4)).replace(day=1)
    observed_months = {(int(r["parameters"]["hdnYear"]), int(r["parameters"]["hdnMonth"])) for r in month_rows}
    if observed_months != expected_months or any(r.get("method") != "POST" for r in month_rows):
        raise SystemExit(f"official archive month coverage mismatch: expected {len(expected_months)}, found {len(month_rows)}")
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
    with (capture / f"auction_panel_{args.window_tag}.csv").open(encoding="utf-8", newline="") as stream:
        panel = list(csv.DictReader(stream))
    if len(panel) != args.expected_auctions or len({r["auction_date"] for r in panel}) != args.expected_auctions:
        raise SystemExit(f"normalized panel must contain {args.expected_auctions} unique {args.table_name} dates; got {len(panel)}")
    if {r["auction_date"] for r in panel} != set(expected):
        raise SystemExit(f"normalized dates do not exactly equal {args.table_name} dates")
    exceptions = 0
    issue_date_conflicts = []
    for row in panel:
        d = row["auction_date"]
        nlist = notices.get(d, [])
        if len(nlist) != 1:
            raise SystemExit(f"expected one official notice for {d}, found {len(nlist)}")
        n = nlist[0]
        t = expected[d]
        if n["notified_amount_crore"] != t["notified_amount_crore"]:
            raise SystemExit(f"notice/{args.table_name} notified-amount mismatch: {d}")
        table_issue_date = row.get("table_issue_date") or t["issue_date"]
        if table_issue_date != t["issue_date"]:
            raise SystemExit(f"CSV/{args.table_name} table issue-date provenance mismatch: {d}")
        if row["issue_date"] != n["issue_date"]:
            raise SystemExit(f"CSV/auction-notice actual issue-date mismatch: {d}")
        if n["issue_date"] != t["issue_date"]:
            conflict = {
                "auction_date": d,
                "table_issue_date": t["issue_date"],
                "notice_issue_date": n["issue_date"],
                "resolution": "RETAIN_BOTH; USE_CONTEMPORANEOUS_AUCTION_NOTICE_FOR_ACTUAL_ISSUE_DATE",
            }
            issue_date_conflicts.append(conflict)
            if row.get("issue_date_resolution") != "NOTICE_OVERRIDES_TABLE_DATE_CONFLICT":
                raise SystemExit(f"undocumented notice/{args.table_name} issue-date conflict: {d}")
        elif row.get("issue_date_resolution") not in (None, "", "NOTICE_AND_TABLE_AGREE"):
            raise SystemExit(f"incorrect issue-date resolution marker: {d}")
        if row["auction_method"] != n["auction_method"]:
            raise SystemExit(f"CSV notice fields mismatch: {d}")
        total = t["total_issue_crore"].replace("-", "0")
        rlist = results.get(d, [])
        if total in {"0", "0.00"}:
            exceptions += 1
            if row["result_status"] != "ZERO_ISSUE_EXCEPTION":
                raise SystemExit(f"zero-issue row not explicitly classified: {d}")
            if len(rlist) != 1:
                raise SystemExit(f"expected one full result to verify other tenors on zero-issue date {d}, found {len(rlist)}")
            if any(rlist[0].get(k) for k in ("cutoff_price_91", "cutoff_yield_91", "weighted_price_91", "weighted_yield_91")):
                raise SystemExit(f"zero-issue 91-day source row conflicts with full result on {d}")
            continue
        if len(rlist) != 1:
            raise SystemExit(f"expected one full result for {d}, found {len(rlist)}")
        r = rlist[0]
        if not r.get("weighted_price_91") or r["cutoff_yield_91"] != t["cutoff_yield_actual_365_pct"]:
            raise SystemExit(f"full-result/{args.table_name} yield mismatch or missing weighted price: {d}")
        rounded = Decimal(r["cutoff_price_91"]).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if rounded != Decimal(t["cutoff_price"]):
            raise SystemExit(f"full-result/{args.table_name} cutoff-price rounding mismatch: {d}")
        for key in ("weighted_price_91", "weighted_yield_91", "cutoff_price_91", "cutoff_yield_91"):
            if row.get(key) != r[key]:
                raise SystemExit(f"CSV/source value mismatch {key} on {d}")

    declared_conflicts = manifest.get("source_discrepancies", {}).get("issue_date_conflicts", [])
    if declared_conflicts != issue_date_conflicts:
        raise SystemExit("manifest issue-date conflicts do not match independent notice/table comparison")

    # Descriptive auction-yield levels only. They are not realized holding-period
    # returns, a chained reinvestment path, or independent annual outcomes.
    matched = [row for row in panel if row["result_status"] == "MATCHED"]
    weighted_yields = sorted(Decimal(row["weighted_yield_91"]) for row in matched)
    weighted_prices = [Decimal(row["weighted_price_91"]) for row in matched]
    n = len(weighted_yields)
    mean_yield = sum(weighted_yields) / Decimal(n)
    sample_variance = sum((value - mean_yield) ** 2 for value in weighted_yields) / Decimal(n - 1)
    sample_sd = sample_variance.sqrt()
    four_dp = Decimal("0.0001")
    median_yield = weighted_yields[n // 2] if n % 2 else (weighted_yields[n // 2 - 1] + weighted_yields[n // 2]) / Decimal(2)
    method_counts = {}
    for row in panel:
        method_counts[row["auction_method"]] = method_counts.get(row["auction_method"], 0) + 1
    summary = {
        "classification": "DESCRIPTIVE_AUCTION_YIELD_LEVELS_NOT_REALIZED_RETURNS",
        "matched_91_day_positive_issue_observations": n,
        "auction_method_counts": method_counts,
        "weighted_yield_91_pct_actual_365": {
            "minimum": str(min(weighted_yields).quantize(four_dp, rounding=ROUND_HALF_UP)),
            "median": str(median_yield.quantize(four_dp, rounding=ROUND_HALF_UP)),
            "mean": str(mean_yield.quantize(four_dp, rounding=ROUND_HALF_UP)),
            "sample_standard_deviation_percentage_points": str(sample_sd.quantize(four_dp, rounding=ROUND_HALF_UP)),
            "maximum": str(max(weighted_yields).quantize(four_dp, rounding=ROUND_HALF_UP)),
            "last_minus_first_percentage_points": str((Decimal(matched[-1]["weighted_yield_91"]) - Decimal(matched[0]["weighted_yield_91"])).quantize(four_dp, rounding=ROUND_HALF_UP)),
        },
        "weighted_price_91_per_100_face": {
            "minimum": str(min(weighted_prices).quantize(four_dp, rounding=ROUND_HALF_UP)),
            "maximum": str(max(weighted_prices).quantize(four_dp, rounding=ROUND_HALF_UP)),
            "distinct_from_cutoff_price_observations": sum(row["weighted_price_91"] != row["cutoff_price_91"] for row in matched),
        },
    }
    result_status = f"PASS_RBI_TBILL_{args.window_tag}_EXACT_DATE_PANEL"
    if issue_date_conflicts:
        result_status += "_WITH_RECORDED_SOURCE_DATE_CONFLICTS"
    print(json.dumps({"result":result_status,"reference_table":args.table_name,"table_dates":len(expected),"matched_notice_dates":len(notices),"matched_result_dates":len(results),"zero_issue_exceptions":exceptions,"issue_date_conflicts":issue_date_conflicts,"captured_source_count":len(records),"descriptive_summary":summary},indent=2))

if __name__ == "__main__":
    main()
