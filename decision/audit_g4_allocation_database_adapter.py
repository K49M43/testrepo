"""Independent audit for the G4.3 policy-to-G2 database adapter."""

from __future__ import annotations

import copy
import hashlib
import json
import sqlite3
import uuid
from contextlib import closing
from decimal import Decimal
from pathlib import Path
from typing import Any

from g4_allocation_database_adapter import (
    ROOT,
    _load_inputs,
    calculate_allocation_arithmetic,
    run_policy_case,
)
import sprint2_database_pilot as g2


def _expect_rejected(action: Any, label: str) -> None:
    try:
        action()
    except (ValueError, RuntimeError):
        return
    raise AssertionError(f"negative case was accepted: {label}")


def _independent_run_key(identity: dict[str, Any]) -> str:
    canonical = json.dumps(identity, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _attempts(database: Path) -> list[sqlite3.Row]:
    with closing(g2.connect_database(database)) as conn:
        return conn.execute(
            "SELECT status, output_json, output_sha256 FROM calculation_attempts ORDER BY started_at_utc, attempt_id"
        ).fetchall()


def audit() -> dict[str, Any]:
    inputs = _load_inputs()
    cases = inputs.case_contract["policy_cases"]
    _require_ids = [case["case_id"] for case in cases]
    if len(_require_ids) != len(set(_require_ids)) or len(cases) != 3:
        raise AssertionError("G4.3 accepts only the three predeclared, uniquely identified G4.2 cases")

    projections = {case["case_id"]: calculate_allocation_arithmetic(inputs, case) for case in cases}
    if set(projections) != set(_require_ids):
        raise AssertionError("policy projection IDs differ from the accepted case set")
    baseline_horizons = projections[_require_ids[0]]["horizons"]
    if [row["contribution_count"] for row in baseline_horizons] != [120, 122]:
        raise AssertionError("both supported G4.2 cashflow horizons must be present")
    for case_id, projection in projections.items():
        for horizon in projection["horizons"]:
            total = Decimal(horizon["gross_total_capital_before_any_reserve_decision_inr"])
            allocated = sum((Decimal(amount) for amount in horizon["total_gross_allocation_by_sleeve_inr"].values()), Decimal("0"))
            if allocated != total:
                raise AssertionError(f"gross allocation fails conservation for {case_id}")
            if horizon["calendar_terminal_date"] is not None:
                raise AssertionError("adapter must not infer calendar terminal dates")
        if projection["investment_authorization"] != "NO_GO":
            raise AssertionError("allocation arithmetic cannot authorize investment")

    bad_case = copy.deepcopy(cases[0])
    bad_case["sip_allocation_fraction"]["nifty500_equity"] = "0.64"
    _expect_rejected(lambda: calculate_allocation_arithmetic(inputs, bad_case), "weights not conserved")
    bad_case = copy.deepcopy(cases[0])
    bad_case["investment_decision_status"] = "APPROVED"
    _expect_rejected(lambda: calculate_allocation_arithmetic(inputs, bad_case), "approved case")
    _expect_rejected(lambda: run_policy_case(ROOT / ".g43-unknown-case-unused.sqlite", "unknown"),
                      "unknown policy id")

    token = uuid.uuid4().hex
    database_a = ROOT / f".g43-audit-{token}-same.sqlite"
    database_b = ROOT / f".g43-audit-{token}-clean.sqlite"
    failure_databases = [ROOT / f".g43-audit-{token}-failure-{point}.sqlite" for point in ("inputs", "compute")]
    audit_databases = [database_a, database_b, *failure_databases]
    try:
        source_hashes_before = {key: source.sha256 for key, source in inputs.source_texts.items()}

        first = run_policy_case(database_a, _require_ids[0], inputs=inputs)
        repeat = run_policy_case(database_a, _require_ids[0], inputs=inputs)
        clean = run_policy_case(database_b, _require_ids[0], inputs=inputs)
        other_cases = [run_policy_case(database_a, case_id, inputs=inputs) for case_id in _require_ids[1:]]

        if first["status"] != "COMPLETE" or repeat["status"] != "COMPLETE":
            raise AssertionError("same-database reruns did not complete")
        if first["run_key_sha256"] != repeat["run_key_sha256"] or first["output_sha256"] != repeat["output_sha256"]:
            raise AssertionError("same policy/config/code did not reproduce its run/output identity")
        if first["run_key_sha256"] != clean["run_key_sha256"] or first["output_sha256"] != clean["output_sha256"]:
            raise AssertionError("clean database rebuild did not reproduce run/output identity")
        if first["attempt_id"] == repeat["attempt_id"]:
            raise AssertionError("attempt identifiers must distinguish individual executions")
        run_keys = {first["run_key_sha256"], *(row["run_key_sha256"] for row in other_cases)}
        snapshot_hashes = {first["snapshot_sha256"], *(row["snapshot_sha256"] for row in other_cases)}
        if len(run_keys) != len(_require_ids) or len(snapshot_hashes) != len(_require_ids):
            raise AssertionError("different policy cases must receive distinct run and snapshot identities")

        for run in [first, repeat, clean, *other_cases]:
            output = run["output"]
            g4_result = output["additional_results"]["g4_allocation_arithmetic"]
            context = output["run_manifest"]["integration_context"]
            manifest = output["run_manifest"]
            if context["g2_accepted_schema_version"] != 1 or context["policy_case_id"] != g4_result["policy_case_id"]:
                raise AssertionError("run manifest does not pin accepted G2 schema and G4 case identity")
            if context["accepted_dependency_commits"].get("g2_sprint2_database_pilot") != "af0e5b81db0745c9055e340fc94739a5200904bb":
                raise AssertionError("run manifest does not pin the accepted G2 merge commit")
            if context.get("g3_outcome_contract_version") != "1.0.0" or context.get("g3_outcome_contract_sha256") != "9723efd8e5c29b06c78fe813a6d4649e12f5be73cf066ddd4aa4ea607bb75873":
                raise AssertionError("run manifest does not pin the accepted G3 outcome contract version and hash")
            if context["accepted_dependency_commits"].get("g3_outcome_contract") != "a241fddaa937bb21b721ee00cef3f1bfc8503ba8":
                raise AssertionError("run manifest does not pin the accepted G3 merge commit")
            if g4_result["source_links"]["cashflow"]["sha256"] != inputs.source_manifest["cashflow"]["sha256"]:
                raise AssertionError("immutable cashflow source link changed in a run result")
            if g4_result["investment_authorization"] != "NO_GO":
                raise AssertionError("stored policy run must remain non-authorizing")

        manifest = first["output"]["run_manifest"]
        identity_payload = {
            "snapshot_sha256": manifest["snapshot_sha256"],
            "input_file_sha256": manifest["input_file_sha256"],
            "expected_file_sha256": manifest["expected_file_sha256"],
            "code_sha256": manifest["code_sha256"],
            "migration_sha256": manifest["migration_sha256"],
            "git_revision": manifest["git_revision"],
            "runtime": manifest["runtime"],
            "integration_context": manifest["integration_context"],
        }
        if _independent_run_key(identity_payload) != first["run_key_sha256"]:
            raise AssertionError("run key does not reproduce from its persisted identity manifest")
        changed_code_identity = copy.deepcopy(identity_payload)
        changed_code_identity["integration_context"]["adapter_code_sha256"] = "0" * 64
        if _independent_run_key(changed_code_identity) == first["run_key_sha256"]:
            raise AssertionError("material adapter-code identity change did not change the run key")
        changed_config_identity = copy.deepcopy(identity_payload)
        changed_config_identity["integration_context"]["g4_policy_contract_fingerprint"] = "0" * 64
        if _independent_run_key(changed_config_identity) == first["run_key_sha256"]:
            raise AssertionError("material policy-contract change did not change the run key")

        for point, failed_db in zip(("inputs", "compute"), failure_databases, strict=True):
            _expect_rejected(
                lambda p=point, db=failed_db: run_policy_case(
                    db, _require_ids[0], inject_failure_after=p, inputs=inputs
                ),
                f"injected failure after {point}",
            )
            failed = _attempts(failed_db)
            if len(failed) != 1 or failed[0]["status"] != "FAILED":
                raise AssertionError(f"{point} failure was not recorded as a failed attempt")
            if failed[0]["output_json"] is not None or failed[0]["output_sha256"] is not None:
                raise AssertionError(f"{point} failure left a published result")

        for key, source in inputs.source_texts.items():
            if g2.normalized_text_sha256(source.path) != source_hashes_before[key]:
                raise AssertionError(f"source artifact was modified during run: {source.path}")
        with closing(g2.connect_database(database_a)) as conn:
            version = conn.execute("PRAGMA user_version").fetchone()[0]
            migration_count = conn.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0]
            integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
            complete_count = conn.execute(
                "SELECT COUNT(*) FROM calculation_attempts WHERE status='COMPLETE' AND output_json IS NOT NULL"
            ).fetchone()[0]
        if version != 1 or migration_count != 1 or integrity != "ok" or complete_count != 4:
            raise AssertionError("G2 schema, transaction, or SQLite integrity acceptance failed")
    finally:
        for database in audit_databases:
            database.unlink(missing_ok=True)
            Path(f"{database}-wal").unlink(missing_ok=True)
            Path(f"{database}-shm").unlink(missing_ok=True)

    return {
        "audit": "PASS",
        "adapter": "G4.3 bounded G4.2-to-G2 SQLite adapter",
        "policy_cases": len(_require_ids),
        "horizons": [120, 122],
        "run_identity": "PASS; case/config/code identities distinct; repeated and clean-database replay exact",
        "atomic_failure_injection": "PASS; failures after input persistence and calculation publish no output",
        "source_immutability": "PASS; all linked source hashes unchanged",
        "schema": "PASS; reuses accepted SQLite schema v1 without a parallel migration",
        "investment_authorization": "NO_GO",
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, ensure_ascii=False))
