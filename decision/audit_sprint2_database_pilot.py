"""Reproduce the frozen Sprint 2 fixture through SQLite and Python."""

from __future__ import annotations

import copy
import json
import sqlite3
import uuid
from pathlib import Path

from sprint2_database_pilot import (
    DEFAULT_EXPECTED_PATH,
    DEFAULT_INPUT_PATH,
    ROOT,
    apply_migrations,
    canonical_json,
    connect_database,
    content_run_key,
    database_state,
    execute_pilot,
    fixture_from_mapping,
    load_fixture,
    sha256_text,
)


def audit() -> dict[str, object]:
    folder = ROOT / "research/sprint2"
    token = uuid.uuid4().hex
    database_a = folder / f".audit-{token}-a.sqlite"
    database_b = folder / f".audit-{token}-b.sqlite"
    failed_input_path = folder / f".audit-{token}-input.json"
    failed_expected_path = folder / f".audit-{token}-expected.json"
    files = [database_a, database_b, failed_input_path, failed_expected_path]

    try:
        fixture = load_fixture()
        assert fixture.raw["fixture_id"] == "after-tax-ledger-two-lot-two-tax-year"
        assert len(fixture.events) == 9

        # Date/year, type, and decimal-string constraints reject malformed input
        # before it can become a persisted snapshot.
        bad_date = copy.deepcopy(fixture.raw)
        bad_date["events"][0]["tax_year"] = "2027-28"
        try:
            fixture_from_mapping(bad_date)
        except ValueError as error:
            assert "tax_year does not match" in str(error)
        else:
            raise AssertionError("date/tax-year mismatch must be rejected")
        bad_amount = copy.deepcopy(fixture.raw)
        bad_amount["events"][0]["cash_amount_inr"] = 1000
        try:
            fixture_from_mapping(bad_amount)
        except ValueError as error:
            assert "decimal string" in str(error)
        else:
            raise AssertionError("numeric JSON amounts must be rejected; INR is encoded as decimal text")

        first = execute_pilot(database_a)
        second = execute_pilot(database_a)
        fresh_database = execute_pilot(database_b)
        assert first["status"] == second["status"] == fresh_database["status"] == "COMPLETE"
        assert first["snapshot_sha256"] == second["snapshot_sha256"] == fresh_database["snapshot_sha256"]
        assert first["run_key_sha256"] == second["run_key_sha256"] == fresh_database["run_key_sha256"]
        assert first["output_sha256"] == second["output_sha256"] == fresh_database["output_sha256"]
        assert first["output"] == second["output"] == fresh_database["output"]

        state = database_state(database_a)
        assert state["schema_version"] == 1
        assert state["integrity_check"] == "ok"
        assert state["counts"] == {
            "schema_migrations": 1,
            "fixture_snapshots": 1,
            "ledger_events": 9,
            "auxiliary_inputs": 4,
            "calculation_attempts": 2,
        }
        conn = connect_database(database_a)
        try:
            migration_sha = apply_migrations(conn)
            assert apply_migrations(conn) == migration_sha
            assert conn.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0] == 1
            assert conn.execute(
                "SELECT COUNT(*) FROM calculation_attempts WHERE status = 'COMPLETE' AND output_json IS NOT NULL"
            ).fetchone()[0] == 2
        finally:
            conn.close()

        # A structurally present but altered normalized auxiliary row must not
        # be silently ignored in favor of the canonical snapshot payload.
        conn = connect_database(database_b)
        try:
            conn.execute(
                "UPDATE auxiliary_inputs SET payload_json = ? WHERE snapshot_sha256 = ? AND input_kind = 'valuation_price'",
                ('{"price_inr":"999999"}', first["snapshot_sha256"]),
            )
            conn.commit()
        finally:
            conn.close()
        try:
            execute_pilot(database_b)
        except RuntimeError as error:
            assert "auxiliary-input rows do not match" in str(error)
        else:
            raise AssertionError("altered normalized auxiliary inputs must fail closed")
        conn = connect_database(database_b)
        try:
            failed = conn.execute(
                "SELECT status, output_json, output_sha256 FROM calculation_attempts "
                "WHERE run_key_sha256 = ? AND status = 'FAILED' LIMIT 1",
                (first["run_key_sha256"],),
            ).fetchone()
            assert tuple(failed) == ("FAILED", None, None)
            assert conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        finally:
            conn.close()

        # A changed code fingerprint creates a different deterministic identity.
        context = {"snapshot_sha256": first["snapshot_sha256"], "code_sha256": "a" * 64}
        changed_context = {**context, "code_sha256": "b" * 64}
        assert content_run_key(context) != content_run_key(changed_context)

        original_input = json.loads(DEFAULT_INPUT_PATH.read_text(encoding="utf-8"))
        original_expected = json.loads(DEFAULT_EXPECTED_PATH.read_text(encoding="utf-8"))
        for version, failure_point in (("failure-inputs-v1", "inputs"), ("failure-compute-v1", "compute")):
            changed_input = copy.deepcopy(original_input)
            changed_input["fixture_version"] = version
            changed_expected = copy.deepcopy(original_expected)
            changed_expected["fixture_version"] = version
            failed_input_path.write_text(json.dumps(changed_input, indent=2) + "\n", encoding="utf-8", newline="\n")
            failed_expected_path.write_text(json.dumps(changed_expected, indent=2) + "\n", encoding="utf-8", newline="\n")
            snapshot_hash = sha256_text(canonical_json(changed_input))
            try:
                execute_pilot(database_a, failed_input_path, failed_expected_path,
                              inject_failure_after=failure_point)
            except RuntimeError as error:
                assert "injected failure" in str(error)
            else:
                raise AssertionError(f"injected {failure_point} failure should raise")
            conn = connect_database(database_a)
            try:
                stored_snapshot = conn.execute(
                    "SELECT event_count FROM fixture_snapshots WHERE snapshot_sha256 = ?", (snapshot_hash,)
                ).fetchone()
                assert stored_snapshot is not None and stored_snapshot["event_count"] == 9
                attempt = conn.execute(
                    "SELECT status, output_json, output_sha256, failure_message FROM calculation_attempts WHERE snapshot_sha256 = ?",
                    (snapshot_hash,),
                ).fetchone()
                assert attempt is not None
                assert attempt["status"] == "FAILED"
                assert attempt["output_json"] is None and attempt["output_sha256"] is None
                assert "injected failure" in attempt["failure_message"]
                event_count = conn.execute(
                    "SELECT COUNT(*) FROM ledger_events WHERE snapshot_sha256 = ?", (snapshot_hash,)
                ).fetchone()[0]
                assert event_count == 9
            finally:
                conn.close()

        final_state = database_state(database_a)
        assert final_state["integrity_check"] == "ok"
        assert final_state["counts"]["calculation_attempts"] == 4
        assert final_state["counts"]["fixture_snapshots"] == 3
        assert final_state["counts"]["ledger_events"] == 27
        assert final_state["counts"]["schema_migrations"] == 1
        assert all(value >= 0 for value in first["timings_ms"].values())

        return {
            "audit": "PASS",
            "scope": "one frozen synthetic nine-event fixture; no investor result",
            "clean_migrations_and_repeatability": "PASS",
            "canonical_snapshot_and_run_identity": "PASS",
            "exact_output_parity_across_runs_and_clean_databases": "PASS",
            "expected_golden_values": {
                "gross_terminal_wealth_inr": "2433",
                "incremental_portfolio_tax_inr": "473.5640",
                "net_accessible_fixture_wealth_inr": "2109.4360",
            },
            "failed_run_atomicity": "PASS; complete inputs retained, failed attempts have no result payload",
            "database_integrity": "PASS",
            "timing_stages_ms": first["timings_ms"],
            "investment_authorization": "NO-GO",
        }
    finally:
        for path in files:
            for candidate in (path, Path(f"{path}-wal"), Path(f"{path}-shm")):
                try:
                    candidate.unlink(missing_ok=True)
                except PermissionError:
                    pass


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, ensure_ascii=False))
