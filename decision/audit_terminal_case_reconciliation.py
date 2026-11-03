"""Independent schedule, lot, tax-year, and hand-calculation audit for Increment 4."""

from __future__ import annotations

import argparse
import csv
import json
from decimal import Decimal
from pathlib import Path
from typing import Any

from terminal_case_reconciliation import reconcile
from ty2026_27_tax_components import section516_round_rupees


D = Decimal
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "research/stage512/2026-11-03/terminal_case_reconciliation.json"


def independent_schedule_totals() -> dict[int, str]:
    path = ROOT / "research/stage512/2026-11-02/cashflow_hurdle_monthly_2026-10_base.csv"
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    values: dict[int, str] = {}
    for horizon in (120, 122):
        applicable = [row for row in rows if int(row["month_index"]) <= horizon]
        independently_summed = sum(
            (D(row["initial_investment_inr"]) + D(row["monthly_contribution_inr"]) for row in applicable), D("0")
        )
        recorded_cumulative = D(applicable[-1]["cumulative_contributions_inr"])
        assert independently_summed == recorded_cumulative
        assert len(applicable) == horizon + 1
        values[horizon] = str(independently_summed)
    return values


def audit() -> dict[str, Any]:
    payload = reconcile()
    contributions = independent_schedule_totals()
    by_key = {(case["horizon_months"], case["case"]): case for case in payload["cases"]}
    tolerance = D("0.000000000001")
    for horizon in (120, 122):
        for case_name in ("fund_one_year_liquidation", "fund_staged_liquidation", "direct_bond_coupon_and_maturity"):
            case = by_key[(horizon, case_name)]
            assert case["ledger_status"] == "PASS"
            assert abs(D(case["cash_contributions_inr"]) - D(contributions[horizon])) <= tolerance
            assert abs(D(case["reconciliation_residual_inr"])) <= tolerance
            assert D(case["gross_terminal_wealth_inr"]) - D(case["remaining_incremental_tax_after_withholding_inr"]) == D(case["net_accessible_fixture_wealth_inr"])
            assert D(case["transaction_costs_inr"]) == 0
            assert D(case["other_fees_inr"]) == 0

    # Independent representative-lot hand check: the original ₹42 lakh
    # synthetic direct bond earns ₹2.1 lakh annual coupon; at ₹30 lakh other
    # ordinary income the fixture's 30% marginal slab plus 4% cess is 31.2%.
    rep_coupon = D("4200000") * D("0.05")
    rep_incremental_tax = rep_coupon * D("0.30") * D("1.04")
    assert rep_coupon == D("210000")
    assert rep_incremental_tax == D("65520")

    # Independent full-tax-year check for all direct-bond coupon years. Every
    # synthetic year's total remains under ₹50 lakh including ₹30 lakh salary,
    # so ordinary coupon tax is exactly coupon × 30% × 1.04 under this fixture.
    full_year_checks = {}
    for horizon in (120, 122):
        bond = by_key[(horizon, "direct_bond_coupon_and_maturity")]
        for year, details in bond["tax_years"].items():
            coupon_income = D(details["portfolio_income"]["ordinary"])
            external_income = D("3000000")
            assert external_income + coupon_income < D("5000000")
            statutory_coupon_base = section516_round_rupees(coupon_income)
            manual_tax = statutory_coupon_base * D("0.30") * D("1.04")
            engine_tax = D(details["incremental_portfolio_tax"])
            assert abs(engine_tax - manual_tax) <= tolerance
            full_year_checks[f"{horizon}:{year}"] = {
                "coupon_income_inr": str(coupon_income),
                "section516_rounded_coupon_base_inr": str(statutory_coupon_base),
                "hand_calculated_incremental_tax_inr": str(manual_tax),
                "engine_incremental_tax_inr": str(engine_tax),
            }

    assert payload["authorization"] == "NO-GO"
    payload["independent_acceptance"] = {
        "status": "PASS",
        "schedule_contributions_inr": {str(key): value for key, value in contributions.items()},
        "representative_lot_hand_calculation": {
            "principal_inr": "4200000", "annual_coupon_rate": "0.05", "coupon_inr": str(rep_coupon),
            "other_ordinary_income_inr": "3000000", "marginal_tax_plus_cess_rate": "0.312",
            "incremental_tax_inr": str(rep_incremental_tax),
        },
        "full_tax_year_coupon_checks": full_year_checks,
        "checks": [
            "independent sum of 120/122 schedule rows equals recorded baseline cumulative contributions",
            "fund single-year and staged exits reconcile all lots and tax years",
            "direct-bond coupons are gross ordinary income and maturity returns principal at par",
            "gross terminal value less fees and incremental tax equals net fixture wealth",
            "representative lot and every full bond coupon tax year match independent marginal-rate arithmetic",
            "no CPI-adjusted or investor-specific result is produced",
        ],
    }
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the committed artifact differs from this rerun")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    rendered = json.dumps(audit(), indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"FAIL: committed output differs from reproducible audit: {args.output}")
        print(f"PASS: terminal cases and committed artifact match: {args.output}")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
        print(json.dumps({"audit": "PASS", "output": str(args.output),
                          "case_count": 6, "schedule_totals_inr": independent_schedule_totals(),
                          "authorization": "NO-GO"}, indent=2))


if __name__ == "__main__":
    main()
