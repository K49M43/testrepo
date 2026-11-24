from __future__ import annotations

import argparse
import calendar
import csv
import hashlib
import json
import math
import statistics
from datetime import date, timedelta
from decimal import Decimal, ROUND_FLOOR
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WINDOWS = (
    ("Table 217", ROOT / "research/stage512/2026-11-19/g6_3/rbi_tbill_window_2024_2025", "auction_panel_2024_2025.csv"),
    ("Table 218", ROOT / "research/stage512/2026-11-06/g6_3/rbi_tbill_window_2025_2026", "auction_panel_2025_2026.csv"),
)
OVERLAP_FIELDS = (
    "issue_date", "notified_amount_crore", "total_issue_crore", "cutoff_price",
    "cutoff_yield_actual_365_pct", "result_status", "weighted_price_91", "weighted_yield_91",
)
HOLIDAY_DIR = ROOT / "research/stage512/2026-11-24/g6_3/rbi_mumbai_holidays_2024_2026"
RULE_SOURCE_MANIFEST = ROOT / "research/stage512/2026-11-24/g6_3/source_raw/rbi_rollover_policy_sources_v1.json"


class Rows(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows = []
        self.row = None
        self.cell = None

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
            self.row.append(" ".join(" ".join(self.cell).split()))
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.row = None


def parse_holiday_page(body: bytes, year: int, month: int) -> list[dict[str, str]]:
    text = " ".join(body.decode("utf-8", errors="replace").split()).casefold()
    header = date(year, month, 1).strftime("%B %Y")
    if f"there are no holidays in mumbai in {header.casefold()}" in text:
        return []
    parser = Rows()
    parser.feed(body.decode("utf-8", errors="replace"))
    if not any(row and row[0] == header for row in parser.rows):
        raise SystemExit(f"holiday page month header mismatch: {header}")
    if not any(row and row[0].casefold() == "mumbai" for row in parser.rows):
        raise SystemExit(f"holiday page has no Mumbai row: {header}")
    start = next((i for i, row in enumerate(parser.rows) if len(row) >= 2 and row[0].casefold() == "holiday description" and row[1].casefold() == "day"), None)
    if start is None:
        raise SystemExit(f"holiday descriptions missing: {header}")
    holidays = []
    for row in parser.rows[start + 1:]:
        if len(row) < 2:
            if holidays: break
            continue
        try:
            day = int(row[1])
        except ValueError:
            if holidays: break
            continue
        if not 1 <= day <= calendar.monthrange(year, month)[1]:
            raise SystemExit(f"invalid holiday day in {header}: {day}")
        holidays.append({"date": f"{year:04d}-{month:02d}-{day:02d}", "description": row[0]})
    return holidays


def read_window(name: str, directory: Path, panel_name: str) -> tuple[dict, list[dict[str, str]]]:
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    reference = manifest.get("table_reference") or manifest.get("table217_reference") or manifest.get("table218_reference")
    if not reference:
        raise SystemExit(f"{name}: reference-table manifest missing")
    table_path = ROOT / reference["path"]
    body = table_path.read_bytes()
    if hashlib.sha256(body).hexdigest() != reference["sha256"] or len(body) != reference["bytes"]:
        raise SystemExit(f"{name}: reference-table hash/byte mismatch")
    with (directory / panel_name).open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != manifest["expected_auctions"] or len({r["auction_date"] for r in rows}) != len(rows):
        raise SystemExit(f"{name}: panel row count or date uniqueness mismatch")
    return manifest, rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Independently reconcile adjacent official RBI T-bill windows and qualify rollover mechanics.")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "research/stage512/2026-11-24/g6_3")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    windows: dict[str, tuple[dict, list[dict[str, str]]]] = {}
    for name, directory, panel_name in WINDOWS:
        windows[name] = read_window(name, directory, panel_name)
    first_manifest, first_rows = windows["Table 217"]
    second_manifest, second_rows = windows["Table 218"]
    first = {row["auction_date"]: row for row in first_rows}
    second = {row["auction_date"]: row for row in second_rows}
    overlap_dates = sorted(set(first) & set(second))
    overlap_mismatches = [
        {"auction_date": day, "field": field, "table217": first[day].get(field), "table218": second[day].get(field)}
        for day in overlap_dates
        for field in OVERLAP_FIELDS
        if first[day].get(field) != second[day].get(field)
    ]
    if overlap_mismatches:
        raise SystemExit(f"Table 217/Table 218 overlap mismatch: {overlap_mismatches[:5]}")

    holiday_manifest = json.loads((HOLIDAY_DIR / "manifest.json").read_text(encoding="utf-8"))
    if holiday_manifest.get("coverage", {}).get("months") != 24:
        raise SystemExit("RBI holiday matrix does not declare all 24 expected months")
    holiday_sources = {record["path"]: record for record in holiday_manifest.get("sources", [])}
    if len(holiday_sources) != len(holiday_manifest.get("sources", [])):
        raise SystemExit("duplicate RBI holiday source paths")
    holiday_records = {f"{entry['year']:04d}-{entry['month']:02d}": entry["holiday_dates"] for entry in holiday_manifest.get("parsed_mumbai_holidays", [])}
    expected_months = []
    y, m = 2024, 10
    while (y, m) <= (2026, 9):
        expected_months.append(f"{y:04d}-{m:02d}")
        if m == 12: y, m = y + 1, 1
        else: m += 1
    if sorted(holiday_records) != expected_months:
        raise SystemExit("RBI holiday matrix parsed-month coverage mismatch")
    initial_pages = [record for record in holiday_sources.values() if record.get("method") == "GET"]
    month_pages = [record for record in holiday_sources.values() if record.get("method") == "POST"]
    if len(initial_pages) != 1 or len(month_pages) != 24:
        raise SystemExit(f"RBI holiday raw capture count mismatch: GET={len(initial_pages)} POST={len(month_pages)}")
    holiday_dates: set[str] = set()
    for path, record in holiday_sources.items():
        body = (HOLIDAY_DIR / path).read_bytes()
        if record.get("http_status") != 200 or record.get("bytes") != len(body) or record.get("sha256") != hashlib.sha256(body).hexdigest():
            raise SystemExit(f"RBI holiday source integrity mismatch: {path}")
        if record.get("method") != "POST":
            continue
        year, month = int(record["parameters"]["drYear"]), int(record["parameters"]["drMonth"])
        key = f"{year:04d}-{month:02d}"
        if record["parameters"].get("drRegionalOffice") != "28":
            raise SystemExit(f"RBI holiday source is not the Mumbai office: {path}")
        extracted = parse_holiday_page(body, year, month)
        if extracted != holiday_records[key]:
            raise SystemExit(f"RBI holiday extracted values differ from manifest: {key}")
        holiday_dates.update(row["date"] for row in extracted)
    rule_manifest = json.loads(RULE_SOURCE_MANIFEST.read_text(encoding="utf-8"))
    for record in rule_manifest.get("sources", []):
        body = (ROOT / record["path"]).read_bytes()
        if record.get("http_status") != 200 or record.get("bytes") != len(body) or record.get("sha256") != hashlib.sha256(body).hexdigest():
            raise SystemExit(f"RBI rollover rule-source integrity mismatch: {record['path']}")

    merged = {**first, **second}
    rows = sorted(merged.values(), key=lambda row: (row["issue_date"], row["auction_date"]))
    positive_rows = [row for row in rows if row.get("result_status") == "MATCHED"]
    issue_dates = [date.fromisoformat(row["issue_date"]) for row in positive_rows]
    transitions = []
    for row in rows:
        item = dict(row)
        if row.get("result_status") != "MATCHED":
            item.update({
                "nominal_91d_maturity_date": "",
                "holiday_adjusted_maturity_date": "",
                "holiday_adjustment_days": "",
                "next_positive_issue_date": "",
                "cash_wait_days_after_adjusted_maturity": "",
                "gross_price_to_par_hpr_pct": "",
                "rollover_status": "NO_91D_ISSUE",
            })
            transitions.append(item)
            continue
        price = Decimal(row["weighted_price_91"])
        if price <= 0 or not row.get("weighted_yield_91"):
            raise SystemExit(f"positive 91-day issue lacks a valid weighted average price/yield: {row['auction_date']}")
        issue = date.fromisoformat(row["issue_date"])
        nominal_maturity = issue + timedelta(days=91)
        adjusted_maturity = nominal_maturity
        while adjusted_maturity.weekday() >= 5 or adjusted_maturity.isoformat() in holiday_dates:
            adjusted_maturity -= timedelta(days=1)
        successor = next((d for d in issue_dates if d > issue and d >= adjusted_maturity), None)
        hpr_pct = (Decimal(100) / price - Decimal(1)) * Decimal(100)
        if successor is None:
            status, next_date, wait = "RIGHT_CENSORED_NO_NEXT_ISSUE_IN_WINDOW", "", ""
        else:
            wait = (successor - adjusted_maturity).days
            status = "NEXT_POSITIVE_ISSUE_ON_ADJUSTED_MATURITY" if wait == 0 else "CASH_GAP_TO_NEXT_POSITIVE_ISSUE"
            next_date = successor.isoformat()
        item.update({
            "nominal_91d_maturity_date": nominal_maturity.isoformat(),
            "holiday_adjusted_maturity_date": adjusted_maturity.isoformat(),
            "holiday_adjustment_days": str((nominal_maturity - adjusted_maturity).days),
            "next_positive_issue_date": next_date,
            "cash_wait_days_after_adjusted_maturity": str(wait),
            "gross_price_to_par_hpr_pct": format(hpr_pct, ".8f"),
            "rollover_status": status,
        })
        transitions.append(item)

    completed = [r for r in transitions if r["rollover_status"] in {"NEXT_POSITIVE_ISSUE_ON_ADJUSTED_MATURITY", "CASH_GAP_TO_NEXT_POSITIVE_ISSUE"}]
    waits = [int(r["cash_wait_days_after_adjusted_maturity"]) for r in completed]
    returns = [Decimal(r["gross_price_to_par_hpr_pct"]) for r in transitions if r["gross_price_to_par_hpr_pct"]]
    positive_by_issue = {date.fromisoformat(row["issue_date"]): row for row in transitions if row.get("gross_price_to_par_hpr_pct")}

    roll_paths = []
    for start in positive_by_issue.values():
        initial_cash = Decimal("10000")
        cash = initial_cash
        start_date = date.fromisoformat(start["issue_date"])
        target_date = start_date + timedelta(days=365)
        current = start
        purchases = 0
        while True:
            price = Decimal(current["weighted_price_91"])
            lot_cost = price * Decimal(100)
            lots = int((cash / lot_cost).to_integral_value(rounding=ROUND_FLOOR))
            if lots < 1:
                roll_paths.append({"start_issue_date": start_date.isoformat(), "target_date": target_date.isoformat(), "status": "LOT_SIZE_UNAFFORDABLE", "purchase_count": purchases})
                break
            face = Decimal(lots * 10000)
            cash -= lot_cost * lots
            purchases += 1
            maturity = date.fromisoformat(current["holiday_adjusted_maturity_date"])
            cash += face
            if maturity >= target_date:
                days = (maturity - start_date).days
                multiple = cash / initial_cash
                annualized = (math.pow(float(multiple), 365 / days) - 1) * 100
                roll_paths.append({
                    "start_issue_date": start_date.isoformat(), "target_date": target_date.isoformat(),
                    "terminal_maturity_date": maturity.isoformat(), "horizon_days": days,
                    "ending_cash_inr": format(cash, ".2f"), "gross_cumulative_return_pct": format((multiple - 1) * 100, ".8f"),
                    "gross_annualized_return_pct": format(annualized, ".8f"), "purchase_count": purchases,
                    "status": "CONDITIONAL_365D_TARGET_HELD_TO_NEXT_MATURITY",
                })
                break
            next_issue = next((d for d in positive_by_issue if d > date.fromisoformat(current["issue_date"]) and d >= maturity), None)
            if next_issue is None:
                roll_paths.append({"start_issue_date": start_date.isoformat(), "target_date": target_date.isoformat(), "status": "CENSORED_SOURCE_WINDOW", "purchase_count": purchases})
                break
            current = positive_by_issue[next_issue]

    complete_roll_paths = [row for row in roll_paths if row["status"] == "CONDITIONAL_365D_TARGET_HELD_TO_NEXT_MATURITY"]
    annualized_rolls = [Decimal(row["gross_annualized_return_pct"]) for row in complete_roll_paths]
    overlap_start, overlap_end = overlap_dates[0], overlap_dates[-1]
    summary = {
        "schema_version": 1,
        "result": "PASS_SOURCE_OVERLAP_AND_GROSS_CASHFLOW_MECHANICS__ROLLOVER_NOT_QUALIFIED",
        "window_inputs": {
            "table217_manifest": "research/stage512/2026-11-19/g6_3/rbi_tbill_window_2024_2025/manifest.json",
            "table218_manifest": "research/stage512/2026-11-06/g6_3/rbi_tbill_window_2025_2026/manifest.json",
        },
        "unique_auction_dates": len(rows),
        "positive_91_day_price_observations": len(returns),
        "overlap": {"dates": len(overlap_dates), "first": overlap_start, "last": overlap_end, "field_mismatches": len(overlap_mismatches)},
        "holiday_calendar": {
            "source_manifest": "research/stage512/2026-11-24/g6_3/rbi_mumbai_holidays_2024_2026/manifest.json",
            "rule_source_manifest": "research/stage512/2026-11-24/g6_3/source_raw/rbi_rollover_policy_sources_v1.json",
            "months": len(holiday_records),
            "listed_mumbai_holiday_dates": len(holiday_dates),
            "nominal_maturities_adjusted_backward": sum((date.fromisoformat(row["nominal_91d_maturity_date"]) - date.fromisoformat(row["holiday_adjusted_maturity_date"])).days > 0 for row in transitions if row.get("holiday_adjusted_maturity_date")),
            "maximum_backward_adjustment_days": max(((date.fromisoformat(row["nominal_91d_maturity_date"]) - date.fromisoformat(row["holiday_adjusted_maturity_date"])).days for row in transitions if row.get("holiday_adjusted_maturity_date")), default=0),
        },
        "zero_issue_dates": [r["auction_date"] for r in rows if r.get("result_status") == "ZERO_ISSUE_EXCEPTION"],
        "conditional_gross_price_to_par_holding_return_pct": {
            "minimum": format(min(returns), ".8f"),
            "mean": format(sum(returns) / Decimal(len(returns)), ".8f"),
            "maximum": format(max(returns), ".8f"),
            "definition": "100 / RBI non-competitive weighted-average price per 100 face - 1; assumes full allotment, hold to redemption at par, and excludes tax, fees, and investor-specific execution.",
        },
        "conditional_365d_target_roll_scenario": {
            "classification": "DETERMINISTIC_HISTORICAL_MECHANICS_SCENARIO_NOT_ACTUAL_INVESTOR_RETURN_OR_FORECAST",
            "initial_cash_inr": "10000.00",
            "minimum_face_lot_inr": "10000",
            "cash_during_wait_days": "0% return",
            "lot_rounding": "buy the greatest whole number of ₹10,000 face-value lots supported by cash at each observed NCB weighted-average price",
            "uses_full_allotment": True,
            "tax_and_fees_included": False,
            "same_day_maturity_and_next_issue_funding_assumed": True,
            "complete_start_cohorts": len(complete_roll_paths),
            "right_censored_start_cohorts": sum(row["status"] == "CENSORED_SOURCE_WINDOW" for row in roll_paths),
            "annualized_gross_return_minimum": format(min(annualized_rolls), ".8f") if annualized_rolls else None,
            "annualized_gross_return_median": format(statistics.median(annualized_rolls), ".8f") if annualized_rolls else None,
            "annualized_gross_return_maximum": format(max(annualized_rolls), ".8f") if annualized_rolls else None,
            "overlap_warning": "Start cohorts overlap in time and are not independent observations; these descriptive values do not estimate a long-run return distribution or probability.",
        },
        "nominal_roll_schedule_diagnostic": {
            "definition": "issue date + 91 calendar days; move maturity backward over weekends and official Mumbai holidays; then select the first observed positive 91-day issue date on or after the adjusted date.",
            "completed_successor_transitions": len(completed),
            "same_date_successors": sum(wait == 0 for wait in waits),
            "delayed_successors": sum(wait > 0 for wait in waits),
            "maximum_cash_wait_days_after_adjusted_maturity": max(waits) if waits else None,
            "right_censored_without_successor": sum(r["rollover_status"] == "RIGHT_CENSORED_NO_NEXT_ISSUE_IN_WINDOW" for r in transitions),
            "limitations": [
                "The diagnostic applies RBI's previous-working-day rule using the captured Mumbai matrix and the official rule that the Government securities market is closed on Saturdays; each security's specific maturity terms still require confirmation.",
                "The deterministic one-year-target roll scenario assumes ₹10,000 bid lots, full allotment, and that redemption proceeds can fund a same-date replacement issue; none of these prove investor-specific access or settlement.",
                "Actual investor charges, tax, partial allotment, and cash yield during any gap are not included.",
                "The two-year observed window is not a long-run interest-rate model or a 2036 probability estimate.",
            ],
        },
    }
    out_json = args.output_dir / "rbi_tbill_rollover_assumption_audit_v1.json"
    out_csv = args.output_dir / "rbi_tbill_merged_roll_schedule_v1.csv"
    rolls_csv = args.output_dir / "rbi_tbill_conditional_365d_roll_scenarios_v1.csv"
    out_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with out_csv.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(transitions[0]))
        writer.writeheader()
        writer.writerows(transitions)
    with rolls_csv.open("w", encoding="utf-8", newline="") as stream:
        fields = sorted({key for row in roll_paths for key in row})
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(roll_paths)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
