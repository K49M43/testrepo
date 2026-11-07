"""Deterministically verify retained 6.94% GS 2036 source and arithmetic artifacts."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "research/g6_3/direct_gsec_2036/2026-10-16"
MANIFEST_PATH = EVIDENCE / "source_manifest.json"
PAIR_PATH = EVIDENCE / "auction_pair_reconciliation_v1.json"
DAYCOUNT_PATH = EVIDENCE / "day_count_reconciliation_v1.json"
CASHFLOW_PATH = EVIDENCE / "nominal_cashflows_v1.json"


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read valid JSON from {path.relative_to(ROOT)}: {exc}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def verify_hash(path: Path, expected_bytes: int, expected_sha256: str) -> None:
    data = path.read_bytes()
    require(len(data) == expected_bytes, f"byte length mismatch: {path.relative_to(ROOT)}")
    actual = hashlib.sha256(data).hexdigest().upper()
    require(actual == expected_sha256.upper(), f"SHA-256 mismatch: {path.relative_to(ROOT)}")


def date_30_360(start: date, end: date) -> int:
    """30/360 count for the dates used here (neither endpoint is month-end)."""
    start_day = min(start.day, 30)
    end_day = min(end.day, 30) if start_day == 30 else end.day
    return 360 * (end.year - start.year) + 30 * (end.month - start.month) + end_day - start_day


def close(actual: str | Decimal, expected: Decimal, tolerance: Decimal, label: str) -> None:
    value = Decimal(str(actual))
    require(abs(value - expected) <= tolerance, f"{label} mismatch: got {value}, expected {expected}")


def main() -> None:
    manifest = load_json(MANIFEST_PATH)
    pair = load_json(PAIR_PATH)
    daycount = load_json(DAYCOUNT_PATH)
    cashflows = load_json(CASHFLOW_PATH)

    result_path = EVIDENCE / manifest["preserved_file"]
    verify_hash(result_path, manifest["byte_length"], manifest["sha256"])
    notification = manifest["specific_notification_source"]
    notification_path = EVIDENCE / notification["retained_file"]
    verify_hash(notification_path, notification["byte_length"], notification["sha256"])
    print("PASS: retained RBI result and Gazette notification byte counts and SHA-256")

    terms = notification["security_terms"]
    require(terms["instrument"] == "6.94% GS 2036", "notification instrument mismatch")
    require(terms["isin"] == "IN0020260025", "notification ISIN mismatch")
    require(terms["auction_date"] == "2026-10-16", "auction date mismatch")
    require(terms["settlement_date"] == "2026-10-19", "settlement date mismatch")
    require(terms["accrued_interest_due_through"] == "2026-10-18", "notification accrual cutoff mismatch")
    require(pair["instrument_match"]["notification_result_amounts_reconcile"] is True, "notice/result amounts do not reconcile")
    require(pair["auction_result_values"]["competitive_weighted_average_clean_price_per_100"] == "96.93", "auction weighted-average clean price mismatch")
    require(pair["noncompetitive_settlement_arithmetic"]["rounding_and_collection_practice_at_settlement_verified"] is False, "rounding status must remain unqualified")
    print("PASS: security identity, auction/settlement dates, and notice/result alignment")

    start = date.fromisoformat(daycount["accrual_start_last_coupon_date"])
    end = date.fromisoformat(daycount["specific_notification_accrued_interest_due_through"])
    days = date_30_360(start, end)
    calc = daycount["calculations"]
    require(days == 157, f"30/360 day count mismatch: got {days}")
    require(calc["auction_notice_30_360_day_count_to_accrued_interest_due_date"] == days, "recorded day count mismatch")

    settlement = pair["noncompetitive_settlement_arithmetic"]
    rate = Decimal("6.94")
    accrued = rate * Decimal(days) / Decimal(360)
    clean = Decimal(settlement["clean_price_per_100_face_value"])
    lot_units = Decimal(settlement["minimum_face_value_inr"]) / Decimal(100)
    dirty = clean + accrued
    tolerance = Decimal("1e-25")
    close(calc["auction_notice_30_360_accrued_interest_per_100_inr"], accrued, tolerance, "day-count accrued interest")
    close(settlement["accrued_interest_per_100_face_value"], accrued, tolerance, "settlement accrued interest")
    close(settlement["dirty_consideration_per_100_face_value"], dirty, tolerance, "dirty price per 100")
    close(settlement["accrued_interest_per_minimum_lot_inr"], accrued * lot_units, tolerance, "minimum-lot accrued interest")
    close(settlement["dirty_consideration_per_minimum_lot_inr"], dirty * lot_units, tolerance, "minimum-lot dirty amount")
    require(settlement["classification"] == "CONDITIONAL_30_360_SENSITIVITY_NOT_QUALIFIED_SETTLEMENT_AMOUNT", "settlement must remain conditional")
    print("PASS: conditional 30/360 accrued-interest and clean-plus-accrued arithmetic")

    events = cashflows["coupon_events"]
    require(len(events) == 20, f"expected 20 nominal cashflow events, found {len(events)}")
    require(cashflows["isin"] == terms["isin"], "cashflow ISIN mismatch")
    require(cashflows["modeled_acquisition_date"] == terms["settlement_date"], "cashflow acquisition date mismatch")
    expected_date = date(2026, 11, 11)
    for index, event in enumerate(events, start=1):
        event_date = date.fromisoformat(event["nominal_coupon_date"])
        require(event["sequence"] == index, f"cashflow sequence mismatch at {index}")
        require(event_date == expected_date, f"nominal coupon date mismatch at sequence {index}")
        require(event["weekday"] == event_date.strftime("%A"), f"weekday label mismatch at sequence {index}")
        require(Decimal(event["coupon_per_100_face_inr"]) == Decimal("3.47"), f"coupon mismatch at sequence {index}")
        final = index == len(events)
        require(event["maturity_coupon_and_redemption"] is final, f"maturity marker mismatch at sequence {index}")
        expected_principal = Decimal("100.00") if final else Decimal("0.00")
        require(Decimal(event["redemption_per_100_face_inr"]) == expected_principal, f"principal mismatch at sequence {index}")
        year = expected_date.year + (1 if expected_date.month == 11 else 0)
        month = 5 if expected_date.month == 11 else 11
        expected_date = date(year, month, 11)
    require(events[-1]["nominal_coupon_date"] == "2036-05-11", "final maturity date mismatch")
    print("PASS: 20-event nominal coupon/redemption schedule and calendar labels")
    print("LIMIT: no market-price history, exact settlement rounding, reinvestment, tax, or investor-specific return qualified")


if __name__ == "__main__":
    main()
