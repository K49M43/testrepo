"""Screen the mandate's 5% gold-to-silver switch with matched AMFI NAV dates."""
from __future__ import annotations

import argparse
import csv
import json
import runpy
from datetime import date
from decimal import Decimal, localcontext
from math import prod
from pathlib import Path

from g3_goal_hurdle import (
    CONTRACT_PATH, DEFAULT_SCHEDULE_PATH, ROOT, cpi_factor, future_value,
    normalized_text_and_sha256, read_schedule, solve_monthly_hurdle,
    validate_schedule_contract,
)


D = Decimal
ONE = D(1)
G5 = ROOT / "research/stage512/2026-11-05/g5_4/audit_g5_candidate_nav_history.py"
OUT = (ROOT / "research/stage512/2026-11-25/g6_3/icici_silver_etf_source_gate"
       / "silver_nav_comparison_v1.json")
CODES = {"equity": "147625", "gilt": "150681", "gold": "113049", "silver": "149464"}
CUTOFF = date(2026, 10, 30)
COST_BPS = (0, 25, 50, 100, 200)
SWITCH_WEIGHT = D("0.05")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def inr(value):
    rounded = value.quantize(D("0.01"))
    return str(abs(rounded) if rounded == 0 else rounded)


def month_endpoints(days):
    return {(day.year, day.month): day for day in sorted(days)}


def load_navs():
    require(__debug__, "The reused G5.4 source audit requires assertions")
    g5 = runpy.run_path(str(G5))
    navs, sources = {}, {}
    for asset, code in CODES.items():
        spec = g5["SPECS"][code]
        sources[asset] = g5["audit"](code, spec)
        require(sources[asset]["status"] == "PASS_RAW_TO_NORMALIZED_LINEAGE_AND_DATE_CONTINUITY",
                f"G5 lineage failed for {asset}")
        with (g5["ROOT"] / f"nav_{code}_daily.csv").open(encoding="utf-8", newline="") as f:
            navs[asset] = {
                date.fromisoformat(row["date"]): D(row["nav"])
                for row in csv.DictReader(f)
            }
    return navs, sources


def align(navs):
    individual = {asset: month_endpoints(series) for asset, series in navs.items()}
    months = set.intersection(*(set(series) for series in individual.values()))
    shared = month_endpoints(day for day in set.intersection(*(set(s) for s in navs.values()))
                             if day <= CUTOFF)
    require(months == set(shared), "Missing shared NAV date within a common month")
    endpoints = sorted(shared.values())
    require(endpoints[-1] == CUTOFF and all(day >= date(2022, 10, 10) for day in endpoints),
            "Unexpected sample bounds or HDFC Gold unit-split exposure")
    require(all(b.year * 12 + b.month - (a.year * 12 + a.month) == 1
                for a, b in zip(endpoints, endpoints[1:])), "Gap between NAV intervals")
    moved = [{"common_observed_date": day.isoformat(),
              "individual_month_ends": {a: series[(day.year, day.month)].isoformat()
                                        for a, series in individual.items()}}
             for day in endpoints
             if any(series[(day.year, day.month)] != day for series in individual.values())]
    interval_gross = [{asset: series[end] / series[start] for asset, series in navs.items()}
                      for start, end in zip(endpoints, endpoints[1:])]
    return endpoints, moved, interval_gross


def terminal_values(path, initial, contributions):
    """Value unit-weight sleeves before adding the portfolio's initial/SIP weights."""
    marks = dict.fromkeys(CODES, initial)
    for month, row in enumerate(path, 1):
        marks = {asset: marks[asset] * gross + contributions[month]
                 for asset, gross in row.items()}
    return marks


def summarize(marks, weights, factor, floor):
    gross_silver = sum(weights[a] * marks[a] for a in marks)
    baseline = gross_silver + SWITCH_WEIGHT * (marks["gold"] - marks["silver"])
    outcomes = {}
    for bps in COST_BPS:
        cost_fraction = D(bps) / 10_000
        cost = SWITCH_WEIGHT * marks["silver"] * (ONE - (ONE - cost_fraction) ** 2)
        real = (gross_silver - cost) / factor
        outcomes[str(bps)] = {
            "silver_cost_terminal_effect_nominal_inr": inr(cost),
            "silver_after_test_cost_nominal_inr": inr(gross_silver - cost),
            "silver_real_before_tax_inr": inr(real),
            "silver_shortfall_before_tax_inr": inr(max(D(0), floor - real)),
            "silver_minus_baseline_real_inr": inr(real - baseline / factor),
        }
    breakeven = (ONE - (marks["gold"] / marks["silver"]).sqrt()) * 10_000
    return {
        "baseline_nominal_before_cost_and_tax_inr": inr(baseline),
        "silver_nominal_before_cost_and_tax_inr": inr(gross_silver),
        "baseline_real_before_cost_and_tax_inr": inr(baseline / factor),
        "baseline_shortfall_before_cost_and_tax_inr": inr(max(D(0), floor - baseline / factor)),
        "breakeven_per_side_bps_if_zero_cost_silver_leads": inr(breakeven) if breakeven > 0 else None,
        "by_incremental_silver_cost_per_side_bps": outcomes,
    }


def build_record():
    navs, sources = load_navs()
    endpoints, moved, history = align(navs)
    _, schedule_hash = normalized_text_and_sha256(DEFAULT_SCHEDULE_PATH)
    contract_text, contract_hash = normalized_text_and_sha256(CONTRACT_PATH)
    contract = json.loads(contract_text)
    schedule = read_schedule()
    validate_schedule_contract(schedule, contract)
    horizon = contract["illustrative_cashflow_fixture"]["primary_contribution_count"]
    floor = D(next(row["real_amount_inr_2026"] for row in contract["targets"]
                   if row["target_id"] == "planning_floor"))
    inflation = D(contract["inflation_scenarios"]["planning_case_fraction"])
    factor = cpi_factor(inflation, horizon)
    mandate = json.loads((ROOT / "config/investment_mandate_2036.json").read_text(encoding="utf-8"),
                         parse_float=D)
    original = mandate["modeling"]["baseline_existing_research_weights"]
    weights = {"equity": original["nifty500_equity"],
               **{a: original[a] for a in ("gilt", "gold", "silver")}}
    require(sum(weights.values()) == ONE and weights["silver"] == SWITCH_WEIGHT,
            "The mandate weights no longer match the gold-to-silver experiment")
    initial, contributions = schedule.initial_inr, schedule.monthly_contributions
    target = floor * factor
    hurdle = solve_monthly_hurdle(target, initial, contributions, horizon)
    quiet = dict.fromkeys(CODES, ONE + hurdle)
    reference = terminal_values([quiet] * horizon, initial, contributions)
    require(abs(reference["gold"] - future_value(hurdle, initial, contributions, horizon)) < D("1e-15")
            and abs(reference["gold"] - target) < D("0.000001"), "Neutral cashflow check failed")
    control = summarize(reference, weights, factor, floor)
    require(control["baseline_real_before_cost_and_tax_inr"] == inr(floor)
            and control["by_incremental_silver_cost_per_side_bps"]["0"]["silver_real_before_tax_inr"] == inr(floor),
            "Identical sleeves must yield identical zero-cost outcomes at the hurdle")

    windows = []
    for start in range(len(history) - 11):
        block = history[start:start + 12]
        gross = {a: prod(row[a] for row in block) for a in CODES}
        baseline_return = sum(weights[a] * gross[a] for a in CODES if a != "silver")
        baseline_return += SWITCH_WEIGHT * gross["gold"] - ONE
        windows.append({
            "first_nav_date": endpoints[start].isoformat(),
            "last_nav_date": endpoints[start + 12].isoformat(),
            "baseline_12_interval_nav_return": str(round(baseline_return, 10)),
            "silver_12_interval_nav_return": str(round(
                baseline_return + SWITCH_WEIGHT * (gross["silver"] - gross["gold"]), 10)),
            "placements": {
                placement: summarize(terminal_values(path, initial, contributions), weights, factor, floor)
                for placement, path in (("first_12_months", block + [quiet] * (horizon - 12)),
                                        ("last_12_months", [quiet] * (horizon - 12) + block))
            },
        })
    require(bool(windows), "No contiguous 12-month sample available")

    # Explicit hypothetical challenge. Equal monthly changes compound to each stated one-year shock.
    joint_crash = {"equity": D("-0.25"), "gilt": D("-0.05"), "gold": D("-0.10"), "silver": D("-0.30")}
    crash_month = {a: (ONE + r) ** (ONE / 12) for a, r in joint_crash.items()}
    crash = terminal_values([quiet] * (horizon - 12) + [crash_month] * 12, initial, contributions)
    return {
        "experiment_id": "G6.3-SILVER-NAV-COMPARISON-2026-11-25-V1",
        "status": "PROVISIONAL_NAV_COMPARISON_ONLY",
        "investment_authorization": "NO_GO",
        "input_sources": sources,
        "g3_schedule_normalized_sha256": schedule_hash,
        "g3_contract_normalized_sha256": contract_hash,
        "experiment_code_normalized_sha256": normalized_text_and_sha256(Path(__file__))[1],
        "alignment": {"shared_endpoints": [d.isoformat() for d in endpoints],
                      "intervals": len(history), "differing_individual_month_ends": moved},
        "assumptions": {
            "weights_with_silver": {a: str(w) for a, w in weights.items()},
            "baseline_gold_weight": str(weights["gold"] + SWITCH_WEIGHT),
            "baseline_silver_weight": "0",
            "portfolio_rule": "Allocate initial and end-of-month contributions at target weights, then hold until liquidation",
            "cashflow_months": horizon, "initial_inr": inr(initial),
            "contributions_inr": inr(sum(contributions[i] for i in range(1, horizon + 1))),
            "annual_inflation": str(inflation), "floor_inr_2026": inr(floor),
            "quiet_months_equal_all_asset_return_annualized": str(round((ONE + hurdle) ** 12 - ONE, 10)),
            "quiet_months_purpose": "Arithmetic hurdle to isolate sequence effects, not a forecast",
            "incremental_silver_cost_per_side_bps": COST_BPS,
            "cost_convention": "One proportional haircut to each silver purchase budget and terminal sale proceeds; other trading costs omitted",
            "tax_scope": "Before investor taxes; no after-tax floor or probability claim",
        },
        "neutral_hurdle_control": control,
        "historical_stress_windows": windows,
        "synthetic_joint_crash_at_exit": {"one_year_asset_returns": {a: str(r) for a, r in joint_crash.items()},
                                          "portfolio_outcomes": summarize(crash, weights, factor, floor)},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify the frozen result instead of writing it")
    args = parser.parse_args()
    with localcontext() as ctx:
        ctx.prec = 50
        record = build_record()
    payload = json.dumps(record, indent=2) + "\n"
    if args.check:
        require(OUT.read_text(encoding="utf-8") == payload, "Frozen Silver ETF result differs")
    else:
        OUT.write_text(payload, encoding="utf-8", newline="\n")
    print(f"Silver NAV comparison reproduced: {record['alignment']['intervals']} matched intervals, "
          f"{len(record['historical_stress_windows'])} rolling blocks. NO_GO.")


if __name__ == "__main__":
    main()
