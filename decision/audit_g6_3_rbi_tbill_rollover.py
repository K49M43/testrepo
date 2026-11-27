from __future__ import annotations

import argparse
import calendar
import csv
import hashlib
import json
import math
import statistics
from collections import Counter
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
SETTLEMENT_HOLIDAY_DIR = ROOT / "research/stage512/2026-11-24/g6_3/rbi_mumbai_holidays_2024_07_2024_09"
RULE_SOURCE_MANIFEST = ROOT / "research/stage512/2026-11-24/g6_3/source_raw/rbi_rollover_policy_sources_v1.json"
RETAIL_RULES_MANIFEST = ROOT / "research/stage512/2026-11-24/g6_3/source_raw/rbi_retail_direct_rules_manifest_v1.json"


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


class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style"} and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def verify_retail_rules() -> dict:
    manifest = json.loads(RETAIL_RULES_MANIFEST.read_text(encoding="utf-8"))
    captures = {}
    for record in manifest.get("sources", []):
        body = (ROOT / record["path"]).read_bytes()
        if record.get("http_status") != 200 or record.get("bytes") != len(body) or record.get("sha256") != hashlib.sha256(body).hexdigest():
            raise SystemExit(f"RBI Retail Direct rule-source integrity mismatch: {record['path']}")
        parser = VisibleText()
        parser.feed(body.decode("utf-8", errors="replace"))
        captures[record["path"]] = " ".join(" ".join(parser.parts).split()).casefold()

    faq_path = "research/stage512/2026-11-24/g6_3/source_raw/rbi_retail_direct_faq_145.html"
    ncb_path = "research/stage512/2026-11-24/g6_3/source_raw/rbi_ncb_scheme_2021_id12193.html"
    if faq_path not in captures or ncb_path not in captures:
        raise SystemExit("RBI Retail Direct FAQ or non-competitive bidding scheme capture missing")
    faq, ncb = captures[faq_path], captures[ncb_path]
    required = {
        "retail_direct_tbill_primary_auction": "treasury bills (t-bills)" in faq and "primary auctions" in faq,
        "single_final_bid": "only one final bid per security in each primary auction" in faq,
        "funding_deadline": "bids which are not funded as on the date of submission of bids to rbi will be cancelled" in faq,
        "partial_allotment_pro_rata": "in case of partial allotment, a pro-rata allotment will be made" in faq,
        "weighted_average_price": "at the weighted average price of the successful bids in the auction" in faq,
        "settlement_typically_t_plus_one": "typically one working day after the trade date/auction date" in faq,
        "rbi_primary_bid_fee_none": "no fee will be charged by rbi at the time of submission of bids" in faq,
        "payment_gateway_charges_investor_borne": "payment gateway charges will have to be borne by the investor" in faq,
        "markup_refund_within_two_business_days": "within two business days from the date of auction" in faq,
        "minimum_bid_10000_and_multiples": "minimum amount for bidding will be ₹10,000 (face value) and thereafter in multiples in ₹10,000" in ncb,
        "aggregate_retail_ncb_cap_5_percent": "maximum of five percent of the aggregate nominal amount" in ncb,
    }
    failed = [name for name, passed in required.items() if not passed]
    if failed:
        raise SystemExit(f"RBI Retail Direct terms missing from captured official sources: {failed}")
    return {
        "source_manifest": "research/stage512/2026-11-24/g6_3/source_raw/rbi_retail_direct_rules_manifest_v1.json",
        "verified_terms": required,
        "minimum_face_value_inr": 10000,
        "minimum_rule_source_date": "2021-11-12 circular; RBI FAQ displays minimums as of 2021-11-12",
        "retail_ncb_aggregate_limit": "up to 5% of notified nominal issue amount, within notified amount, or other percentage set by RBI; not an individual guaranteed allocation",
        "partial_allotment": "pro-rata if auction allocation is partial; actual investor allocation is unknown without bid/allotment records",
        "investor_access": "RBI Retail Direct permits eligible individuals to bid in primary T-bill auctions through the non-competitive segment; this capture does not verify this investor's RDG account or operational eligibility",
        "upfront_markup_amount": "required by FAQ as part of funding basis, but amount/formula is not specified in captured FAQ; affordability is not qualified",
        "cash_costs": "RBI reports no account maintenance or primary bid fee; payment-gateway charges are borne by investor and amount is not specified",
        "settlement": "typically one working day after auction; use observed issue dates as historical settlement dates; this is not a guarantee for future auctions",
    }


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
    maturity_holiday_dates = set(holiday_dates)

    settlement_manifest = json.loads((SETTLEMENT_HOLIDAY_DIR / "manifest.json").read_text(encoding="utf-8"))
    settlement_sources = {record["path"]: record for record in settlement_manifest.get("sources", [])}
    if settlement_manifest.get("coverage") != {"first_month": "2024-07", "last_month": "2024-09", "months": 3}:
        raise SystemExit("RBI settlement holiday package does not cover July through September 2024")
    if len(settlement_sources) != 4 or len([r for r in settlement_sources.values() if r.get("method") == "POST"]) != 3:
        raise SystemExit("RBI settlement holiday package must contain one initial GET and three month POSTs")
    settlement_months = {}
    for path, record in settlement_sources.items():
        body = (SETTLEMENT_HOLIDAY_DIR / path).read_bytes()
        if record.get("http_status") != 200 or record.get("bytes") != len(body) or record.get("sha256") != hashlib.sha256(body).hexdigest():
            raise SystemExit(f"RBI settlement holiday source integrity mismatch: {path}")
        if record.get("method") != "POST":
            continue
        year, month = int(record["parameters"]["drYear"]), int(record["parameters"]["drMonth"])
        if record["parameters"].get("drRegionalOffice") != "28":
            raise SystemExit(f"RBI settlement holiday source is not the Mumbai office: {path}")
        extracted = parse_holiday_page(body, year, month)
        settlement_months[f"{year:04d}-{month:02d}"] = extracted
        holiday_dates.update(row["date"] for row in extracted)
    if sorted(settlement_months) != ["2024-07", "2024-08", "2024-09"]:
        raise SystemExit("RBI settlement holiday month coverage mismatch")

    rule_manifest = json.loads(RULE_SOURCE_MANIFEST.read_text(encoding="utf-8"))
    for record in rule_manifest.get("sources", []):
        body = (ROOT / record["path"]).read_bytes()
        if record.get("http_status") != 200 or record.get("bytes") != len(body) or record.get("sha256") != hashlib.sha256(body).hexdigest():
            raise SystemExit(f"RBI rollover rule-source integrity mismatch: {record['path']}")
    retail_rules = verify_retail_rules()

    merged = {**first, **second}
    rows = sorted(merged.values(), key=lambda row: (row["issue_date"], row["auction_date"]))
    positive_rows = [row for row in rows if row.get("result_status") == "MATCHED"]
    positive_rows = sorted(positive_rows, key=lambda row: row["auction_date"])
    positive_by_auction = {date.fromisoformat(row["auction_date"]): row for row in positive_rows}
    if len(positive_by_auction) != len(positive_rows):
        raise SystemExit("duplicate positive T-bill auction dates")

    def next_working_day(day: date) -> date:
        candidate = day + timedelta(days=1)
        while candidate.weekday() >= 5 or candidate.isoformat() in holiday_dates:
            candidate += timedelta(days=1)
        return candidate

    settlement_mismatches = []
    for row in positive_rows:
        auction_day = date.fromisoformat(row["auction_date"])
        observed_settlement = date.fromisoformat(row["issue_date"])
        expected_settlement = next_working_day(auction_day)
        if expected_settlement != observed_settlement:
            settlement_mismatches.append({"auction_date": row["auction_date"], "observed_issue_date": row["issue_date"], "next_working_day": expected_settlement.isoformat()})
    if settlement_mismatches:
        raise SystemExit(f"auction/settlement dates do not reconcile to the RBI Mumbai calendar: {settlement_mismatches[:5]}")

    transitions = []
    for row in rows:
        item = dict(row)
        if row.get("result_status") != "MATCHED":
            item.update({
                "nominal_91d_maturity_date": "",
                "holiday_adjusted_maturity_date": "",
                "holiday_adjustment_days": "",
                "next_positive_issue_date": "",
                "next_positive_auction_date": "",
                "cash_wait_days_to_next_auction_funding": "",
                "auction_to_settlement_days": "",
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
        while adjusted_maturity.weekday() >= 5 or adjusted_maturity.isoformat() in maturity_holiday_dates:
            adjusted_maturity -= timedelta(days=1)
        legacy_successor = next((candidate for candidate in positive_rows if date.fromisoformat(candidate["issue_date"]) > issue and date.fromisoformat(candidate["issue_date"]) >= adjusted_maturity), None)
        successor = next((d for d in positive_by_auction if d > adjusted_maturity), None)
        hpr_pct = (Decimal(100) / price - Decimal(1)) * Decimal(100)
        if successor is None:
            status, next_auction, next_issue, wait, settlement_lag = "RIGHT_CENSORED_NO_NEXT_ELIGIBLE_AUCTION_IN_WINDOW", "", "", "", ""
        else:
            successor_row = positive_by_auction[successor]
            wait = (successor - adjusted_maturity).days
            status = "NEXT_POSITIVE_AUCTION_AFTER_MATURITY"
            next_auction = successor.isoformat()
            next_issue = successor_row["issue_date"]
            settlement_lag = (date.fromisoformat(next_issue) - successor).days
        legacy_auction_precedes_maturity = bool(legacy_successor and date.fromisoformat(legacy_successor["auction_date"]) <= adjusted_maturity)
        item.update({
            "nominal_91d_maturity_date": nominal_maturity.isoformat(),
            "holiday_adjusted_maturity_date": adjusted_maturity.isoformat(),
            "holiday_adjustment_days": str((nominal_maturity - adjusted_maturity).days),
            "legacy_selected_issue_date": legacy_successor["issue_date"] if legacy_successor else "",
            "legacy_selected_auction_not_after_maturity": legacy_auction_precedes_maturity,
            "next_positive_auction_date": next_auction,
            "next_positive_issue_date": next_issue,
            "cash_wait_days_to_next_auction_funding": str(wait),
            "auction_to_settlement_days": str(settlement_lag),
            "gross_price_to_par_hpr_pct": format(hpr_pct, ".8f"),
            "rollover_status": status,
        })
        transitions.append(item)

    completed = [r for r in transitions if r["rollover_status"] == "NEXT_POSITIVE_AUCTION_AFTER_MATURITY"]
    waits = [int(r["cash_wait_days_to_next_auction_funding"]) for r in completed]
    returns = [Decimal(r["gross_price_to_par_hpr_pct"]) for r in transitions if r["gross_price_to_par_hpr_pct"]]
    positive_by_auction = {date.fromisoformat(row["auction_date"]): row for row in transitions if row.get("gross_price_to_par_hpr_pct")}

    roll_paths = []
    for start in positive_by_auction.values():
        initial_cash = Decimal("10000")
        cash = initial_cash
        start_date = date.fromisoformat(start["auction_date"])
        target_date = start_date + timedelta(days=365)
        current = start
        purchases = 0
        while True:
            price = Decimal(current["weighted_price_91"])
            lot_cost = price * Decimal(100)
            lots = int((cash / lot_cost).to_integral_value(rounding=ROUND_FLOOR))
            if lots < 1:
                roll_paths.append({"start_auction_date": start_date.isoformat(), "target_date": target_date.isoformat(), "status": "LOT_SIZE_UNAFFORDABLE", "purchase_count": purchases})
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
                    "start_auction_date": start_date.isoformat(), "target_date": target_date.isoformat(),
                    "terminal_maturity_date": maturity.isoformat(), "horizon_days": days,
                    "ending_cash_inr": format(cash, ".2f"), "gross_cumulative_return_pct": format((multiple - 1) * 100, ".8f"),
                    "gross_annualized_return_pct": format(annualized, ".8f"), "purchase_count": purchases,
                    "status": "CONDITIONAL_365D_TARGET_HELD_TO_NEXT_MATURITY",
                })
                break
            next_auction = next((d for d in positive_by_auction if d > maturity), None)
            if next_auction is None:
                roll_paths.append({"start_auction_date": start_date.isoformat(), "target_date": target_date.isoformat(), "status": "CENSORED_SOURCE_WINDOW", "purchase_count": purchases})
                break
            current = positive_by_auction[next_auction]

    complete_roll_paths = [row for row in roll_paths if row["status"] == "CONDITIONAL_365D_TARGET_HELD_TO_NEXT_MATURITY"]
    annualized_rolls = [Decimal(row["gross_annualized_return_pct"]) for row in complete_roll_paths]
    overlap_start, overlap_end = overlap_dates[0], overlap_dates[-1]
    summary = {
        "schema_version": 2,
        "result": "PASS_SOURCE_OVERLAP_RETAIL_RULES_AND_BID_DATE_ROLLOVER_MECHANICS__INVESTOR_ROLLOVER_NOT_QUALIFIED",
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
            "listed_mumbai_holiday_dates": len(maturity_holiday_dates),
            "nominal_maturities_adjusted_backward": sum((date.fromisoformat(row["nominal_91d_maturity_date"]) - date.fromisoformat(row["holiday_adjusted_maturity_date"])).days > 0 for row in transitions if row.get("holiday_adjusted_maturity_date")),
            "maximum_backward_adjustment_days": max(((date.fromisoformat(row["nominal_91d_maturity_date"]) - date.fromisoformat(row["holiday_adjusted_maturity_date"])).days for row in transitions if row.get("holiday_adjusted_maturity_date")), default=0),
        },
        "settlement_calendar": {
            "extended_source_manifest": "research/stage512/2026-11-24/g6_3/rbi_mumbai_holidays_2024_07_2024_09/manifest.json",
            "months_added_for_initial_auctions": len(settlement_months),
            "additional_mumbai_holiday_dates": len(holiday_dates - maturity_holiday_dates),
            "historical_positive_auction_settlements_checked": len(positive_rows),
            "auction_to_next_mumbai_working_day_mismatches": len(settlement_mismatches),
            "observed_settlement_calendar_day_lags": dict(sorted(Counter((date.fromisoformat(row["issue_date"]) - date.fromisoformat(row["auction_date"])).days for row in positive_rows).items())),
            "basis": "Observed RBI auction dates and issue/settlement dates reconciled against weekends plus captured official Mumbai holidays; not a future settlement guarantee.",
        },
        "retail_direct_rules": retail_rules,
        "zero_issue_dates": [r["auction_date"] for r in rows if r.get("result_status") == "ZERO_ISSUE_EXCEPTION"],
        "conditional_gross_price_to_par_holding_return_pct": {
            "minimum": format(min(returns), ".8f"),
            "mean": format(sum(returns) / Decimal(len(returns)), ".8f"),
            "maximum": format(max(returns), ".8f"),
            "definition": "100 / RBI non-competitive weighted-average price per 100 face - 1; assumes full allotment, hold to redemption at par, and excludes tax, fees, and investor-specific execution.",
        },
        "conditional_365d_target_roll_scenario": {
            "classification": "DETERMINISTIC_HISTORICAL_BID_DATE_AND_CASH_GAP_SCENARIO_NOT_ACTUAL_INVESTOR_RETURN_OR_FORECAST",
            "initial_cash_inr": "10000.00",
            "minimum_face_lot_inr": "10000",
            "cash_during_wait_days": "0% return",
            "lot_rounding": "buy the greatest whole number of ₹10,000 face-value lots supported by cash at each observed NCB weighted-average price; upfront markup and payment-gateway charges are excluded, so bid affordability is not established",
            "uses_full_allotment": True,
            "tax_and_fees_included": False,
            "same_day_maturity_and_next_auction_funding_assumed": False,
            "next_bid_date_rule": "first observed positive 91-day auction date strictly after adjusted maturity; same-day funding is excluded because RBI requires funding on the bid-submission date and intraday maturity-credit timing is not established",
            "cash_wait_return_assumption": "0% between maturity receipt and next eligible auction; no return is credited while auction funds are reserved or excess markup is awaiting refund",
            "upfront_markup_and_refund_timing": "RBI FAQ requires markup-funded bids and says excess is refunded within two business days; the markup amount is unspecified and not modeled",
            "complete_start_cohorts": len(complete_roll_paths),
            "right_censored_start_cohorts": sum(row["status"] == "CENSORED_SOURCE_WINDOW" for row in roll_paths),
            "annualized_gross_return_minimum": format(min(annualized_rolls), ".8f") if annualized_rolls else None,
            "annualized_gross_return_median": format(statistics.median(annualized_rolls), ".8f") if annualized_rolls else None,
            "annualized_gross_return_maximum": format(max(annualized_rolls), ".8f") if annualized_rolls else None,
            "overlap_warning": "Start cohorts overlap in time and are not independent observations; these descriptive values do not estimate a long-run return distribution or probability.",
        },
        "nominal_roll_schedule_diagnostic": {
            "definition": "Issue date + 91 calendar days; move maturity backward over weekends and official Mumbai holidays; then select the first positive auction date strictly after adjusted maturity because retail funding is required on the auction/bid date.",
            "completed_successor_transitions": len(completed),
            "legacy_selected_auction_not_after_maturity_count": sum(bool(r.get("legacy_selected_auction_not_after_maturity")) for r in transitions),
            "same_day_auction_funding_used": sum(wait == 0 for wait in waits),
            "minimum_cash_wait_days_to_next_bid": min(waits) if waits else None,
            "maximum_cash_wait_days_to_next_bid": max(waits) if waits else None,
            "median_cash_wait_days_to_next_bid": statistics.median(waits) if waits else None,
            "right_censored_without_successor": sum(r["rollover_status"] == "RIGHT_CENSORED_NO_NEXT_ELIGIBLE_AUCTION_IN_WINDOW" for r in transitions),
            "limitations": [
                "The diagnostic applies RBI's previous-working-day rule using the captured Mumbai matrix and the official rule that the Government securities market is closed on Saturdays; each security's specific maturity terms still require confirmation.",
                "The deterministic one-year-target roll scenario uses the public ₹10,000 minimum lot and historical auction dates, assumes full allotment, and excludes required upfront markup; it does not prove investor-specific access or bid affordability.",
                "The bid-date rule conservatively excludes an auction on the same date as maturity because the exact order of maturity credit and bid-funding cutoff is not established by public evidence.",
                "Actual partial allocation, payment-gateway charges, markup amount/refund cash timing, tax, and any bank cash yield are not modeled.",
                "The two-year observed window is not a long-run interest-rate model or a 2036 probability estimate.",
            ],
        },
    }
    out_json = args.output_dir / "rbi_tbill_rollover_assumption_audit_v2.json"
    out_csv = args.output_dir / "rbi_tbill_merged_roll_schedule_v2.csv"
    rolls_csv = args.output_dir / "rbi_tbill_conditional_365d_roll_scenarios_v2.csv"
    retail_json = args.output_dir / "rbi_tbill_retail_route_qualification_v1.json"
    out_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    retail_json.write_text(json.dumps(retail_rules, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
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
