"""Audit the bounded G4.2 allocation-policy cases and zero-return control."""

from __future__ import annotations

import copy
import csv
import hashlib
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
CASE_PATH = ROOT / "config" / "g4_allocation_policy_cases_v1.json"
SCHEMA_PATH = ROOT / "config" / "g4_allocation_policy_cases.schema.v1.json"
INPUT_PATH = ROOT / "config" / "g4_action_allocation_policy_v1.json"
TOLERANCE = Decimal("0.000000000001")
SLEEVE_IDS = ["nifty500_equity", "rolling_gilt_fund_proxy", "gold", "silver", "strategic_cash"]
EXPECTED_CASES = {
    "existing_65_20_10_5_challenger": {
        "nifty500_equity": "0.65", "rolling_gilt_fund_proxy": "0.20", "gold": "0.10", "silver": "0.05", "strategic_cash": "0"
    },
    "lower_equity_cashflow_matched": {
        "nifty500_equity": "0.50", "rolling_gilt_fund_proxy": "0.30", "gold": "0.15", "silver": "0.05", "strategic_cash": "0"
    },
    "equity_forward_diversified_growth": {
        "nifty500_equity": "0.75", "rolling_gilt_fund_proxy": "0.10", "gold": "0.10", "silver": "0.05", "strategic_cash": "0"
    },
}
EXPECTED_ROLES = {
    "existing_65_20_10_5_challenger": "REFERENCE_CHALLENGER",
    "lower_equity_cashflow_matched": "LOWER_EQUITY_TEST",
    "equity_forward_diversified_growth": "GROWTH_SENSITIVITY_TEST",
}
EXPECTED_BLOCKERS = [
    "G3 issue #18 outcome and exit contract",
    "G5 product identity, availability, fee, tax, and execution",
    "Investor confirmation of unresolved G4.1 inputs",
]
EXPECTED_CONTROL_VALUES = {
    120: "8981227.380300000",
    122: "9110914.503305000",
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(value, dict), f"{path.name} root must be an object")
    return value


def _fingerprint(value: dict[str, Any]) -> str:
    payload = {key: item for key, item in value.items() if key != "content_sha256"}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _text_sha256(path: Path) -> str:
    text = path.read_bytes().decode("utf-8")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()


def _field(contract: dict[str, Any], field_id: str) -> dict[str, Any]:
    return next(item for item in contract["field_register"] if item["field_id"] == field_id)


def _validate_control(control: dict[str, Any], input_contract: dict[str, Any], *, check_sources: bool) -> dict[int, Decimal]:
    _require(control.get("control_id") == "ZERO_RETURN_ARITHMETIC_CONTROL", "required zero-return control is missing")
    _require(control.get("not_an_investable_case") is True, "arithmetic control must not be counted as an investable case")
    _require(control.get("assumptions") == {
        "nominal_return_fraction_per_month": "0",
        "tax_inr": "0",
        "fees_and_costs_inr": "0",
        "inflation_fraction_per_month": "0",
    }, "zero-return control must set return, tax, costs, and inflation to zero")
    fixture = control.get("source_fixture", {})
    relative = fixture.get("path")
    _require(relative == "research/stage512/2026-11-02/cashflow_hurdle_monthly_2026-10_base.csv",
             "zero-return control must use the frozen cashflow fixture")
    path = (ROOT / relative).resolve()
    _require(path.is_relative_to(ROOT) and path.is_file(), "cashflow fixture is missing or escapes the repository")
    _require(fixture.get("sha256") == "d69d9e179fce37e978db75cf59940a2a48b9fc498ceb80341dc45728c70d31ec",
             "cashflow control fixture checksum must match the G4.1 source pin")
    if check_sources:
        _require(_text_sha256(path) == fixture["sha256"], "cashflow fixture hash is stale")

    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    _require(len(rows) == 123, "cashflow fixture must contain month 0 through month 122")
    _require([int(row["month_index"]) for row in rows] == list(range(123)), "cashflow month indices must be complete and ordered")

    initial_amount = Decimal(_field(input_contract, "capital.initial_corpus.amount")["value"])
    starting_contribution = Decimal(_field(input_contract, "contributions.starting_monthly_amount")["value"])
    step_up = Decimal(_field(input_contract, "contributions.step_up_fraction")["value"])
    step_interval = _field(input_contract, "contributions.step_up_interval")["value"]
    _require(Decimal(rows[0]["initial_investment_inr"]) == initial_amount and
             Decimal(rows[0]["monthly_contribution_inr"]) == 0,
             "cashflow fixture month zero must contain the mandate initial corpus only")
    for row in rows[1:]:
        contribution_number = int(row["month_index"])
        step_count = (contribution_number - 1) // step_interval
        expected_contribution = starting_contribution * ((Decimal("1") + step_up) ** step_count)
        _require(Decimal(row["monthly_contribution_inr"]) == expected_contribution,
                 f"cashflow fixture contribution/step-up schedule diverges at month {contribution_number}")
        _require(Decimal(row["initial_investment_inr"]) == 0,
                 f"initial corpus is duplicated after month zero at month {contribution_number}")

    cumulative = Decimal("0")
    for row in rows:
        initial = Decimal(row["initial_investment_inr"])
        contribution = Decimal(row["monthly_contribution_inr"])
        cumulative += initial + contribution
        _require(cumulative == Decimal(row["cumulative_contributions_inr"]),
                 f"cashflow cumulative reconciliation fails at month {row['month_index']}")

    expected = {int(row["horizon_contributions"]): Decimal(row["expected_nominal_value_inr_exact"])
                for row in control["expected_terminal_values"]}
    _require(set(expected) == {120, 122}, "control must contain exactly the 120- and 122-contribution fixtures")
    for horizon, expected_value in expected.items():
        _require(expected_value == Decimal(EXPECTED_CONTROL_VALUES[horizon]),
                 f"zero-return control stored value is incorrect at {horizon} contributions")
        actual = sum((Decimal(row["initial_investment_inr"]) + Decimal(row["monthly_contribution_inr"])
                      for row in rows if int(row["month_index"]) <= horizon), Decimal("0"))
        _require(actual == expected_value, f"zero-return amount does not reconcile at {horizon} contributions")
        terminal = next(item for item in control["expected_terminal_values"] if item["horizon_contributions"] == horizon)
        rounded = actual.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        _require(terminal["expected_nominal_value_inr_rounded_2dp"] == f"{rounded:.2f}",
                 f"rounded control amount is incorrect at {horizon} contributions")
    return expected


def validate_contract(contract: dict[str, Any], *, check_sources: bool = True, check_schema: bool = True) -> dict[int, Decimal]:
    if check_schema:
        schema = _load_json(SCHEMA_PATH)
        Draft202012Validator.check_schema(schema)
        errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(contract))
        _require(not errors, f"G4.2 contract schema validation failed: {errors[0].message if errors else ''}")

    _require(contract.get("contract_id") == "g4-allocation-policy-cases", "wrong G4.2 contract id")
    _require(contract.get("contract_version") == "1.0.0", "unexpected G4.2 contract version")
    _require(contract.get("content_sha256") == _fingerprint(contract), "G4.2 content fingerprint is stale")
    _require(contract.get("contract_status") in {"DRAFT", "AUDIT_PENDING", "ACCEPTED"}, "invalid contract status")
    _require(contract.get("investment_authorization") == "NO_GO", "G4.2 must fail closed to NO_GO")
    limits = contract.get("case_limit", {})
    _require(limits.get("minimum_investable_research_cases") == 3 and limits.get("maximum_investable_research_cases") == 5,
             "case count limits must remain 3 to 5")
    _require(limits.get("optimizer_allowed") is False, "G4.2 must not authorize an optimizer")

    input_contract = _load_json(INPUT_PATH)
    ref = contract.get("input_contract_reference", {})
    _require(ref.get("path") == "config/g4_action_allocation_policy_v1.json", "wrong G4.1 input contract path")
    _require(ref.get("contract_version") == input_contract.get("contract_version"), "G4.1 contract version does not match")
    _require(ref.get("content_sha256") == input_contract.get("content_sha256"), "G4.1 contract fingerprint does not match")
    _require("immutable snapshot" in contract.get("relationship_to_g4_1", "") and
             "without rewriting" in contract.get("relationship_to_g4_1", ""),
             "G4.2 must explain that it extends rather than mutates the accepted G4.1 contract snapshot")

    mandate = _load_json(ROOT / "config" / "investment_mandate_2036.json")
    mandate_weights = mandate["modeling"]["baseline_existing_research_weights"]
    base = EXPECTED_CASES["existing_65_20_10_5_challenger"]
    _require(Decimal(base["nifty500_equity"]) == Decimal(str(mandate_weights["nifty500_equity"])),
             "reference equity weight diverges from the mandate research anchor")
    _require(Decimal(base["rolling_gilt_fund_proxy"]) == Decimal(str(mandate_weights["gilt"])),
             "reference fixed-income weight diverges from the mandate research anchor")
    _require(Decimal(base["gold"]) == Decimal(str(mandate_weights["gold"])) and
             Decimal(base["silver"]) == Decimal(str(mandate_weights["silver"])),
             "reference precious-metal weights diverge from the mandate research anchor")

    sleeves = [item["sleeve_id"] for item in contract.get("asset_sleeves", [])]
    _require(sleeves == SLEEVE_IDS, "asset sleeves must be complete and in the controlled order")
    cases = contract.get("policy_cases", [])
    _require(3 <= len(cases) <= 5, "policy case count must be from 3 to 5")
    ids = [case.get("case_id") for case in cases]
    _require(len(ids) == len(set(ids)), "policy case IDs must be unique")
    _require(set(ids) == set(EXPECTED_CASES), "G4.2 case set must contain the three predeclared comparison questions")
    distinct_weights: set[tuple[str, ...]] = set()
    for case in cases:
        case_id = case["case_id"]
        _require(case.get("case_role") == EXPECTED_ROLES[case_id], f"{case_id} has the wrong comparison role")
        expected_origin = ("EXISTING_UNAPPROVED_RESEARCH_REFERENCE" if case_id == "existing_65_20_10_5_challenger"
                           else "ANALYST_DESIGNED_NOT_INVESTOR_PREFERENCE")
        _require(case.get("design_origin") == expected_origin,
                 f"{case_id} must distinguish existing research from analyst-designed policy")
        weights = case.get("weights_fraction", {})
        _require(list(weights) == SLEEVE_IDS, f"{case_id} must specify every sleeve, including cash")
        parsed = {key: Decimal(value) for key, value in weights.items()}
        _require(all(Decimal("0") <= value <= Decimal("1") for value in parsed.values()),
                 f"{case_id} has a weight outside [0, 1]")
        _require(abs(sum(parsed.values(), Decimal("0")) - Decimal("1")) <= TOLERANCE,
                 f"{case_id} weights must sum to 100% within 1e-12")
        _require(weights == EXPECTED_CASES[case_id], f"{case_id} weights changed without an audited case-set revision")
        vector = tuple(str(parsed[key]) for key in SLEEVE_IDS)
        _require(vector not in distinct_weights, "policy cases must have nonduplicate allocation vectors")
        distinct_weights.add(vector)
        for label in ("initial_allocation_fraction", "sip_allocation_fraction", "step_up_allocation_fraction"):
            _require(case.get(label) == weights, f"{case_id} {label} must match its target allocation")
        _require(case.get("common_action_rules_ref") == "#/common_action_rules",
                 f"{case_id} must inherit explicit common cashflow, deployment, rebalance, distribution, exit, and reserve rules")
        _require(case.get("case_status") == "RESEARCH_COMPARISON_ONLY_NOT_RECOMMENDATION",
                 f"{case_id} must remain an unapproved research comparison")
        _require(case.get("investment_decision_status") == "BLOCKED_PENDING_G3_G5_AND_INVESTOR_CONFIRMATIONS" and
                 case.get("blocked_dependencies") == EXPECTED_BLOCKERS,
                 f"{case_id} must state its exact downstream and investor-confirmation blockers")
        _require(isinstance(case.get("research_question"), str) and case["research_question"].strip(),
                 f"{case_id} must state the question it tests")

    common = contract.get("common_action_rules", {})
    initial = common.get("initial_deployment", {})
    _require(initial.get("rule") == "LUMP_SUM_ON_ACTUAL_CONFIRMED_DATE" and initial.get("staged_deployment") is False,
             "each case must use the same explicit lump-sum research convention")
    _require(initial.get("status") == "ANALYST_PROPOSED" and initial.get("investor_confirmation_required") is True,
             "deployment convention must remain an unconfirmed comparison assumption")
    _require(initial.get("date_field_id") == "capital.initial_corpus.date" and
             _field(input_contract, "capital.initial_corpus.date")["status"] == "UNRESOLVED",
             "initial deployment date must remain unresolved")

    capital = common.get("capital_basis", {})
    reserve = _field(input_contract, "capital.reserve.amount")
    initial_amount = _field(input_contract, "capital.initial_corpus.amount")
    _require(capital.get("initial_amount_field_id") == "capital.initial_corpus.amount" and
             initial_amount["status"] == "MANDATE_DERIVED" and initial_amount["value"] == "4200000",
             "capital basis must trace to the mandate-derived initial corpus")
    _require(capital.get("external_reserve_amount_inr") is None and
             capital.get("external_reserve_status") == "UNRESOLVED" and
             capital.get("must_not_infer_reserve_is_zero") is True and reserve["value"] is None,
             "do not infer an external reserve amount or presume it is zero")
    contribution = common.get("contribution_schedule", {})
    _require(_field(input_contract, contribution["starting_amount_field_id"])["value"] == "25000",
             "contribution schedule must use the mandate's starting monthly amount")
    _require(_field(input_contract, contribution["step_up_fraction_field_id"])["value"] == "0.10" and
             _field(input_contract, contribution["step_up_interval_field_id"])["value"] == 12,
             "step-up schedule must preserve +10% after each 12 contributions")
    _require(contribution.get("step_up_fraction") == "0.10" and
             contribution.get("step_up_interval_contributions") == 12 and
             contribution.get("step_up_allocation_rule") == "Same sleeve fractions as the case SIP allocation.",
             "G4.2 step-up must be explicitly structured and cashflow-matched")
    timing = _field(input_contract, contribution["timing_field_id"])
    _require(contribution.get("research_timing_value") == timing["value"] == "END_OF_MONTH" and
             contribution.get("timing_status") == "ANALYST_PROPOSED" and timing["status"] == "ANALYST_PROPOSED",
             "end-of-month timing must remain a disclosed research convention")
    _require(contribution.get("fixture_horizons_in_contributions") == [120, 122] and
             _field(input_contract, contribution["first_payment_date_field_id"])["status"] == "UNRESOLVED",
             "fixture horizons are allowed, but actual first contribution date must stay unresolved")

    rebalance = common.get("rebalancing", {})
    _require(rebalance.get("status") == "ANALYST_PROPOSED" and rebalance.get("investor_confirmation_required") is True,
             "rebalancing rule must be labeled analyst-proposed pending confirmation")
    _require("each 12-contribution anniversary" in rebalance.get("rule", ""),
             "rebalance schedule must be explicit and anchored to contribution counts")
    _require(rebalance.get("cadence_contributions") == 12 and
             rebalance.get("target_rule") == "Restore holdings to the case target weights at the stated cadence.",
             "rebalance cadence and target restoration must be explicit")
    distribution = common.get("distribution_handling", {})
    income = _field(input_contract, distribution.get("field_id", ""))
    _require(distribution.get("research_value") == "REINVEST_AFTER_TAX" and
             distribution.get("status") == income["status"] == "ANALYST_PROPOSED" and
             distribution.get("investor_confirmation_required") is True,
             "after-tax reinvestment must remain a disclosed proposed assumption")

    cash_rules = common.get("cash_and_reserve", {})
    _require(cash_rules.get("strategic_cash_weight_fraction") == "0" and
             cash_rules.get("external_reserve_amount_inr") is None and
             cash_rules.get("external_reserve_status") == "UNRESOLVED" and
             cash_rules.get("must_not_infer_no_reserve") is True,
             "zero strategic cash must not be presented as zero external reserve")
    terminal = common.get("terminal_measurement_and_exit", {})
    g3 = input_contract["upstream_contracts"]["g3_outcome_contract"]
    _require(terminal.get("status") == "BLOCKED_PENDING_G3_AND_INVESTOR_DATE" and
             terminal.get("dependency_issue") == 18 and
             g3["status"] == "PENDING_MERGE_AND_EXACT_HEAD_VERIFICATION" and
             _field(input_contract, terminal["date_field_id"])["status"] == "UNRESOLVED" and
             terminal.get("forced_liquidation") == "NOT_ASSUMED_PENDING_G3",
             "terminal measurement and exit must remain blocked until G3 and investor date acceptance")
    eligibility = common.get("product_eligibility", {})
    _require(eligibility.get("status") == "BLOCKED_PENDING_G5" and
             eligibility.get("security_identifiers") == [] and eligibility.get("security_eligible") is False,
             "G4.2 must not imply security eligibility before G5")
    _require(common.get("execution_precision", {}).get("execution_rounding_status") == "BLOCKED_PENDING_G5_AND_G4_3",
             "execution rounding must remain blocked pending instrument/account checks")

    values = _validate_control(contract.get("zero_return_arithmetic_control", {}), input_contract,
                               check_sources=check_sources)
    if check_sources:
        fixture_ref = input_contract["upstream_contracts"]["cashflow_fixture"]
        _require(contract["zero_return_arithmetic_control"]["source_fixture"]["sha256"] == fixture_ref["sha256"],
                 "G4.2 zero-return control must use the G4.1-pinned fixture")
    _require(isinstance(contract.get("known_limitations"), list) and contract["known_limitations"],
             "G4.2 limitations must be explicit")
    _require(isinstance(contract.get("invalidation_triggers"), list) and contract["invalidation_triggers"],
             "G4.2 invalidation triggers must be explicit")
    return values


def _expect_rejected(candidate: dict[str, Any], label: str, *, refresh_fingerprint: bool = True) -> None:
    if refresh_fingerprint:
        candidate["content_sha256"] = _fingerprint(candidate)
    try:
        validate_contract(candidate, check_sources=True)
    except (ValueError, TypeError, KeyError, StopIteration):
        return
    raise AssertionError(f"negative case unexpectedly passed: {label}")


def audit() -> dict[str, Any]:
    contract = _load_json(CASE_PATH)
    control_values = validate_contract(contract, check_sources=True)
    negative_cases = 0

    bad = copy.deepcopy(contract)
    bad["content_sha256"] = "0" * 64
    _expect_rejected(bad, "stale G4.2 fingerprint", refresh_fingerprint=False)
    negative_cases += 1

    bad = copy.deepcopy(contract)
    bad["policy_cases"][0]["weights_fraction"]["nifty500_equity"] = "0.64"
    _expect_rejected(bad, "allocation weights do not sum to 100%")
    negative_cases += 1

    bad = copy.deepcopy(contract)
    bad["policy_cases"][0]["initial_allocation_fraction"]["nifty500_equity"] = "0.64"
    _expect_rejected(bad, "initial allocation differs from target")
    negative_cases += 1

    bad = copy.deepcopy(contract)
    bad["policy_cases"][1]["case_id"] = bad["policy_cases"][0]["case_id"]
    _expect_rejected(bad, "duplicate case ID")
    negative_cases += 1

    bad = copy.deepcopy(contract)
    del bad["policy_cases"][0]["weights_fraction"]["silver"]
    _expect_rejected(bad, "required sleeve omitted")
    negative_cases += 1

    bad = copy.deepcopy(contract)
    bad["policy_cases"][2]["sip_allocation_fraction"]["nifty500_equity"] = "0.70"
    _expect_rejected(bad, "SIP allocation differs from target")
    negative_cases += 1

    bad = copy.deepcopy(contract)
    bad["common_action_rules"]["cash_and_reserve"]["external_reserve_amount_inr"] = "0"
    _expect_rejected(bad, "unresolved reserve inferred as zero")
    negative_cases += 1

    bad = copy.deepcopy(contract)
    bad["common_action_rules"]["terminal_measurement_and_exit"]["status"] = "ACCEPTED"
    _expect_rejected(bad, "exit semantics promoted before G3")
    negative_cases += 1

    bad = copy.deepcopy(contract)
    bad["common_action_rules"]["contribution_schedule"]["step_up_interval_contributions"] = 11
    _expect_rejected(bad, "SIP step-up interval changed from 12 contributions")
    negative_cases += 1

    bad = copy.deepcopy(contract)
    bad["common_action_rules"]["rebalancing"]["cadence_contributions"] = 6
    _expect_rejected(bad, "rebalance cadence changed without policy review")
    negative_cases += 1

    mandate_changed = _load_json(INPUT_PATH)
    _field(mandate_changed, "contributions.step_up_fraction")["value"] = "0.09"
    try:
        _validate_control(contract["zero_return_arithmetic_control"], mandate_changed, check_sources=False)
    except (ValueError, TypeError, KeyError):
        negative_cases += 1
    else:
        raise AssertionError("negative case unexpectedly passed: cashflow fixture diverges from mandate SIP step-up")

    bad = copy.deepcopy(contract)
    bad["common_action_rules"]["product_eligibility"]["security_eligible"] = True
    _expect_rejected(bad, "security marked eligible before G5")
    negative_cases += 1

    bad = copy.deepcopy(contract)
    bad["policy_cases"][1]["investment_decision_status"] = "READY_TO_INVEST"
    _expect_rejected(bad, "case marked ready despite G3, G5, and investor blockers")
    negative_cases += 1

    bad = copy.deepcopy(contract)
    bad["zero_return_arithmetic_control"]["expected_terminal_values"][0]["expected_nominal_value_inr_exact"] = "8981227.38"
    _expect_rejected(bad, "incorrect exact zero-return amount")
    negative_cases += 1

    bad = copy.deepcopy(contract)
    bad["zero_return_arithmetic_control"]["source_fixture"]["sha256"] = "0" * 64
    _expect_rejected(bad, "stale cashflow fixture source hash")
    negative_cases += 1

    bad = copy.deepcopy(contract)
    bad["zero_return_arithmetic_control"]["assumptions"]["tax_inr"] = "1"
    _expect_rejected(bad, "nonzero tax in zero-return control")
    negative_cases += 1

    bad = copy.deepcopy(contract)
    bad["policy_cases"] = bad["policy_cases"][:2]
    _expect_rejected(bad, "fewer than three investment-policy cases")
    negative_cases += 1

    bad = copy.deepcopy(contract)
    bad["case_limit"]["optimizer_allowed"] = True
    _expect_rejected(bad, "optimizer enabled")
    negative_cases += 1

    rounded = {str(horizon): str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
               for horizon, value in control_values.items()}
    return {
        "audit": "PASS",
        "contract": f"{contract['contract_id']} {contract['contract_version']}",
        "status": contract["contract_status"],
        "investment_policy_cases": len(contract["policy_cases"]),
        "zero_return_arithmetic_control": "PASS; 120- and 122-contribution cashflow fixtures reconcile exactly",
        "rounded_zero_return_values_inr": rounded,
        "negative_cases_rejected": negative_cases,
        "g3_terminal_exit": "BLOCKED pending accepted G3 contract and investor terminal date",
        "g5_security_eligibility": "BLOCKED; no security is represented as eligible",
        "investment_authorization": contract["investment_authorization"],
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, ensure_ascii=False))
