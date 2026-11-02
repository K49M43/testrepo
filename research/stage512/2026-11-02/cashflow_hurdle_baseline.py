"""Deterministic 2036 goal hurdle, before taxes, fees, and trading costs.

Uses the mandate's illustrative end-of-month SIP convention and an October 2026
starting reference. This is an arithmetic baseline, not a return forecast or
portfolio probability model. Actual dates remain unconfirmed.
"""

from __future__ import annotations

import argparse
import csv
from decimal import Decimal
from pathlib import Path


INITIAL_INR = Decimal("4200000")
STARTING_SIP_INR = Decimal("25000")
STEP_UP = Decimal("0.10")
STEP_EVERY_MONTHS = 12
REAL_FLOOR_INR = Decimal("9000000")
BASE_MONTH = "2026-10"
HORIZONS_MONTHS = (120, 122)
INFLATION_CASES = (Decimal("0.04"), Decimal("0.06"), Decimal("0.08"))


def contribution_schedule(months: int) -> list[Decimal]:
    """End-of-month mathematical schedule; transaction rounding is not assumed."""
    if months <= 0:
        raise ValueError("months must be positive")
    rows = []
    for index in range(months):
        step = index // STEP_EVERY_MONTHS
        amount = STARTING_SIP_INR * (Decimal("1") + STEP_UP) ** step
        rows.append(amount)
    return rows


def future_value(monthly_rate: float, contributions: list[Decimal]) -> float:
    """Initial capital at t=0 plus end-of-month SIPs through the horizon."""
    n = len(contributions)
    value = float(INITIAL_INR) * (1.0 + monthly_rate) ** n
    for index, amount in enumerate(contributions):
        periods = n - index - 1
        value += float(amount) * (1.0 + monthly_rate) ** periods
    return value


def solve_monthly_hurdle(target_inr: float, contributions: list[Decimal]) -> float:
    """Find a constant monthly return matching the nominal target."""
    low, high = -0.99, 1.0
    if future_value(low, contributions) > target_inr:
        return low
    while future_value(high, contributions) < target_inr:
        high = 2.0 * high + 1.0
        if high > 1_000_000:
            raise ArithmeticError("unable to bracket nominal-return hurdle")
    for _ in range(240):
        middle = (low + high) / 2.0
        if future_value(middle, contributions) < target_inr:
            low = middle
        else:
            high = middle
    return (low + high) / 2.0


def write_cashflow(path: Path, max_months: int) -> None:
    rows = contribution_schedule(max_months)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(("month_index", "calendar_month", "initial_investment_inr", "monthly_contribution_inr", "cumulative_contributions_inr"))
        writer.writerow((0, BASE_MONTH, str(INITIAL_INR), "0.00", str(INITIAL_INR)))
        cumulative = INITIAL_INR
        year, month = map(int, BASE_MONTH.split("-"))
        for index, amount in enumerate(rows, start=1):
            absolute_month = year * 12 + (month - 1) + index
            contribution_year, contribution_month0 = divmod(absolute_month, 12)
            contribution_month = contribution_month0 + 1
            cumulative += amount
            writer.writerow((index, f"{contribution_year:04d}-{contribution_month:02d}", "0.000000000", f"{amount:.9f}", f"{cumulative:.9f}"))


def write_hurdles(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(("base_month", "horizon_months", "terminal_month", "contribution_count", "total_contributions_inr", "annual_inflation_scenario", "real_floor_inr_2026", "nominal_floor_inr", "required_monthly_return_before_tax_costs", "required_effective_annual_return_before_tax_costs"))
        year, month = map(int, BASE_MONTH.split("-"))
        for months in HORIZONS_MONTHS:
            contributions = contribution_schedule(months)
            absolute_month = year * 12 + (month - 1) + months
            terminal_year, terminal_month0 = divmod(absolute_month, 12)
            terminal_month = terminal_month0 + 1
            for inflation in INFLATION_CASES:
                factor = (1.0 + float(inflation)) ** (months / 12.0)
                nominal_goal = float(REAL_FLOOR_INR) * factor
                monthly_hurdle = solve_monthly_hurdle(nominal_goal, contributions)
                writer.writerow((BASE_MONTH, months, f"{terminal_year:04d}-{terminal_month:02d}", months, f"{sum(contributions, Decimal('0')):.2f}", f"{inflation:.4f}", f"{REAL_FLOOR_INR:.2f}", f"{nominal_goal:.2f}", f"{monthly_hurdle:.10f}", f"{(1.0 + monthly_hurdle) ** 12 - 1.0:.10f}"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent)
    args = parser.parse_args()
    write_cashflow(args.output_dir / "cashflow_hurdle_monthly_2026-10_base.csv", max(HORIZONS_MONTHS))
    write_hurdles(args.output_dir / "cashflow_hurdle_sensitivity.csv")
    print(f"Wrote deterministic cashflow and hurdle schedules under {args.output_dir}")


if __name__ == "__main__":
    main()
