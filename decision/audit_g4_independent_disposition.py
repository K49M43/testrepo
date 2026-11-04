"""Independent G4.4 audit of policy invariants and G4 delivery disposition."""

from __future__ import annotations

import copy
import csv
import hashlib
import json
import uuid
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator, FormatChecker

import g4_allocation_database_adapter as g43
import sprint2_database_pilot as g2


ROOT = Path(__file__).resolve().parents[1]
ACTION_PATH = ROOT / "config/g4_action_allocation_policy_v1.json"
ACTION_SCHEMA_PATH = ROOT / "config/g4_action_allocation_policy.schema.v1.json"
CASES_PATH = ROOT / "config/g4_allocation_policy_cases_v1.json"
CASES_SCHEMA_PATH = ROOT / "config/g4_allocation_policy_cases.schema.v1.json"
CASHFLOW_PATH = ROOT / "research/stage512/2026-11-02/cashflow_hurdle_monthly_2026-10_base.csv"
HORIZONS = (120, 122)
ZERO = Decimal("0")


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _hash(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _fingerprint(document: Mapping[str, Any]) -> str:
    return _hash({key: value for key, value in document.items() if key != "content_sha256"})


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _decimal(value: Any, label: str) -> Decimal:
    _require(isinstance(value, str), f"{label} must be a decimal string")
    result = Decimal(value)
    _require(result.is_finite(), f"{label} must be finite")
    return result


def _validate_schema(document: Mapping[str, Any], schema: Mapping[str, Any], label: str) -> None:
    Draft202012Validator.check_schema(dict(schema))
    errors = list(Draft202012Validator(dict(schema), format_checker=FormatChecker()).iter_errors(document))
    _require(not errors, f"{label} failed JSON Schema validation: {errors[0].message if errors else ''}")


def _load() -> tuple[dict[str, Any], dict[str, Any], tuple[dict[str, str], ...]]:
    action = json.loads(ACTION_PATH.read_text(encoding="utf-8"))
    action_schema = json.loads(ACTION_SCHEMA_PATH.read_text(encoding="utf-8"))
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    cases_schema = json.loads(CASES_SCHEMA_PATH.read_text(encoding="utf-8"))
    _validate_schema(action, action_schema, "G4.1 action contract")
    _validate_schema(cases, cases_schema, "G4.2 policy case set")
    _require(action.get("content_sha256") == _fingerprint(action), "G4.1 canonical content hash mismatch")
    _require(cases.get("content_sha256") == _fingerprint(cases), "G4.2 canonical content hash mismatch")
    _require(cases.get("input_contract_reference", {}).get("content_sha256") == action.get("content_sha256"),
             "G4.2 does not pin the accepted G4.1 content hash")
    source = CASHFLOW_PATH.read_bytes().decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    cashflow_hash = hashlib.sha256(source.encode("utf-8")).hexdigest()
    expected_hash = action["upstream_contracts"]["cashflow_fixture"]["sha256"]
    _require(cashflow_hash == expected_hash == cases["zero_return_arithmetic_control"]["source_fixture"]["sha256"],
             "G4 cashflow control does not match its pinned source hash")
    rows = tuple(csv.DictReader(source.splitlines()))
    return action, cases, rows


def _field_map(action: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    fields = action.get("field_register")
    _require(isinstance(fields, list), "G4.1 field register must be a list")
    result = {row.get("field_id"): row for row in fields}
    _require(len(result) == len(fields) and None not in result, "G4.1 field IDs must be nonempty and unique")
    return result


def _validate_independent(action: Mapping[str, Any], cases: Mapping[str, Any],
                          rows: tuple[dict[str, str], ...]) -> dict[int, Decimal]:
    fields = _field_map(action)
    for row in fields.values():
        status = row.get("status")
        value = row.get("value")
        if status in {"UNRESOLVED", "DEPENDENCY_BLOCKED"}:
            _require(value is None and row.get("must_not_infer") is True,
                     f"unknown field was silently filled: {row.get('field_id')}")
        elif status in {"INVESTOR_CONFIRMED", "MANDATE_DERIVED", "ANALYST_PROPOSED"}:
            _require(value is not None, f"valued field has a null value: {row.get('field_id')}")
            if row.get("data_type") == "iso_date":
                try:
                    parsed = date.fromisoformat(value)
                except (TypeError, ValueError) as error:
                    raise ValueError(f"invalid ISO date in {row.get('field_id')}") from error
                _require(parsed.isoformat() == value, f"date is not canonical YYYY-MM-DD in {row.get('field_id')}")
        else:
            raise ValueError(f"unsupported field status for {row.get('field_id')}: {status}")

    for field_id in (
        "capital.reserve.amount", "capital.initial_corpus.date", "contributions.first_payment_date",
        "goals.success_and_shortfall_event", "inflation.purchasing_power_anchor_date",
        "horizon.terminal_measurement_date", "risk.interim_drawdown_tolerance",
        "implementation.account_and_product_constraints", "policy.initial_deployment_rule",
        "policy.allocation_schedule", "policy.rebalancing_rule", "policy.terminal_measurement_contract",
        "policy.investor_exit_choice",
    ):
        field = fields[field_id]
        _require(field["value"] is None and field["status"] in {"UNRESOLVED", "DEPENDENCY_BLOCKED"}
                 and field.get("must_not_infer") is True,
                 f"investor/dependency unknown must remain null: {field_id}")

    initial = _decimal(fields["capital.initial_corpus.amount"]["value"], "initial corpus")
    _require(initial == Decimal("4200000") and fields["capital.initial_corpus.amount"]["status"] == "MANDATE_DERIVED",
             "illustrative corpus must trace to the mandate and remain gross before reserve")
    _require(fields["goals.planning_floor.amount"]["value"] == "9000000"
             and fields["goals.stretch_goal.amount"]["value"] == "10000000",
             "original ₹90L floor and ₹1Cr stretch objective must remain distinct and unchanged")
    for field_id in ("capital.initial_corpus.amount", "contributions.starting_monthly_amount",
                     "contributions.step_up_fraction", "contributions.step_up_interval"):
        _require(fields[field_id]["status"] == "MANDATE_DERIVED",
                 f"mandate-derived field classification changed: {field_id}")
    reserve_rule = cases["common_action_rules"]["capital_basis"]
    _require(reserve_rule["external_reserve_amount_inr"] is None
             and reserve_rule["external_reserve_status"] == "UNRESOLVED"
             and reserve_rule["must_not_infer_reserve_is_zero"] is True,
             "G4.2 must not silently assume a zero reserve")

    contribution = cases["common_action_rules"]["contribution_schedule"]
    interval = int(fields["contributions.step_up_interval"]["value"])
    start = _decimal(fields["contributions.starting_monthly_amount"]["value"], "starting contribution")
    step = _decimal(fields["contributions.step_up_fraction"]["value"], "contribution step-up")
    _require(interval == contribution["step_up_interval_contributions"] == 12,
             "step-up must occur after exactly twelve contributions")
    _require(contribution["timing_status"] == "ANALYST_PROPOSED"
             and contribution["actual_first_payment_date_status"] == "UNRESOLVED",
             "payment timing/date must remain an explicitly unconfirmed assumption")
    _require(len(rows) >= max(HORIZONS) + 1, "cashflow fixture omits required contributions")
    cumulative = initial
    totals: dict[int, Decimal] = {}
    for month, row in enumerate(rows[: max(HORIZONS) + 1]):
        _require(int(row["month_index"]) == month, f"cashflow fixture omits or reorders month {month}")
        _require(Decimal(row["initial_investment_inr"]) == (initial if month == 0 else ZERO),
                 f"unexpected initial capital at cashflow month {month}")
        if month:
            expected = start * ((Decimal("1") + step) ** ((month - 1) // interval))
            actual = Decimal(row["monthly_contribution_inr"])
            _require(actual == expected and actual >= ZERO,
                     f"cashflow step-up or cash nonnegativity failed at payment {month}")
            cumulative += actual
        _require(Decimal(row["cumulative_contributions_inr"]) == cumulative,
                 f"cumulative cashflow fails to reconcile at month {month}")
        if month in HORIZONS:
            totals[month] = cumulative

    control = cases["zero_return_arithmetic_control"]
    _require(control["not_an_investable_case"] is True, "zero-return control must not be treated as investable")
    _require(control["assumptions"] == {
        "nominal_return_fraction_per_month": "0", "tax_inr": "0",
        "fees_and_costs_inr": "0", "inflation_fraction_per_month": "0",
    }, "zero-return arithmetic control scope changed")
    expected_controls = {entry["horizon_contributions"]: Decimal(entry["expected_nominal_value_inr_exact"])
                         for entry in control["expected_terminal_values"]}
    _require(totals == expected_controls, "cashflow totals do not match zero-return arithmetic controls")

    sleeves = [row["sleeve_id"] for row in cases["asset_sleeves"]]
    policy_cases = cases.get("policy_cases", [])
    _require(3 <= len(policy_cases) <= 5, "policy case count is outside the accepted range")
    identities: set[tuple[str, ...]] = set()
    for case in policy_cases:
        base = case.get("weights_fraction")
        _require(isinstance(base, dict) and set(base) == set(sleeves),
                 f"{case.get('case_id')} has missing/invalid asset references")
        weights = [_decimal(base[sleeve], f"{case.get('case_id')}/{sleeve}") for sleeve in sleeves]
        _require(all(ZERO <= weight <= Decimal("1") for weight in weights),
                 f"{case.get('case_id')} has negative or greater-than-one weight")
        _require(sum(weights, ZERO) == Decimal("1"), f"{case.get('case_id')} weights do not reconcile to 100%")
        _require(case.get("initial_allocation_fraction") == base
                 and case.get("sip_allocation_fraction") == base
                 and case.get("step_up_allocation_fraction") == base,
                 f"{case.get('case_id')} changes allocation across capital flows")
        identity = tuple(base[sleeve] for sleeve in sleeves)
        _require(identity not in identities, "duplicate-equivalent policy allocations found")
        identities.add(identity)
        _require(case.get("case_status") == "RESEARCH_COMPARISON_ONLY_NOT_RECOMMENDATION"
                 and case.get("investment_decision_status") == "BLOCKED_PENDING_G3_G5_AND_INVESTOR_CONFIRMATIONS",
                 f"{case.get('case_id')} lost its research-only/dependency-blocked status")
        _require(all(Decimal(row["monthly_contribution_inr"]) >= ZERO for row in rows[1:max(HORIZONS) + 1]),
                 "negative contribution cashflow found")

    _require(cases["common_action_rules"]["distribution_handling"]["research_value"] == "REINVEST_AFTER_TAX",
             "distribution policy must specify net-of-tax reinvestment")
    terminal = cases["common_action_rules"]["terminal_measurement_and_exit"]
    _require(terminal["status"] == "BLOCKED_PENDING_G3_AND_INVESTOR_DATE"
             and terminal["forced_liquidation"] == "NOT_ASSUMED_PENDING_G3",
             "G3/terminal exit blocker was removed or liquidation was inferred")
    eligibility = cases["common_action_rules"]["product_eligibility"]
    _require(eligibility["status"] == "BLOCKED_PENDING_G5" and eligibility["security_eligible"] is False
             and eligibility["security_identifiers"] == [],
             "G5 product eligibility must remain blocked")
    return totals


def _expect_rejected(action: Any, label: str) -> None:
    try:
        action()
    except (ValueError, KeyError, TypeError):
        return
    raise AssertionError(f"negative case was accepted: {label}")


def _negative_cases(action: dict[str, Any], cases: dict[str, Any],
                    rows: tuple[dict[str, str], ...]) -> int:
    count = 0
    bad = copy.deepcopy(cases)
    bad["policy_cases"][0]["weights_fraction"]["nifty500_equity"] = "0.66"
    _expect_rejected(lambda: _validate_independent(action, bad, rows), "over-allocation")
    count += 1

    _expect_rejected(lambda: _validate_independent(action, cases, rows[:-1]), "omitted final contribution")
    count += 1

    bad_action = copy.deepcopy(action)
    initial_date = next(row for row in bad_action["field_register"]
                        if row["field_id"] == "capital.initial_corpus.date")
    initial_date.update(status="ANALYST_PROPOSED", value="not-a-date", must_not_infer=False)
    _expect_rejected(lambda: _validate_independent(bad_action, cases, rows), "malformed confirmed date")
    count += 1

    bad_action = copy.deepcopy(action)
    initial_date = next(row for row in bad_action["field_register"]
                        if row["field_id"] == "capital.initial_corpus.date")
    initial_date.update(status="INVESTOR_CONFIRMED", value=None, must_not_infer=False)
    _expect_rejected(lambda: _validate_independent(bad_action, cases, rows), "missing required date")
    count += 1

    bad_action = copy.deepcopy(action)
    reserve = next(row for row in bad_action["field_register"] if row["field_id"] == "capital.reserve.amount")
    reserve.update(status="INVESTOR_CONFIRMED", value="0", must_not_infer=False)
    _expect_rejected(lambda: _validate_independent(bad_action, cases, rows), "unknown reserve marked confirmed")
    count += 1

    bad = copy.deepcopy(cases)
    for key in ("weights_fraction", "initial_allocation_fraction", "sip_allocation_fraction",
                "step_up_allocation_fraction"):
        bad["policy_cases"][1][key] = copy.deepcopy(bad["policy_cases"][0][key])
    _expect_rejected(lambda: _validate_independent(action, bad, rows), "duplicate-equivalent policy")
    count += 1

    bad = copy.deepcopy(cases)
    bad["policy_cases"][0]["weights_fraction"]["unverified_asset"] = "0"
    _expect_rejected(lambda: _validate_independent(action, bad, rows), "invalid asset reference")
    count += 1

    bad = copy.deepcopy(cases)
    bad["policy_cases"][0]["weights_fraction"]["nifty500_equity"] = "-0.01"
    _expect_rejected(lambda: _validate_independent(action, bad, rows), "negative holding")
    count += 1

    bad = copy.deepcopy(cases)
    bad["policy_cases"][0]["weights_fraction"]["nifty500_equity"] = "0.64"
    _expect_rejected(lambda: _validate_independent(action, bad, rows), "weight sum below 100% / omitted cash")
    count += 1

    return count


def _database_runs(cases: dict[str, Any], rows: tuple[dict[str, str], ...],
                   expected_totals: Mapping[int, Decimal]) -> dict[str, Any]:
    database = ROOT / f".g44-independent-{uuid.uuid4().hex}.sqlite"
    try:
        runs = g43.run_all(database)
    finally:
        database.unlink(missing_ok=True)
        Path(f"{database}-wal").unlink(missing_ok=True)
        Path(f"{database}-shm").unlink(missing_ok=True)
    expected_ids = [case["case_id"] for case in cases["policy_cases"]]
    _require([run["output"]["additional_results"]["g4_allocation_arithmetic"]["policy_case_id"]
              for run in runs] == expected_ids, "database runs do not preserve the predeclared policy order")
    _require(len({run["run_key_sha256"] for run in runs}) == len(runs),
             "separate policies did not receive distinct database run identities")
    for run, case in zip(runs, cases["policy_cases"], strict=True):
        output = run["output"]
        result = output["additional_results"]["g4_allocation_arithmetic"]
        manifest = output["run_manifest"]
        _require(run["status"] == "COMPLETE" and manifest["schema_version"] == 1,
                 "database run did not complete on accepted schema version 1")
        _require(manifest["migration_sha256"] == manifest["integration_context"]["g2_migration_sha256"],
                 "top-level G2 migration identity disagrees with G4 context")
        _require(manifest["code_sha256"] == manifest["integration_context"]["g2_engine_code_sha256"],
                 "top-level G2 engine identity disagrees with G4 context")
        _require(manifest["integration_context"]["policy_case_sha256"] == _hash(case),
                 "policy case hash fails independent canonical recomputation")
        identity = {key: manifest[key] for key in (
            "snapshot_sha256", "input_file_sha256", "expected_file_sha256", "code_sha256",
            "migration_sha256", "git_revision", "runtime",
        )}
        identity["integration_context"] = manifest["integration_context"]
        _require(g2.content_run_key(identity) == run["run_key_sha256"],
                 "database run key fails independent manifest recomputation")
        weights = {key: Decimal(value) for key, value in case["weights_fraction"].items()}
        _require(result["investment_authorization"] == "NO_GO", "run output changed investment authorization")
        for horizon in result["horizons"]:
            count = horizon["contribution_count"]
            expected_gross = expected_totals[count]
            _require(Decimal(horizon["gross_total_capital_before_any_reserve_decision_inr"]) == expected_gross,
                     f"stored {count}-payment gross total disagrees with independent cashflow rollup")
            total_by_sleeve = horizon["total_gross_allocation_by_sleeve_inr"]
            _require(all(Decimal(total_by_sleeve[key]) == expected_gross * weights[key] for key in weights),
                     f"stored {count}-payment sleeve allocation fails independent Decimal calculation")
            _require(all(Decimal(value) >= ZERO for value in total_by_sleeve.values()),
                     "negative holdings allocation found")
            _require(horizon["calendar_terminal_date"] is None,
                     "relative cashflow horizon must not infer a calendar terminal date")
    return {"cases": len(runs), "run_keys": [run["run_key_sha256"] for run in runs]}


def audit() -> dict[str, Any]:
    action, cases, rows = _load()
    totals = _validate_independent(action, cases, rows)
    negative_count = _negative_cases(action, cases, rows)
    database = _database_runs(cases, rows, totals)
    return {
        "audit": "PASS",
        "as_of": "2026-11-04",
        "scope": "G4 roadmap policy-definition delivery only; not investment decision Gate G4",
        "independent_policy_cases": len(cases["policy_cases"]),
        "negative_cases_rejected": negative_count,
        "evidence_hashes": {
            "g4_1_content_sha256": action["content_sha256"],
            "g4_2_content_sha256": cases["content_sha256"],
            "cashflow_fixture_sha256": g43._load_inputs().source_texts["cashflow"].sha256,
            "g2_schema_version": g2.MIGRATION_VERSION,
            "g2_migration_sha256": g2.calculation_identity()["migration_sha256"],
        },
        "zero_return_cashflow_control_inr": {str(key): format(value, "f") for key, value in totals.items()},
        "database_run_cases": database["cases"],
        "database_run_keys_sha256": database["run_keys"],
        "canonical_policy_hashes": "PASS; G4.1, G4.2, and selected-case fingerprints independently recomputed",
        "run_identity": "PASS; each database run identity independently recomputed from its manifest",
        "investor_unknowns": "PASS; reserve, dates, exit, drawdown, account/product constraints remain explicit",
        "G3_terminal_exit": "BLOCKED pending accepted G3 semantics and investor date",
        "G5_product_eligibility": "BLOCKED; no security identity is asserted eligible",
        "roadmap_G4_disposition": "PASS for bounded policy-definition and G2 integration deliverables",
        "investment_decision_G4": "BLOCKED; future return, tax, real-wealth, suitability, feasibility, and uncertainty gates remain open",
        "investment_authorization": "NO_GO",
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, ensure_ascii=False))
