"""Run the frozen G6.3 WP3 allocation stress protocol without probability claims."""
from __future__ import annotations

import argparse
import json
from datetime import date, timedelta
from decimal import localcontext
from functools import cache
from pathlib import Path

from audit_g6_3_exact_date_coverage import load_marks, provenance
from g6_3_wp2_dated import (
    ACCRUAL_CASES, AUCTION, BASE_INPUT, CASHFLOW_PATH, CONTRACT_PATH, COVERAGE, DEFAULT_SCHEDULE_PATH,
    D, IDS, INPUT as WP2_INPUT, ONE, ROOT, SBI_HOLDINGS, SOVEREIGN_INPUT, ZERO, Policy, bond_terms,
    cpi_factor, growth, pct, read, read_schedule, reference_funding, require, rounded, simulate,
    validate_schedule_contract,
)


DIR = ROOT / "research/g6_3/2026-11-27-wp3-allocation-stress"
PROTOCOL = DIR / "protocol_v1.json"
RESULTS = DIR / "results_v1.json"
FROZEN_PROTOCOL_COMMIT = "9cb2a3b543f1fa94d7cdc85e957d424383132510"
RESIDUAL = D("0.00000001")


def portfolio_weights(mix, gilt):
    return {gilt if name == "gilt" else name: D(value) for name, value in mix.items()}


def drawdown(snapshots):
    """End-of-month unitized NAV. Remove contributions before chaining returns."""
    level = peak = ONE
    worst = ZERO
    previous = ZERO
    max_on = None
    for day, value, contribution in snapshots:
        require(value > ZERO and contribution >= ZERO
                and (value > contribution if previous else contribution > ZERO),
                "invalid marked wealth or external flow")
        level *= (value - contribution) / previous if previous else value / contribution
        peak = max(peak, level)
        drop = ONE - level / peak
        if drop > worst:
            worst, max_on = drop, day
        previous = value
    return {"percent": rounded(worst * 100, "0.0001"), "on": max_on.isoformat() if max_on else None}


def snapshots(trace, funding, marks, terminal):
    """Rebuild marked cash, open lots and net sale receivables from WP2 events."""
    cash = ZERO
    lots, pending = {}, {}
    rows = iter(trace)
    row = next(rows, None)
    output = []
    for day, contribution in funding:
        funded = ZERO
        while row is not None and row["date"] <= day.isoformat():
            kind, delta = row["event"], D(row["cash_delta"])
            cash += delta
            if kind == "acquisition":
                lots[row["lot"]] = row["asset"], D(row["units"])
            elif kind in ("sale", "maturity"):
                asset, held = lots[row["lot"]]
                remaining = held - D(row["units"])
                require(remaining >= ZERO, "negative units in marked snapshot")
                if remaining:
                    lots[row["lot"]] = asset, remaining
                else:
                    del lots[row["lot"]]
                pending[str(row["id"])] = D(row["proceeds"]) - D(row["fee"])
            elif kind == "cash_release":
                require(abs(pending.pop(row["trade_event"]) - delta) < RESIDUAL, "cash release disagrees with net claim")
            elif kind == "contribution":
                require(row["date"] == day.isoformat(), "funding omitted from snapshot schedule")
                funded += delta
            elif kind == "withdrawal":
                raise ValueError("withdrawals are outside this monthly drawdown specification")
            row = next(rows, None)
        require(funded == contribution, "snapshot funding mismatch")
        values = {asset: marks[asset](day) for asset in {asset for asset, _ in lots.values()}}
        total = cash + sum(pending.values(), ZERO) + sum((units * values[asset] for asset, units in lots.values()), ZERO)
        output.append((day, total, funded))
    require(row is None and not lots and not pending and abs(cash - terminal) < RESIDUAL,
            "marked terminal balance or settlement differs from dated engine")
    return output


def mark_path(level, annual, first, jump=None, multiplier=ONE, maturity=None):
    @cache
    def mark(day):
        value = level * growth(annual, first, day)
        if jump is None or day < jump:
            return value
        if maturity is None:
            return value * multiplier
        remaining = max(0, (maturity - day).days)
        return value * (ONE - (ONE - multiplier) * D(remaining) / (maturity - jump).days)

    return mark


def matched_dates(coverage, spec, funding_start):
    endpoints = coverage["nav_replay_panels"][spec["panel"]]["latest_common_observed_endpoints"]
    start, count = spec["first_interval"], spec["interval_count"]
    observed = [date.fromisoformat(day) for day in endpoints[start:start + count + 1]]
    require(start >= 0 and count > 0 and len(observed) == count + 1
            and observed[-1] < funding_start and all(
                (b.year - a.year) * 12 + b.month - a.month == 1 and b > a
                for a, b in zip(observed, observed[1:])), "history has gaps, missing observations or look-ahead")
    return observed


def track(case, funding, weights, policy, marks, maturities, bond, costs, inflation, *, historical=False):
    actual = simulate(funding, weights, policy, marks, maturities, bond, costs)
    before_tax = simulate(funding, weights, policy, marks, maturities, bond, costs, apply_tax=False)
    after_tax = actual["cash"]
    months = len(funding) - 1
    real = after_tax / cpi_factor(inflation, months)
    require(ZERO < after_tax <= before_tax["cash"] + RESIDUAL, "invalid dated tax or wealth ordering")
    return {**case, "payments": months, "end": funding[-1][0].isoformat(), "inflation": str(inflation),
            "contributions": rounded(sum(amount for _, amount in funding)),
            "pre_tax_nominal_after_product_costs": rounded(before_tax["cash"]),
            "modeled_tax_set_aside": rounded(actual["total_tax"]), "after_tax_nominal": rounded(after_tax),
            "after_tax_real": rounded(real), "xirr_nominal_after_modeled_tax": actual["xirr"],
            "floor_shortfall": None if historical else rounded(max(ZERO, D(9_000_000) - real)),
            "stretch_shortfall": None if historical else rounded(max(ZERO, D(10_000_000) - real)),
            "gain_loss_offsets": rounded(sum((D(row["amount_inr"]) for year in actual["tax_years"].values()
                                            for row in year["offsets"]), ZERO)),
            "monthly_max_drawdown": drawdown(snapshots(actual["trace"], funding, marks, after_tax)),
            "trace_events": len(actual["trace"])}


def build():
    protocol, base, cfg, coverage = map(read, (PROTOCOL, BASE_INPUT, WP2_INPUT, COVERAGE))
    contract, terms, holdings = map(read, (CONTRACT_PATH, SOVEREIGN_INPUT, SBI_HOLDINGS))
    schedule = read_schedule(DEFAULT_SCHEDULE_PATH)
    validate_schedule_contract(schedule, contract)
    evidence = protocol["evidence"]
    require(all(coverage[key] == value for key, value in evidence.items()), "stale evidence dispositions")
    require(tuple(protocol["sovereign_routes"]) == ("lic", "bond", *ACCRUAL_CASES), "expected both SBI accrual cases")
    costs = {**base["costs"], "sbi_stamp_percent": terms["fund"]["stamp_duty_percent_of_subscription"]}
    return_assumptions = {row["label"]: row for row in base["forward_returns"]}
    series = {}
    for asset in ("equity", "gold", "silver", "lic", "sbi"):
        source = coverage["source_series"][IDS[asset]]
        path = ROOT / source["path"]
        require(provenance(path)["sha256_normalized"] == source["sha256_normalized"], "observed NAV source hash changed")
        series[asset] = load_marks(path, "date", source["value_field"])
    mark_anchor = date.fromisoformat(coverage["nav_replay_panels"]["sbi_plus_gold_silver"]
                                     ["latest_common_observed_endpoints"][-1])

    def model_policy(funding, scenario):
        end = funding[-1][0]
        replay = scenario is None
        spec = {} if replay else scenario
        rates = return_assumptions[spec.get("rates", "reference")]
        lag = 0 if replay else cfg["sale_lag_calendar_days"]
        stress_tax = spec.get("tax_context") == "stress"
        return Policy(end, end - timedelta(days=lag), lag,
                      0 if replay else spec.get("sbi_lag", base["sbi_maturity_cash_availability_lag_calendar_days"]),
                      None, ZERO, None, ZERO, ZERO if replay else pct(rates["reserve_gross_pct"]),
                      D(cfg["stress_external_income"] if stress_tax else cfg["ordinary_external_income"]),
                      D(spec.get("etf_bps", costs["etf_assumed_all_in_friction_bps_per_side"])),
                      D(spec.get("bond_bps", costs["direct_bond_entry_cost_bps"])), "clean",
                      D(spec.get("sbi_ter", pct(rates["sbi_ter_pct"]))),
                      0 if replay else cfg["bond_redemption_lag_calendar_days"],
                      D(cfg["stress_cess"]) if stress_tax else D("0.04"))

    def forward_market(scenario, funding, route, policy):
        rates = return_assumptions[scenario["rates"]]
        shock = scenario.get("shock", {})
        jump = funding[shock["month"]][0] if shock else None
        first = funding[0][0]
        require(mark_anchor < first, "forward NAV anchor contains future observations")
        gilt = "sbi" if route in ACCRUAL_CASES else route
        marks = {}
        for asset in ("equity", "gold"):
            marks[asset] = mark_path(series[asset][mark_anchor], pct(rates[f"{asset}_nav_pct"]),
                                     first, jump, D(shock.get(asset, "1")))
        maturities = {}
        bond = {}
        if gilt == "lic":
            marks[gilt] = mark_path(series[gilt][mark_anchor], pct(rates["lic_nav_pct"]), first,
                                    jump, D(shock.get("lic", "1")))
        elif gilt == "bond":
            bond = bond_terms(ZERO)
            maturities[gilt] = bond["maturity"]
            shifted = bond_terms(D(shock["bond_yield_add"])) if "bond_yield_add" in shock else bond
            marks[gilt] = lambda day: (shifted if jump and day >= jump else bond)["mark"](day)
        else:
            mat = date.fromisoformat(terms["fund"]["target_maturity_date"])
            maturities[gilt] = mat
            require(jump is None or jump < mat, "cannot shock SBI NAV after modeled maturity")
            row = next(row for row in holdings["scenarios"] if row["market_value_basis"] == route
                       and not row["residual_earns_reinvestment_rate"]
                       and pct(row["reinvest_percent"]) == policy.reserve and pct(row["ter_percent"]) == policy.sbi_ter)
            rate = (ONE + pct(row["gross_effective_annual_percent"])) * (ONE - policy.sbi_ter) - ONE
            marks[gilt] = mark_path(series[gilt][mark_anchor], rate, first, jump,
                                    D(shock.get("sbi_initial", "1")), mat)
        return gilt, marks, maturities, bond

    forward = []
    for scenario in protocol["forward"]:
        funding = reference_funding(schedule, scenario["payments"])
        policy = model_policy(funding, scenario)
        for route in protocol["sovereign_routes"]:
            gilt, marks, maturities, bond = forward_market(scenario, funding, route, policy)
            for name, mix in protocol["policies"].items():
                forward.append(track({"scenario": scenario["id"], "route": route, "policy": name},
                                     funding, portfolio_weights(mix, gilt), policy, marks, maturities, bond,
                                     costs, D(scenario["inflation"])))

    historical = []
    for spec in protocol["historical"]:
        funding = reference_funding(schedule, spec["interval_count"])
        observed = matched_dates(coverage, spec, funding[0][0])
        policy, gilt = model_policy(funding, None), spec["gilt"]
        allocations = dict(protocol["policies"])
        silver = protocol["silver_challenge"]
        if spec["id"] == silver["tape"]:
            mix = allocations[silver["policy"]]
            swap = D(silver["swap_gold_to_silver"])
            allocations["diversified_silver"] = {**mix, "gold": str(D(mix["gold"]) - swap), "silver": str(swap)}
        for name, mix in allocations.items():
            weights = portfolio_weights(mix, gilt)
            marks = {asset: {target: series[asset][obs] for (target, _), obs in zip(funding, observed)}.__getitem__
                     for asset in weights}
            case = {"scenario": spec["id"], "route": gilt, "policy": name,
                    "first_observed": observed[0].isoformat(), "last_observed": observed[-1].isoformat()}
            historical.append(track(case, funding, weights, policy, marks, {}, {}, costs, D("0.06"), historical=True))

    return {"id": protocol["id"], "status": "WP3_DETERMINISTIC_STRESS_ONLY", "protocol_commit": FROZEN_PROTOCOL_COMMIT,
            "decision_grade_personal_output": False, "probability_qualified": False, **evidence,
            "sources": [provenance(path) for path in (PROTOCOL, WP2_INPUT, BASE_INPUT, COVERAGE, CONTRACT_PATH,
                        DEFAULT_SCHEDULE_PATH, CASHFLOW_PATH, AUCTION, SBI_HOLDINGS, SOVEREIGN_INPUT,
                        Path(__file__).resolve(), ROOT / "decision/audit_g6_3_wp3_allocation_stress.py",
                        ROOT / "decision/g6_3_wp2_dated.py", ROOT / "decision/capital_gain_loss_schedule.py",
                        ROOT / "decision/ty2026_27_tax_components.py")],
            "forward": forward, "historical": historical}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    with localcontext() as context:
        context.prec = 42
        result = build()
    payload = json.dumps(result, indent=2) + "\n"
    if args.check:
        require(RESULTS.read_text(encoding="utf-8") == payload, "frozen stress results changed")
    else:
        RESULTS.write_text(payload, encoding="utf-8", newline="\n")
    print(f"PASS: {len(result['forward'])} forward stresses and {len(result['historical'])} NAV replays. NO_GO.")


if __name__ == "__main__":
    main()
