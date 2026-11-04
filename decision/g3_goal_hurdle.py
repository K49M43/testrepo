"""Derive deterministic 2036 target hurdles from the frozen dated cashflows.

These are gross arithmetic requirements before tax, fees, and trading costs.
They do not estimate returns, probabilities, or investment suitability.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP, localcontext
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "research/stage512/2026-11-04/g3_outcome_contract_v1.json"
DEFAULT_SCHEDULE_PATH = ROOT / "research/stage512/2026-11-02/cashflow_hurdle_monthly_2026-10_base.csv"
DEFAULT_OUTPUT_PATH = ROOT / "research/stage512/2026-11-04/g3_deterministic_hurdles_v1.json"
PRECISION = 50
ZERO = Decimal("0")
ONE = Decimal("1")
CENT = Decimal("0.01")


@dataclass(frozen=True)
class CashflowSchedule:
    base_month: str
    initial_inr: Decimal
    monthly_contributions: Mapping[int, Decimal]
    cumulative_contributions: Mapping[int, Decimal]

    @property
    def max_month(self) -> int:
        return max(self.monthly_contributions)


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def normalized_text_and_sha256(path: Path) -> tuple[str, str]:
    text = path.read_bytes().decode("utf-8")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return normalized, digest


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _month_after(base_month: str, offset: int) -> str:
    year, month = (int(part) for part in base_month.split("-"))
    ordinal = year * 12 + month - 1 + offset
    out_year, out_month0 = divmod(ordinal, 12)
    return f"{out_year:04d}-{out_month0 + 1:02d}"


def _decimal_cell(value: str, field: str) -> Decimal:
    try:
        parsed = Decimal(value)
    except Exception as error:
        raise ValueError(f"{field} must be decimal text") from error
    if not parsed.is_finite():
        raise ValueError(f"{field} must be finite")
    return parsed


def parse_schedule_text(schedule_text: str) -> CashflowSchedule:
    from io import StringIO

    reader = csv.DictReader(StringIO(schedule_text))
    required = {
        "month_index", "calendar_month", "initial_investment_inr",
        "monthly_contribution_inr", "cumulative_contributions_inr",
    }
    if reader.fieldnames is None or set(reader.fieldnames) != required:
        raise ValueError("cashflow schedule columns do not match the frozen contract")
    rows = list(reader)
    if not rows:
        raise ValueError("cashflow schedule must not be empty")

    monthly: dict[int, Decimal] = {}
    cumulative: dict[int, Decimal] = {}
    initial: Decimal | None = None
    base_month = rows[0]["calendar_month"]
    running_total = ZERO
    for expected_index, row in enumerate(rows):
        try:
            month_index = int(row["month_index"])
        except ValueError as error:
            raise ValueError(f"month_index {expected_index} must be an integer") from error
        if month_index != expected_index or row["calendar_month"] != _month_after(base_month, month_index):
            raise ValueError("cashflow month indices and calendar months must be contiguous")
        initial_amount = _decimal_cell(row["initial_investment_inr"], f"row {month_index} initial")
        contribution = _decimal_cell(row["monthly_contribution_inr"], f"row {month_index} contribution")
        recorded_total = _decimal_cell(row["cumulative_contributions_inr"], f"row {month_index} cumulative")
        if initial_amount < ZERO or contribution < ZERO:
            raise ValueError("cash contributions cannot be negative")
        if month_index == 0:
            initial = initial_amount
            if contribution != ZERO:
                raise ValueError("month 0 must not include a recurring contribution")
        elif initial_amount != ZERO:
            raise ValueError("initial contribution is permitted only at month 0")
        running_total += initial_amount + contribution
        if recorded_total != running_total:
            raise ValueError(f"row {month_index} cumulative contributions do not reconcile")
        monthly[month_index] = contribution
        cumulative[month_index] = recorded_total
    if initial is None or initial <= ZERO:
        raise ValueError("month 0 must contain a positive initial contribution")
    if monthly[0] != ZERO:
        raise ValueError("month 0 contribution must be zero")
    return CashflowSchedule(base_month, initial, monthly, cumulative)


def read_schedule(path: Path = DEFAULT_SCHEDULE_PATH) -> CashflowSchedule:
    schedule_text, _ = normalized_text_and_sha256(path)
    with localcontext() as context:
        context.prec = PRECISION
        context.rounding = ROUND_HALF_EVEN
        return parse_schedule_text(schedule_text)


def validate_schedule_contract(schedule: CashflowSchedule, contract: Mapping[str, Any]) -> None:
    cashflow = contract["illustrative_cashflow_fixture"]
    if schedule.base_month != cashflow["base_month"]:
        raise ValueError("cashflow schedule base month does not match outcome contract")
    if schedule.initial_inr != Decimal(cashflow["initial_contribution_inr_at_month_0"]):
        raise ValueError("initial contribution does not match outcome contract")
    count = cashflow["step_up_after_contributions_count"]
    initial_sip = Decimal(cashflow["first_monthly_contribution_inr"])
    step_up = Decimal(cashflow["annual_step_up_fraction"])
    for month in range(1, schedule.max_month + 1):
        step = (month - 1) // count
        expected = (initial_sip * (ONE + step_up) ** step).quantize(
            Decimal("0.000000001"), rounding=ROUND_HALF_EVEN
        )
        if schedule.monthly_contributions[month] != expected:
            raise ValueError(f"month {month} contribution does not match step-up contract")
    if schedule.max_month < cashflow["sensitivity_contribution_count"]:
        raise ValueError("cashflow schedule does not cover the declared sensitivity horizon")
    for horizon_key, month_key in (
        ("primary_contribution_count", "primary_terminal_month"),
        ("sensitivity_contribution_count", "sensitivity_terminal_month"),
    ):
        horizon = cashflow[horizon_key]
        if _month_after(schedule.base_month, horizon) != cashflow[month_key]:
            raise ValueError(f"{horizon_key} does not match its declared terminal month")


def cpi_factor(annual_inflation: Decimal, months: int) -> Decimal:
    if annual_inflation <= Decimal("-1") or months < 0:
        raise ValueError("inflation must exceed -100% and month count cannot be negative")
    return (ONE + annual_inflation) ** (Decimal(months) / Decimal(12))


def future_value(monthly_return: Decimal, initial: Decimal,
                 contributions: Mapping[int, Decimal], horizon: int) -> Decimal:
    if monthly_return <= Decimal("-1"):
        if monthly_return < Decimal("-1"):
            raise ValueError("monthly return cannot be below -100%")
    if horizon < 1:
        raise ValueError("horizon must be positive")
    growth = ONE + monthly_return
    value = initial * (growth ** horizon)
    for month in range(1, horizon + 1):
        periods = horizon - month
        value += contributions[month] if periods == 0 else contributions[month] * (growth ** periods)
    return value


def solve_monthly_hurdle(target: Decimal, initial: Decimal,
                         contributions: Mapping[int, Decimal], horizon: int) -> Decimal:
    """Solve the unique rate greater than -100% for positive dated cashflows."""
    if target <= contributions[horizon]:
        raise ValueError("target must exceed the final end-of-month contribution for a finite hurdle")
    low = Decimal("-1")
    high = ONE
    if future_value(low, initial, contributions, horizon) > target:
        raise ValueError("target is below the limiting value of the cashflow schedule")
    while future_value(high, initial, contributions, horizon) < target:
        high = high * 2 + ONE
        if high > Decimal("1000"):
            raise ArithmeticError("unable to bracket the required return")
    for _ in range(240):
        middle = (low + high) / 2
        if future_value(middle, initial, contributions, horizon) < target:
            low = middle
        else:
            high = middle
        if high - low < Decimal("1e-35"):
            break
    return (low + high) / 2


def future_value_derivative(monthly_return: Decimal, initial: Decimal,
                            contributions: Mapping[int, Decimal], horizon: int) -> Decimal:
    """d(FV)/d(monthly return) for the fixed contribution schedule."""
    growth = ONE + monthly_return
    derivative = Decimal(horizon) * initial * (growth ** (horizon - 1))
    for month in range(1, horizon + 1):
        periods = horizon - month
        if periods:
            derivative += Decimal(periods) * contributions[month] * (growth ** (periods - 1))
    return derivative


def _fmt(value: Decimal, places: int = 24) -> str:
    quantum = Decimal(1).scaleb(-places)
    return format(value.quantize(quantum, rounding=ROUND_HALF_EVEN), "f")


def _fmt_inr(value: Decimal) -> str:
    return format(value.quantize(CENT, rounding=ROUND_HALF_UP), "f")


def build_results(schedule: CashflowSchedule, contract: Mapping[str, Any],
                  schedule_sha256: str, contract_sha256: str,
                  code_path: Path = Path(__file__)) -> dict[str, Any]:
    target_rows = contract["targets"]
    inflation_rows = contract["inflation_scenarios"]["annual_compound_fractions"]
    horizons = (
        contract["illustrative_cashflow_fixture"]["primary_contribution_count"],
        contract["illustrative_cashflow_fixture"]["sensitivity_contribution_count"],
    )
    results: list[dict[str, Any]] = []
    with localcontext() as context:
        context.prec = PRECISION
        context.rounding = ROUND_HALF_EVEN
        for horizon in horizons:
            if horizon > schedule.max_month:
                raise ValueError(f"schedule does not cover horizon {horizon}")
            terminal_month = _month_after(schedule.base_month, horizon)
            contributions = {month: schedule.monthly_contributions[month] for month in range(1, horizon + 1)}
            total_contributed = schedule.initial_inr + sum(contributions.values(), ZERO)
            for target_row in target_rows:
                real_target = Decimal(target_row["real_amount_inr_2026"])
                for inflation_text in inflation_rows:
                    inflation = Decimal(inflation_text)
                    terminal_cpi = cpi_factor(inflation, horizon)
                    nominal_target = real_target * terminal_cpi
                    nominal_monthly_hurdle = solve_monthly_hurdle(
                        nominal_target, schedule.initial_inr, contributions, horizon
                    )
                    nominal_annual_hurdle = (ONE + nominal_monthly_hurdle) ** 12 - ONE
                    real_annual_equivalent = (
                        (ONE + nominal_annual_hurdle) / (ONE + inflation) - ONE
                    )

                    real_initial = schedule.initial_inr
                    real_contributions = {
                        month: contributions[month] / cpi_factor(inflation, month)
                        for month in range(1, horizon + 1)
                    }
                    real_monthly_hurdle = solve_monthly_hurdle(
                        real_target, real_initial, real_contributions, horizon
                    )
                    real_annual_direct = (ONE + real_monthly_hurdle) ** 12 - ONE

                    derivative_fv = future_value_derivative(
                        nominal_monthly_hurdle, schedule.initial_inr, contributions, horizon
                    )
                    annual_return_derivative_per_inr = (
                        Decimal(12) * (ONE + nominal_monthly_hurdle) ** 11 / derivative_fv
                    )
                    nominal_target_change_per_inflation_pp = (
                        nominal_target * Decimal(horizon) / Decimal(12)
                        / (ONE + inflation) * Decimal("0.01")
                    )
                    annual_hurdle_change_pp_per_inflation_pp = (
                        annual_return_derivative_per_inr
                        * nominal_target_change_per_inflation_pp
                        * Decimal(100)
                    )
                    nominal_reconstruction = future_value(
                        nominal_monthly_hurdle, schedule.initial_inr, contributions, horizon
                    )
                    real_reconstruction = future_value(
                        real_monthly_hurdle, real_initial, real_contributions, horizon
                    )

                    results.append({
                        "target_id": target_row["target_id"],
                        "target_role": target_row["role"],
                        "horizon_months": horizon,
                        "contribution_count": horizon,
                        "terminal_month": terminal_month,
                        "annual_inflation_scenario": _fmt(inflation, 6),
                        "real_target_inr_2026": _fmt_inr(real_target),
                        "terminal_cpi_factor": _fmt(terminal_cpi, 18),
                        "nominal_target_inr": _fmt_inr(nominal_target),
                        "total_contributions_inr": _fmt_inr(total_contributed),
                        "required_monthly_nominal_return_before_tax_costs": _fmt(nominal_monthly_hurdle, 18),
                        "required_effective_annual_nominal_return_before_tax_costs": _fmt(nominal_annual_hurdle, 16),
                        "required_effective_annual_real_return_before_tax_costs": _fmt(real_annual_equivalent, 16),
                        "independently_solved_effective_annual_real_return": _fmt(real_annual_direct, 16),
                        "nominal_terminal_reconstruction_inr": _fmt_inr(nominal_reconstruction),
                        "real_terminal_reconstruction_inr_2026": _fmt_inr(real_reconstruction),
                        "derivatives": {
                            "annual_nominal_return_percentage_points_per_100000_inr_target": _fmt(
                                annual_return_derivative_per_inr * Decimal(100000) * Decimal(100), 14
                            ),
                            "nominal_target_inr_change_per_1_percentage_point_cpi_increase": _fmt_inr(
                                nominal_target_change_per_inflation_pp
                            ),
                            "annual_nominal_hurdle_percentage_points_change_per_1_percentage_point_cpi_increase": _fmt(
                                annual_hurdle_change_pp_per_inflation_pp, 12
                            ),
                        },
                        "hurdle_status": "ARITHMETIC_ONLY_PRE_TAX_PRE_COST",
                        "probability_or_forecast": False,
                    })

    return {
        "artifact_id": "g3-deterministic-goal-hurdles",
        "artifact_version": "1.0.0",
        "contract_sha256": contract_sha256,
        "cashflow_schedule_sha256": schedule_sha256,
        "calculation_code_sha256": normalized_text_and_sha256(code_path)[1],
        "decimal_context": {
            "decimal_precision": PRECISION,
            "decimal_rounding": ROUND_HALF_EVEN,
        },
        "method": {
            "nominal_equation": "FV(r,n) = initial*(1+r)^n + sum(contribution_m*(1+r)^(n-m)); solve FV = real_target*(1+inflation)^(n/12)",
            "real_equation": "Deflate each dated contribution by (1+inflation)^(m/12), then independently solve FV(real_r,n) = real_target",
            "annualization": "effective annual return = (1+monthly return)^12 - 1",
            "hurdle_sensitivity": "implicit derivative d(r_annual)/d(target) = 12*(1+r_monthly)^11 / d(FV)/d(r_monthly)",
            "cpi_sensitivity": "chain rule: d(target_nominal)/d(inflation) = target_nominal*(n/12)/(1+inflation)",
        },
        "limitations": contract["deterministic_hurdle_scope"],
        "results": results,
        "authorization": "NO-GO",
    }


def generate(schedule_path: Path = DEFAULT_SCHEDULE_PATH,
             contract_path: Path = CONTRACT_PATH) -> dict[str, Any]:
    schedule_text, schedule_hash = normalized_text_and_sha256(schedule_path)
    contract_text, contract_hash = normalized_text_and_sha256(contract_path)
    contract = json.loads(contract_text)
    with localcontext() as context:
        context.prec = PRECISION
        context.rounding = ROUND_HALF_EVEN
        schedule = parse_schedule_text(schedule_text)
        validate_schedule_contract(schedule, contract)
        return build_results(schedule, contract, schedule_hash, contract_hash)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schedule", type=Path, default=DEFAULT_SCHEDULE_PATH)
    parser.add_argument("--contract", type=Path, default=CONTRACT_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args()
    output = generate(args.schedule, args.contract)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({
        "status": "PASS",
        "output": str(args.output),
        "scenario_count": len(output["results"]),
        "authorization": output["authorization"],
    }, indent=2))


if __name__ == "__main__":
    main()
