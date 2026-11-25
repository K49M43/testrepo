from __future__ import annotations

import csv
import hashlib
import json
from datetime import date, timedelta
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "research/stage512/2026-11-25/g6_3"
FAQ_MANIFEST = ROOT / "research/stage512/2026-11-24/g6_3/source_raw/rbi_rollover_policy_sources_v1.json"
MATURITY_FLAGS = OUTPUT_DIR / "rbi_tbill_early_window_settlement_reconciliation_v1.csv"
HOLIDAY_DIRS = (
    (OUTPUT_DIR / "rbi_mumbai_holidays_2023_2024", {"first_month": "2023-10", "last_month": "2024-09", "months": 12}),
    (ROOT / "research/stage512/2026-11-24/g6_3/rbi_mumbai_holidays_2024_2026", {"first_maturity_month": "2024-10", "last_maturity_month": "2026-09", "months": 24}),
)
WINDOWS = (
    ("Table 213", ROOT / "research/stage512/2026-11-24/g6_3/rbi_tbill_window_2023_2024", "auction_panel_2023_2024.csv"),
    ("Table 217", ROOT / "research/stage512/2026-11-19/g6_3/rbi_tbill_window_2024_2025", "auction_panel_2024_2025.csv"),
    ("Table 218", ROOT / "research/stage512/2026-11-06/g6_3/rbi_tbill_window_2025_2026", "auction_panel_2025_2026.csv"),
)
OVERLAP_FIELDS = (
    "issue_date", "notified_amount_crore", "total_issue_crore", "cutoff_price",
    "cutoff_yield_actual_365_pct", "result_status", "weighted_price_91", "weighted_yield_91",
)


class TableRows(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[list[str]] = []
        self.row: list[str] | None = None
        self.cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs) -> None:
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

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"script", "style"}:
            self.skip += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self.skip:
            self.skip -= 1

    def handle_data(self, data: str) -> None:
        if not self.skip:
            self.parts.append(data)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def source_path(directory: Path, value: str) -> Path:
    candidate = directory / value
    if candidate.is_file():
        return candidate
    candidate = ROOT / value
    if candidate.is_file():
        return candidate
    raise SystemExit(f"manifest source not found: {value}")


def verify_record(directory: Path, record: dict) -> None:
    path = source_path(directory, record["path"])
    body = path.read_bytes()
    if record.get("http_status") != 200:
        raise SystemExit(f"source did not record HTTP 200: {record['path']}")
    if record.get("bytes") != len(body):
        raise SystemExit(f"source byte count mismatch: {record['path']}")
    if record.get("sha256") != hashlib.sha256(body).hexdigest():
        raise SystemExit(f"source SHA-256 mismatch: {record['path']}")


def read_window(name: str, directory: Path, panel_name: str) -> tuple[dict, list[dict[str, str]]]:
    manifest = load_json(directory / "manifest.json")
    ref = manifest.get("table_reference") or manifest.get("table217_reference") or manifest.get("table218_reference")
    if not ref:
        raise SystemExit(f"{name}: table reference missing")
    body = source_path(ROOT, ref["path"]).read_bytes()
    if len(body) != ref.get("bytes") or hashlib.sha256(body).hexdigest() != ref.get("sha256"):
        raise SystemExit(f"{name}: table reference hash/byte mismatch")
    for record in manifest.get("sources", []):
        verify_record(directory, record)
    panel_path = directory / panel_name
    panel = panel_path.read_bytes()
    panel_meta = manifest.get("normalized_panel", {})
    if panel_meta and (len(panel) != panel_meta.get("bytes") or hashlib.sha256(panel).hexdigest() != panel_meta.get("sha256")):
        raise SystemExit(f"{name}: normalized panel hash/byte mismatch")
    with panel_path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != manifest.get("expected_auctions") or len({r["auction_date"] for r in rows}) != len(rows):
        raise SystemExit(f"{name}: panel row count/date uniqueness mismatch")
    return manifest, rows


def holiday_dates_and_descriptions() -> dict[str, str]:
    all_dates: dict[str, str] = {}
    for holiday_dir, expected_coverage in HOLIDAY_DIRS:
        manifest = load_json(holiday_dir / "manifest.json")
        if manifest.get("coverage") != expected_coverage:
            raise SystemExit(f"holiday source package coverage mismatch: {holiday_dir}")
        first_month = expected_coverage.get("first_month", expected_coverage.get("first_maturity_month"))
        last_month = expected_coverage.get("last_month", expected_coverage.get("last_maturity_month"))
        expected_months: list[str] = []
        year, month = map(int, first_month.split("-"))
        final_year, final_month = map(int, last_month.split("-"))
        while (year, month) <= (final_year, final_month):
            expected_months.append(f"{year:04d}-{month:02d}")
            if month == 12:
                year, month = year + 1, 1
            else:
                month += 1
        parsed: dict[str, str] = {}
        parsed_months = [f"{row['year']:04d}-{row['month']:02d}" for row in manifest.get("parsed_mumbai_holidays", [])]
        if parsed_months != expected_months:
            raise SystemExit(f"parsed holiday months incomplete or out of order: {holiday_dir}")
        for month in manifest.get("parsed_mumbai_holidays", []):
            for entry in month.get("holiday_dates", []):
                parsed[entry["date"]] = entry["description"]
        rebuilt: dict[str, str] = {}
        source_records = manifest.get("sources", [])
        post_records = [record for record in source_records if record.get("method") == "POST"]
        post_months = sorted(f"{int(record['parameters']['drYear']):04d}-{int(record['parameters']['drMonth']):02d}" for record in post_records)
        if post_months != expected_months or len([record for record in source_records if record.get("method") == "GET"]) != 1:
            raise SystemExit(f"raw holiday page coverage incomplete: {holiday_dir}")
        for record in source_records:
            verify_record(holiday_dir, record)
            if record.get("method") != "POST":
                continue
            params = record.get("parameters", {})
            if params.get("drRegionalOffice") != "28":
                raise SystemExit(f"holiday source is not Mumbai: {record['path']}")
            year, month = int(params["drYear"]), int(params["drMonth"])
            header = date(year, month, 1).strftime("%B %Y").casefold()
            body = source_path(holiday_dir, record["path"]).read_bytes().decode("utf-8", errors="replace")
            rows = TableRows()
            rows.feed(body)
            normalized = [[cell.casefold() for cell in row] for row in rows.rows]
            start = next((i for i, row in enumerate(normalized) if len(row) >= 2 and row[0] == "holiday description" and row[1] == "day"), None)
            if start is None:
                text = " ".join(body.casefold().split())
                if f"there are no holidays in mumbai in {header}" in text:
                    continue
                raise SystemExit(f"holiday table header missing: {record['path']}")
            for row in rows.rows[start + 1:]:
                if len(row) < 2:
                    continue
                try:
                    day = int(row[1])
                except ValueError:
                    continue
                if not 1 <= day <= 31:
                    raise SystemExit(f"invalid holiday day in {record['path']}: {day}")
                key = f"{year:04d}-{month:02d}-{day:02d}"
                rebuilt[key] = row[0]
        if rebuilt != parsed:
            raise SystemExit(f"holiday dates parsed from RBI pages differ from the source manifest: {holiday_dir}")
        for key, description in rebuilt.items():
            if key in all_dates and all_dates[key] != description:
                raise SystemExit(f"overlapping RBI holiday packages conflict: {key}")
            all_dates[key] = description
    return all_dates


def previous_mumbai_nonholiday_weekday(day: date, holidays: dict[str, str]) -> date:
    candidate = day - timedelta(days=1)
    while candidate.weekday() >= 5 or candidate.isoformat() in holidays:
        candidate -= timedelta(days=1)
    return candidate


def main() -> None:
    windows: dict[str, tuple[dict, list[dict[str, str]]]] = {}
    for name, directory, panel_name in WINDOWS:
        windows[name] = read_window(name, directory, panel_name)

    deduplicated: dict[str, dict[str, str]] = {}
    for _, rows in windows.values():
        for row in rows:
            key = row["auction_date"]
            if key in deduplicated:
                mismatches = [field for field in OVERLAP_FIELDS if deduplicated[key].get(field) != row.get(field)]
                if mismatches:
                    raise SystemExit(f"three-window overlap mismatch on {key}: {mismatches}")
            else:
                deduplicated[key] = row
    positive = {
        date.fromisoformat(key): row
        for key, row in deduplicated.items()
        if row.get("result_status") == "MATCHED" and row.get("weighted_price_91")
    }
    if len(deduplicated) != 151 or len(positive) != 149:
        raise SystemExit(f"expected 151 unique/149 positive observations, got {len(deduplicated)}/{len(positive)}")

    faq_manifest = load_json(FAQ_MANIFEST)
    faq_record = next((row for row in faq_manifest.get("sources", []) if row.get("path", "").endswith("retail_ncb_faq.html")), None)
    if not faq_record:
        raise SystemExit("RBI FAQ source record not found")
    verify_record(ROOT, faq_record)
    faq_body = source_path(ROOT, faq_record["path"]).read_bytes().decode("utf-8", errors="replace")
    text_parser = VisibleText()
    text_parser.feed(faq_body)
    faq_text = " ".join(" ".join(text_parser.parts).split()).casefold()
    tbill_heading = faq_text.find("treasury bills (t-bills)")
    dated_gsec_heading = faq_text.find("dated g-secs")
    holiday_rule = faq_text.find("however, if the maturity date falls on a sunday or a holiday")
    if min(tbill_heading, dated_gsec_heading, holiday_rule) < 0 or not tbill_heading < dated_gsec_heading < holiday_rule:
        raise SystemExit("RBI FAQ section-order evidence did not match the retained source")

    holidays = holiday_dates_and_descriptions()
    with MATURITY_FLAGS.open(encoding="utf-8", newline="") as stream:
        flags = list(csv.DictReader(stream))
    target_dates = {"2024-04-11", "2024-05-23", "2024-08-15", "2024-11-15"}
    target_flags = [row for row in flags if row["nominal_issue_plus_91_day_maturity"] in target_dates]
    if len(target_flags) != 4 or {row["nominal_issue_plus_91_day_maturity"] for row in target_flags} != target_dates:
        raise SystemExit("the four expected nominal holiday maturities were not found exactly once")

    events = []
    for flag in sorted(target_flags, key=lambda row: row["nominal_issue_plus_91_day_maturity"]):
        auction_key = flag["auction_date"]
        origin = deduplicated.get(auction_key)
        if not origin or origin["issue_date"] != flag["notice_issue_settlement_date"] or origin["result_status"] != "MATCHED":
            raise SystemExit(f"origin issue/settlement does not reconcile for {auction_key}")
        nominal = date.fromisoformat(origin["issue_date"]) + timedelta(days=91)
        if nominal.isoformat() != flag["nominal_issue_plus_91_day_maturity"]:
            raise SystemExit(f"91-day nominal maturity arithmetic mismatch for {auction_key}")
        if nominal.isoformat() not in holidays or flag["nominal_maturity_is_mumbai_ni_act_holiday"] != "True":
            raise SystemExit(f"nominal maturity is not an independently parsed Mumbai holiday: {nominal}")
        conditional = previous_mumbai_nonholiday_weekday(nominal, holidays)
        same_day_auction = positive.get(conditional)
        same_day_settlement = next((row for row in positive.values() if row["issue_date"] == conditional.isoformat()), None)
        next_after_nominal = next((d for d in sorted(positive) if d > nominal), None)
        next_after_conditional = next((d for d in sorted(positive) if d > conditional), None)
        if next_after_nominal is None or next_after_conditional is None:
            raise SystemExit(f"successor auction missing for {nominal}")
        if next_after_nominal != next_after_conditional:
            raise SystemExit(f"strict-after successor changed unexpectedly for {nominal}")
        next_row = positive[next_after_conditional]
        events.append({
            "origin_auction_date": auction_key,
            "origin_notice_id": flag["rbi_notice_id"],
            "origin_notice_issue_settlement_date": origin["issue_date"],
            "nominal_maturity_date_issue_plus_91_calendar_days": nominal.isoformat(),
            "mumbai_holiday_description": holidays[nominal.isoformat()],
            "conditional_previous_mumbai_nonholiday_weekday": conditional.isoformat(),
            "conditional_date_is_actual_tbill_redemption_date": "NOT_ESTABLISHED",
            "positive_tbill_auction_on_conditional_date": bool(same_day_auction),
            "positive_tbill_issue_settlement_on_conditional_date": bool(same_day_settlement),
            "same_day_maturity_proceeds_funding_eligibility": "UNQUALIFIED_AND_EXCLUDED",
            "next_positive_auction_strictly_after_nominal_date": next_after_nominal.isoformat(),
            "next_positive_auction_strictly_after_conditional_date": next_after_conditional.isoformat(),
            "next_positive_issue_settlement_date": next_row["issue_date"],
            "calendar_days_nominal_to_next_bid_date": (next_after_nominal - nominal).days,
            "calendar_days_conditional_date_to_next_bid_date": (next_after_conditional - conditional).days,
            "calendar_days_extra_wait_if_previous_day_rule_applies": (next_after_conditional - conditional).days - (next_after_nominal - nominal).days,
            "source_status": "CONDITIONAL_MECHANICS_ONLY; T_BILL_HOLIDAY_RULE_SCOPE_AND_PROCEEDS_CREDIT_UNQUALIFIED",
        })

    csv_path = OUTPUT_DIR / "rbi_tbill_holiday_maturity_sensitivity_v1.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(events[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(events)

    result = {
        "schema_version": 1,
        "record_id": "g6-3-rbi-tbill-maturity-rule-scope-audit-2026-11-25-v1",
        "as_of": "2026-11-25",
        "result": "RBI_RULE_SCOPE_AMBIGUOUS_FOR_TBILLS__FOUR_EVENT_SENSITIVITY_REPRODUCED__ROLLOVER_STILL_UNQUALIFIED",
        "rule_evidence": {
            "source_url": faq_record["url"],
            "source_path": faq_record["path"],
            "source_sha256": faq_record["sha256"],
            "t_bill_definition_and_tenors_present": True,
            "holiday_rule_text_present": True,
            "section_order": "Treasury Bills subsection precedes Dated G-Secs subsection; previous-working-day sentence occurs after the Dated G-Secs heading.",
            "t_bill_specific_holiday_adjustment_qualified": False,
            "interpretation": "Do not promote the previous-working-day sentence into a T-bill-specific rule without an explicit applicable RBI/GoI source. Keep any calendar adjustment as sensitivity only.",
        },
        "official_2018_tbill_terms_access": {
            "rbi_notification_url": "https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=11250&Mode=0",
            "linked_goi_tbill_notification_url": "https://rbidocs.rbi.org.in/rdocs/content/pdfs/GOI27032018_TBill.pdf",
            "status": "RBI_ATTACHMENT_PATH_PRESENTS_HUMAN_VERIFICATION_CHALLENGE_IN_BROWSER_TOOL; RAW_BYTES_NOT_RETAINED",
            "local_official_source_fetch": "A separate local fetch attempt for the official 2025 eGazette PDF was refused by the execution environment; it was not a fetch attempt for this 2018 attachment. No access control was bypassed.",
            "gate_effect": "Historical 2024 T-bill maturity terms remain unqualified until the applicable 2018 terms or a date-specific RBI/GoI redemption record is retained and audited.",
        },
        "historical_panel": {
            "unique_auction_dates": len(deduplicated),
            "positive_91_day_observations": len(positive),
            "zero_issue_exceptions": sorted(k for k, row in deduplicated.items() if row.get("result_status") != "MATCHED"),
            "source_windows": [name for name, _, _ in WINDOWS],
        },
        "holiday_calendar": {
            "source_manifests": [
                "research/stage512/2026-11-25/g6_3/rbi_mumbai_holidays_2023_2024/manifest.json",
                "research/stage512/2026-11-24/g6_3/rbi_mumbai_holidays_2024_2026/manifest.json",
            ],
            "coverage": "2023-10 through 2026-09, 36 months; relevant raw pages rehashed and all monthly pages independently reparsed",
            "usage_limit": "RBI Mumbai holiday matrix is not treated as a complete G-Sec/T-bill operational calendar.",
        },
        "conditional_event_sensitivity": {
            "rows": len(events),
            "events_with_auction_on_conditional_date": sum(bool(row["positive_tbill_auction_on_conditional_date"]) for row in events),
            "next_strictly_later_auction_changes_between_nominal_and_conditional_dates": sum(row["next_positive_auction_strictly_after_nominal_date"] != row["next_positive_auction_strictly_after_conditional_date"] for row in events),
            "event_schedule_csv": "research/stage512/2026-11-25/g6_3/rbi_tbill_holiday_maturity_sensitivity_v1.csv",
            "scope": "Descriptive date alignment only. No actual redemption date, credited-funds timing, investor return, auction allocation, tax, fee or probability is inferred.",
        },
        "decision_status": "NO_GO",
        "investment_authorization": "NO_GO",
    }
    json_path = OUTPUT_DIR / "rbi_tbill_maturity_rule_scope_audit_v1.json"
    json_path.write_bytes((json.dumps(result, indent=2) + "\n").encode("utf-8"))
    print(f"Wrote {json_path.relative_to(ROOT)} and {csv_path.relative_to(ROOT)}")
    print(f"Four conditional cases audited; T-bill holiday rule remains unqualified; {len(deduplicated)} unique auction dates / {len(positive)} positive 91-day observations.")


if __name__ == "__main__":
    main()
