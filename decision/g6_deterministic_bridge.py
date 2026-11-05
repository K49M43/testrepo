"""Fixture-only G6 adapter joining the frozen schedule, lot ledger and CPI ratio.

This first increment deliberately supports one synthetic instrument and one
tax year. It is not a return engine for qualified products or an investor
projection. Losses, cross-tax-year paths, missing prices and actual inputs fail
closed until their separate contracts are implemented and audited.
"""

from __future__ import annotations

import hashlib
import json
from calendar import monthrange
from datetime import date
from decimal import Decimal, localcontext
from pathlib import Path
from typing import Any, Mapping

from after_tax_event_ledger import LedgerEvent, run_ledger, tax_year_for
from g3_goal_hurdle import (
    CONTRACT_PATH,
    DEFAULT_SCHEDULE_PATH,
    read_schedule,
    validate_schedule_contract,
)
from ty2026_27_tax_components import TaxInput


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE = ROOT / "research/stage512/2026-11-05/g6_1/input.json"
DEFAULT_OUTPUT = ROOT / "research/stage512/2026-11-05/g6_1/result.json"
ZERO = Decimal("0")
ONE = Decimal("1")
PRECISION = 50
FIXTURE_LABEL = "SYNTHETIC_FIXTURE_ONLY"


def _d(value: Any, field: str, *, positive: bool = False) -> Decimal:
    try:
        parsed = value if isinstance(value, Decimal) else Decimal(str(value))
    except Exception as error:
        raise ValueError(f"{field} must be decimal text") from error
    if not parsed.is_finite() or (parsed <= ZERO if positive else parsed < ZERO):
        requirement = "positive" if positive else "finite and non-negative"
        raise ValueError(f"{field} must be {requirement}")
    return parsed


def _month_end(month: str) -> date:
    parts = month.split("-")
    if len(parts) != 2:
        raise ValueError(f"invalid calendar month: {month}")
    year, month_number = (int(part) for part in parts)
    if not 1 <= month_number <= 12:
        raise ValueError(f"invalid calendar month: {month}")
    return date(year, month_number, monthrange(year, month_number)[1])


def load_fixture(path: Path = DEFAULT_FIXTURE) -> dict[str, Any]:
    return load_fixture_text(path.read_text(encoding="utf-8"))


def load_fixture_text(text: str) -> dict[str, Any]:
    raw = json.loads(text)
    required = {
        "schema_version", "experiment_id", "input_classification", "terminal_month_index",
        "instrument", "price_path_basis", "scenarios", "costs", "tax_assumptions", "cpi",
    }
    if set(raw) != required:
        raise ValueError(f"fixture fields must match contract; missing={sorted(required-set(raw))}, extra={sorted(set(raw)-required)}")
    if isinstance(raw["schema_version"], bool) or raw["schema_version"] != 1 or raw["input_classification"] != FIXTURE_LABEL:
        raise ValueError("only schema v1 synthetic fixtures are supported")
    if (not isinstance(raw["experiment_id"], str) or not raw["experiment_id"].strip()
            or not isinstance(raw["price_path_basis"], str)
            or not raw["price_path_basis"].startswith("Synthetic ")):
        raise ValueError("experiment ID and explicitly synthetic price-path basis are required")
    return raw


def _validate_fixture(raw: Mapping[str, Any]) -> tuple[Any, dict[str, Any], date, str]:
    with localcontext() as ctx:
        ctx.prec = PRECISION
        schedule = read_schedule(DEFAULT_SCHEDULE_PATH)
        contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        validate_schedule_contract(schedule, contract)
        terminal_index = raw["terminal_month_index"]
        if not isinstance(terminal_index, int) or isinstance(terminal_index, bool) or terminal_index < 1:
            raise ValueError("terminal_month_index must be a positive integer")
        if terminal_index > schedule.max_month:
            raise ValueError("terminal month is outside the frozen contribution schedule")
        base_month = schedule.base_month
        terminal_month = schedule.base_month
        base_year, base_m = (int(item) for item in base_month.split("-"))
        absolute = base_year * 12 + base_m - 1 + terminal_index
        terminal_year, terminal_m0 = divmod(absolute, 12)
        terminal_month = f"{terminal_year:04d}-{terminal_m0 + 1:02d}"
        start_date = _month_end(base_month)
        terminal_date = _month_end(terminal_month)
        tax_year = tax_year_for(start_date)
        if tax_year_for(terminal_date) != tax_year:
            raise ValueError("G6.1 fixture must remain within one Indian tax year")

        instrument = raw["instrument"]
        if not isinstance(instrument, dict) or set(instrument) != {"instrument_id", "tax_classification", "section76_specified_fund_confirmed"}:
            raise ValueError("instrument fields do not match G6.1 fixture contract")
        if not isinstance(instrument["instrument_id"], str) or not instrument["instrument_id"].startswith("SYNTHETIC-"):
            raise ValueError("actual or investable instrument inputs are not supported by G6.1")
        if instrument["tax_classification"] != "section76" or instrument["section76_specified_fund_confirmed"] is not True:
            raise ValueError("G6.1 only supports the explicitly synthetic section 76 fixture branch")

        costs = raw["costs"]
        if set(costs) != {"account_fee_per_contribution_inr", "terminal_transaction_cost_inr", "terminal_cost_deductible_for_tax"}:
            raise ValueError("cost fields do not match G6.1 fixture contract")
        _d(costs["account_fee_per_contribution_inr"], "account_fee_per_contribution_inr")
        _d(costs["terminal_transaction_cost_inr"], "terminal_transaction_cost_inr")
        if costs["terminal_cost_deductible_for_tax"] is not False:
            raise ValueError("tax deductibility is not inferred; this fixture explicitly excludes it")

        tax = raw["tax_assumptions"]
        if not isinstance(tax, dict) or set(tax) != {
            "model_tax_year", "resident_individual", "external_ordinary_income_inr", "rule_set"
        }:
            raise ValueError("tax assumptions do not match G6.1 fixture contract")
        if tax["model_tax_year"] != tax_year or tax["rule_set"] != "TY 2026-27 research component; fixture only":
            raise ValueError("tax year or rule-set is outside this bounded fixture")
        if tax["resident_individual"] is not True:
            raise ValueError("G6.1 requires an explicit synthetic resident-individual tax assumption")
        _d(tax["external_ordinary_income_inr"], "external_ordinary_income_inr")

        cpi = raw["cpi"]
        if set(cpi) != {"classification", "base_month", "base_index", "terminal_month", "terminal_index"}:
            raise ValueError("CPI fields do not match G6.1 fixture contract")
        if cpi["classification"] != FIXTURE_LABEL or cpi["base_month"] != base_month or cpi["terminal_month"] != terminal_month:
            raise ValueError("CPI labels/months must exactly match the synthetic investment dates")
        _d(cpi["base_index"], "base_index", positive=True)
        _d(cpi["terminal_index"], "terminal_index", positive=True)

        scenarios = raw["scenarios"]
        if not isinstance(scenarios, list) or not scenarios:
            raise ValueError("at least one deterministic price-path scenario is required")
        names: set[str] = set()
        for scenario in scenarios:
            if not isinstance(scenario, dict) or set(scenario) != {"scenario_id", "price_by_month_inr"}:
                raise ValueError("scenario fields do not match G6.1 fixture contract")
            if not isinstance(scenario["scenario_id"], str) or not scenario["scenario_id"].strip() or scenario["scenario_id"] in names:
                raise ValueError("scenario IDs must be non-empty and unique")
            names.add(scenario["scenario_id"])
            prices = scenario["price_by_month_inr"]
            if not isinstance(prices, list) or len(prices) != terminal_index + 1:
                raise ValueError("each price path must cover every schedule month from inception through exit")
            for index, price in enumerate(prices):
                _d(price, f"{scenario['scenario_id']}.price_by_month_inr[{index}]", positive=True)
        return schedule, contract, terminal_date, tax_year


def run_scenario(raw: Mapping[str, Any], scenario: Mapping[str, Any]) -> dict[str, Any]:
    with localcontext() as ctx:
        ctx.prec = PRECISION
        schedule, _, terminal_date, tax_year = _validate_fixture(raw)
        terminal_index = raw["terminal_month_index"]
        prices = [_d(value, f"price[{index}]", positive=True)
                  for index, value in enumerate(scenario["price_by_month_inr"])]
        instrument = raw["instrument"]
        costs = raw["costs"]
        account_fee = _d(costs["account_fee_per_contribution_inr"], "account fee")
        exit_fee = _d(costs["terminal_transaction_cost_inr"], "terminal transaction cost")
        events: list[LedgerEvent] = []
        lots: list[tuple[str, Decimal, Decimal]] = []
        sequence = 0
        for month_index in range(terminal_index + 1):
            month = schedule.base_month
            year, month_number = (int(item) for item in month.split("-"))
            absolute = year * 12 + month_number - 1 + month_index
            month_year, month0 = divmod(absolute, 12)
            month_label = f"{month_year:04d}-{month0 + 1:02d}"
            when = _month_end(month_label)
            contribution = schedule.initial_inr if month_index == 0 else schedule.monthly_contributions[month_index]
            if contribution == ZERO:
                continue
            sequence = 1
            is_initial = month_index == 0
            events.append(LedgerEvent(
                event_id=f"{scenario['scenario_id']}-contribution-{month_index:03d}",
                event_date=when, tax_year=tax_year, event_sequence=sequence,
                event_type="initial_contribution" if is_initial else "sip_contribution",
                instrument_id=instrument["instrument_id"], cash_amount_inr=contribution,
                source_or_assumption="Synthetic frozen G3 schedule input; not actual transaction data",
                qualification_status=FIXTURE_LABEL,
            ))
            remaining = contribution
            if account_fee:
                sequence += 1
                events.append(LedgerEvent(
                    event_id=f"{scenario['scenario_id']}-account-fee-{month_index:03d}",
                    event_date=when, tax_year=tax_year, event_sequence=sequence,
                    event_type="fee", instrument_id=instrument["instrument_id"],
                    cash_amount_inr=account_fee,
                    source_or_assumption="Explicit synthetic account-fee assumption; tax basis/deductibility not inferred",
                    qualification_status=FIXTURE_LABEL,
                ))
                remaining -= account_fee
            if remaining <= ZERO:
                raise ValueError("account fee must be less than each scheduled contribution")
            quantity = remaining / prices[month_index]
            lot_id = f"{scenario['scenario_id']}-lot-{month_index:03d}"
            sequence += 1
            events.append(LedgerEvent(
                event_id=f"{scenario['scenario_id']}-acquisition-{month_index:03d}",
                event_date=when, tax_year=tax_year, event_sequence=sequence,
                event_type="acquisition", instrument_id=instrument["instrument_id"],
                cash_amount_inr=remaining,
                source_or_assumption="Synthetic units derived from dated schedule contribution and explicit price mark",
                qualification_status=FIXTURE_LABEL,
                lot_id=lot_id, units=quantity, unit_price_inr=prices[month_index],
            ))
            lots.append((lot_id, quantity, remaining))

        sequence += 1
        events.append(LedgerEvent(
            event_id=f"{scenario['scenario_id']}-terminal-sale", event_date=terminal_date,
            tax_year=tax_year, event_sequence=sequence, event_type="terminal_disposal",
            instrument_id=instrument["instrument_id"], cash_amount_inr=lots[-1][1] * prices[terminal_index],
            source_or_assumption="Synthetic terminal price mark; full forced liquidation fixture",
            qualification_status=FIXTURE_LABEL,
            lot_id=lots[-1][0], units=lots[-1][1], unit_price_inr=prices[terminal_index],
            transaction_cost_inr=exit_fee, deductible_transfer_expenses_inr=ZERO,
            tax_classification=instrument["tax_classification"], tax_classification_confirmed=True,
            section76_specified_fund_confirmed=True,
        ))
        # Liquidate earlier lots at the same terminal mark, each with a distinct
        # same-day sequence; one disposal per lot preserves lot-level tax traces.
        for lot_id, quantity, _ in reversed(lots[:-1]):
            sequence += 1
            events.append(LedgerEvent(
                event_id=f"{scenario['scenario_id']}-terminal-sale-{lot_id}", event_date=terminal_date,
                tax_year=tax_year, event_sequence=sequence, event_type="terminal_disposal",
                instrument_id=instrument["instrument_id"], cash_amount_inr=quantity * prices[terminal_index],
                source_or_assumption="Synthetic terminal price mark; full forced liquidation fixture",
                qualification_status=FIXTURE_LABEL,
                lot_id=lot_id, units=quantity, unit_price_inr=prices[terminal_index],
                transaction_cost_inr=ZERO, deductible_transfer_expenses_inr=ZERO,
                tax_classification=instrument["tax_classification"], tax_classification_confirmed=True,
                section76_specified_fund_confirmed=True,
            ))
        if len({event.event_id for event in events}) != len(events):
            raise AssertionError("adapter generated duplicate event identifiers")
        external_income = _d(raw["tax_assumptions"]["external_ordinary_income_inr"], "external income")
        result = run_ledger(
            events, {}, external_tax_inputs={tax_year: TaxInput(
                ordinary_income=external_income,
                resident_individual=raw["tax_assumptions"]["resident_individual"],
            )},
        )
        if result.capital_loss_trace:
            raise ValueError("realized losses require an explicit, independently qualified G6 loss-allocation contract")
        base_cpi = _d(raw["cpi"]["base_index"], "base CPI", positive=True)
        terminal_cpi = _d(raw["cpi"]["terminal_index"], "terminal CPI", positive=True)
        cpi_factor = terminal_cpi / base_cpi
        net_nominal = result.net_accessible_fixture_wealth_inr
        if net_nominal is None:
            raise AssertionError("ledger did not produce bounded fixture net wealth")
        real_value = net_nominal / cpi_factor
        acquisitions = {event.lot_id: event for event in events if event.event_type == "acquisition"}
        lot_disposal_trace = []
        for event in events:
            if event.event_type != "terminal_disposal":
                continue
            acquisition = acquisitions[event.lot_id]
            disposed_units = event.units
            proceeds = event.cash_amount_inr
            tax_basis = (
                acquisition.cash_amount_inr - acquisition.transaction_cost_inr
                + acquisition.tax_basis_addition_inr
            ) * disposed_units / acquisition.units
            deductible_expenses = event.deductible_transfer_expenses_inr
            lot_disposal_trace.append({
                "event_id": event.event_id,
                "lot_id": event.lot_id,
                "acquired_date": acquisition.event_date.isoformat(),
                "disposed_date": event.event_date.isoformat(),
                "units_disposed": str(disposed_units),
                "unit_price_inr": str(event.unit_price_inr),
                "proceeds_inr": str(proceeds),
                "tax_basis_removed_inr": str(tax_basis),
                "deductible_transfer_expenses_inr": str(deductible_expenses),
                "signed_realized_result_inr": str(proceeds - tax_basis - deductible_expenses),
            })
        total_contributions = sum(
            (schedule.initial_inr if month_index == 0 else schedule.monthly_contributions[month_index]
             for month_index in range(terminal_index + 1)), ZERO
        )
        return {
            "scenario_id": scenario["scenario_id"],
            "classification": FIXTURE_LABEL,
            "instrument_id": instrument["instrument_id"],
            "start_date": _month_end(schedule.base_month).isoformat(),
            "terminal_date": terminal_date.isoformat(),
            "tax_year": tax_year,
            "contribution_months_including_initial": terminal_index + 1,
            "contributions_inr": str(total_contributions),
            "gross_terminal_sale_proceeds_before_terminal_cost_and_tax_inr": str(result.gross_terminal_wealth_inr + result.transaction_costs_inr),
            "gross_terminal_wealth_after_recorded_costs_before_tax_inr": str(result.gross_terminal_wealth_inr),
            "recorded_account_fees_inr": str(result.other_fees_inr),
            "recorded_transaction_costs_inr": str(result.transaction_costs_inr),
            "incremental_fixture_tax_inr": str(result.incremental_portfolio_tax_inr),
            "net_nominal_after_costs_and_incremental_fixture_tax_inr": str(net_nominal),
            "cpi": {
                "classification": FIXTURE_LABEL,
                "base_month": raw["cpi"]["base_month"],
                "base_index": str(base_cpi),
                "terminal_month": raw["cpi"]["terminal_month"],
                "terminal_index": str(terminal_cpi),
                "factor": str(cpi_factor),
            },
            "net_real_2026_base_fixture_value_inr": str(real_value),
            "event_count": result.event_count,
            "reconciliation_residual_inr": str(result.reconciliation_residual_inr),
            "tax_year_trace": result.tax_years,
            "tax_event_trace": result.tax_event_trace,
            "lot_disposal_trace": lot_disposal_trace,
            "qualification_limits": [
                "Synthetic price paths and synthetic CPI levels are not market history or an inflation forecast.",
                "TY 2026-27 component tax is held fixed for this one synthetic tax year only.",
                "No withholding, returns, investor tax profile, or future-law assumptions are inferred.",
                "Recorded account/transaction costs are fixture assumptions; tax deductibility is not inferred.",
                "Full forced liquidation is a mechanics case, not a 2036 exit recommendation.",
                "No probability, portfolio ranking, suitability or investment authorization is produced.",
            ],
            "investment_authorization": "NO_GO",
        }


def run_fixture(path: Path = DEFAULT_FIXTURE) -> dict[str, Any]:
    raw = load_fixture(path)
    _, _, _, _ = _validate_fixture(raw)
    results = [run_scenario(raw, scenario) for scenario in raw["scenarios"]]
    tracked = {
        "input_fixture": path,
        "cashflow_schedule": DEFAULT_SCHEDULE_PATH,
        "g3_contract": CONTRACT_PATH,
        "bridge_code": Path(__file__).resolve(),
        "event_ledger_code": Path(__file__).resolve().with_name("after_tax_event_ledger.py"),
        "tax_component_code": Path(__file__).resolve().with_name("ty2026_27_tax_components.py"),
        "g3_hurdle_code": Path(__file__).resolve().with_name("g3_goal_hurdle.py"),
    }
    source_hashes = {
        key: {"path": source.resolve().relative_to(ROOT).as_posix(),
              "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}
        for key, source in tracked.items()
    }
    run_key_material = json.dumps({"experiment_id": raw["experiment_id"], "source_hashes": source_hashes},
                                  sort_keys=True, separators=(",", ":"))
    return {
        "schema_version": 1,
        "record_id": "g6-1-deterministic-bridge-v1",
        "experiment_id": raw["experiment_id"],
        "classification": FIXTURE_LABEL,
        "scenario_count": len(results),
        "run_key": hashlib.sha256(run_key_material.encode("utf-8")).hexdigest(),
        "source_hashes": source_hashes,
        "scenarios": results,
        "decision_scope": "G6.1 deterministic integration mechanics only; not decision-grade G6",
        "investment_authorization": "NO_GO",
    }


def main() -> None:
    output = run_fixture()
    DEFAULT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_OUTPUT.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({
        "record_id": output["record_id"],
        "scenario_count": output["scenario_count"],
        "scenarios": [{"id": row["scenario_id"], "gross_after_costs_before_tax": row["gross_terminal_wealth_after_recorded_costs_before_tax_inr"],
                       "incremental_tax": row["incremental_fixture_tax_inr"], "net_nominal": row["net_nominal_after_costs_and_incremental_fixture_tax_inr"],
                       "net_real": row["net_real_2026_base_fixture_value_inr"], "residual": row["reconciliation_residual_inr"]}
                      for row in output["scenarios"]],
        "output": DEFAULT_OUTPUT.relative_to(ROOT).as_posix(),
        "authorization": "NO_GO",
    }, indent=2))


if __name__ == "__main__":
    main()
