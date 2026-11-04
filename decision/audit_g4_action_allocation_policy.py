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
EXPECTED_TYPES = {
    "capital.initial_corpus.amount": "decimal_string",
    "capital.reserve.amount": "decimal_string",
    "capital.initial_corpus.date": "iso_date",
    "contributions.starting_monthly_amount": "decimal_string",
    "contributions.step_up_fraction": "decimal_string",
    "contributions.step_up_interval": "positive_integer",
    "contributions.timing_convention": "enum",
    "contributions.first_payment_date": "iso_date",
    "goals.planning_floor.amount": "decimal_string",
    "goals.stretch_goal.amount": "decimal_string",
    "goals.success_and_shortfall_event": "string",
    "inflation.purchasing_power_anchor_date": "iso_date",
    "horizon.terminal_measurement_date": "iso_date",
    "risk.interim_drawdown_tolerance": "decimal_string",
    "implementation.account_and_product_constraints": "string",
    "implementation.broker_route": "string",
    "income_and_coupon_handling": "enum",
    "policy.initial_deployment_rule": "enum",
    "policy.allocation_schedule": "object",
    "policy.rebalancing_rule": "string",
    "policy.terminal_measurement_contract": "string",
    "policy.investor_exit_choice": "string",
}
EXPECTED_SOURCES = {
    "capital.initial_corpus.amount": "config/investment_mandate_2036.json#/cashflows/initial_lump_sum_inr",
    "capital.reserve.amount": "config/investment_mandate_2036.json#/cashflows/initial_lump_sum_inr",
    "capital.initial_corpus.date": "config/investment_mandate_2036.json#/cashflows/actual_initial_investment_date",
    "contributions.starting_monthly_amount": "config/investment_mandate_2036.json#/cashflows/starting_monthly_contribution_inr",
    "contributions.step_up_fraction": "config/investment_mandate_2036.json#/cashflows/annual_sip_step_up_fraction",
    "contributions.step_up_interval": "config/investment_mandate_2036.json#/cashflows/months_between_step_ups",
    "contributions.timing_convention": "config/investment_mandate_2036.json#/cashflows/modeled_contribution_timing",
    "contributions.first_payment_date": "config/investment_mandate_2036.json#/cashflows/actual_first_contribution_date",
    "goals.planning_floor.amount": "config/investment_mandate_2036.json#/goals/real_after_tax_floor_inr",
    "goals.stretch_goal.amount": "config/investment_mandate_2036.json#/goals/real_after_tax_stretch_inr",
    "goals.success_and_shortfall_event": "research/stage512/2026-11-04/g3_outcome_contract_v1.json",
    "inflation.purchasing_power_anchor_date": "config/investment_mandate_2036.json#/goals/purchasing_power_base_specific_date",
    "horizon.terminal_measurement_date": "config/investment_mandate_2036.json#/goals/target_measurement_dates_in_2036",
    "risk.interim_drawdown_tolerance": "config/investment_mandate_2036.json#/modeling/require_investment_drawdown_tolerance_confirmation",
    "implementation.account_and_product_constraints": "config/investment_mandate_2036.json#/unknowns_for_final_signoff",
    "implementation.broker_route": "config/investment_mandate_2036.json#/investor/broker",
    "income_and_coupon_handling": "docs/INVESTMENT_DECISION_MANDATE_2036.md",
    "policy.initial_deployment_rule": "GitHub issue #22 (G4.2 bounded action set)",
    "policy.allocation_schedule": "GitHub issue #22 (G4.2 bounded action set)",
    "policy.rebalancing_rule": "GitHub issue #22 (G4.2 bounded action set)",
    "policy.terminal_measurement_contract": "research/stage512/2026-11-04/g3_outcome_contract_v1.json",
    "policy.investor_exit_choice": "config/investment_mandate_2036.json#/goals/target_measurement_dates_in_2036",
}
EXPECTED_STATUSES = {
    "capital.initial_corpus.amount": "MANDATE_DERIVED",
    "capital.reserve.amount": "UNRESOLVED",
    "capital.initial_corpus.date": "UNRESOLVED",
    "contributions.starting_monthly_amount": "MANDATE_DERIVED",
    "contributions.step_up_fraction": "MANDATE_DERIVED",
    "contributions.step_up_interval": "MANDATE_DERIVED",
    "contributions.timing_convention": "ANALYST_PROPOSED",
    "contributions.first_payment_date": "UNRESOLVED",
    "goals.planning_floor.amount": "MANDATE_DERIVED",
    "goals.stretch_goal.amount": "MANDATE_DERIVED",
    "goals.success_and_shortfall_event": "DEPENDENCY_BLOCKED",
    "inflation.purchasing_power_anchor_date": "UNRESOLVED",
    "horizon.terminal_measurement_date": "UNRESOLVED",
    "risk.interim_drawdown_tolerance": "UNRESOLVED",
    "implementation.account_and_product_constraints": "UNRESOLVED",
    "implementation.broker_route": "MANDATE_DERIVED",
    "income_and_coupon_handling": "ANALYST_PROPOSED",
    "policy.initial_deployment_rule": "DEPENDENCY_BLOCKED",
    "policy.allocation_schedule": "DEPENDENCY_BLOCKED",
    "policy.rebalancing_rule": "DEPENDENCY_BLOCKED",
    "policy.terminal_measurement_contract": "DEPENDENCY_BLOCKED",
    "policy.investor_exit_choice": "UNRESOLVED",
}
EXPECTED_CONFIRMATION = {
    "MANDATE_DERIVED": False,
    "ANALYST_PROPOSED": True,
    "UNRESOLVED": True,
    "DEPENDENCY_BLOCKED": False,
}
DECIMAL_RANGES = {
    "capital.initial_corpus.amount": (Decimal("0"), None),
    "capital.reserve.amount": (Decimal("0"), None),
    "contributions.starting_monthly_amount": (Decimal("0"), None),
    "contributions.step_up_fraction": (Decimal("0"), Decimal("1")),
    "goals.planning_floor.amount": (Decimal("0"), None),
    "goals.stretch_goal.amount": (Decimal("0"), None),
    "risk.interim_drawdown_tolerance": (Decimal("0"), Decimal("1")),
}
STRICTLY_POSITIVE_DECIMALS = {
    "capital.initial_corpus.amount",
    "contributions.starting_monthly_amount",
    "goals.planning_floor.amount",
    "goals.stretch_goal.amount",
}
MANDATE_DERIVED_POINTERS = {
    "capital.initial_corpus.amount": ("cashflows", "initial_lump_sum_inr"),
    "contributions.starting_monthly_amount": ("cashflows", "starting_monthly_contribution_inr"),
    "contributions.step_up_fraction": ("cashflows", "annual_sip_step_up_fraction"),
    "contributions.step_up_interval": ("cashflows", "months_between_step_ups"),
    "goals.planning_floor.amount": ("goals", "real_after_tax_floor_inr"),
    "goals.stretch_goal.amount": ("goals", "real_after_tax_stretch_inr"),
    "implementation.broker_route": ("investor", "broker"),
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


def _portable_text_sha256(raw: bytes) -> str:
    """Hash tracked UTF-8 text consistently across LF and CRLF checkouts."""
    text = raw.decode("utf-8")
    canonical = text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _contract_fingerprint(contract: dict[str, Any]) -> str:
    payload = {key: value for key, value in contract.items() if key != "content_sha256"}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _refresh_contract_fingerprint(contract: dict[str, Any]) -> None:
    contract["content_sha256"] = _contract_fingerprint(contract)


def _check_hash_reference(reference: dict[str, Any], label: str) -> None:
    relative = reference.get("path")
    expected = reference.get("sha256")
    _require(isinstance(relative, str) and relative, f"{label} reference path is required")
    _require(bool(re.fullmatch(r"[0-9a-f]{64}", str(expected))), f"{label} SHA-256 must be 64 lowercase hex characters")
    resolved = (ROOT / relative).resolve()
    _require(resolved.is_relative_to(ROOT), f"{label} path escapes the repository")
    _require(resolved.is_file(), f"{label} reference file is missing: {relative}")
    _require(resolved.suffix.lower() in {".json", ".csv", ".md", ".py", ".yml", ".yaml"},
             f"{label} reference is not a supported tracked-text format")
    actual = _portable_text_sha256(resolved.read_bytes())
    _require(actual == expected, f"{label} normalized UTF-8/LF SHA-256 is stale: {relative}")


def _validate_typed_value(field: dict[str, Any]) -> None:
    value = field["value"]
    field_type = field["data_type"]
    if field_type == "decimal_string":
        _require(isinstance(value, str) and bool(re.fullmatch(r"-?\d+(?:\.\d+)?", value)),
                 f"{field['field_id']} must be a finite decimal string")
        try:
            number = Decimal(value)
            _require(number.is_finite(), f"{field['field_id']} must be finite")
        except InvalidOperation as error:
            raise ValueError(f"{field['field_id']} is not a valid decimal") from error
        lower, upper = DECIMAL_RANGES[field["field_id"]]
        lower_ok = number > lower if field["field_id"] in STRICTLY_POSITIVE_DECIMALS else number >= lower
        _require(lower_ok and (upper is None or number <= upper),
                 f"{field['field_id']} is outside its permitted numeric range")
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


def _resolve_json_pointer(document: Any, pointer: tuple[str, ...]) -> Any:
    current = document
    for token in pointer:
        token = token.replace("~1", "/").replace("~0", "~")
        _require(isinstance(current, dict) and token in current,
                 f"mandate source pointer does not resolve: {pointer}")
        current = current[token]
    return current


def _check_mandate_derived_values(contract: dict[str, Any]) -> None:
    mandate = _load_json(ROOT / "config" / "investment_mandate_2036.json")
    for field in contract["field_register"]:
        field_id = field["field_id"]
        if field["status"] != "MANDATE_DERIVED":
            continue
        _require(field_id in MANDATE_DERIVED_POINTERS,
                 f"no approved mandate source mapping for {field_id}")
        source_value = _resolve_json_pointer(mandate, MANDATE_DERIVED_POINTERS[field_id])
        if field["data_type"] == "decimal_string":
            matches = Decimal(str(source_value)) == Decimal(field["value"])
        else:
            matches = source_value == field["value"]
        _require(matches, f"{field_id} value differs from its pinned mandate source")


def _validate_field_semantics(field: dict[str, Any]) -> None:
    field_id = field["field_id"]
    _require(field["data_type"] == EXPECTED_TYPES[field_id],
             f"wrong data_type for {field_id}; expected {EXPECTED_TYPES[field_id]}")
    _require(field["source_ref"] == EXPECTED_SOURCES[field_id],
             f"unsupported source_ref for {field_id}")
    _require(field["status"] == EXPECTED_STATUSES[field_id],
             f"unexpected provenance status for {field_id}; requires explicit contract review")
    _require(field["investor_confirmation_required"] == EXPECTED_CONFIRMATION[field["status"]],
             f"incorrect investor confirmation flag for {field_id}")


def validate_contract(contract: dict[str, Any], *, check_sources: bool = False) -> None:
    _require(contract.get("contract_id") == "g4-action-allocation-policy", "wrong contract_id")
    _require(contract.get("contract_version") == "1.0.0", "unexpected contract version")
    _require(contract.get("content_sha256") == _contract_fingerprint(contract),
             "contract content_sha256 is stale; refresh identity after any contract change")
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
        _validate_field_semantics(field)
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
    _require(limits.get("required_control") == "ZERO_RETURN_ARITHMETIC_CONTROL",
             "G4.2 must retain its mandatory zero-return arithmetic control")
    _require(limits.get("minimum_investable_research_cases") <= limits.get("maximum_investable_research_cases"),
             "G4.2 case-count limits are inconsistent")
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
        _check_mandate_derived_values(contract)


def _expect_rejected(candidate: dict[str, Any], label: str, *, check_sources: bool = False,
                     refresh_fingerprint: bool = True) -> None:
    if refresh_fingerprint:
        _refresh_contract_fingerprint(candidate)
    try:
        validate_contract(candidate, check_sources=check_sources)
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
    bad["content_sha256"] = "0" * 64
    _expect_rejected(bad, "stale contract identity", refresh_fingerprint=False)
    negative_cases += 1

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

    bad = copy.deepcopy(contract)
    field = next(field for field in bad["field_register"] if field["field_id"] == "capital.initial_corpus.amount")
    field.update({"data_type": "string", "value": "banana", "status": "INVESTOR_CONFIRMED",
                  "as_of": "2026-11-04", "investor_confirmation_required": True})
    _expect_rejected(bad, "field type and status cannot be relabeled to bypass validation")
    negative_cases += 1

    bad = copy.deepcopy(contract)
    field = next(field for field in bad["field_register"] if field["field_id"] == "capital.initial_corpus.amount")
    field["source_ref"] = "unsupported source"
    _expect_rejected(bad, "unsupported provenance source")
    negative_cases += 1

    bad = copy.deepcopy(contract)
    field = next(field for field in bad["field_register"] if field["field_id"] == "capital.initial_corpus.amount")
    field["value"] = "9999999"
    _expect_rejected(bad, "mandate-derived value conflicts with cited source", check_sources=True)
    negative_cases += 1

    bad = copy.deepcopy(contract)
    field = next(field for field in bad["field_register"] if field["field_id"] == "contributions.step_up_fraction")
    field["value"] = "2"
    _expect_rejected(bad, "step-up fraction exceeds its permitted range")
    negative_cases += 1

    bad = copy.deepcopy(contract)
    field = next(field for field in bad["field_register"] if field["field_id"] == "contributions.starting_monthly_amount")
    field["value"] = "0"
    _expect_rejected(bad, "mandated monthly contribution must be positive")
    negative_cases += 1

    bad = copy.deepcopy(contract)
    bad["policy_case_set"]["case_limit"]["required_control"] = "NONE"
    _expect_rejected(bad, "required zero-return control cannot be removed")
    negative_cases += 1

    return {
        "audit": "PASS",
        "contract": "g4-action-allocation-policy 1.0.0",
        "status": contract["contract_status"],
        "registered_fields": len(contract["field_register"]),
        "required_policy_dimensions": len(contract["required_policy_dimensions"]),
        "negative_cases_rejected": negative_cases,
        "json_schema_2020_12": "PASS; schema validates and validates the contract instance",
        "source_hashes": "PASS; normalized UTF-8/LF hashes match mandate and cashflow fixture; mandate-derived field values resolve and match",
        "unresolved_investor_inputs_preserved": "PASS; reserve, dates, exit, product limits, and drawdown tolerance are not imputed",
        "g2_g3_dependencies": "PASS; pending contracts remain blocked pending acceptance",
        "investment_authorization": contract["investment_authorization"],
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, ensure_ascii=False))
