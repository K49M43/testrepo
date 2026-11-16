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
YIELD_PATH = EVIDENCE / "auction_yield_reconciliation_v1.json"


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


def xirr_actual_365(cashflows: list[tuple[float, date]]) -> float:
    """Solve annual-effective XIRR using actual calendar days divided by 365."""
    origin = cashflows[0][1]

    def npv(rate: float) -> float:
        return sum(
            amount / (1.0 + rate) ** ((when - origin).days / 365.0)
            for amount, when in cashflows
        )

    low, high = -0.99, 1.0
    require(npv(low) > 0.0 and npv(high) < 0.0, "XIRR root is not bracketed in [-99%, 100%]")
    for _ in range(200):
        middle = (low + high) / 2.0
        if npv(middle) > 0.0:
            low = middle
        else:
            high = middle
    return (low + high) / 2.0


def main() -> None:
    manifest = load_json(MANIFEST_PATH)
    pair = load_json(PAIR_PATH)
    daycount = load_json(DAYCOUNT_PATH)
    cashflows = load_json(CASHFLOW_PATH)
    yield_record = load_json(YIELD_PATH)

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

    # Independent cashflow-yield reconciliation. The initial dirty consideration
    # remains conditional because retail settlement rounding is not qualified.
    dirty = Decimal(settlement["dirty_consideration_per_100_face_value"])
    initial = -float(dirty)
    yield_cashflows = [(initial, date.fromisoformat(cashflows["modeled_acquisition_date"]))]
    for event in events:
        amount = Decimal(event["coupon_per_100_face_inr"]) + Decimal(event["redemption_per_100_face_inr"])
        yield_cashflows.append((float(amount), date.fromisoformat(event["nominal_coupon_date"])))
    xirr = xirr_actual_365(yield_cashflows)
    quoted_nominal = Decimal(str(pair["auction_result_values"]["competitive_weighted_average_yield_percent"])) / Decimal(100)
    quoted_effective = (Decimal(1) + quoted_nominal / Decimal(2)) ** 2 - Decimal(1)
    difference_bps = (Decimal(str(xirr)) - quoted_effective) * Decimal(10000)
    gross_receipts = sum(Decimal(str(amount)) for amount, _ in yield_cashflows[1:])
    gross_excess = gross_receipts - dirty
    min_lot_units = Decimal(settlement["minimum_face_value_inr"]) / Decimal(100)

    close(yield_record["inputs"]["initial_dirty_consideration_per_100"], dirty, Decimal("1e-25"), "yield input dirty consideration")
    close(yield_record["results"]["actual_365_xirr_effective_percent"], Decimal(str(xirr * 100)), Decimal("1e-10"), "actual/365 XIRR")
    close(yield_record["results"]["quoted_yield_semiannual_effective_percent"], quoted_effective * Decimal(100), Decimal("1e-20"), "effective auction yield")
    close(yield_record["results"]["difference_actual_365_xirr_minus_quoted_effective_bps"], difference_bps, Decimal("1e-9"), "yield convention difference")
    close(yield_record["results"]["gross_nominal_receipts_per_100_face"], gross_receipts, Decimal("1e-20"), "nominal coupon and redemption receipts")
    close(yield_record["results"]["gross_receipts_less_conditional_dirty_consideration_per_100_face"], gross_excess, Decimal("1e-20"), "nominal receipts less conditional outlay")
    require(abs(difference_bps) < Decimal("0.5"), "cashflow XIRR differs from converted auction yield by 0.5 bp or more")
    close(yield_record["results"]["minimum_lot_dirty_consideration_inr"], dirty * min_lot_units, Decimal("1e-20"), "minimum-lot dirty consideration")
    close(yield_record["results"]["minimum_lot_nominal_receipts_inr"], gross_receipts * min_lot_units, Decimal("1e-18"), "minimum-lot nominal receipts")
    require(yield_record["qualification"] == "ARITHMETIC_CROSSCHECK_ONLY_CONDITIONAL_INPUTS", "yield result must remain conditional and non-decision-grade")
    print("PASS: conditional nominal cashflow XIRR reconciles to auction yield within 0.5 bp")
    print("LIMIT: no market-price history, exact settlement rounding, reinvestment, tax, or investor-specific return qualified")


if __name__ == "__main__":
    main()
