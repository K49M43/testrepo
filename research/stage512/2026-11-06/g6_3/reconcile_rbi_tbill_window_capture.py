#!/usr/bin/env python3
"""Reconcile already-captured RBI auction pages without making network requests."""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import sys
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
CAPTURE_SCRIPT = Path(__file__).with_name("acquire_rbi_tbill_window.py")
SPEC = importlib.util.spec_from_file_location("rbi_tbill_capture", CAPTURE_SCRIPT)
CAPTURE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CAPTURE
SPEC.loader.exec_module(CAPTURE)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_timestamp(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()


def source_record(path: Path, out: Path, url: str, method: str, **extra) -> dict:
    body = path.read_bytes()
    return {
        "path": path.relative_to(out).as_posix(),
        "url": url,
        "method": method,
        # The acquisition code wrote each body only after observing HTTP 200.
        "http_status": 200,
        # The failed reconciliation attempt did not persist response headers.
        "content_type": "NOT_RETAINED_DURING_CAPTURE_ATTEMPT",
        "retrieved_at_utc": file_timestamp(path),
        "bytes": len(body),
        "sha256": digest(body),
        **extra,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--table-path", required=True, type=Path)
    parser.add_argument("--table-url", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--table-name", required=True)
    parser.add_argument("--window-tag", required=True)
    parser.add_argument("--expected-auctions", required=True, type=int)
    parser.add_argument("--first-date", required=True)
    parser.add_argument("--last-date", required=True)
    args = parser.parse_args()

    table_path = args.table_path.resolve()
    out = args.output_dir.resolve()
    if not table_path.is_file() or not out.is_dir():
        raise SystemExit("captured table or output directory is missing")
    table_bytes = table_path.read_bytes()
    expected = CAPTURE.parse_table218(table_bytes, args.expected_auctions, args.first_date, args.last_date)
    auction_dates = [date.fromisoformat(value) for value in expected]

    first_month = min(auction_dates).replace(day=1) - timedelta(days=1)
    first_month = first_month.replace(day=1)
    last_month = max(auction_dates).replace(day=1)
    months = []
    cursor = first_month
    while cursor <= last_month:
        months.append((cursor.year, cursor.month))
        cursor = (cursor.replace(day=28) + timedelta(days=4)).replace(day=1)

    index_path = out / "archive_index.html"
    if not index_path.is_file():
        raise SystemExit("captured RBI archive index is missing")
    records = [source_record(index_path, out, CAPTURE.ARCHIVE_URL, "GET")]
    all_items = []
    for year, month in months:
        name = f"archive_{year}_{month:02d}.html"
        path = out / "archive" / name
        if not path.is_file():
            raise SystemExit(f"captured archive month is missing: {name}")
        records.append(source_record(
            path, out, CAPTURE.ARCHIVE_URL, "POST",
            parameters={"hdnYear": str(year), "hdnMonth": str(month)},
        ))
        all_items.extend(CAPTURE.archive_items(path.read_bytes()))

    notice_start = min(auction_dates) - timedelta(days=7)
    notice_end = max(auction_dates)
    notice_links = {
        item["prid"]: item for item in all_items
        if CAPTURE.is_tbill_notice_title(item["title"])
        and notice_start.isoformat() <= item["archive_date"] <= notice_end.isoformat()
    }
    result_links = {
        item["prid"]: item for item in all_items
        if "full auction result" in item["title"].casefold()
        and item["archive_date"] in expected
    }

    notice_by_date: dict[str, list[dict]] = {}
    for prid, item in notice_links.items():
        name = f"notice_prid{prid}.html"
        path = out / "notices" / name
        if not path.is_file():
            continue
        records.append(source_record(path, out, item["url"], "GET", archive_date=item["archive_date"]))
        detail = CAPTURE.notice_data(path.read_bytes())
        if detail["auction_date"] in expected:
            detail.update({"prid": prid, "path": f"notices/{name}", "url": item["url"]})
            notice_by_date.setdefault(detail["auction_date"], []).append(detail)

    result_by_date: dict[str, dict] = {}
    for prid, item in result_links.items():
        name = f"full_result_prid{prid}.html"
        path = out / "results" / name
        if not path.is_file():
            continue
        records.append(source_record(path, out, item["url"], "GET", archive_date=item["archive_date"]))
        detail = CAPTURE.result_data(path.read_bytes())
        if detail["result_date"] != item["archive_date"]:
            raise SystemExit(f"archive/result date mismatch for {prid}")
        detail.update({"prid": prid, "path": f"results/{name}", "url": item["url"]})
        if detail["result_date"] in result_by_date:
            raise SystemExit(f"duplicate full results for {detail['result_date']}")
        result_by_date[detail["result_date"]] = detail

    rows = []
    zero_issue_exceptions = []
    issue_date_conflicts = []
    for auction_date, table_row in sorted(expected.items()):
        notice_candidates = notice_by_date.get(auction_date, [])
        if len(notice_candidates) != 1:
            raise SystemExit(f"expected one official notice for {auction_date}; found {len(notice_candidates)}")
        notice = notice_candidates[0]
        if notice["notified_amount_crore"] != table_row["notified_amount_crore"]:
            raise SystemExit(f"notified amount mismatch on {auction_date}")
        table_issue_date = table_row["issue_date"]
        issue_date = notice["issue_date"]
        issue_date_resolution = "NOTICE_AND_TABLE_AGREE"
        if issue_date != table_issue_date:
            issue_date_resolution = "NOTICE_OVERRIDES_TABLE_DATE_CONFLICT"
            issue_date_conflicts.append({
                "auction_date": auction_date,
                "table_issue_date": table_issue_date,
                "notice_issue_date": issue_date,
                "resolution": "RETAIN_BOTH; USE_CONTEMPORANEOUS_AUCTION_NOTICE_FOR_ACTUAL_ISSUE_DATE",
            })

        total_issue = table_row["total_issue_crore"].replace("-", "0")
        result = result_by_date.get(auction_date)
        row = {
            **table_row,
            "table_issue_date": table_issue_date,
            "issue_date": issue_date,
            "issue_date_resolution": issue_date_resolution,
            "notice_prid": notice["prid"],
            "notice_date": notice["notice_date"],
            "auction_method": notice["auction_method"],
            "retail_route_stated": notice["retail_route"],
            "notice_path": notice["path"],
            "result_status": "MATCHED" if result else "NO_RESULT_PAGE",
        }
        if total_issue in {"0", "0.00"}:
            row["result_status"] = "ZERO_ISSUE_EXCEPTION"
            if result and result.get("weighted_price_91"):
                raise SystemExit(f"zero-issue row has a positive 91-day result: {auction_date}")
            zero_issue_exceptions.append({"auction_date": auction_date, "status": "ZERO_ISSUE_EXCEPTION"})
        else:
            if not result:
                raise SystemExit(f"positive-issue auction lacks a full result: {auction_date}")
            if result.get("cutoff_yield_91") != table_row["cutoff_yield_actual_365_pct"]:
                raise SystemExit(f"91-day cutoff-yield mismatch: {auction_date}")
            result_price = result.get("cutoff_price_91")
            if result_price and Decimal(result_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) != Decimal(table_row["cutoff_price"]):
                raise SystemExit(f"91-day cutoff-price rounding mismatch: {auction_date}")
            row.update({key: value for key, value in result.items() if key.startswith(("weighted_", "cutoff_"))})
            row["result_path"] = result["path"]
            row["result_prid"] = result["prid"]
        rows.append(row)

    if len(notice_by_date) != args.expected_auctions or len(result_by_date) != args.expected_auctions:
        raise SystemExit("captured source dates do not cover every table auction exactly once")

    panel_name = f"auction_panel_{args.window_tag}.csv"
    panel_path = out / panel_name
    fields = sorted({key for row in rows for key in row})
    with panel_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    source_times = [datetime.fromisoformat(record["retrieved_at_utc"]) for record in records]
    panel_bytes = panel_path.read_bytes()
    table_reference = {
        "path": table_path.relative_to(ROOT).as_posix(),
        "url": args.table_url,
        "method": "GET",
        "http_status": 200,
        "content_type": "NOT_RETAINED_DURING_CAPTURE_ATTEMPT",
        "retrieved_at_utc": file_timestamp(table_path),
        "bytes": len(table_bytes),
        "sha256": digest(table_bytes),
    }
    manifest = {
        "schema_version": 1,
        "captured_at_utc": max(source_times).isoformat(),
        "manifest_reconciled_at_utc": datetime.now(timezone.utc).isoformat(),
        "capture_reconstruction": {
            "mode": "OFFLINE_RECONCILIATION_FROM_RETAINED_RAW_RESPONSES",
            "network_refetch_performed": False,
            "http_status_basis": "The original capture wrote response bodies only after verifying HTTP status 200.",
            "response_header_limitation": "Content-Type headers were not persisted before the original run stopped during cross-source validation; content_type is explicitly marked NOT_RETAINED.",
            "retrieval_timestamp_basis": "Per-file filesystem write timestamps in UTC; no response Date header is asserted.",
        },
        "scope": f"Official RBI T-bill notice/full-result pairs for {args.expected_auctions} rows in {args.table_name} ({args.first_date} through {args.last_date}); table/notice issue-date conflicts retain both source values and use the contemporaneous auction notice for the normalized issue date; auction-yield levels only, not a calibrated risk history.",
        "request_policy": "Original capture used sequential requests with a minimum 2-second gap, max 3 attempts for HTTP 429 only, 30-second timeout, and 5 MB response cap; this reconciliation made no network requests.",
        "reference_table": args.table_name,
        "table_reference": table_reference,
        "normalized_panel": {"path": panel_name, "bytes": len(panel_bytes), "sha256": digest(panel_bytes)},
        "window": {"first_date": args.first_date, "last_date": args.last_date},
        "expected_auctions": len(expected),
        "matched_notice_dates": len(notice_by_date),
        "matched_full_result_dates": len(result_by_date),
        "exceptions": zero_issue_exceptions,
        "source_discrepancies": {"issue_date_conflicts": issue_date_conflicts},
        "sources": records,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "result": "RECONCILED_RBI_TBILL_CAPTURE_FROM_RETAINED_BYTES",
        "reference_table": args.table_name,
        "table_dates": len(expected),
        "matched_notice_dates": len(notice_by_date),
        "matched_result_dates": len(result_by_date),
        "issue_date_conflicts": issue_date_conflicts,
        "source_count": len(records),
        "network_refetch_performed": False,
        "manifest": str(out / "manifest.json"),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
