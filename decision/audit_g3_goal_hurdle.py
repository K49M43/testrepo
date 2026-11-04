"""Independent arithmetic challenge for the G3 outcome and hurdle contract."""

from __future__ import annotations

import csv
import json
from decimal import Decimal, ROUND_HALF_EVEN, localcontext
from pathlib import Path

from g3_goal_hurdle import (
    CONTRACT_PATH,
    DEFAULT_OUTPUT_PATH,
    DEFAULT_SCHEDULE_PATH,
    PRECISION,
    ZERO,
    canonical_json,
    cpi_factor,
    future_value,
    generate,
    normalized_text_and_sha256,
    read_schedule,
    solve_monthly_hurdle,
)


D = Decimal
ONE = D("1")


def independent_cpi_factor(inflation: Decimal, months: int) -> Decimal:
    """Use exp/ln rather than the production fractional-power operation."""
    return (((ONE + inflation).ln()) * D(months) / D(12)).exp()


def independent_future_value(monthly_return: Decimal, initial: Decimal,
                              contributions: dict[int, Decimal], horizon: int) -> Decimal:
    """Month-by-month accumulation, independent of production exponentiation."""
    balance = initial
    for month in range(1, horizon + 1):
        balance = balance * (ONE + monthly_return) + contributions[month]
    return balance


def independent_solve(target: Decimal, initial: Decimal,
                      contributions: dict[int, Decimal], horizon: int) -> Decimal:
    if target <= contributions[horizon]:
        raise ValueError("independent hurdle has no finite solution above -100%")
    low, high = D("-1"), ONE
    while independent_future_value(high, initial, contributions, horizon) < target:
        high = high * 2 + ONE
    for _ in range(240):
        middle = (low + high) / 2
        if independent_future_value(middle, initial, contributions, horizon) < target:
            low = middle
        else:
            high = middle
        if high - low < D("1e-35"):
            break
    return (low + high) / 2


def independent_annual_return(monthly_return: Decimal) -> Decimal:
    return (ONE + monthly_return) ** 12 - ONE


def read_legacy_hurdles(path: Path) -> dict[tuple[int, Decimal], Decimal]:
    legacy = Path(path).with_name("cashflow_hurdle_sensitivity.csv")
    with legacy.open("r", encoding="utf-8", newline="") as stream:
        return {
            (int(row["horizon_months"]), D(row["annual_inflation_scenario"])):
            D(row["required_effective_annual_return_before_tax_costs"])
            for row in csv.DictReader(stream)
        }


def audit() -> dict[str, object]:
    with localcontext() as context:
        context.prec = PRECISION
        context.rounding = ROUND_HALF_EVEN
        schedule = read_schedule(DEFAULT_SCHEDULE_PATH)
        assert schedule.cumulative_contributions[120] == D("8981227.380300000")
        assert schedule.cumulative_contributions[122] == D("9110914.503305000")
        boundary_contributions = {
            m: schedule.monthly_contributions[m] for m in range(1, 121)
        }
        assert future_value(
            D("-1"), schedule.initial_inr, boundary_contributions, 120
        ) == boundary_contributions[120]
        try:
            solve_monthly_hurdle(
                boundary_contributions[120], schedule.initial_inr, boundary_contributions, 120
            )
        except ValueError:
            pass
        else:
            raise AssertionError("target at/below final contribution must not invent a finite hurdle")
        try:
            cpi_factor(D("-1"), 120)
        except ValueError:
            pass
        else:
            raise AssertionError("-100% CPI is outside the valid compound-factor domain")

        contract_text, contract_hash = normalized_text_and_sha256(CONTRACT_PATH)
        contract = json.loads(contract_text)
        output_text, _ = normalized_text_and_sha256(DEFAULT_OUTPUT_PATH)
        stored = json.loads(output_text)
        regenerated = generate(DEFAULT_SCHEDULE_PATH, CONTRACT_PATH)
        assert canonical_json(stored) == canonical_json(regenerated)
        assert stored["contract_sha256"] == contract_hash
        assert stored["cashflow_schedule_sha256"] == normalized_text_and_sha256(DEFAULT_SCHEDULE_PATH)[1]
        assert len(stored["results"]) == 12
        assert stored["authorization"] == "NO-GO"
        assert stored["limitations"]["interpretation"].startswith("pre-tax/pre-cost arithmetic hurdle")
        assert contract["targets"][0]["real_amount_inr_2026"] == "9000000"
        assert contract["targets"][1]["real_amount_inr_2026"] == "10000000"
        assert all(target["guarantee"] is False for target in contract["targets"])

        legacy = read_legacy_hurdles(DEFAULT_SCHEDULE_PATH)
        maximum_nominal_residual = ZERO
        maximum_real_residual = ZERO
        maximum_real_hurdle_crosscheck = ZERO
        maximum_target_derivative_residual = ZERO
        maximum_cpi_derivative_residual = ZERO

        for row in stored["results"]:
            horizon = row["horizon_months"]
            inflation = D(row["annual_inflation_scenario"])
            target_real = D(row["real_target_inr_2026"])
            target_nominal = D(row["nominal_target_inr"])
            nominal_monthly = D(row["required_monthly_nominal_return_before_tax_costs"])
            nominal_annual = D(row["required_effective_annual_nominal_return_before_tax_costs"])
            real_annual = D(row["required_effective_annual_real_return_before_tax_costs"])
            direct_real_annual = D(row["independently_solved_effective_annual_real_return"])
            contributions = {m: schedule.monthly_contributions[m] for m in range(1, horizon + 1)}

            independent_terminal_cpi = independent_cpi_factor(inflation, horizon)
            independent_target_nominal = target_real * independent_terminal_cpi
            assert abs(independent_target_nominal - target_nominal) < D("0.005")
            independent_nominal_hurdle = independent_solve(
                independent_target_nominal, schedule.initial_inr, contributions, horizon
            )
            assert abs(independent_nominal_hurdle - nominal_monthly) < D("1e-15")
            nominal_rebuilt = independent_future_value(
                nominal_monthly, schedule.initial_inr, contributions, horizon
            )
            nominal_residual = abs(nominal_rebuilt - independent_target_nominal)
            maximum_nominal_residual = max(maximum_nominal_residual, nominal_residual)
            assert nominal_residual < D("0.01")

            real_initial = schedule.initial_inr
            real_flows = {
                m: contributions[m] / independent_cpi_factor(inflation, m)
                for m in range(1, horizon + 1)
            }
            independent_real_monthly = independent_solve(
                target_real, real_initial, real_flows, horizon
            )
            independently_solved_real_annual = independent_annual_return(independent_real_monthly)
            real_residual = abs(
                independent_future_value(independent_real_monthly, real_initial, real_flows, horizon)
                - target_real
            )
            maximum_real_residual = max(maximum_real_residual, real_residual)
            maximum_real_hurdle_crosscheck = max(
                maximum_real_hurdle_crosscheck,
                abs(independently_solved_real_annual - direct_real_annual),
                abs(real_annual - direct_real_annual),
            )
            assert real_residual < D("0.01")
            assert abs(independently_solved_real_annual - direct_real_annual) < D("1e-13")
            assert abs(real_annual - direct_real_annual) < D("1e-13")
            assert abs((ONE + nominal_annual) / (ONE + inflation) - ONE - real_annual) < D("1e-13")

            if row["target_id"] == "planning_floor":
                old = legacy[(horizon, inflation)]
                assert abs(nominal_annual - old) < D("1e-9")

            # Derive the target derivative from the implicit function and
            # challenge it with a centered finite difference in target amount.
            perturbation = D("1000")
            up = independent_solve(target_nominal + perturbation, schedule.initial_inr, contributions, horizon)
            down = independent_solve(target_nominal - perturbation, schedule.initial_inr, contributions, horizon)
            finite_diff_target = (
                independent_annual_return(up) - independent_annual_return(down)
            ) / (2 * perturbation) * D(100000) * D(100)
            stated_target = D(row["derivatives"]["annual_nominal_return_percentage_points_per_100000_inr_target"])
            target_derivative_residual = abs(finite_diff_target - stated_target)
            maximum_target_derivative_residual = max(maximum_target_derivative_residual, target_derivative_residual)
            assert target_derivative_residual < D("0.00000001")

            # Re-solve with +/- 1 bp CPI to independently challenge the
            # analytic chain-rule sensitivity, reported per 1 pp CPI move.
            epsilon = D("0.0001")
            annual_hurdles = []
            for shifted_inflation in (inflation - epsilon, inflation + epsilon):
                shifted_target = target_real * independent_cpi_factor(shifted_inflation, horizon)
                shifted_monthly = independent_solve(
                    shifted_target, schedule.initial_inr, contributions, horizon
                )
                annual_hurdles.append(independent_annual_return(shifted_monthly))
            finite_diff_cpi = (annual_hurdles[1] - annual_hurdles[0]) / (2 * epsilon)
            stated_cpi = D(row["derivatives"][
                "annual_nominal_hurdle_percentage_points_change_per_1_percentage_point_cpi_increase"
            ])
            cpi_derivative_residual = abs(finite_diff_cpi - stated_cpi)
            maximum_cpi_derivative_residual = max(maximum_cpi_derivative_residual, cpi_derivative_residual)
            assert cpi_derivative_residual < D("0.0001")

        # Floor and stretch compare the same cashflow and inflation policy;
        # both nominal targets and nominal hurdles must rise with the goal.
        lookup = {
            (row["target_id"], row["horizon_months"], row["annual_inflation_scenario"]): row
            for row in stored["results"]
        }
        for horizon in (120, 122):
            for inflation in ("0.040000", "0.060000", "0.080000"):
                floor = lookup[("planning_floor", horizon, inflation)]
                stretch = lookup[("stretch_goal", horizon, inflation)]
                assert D(stretch["nominal_target_inr"]) > D(floor["nominal_target_inr"])
                assert D(stretch["required_effective_annual_nominal_return_before_tax_costs"]) > D(
                    floor["required_effective_annual_nominal_return_before_tax_costs"]
                )

        floor_120_6 = lookup[("planning_floor", 120, "0.060000")]
        stretch_120_6 = lookup[("stretch_goal", 120, "0.060000")]
        assert floor_120_6["nominal_target_inr"] == "16117629.27"
        assert stretch_120_6["nominal_target_inr"] == "17908476.97"
        assert abs(
            D(stretch_120_6["required_effective_annual_nominal_return_before_tax_costs"])
            - D("0.0971166853555328")
        ) < D("1e-15")

        return {
            "audit": "PASS",
            "scenario_count": len(stored["results"]),
            "legacy_floor_hurdles_reconciled": "PASS; Decimal results match prior float baseline within 1e-9 annual-return fraction",
            "independent_real_and_nominal_reconstruction": "PASS; separate monthly recurrence and exp/ln CPI calculations",
            "target_and_cpi_derivatives": "PASS; implicit derivatives match centered finite differences",
            "max_nominal_terminal_residual_inr": str(maximum_nominal_residual),
            "max_real_terminal_residual_inr": str(maximum_real_residual),
            "max_real_hurdle_crosscheck_difference": str(maximum_real_hurdle_crosscheck),
            "max_target_derivative_difference": str(maximum_target_derivative_residual),
            "max_cpi_derivative_difference": str(maximum_cpi_derivative_residual),
            "objective_semantics": "PASS; ₹90L floor and ₹1Cr stretch remain distinct, non-guaranteed real targets",
            "authorization": "NO-GO",
        }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, ensure_ascii=True))
