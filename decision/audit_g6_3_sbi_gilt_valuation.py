"""Challenge SBI's reported bond yield and rerun both after-tax accounting cases."""
from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timedelta
from decimal import localcontext
from itertools import product
from pathlib import Path

from audit_g6_3_direct_gsec_2036 import load_json, require, verify_hash
from audit_g6_3_sbi_gilt_holdings import (
    INPUT as OCTOBER_SNAPSHOT, OUTPUT as FROZEN_HOLDINGS, accrued_days, build as build_holdings,
)
from compare_g6_3_gilt_routes import D, ONE, ROOT, rounded, years
from g3_goal_hurdle import normalized_text_and_sha256


EVIDENCE = ROOT / "research/g6_3/direct_gsec_2036/2026-11-27-sbi-valuation"
INPUT = EVIDENCE / "inputs_v1.json"
OUTPUT = EVIDENCE / "valuation_audit_v1.json"


def check_source_sheet(source, path):
    from openpyxl import load_workbook

    verify_hash(path, source["bytes"], source["sha256"])
    workbook = load_workbook(path, read_only=True, data_only=True)
    try:
        sheet = workbook[source["sheet"]]
        for cell, expected in source["cells"].items():
            value = sheet[cell].value
            if isinstance(value, datetime):
                value = value.date().isoformat()
            require(str(value) == expected, f"{source['sheet']} cell {cell} differs")
    finally:
        workbook.close()


def valuation_cases(cells, nominal_dates, coupon):
    as_of = date.fromisoformat(cells["D4"])
    quantity = D(cells["F24"])
    report_yield = D(cells["I24"]) / 100
    market_value = D(cells["G24"])
    mark = market_value * 100_000 / quantity
    half_rounding_tick = D("0.005") * 100_000 / quantity
    require(sum(D(cells[key]) for key in ("G24", "G53", "G58")) == D(cells["G61"]),
            "reported NAV components do not reconcile")

    last_coupon = date(as_of.year, 5, 23)
    maturity = nominal_dates[-1]
    cases = []
    for shift, fraction, style in product((0, 1), ("actual365", "30e360"), ("effective", "nominal_semiannual")):
        trial = as_of + timedelta(days=shift)
        require(last_coupon < trial < nominal_dates[0], "unexpected coupon period")
        rate = report_yield if style == "effective" else (ONE + report_yield / 2) ** 2 - ONE
        accrued = coupon * accrued_days(last_coupon, trial) / 180
        pv = sum((coupon + (100 if dt == maturity else 0)) / (ONE + rate) ** (
            years(trial, dt) if fraction == "actual365" else D(accrued_days(trial, dt)) / 360)
            for dt in nominal_dates)
        dirty_gap = mark - pv
        clean_gap = mark + accrued - pv
        cases.append({
            "trial_valuation_date": trial.isoformat(), "discount_day_count": fraction, "yield_style": style,
            "accrued_30e360_per_100_inr": rounded(accrued, "0.00000000"),
            "implied_dirty_pv_per_100_inr": rounded(pv, "0.00000000"),
            "implied_clean_pv_per_100_inr": rounded(pv - accrued, "0.00000000"),
            "reported_minus_model_dirty_per_100_inr": rounded(dirty_gap, "0.00000000"),
            "reported_minus_model_clean_per_100_inr": rounded(clean_gap, "0.00000000"),
            "clean_gap_in_lakh_at_reported_quantity": rounded(clean_gap * quantity / 100_000, "0.000001"),
            "clean_fits_amount_rounding": abs(clean_gap) <= half_rounding_tick,
            "dirty_fits_amount_rounding": abs(dirty_gap) <= half_rounding_tick,
        })
    return {
        "as_of": as_of.isoformat(), "reported_mark_per_100_inr": rounded(mark, "0.00000000"),
        "reported_holding_yield_percent": cells["I24"],
        "half_market_value_rounding_tick_per_100_inr": rounded(half_rounding_tick, "0.00000000"),
        "cases": cases,
    }


def after_tax_ranges(rows):
    grouped = {}
    for row in rows:
        key = (row["ter_percent"], row["reinvest_percent"], row["market_value_basis"])
        grouped.setdefault(key, []).append(row)
    require(len(rows) == 40 and len(grouped) == 20, "unexpected after-tax sensitivity coverage")
    ranges = []
    for (ter, rate, basis), scenarios in sorted(grouped.items()):
        require({row["residual_earns_reinvestment_rate"] for row in scenarios} == {True, False},
                "missing residual asset sensitivity")
        result = {"ter_percent": ter, "gross_reinvestment_percent": rate, "market_value_basis": basis}
        for field in ("fund_after_cost_and_tax_inr", "fund_minus_fixed_4pct_direct_after_tax_inr",
                      "fund_minus_same_rate_direct_after_tax_inr"):
            values = [D(row[field]) for row in scenarios]
            result[field] = [rounded(min(values)), rounded(max(values))]
        if rate == "4.00":
            require(result["fund_minus_fixed_4pct_direct_after_tax_inr"] ==
                    result["fund_minus_same_rate_direct_after_tax_inr"], "common 4% direct cases disagree")
        ranges.append(result)
    return ranges


def build(sources):
    snapshot = load_json(OCTOBER_SNAPSHOT)
    september = sources["september_holdings"]["cells"]
    halfyear = sources["september_financial_results"]["cells"]
    october = snapshot["portfolio"]["cells"]
    require(september["D24"] == october["D24"] == snapshot["bond_terms"]["isin"], "holdings are for different bonds")
    require(rounded(D(halfyear["AU16"]) * 100) == september["G61"]
            and halfyear["AV27"] == september["E83"] and halfyear["AV55"] == "0.28",
            "September portfolio, NAV or TER corroboration failed")
    holdings = build_holdings(snapshot)
    require(holdings == load_json(FROZEN_HOLDINGS), "base holdings replay differs from frozen output")
    nominal_dates = [date.fromisoformat(dt) for dt in holdings["nominal_coupon_dates"]]
    coupon = D(snapshot["bond_terms"]["coupon_annual_percent"]) / 2
    valuations = [valuation_cases(cells, nominal_dates, coupon) for cells in (september, october)]
    for valuation in valuations:
        trial = next(row for row in valuation["cases"] if row["trial_valuation_date"] > valuation["as_of"]
                     and row["discount_day_count"] == "30e360" and row["yield_style"] == "effective")
        require(abs(D(trial["reported_minus_model_clean_per_100_inr"])) < D("0.001")
                and not any(row["dirty_fits_amount_rounding"] for row in valuation["cases"]),
                "dated evidence no longer supports the clean-mark hypothesis")

    return {
        "record_id": sources["record_id"],
        "accounting_evidence": "CLEAN_MARK_WITH_SEPARATE_ACCRUAL_BETTER_SUPPORTED_OCTOBER_LEDGER_UNVERIFIED",
        "holding_yield_basis": "ANNUAL_EFFECTIVE_30E360_STRONGLY_INDICATED_CUTOFF_UNVERIFIED",
        "october_cashflows": "BOTH_ACCOUNTING_CASES_RETAINED",
        "input_sha256_normalized": normalized_text_and_sha256(INPUT)[1],
        "base_holdings_sha256_normalized": normalized_text_and_sha256(FROZEN_HOLDINGS)[1],
        "code_sha256_normalized": normalized_text_and_sha256(Path(__file__))[1],
        "pricing_diagnostics": valuations,
        "after_tax_comparison": {
            "start": holdings["start"], "end": holdings["end"], "budget_inr": "100000",
            "scenario_count": len(holdings["scenarios"]),
            "matched_date_fixed_4pct_direct_after_tax_inr": holdings["matched_31_oct_direct_fixed_4pct_post_tax_inr"],
            "ranges": after_tax_ranges(holdings["scenarios"]),
        },
        **{key: holdings[key] for key in ("live_quote", "paid_silver_history", "rbi_tbill_payment_timing",
                                         "investment_authorization")},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--september-holdings", type=Path)
    parser.add_argument("--september-financials", type=Path)
    args = parser.parse_args()
    sources = load_json(INPUT)
    for path, key in ((args.september_holdings, "september_holdings"),
                      (args.september_financials, "september_financial_results")):
        if path:
            check_source_sheet(sources[key], path.resolve())
    with localcontext() as ctx:
        ctx.prec = 45
        result = build(sources)
    payload = json.dumps(result, indent=2) + "\n"
    if args.check:
        require(OUTPUT.read_text(encoding="utf-8") == payload, "valuation replay differs from retained output")
    else:
        OUTPUT.write_text(payload, encoding="utf-8", newline="\n")
    print("PASS: 16 holding price and yield diagnostics, 40 after-tax cases. Accounting cutoff unverified. NO_GO.")


if __name__ == "__main__":
    main()
