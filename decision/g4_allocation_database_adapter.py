"""Run G4.2 allocation arithmetic through the accepted G2 SQLite boundary.

This is a deterministic gross-cash allocation adapter. It does not model
returns, taxes, fees, inflation, investable-product eligibility, or probability.
The G2 Python ledger remains the validated calculation/persistence boundary;
SQLite schema v1 is reused without new tables or migration.
"""

from __future__ import annotations

import csv
import hashlib
import json
import uuid
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from pathlib import PurePosixPath
from typing import Any, Mapping

from jsonschema import Draft202012Validator, FormatChecker

import sprint2_database_pilot as g2
from audit_g4_action_allocation_policy import audit as audit_g4_action_contract
from audit_g4_allocation_policy_cases import audit as audit_g4_policy_cases


ROOT = Path(__file__).resolve().parents[1]
G4_ACTION_PATH = ROOT / "config/g4_action_allocation_policy_v1.json"
G4_ACTION_SCHEMA_PATH = ROOT / "config/g4_action_allocation_policy.schema.v1.json"
G4_CASES_PATH = ROOT / "config/g4_allocation_policy_cases_v1.json"
G4_CASES_SCHEMA_PATH = ROOT / "config/g4_allocation_policy_cases.schema.v1.json"
CASHFLOW_PATH = ROOT / "research/stage512/2026-11-02/cashflow_hurdle_monthly_2026-10_base.csv"
ZERO = Decimal("0")
SUPPORTED_HORIZONS = (120, 122)


@dataclass(frozen=True)
class SourceText:
    path: Path
    text: str
    sha256: str


@dataclass(frozen=True)
class AdapterInputs:
    action_contract: dict[str, Any]
    case_contract: dict[str, Any]
    cashflow_rows: tuple[dict[str, str], ...]
    source_manifest: dict[str, Any]
    source_texts: Mapping[str, SourceText]


def _read_source(path: Path) -> SourceText:
    raw = path.read_bytes()
    text = raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return SourceText(path, text, hashlib.sha256(text.encode("utf-8")).hexdigest())


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _fingerprint(value: Mapping[str, Any]) -> str:
    payload = {key: item for key, item in value.items() if key != "content_sha256"}
    return hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _validate_schema(document: Mapping[str, Any], schema: Mapping[str, Any], label: str) -> None:
    Draft202012Validator.check_schema(dict(schema))
    errors = sorted(
        Draft202012Validator(dict(schema), format_checker=FormatChecker()).iter_errors(document),
        key=lambda error: (list(error.absolute_path), error.message),
    )
    if errors:
        first = errors[0]
        location = "/".join(str(part) for part in first.absolute_path) or "<root>"
        raise ValueError(f"{label} schema violation at {location}: {first.message}")


def _decimal(value: Any, label: str, *, non_negative: bool = True) -> Decimal:
    _require(isinstance(value, str), f"{label} must be a decimal string")
    try:
        result = Decimal(value)
    except InvalidOperation as error:
        raise ValueError(f"{label} must be a valid decimal string") from error
    _require(result.is_finite(), f"{label} must be finite")
    if non_negative:
        _require(result >= ZERO, f"{label} must be non-negative")
    return result


def _decimal_text(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def _field(contract: Mapping[str, Any], field_id: str) -> Mapping[str, Any]:
    matches = [row for row in contract.get("field_register", []) if row.get("field_id") == field_id]
    _require(len(matches) == 1, f"G4.1 must define exactly one {field_id}")
    return matches[0]


def _load_inputs() -> AdapterInputs:
    paths = {
        "g4_action": G4_ACTION_PATH,
        "g4_action_schema": G4_ACTION_SCHEMA_PATH,
        "g4_cases": G4_CASES_PATH,
        "g4_cases_schema": G4_CASES_SCHEMA_PATH,
        "cashflow": CASHFLOW_PATH,
        "g2_input": g2.DEFAULT_INPUT_PATH,
        "g2_expected": g2.DEFAULT_EXPECTED_PATH,
        "g2_migration": g2.MIGRATION_PATH,
        "g2_engine": Path(g2.__file__).resolve(),
        "adapter": Path(__file__).resolve(),
    }
    sources = {key: _read_source(path) for key, path in paths.items()}
    documents = {
        key: json.loads(source.text)
        for key, source in sources.items()
        if key in {"g4_action", "g4_action_schema", "g4_cases", "g4_cases_schema", "g2_input", "g2_expected"}
    }
    _validate_schema(documents["g4_action"], documents["g4_action_schema"], "G4.1 action contract")
    _validate_schema(documents["g4_cases"], documents["g4_cases_schema"], "G4.2 policy case set")
    _require(documents["g4_action"].get("investment_authorization") == "NO_GO",
             "G4.1 investment authorization must remain NO_GO")
    _require(documents["g4_cases"].get("investment_authorization") == "NO_GO",
             "G4.2 investment authorization must remain NO_GO")
    _require(documents["g4_cases"].get("contract_status") == "DRAFT",
             "adapter only accepts the current bounded DRAFT policy contract")
    _require(audit_g4_action_contract().get("audit") == "PASS", "G4.1 upstream contract audit failed")
    _require(audit_g4_policy_cases().get("audit") == "PASS", "G4.2 policy-case audit failed")
    _require(documents["g4_cases"].get("content_sha256") == _fingerprint(documents["g4_cases"]),
             "G4.2 content fingerprint is stale")
    action = documents["g4_action"]
    cases = documents["g4_cases"]
    _require(action.get("content_sha256") == _fingerprint(action), "G4.1 content fingerprint is stale")
    _require(cases.get("input_contract_reference", {}).get("contract_version") == action.get("contract_version"),
             "G4.2 references a different G4.1 version")
    _require(cases.get("input_contract_reference", {}).get("content_sha256") == action.get("content_sha256"),
             "G4.2 does not pin the current G4.1 fingerprint")

    initial = _field(action, "capital.initial_corpus.amount")
    _require(initial.get("status") == "MANDATE_DERIVED" and initial.get("value") == "4200000",
             "supported allocation basis must remain the mandate-derived illustrative corpus")
    reserve = _field(action, "capital.reserve.amount")
    _require(reserve.get("status") == "UNRESOLVED" and reserve.get("value") is None
             and reserve.get("must_not_infer") is True,
             "external reserve must remain unresolved and must not be imputed")
    rules = cases["common_action_rules"]
    horizon_values = rules["contribution_schedule"].get("fixture_horizons_in_contributions")
    _require(horizon_values == list(SUPPORTED_HORIZONS), "supported contribution horizons changed")

    expected_cashflow_hash = action["upstream_contracts"]["cashflow_fixture"].get("sha256")
    _require(sources["cashflow"].sha256 == expected_cashflow_hash,
             "cashflow fixture source hash differs from the accepted G4.1 contract")
    rows = tuple(csv.DictReader(sources["cashflow"].text.splitlines()))
    _require(len(rows) >= max(SUPPORTED_HORIZONS) + 1, "cashflow fixture does not cover 122 contributions")
    _require(tuple(rows[0].keys()) == (
        "month_index", "calendar_month", "initial_investment_inr",
        "monthly_contribution_inr", "cumulative_contributions_inr",
    ), "cashflow fixture columns changed")
    for index, row in enumerate(rows[: max(SUPPORTED_HORIZONS) + 1]):
        _require(row["month_index"] == str(index), f"cashflow fixture month index is not contiguous at row {index}")
        for field in ("initial_investment_inr", "monthly_contribution_inr", "cumulative_contributions_inr"):
            _decimal(row[field], f"cashflow row {index} {field}")
        year, month = (int(part) for part in row["calendar_month"].split("-"))
        month_number = 2026 * 12 + 9 + index  # month zero is October 2026
        _require((year, month) == (month_number // 12, month_number % 12 + 1),
                 f"cashflow fixture calendar month is discontinuous at row {index}")
    _require(_decimal(rows[0]["initial_investment_inr"], "initial amount") == Decimal(initial["value"]),
             "cashflow fixture initial amount does not match G4.1 mandate-derived amount")
    _require(_decimal(rows[0]["monthly_contribution_inr"], "month-zero contribution") == ZERO,
             "cashflow fixture must not add a month-zero SIP")
    starting_amount = _decimal(_field(action, "contributions.starting_monthly_amount")["value"],
                               "starting monthly contribution")
    step_fraction = _decimal(_field(action, "contributions.step_up_fraction")["value"], "step-up fraction")
    step_interval = _field(action, "contributions.step_up_interval")["value"]
    _require(isinstance(step_interval, int) and not isinstance(step_interval, bool) and step_interval > 0,
             "step-up interval must be a positive integer")
    cumulative = _decimal(rows[0]["cumulative_contributions_inr"], "month-zero cumulative amount")
    for contribution_index in range(1, max(SUPPORTED_HORIZONS) + 1):
        row = rows[contribution_index]
        _require(_decimal(row["initial_investment_inr"],
                          f"cashflow row {contribution_index} initial amount") == ZERO,
                 f"cashflow fixture contains an unexpected second initial investment at row {contribution_index}")
        step_count = (contribution_index - 1) // step_interval
        expected_contribution = starting_amount * ((Decimal("1") + step_fraction) ** step_count)
        actual_contribution = _decimal(row["monthly_contribution_inr"],
                                       f"cashflow row {contribution_index} contribution")
        _require(actual_contribution == expected_contribution,
                 f"cashflow fixture amount does not follow the G4.1 step-up at contribution {contribution_index}")
        cumulative += actual_contribution
        _require(_decimal(row["cumulative_contributions_inr"],
                          f"cashflow row {contribution_index} cumulative amount") == cumulative,
                 f"cashflow fixture cumulative amount fails to reconcile at contribution {contribution_index}")
    case_ids = [case.get("case_id") for case in cases.get("policy_cases", [])]
    _require(len(case_ids) == len(set(case_ids)) == len(cases.get("policy_cases", [])),
             "G4.2 case IDs must be unique")

    source_manifest = {
        key: {"path": source.path.relative_to(ROOT).as_posix(), "sha256": source.sha256}
        for key, source in sources.items()
    }
    # Keep explicit IDs for machine consumers while making source links inspectable.
    source_manifest["g2_database_schema"] = {
        "path": sources["g2_migration"].path.relative_to(ROOT).as_posix(),
        "schema_version": g2.MIGRATION_VERSION,
        "migration_sha256": sources["g2_migration"].sha256,
    }
    return AdapterInputs(action, cases, rows, source_manifest, sources)


def _allocation_vector(raw: Any, sleeve_ids: tuple[str, ...], label: str) -> dict[str, Decimal]:
    _require(isinstance(raw, dict), f"{label} must be an object")
    _require(set(raw) == set(sleeve_ids), f"{label} sleeve keys do not match the frozen G4.2 sleeve set")
    weights = {sleeve: _decimal(raw[sleeve], f"{label}.{sleeve}") for sleeve in sleeve_ids}
    _require(sum(weights.values(), ZERO) == Decimal("1"), f"{label} weights must sum exactly to one")
    return weights


def calculate_allocation_arithmetic(inputs: AdapterInputs, case: Mapping[str, Any]) -> dict[str, Any]:
    """Allocate frozen gross cashflows by exact policy fractions, with no returns."""
    case_id = case.get("case_id")
    _require(isinstance(case_id, str) and case_id, "policy case id is required")
    _require(case.get("case_status") == "RESEARCH_COMPARISON_ONLY_NOT_RECOMMENDATION",
             "only non-recommendation research cases are accepted")
    _require(case.get("investment_decision_status") == "BLOCKED_PENDING_G3_G5_AND_INVESTOR_CONFIRMATIONS",
             "policy case must retain its G3/G5/investor blocks")
    sleeves = tuple(row["sleeve_id"] for row in inputs.case_contract["asset_sleeves"])
    initial_weights = _allocation_vector(case.get("initial_allocation_fraction"), sleeves, "initial allocation")
    sip_weights = _allocation_vector(case.get("sip_allocation_fraction"), sleeves, "SIP allocation")
    step_up_weights = _allocation_vector(case.get("step_up_allocation_fraction"), sleeves, "step-up allocation")
    target_weights = _allocation_vector(case.get("weights_fraction"), sleeves, "target allocation")
    _require(initial_weights == sip_weights == step_up_weights == target_weights,
             "initial, SIP, step-up, and target allocations must match the accepted G4.2 policy")

    initial_value = _decimal(_field(inputs.action_contract, "capital.initial_corpus.amount")["value"],
                              "initial corpus")
    horizons: list[dict[str, Any]] = []
    for horizon in SUPPORTED_HORIZONS:
        initial_allocated = {sleeve: initial_value * initial_weights[sleeve] for sleeve in sleeves}
        contribution_allocated = {sleeve: ZERO for sleeve in sleeves}
        monthly_rows: list[dict[str, Any]] = []
        for contribution_index in range(1, horizon + 1):
            row = inputs.cashflow_rows[contribution_index]
            gross_contribution = _decimal(row["monthly_contribution_inr"],
                                          f"cashflow row {contribution_index} contribution")
            weights = step_up_weights if contribution_index > 1 and (
                contribution_index - 1
            ) // int(_field(inputs.action_contract, "contributions.step_up_interval")["value"]) > (
                contribution_index - 2
            ) // int(_field(inputs.action_contract, "contributions.step_up_interval")["value"]) else sip_weights
            sleeve_amounts = {sleeve: gross_contribution * weights[sleeve] for sleeve in sleeves}
            for sleeve, amount in sleeve_amounts.items():
                contribution_allocated[sleeve] += amount
            monthly_rows.append({
                "contribution_index": contribution_index,
                "cashflow_fixture_month": int(row["month_index"]),
                "gross_contribution_inr": _decimal_text(gross_contribution),
                "allocation_by_sleeve_inr": {sleeve: _decimal_text(sleeve_amounts[sleeve]) for sleeve in sleeves},
            })

        _require(all(sum((Decimal(item["allocation_by_sleeve_inr"][sleeve]) for sleeve in sleeves), ZERO)
                      == Decimal(item["gross_contribution_inr"]) for item in monthly_rows),
                 "monthly allocation arithmetic does not conserve gross cashflow")
        total_by_sleeve = {sleeve: initial_allocated[sleeve] + contribution_allocated[sleeve]
                           for sleeve in sleeves}
        gross_contributions = sum(contribution_allocated.values(), ZERO)
        total_gross_capital = initial_value + gross_contributions
        _require(sum(total_by_sleeve.values(), ZERO) == total_gross_capital,
                 "sleeve allocations do not reconcile to gross mandate cashflows")
        horizons.append({
            "contribution_count": horizon,
            "horizon_measure": "relative_contribution_count_only",
            "calendar_terminal_date": None,
            "initial_corpus_before_unresolved_reserve_inr": _decimal_text(initial_value),
            "gross_contributions_inr": _decimal_text(gross_contributions),
            "gross_total_capital_before_any_reserve_decision_inr": _decimal_text(total_gross_capital),
            "initial_allocation_by_sleeve_inr": {sleeve: _decimal_text(initial_allocated[sleeve]) for sleeve in sleeves},
            "contribution_allocation_by_sleeve_inr": {sleeve: _decimal_text(contribution_allocated[sleeve]) for sleeve in sleeves},
            "total_gross_allocation_by_sleeve_inr": {sleeve: _decimal_text(total_by_sleeve[sleeve]) for sleeve in sleeves},
            "monthly_contribution_allocation": monthly_rows,
            "rebalance_cashflows_inr": "0",
            "rebalance_interpretation": "No return or distribution drift is modeled; same target weights for initial capital and each contribution produce no rebalance transfer in this arithmetic control.",
        })

    return {
        "calculation_scope": "DETERMINISTIC_GROSS_CASH_ALLOCATION_ARITHMETIC_ONLY",
        "policy_case_id": case_id,
        "policy_case_role": case["case_role"],
        "case_status": case["case_status"],
        "investment_decision_status": case["investment_decision_status"],
        "investment_authorization": "NO_GO",
        "source_links": inputs.source_manifest,
        "policy_weights_fraction": {
            "initial": {key: _decimal_text(value) for key, value in initial_weights.items()},
            "sip": {key: _decimal_text(value) for key, value in sip_weights.items()},
            "step_up": {key: _decimal_text(value) for key, value in step_up_weights.items()},
        },
        "limitations": [
            "The initial corpus amount is mandate-derived illustrative gross capital before the external reserve decision; it is not labeled deployable or investable capital.",
            "Contribution calendar dates are unresolved; fixture month indices are relative only.",
            "Returns, taxes, fees, inflation, security rounding, eligibility, availability, and probabilities are not calculated.",
            "The underlying G2 ledger result in this run is a separate synthetic fixture validation and is not a G4 policy result.",
            "G3 terminal outcome/exit semantics, G5 product checks, and investor confirmations remain blocked.",
        ],
        "horizons": horizons,
    }


def _integration_context(inputs: AdapterInputs, case: Mapping[str, Any]) -> dict[str, Any]:
    g2_identity = g2.calculation_identity()
    adapter_hash = inputs.source_texts["adapter"].sha256
    case_contract = inputs.case_contract
    action_contract = inputs.action_contract
    return {
        "adapter_id": "g4-policy-to-g2-sqlite",
        "adapter_version": "1.0.0",
        "policy_case_id": case["case_id"],
        "policy_case_sha256": hashlib.sha256(_canonical(case).encode("utf-8")).hexdigest(),
        "g4_action_contract_version": action_contract["contract_version"],
        "g4_action_contract_fingerprint": action_contract["content_sha256"],
        "g4_policy_contract_version": case_contract["contract_version"],
        "g4_policy_contract_fingerprint": case_contract["content_sha256"],
        "adapter_code_sha256": adapter_hash,
        "g2_engine_code_sha256": g2_identity["engine_code_sha256"],
        "g2_accepted_schema_version": g2_identity["schema_version"],
        "g2_migration_sha256": g2_identity["migration_sha256"],
        "accepted_dependency_commits": {
            "g2_sprint2_database_pilot": "af0e5b81db0745c9055e340fc94739a5200904bb",
            "g4_1_action_policy": "e8ac909d9bd665f4b4c263679d0bcc2951361621",
            "g4_2_allocation_cases": "4bad5ac0adec63814ae4b94cb06aeac3e95c06dc",
        },
        "cashflow_source_sha256": inputs.source_texts["cashflow"].sha256,
        "result_domain": "G4_DETERMINISTIC_GROSS_ALLOCATION_ARITHMETIC",
        "investment_authorization": "NO_GO",
    }


def run_policy_case(database_path: Path, case_id: str, *,
                    inject_failure_after: str | None = None,
                    inputs: AdapterInputs | None = None) -> dict[str, Any]:
    inputs = inputs or _load_inputs()
    matches = [case for case in inputs.case_contract["policy_cases"] if case.get("case_id") == case_id]
    _require(len(matches) == 1, f"unknown or duplicate G4.2 policy case: {case_id}")
    case = matches[0]
    context = _integration_context(inputs, case)
    snapshot_context = {
        "integration_id": context["adapter_id"],
        "integration_version": context["adapter_version"],
        "integration_context": context,
        "source_links": inputs.source_manifest,
        "g4_action_contract": inputs.action_contract,
        "g4_policy_case_set": inputs.case_contract,
    }

    def calculate_from_persisted_snapshot(snapshot_payload: Mapping[str, Any]) -> Mapping[str, Any]:
        persisted_context = snapshot_payload.get("integration_context")
        _require(isinstance(persisted_context, dict), "SQLite snapshot lacks G4 integration context")
        _require(persisted_context.get("integration_id") == context["adapter_id"],
                 "SQLite snapshot integration id does not match this adapter")
        _require(persisted_context.get("integration_context") == context,
                 "persisted G4 run context differs from the pinned run configuration")
        _require(persisted_context.get("g4_action_contract") == inputs.action_contract
                 and persisted_context.get("g4_policy_case_set") == inputs.case_contract,
                 "persisted G4 contracts differ from the validated source documents")
        persisted_case_set = persisted_context["g4_policy_case_set"]
        persisted_case = [row for row in persisted_case_set["policy_cases"]
                          if row.get("case_id") == context["policy_case_id"]]
        _require(len(persisted_case) == 1, "selected policy case is missing or ambiguous in SQLite snapshot")
        persisted_sources = persisted_context.get("source_links")
        _require(persisted_sources == inputs.source_manifest,
                 "persisted source manifest differs from the hashed run inputs")
        persisted_cashflow_rows: tuple[dict[str, str], ...] | None = None
        for key in ("g4_action", "g4_action_schema", "g4_cases", "g4_cases_schema", "cashflow"):
            reference = persisted_sources[key]
            relative = PurePosixPath(reference["path"])
            source_path = (ROOT.joinpath(*relative.parts)).resolve()
            try:
                source_path.relative_to(ROOT.resolve())
            except ValueError as error:
                raise ValueError(f"persisted source path escapes repository root: {key}") from error
            current_source = _read_source(source_path)
            _require(current_source.sha256 == reference["sha256"],
                     f"immutable source changed after the SQLite input snapshot was created: {key}")
            if key == "cashflow":
                persisted_cashflow_rows = tuple(csv.DictReader(current_source.text.splitlines()))
        _require(persisted_cashflow_rows is not None, "cashflow source could not be read from the pinned link")
        persisted_inputs = AdapterInputs(
            persisted_context["g4_action_contract"],
            persisted_case_set,
            persisted_cashflow_rows,
            persisted_sources,
            inputs.source_texts,
        )
        allocation_result = calculate_allocation_arithmetic(persisted_inputs, persisted_case[0])
        return {"g4_allocation_arithmetic": allocation_result}
    # Use the exact source bytes loaded and hashed above, through a private
    # transient fixture pair. G2 reads each snapshot file once; source evidence
    # remains untouched and is only linked by path/hash.
    database_path.parent.mkdir(parents=True, exist_ok=True)
    token = uuid.uuid4().hex
    input_path = database_path.parent / f".{database_path.name}.{token}.input.json"
    expected_path = database_path.parent / f".{database_path.name}.{token}.expected.json"
    try:
        input_path.write_text(inputs.source_texts["g2_input"].text, encoding="utf-8", newline="\n")
        expected_path.write_text(inputs.source_texts["g2_expected"].text, encoding="utf-8", newline="\n")
        return g2.execute_pilot(
            database_path,
            input_path,
            expected_path,
            inject_failure_after=inject_failure_after,
            snapshot_context=snapshot_context,
            run_context_extension=context,
            result_calculator=calculate_from_persisted_snapshot,
        )
    finally:
        input_path.unlink(missing_ok=True)
        expected_path.unlink(missing_ok=True)


def run_all(database_path: Path) -> list[dict[str, Any]]:
    inputs = _load_inputs()
    return [run_policy_case(database_path, case["case_id"], inputs=inputs)
            for case in inputs.case_contract["policy_cases"]]


def audit_case_contract() -> dict[str, Any]:
    inputs = _load_inputs()
    projections = [calculate_allocation_arithmetic(inputs, case)
                   for case in inputs.case_contract["policy_cases"]]
    return {
        "audit": "PASS",
        "adapter": "g4-policy-to-g2-sqlite 1.0.0",
        "g2_schema_version": g2.MIGRATION_VERSION,
        "policy_cases": len(projections),
        "cashflow_horizons": list(SUPPORTED_HORIZONS),
        "source_identity": "PASS; all inputs are linked by source path and normalized content hash",
        "allocation_conservation": "PASS; exact Decimal arithmetic for each monthly contribution and total sleeve allocation",
        "investment_authorization": "NO_GO",
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, required=True,
                        help="SQLite database path; keep pilot databases outside Git")
    parser.add_argument("--case-id", help="G4.2 policy case id; omit to run all three cases")
    args = parser.parse_args()
    runs = ([run_policy_case(args.database, args.case_id)] if args.case_id
            else run_all(args.database))
    print(json.dumps({
        "status": "PASS",
        "schema_version": g2.MIGRATION_VERSION,
        "runs": [{
            "policy_case_id": run["output"]["additional_results"]["g4_allocation_arithmetic"]["policy_case_id"],
            "attempt_id": run["attempt_id"],
            "run_key_sha256": run["run_key_sha256"],
            "snapshot_sha256": run["snapshot_sha256"],
            "output_sha256": run["output_sha256"],
            "status": run["status"],
            "horizons": [{
                "contribution_count": horizon["contribution_count"],
                "gross_total_capital_before_any_reserve_decision_inr": horizon[
                    "gross_total_capital_before_any_reserve_decision_inr"
                ],
            } for horizon in run["output"]["additional_results"]["g4_allocation_arithmetic"]["horizons"]],
            "timings_ms": run["timings_ms"],
        } for run in runs],
        "investment_authorization": "NO_GO",
    }, indent=2, ensure_ascii=False))
