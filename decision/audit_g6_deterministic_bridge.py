"""Independent fixture contract and arithmetic audit for G6.1."""

from __future__ import annotations

import copy
import hashlib
import json
from decimal import Decimal, localcontext
from pathlib import Path

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
from ty2026_27_tax_components import TaxInput, calculate_tax


ROOT = Path(__file__).resolve().parents[1]
AUDIT_OUTPUT = ROOT / "research/stage512/2026-11-05/g6_1/audit.json"
D = Decimal
TOL = D("0.000000000001")


def independent_expected(raw: dict, scenario: dict) -> dict[str, str]:
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
        external_tax = calculate_tax(TaxInput(ordinary_income=external)).tax_before_credits
        combined_tax = calculate_tax(TaxInput(ordinary_income=external + taxable_gain)).tax_before_credits
        incremental_tax = combined_tax - external_tax
        net_nominal = gross_after_costs - incremental_tax
        cpi_factor = D(raw["cpi"]["terminal_index"]) / D(raw["cpi"]["base_index"])
        real_value = net_nominal / cpi_factor
        fees = fee * D(n + 1) + exit_fee
        return {
            "contributions_inr": str(total_contributions),
            "deployed_basis_inr": str(deployed_basis),
            "units_at_exit": str(units),
            "gross_sale_proceeds_inr": str(proceeds),
            "recorded_costs_inr": str(fees),
            "gross_terminal_after_costs_before_tax_inr": str(gross_after_costs),
            "taxable_gain_inr": str(taxable_gain),
            "incremental_fixture_tax_inr": str(incremental_tax),
            "net_nominal_inr": str(net_nominal),
            "cpi_factor": str(cpi_factor),
            "net_real_inr": str(real_value),
        }


ZERO = D("0")


def audit() -> dict:
    raw = load_fixture()
    schedule, _, terminal, year = _validate_fixture(raw)
    assert schedule.base_month == raw["cpi"]["base_month"] == "2026-10"
    assert terminal.isoformat() == "2027-03-31"
    assert year == tax_year_for(terminal) == "2026-27"
    assert raw["input_classification"] == FIXTURE_LABEL

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
        assert D(row["reconciliation_residual_inr"]) == ZERO
        assert row["event_count"] == 24
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
        "scope": "one synthetic instrument; one tax year; two deterministic paths; no market or personal data",
        "scenario_count": len(actual["scenarios"]),
        "independent_formula_reconciliation": "PASS",
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
    AUDIT_OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, ensure_ascii=False))
