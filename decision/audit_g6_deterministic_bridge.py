"""Independent fixture contract and arithmetic audit for G6.1."""

from __future__ import annotations

import copy
import hashlib
import json
from calendar import monthrange
from datetime import date
from decimal import Decimal, ROUND_DOWN, localcontext
from pathlib import Path
from typing import Any

from after_tax_event_ledger import tax_year_for
from g3_goal_hurdle import DEFAULT_SCHEDULE_PATH, read_schedule, validate_schedule_contract, CONTRACT_PATH
from g6_deterministic_bridge import (
    DEFAULT_FIXTURE,
    DEFAULT_OUTPUT,
    FIXTURE_LABEL,
    _validate_fixture,
    load_fixture,
    run_fixture,
    run_scenario,
)


ROOT = Path(__file__).resolve().parents[1]
AUDIT_OUTPUT = ROOT / "research/stage512/2026-11-05/g6_1/audit.json"
D = Decimal
TOL = D("0.000000000001")


def independent_section516_round(value: Decimal) -> Decimal:
    """Independent TY fixture implementation of section 516 rounding."""
    whole_rupees = value.to_integral_value(rounding=ROUND_DOWN)
    lower_ten = (whole_rupees // D("10")) * D("10")
    return lower_ten + (D("10") if whole_rupees - lower_ten >= D("5") else D("0"))


def independent_ordinary_tax_before_credits(income: Decimal) -> Decimal:
    """Fixture-only independent slab/cess calculation for ordinary income.

    The fixture deliberately stays above the rebate threshold and below the
    surcharge threshold, with no dividend or special-rate income. Values
    outside that envelope fail closed instead of falling back to the shared
    statutory calculator.
    """
    rounded_income = independent_section516_round(income)
    if not D("1200000") < rounded_income <= D("5000000"):
        raise ValueError("independent G6.1 tax check only supports ordinary income above rebate and at/below surcharge thresholds")
    slabs = (
        (D("400000"), D("0")), (D("800000"), D("0.05")),
        (D("1200000"), D("0.10")), (D("1600000"), D("0.15")),
        (D("2000000"), D("0.20")), (D("2400000"), D("0.25")),
        (None, D("0.30")),
    )
    tax = D("0")
    lower = D("0")
    for upper, rate in slabs:
        end = rounded_income if upper is None else min(rounded_income, upper)
        if end > lower:
            tax += (end - lower) * rate
        if upper is None or rounded_income <= upper:
            break
        lower = upper
    return tax * D("1.04")


def independent_expected(raw: dict, scenario: dict) -> dict[str, Any]:
    """Recalculate quantities/wealth from schedule rows without the adapter."""
    with localcontext() as ctx:
        ctx.prec = 50
        schedule = read_schedule(DEFAULT_SCHEDULE_PATH)
        contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        validate_schedule_contract(schedule, contract)
        n = raw["terminal_month_index"]
        fee = D(raw["costs"]["account_fee_per_contribution_inr"])
        exit_fee = D(raw["costs"]["terminal_transaction_cost_inr"])
        marks = [D(value) for value in scenario["price_by_month_inr"]]
        total_contributions = schedule.initial_inr
        deployed_basis = schedule.initial_inr - fee
        units = deployed_basis / marks[0]
        for month in range(1, n + 1):
            contribution = schedule.monthly_contributions[month]
            total_contributions += contribution
            principal = contribution - fee
            deployed_basis += principal
            units += principal / marks[month]
        proceeds = units * marks[n]
        gross_after_costs = proceeds - exit_fee
        taxable_gain = proceeds - deployed_basis
        if taxable_gain < ZERO:
            raise ValueError("independent fixture calculation does not qualify loss relief")
        external = D(raw["tax_assumptions"]["external_ordinary_income_inr"])
        external_tax = independent_ordinary_tax_before_credits(external)
        combined_tax = independent_ordinary_tax_before_credits(external + taxable_gain)
        incremental_tax = combined_tax - external_tax
        net_nominal = gross_after_costs - incremental_tax
        cpi_factor = D(raw["cpi"]["terminal_index"]) / D(raw["cpi"]["base_index"])
        real_value = net_nominal / cpi_factor
        fees = fee * D(n + 1) + exit_fee
        base_year, base_month_number = (int(item) for item in schedule.base_month.split("-"))
        expected_lots = []
        for month in range(n + 1):
            absolute_month = base_year * 12 + base_month_number - 1 + month
            year, month0 = divmod(absolute_month, 12)
            acquired = date(year, month0 + 1, monthrange(year, month0 + 1)[1])
            contribution = schedule.initial_inr if month == 0 else schedule.monthly_contributions[month]
            principal = contribution - fee
            lot_id = f"{scenario['scenario_id']}-lot-{month:03d}"
            lot_units = principal / marks[month]
            lot_proceeds = lot_units * marks[n]
            lot_gain = lot_proceeds - principal
            expected_lots.append({
                "event_id": (f"{scenario['scenario_id']}-terminal-sale" if month == n
                             else f"{scenario['scenario_id']}-terminal-sale-{lot_id}"),
                "lot_id": lot_id,
                "acquired_date": acquired.isoformat(),
                "disposed_date": _month_end_for_index(schedule.base_month, n).isoformat(),
                "units_disposed": str(lot_units),
                "unit_price_inr": str(marks[n]),
                "proceeds_inr": str(lot_proceeds),
                "tax_basis_removed_inr": str(principal),
                "deductible_transfer_expenses_inr": "0",
                "signed_realized_result_inr": str(lot_gain),
            })
        return {
            "contributions_inr": str(total_contributions),
            "deployed_basis_inr": str(deployed_basis),
            "units_at_exit": str(units),
            "gross_sale_proceeds_inr": str(proceeds),
            "recorded_costs_inr": str(fees),
            "gross_terminal_after_costs_before_tax_inr": str(gross_after_costs),
            "taxable_gain_inr": str(taxable_gain),
            "external_tax_before_credits_inr": str(external_tax),
            "combined_tax_before_credits_inr": str(combined_tax),
            "incremental_fixture_tax_inr": str(incremental_tax),
            "net_nominal_inr": str(net_nominal),
            "lot_disposal_trace": expected_lots,
            "cpi_factor": str(cpi_factor),
            "net_real_inr": str(real_value),
        }


ZERO = D("0")


def _month_end_for_index(base_month: str, index: int) -> date:
    year, month = (int(item) for item in base_month.split("-"))
    absolute = year * 12 + month - 1 + index
    result_year, month0 = divmod(absolute, 12)
    result_month = month0 + 1
    return date(result_year, result_month, monthrange(result_year, result_month)[1])


def audit() -> dict:
    raw = load_fixture()
    schedule, _, terminal, year = _validate_fixture(raw)
    assert schedule.base_month == raw["cpi"]["base_month"] == "2026-10"
    assert terminal.isoformat() == "2027-03-31"
    assert year == tax_year_for(terminal) == "2026-27"
    assert raw["input_classification"] == FIXTURE_LABEL
    assert raw["tax_assumptions"]["resident_individual"] is True

    actual = run_fixture()
    assert len(actual["scenarios"]) == 2
    if not DEFAULT_OUTPUT.exists():
        raise AssertionError("bridge output was not written by the run step")
    committed_output = json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8"))
    assert committed_output == actual

    formula_results = {}
    for row, scenario in zip(actual["scenarios"], raw["scenarios"], strict=True):
        independent = independent_expected(raw, scenario)
        formula_results[row["scenario_id"]] = independent
        mappings = {
            "contributions_inr": "contributions_inr",
            "gross_terminal_sale_proceeds_before_terminal_cost_and_tax_inr": "gross_sale_proceeds_inr",
            "gross_terminal_wealth_after_recorded_costs_before_tax_inr": "gross_terminal_after_costs_before_tax_inr",
            "incremental_fixture_tax_inr": "incremental_fixture_tax_inr",
            "net_nominal_after_costs_and_incremental_fixture_tax_inr": "net_nominal_inr",
            "net_real_2026_base_fixture_value_inr": "net_real_inr",
        }
        for output_key, expected_key in mappings.items():
            assert abs(D(row[output_key]) - D(independent[expected_key])) <= TOL, (row["scenario_id"], output_key)
        year_tax = row["tax_year_trace"][row["tax_year"]]
        assert abs(D(year_tax["external_only_tax_before_credits"]) - D(independent["external_tax_before_credits_inr"])) <= TOL
        assert abs(D(year_tax["total_tax_before_credits"]) - D(independent["combined_tax_before_credits_inr"])) <= TOL
        assert abs(D(year_tax["incremental_portfolio_tax"]) - D(independent["incremental_fixture_tax_inr"])) <= TOL
        assert D(row["reconciliation_residual_inr"]) == ZERO
        assert row["event_count"] == 24
        actual_lots = {entry["lot_id"]: entry for entry in row["lot_disposal_trace"]}
        expected_lots = {entry["lot_id"]: entry for entry in independent["lot_disposal_trace"]}
        assert len(actual_lots) == len(expected_lots) == raw["terminal_month_index"] + 1
        assert set(actual_lots) == set(expected_lots)
        lot_numeric_fields = (
            "units_disposed", "unit_price_inr", "proceeds_inr", "tax_basis_removed_inr",
            "deductible_transfer_expenses_inr", "signed_realized_result_inr",
        )
        for lot_id, expected_lot in expected_lots.items():
            actual_lot = actual_lots[lot_id]
            assert actual_lot["event_id"] == expected_lot["event_id"]
            assert actual_lot["acquired_date"] == expected_lot["acquired_date"]
            assert actual_lot["disposed_date"] == expected_lot["disposed_date"]
            for field in lot_numeric_fields:
                assert abs(D(actual_lot[field]) - D(expected_lot[field])) <= TOL, (row["scenario_id"], lot_id, field)
        taxable_lots = {
            entry["lot_id"]: entry for entry in independent["lot_disposal_trace"]
            if D(entry["signed_realized_result_inr"]) > ZERO
        }
        taxable_trace = {
            entry["lot_id"]: entry for entry in row["tax_event_trace"]
            if "realized_disposal" in entry
        }
        assert set(taxable_trace) == set(taxable_lots)
        for lot_id, expected_lot in taxable_lots.items():
            trace = taxable_trace[lot_id]
            assert trace["tax_category"] == "ordinary"
            assert trace["tax_classification"] == "section76"
            assert abs(D(trace["taxable_amount_inr"]) - D(expected_lot["signed_realized_result_inr"])) <= TOL
            disposal = trace["realized_disposal"]
            assert abs(D(disposal["proceeds_inr"]) - D(expected_lot["proceeds_inr"])) <= TOL
            assert abs(D(disposal["tax_basis_removed_inr"]) - D(expected_lot["tax_basis_removed_inr"])) <= TOL
        assert row["investment_authorization"] == "NO_GO"
        assert "probability" not in row
    assert D(actual["scenarios"][0]["incremental_fixture_tax_inr"]) == ZERO
    assert D(actual["scenarios"][1]["incremental_fixture_tax_inr"]) > ZERO
    assert D(actual["scenarios"][1]["net_nominal_after_costs_and_incremental_fixture_tax_inr"]) > \
           D(actual["scenarios"][0]["net_nominal_after_costs_and_incremental_fixture_tax_inr"])

    failures = {}
    mutations = []
    bad_actual = copy.deepcopy(raw)
    bad_actual["input_classification"] = "ACTUAL_MARKET_DATA"
    mutations.append(("actual_input_rejected", bad_actual, "load"))
    bad_price_source = copy.deepcopy(raw)
    bad_price_source["price_path_basis"] = "Official AMFI NAV observations"
    mutations.append(("non_synthetic_price_basis_rejected", bad_price_source, "load"))
    bad_marks = copy.deepcopy(raw)
    bad_marks["scenarios"][0]["price_by_month_inr"].pop()
    mutations.append(("incomplete_price_path_rejected", bad_marks, "validate"))
    bad_cpi = copy.deepcopy(raw)
    bad_cpi["cpi"]["terminal_index"] = "0"
    mutations.append(("zero_cpi_rejected", bad_cpi, "validate"))
    bad_tax = copy.deepcopy(raw)
    del bad_tax["tax_assumptions"]["external_ordinary_income_inr"]
    mutations.append(("missing_external_tax_input_rejected", bad_tax, "validate"))
    missing_residency = copy.deepcopy(raw)
    del missing_residency["tax_assumptions"]["resident_individual"]
    mutations.append(("missing_synthetic_residency_rejected", missing_residency, "validate"))
    nonresident = copy.deepcopy(raw)
    nonresident["tax_assumptions"]["resident_individual"] = False
    mutations.append(("unsupported_nonresident_assumption_rejected", nonresident, "validate"))
    cross_year = copy.deepcopy(raw)
    cross_year["terminal_month_index"] = 6
    cross_year["cpi"]["terminal_month"] = "2027-04"
    cross_year["cpi"]["terminal_index"] = "103"
    for key, mutation, stage in mutations:
        try:
            if stage == "load":
                from g6_deterministic_bridge import load_fixture_text
                load_fixture_text(json.dumps(mutation))
            else:
                _validate_fixture(mutation)
        except (ValueError, KeyError):
            failures[key] = "PASS"
        else:
            raise AssertionError(f"mutation unexpectedly passed: {key}")
    try:
        _validate_fixture(cross_year)
    except ValueError:
        failures["cross_tax_year_rejected"] = "PASS"
    else:
        raise AssertionError("cross-tax-year path unexpectedly passed")

    downside = copy.deepcopy(raw["scenarios"][0])
    downside["scenario_id"] = "downside-loss-mutation"
    downside["price_by_month_inr"] = ["100", "98", "96", "94", "92", "90"]
    try:
        run_scenario(raw, downside)
    except ValueError as error:
        assert "realized losses require" in str(error)
        failures["unallocated_loss_blocks_result"] = "PASS"
    else:
        raise AssertionError("unallocated realized loss unexpectedly produced a tax/real result")

    report = {
        "audit": "PASS",
        "record_id": "g6-1-independent-bridge-audit-v1",
        "scope": "one synthetic instrument; one tax year; two deterministic paths; no market or investor-specific data",
        "independent_tax_check_scope": "independent section 516 rounding, ordinary slab, and cess arithmetic within the fixture's explicit resident-only, >rebate-threshold, <=surcharge-threshold envelope; not an independent tax-law opinion",
        "scenario_count": len(actual["scenarios"]),
        "independent_formula_reconciliation": "PASS",
        "independent_tax_slab_and_cess_reconciliation": "PASS",
        "complete_per_lot_disposal_and_tax_trace_reconciliation": "PASS",
        "zero_cash_ledger_residuals": all(D(row["reconciliation_residual_inr"]) == ZERO for row in actual["scenarios"]),
        "mutation_cases": failures,
        "tax_year": year,
        "terminal_date": terminal.isoformat(),
        "decision_grade_g6": "NOT_READY",
        "investment_authorization": "NO_GO",
        "audit_code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "result_sha256": hashlib.sha256(DEFAULT_OUTPUT.read_bytes()).hexdigest(),
        "independent_formula_results": formula_results,
    }
    AUDIT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return report


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, ensure_ascii=False))
