#!/usr/bin/env python3
"""Reconcile early RBI T-bill notice settlements and flag unqualified maturities."""
from __future__ import annotations

import argparse
import calendar
import csv
import hashlib
import json
from collections import Counter
from datetime import date, timedelta
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL_HOLIDAY_URL = "https://www.rbi.org.in/scripts/HolidayMatrixDisplay.aspx?regoff=Mumbai"
EXCEPTION_MANIFEST = "research/stage512/2026-11-25/g6_3/rbi_gsec_calendar_exceptions_v1.json"
EXCEPTION_SOURCE = "research/stage512/2026-11-25/g6_3/source_raw/rbi_gsec_market_open_exception_2023_09_29.html"
WINDOWS = (
    ("Table 213", "research/stage512/2026-11-24/g6_3/rbi_tbill_window_2023_2024", "auction_panel_2023_2024.csv", 60, "2023-07-12", "2024-08-28"),
    ("Table 217", "research/stage512/2026-11-19/g6_3/rbi_tbill_window_2024_2025", "auction_panel_2024_2025.csv", 55, "2024-07-03", "2025-07-30"),
    ("Table 218", "research/stage512/2026-11-06/g6_3/rbi_tbill_window_2025_2026", "auction_panel_2025_2026.csv", 50, "2025-07-02", "2026-06-24"),
)
HOLIDAY_PACKAGES = (
    ("early_settlement_2023", "research/stage512/2026-11-25/g6_3/rbi_mumbai_holidays_2023_07_2023_09", "2023-07", "2023-09"),
    ("early_maturity_2023_2024", "research/stage512/2026-11-25/g6_3/rbi_mumbai_holidays_2023_2024", "2023-10", "2024-09"),
    ("rollover_2024_2026", "research/stage512/2026-11-24/g6_3/rbi_mumbai_holidays_2024_2026", "2024-10", "2026-09"),
    ("settlement_2024", "research/stage512/2026-11-24/g6_3/rbi_mumbai_holidays_2024_07_2024_09", "2024-07", "2024-09"),
)
OVERLAP_FIELDS = (
    "issue_date", "notified_amount_crore", "total_issue_crore", "cutoff_price",
    "cutoff_yield_actual_365_pct", "result_status", "weighted_price_91", "weighted_yield_91",
)


class Rows(HTMLParser):
    """Minimal independent table reader used to validate the captured holiday pages."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[list[str]] = []
        self.row: list[str] | None = None
        self.cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "tr":
            self.row = []
        elif tag in {"td", "th"} and self.row is not None:
            self.cell = []

    def handle_data(self, data: str) -> None:
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"td", "th"} and self.cell is not None and self.row is not None:
            self.row.append(" ".join(" ".join(self.cell).split()))
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.row = None


class VisibleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self.skip += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self.skip:
            self.skip -= 1

    def handle_data(self, data: str) -> None:
        if not self.skip:
            self.parts.append(data)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def repo_bytes(relative: str) -> bytes:
    path = (ROOT / relative).resolve()
    require(path.is_relative_to(ROOT), f"source path escapes repository: {relative}")
    require(path.is_file(), f"source file missing: {relative}")
    return path.read_bytes()


def verify_blob(relative: str, record: dict[str, Any]) -> bytes:
    body = repo_bytes(relative)
    if "http_status" in record:
        require(record.get("http_status") == 200, f"source was not captured with HTTP 200: {relative}")
    require(record.get("bytes") == len(body), f"source byte count mismatch: {relative}")
    require(record.get("sha256") == hashlib.sha256(body).hexdigest(), f"source SHA-256 mismatch: {relative}")
    return body


def month_range(first: str, last: str) -> list[str]:
    year, month = map(int, first.split("-"))
    end_year, end_month = map(int, last.split("-"))
    months = []
    while (year, month) <= (end_year, end_month):
        months.append(f"{year:04d}-{month:02d}")
        if month == 12:
            year, month = year + 1, 1
        else:
            month += 1
    return months


def parse_month(body: bytes, year: int, month: int) -> list[dict[str, str]]:
    decoded = body.decode("utf-8", errors="replace")
    folded = " ".join(decoded.split()).casefold()
    expected_header = f"{calendar.month_name[month]} {year}"
    if f"there are no holidays in mumbai in {expected_header.casefold()}" in folded:
        return []
    parser = Rows()
    parser.feed(decoded)
    require(any(row and row[0] == expected_header for row in parser.rows), f"RBI holiday month header mismatch: {expected_header}")
    require(any(row and row[0].casefold() == "mumbai" for row in parser.rows), f"RBI month is not Mumbai: {expected_header}")
    header = next((i for i, row in enumerate(parser.rows) if len(row) >= 2 and row[0].casefold() == "holiday description" and row[1].casefold() == "day"), None)
    require(header is not None, f"RBI holiday details missing: {expected_header}")
    items = []
    for row in parser.rows[header + 1:]:
        if len(row) < 2:
            if items:
                break
            continue
        try:
            day = int(row[1])
        except ValueError:
            if items:
                break
            continue
        require(1 <= day <= calendar.monthrange(year, month)[1], f"RBI holiday day outside {expected_header}: {day}")
        items.append({"date": f"{year:04d}-{month:02d}-{day:02d}", "description": row[0]})
    require(len({item["date"] for item in items}) == len(items), f"duplicate RBI holiday date: {expected_header}")
    return items


def check_holiday_package(name: str, relative_dir: str, first: str, last: str) -> tuple[dict[str, list[dict[str, str]]], dict[str, Any]]:
    directory = ROOT / relative_dir
    manifest = read_json(directory / "manifest.json")
    coverage = manifest.get("coverage", {})
    declared_first = coverage.get("first_month", coverage.get("first_maturity_month"))
    declared_last = coverage.get("last_month", coverage.get("last_maturity_month"))
    expected = month_range(first, last)
    require(manifest.get("source_url") == OFFICIAL_HOLIDAY_URL, f"{name}: not the official RBI Mumbai holiday matrix")
    require(manifest.get("regional_office") == "Mumbai" and str(manifest.get("regional_office_value")) == "28", f"{name}: regional office is not Mumbai")
    require(declared_first == first and declared_last == last and coverage.get("months") == len(expected), f"{name}: declared month coverage mismatch")
    require("minimum 2 seconds" in manifest.get("request_policy", ""), f"{name}: rate-limit policy not recorded")
    sources = manifest.get("sources", [])
    paths = [source.get("path") for source in sources]
    require(len(paths) == len(set(paths)), f"{name}: duplicate source path")
    gets = [source for source in sources if source.get("method") == "GET"]
    posts = [source for source in sources if source.get("method") == "POST"]
    require(len(gets) == 1 and len(posts) == len(expected), f"{name}: expected one initial GET and one POST per month")
    for source in sources:
        require(source.get("url") == OFFICIAL_HOLIDAY_URL, f"{name}: unexpected source URL")
        require(source.get("content_type") and source.get("retrieved_at_utc"), f"{name}: response metadata missing")
        verify_blob(f"{relative_dir}/{source['path']}", source)
    parsed_manifest = {f"{item['year']:04d}-{item['month']:02d}": item["holiday_dates"] for item in manifest.get("parsed_mumbai_holidays", [])}
    require(sorted(parsed_manifest) == expected, f"{name}: parsed month coverage differs")
    parsed_raw = {}
    for source in posts:
        params = source.get("parameters", {})
        require(str(params.get("drRegionalOffice")) == "28", f"{name}: month page is not Mumbai")
        year, month = int(params["drYear"]), int(params["drMonth"])
        key = f"{year:04d}-{month:02d}"
        require(key in expected and key not in parsed_raw, f"{name}: duplicate or unexpected month POST: {key}")
        extracted = parse_month(repo_bytes(f"{relative_dir}/{source['path']}"), year, month)
        require(extracted == parsed_manifest[key], f"{name}: raw HTML and manifest holiday values differ: {key}")
        parsed_raw[key] = extracted
    require(sorted(parsed_raw) == expected, f"{name}: raw month page coverage differs")
    return parsed_raw, {
        "manifest": f"{relative_dir}/manifest.json", "months": len(parsed_raw),
        "raw_pages": len(sources), "holiday_dates": sum(map(len, parsed_raw.values())),
        "first_month": first, "last_month": last,
    }


def load_window(name: str, relative_dir: str, panel_name: str, expected_count: int, first: str, last: str) -> list[dict[str, str]]:
    directory = ROOT / relative_dir
    manifest = read_json(directory / "manifest.json")
    reference = manifest.get("table_reference") or manifest.get("table217_reference") or manifest.get("table218_reference")
    require(reference is not None, f"{name}: official table reference missing")
    verify_blob(reference["path"], reference)
    panel_meta = manifest.get("normalized_panel", {})
    panel_path = f"{relative_dir}/{panel_meta.get('path', panel_name)}"
    panel_bytes = repo_bytes(panel_path)
    if panel_meta:
        require(len(panel_bytes) == panel_meta.get("bytes") and hashlib.sha256(panel_bytes).hexdigest() == panel_meta.get("sha256"), f"{name}: normalized panel hash mismatch")
    else:
        require(name in {"Table 217", "Table 218"}, f"{name}: normalized panel has no recorded integrity basis")
    with (directory / panel_name).open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    dates = [row["auction_date"] for row in rows]
    require(len(rows) == expected_count and len(set(dates)) == expected_count, f"{name}: auction count or uniqueness mismatch")
    require(min(dates) == first and max(dates) == last, f"{name}: date coverage mismatch")
    return rows


def verify_gsec_exception() -> tuple[dict[str, Any], set[str]]:
    manifest = read_json(ROOT / EXCEPTION_MANIFEST)
    require(manifest.get("source_class") == "OFFICIAL_RBI_PRESS_RELEASE", "G-Sec exception is not sourced to an official RBI release")
    exceptions = manifest.get("operational_exception_dates", [])
    require(len(exceptions) == 1, "expected exactly one explicitly retained G-Sec calendar exception")
    exception = exceptions[0]
    require(exception.get("date") == "2023-09-29" and exception.get("status") == "GSEC_MARKET_OPERATIONAL_DESPITE_NI_ACT_PUBLIC_HOLIDAY", "unexpected G-Sec exception classification")
    require(exception.get("auction_settlement") == {"auction_date": "2023-09-27", "settlement_date": "2023-09-29"}, "G-Sec exception settlement scope changed")
    require(exception.get("rbi_press_release_number") == "2023-2024/1005", "G-Sec exception RBI release number changed")
    require("not a complete historical G-Sec business-day calendar" in manifest.get("interpretation_limit", ""), "G-Sec exception scope limitation missing")
    sources = manifest.get("sources", [])
    require(len(sources) == 1 and sources[0].get("url") == "https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=56455", "unexpected G-Sec exception source")
    body = verify_blob(EXCEPTION_SOURCE, sources[0])
    parser = VisibleText()
    parser.feed(body.decode("utf-8", errors="replace"))
    text = " ".join(" ".join(parser.parts).split()).casefold()
    required = (
        "september 29, 2023 as a public holiday", "government securities market",
        "operational on september 29, 2023",
        "treasury bills conducted on september 27, 2023 will take place on september 29, 2023",
        "2023-2024/1005",
    )
    require(all(phrase in text for phrase in required), "captured RBI G-Sec exception page does not support the manifest claims")
    return manifest, {exception["date"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "research/stage512/2026-11-25/g6_3")
    args = parser.parse_args()

    holidays_by_month: dict[str, list[dict[str, str]]] = {}
    packages = {}
    for name, directory, first, last in HOLIDAY_PACKAGES:
        records, summary = check_holiday_package(name, directory, first, last)
        packages[name] = summary
        for month, entries in records.items():
            require(month not in holidays_by_month or holidays_by_month[month] == entries, f"overlapping RBI holiday captures disagree: {month}")
            holidays_by_month[month] = entries
    months = month_range("2023-07", "2026-09")
    require(sorted(holidays_by_month) == months, "merged RBI holiday calendar is not contiguous from 2023-07 to 2026-09")
    ni_act_holidays = {item["date"] for entries in holidays_by_month.values() for item in entries}
    exception_manifest, gsec_open_override_dates = verify_gsec_exception()

    windows = {name: load_window(name, directory, panel, count, first, last) for name, directory, panel, count, first, last in WINDOWS}
    deduplicated: dict[str, dict[str, str]] = {}
    overlaps = []
    for i, (left_name, *_rest) in enumerate(WINDOWS):
        left = {row["auction_date"]: row for row in windows[left_name]}
        for right_name, *_right in WINDOWS[i + 1:]:
            right = {row["auction_date"]: row for row in windows[right_name]}
            shared = sorted(set(left) & set(right))
            mismatches = [
                {"auction_date": day, "field": field, "left": left[day].get(field), "right": right[day].get(field)}
                for day in shared for field in OVERLAP_FIELDS if left[day].get(field) != right[day].get(field)
            ]
            require(not mismatches, f"{left_name}/{right_name}: overlapping auction rows differ: {mismatches[:3]}")
            overlaps.append({"left": left_name, "right": right_name, "dates": len(shared), "field_mismatches": 0})
        for row in windows[left_name]:
            if row["auction_date"] in deduplicated:
                require(all(deduplicated[row["auction_date"]].get(field) == row.get(field) for field in OVERLAP_FIELDS), f"auction deduplication conflict: {row['auction_date']}")
            else:
                deduplicated[row["auction_date"]] = row
    require(len(deduplicated) == 151, f"deduplicated auction count changed: {len(deduplicated)}")
    positive_count = sum(row.get("result_status") == "MATCHED" and bool(row.get("weighted_price_91")) for row in deduplicated.values())
    require(positive_count == 149, f"positive 91-day observation count changed: {positive_count}")

    table213_rows = sorted(windows["Table 213"], key=lambda row: row["auction_date"])
    table_dir = ROOT / "research/stage512/2026-11-24/g6_3/rbi_tbill_window_2023_2024"
    table_manifest = read_json(table_dir / "manifest.json")
    conflicts = table_manifest.get("source_discrepancies", {}).get("issue_date_conflicts", [])
    require(len(table213_rows) == 60 and len(conflicts) == 4, "Table 213 window or retained notice/table conflict count changed")
    for source in table_manifest.get("sources", []):
        verify_blob(f"research/stage512/2026-11-24/g6_3/rbi_tbill_window_2023_2024/{source['path']}", source)
    verify_blob(table_manifest["table_reference"]["path"], table_manifest["table_reference"])
    conflict_dates = {item.get("auction_date") for item in conflicts}

    settlement_rows = []
    holiday_issue_dates = []
    weekend_issue_dates = []
    maturity_holiday_dates: Counter[str] = Counter()
    maturity_weekend_dates: Counter[str] = Counter()
    for row in table213_rows:
        auction = date.fromisoformat(row["auction_date"])
        issue = date.fromisoformat(row["issue_date"])
        require(issue > auction, f"notice issue date is not later than auction: {auction} -> {issue}")
        require(auction.strftime("%Y-%m") in holidays_by_month and issue.strftime("%Y-%m") in holidays_by_month, f"holiday evidence does not cover auction/issue date: {auction}")
        issue_is_holiday = issue.isoformat() in ni_act_holidays
        issue_is_weekend = issue.weekday() >= 5
        has_override = issue.isoformat() in gsec_open_override_dates
        if issue_is_holiday:
            holiday_issue_dates.append(issue.isoformat())
        if issue_is_weekend:
            weekend_issue_dates.append(issue.isoformat())
        require(not (issue_is_holiday or issue_is_weekend) or has_override, f"observed notice issue date needs a date-specific G-Sec operational source: {issue}")
        maturity = issue + timedelta(days=91)
        require(maturity.strftime("%Y-%m") in holidays_by_month, f"maturity holiday evidence does not cover nominal date: {maturity}")
        maturity_holiday = maturity.isoformat() in ni_act_holidays
        maturity_weekend = maturity.weekday() >= 5
        if maturity_holiday:
            maturity_holiday_dates[maturity.isoformat()] += 1
        if maturity_weekend:
            maturity_weekend_dates[maturity.isoformat()] += 1
        table_issue = row.get("table_issue_date", "")
        conflict = issue.isoformat() != table_issue
        require(conflict == (auction.isoformat() in conflict_dates), f"Table 213 notice/table issue-date discrepancy classification mismatch: {auction}")
        settlement_rows.append({
            "auction_date": auction.isoformat(),
            "rbi_notice_id": row.get("notice_prid", ""),
            "table213_issue_date": table_issue,
            "notice_issue_settlement_date": issue.isoformat(),
            "auction_to_issue_calendar_days": (issue - auction).days,
            "issue_date_is_mumbai_ni_act_holiday": issue_is_holiday,
            "issue_date_is_weekend": issue_is_weekend,
            "issue_date_has_explicit_gsec_open_override": has_override,
            "table_notice_issue_date_conflict": conflict,
            "nominal_issue_plus_91_day_maturity": maturity.isoformat(),
            "nominal_maturity_is_mumbai_ni_act_holiday": maturity_holiday,
            "nominal_maturity_is_weekend": maturity_weekend,
            "maturity_adjustment_status": "NOT_QUALIFIED_GSEC_CALENDAR_INCOMPLETE",
        })

    require(len(settlement_rows) == 60, "expected 60 notice settlement rows")
    require(holiday_issue_dates == ["2023-09-29"], f"unexpected notice issue date on NI Act holiday: {holiday_issue_dates}")
    require(weekend_issue_dates == [], f"unexpected weekend issue dates: {weekend_issue_dates}")
    require(gsec_open_override_dates == {"2023-09-29"}, "date-specific G-Sec override set changed")
    require(sum(maturity_holiday_dates.values()) == 4, f"expected four maturity dates on Mumbai NI Act holidays, found {sum(maturity_holiday_dates.values())}")

    result = {
        "schema_version": 1,
        "record_id": "g6-3-rbi-tbill-early-settlement-calendar-audit-2026-11-25-v1",
        "result": "PASS_NOTICE_SETTLEMENT_RECONCILIATION__MATURITY_ADJUSTMENT_UNQUALIFIED",
        "source_class": "OFFICIAL_RBI_AUCTION_TABLES_NOTICES_RESULTS_MUMBAI_HOLIDAY_MATRIX_AND_DATE_SPECIFIC_GSEC_EXCEPTION",
        "calendar_source_url": OFFICIAL_HOLIDAY_URL,
        "calendar_packages": packages,
        "mumbai_holiday_calendar_coverage": {"first_month": "2023-07", "last_month": "2026-09", "months": len(holidays_by_month), "unique_listed_dates": len(ni_act_holidays)},
        "gsec_operational_exception": {
            "manifest": EXCEPTION_MANIFEST,
            "rbi_release_number": "2023-2024/1005",
            "date": "2023-09-29",
            "scope": exception_manifest["interpretation_limit"],
        },
        "three_window_deduplication": {
            "unique_auction_dates": len(deduplicated),
            "positive_91_day_price_observations": positive_count,
            "pairwise_overlaps": overlaps,
            "use_limit": "Auction-yield levels and event dates only; not realized rollover returns, long-run risk history, or calibrated success probabilities.",
        },
        "table213_settlement_reconciliation": {
            "notice_settlement_dates_checked": len(settlement_rows),
            "notice_table_issue_date_conflicts": len(conflicts),
            "notice_table_conflict_auction_dates": sorted(conflict_dates),
            "notice_issue_dates_on_mumbai_ni_act_holidays": holiday_issue_dates,
            "holiday_settlement_dates_with_explicit_gsec_override": sorted(gsec_open_override_dates),
            "weekend_issue_dates": weekend_issue_dates,
            "settlement_basis": "Normalized issue_date is taken from the contemporaneous auction notice; both notice and Table 213 dates remain recorded. CI independently reparses notice/result source files.",
        },
        "nominal_maturity_calendar_flags": {
            "rows_checked": len(settlement_rows),
            "maturities_on_mumbai_ni_act_holidays": dict(sorted(maturity_holiday_dates.items())),
            "maturity_rows_on_mumbai_ni_act_holidays": sum(maturity_holiday_dates.values()),
            "maturity_dates_on_weekends": dict(sorted(maturity_weekend_dates.items())),
            "adjustment_status": "NOT_QUALIFIED",
            "reason": "The RBI Mumbai NI Act matrix is not a complete G-Sec operational calendar. The one verified 2023-09-29 override proves that holiday-matrix dates cannot be applied mechanically; other maturity dates need applicable official G-Sec settlement/holiday evidence.",
        },
        "limitations": [
            "The date-specific RBI release validates one G-Sec operational exception only, not a complete historical G-Sec calendar.",
            "No maturity date is adjusted in this audit, and no maturity-to-auction transition, cash wait, or rollover return is calculated.",
            "The RBI notice issue date does not prove investor-specific settlement timing or intraday availability of maturity proceeds.",
            "The auction panel remains a short history of auction quote levels, not a long-run risk distribution, exact cross-asset covariance, or 2036 floor-success probability.",
        ],
        "decision_status": "NO_GO",
        "investment_authorization": "NO_GO",
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / "rbi_tbill_early_settlement_calendar_audit_v1.json"
    csv_path = args.output_dir / "rbi_tbill_early_window_settlement_reconciliation_v1.csv"
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(settlement_rows[0]))
        writer.writeheader()
        writer.writerows(settlement_rows)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
