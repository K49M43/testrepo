"""SQLite persistence pilot for the frozen Sprint 2 synthetic fixture.

This module keeps numerical calculations in the existing Python ledger. SQLite
stores a content-addressed input snapshot, normalized event/evidence rows, run
attempt status, and the completed deterministic result.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Callable, Mapping

from after_tax_event_ledger import LedgerEvent, run_ledger, tax_year_for
from capital_gain_loss_schedule import Loss, Offset
from ty2026_27_tax_components import TaxInput


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE_DIR = ROOT / "research/sprint2/fixture_v1"
DEFAULT_INPUT_PATH = DEFAULT_FIXTURE_DIR / "input.json"
DEFAULT_EXPECTED_PATH = DEFAULT_FIXTURE_DIR / "expected.json"
MIGRATION_PATH = ROOT / "decision/migrations/001_sprint2_fixture_pilot.sql"
MIGRATION_VERSION = 1
ZERO = Decimal("0")


@dataclass(frozen=True)
class FixtureData:
    raw: dict[str, Any]
    events: list[LedgerEvent]
    valuation_prices: dict[str, Decimal]
    external_tax_inputs: dict[str, TaxInput]
    capital_loss_offsets_by_year: dict[str, list[Offset]]
    carried_losses_by_year: dict[str, list[Loss]]


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def normalized_text_and_sha256(path: Path) -> tuple[str, str]:
    """Read UTF-8 text once and return the normalized content and its hash."""
    text = path.read_bytes().decode("utf-8")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return normalized, hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def normalized_text_sha256(path: Path) -> str:
    return normalized_text_and_sha256(path)[1]


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def content_run_key(run_context: Mapping[str, Any]) -> str:
    """Create a stable identity from calculation and provenance inputs."""
    return sha256_text(canonical_json(dict(run_context)))


def _decimal(value: Any, field: str, *, non_negative: bool = True) -> Decimal:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be encoded as a decimal string")
    try:
        parsed = Decimal(value)
    except InvalidOperation as error:
        raise ValueError(f"{field} is not a valid decimal string") from error
    if not parsed.is_finite() or (non_negative and parsed < ZERO):
        qualifier = "finite and non-negative" if non_negative else "finite"
        raise ValueError(f"{field} must be {qualifier}")
    return parsed


def _bool(value: Any, field: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{field} must be a JSON boolean")
    return value


def fixture_from_mapping(raw: Mapping[str, Any]) -> FixtureData:
    data = dict(raw)
    for field in ("fixture_id", "fixture_version", "fixture_status", "source_or_assumption", "qualification_status"):
        if not isinstance(data.get(field), str) or not data[field].strip():
            raise ValueError(f"fixture requires non-empty {field}")
    origin = data.get("origin")
    if not isinstance(origin, dict) or not origin.get("source_file") or not origin.get("source_commit"):
        raise ValueError("fixture origin requires source_file and source_commit")
    event_rows = data.get("events")
    if not isinstance(event_rows, list) or not event_rows:
        raise ValueError("fixture events must be a non-empty list")

    events: list[LedgerEvent] = []
    for index, row in enumerate(event_rows):
        if not isinstance(row, dict):
            raise ValueError(f"events[{index}] must be an object")
        try:
            event_date = date.fromisoformat(row["event_date"])
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(f"events[{index}].event_date must be an ISO date") from error
        if event_date.isoformat() != row["event_date"]:
            raise ValueError(f"events[{index}].event_date must use YYYY-MM-DD")
        if row.get("tax_year") != tax_year_for(event_date):
            raise ValueError(f"events[{index}].tax_year does not match its date")
        event_id = row.get("event_id")
        if not isinstance(event_id, str) or not event_id.strip():
            raise ValueError(f"events[{index}].event_id is required")
        seq = row.get("event_sequence")
        if isinstance(seq, bool) or not isinstance(seq, int) or seq <= 0:
            raise ValueError(f"events[{index}].event_sequence must be a positive integer")
        tax_year = row.get("tax_year")
        if not isinstance(tax_year, str) or len(tax_year) != 7:
            raise ValueError(f"events[{index}].tax_year must be YYYY-YY")
        if not isinstance(row.get("instrument_id"), str) or not row["instrument_id"].strip():
            raise ValueError(f"events[{index}].instrument_id is required")

        optional_decimal_fields: dict[str, Decimal | None] = {}
        for field in ("units", "unit_price_inr"):
            value = row.get(field)
            optional_decimal_fields[field] = None if value is None else _decimal(value, f"events[{index}].{field}")
        events.append(LedgerEvent(
            event_id=event_id,
            event_date=event_date,
            tax_year=tax_year,
            event_sequence=seq,
            event_type=row.get("event_type", ""),
            instrument_id=row["instrument_id"],
            cash_amount_inr=_decimal(row.get("cash_amount_inr"), f"events[{index}].cash_amount_inr"),
            source_or_assumption=data["source_or_assumption"],
            qualification_status=data["qualification_status"],
            lot_id=row.get("lot_id"),
            units=optional_decimal_fields["units"],
            unit_price_inr=optional_decimal_fields["unit_price_inr"],
            transaction_cost_inr=_decimal(row.get("transaction_cost_inr"), f"events[{index}].transaction_cost_inr"),
            tax_basis_addition_inr=_decimal(row.get("tax_basis_addition_inr"), f"events[{index}].tax_basis_addition_inr"),
            gross_income_inr=_decimal(row.get("gross_income_inr"), f"events[{index}].gross_income_inr"),
            tax_withheld_inr=_decimal(row.get("tax_withheld_inr"), f"events[{index}].tax_withheld_inr"),
            deductible_transfer_expenses_inr=_decimal(
                row.get("deductible_transfer_expenses_inr"), f"events[{index}].deductible_transfer_expenses_inr"
            ),
            tax_classification=row.get("tax_classification", ""),
            tax_classification_confirmed=_bool(row.get("tax_classification_confirmed"), f"events[{index}].tax_classification_confirmed"),
            section76_specified_fund_confirmed=_bool(
                row.get("section76_specified_fund_confirmed"), f"events[{index}].section76_specified_fund_confirmed"
            ),
            section196_eligibility_confirmed=_bool(
                row.get("section196_eligibility_confirmed"), f"events[{index}].section196_eligibility_confirmed"
            ),
            section197_eligibility_confirmed=_bool(
                row.get("section197_eligibility_confirmed"), f"events[{index}].section197_eligibility_confirmed"
            ),
            section198_eligibility_confirmed=_bool(
                row.get("section198_eligibility_confirmed"), f"events[{index}].section198_eligibility_confirmed"
            ),
        ))

    external_rows = data.get("external_tax_inputs")
    if not isinstance(external_rows, dict) or not external_rows:
        raise ValueError("external_tax_inputs must explicitly cover every fixture tax year")
    tax_decimal_fields = (
        "ordinary_income", "dividend_income", "section76_stcg", "section196_stcg",
        "section197_ltcg", "section198_ltcg", "tax_withheld_credit",
    )
    tax_bool_fields = (
        "resident_individual", "section196_eligible", "section197_eligible",
        "section198_eligible", "section76_eligible",
    )
    external: dict[str, TaxInput] = {}
    for year, row in external_rows.items():
        if not isinstance(row, dict):
            raise ValueError(f"external_tax_inputs[{year}] must be an object")
        values = {field: _decimal(row.get(field), f"external_tax_inputs[{year}].{field}") for field in tax_decimal_fields}
        values.update({field: _bool(row.get(field), f"external_tax_inputs[{year}].{field}") for field in tax_bool_fields})
        external[year] = TaxInput(**values)

    raw_prices = data.get("valuation_prices_inr")
    if not isinstance(raw_prices, dict):
        raise ValueError("valuation_prices_inr must be an object")
    prices = {lot_id: _decimal(price, f"valuation_prices_inr[{lot_id}]") for lot_id, price in raw_prices.items()}

    offsets: dict[str, list[Offset]] = {}
    raw_offsets = data.get("capital_loss_offsets_by_year", {})
    if not isinstance(raw_offsets, dict):
        raise ValueError("capital_loss_offsets_by_year must be an object")
    for year, rows in raw_offsets.items():
        if not isinstance(rows, list):
            raise ValueError(f"capital_loss_offsets_by_year[{year}] must be a list")
        offsets[year] = [
            Offset(str(row["loss_id"]), str(row["gain_id"]), _decimal(row["amount_inr"], f"offset[{index}].amount_inr"))
            for index, row in enumerate(rows)
        ]

    carried: dict[str, list[Loss]] = {}
    raw_carried = data.get("carried_losses_by_year", {})
    if not isinstance(raw_carried, dict):
        raise ValueError("carried_losses_by_year must be an object")
    for year, rows in raw_carried.items():
        if not isinstance(rows, list):
            raise ValueError(f"carried_losses_by_year[{year}] must be a list")
        carried[year] = [
            Loss(
                loss_id=str(row["loss_id"]), source_event_id=str(row["source_event_id"]),
                lot_id=str(row["lot_id"]), origin_tax_year=str(row["origin_tax_year"]),
                amount_inr=_decimal(row["amount_inr"], f"carried_loss[{index}].amount_inr"),
                character=str(row["character"]),
                return_filed_under_263_1=_bool(row["return_filed_under_263_1"], f"carried_loss[{index}].return_filed_under_263_1"),
                return_evidence_reference=str(row.get("return_evidence_reference", "")),
            )
            for index, row in enumerate(rows)
        ]

    event_years = {event.tax_year for event in events}
    if not event_years.issubset(external):
        raise ValueError(f"external_tax_inputs missing fixture years: {sorted(event_years - set(external))}")
    return FixtureData(data, events, prices, external, offsets, carried)


def load_fixture(input_path: Path = DEFAULT_INPUT_PATH) -> FixtureData:
    input_text, _ = normalized_text_and_sha256(input_path)
    return load_fixture_text(input_text)


def load_fixture_text(input_text: str) -> FixtureData:
    raw = json.loads(input_text)
    return fixture_from_mapping(raw)


def run_fixture(fixture: FixtureData):
    return run_ledger(
        fixture.events,
        fixture.valuation_prices,
        external_tax_inputs=fixture.external_tax_inputs,
        capital_loss_offsets_by_year=fixture.capital_loss_offsets_by_year,
        carried_losses_by_year=fixture.carried_losses_by_year,
    )


def result_summary(result: Any) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "ledger_status": result.ledger_status,
        "event_count": result.event_count,
    }
    for field in (
        "cash_contributions_inr", "gross_income_inr", "portfolio_withholding_inr", "transaction_costs_inr",
        "other_fees_inr", "withdrawals_inr", "ending_cash_inr", "ending_market_value_inr",
        "realized_economic_gain_inr", "unrealized_gain_inr", "gross_terminal_wealth_inr",
        "incremental_portfolio_tax_inr", "remaining_incremental_tax_after_withholding_inr",
        "excess_portfolio_withholding_not_valued_inr", "net_accessible_fixture_wealth_inr",
        "reconciliation_residual_inr",
    ):
        value = getattr(result, field)
        summary[field] = None if value is None else str(value)
    summary["tax_years"] = {}
    for year, details in result.tax_years.items():
        income = details["portfolio_income"]
        row = {
            "portfolio_withholding_inr": income["withholding_credit"],
            "incremental_portfolio_tax_inr": details["incremental_portfolio_tax"],
            "remaining_tax_after_withholding_inr": details["remaining_incremental_tax_after_portfolio_withholding"],
        }
        for category, field in (
            ("ordinary", "portfolio_ordinary_income_inr"),
            ("dividend", "portfolio_dividend_income_inr"),
            ("section197_ltcg", "portfolio_section197_ltcg_inr"),
        ):
            if income.get(category) not in (None, "0", "0.0", "0.00"):
                row[field] = income[category]
        if "excess_portfolio_withholding_not_valued_as_refund" in details:
            row["excess_withholding_not_valued_as_refund_inr"] = details[
                "excess_portfolio_withholding_not_valued_as_refund"
            ]
        summary["tax_years"][year] = row
    return summary


def assert_expected(result: Any, expected_path: Path = DEFAULT_EXPECTED_PATH, *,
                    expected_data: Mapping[str, Any] | None = None) -> dict[str, Any]:
    if expected_data is None:
        expected_text, _ = normalized_text_and_sha256(expected_path)
        expected_data = json.loads(expected_text)
    summary = result_summary(result)
    expected = expected_data["expected_outputs"]

    def compare(actual_value: Any, expected_value: Any, path: str) -> None:
        if isinstance(expected_value, dict):
            if not isinstance(actual_value, dict):
                raise AssertionError(f"{path}: expected an object")
            for key, value in expected_value.items():
                if key not in actual_value:
                    raise AssertionError(f"{path}.{key}: missing from actual output")
                compare(actual_value[key], value, f"{path}.{key}")
        elif isinstance(expected_value, str) and isinstance(actual_value, str):
            try:
                equal = Decimal(actual_value) == Decimal(expected_value)
            except Exception:
                equal = actual_value == expected_value
            if not equal:
                raise AssertionError(f"{path}: expected {expected_value!r}, got {actual_value!r}")
        elif actual_value != expected_value:
            raise AssertionError(f"{path}: expected {expected_value!r}, got {actual_value!r}")

    compare(summary, expected, "expected_outputs")
    return expected_data


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _git_revision() -> str | None:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True,
            capture_output=True, text=True, timeout=5,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


def _hash_code_and_migration() -> tuple[str, str]:
    paths = (
        ROOT / "decision/after_tax_event_ledger.py",
        ROOT / "decision/capital_gain_loss_schedule.py",
        ROOT / "decision/ty2026_27_tax_components.py",
        Path(__file__).resolve(),
        MIGRATION_PATH,
    )
    components = {path.relative_to(ROOT).as_posix(): normalized_text_sha256(path) for path in paths}
    return sha256_text(canonical_json(components)), components[MIGRATION_PATH.relative_to(ROOT).as_posix()]


def calculation_identity() -> dict[str, Any]:
    """Expose the accepted engine and schema identity to bounded adapters."""
    code_hash, migration_hash = _hash_code_and_migration()
    return {
        "engine_code_sha256": code_hash,
        "schema_version": MIGRATION_VERSION,
        "migration_sha256": migration_hash,
    }


def _execute_sql_script(conn: sqlite3.Connection, script: str) -> None:
    statement = ""
    for line in script.splitlines(keepends=True):
        statement += line
        if sqlite3.complete_statement(statement):
            sql = statement.strip()
            if sql:
                conn.execute(sql)
            statement = ""
    if statement.strip():
        raise ValueError("migration has an incomplete SQL statement")


def connect_database(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=30, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 30000")
    return conn


def apply_migrations(conn: sqlite3.Connection) -> str:
    migration_text = MIGRATION_PATH.read_text(encoding="utf-8")
    migration_text = migration_text.replace("\r\n", "\n").replace("\r", "\n")
    migration_hash = sha256_text(migration_text)
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    if version > MIGRATION_VERSION:
        raise RuntimeError(f"database schema version {version} is newer than supported {MIGRATION_VERSION}")
    if version == MIGRATION_VERSION:
        row = conn.execute(
            "SELECT sha256 FROM schema_migrations WHERE version = ?", (MIGRATION_VERSION,)
        ).fetchone()
        if row is None or row["sha256"] != migration_hash:
            raise RuntimeError("applied migration checksum does not match the migration file")
        return migration_hash
    if version != 0:
        raise RuntimeError(f"no migration path from schema version {version}")

    conn.execute("BEGIN IMMEDIATE")
    try:
        _execute_sql_script(conn, migration_text)
        conn.execute(
            "INSERT INTO schema_migrations(version, migration_name, sha256, applied_at_utc) VALUES (?, ?, ?, ?)",
            (MIGRATION_VERSION, MIGRATION_PATH.name, migration_hash, _utc_now()),
        )
        conn.execute(f"PRAGMA user_version = {MIGRATION_VERSION}")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    return migration_hash


def _auxiliary_rows(raw: Mapping[str, Any]) -> list[tuple[str, str, str, str]]:
    rows: list[tuple[str, str, str, str]] = []
    for year, payload in raw["external_tax_inputs"].items():
        rows.append(("external_tax_input", year, year, canonical_json(payload)))
    for lot_id, price in raw["valuation_prices_inr"].items():
        rows.append(("valuation_price", "", lot_id, canonical_json({"price_inr": price})))
    for year, items in raw.get("capital_loss_offsets_by_year", {}).items():
        for index, payload in enumerate(items):
            rows.append(("capital_loss_offset", year, str(index), canonical_json(payload)))
    for year, items in raw.get("carried_losses_by_year", {}).items():
        for index, payload in enumerate(items):
            rows.append(("carried_loss", year, str(index), canonical_json(payload)))
    return rows


def _insert_auxiliary_rows(conn: sqlite3.Connection, snapshot_hash: str, raw: Mapping[str, Any]) -> None:
    conn.executemany(
        "INSERT INTO auxiliary_inputs(snapshot_sha256, input_kind, tax_year, row_key, payload_json) VALUES (?, ?, ?, ?, ?)",
        [(snapshot_hash, kind, year, key, payload) for kind, year, key, payload in _auxiliary_rows(raw)],
    )


def _persist_snapshot(conn: sqlite3.Connection, fixture: FixtureData, snapshot_hash: str,
                      canonical_payload: str) -> None:
    existing = conn.execute(
        "SELECT canonical_payload_json, event_count FROM fixture_snapshots WHERE snapshot_sha256 = ?",
        (snapshot_hash,),
    ).fetchone()
    if existing is not None:
        if existing["canonical_payload_json"] != canonical_payload or existing["event_count"] != len(fixture.events):
            raise RuntimeError("content-address collision or corrupt stored fixture snapshot")
        return
    conn.execute(
        "INSERT INTO fixture_snapshots(snapshot_sha256, fixture_id, fixture_version, canonical_payload_json, event_count, created_at_utc) VALUES (?, ?, ?, ?, ?, ?)",
        (snapshot_hash, fixture.raw["fixture_id"], fixture.raw["fixture_version"], canonical_payload,
         len(fixture.events), _utc_now()),
    )
    for event_order, row in enumerate(fixture.raw["events"]):
        conn.execute(
            "INSERT INTO ledger_events(snapshot_sha256, event_id, event_order, event_date, tax_year, event_sequence, event_type, instrument_id, cash_amount_inr, payload_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (snapshot_hash, row["event_id"], event_order, row["event_date"], row["tax_year"], row["event_sequence"],
             row["event_type"], row["instrument_id"], row["cash_amount_inr"], canonical_json(row)),
        )
    _insert_auxiliary_rows(conn, snapshot_hash, fixture.raw)


def _read_snapshot(conn: sqlite3.Connection, snapshot_hash: str, expected_event_count: int) -> dict[str, Any]:
    row = conn.execute(
        "SELECT canonical_payload_json, event_count FROM fixture_snapshots WHERE snapshot_sha256 = ?",
        (snapshot_hash,),
    ).fetchone()
    if row is None or row["event_count"] != expected_event_count:
        raise RuntimeError("persisted fixture snapshot is missing or incomplete")
    event_rows = conn.execute(
        "SELECT event_id, event_order, event_date, tax_year, event_sequence, event_type, instrument_id, cash_amount_inr, payload_json FROM ledger_events WHERE snapshot_sha256 = ? ORDER BY event_order",
        (snapshot_hash,),
    ).fetchall()
    if len(event_rows) != expected_event_count:
        raise RuntimeError("persisted event rows do not match the snapshot event count")
    payload = json.loads(row["canonical_payload_json"])
    if canonical_json(payload) != row["canonical_payload_json"] or sha256_text(canonical_json(payload)) != snapshot_hash:
        raise RuntimeError("persisted canonical input does not match its content hash")
    for index, stored in enumerate(event_rows):
        expected_event = payload["events"][index]
        if (stored["event_order"] != index or stored["event_id"] != expected_event["event_id"]
                or stored["event_date"] != expected_event["event_date"]
                or stored["tax_year"] != expected_event["tax_year"]
                or stored["event_sequence"] != expected_event["event_sequence"]
                or stored["event_type"] != expected_event["event_type"]
                or stored["instrument_id"] != expected_event["instrument_id"]
                or stored["cash_amount_inr"] != expected_event["cash_amount_inr"]
                or stored["payload_json"] != canonical_json(expected_event)):
            raise RuntimeError(f"normalized event row {index} does not match canonical snapshot")
    return payload


def execute_pilot(database_path: Path, input_path: Path = DEFAULT_INPUT_PATH,
                  expected_path: Path = DEFAULT_EXPECTED_PATH, *,
                  inject_failure_after: str | None = None,
                  snapshot_context: Mapping[str, Any] | None = None,
                  run_context_extension: Mapping[str, Any] | None = None,
                  result_extensions: Mapping[str, Any] | None = None,
                  result_calculator: Callable[[Mapping[str, Any]], Mapping[str, Any]] | None = None) -> dict[str, Any]:
    if inject_failure_after not in (None, "inputs", "compute"):
        raise ValueError("inject_failure_after must be None, 'inputs', or 'compute'")
    if result_extensions is not None and result_calculator is not None:
        raise ValueError("provide either result_extensions or result_calculator, not both")
    load_started = time.perf_counter()
    input_text, input_file_hash = normalized_text_and_sha256(input_path)
    expected_text, expected_file_hash = normalized_text_and_sha256(expected_path)
    fixture = load_fixture_text(input_text)
    if snapshot_context is not None:
        context = dict(snapshot_context)
        # Fail before touching SQLite if the adapter context is not canonical JSON.
        canonical_json(context)
        fixture.raw["integration_context"] = context
    expected_data = json.loads(expected_text)
    if expected_data.get("fixture_id") != fixture.raw["fixture_id"] or expected_data.get("fixture_version") != fixture.raw["fixture_version"]:
        raise ValueError("expected-output fixture identity does not match input fixture")
    canonical_payload = canonical_json(fixture.raw)
    snapshot_hash = sha256_text(canonical_payload)
    load_ms = (time.perf_counter() - load_started) * 1000

    code_hash, migration_hash = _hash_code_and_migration()
    git_revision = _git_revision()
    runtime = {"python": sys.version.split()[0], "sqlite": sqlite3.sqlite_version}
    run_context = {
        "snapshot_sha256": snapshot_hash,
        "input_file_sha256": input_file_hash,
        "expected_file_sha256": expected_file_hash,
        "code_sha256": code_hash,
        "migration_sha256": migration_hash,
        "git_revision": git_revision,
        "runtime": runtime,
    }
    if run_context_extension is not None:
        extension = dict(run_context_extension)
        canonical_json(extension)
        run_context["integration_context"] = extension
    run_key = content_run_key(run_context)
    attempt_id = uuid.uuid4().hex
    started_at = _utc_now()

    conn = connect_database(database_path)
    try:
        apply_migrations(conn)
        conn.execute(
            "INSERT INTO calculation_attempts(attempt_id, run_key_sha256, snapshot_sha256, code_sha256, status, started_at_utc) VALUES (?, ?, ?, ?, 'RUNNING', ?)",
            (attempt_id, run_key, snapshot_hash, code_hash, started_at),
        )
        conn.commit()
        compute_ms = 0.0
        snapshot_read_ms = 0.0
        try:
            conn.execute("BEGIN IMMEDIATE")
            _persist_snapshot(conn, fixture, snapshot_hash, canonical_payload)
            conn.commit()
            if inject_failure_after == "inputs":
                raise RuntimeError("injected failure after complete input snapshot persistence")

            snapshot_started = time.perf_counter()
            conn.execute("BEGIN")
            snapshot_payload = _read_snapshot(conn, snapshot_hash, len(fixture.events))
            expected_auxiliary_rows = sorted(_auxiliary_rows(snapshot_payload))
            stored_auxiliary_rows = [
                tuple(row)
                for row in conn.execute(
                    "SELECT input_kind, tax_year, row_key, payload_json FROM auxiliary_inputs "
                    "WHERE snapshot_sha256 = ? ORDER BY input_kind, tax_year, row_key",
                    (snapshot_hash,),
                ).fetchall()
            ]
            if stored_auxiliary_rows != expected_auxiliary_rows:
                raise RuntimeError("persisted auxiliary-input rows do not match canonical snapshot")
            conn.commit()
            persisted_fixture = fixture_from_mapping(snapshot_payload)
            snapshot_read_ms = (time.perf_counter() - snapshot_started) * 1000

            compute_started = time.perf_counter()
            ledger_result = run_fixture(persisted_fixture)
            assert_expected(ledger_result, expected_path, expected_data=expected_data)
            if result_calculator is not None:
                calculated_extensions = result_calculator(snapshot_payload)
                if not isinstance(calculated_extensions, Mapping):
                    raise ValueError("result_calculator must return a mapping")
                result_extensions = dict(calculated_extensions)
                canonical_json(result_extensions)
            compute_ms = (time.perf_counter() - compute_started) * 1000
            if inject_failure_after == "compute":
                raise RuntimeError("injected failure after calculation before result persistence")

            result_payload = ledger_result.as_json()
            manifest = {
                "fixture_id": fixture.raw["fixture_id"],
                "fixture_version": fixture.raw["fixture_version"],
                "snapshot_sha256": snapshot_hash,
                "input_file_sha256": input_file_hash,
                "expected_file_sha256": expected_file_hash,
                "code_sha256": code_hash,
                "migration_sha256": migration_hash,
                "run_key_sha256": run_key,
                "git_revision": git_revision,
                "runtime": runtime,
                "schema_version": MIGRATION_VERSION,
            }
            output = {"run_manifest": manifest, "result": result_payload}
            if run_context_extension is not None:
                output["run_manifest"]["integration_context"] = dict(run_context_extension)
            if result_extensions is not None:
                extensions = dict(result_extensions)
                canonical_json(extensions)
                output["additional_results"] = extensions
            output_json = canonical_json(output)
            output_hash = sha256_text(output_json)
            prior = conn.execute(
                "SELECT output_sha256 FROM calculation_attempts WHERE run_key_sha256 = ? AND status = 'COMPLETE' LIMIT 1",
                (run_key,),
            ).fetchone()
            if prior is not None and prior["output_sha256"] != output_hash:
                raise RuntimeError("deterministic rerun output differs for the same run key")

            timings = {
                "fixture_load_ms": load_ms,
                "database_snapshot_read_ms": snapshot_read_ms,
                "compute_ms": compute_ms,
            }
            persist_started = time.perf_counter()
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                "UPDATE calculation_attempts SET status = 'COMPLETE', output_json = ?, output_sha256 = ?, finished_at_utc = ? WHERE attempt_id = ?",
                (output_json, output_hash, _utc_now(), attempt_id),
            )
            timings["result_persist_precommit_ms"] = (time.perf_counter() - persist_started) * 1000
            conn.execute(
                "UPDATE calculation_attempts SET timings_json = ? WHERE attempt_id = ?",
                (canonical_json(timings), attempt_id),
            )
            conn.commit()
            # Commit duration is only measurable after this transaction has
            # committed; return it to the caller without implying it is stored.
            timings["result_persist_commit_ms"] = (time.perf_counter() - persist_started) * 1000
            return {
                "attempt_id": attempt_id,
                "run_key_sha256": run_key,
                "snapshot_sha256": snapshot_hash,
                "output_sha256": output_hash,
                "status": "COMPLETE",
                "output": output,
                "timings_ms": timings,
            }
        except Exception as error:
            conn.rollback()
            conn.execute(
                "UPDATE calculation_attempts SET status = 'FAILED', failure_message = ?, finished_at_utc = ? WHERE attempt_id = ?",
                (f"{type(error).__name__}: {error}", _utc_now(), attempt_id),
            )
            conn.commit()
            raise
    finally:
        conn.close()


def database_state(database_path: Path) -> dict[str, Any]:
    conn = connect_database(database_path)
    try:
        version = conn.execute("PRAGMA user_version").fetchone()[0]
        counts = {}
        for table in ("schema_migrations", "fixture_snapshots", "ledger_events", "auxiliary_inputs", "calculation_attempts"):
            try:
                counts[table] = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            except sqlite3.OperationalError:
                counts[table] = None
        return {"schema_version": version, "counts": counts,
                "integrity_check": conn.execute("PRAGMA integrity_check").fetchone()[0]}
    finally:
        conn.close()
