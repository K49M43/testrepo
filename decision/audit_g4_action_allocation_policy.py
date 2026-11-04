"""Validate the G4.1 action-policy input contract without third-party runtime dependencies."""

from __future__ import annotations

import copy
import hashlib
import json
import re
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "config" / "g4_action_allocation_policy_v1.json"
SCHEMA_PATH = ROOT / "config" / "g4_action_allocation_policy.schema.v1.json"
STATUS_VALUES = {
    "INVESTOR_CONFIRMED",
    "MANDATE_DERIVED",
    "ANALYST_PROPOSED",
    "UNRESOLVED",
    "DEPENDENCY_BLOCKED",
}
VALUE_STATUSES = {"INVESTOR_CONFIRMED", "MANDATE_DERIVED", "ANALYST_PROPOSED"}
NULL_STATUSES = {"UNRESOLVED", "DEPENDENCY_BLOCKED"}
EXPECTED_UNITS = {
    "capital.initial_corpus.amount": "INR",
    "capital.reserve.amount": "INR",
    "capital.initial_corpus.date": "calendar_date",
    "contributions.starting_monthly_amount": "INR_per_month",
    "contributions.step_up_fraction": "fraction",
    "contributions.step_up_interval": "contributions",
    "contributions.timing_convention": "payment_timing",
    "contributions.first_payment_date": "calendar_date",
    "goals.planning_floor.amount": "INR_2026_purchasing_power",
    "goals.stretch_goal.amount": "INR_2026_purchasing_power",
    "goals.success_and_shortfall_event": "outcome_definition",
    "inflation.purchasing_power_anchor_date": "calendar_date",
    "horizon.terminal_measurement_date": "calendar_date",
    "risk.interim_drawdown_tolerance": "fraction_of_peak_portfolio_value",
    "implementation.account_and_product_constraints": "constraint_record",
    "implementation.broker_route": "broker_name",
    "income_and_coupon_handling": "distribution_policy",
    "policy.initial_deployment_rule": "deployment_policy",
    "policy.allocation_schedule": "fraction_of_deployable_capital",
    "policy.rebalancing_rule": "rebalancing_policy",
    "policy.terminal_measurement_contract": "exit_policy",
    "policy.investor_exit_choice": "exit_policy",
}
REQUIRED_FIELD_IDS = set(EXPECTED_UNITS)
REQUIRED_DIMENSIONS = {
    "capital_and_reserve",
    "initial_deployment",
    "dated_contributions_and_stepups",
    "asset_allocation_by_date",
    "implementation_and_cash_rounding",
    "rebalance_or_hold_rule",
    "income_and_coupon_reinvestment",
    "liquidity_and_availability_constraints",
    "terminal_measurement_and_exit",
    "cost_and_tax_treatment_reference",
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(value, dict), f"{path.name} root must be a JSON object")
    return value


def _check_hash_reference(reference: dict[str, Any], label: str) -> None:
    relative = reference.get("path")
    expected = reference.get("sha256")
    _require(isinstance(relative, str) and relative, f"{label} reference path is required")
    _require(bool(re.fullmatch(r"[0-9a-f]{64}", str(expected))), f"{label} SHA-256 must be 64 lowercase hex characters")
    resolved = (ROOT / relative).resolve()
    _require(resolved.is_relative_to(ROOT), f"{label} path escapes the repository")
    _require(resolved.is_file(), f"{label} reference file is missing: {relative}")
    actual = hashlib.sha256(resolved.read_bytes()).hexdigest()
    _require(actual == expected, f"{label} source hash is stale: {relative}")


def _validate_typed_value(field: dict[str, Any]) -> None:
    value = field["value"]
    field_type = field["data_type"]
    if field_type == "decimal_string":
        _require(isinstance(value, str) and bool(re.fullmatch(r"-?\d+(?:\.\d+)?", value)),
                 f"{field['field_id']} must be a finite decimal string")
        try:
            _require(Decimal(value).is_finite(), f"{field['field_id']} must be finite")
        except InvalidOperation as error:
            raise ValueError(f"{field['field_id']} is not a valid decimal") from error
    elif field_type == "positive_integer":
        _require(isinstance(value, int) and not isinstance(value, bool) and value > 0,
                 f"{field['field_id']} must be a positive integer")
    elif field_type == "iso_date":
        _require(isinstance(value, str), f"{field['field_id']} must be an ISO calendar date")
        parsed = date.fromisoformat(value)
        _require(parsed.isoformat() == value, f"{field['field_id']} must use YYYY-MM-DD")
    elif field_type == "enum":
        allowed = field.get("allowed_values")
        _require(isinstance(allowed, list) and allowed and all(isinstance(item, str) for item in allowed),
                 f"{field['field_id']} must declare allowed enum values")
        _require(isinstance(value, str) and value in allowed,
                 f"{field['field_id']} value must be one of {allowed}")
    elif field_type == "string":
        _require(isinstance(value, str) and value.strip(), f"{field['field_id']} must be a non-empty string")
    elif field_type == "object":
        _require(isinstance(value, dict), f"{field['field_id']} must be an object")
    else:
        raise ValueError(f"Unsupported data type for {field['field_id']}: {field_type}")


def validate_contract(contract: dict[str, Any], *, check_sources: bool = False) -> None:
    _require(contract.get("contract_id") == "g4-action-allocation-policy", "wrong contract_id")
    _require(contract.get("contract_version") == "1.0.0", "unexpected contract version")
    _require(contract.get("contract_status") in {"DRAFT", "ACCEPTED"}, "invalid contract_status")
    _require(contract.get("investment_authorization") == "NO_GO", "G4.1 must fail closed to NO_GO")
    _require(contract.get("as_of") == "2026-11-04", "as_of must be explicitly reviewed when the contract changes")

    definitions = contract.get("field_status_definitions", {})
    _require(set(definitions) == STATUS_VALUES, "status definitions must cover every permitted status exactly")
    fields = contract.get("field_register")
    _require(isinstance(fields, list), "field_register must be an array")
    indexed: dict[str, dict[str, Any]] = {}
    for field in fields:
        _require(isinstance(field, dict), "each field_register item must be an object")
        field_id = field.get("field_id")
        _require(isinstance(field_id, str) and field_id not in indexed, f"duplicate or invalid field_id: {field_id}")
        indexed[field_id] = field
        _require(field_id in EXPECTED_UNITS, f"unrecognized policy field: {field_id}")
        _require(field.get("unit") == EXPECTED_UNITS[field_id], f"wrong unit for {field_id}")
        status = field.get("status")
        _require(status in STATUS_VALUES, f"invalid provenance status for {field_id}")
        _require(isinstance(field.get("source_ref"), str) and field["source_ref"].strip(),
                 f"source_ref is required for {field_id}")
        _require(isinstance(field.get("investor_confirmation_required"), bool),
                 f"investor_confirmation_required must be boolean for {field_id}")
        _require(isinstance(field.get("decision_effect"), str) and field["decision_effect"].strip(),
                 f"decision_effect is required for {field_id}")
        _require(field.get("as_of") == "2026-11-04" or status == "MANDATE_DERIVED",
                 f"as_of must be refreshed for non-mandate input {field_id}")

        if status in NULL_STATUSES:
            _require(field.get("value") is None, f"{status} field {field_id} must have null value")
            _require(field.get("must_not_infer") is True, f"{status} field {field_id} must set must_not_infer=true")
            if status == "UNRESOLVED":
                _require(field["investor_confirmation_required"] is True,
                         f"unresolved field {field_id} must require investor confirmation")
            else:
                _require(isinstance(field.get("dependency_issue"), int),
                         f"blocked field {field_id} must identify its dependency issue")
        else:
            _require(field.get("value") is not None, f"{status} field {field_id} cannot be null")
            _validate_typed_value(field)

    _require(set(indexed) == REQUIRED_FIELD_IDS, "field_register must contain the exact required policy inputs")
    _require(indexed["capital.reserve.amount"]["status"] == "UNRESOLVED",
             "the mandate specifies no separate reserve; do not assume zero or invent a reserve")
    _require(indexed["risk.interim_drawdown_tolerance"]["status"] == "UNRESOLVED",
             "drawdown tolerance must remain unresolved until investor confirmation")
    _require(indexed["contributions.timing_convention"]["status"] == "ANALYST_PROPOSED",
             "end-of-month fixture timing is not investor-confirmed")
    _require(indexed["goals.planning_floor.amount"]["value"] == "9000000",
             "the ₹90 lakh planning floor must be preserved")
    _require(indexed["goals.stretch_goal.amount"]["value"] == "10000000",
             "the ₹1 crore stretch goal must remain separate")

    dimensions = contract.get("required_policy_dimensions")
    _require(isinstance(dimensions, list) and set(dimensions) == REQUIRED_DIMENSIONS,
             "required_policy_dimensions must cover the full action policy surface")
    case_set = contract.get("policy_case_set", {})
    _require(case_set.get("status") == "NOT_STARTED_G4_2" and case_set.get("cases") == [],
             "G4.1 must not silently add candidate allocation policies")
    limits = case_set.get("case_limit", {})
    _require(limits.get("minimum_investable_research_cases") == 3, "G4.2 minimum case count drifted")
    _require(limits.get("maximum_investable_research_cases") == 5, "G4.2 maximum case count drifted")
    _require(limits.get("optimizer_allowed") is False, "G4.1 must not authorize an optimizer")

    upstream = contract.get("upstream_contracts", {})
    g3 = upstream.get("g3_outcome_contract", {})
    _require(g3.get("status") == "PENDING_MERGE_AND_EXACT_HEAD_VERIFICATION" and g3.get("sha256") is None,
             "G3 must not be represented as accepted before merge and exact-head verification")
    g2 = upstream.get("g2_database_run_contract", {})
    _require(g2.get("status") == "PENDING_SPRINT_2_ACCEPTANCE" and g2.get("path") is None,
             "G2 database schema must not be invented or treated as accepted")

    for label in ("known_limitations", "invalidation_triggers"):
        _require(isinstance(contract.get(label), list) and contract[label], f"{label} must be explicit")

    if check_sources:
        _check_hash_reference(contract["mandate_reference"], "mandate")
        _check_hash_reference(upstream["cashflow_fixture"], "cashflow fixture")


def _expect_rejected(candidate: dict[str, Any], label: str) -> None:
    try:
        validate_contract(candidate)
    except (ValueError, TypeError, KeyError):
        return
    raise AssertionError(f"negative case unexpectedly passed: {label}")


def audit() -> dict[str, Any]:
    schema = _load_json(SCHEMA_PATH)
    contract = _load_json(CONTRACT_PATH)
    _require(schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema",
             "contract schema must declare JSON Schema 2020-12")
    Draft202012Validator.check_schema(schema)
    schema_errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(contract))
    _require(not schema_errors, f"contract does not satisfy JSON Schema: {schema_errors[0].message if schema_errors else ''}")
    validate_contract(contract, check_sources=True)

    negative_cases = 0
    bad = copy.deepcopy(contract)
    next(field for field in bad["field_register"] if field["field_id"] == "capital.reserve.amount")["status"] = "MANDATE_DERIVED"
    _expect_rejected(bad, "unresolved reserve promoted without a value")
    negative_cases += 1

    bad = copy.deepcopy(contract)
    next(field for field in bad["field_register"] if field["field_id"] == "capital.initial_corpus.amount")["unit"] = "USD"
    _expect_rejected(bad, "wrong currency unit")
    negative_cases += 1

    bad = copy.deepcopy(contract)
    field = next(field for field in bad["field_register"] if field["field_id"] == "capital.initial_corpus.date")
    field.update({"value": "2026-13-50", "status": "ANALYST_PROPOSED", "investor_confirmation_required": True})
    _expect_rejected(bad, "malformed calendar date")
    negative_cases += 1

    bad = copy.deepcopy(contract)
    field = next(field for field in bad["field_register"] if field["field_id"] == "contributions.timing_convention")
    field["value"] = "END_OF_YEAR"
    _expect_rejected(bad, "invalid enum value")
    negative_cases += 1

    bad = copy.deepcopy(contract)
    bad["field_register"][0]["status"] = "TRUST_ME"
    _expect_rejected(bad, "invalid provenance status")
    negative_cases += 1

    bad = copy.deepcopy(contract)
    bad["upstream_contracts"]["g3_outcome_contract"].update({
        "status": "ACCEPTED", "sha256": "0" * 64
    })
    _expect_rejected(bad, "unverified G3 contract marked accepted")
    negative_cases += 1

    return {
        "audit": "PASS",
        "contract": "g4-action-allocation-policy 1.0.0",
        "status": contract["contract_status"],
        "registered_fields": len(contract["field_register"]),
        "required_policy_dimensions": len(contract["required_policy_dimensions"]),
        "negative_cases_rejected": negative_cases,
        "json_schema_2020_12": "PASS; schema validates and validates the contract instance",
        "source_hashes": "PASS; mandate and frozen cashflow fixture match pinned SHA-256",
        "unresolved_investor_inputs_preserved": "PASS; reserve, dates, exit, product limits, and drawdown tolerance are not imputed",
        "g2_g3_dependencies": "PASS; pending contracts remain blocked pending acceptance",
        "investment_authorization": contract["investment_authorization"],
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, ensure_ascii=False))
