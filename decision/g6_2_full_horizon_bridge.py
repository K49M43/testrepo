"""Synthetic full-horizon G6.2 schedule-to-after-tax bridge.

All marks, tax contexts, fees, and inflation inputs are mechanical fixtures.
The TY 2026-27 tax component is deliberately repeated across later years only
as an integration assumption; this module is not a future-law forecast.
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
    CONTRACT_PATH, DEFAULT_SCHEDULE_PATH, cpi_factor, read_schedule,
    validate_schedule_contract,
)
from ty2026_27_tax_components import TaxInput

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE = ROOT / "research/stage512/2026-11-05/g6_2/input.json"
DEFAULT_OUTPUT = ROOT / "research/stage512/2026-11-05/g6_2/result.json"
ZERO = Decimal("0")
ONE = Decimal("1")
PRECISION = 50
FIXTURE_LABEL = "SYNTHETIC_FIXTURE_ONLY"
TAX_RULE_SET = "TY 2026-27 component repeated for fixture mechanics only; not future law"


def _d(value: Any, field: str) -> Decimal:
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except Exception as error:
        raise ValueError(f"{field} must be decimal text") from error
    if not result.is_finite():
        raise ValueError(f"{field} must be finite")
    return result


def _month_label(base_month: str, offset: int) -> str:
    year, month = (int(part) for part in base_month.split("-"))
    absolute = year * 12 + month - 1 + offset
    out_year, out_month0 = divmod(absolute, 12)
    return f"{out_year:04d}-{out_month0 + 1:02d}"


def _month_end(base_month: str, offset: int) -> date:
    label = _month_label(base_month, offset)
    year, month = (int(part) for part in label.split("-"))
    return date(year, month, monthrange(year, month)[1])


def _validate_fixture_schema(raw: Any) -> dict[str, Any]:
    required = {
        "schema_version", "experiment_id", "input_classification", "horizons_months",
        "instrument", "price_path_basis", "starting_mark_inr", "scenarios", "costs",
        "tax_assumptions", "cpi",
    }
    if not isinstance(raw, dict) or set(raw) != required:
        raise ValueError("fixture fields must match the G6.2 schema")
    if isinstance(raw["schema_version"], bool) or raw["schema_version"] != 1:
        raise ValueError("only schema v1 is supported")
    if raw["input_classification"] != FIXTURE_LABEL:
        raise ValueError("only explicitly synthetic fixture data is supported")
    if not isinstance(raw["experiment_id"], str) or not raw["experiment_id"].strip():
        raise ValueError("experiment ID is required")
    if raw["horizons_months"] != [120, 122]:
        raise ValueError("G6.2 supports only the frozen 120- and 122-month horizons")
    if not isinstance(raw["price_path_basis"], str) or not raw["price_path_basis"].startswith("Synthetic "):
        raise ValueError("price path must be explicitly synthetic")
    return raw


def load_fixture_text(text: str) -> dict[str, Any]:
    return _validate_fixture_schema(json.loads(text))


def load_fixture(path: Path = DEFAULT_FIXTURE) -> dict[str, Any]:
    return load_fixture_text(path.read_text(encoding="utf-8"))


def _validate_fixture(raw: Mapping[str, Any]):
    _validate_fixture_schema(raw)
    with localcontext() as ctx:
        ctx.prec = PRECISION
        schedule = read_schedule(DEFAULT_SCHEDULE_PATH)
        contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        validate_schedule_contract(schedule, contract)
        if schedule.max_month < 122:
            raise ValueError("frozen schedule does not cover the 122-month sensitivity")
        if raw["horizons_months"] != [
            contract["illustrative_cashflow_fixture"]["primary_contribution_count"],
            contract["illustrative_cashflow_fixture"]["sensitivity_contribution_count"],
        ]:
            raise ValueError("fixture horizons do not match the G3 contract")
        instrument = raw["instrument"]
        if not isinstance(instrument, dict) or set(instrument) != {
            "instrument_id", "tax_classification", "section76_specified_fund_confirmed"
        }:
            raise ValueError("instrument fields do not match G6.2 contract")
        if (not isinstance(instrument["instrument_id"], str)
                or not instrument["instrument_id"].startswith("SYNTHETIC-")
                or instrument["tax_classification"] != "section76"
                or instrument["section76_specified_fund_confirmed"] is not True):
            raise ValueError("only the explicit synthetic specified-fund branch is supported")
        _d(raw["starting_mark_inr"], "starting_mark_inr")
        if _d(raw["starting_mark_inr"], "starting_mark_inr") <= ZERO:
            raise ValueError("starting mark must be positive")
        scenarios = raw["scenarios"]
        if not isinstance(scenarios, list) or len(scenarios) != 2:
            raise ValueError("G6.2 requires two deterministic scenarios")
        ids = set()
        for scenario in scenarios:
            if not isinstance(scenario, dict) or set(scenario) != {"scenario_id", "monthly_mark_growth_rate"}:
                raise ValueError("scenario fields do not match G6.2 contract")
            if not isinstance(scenario["scenario_id"], str) or not scenario["scenario_id"].strip() or scenario["scenario_id"] in ids:
                raise ValueError("scenario IDs must be unique and non-empty")
            ids.add(scenario["scenario_id"])
            if _d(scenario["monthly_mark_growth_rate"], "monthly_mark_growth_rate") <= Decimal("-1"):
                raise ValueError("monthly growth rate must be greater than -100%")
        costs = raw["costs"]
        if not isinstance(costs, dict) or set(costs) != {
            "account_fee_per_contribution_inr", "terminal_transaction_cost_inr",
            "terminal_cost_deductible_for_tax",
        }:
            raise ValueError("cost fields do not match G6.2 contract")
        if _d(costs["account_fee_per_contribution_inr"], "account fee") < ZERO:
            raise ValueError("account fee must be non-negative")
        if _d(costs["terminal_transaction_cost_inr"], "terminal transaction cost") < ZERO:
            raise ValueError("terminal transaction cost must be non-negative")
        if costs["terminal_cost_deductible_for_tax"] is not False:
            raise ValueError("sale-cost deductibility is explicit and false in this fixture")
        tax = raw["tax_assumptions"]
        if not isinstance(tax, dict) or set(tax) != {
            "source_component_tax_year", "resident_individual", "external_ordinary_income_by_tax_year", "rule_set"
        }:
            raise ValueError("tax assumptions do not match G6.2 contract")
        if tax["source_component_tax_year"] != "2026-27" or tax["rule_set"] != TAX_RULE_SET:
            raise ValueError("tax component cannot be promoted to future statutory law")
        if tax["resident_individual"] is not True:
            raise ValueError("an explicit synthetic resident-individual assumption is required")
        all_dates = [_month_end(schedule.base_month, month) for month in range(123)]
        tax_years = sorted({tax_year_for(when) for when in all_dates})
        yearly_income = tax["external_ordinary_income_by_tax_year"]
        if not isinstance(yearly_income, dict) or set(yearly_income) != set(tax_years):
            raise ValueError("explicit external tax inputs are required for every modeled tax year")
        for year, income in yearly_income.items():
            if _d(income, f"external ordinary income {year}") < ZERO:
                raise ValueError("external ordinary income must be non-negative")
        cpi = raw["cpi"]
        if not isinstance(cpi, dict) or set(cpi) != {
            "classification", "base_month", "annual_inflation_fraction"
        }:
            raise ValueError("CPI fields do not match G6.2 contract")
        if cpi["classification"] != FIXTURE_LABEL or cpi["base_month"] != schedule.base_month:
            raise ValueError("CPI must be synthetic and anchored to the exact G3 base month")
        inflation = _d(cpi["annual_inflation_fraction"], "annual inflation")
        if inflation <= Decimal("-1"):
            raise ValueError("synthetic annual inflation must exceed -100%")
        for year in (120, 122):
            if schedule.cumulative_contributions[year] <= ZERO:
                raise ValueError("horizon schedule is missing cumulative contributions")
        return schedule, contract, tax_years


def run_scenario(raw: Mapping[str, Any], horizon: int, scenario: Mapping[str, Any]) -> dict[str, Any]:
    with localcontext() as ctx:
        ctx.prec = PRECISION
        schedule, _, modeled_tax_years = _validate_fixture(raw)
        if horizon not in (120, 122):
            raise ValueError("only the 120- and 122-month G3 horizons are supported")
        growth = _d(scenario["monthly_mark_growth_rate"], "monthly mark growth")
        starting_mark = _d(raw["starting_mark_inr"], "starting mark")
        account_fee = _d(raw["costs"]["account_fee_per_contribution_inr"], "account fee")
        exit_fee = _d(raw["costs"]["terminal_transaction_cost_inr"], "terminal transaction cost")
        instrument = raw["instrument"]
        events: list[LedgerEvent] = []
        lot_acquisitions: dict[str, LedgerEvent] = {}
        seq_by_date: dict[date, int] = {}
        prices: list[Decimal] = []
        lots: list[str] = []

        for month in range(horizon + 1):
            when = _month_end(schedule.base_month, month)
            mark = starting_mark * (ONE + growth) ** month
            if mark <= ZERO:
                raise ValueError("generated synthetic price mark must remain positive")
            prices.append(mark)
            contribution = schedule.initial_inr if month == 0 else schedule.monthly_contributions[month]
            if contribution == ZERO:
                continue
            seq = 1
            scenario_id = scenario["scenario_id"]
            event_year = tax_year_for(when)
            events.append(LedgerEvent(
                event_id=f"{scenario_id}-h{horizon}-contribution-{month:03d}", event_date=when,
                tax_year=event_year, event_sequence=seq, event_type="initial_contribution" if month == 0 else "sip_contribution",
                instrument_id=instrument["instrument_id"], cash_amount_inr=contribution,
                source_or_assumption="Synthetic dated G3 schedule input; no actual transaction data",
                qualification_status=FIXTURE_LABEL,
            ))
            seq += 1
            remaining = contribution
            if account_fee:
                events.append(LedgerEvent(
                    event_id=f"{scenario_id}-h{horizon}-account-fee-{month:03d}", event_date=when,
                    tax_year=event_year, event_sequence=seq, event_type="fee",
                    instrument_id=instrument["instrument_id"], cash_amount_inr=account_fee,
                    source_or_assumption="Synthetic account-fee fixture; excluded from tax basis",
                    qualification_status=FIXTURE_LABEL,
                ))
                remaining -= account_fee
                seq += 1
            if remaining <= ZERO:
                raise ValueError("account fee must be less than every scheduled contribution")
            units = remaining / mark
            lot_id = f"{scenario_id}-h{horizon}-lot-{month:03d}"
            acquisition = LedgerEvent(
                event_id=f"{scenario_id}-h{horizon}-acquisition-{month:03d}", event_date=when,
                tax_year=event_year, event_sequence=seq, event_type="acquisition",
                instrument_id=instrument["instrument_id"], cash_amount_inr=remaining,
                source_or_assumption="Synthetic units from G3 cashflow and generated monthly mark",
                qualification_status=FIXTURE_LABEL, lot_id=lot_id, units=units, unit_price_inr=mark,
            )
            events.append(acquisition)
            lot_acquisitions[lot_id] = acquisition
            lots.append(lot_id)
            seq_by_date[when] = seq

        terminal_date = _month_end(schedule.base_month, horizon)
        terminal_mark = prices[-1]
        for lot_id in reversed(lots):
            acquisition = lot_acquisitions[lot_id]
            seq = seq_by_date.get(terminal_date, 3) + 1
            seq_by_date[terminal_date] = seq
            fee = exit_fee if lot_id == lots[-1] else ZERO
            events.append(LedgerEvent(
                event_id=f"{scenario['scenario_id']}-h{horizon}-terminal-sale-{lot_id}",
                event_date=terminal_date, tax_year=tax_year_for(terminal_date), event_sequence=seq,
                event_type="terminal_disposal", instrument_id=instrument["instrument_id"],
                cash_amount_inr=acquisition.units * terminal_mark,
                source_or_assumption="Synthetic terminal mark; full forced liquidation fixture",
                qualification_status=FIXTURE_LABEL, lot_id=lot_id, units=acquisition.units,
                unit_price_inr=terminal_mark, transaction_cost_inr=fee,
                deductible_transfer_expenses_inr=ZERO,
                tax_classification=instrument["tax_classification"], tax_classification_confirmed=True,
                section76_specified_fund_confirmed=True,
            ))
        tax_inputs = {
            year: TaxInput(
                ordinary_income=_d(raw["tax_assumptions"]["external_ordinary_income_by_tax_year"][year], f"external income {year}"),
                resident_individual=raw["tax_assumptions"]["resident_individual"],
            ) for year in modeled_tax_years
        }
        result = run_ledger(events, {}, external_tax_inputs=tax_inputs)
        if result.capital_loss_trace:
            raise ValueError("realized losses require the separately qualified explicit G6 loss-allocation contract")
        if result.ending_market_value_inr != ZERO or result.open_lots:
            raise AssertionError("full liquidation did not close every lot")
        cpi_factor_value = cpi_factor(_d(raw["cpi"]["annual_inflation_fraction"], "annual inflation"), horizon)
        net_nominal = result.net_accessible_fixture_wealth_inr
        if net_nominal is None:
            raise AssertionError("ledger did not produce bounded synthetic net wealth")
        acquisitions = {event.lot_id: event for event in events if event.event_type == "acquisition"}
        disposal_trace = []
        for event in events:
            if event.event_type != "terminal_disposal":
                continue
            acquisition = acquisitions[event.lot_id]
            basis_removed = acquisition.cash_amount_inr * event.units / acquisition.units
            disposal_trace.append({
                "event_id": event.event_id, "lot_id": event.lot_id,
                "acquired_date": acquisition.event_date.isoformat(), "disposed_date": event.event_date.isoformat(),
                "acquired_tax_year": acquisition.tax_year, "disposal_tax_year": event.tax_year,
                "units_disposed": str(event.units), "unit_price_inr": str(event.unit_price_inr),
                "proceeds_inr": str(event.cash_amount_inr), "tax_basis_removed_inr": str(basis_removed),
                "deductible_transfer_expenses_inr": str(event.deductible_transfer_expenses_inr),
                "signed_realized_result_inr": str(event.cash_amount_inr - basis_removed - event.deductible_transfer_expenses_inr),
            })
        all_contributions = schedule.cumulative_contributions[horizon]
        return {
            "horizon_months": horizon, "scenario_id": scenario["scenario_id"],
            "classification": FIXTURE_LABEL, "instrument_id": instrument["instrument_id"],
            "start_date": _month_end(schedule.base_month, 0).isoformat(),
            "terminal_date": terminal_date.isoformat(),
            "monthly_contribution_count": horizon,
            "lot_count_including_initial": len(lots),
            "tax_year_count": len(modeled_tax_years), "modeled_tax_years": modeled_tax_years,
            "contributions_inr": str(all_contributions),
            "gross_terminal_sale_proceeds_before_terminal_cost_and_tax_inr": str(result.gross_terminal_wealth_inr + result.transaction_costs_inr),
            "gross_terminal_wealth_after_recorded_costs_before_tax_inr": str(result.gross_terminal_wealth_inr),
            "recorded_account_fees_inr": str(result.other_fees_inr),
            "recorded_transaction_costs_inr": str(result.transaction_costs_inr),
            "tax_rule_set": TAX_RULE_SET,
            "tax_year_trace": result.tax_years,
            "tax_event_trace": result.tax_event_trace,
            "incremental_fixture_tax_inr": str(result.incremental_portfolio_tax_inr),
            "net_nominal_after_costs_and_incremental_fixture_tax_inr": str(net_nominal),
            "cpi": {
                "classification": FIXTURE_LABEL, "base_month": raw["cpi"]["base_month"],
                "terminal_month": _month_label(schedule.base_month, horizon),
                "annual_inflation_fraction": str(_d(raw["cpi"]["annual_inflation_fraction"], "annual inflation")),
                "factor": str(cpi_factor_value),
            },
            "net_real_2026_base_fixture_value_inr": str(net_nominal / cpi_factor_value),
            "lot_disposal_trace": disposal_trace,
            "event_count": result.event_count,
            "reconciliation_residual_inr": str(result.reconciliation_residual_inr),
            "qualification_limits": [
                "All prices, fees, tax contexts, and inflation are synthetic deterministic mechanics inputs.",
                "TY 2026-27 tax components are repeated in later modeled FYs solely as a fixture rule, not future law.",
                "External ordinary income is synthetic fixture context and is not an investor tax profile.",
                "No distributions, reinvestment, loss relief, flexible exit, or actual product execution costs are modeled.",
                "No probability, candidate ranking, personal outcome, recommendation, or investment authorization is produced.",
            ],
            "investment_authorization": "NO_GO",
        }


def run_fixture(path: Path = DEFAULT_FIXTURE) -> dict[str, Any]:
    raw = load_fixture(path)
    schedule, _, _ = _validate_fixture(raw)
    results = [run_scenario(raw, horizon, scenario)
               for horizon in raw["horizons_months"] for scenario in raw["scenarios"]]
    tracked = {
        "input_fixture": path,
        "cashflow_schedule": DEFAULT_SCHEDULE_PATH,
        "g3_contract": CONTRACT_PATH,
        "bridge_code": Path(__file__).resolve(),
        "event_ledger_code": Path(__file__).resolve().with_name("after_tax_event_ledger.py"),
        "capital_loss_schedule_code": Path(__file__).resolve().with_name("capital_gain_loss_schedule.py"),
        "tax_component_code": Path(__file__).resolve().with_name("ty2026_27_tax_components.py"),
        "g3_hurdle_code": Path(__file__).resolve().with_name("g3_goal_hurdle.py"),
    }
    source_hashes = {
        key: {"path": source.resolve().relative_to(ROOT).as_posix(),
              "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}
        for key, source in tracked.items()
    }
    key_material = json.dumps({"experiment_id": raw["experiment_id"], "source_hashes": source_hashes},
                              sort_keys=True, separators=(",", ":"))
    return {
        "schema_version": 1, "record_id": "g6-2-full-horizon-bridge-v1",
        "experiment_id": raw["experiment_id"], "classification": FIXTURE_LABEL,
        "scenario_count": len(results),
        "run_key": hashlib.sha256(key_material.encode("utf-8")).hexdigest(),
        "source_hashes": source_hashes, "scenarios": results,
        "decision_scope": "G6.2 full-horizon deterministic synthetic integration only; not decision-grade G6",
        "investment_authorization": "NO_GO",
    }


def main() -> None:
    output = run_fixture()
    DEFAULT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_OUTPUT.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({
        "record_id": output["record_id"], "scenario_count": output["scenario_count"],
        "scenarios": [{"horizon": row["horizon_months"], "scenario": row["scenario_id"],
                       "contributions": row["contributions_inr"], "gross_after_costs": row["gross_terminal_wealth_after_recorded_costs_before_tax_inr"],
                       "tax": row["incremental_fixture_tax_inr"], "net_nominal": row["net_nominal_after_costs_and_incremental_fixture_tax_inr"],
                       "net_real": row["net_real_2026_base_fixture_value_inr"], "residual": row["reconciliation_residual_inr"]}
                      for row in output["scenarios"]],
        "authorization": "NO_GO",
    }, indent=2))


if __name__ == "__main__":
    main()
