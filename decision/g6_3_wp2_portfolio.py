"""Replay matched NAV moves and run bounded 2036 portfolio cashflow scenarios."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal, localcontext
from itertools import product
from math import fsum
from pathlib import Path

from audit_g6_3_direct_gsec_2036 import CASHFLOW_PATH, xirr_actual_365
from audit_g6_3_direct_gsec_november_auction import OUT as AUCTION
from audit_g6_3_exact_date_coverage import (
    GOLD, LIC, MOTILAL, OUT as COVERAGE, SBI_GILT, SILVER, load_marks, provenance,
)
from audit_g6_3_sbi_gilt_holdings import OUTPUT as SBI_HOLDINGS, accrued_days
from compare_g6_3_gilt_routes import (
    D, INPUT as SOVEREIGN_INPUT, ONE, ROOT, ZERO, bond_value, growth, rounded, tax_rates,
)
from g3_goal_hurdle import (
    CONTRACT_PATH, DEFAULT_SCHEDULE_PATH, cpi_factor, read_schedule, validate_schedule_contract,
)
from g6_2_full_horizon_bridge import _month_end
from ty2026_27_tax_components import SECTION198_ANNUAL_DEDUCTION, section76_specified_fund_gain


EVIDENCE = ROOT / "research/g6_3/2026-11-27-wp2-portfolio"
INPUT = EVIDENCE / "inputs_v1.json"
OUT = EVIDENCE / "portfolio_v1.json"
SEPARATE_ACCRUAL = "accrual_in_net_receivables"
INCLUDED_ACCRUAL = "market_value_includes_accrual"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def long_term(acquired, exited):
    """Model the strict more-than-12-calendar-month test for these listed/equity lots."""
    anniversary = acquired.replace(year=acquired.year + 1, day=28) if (acquired.month, acquired.day) == (2, 29) else (
        acquired.replace(year=acquired.year + 1)
    )
    return exited > anniversary


@dataclass
class Sleeve:
    before_costs: Decimal = ZERO
    before_tax: Decimal = ZERO
    after_tax: Decimal = ZERO
    funded: Decimal = ZERO
    maturity_or_exit_tax: Decimal = ZERO
    coupon_tax: Decimal = ZERO
    realized_losses_excluded: Decimal = ZERO
    contributions_to_cash: Decimal = ZERO
    acquired_lots: int = 0
    long_lots: int = 0
    short_lots: int = 0
    exit_load_inr: Decimal = ZERO
    gains: dict = field(default_factory=lambda: defaultdict(Decimal))

    def report(self):
        return {key: ({k: rounded(v) for k, v in sorted(value.items())} if isinstance(value, dict)
                      else value if isinstance(value, int) else rounded(value))
                for key, value in vars(self).items()}


def nav_sleeve(kind, funding, terminal, gross_factor, net_factor, costs, tax, gross_reserve,
               sell_date=None, available_date=None):
    """Price each purchase lot and tax its gain on the modeled uplift or redemption date."""
    exit_day = sell_date or terminal
    available = available_date or exit_day
    ordinary, ltcg = tax_rates(tax)
    net_reserve = gross_reserve * (ONE - ordinary)
    eq_short = D("0.20") * (ONE + D(tax["cess_percent"]) / 100) * (ONE + D(tax["surcharge_percent"]) / 100)
    exemption = D(tax["assumed_available_equity_ltcg_exemption_inr"])
    require(ZERO <= exemption <= SECTION198_ANNUAL_DEDUCTION and available <= terminal, "invalid tax or payout scenario")
    etf_fee = D(costs["etf_assumed_all_in_friction_bps_per_side"]) / 10_000
    entry_cost = (D(costs["equity_fund_entry_stamp_percent"]) / 100 if kind == "equity" else
                  D(costs["sbi_stamp_percent"]) / 100 if kind == "sbi" else etf_fee)
    exit_cost = (D(costs["equity_fund_exit_stt_percent"]) / 100 if kind == "equity" else
                 ZERO if kind == "sbi" else etf_fee)
    sleeve = Sleeve()
    for day, cash in funding:
        sleeve.funded += cash
        if day >= exit_day:
            sleeve.contributions_to_cash += cash
            sleeve.before_costs += cash * growth(gross_reserve, day, terminal)
            sleeve.before_tax += cash * growth(gross_reserve, day, terminal)
            sleeve.after_tax += cash * growth(net_reserve, day, terminal)
            continue
        sleeve.acquired_lots += 1
        bought = cash * (ONE - entry_cost)
        market_value = bought * net_factor(day)
        load = ZERO
        if kind == "equity" and (exit_day - day).days <= costs["equity_fund_exit_load_up_to_days"]:
            load = D(costs["equity_fund_exit_load_percent"]) / 100
        if kind == "sbi" and (exit_day - day).days <= costs["sbi_exit_load_up_to_days"]:
            load = D(costs["sbi_exit_load_percent_sensitivity"]) / 100
        sleeve.exit_load_inr += market_value * load
        redemption = market_value * (ONE - load)
        # Modeled acquisition basis is invested principal. ETF friction and STT receive no deduction.
        signed_gain = redemption - bought
        sleeve.realized_losses_excluded += max(ZERO, -signed_gain)
        if kind in ("sbi", "lic"):
            bucket = "section76"
            require(day >= date(2023, 4, 1), "pre-transition fund lots are outside this scenario")
            gain = section76_specified_fund_gain(redemption, bought, ZERO,
                                                acquired_on_or_after_2023_04_01=True,
                                                specified_mutual_fund_confirmed=True) if signed_gain >= ZERO else ZERO
            sleeve.short_lots += 1
        else:
            gain = max(ZERO, signed_gain)
            is_long = long_term(day, exit_day)
            sleeve.long_lots += int(is_long)
            sleeve.short_lots += int(not is_long)
            bucket = (("section198" if is_long else "section196") if kind == "equity" else
                      ("section197" if is_long else "ordinary_stcg"))
        sleeve.gains[bucket] += gain
        proceeds = redemption * (ONE - exit_cost)
        sleeve.before_costs += cash * gross_factor(day) * growth(gross_reserve, available, terminal)
        sleeve.before_tax += proceeds * growth(gross_reserve, available, terminal)
        sleeve.after_tax += proceeds * growth(net_reserve, available, terminal)
    tax_due = (ordinary * (sleeve.gains.get("section76", ZERO) + sleeve.gains.get("ordinary_stcg", ZERO))
               + ltcg * (sleeve.gains.get("section197", ZERO) + max(ZERO, sleeve.gains.get("section198", ZERO) - exemption))
               + eq_short * sleeve.gains.get("section196", ZERO))
    sleeve.maturity_or_exit_tax = tax_due
    sleeve.after_tax -= tax_due * growth(net_reserve, available, terminal)
    require(sleeve.long_lots + sleeve.short_lots == sleeve.acquired_lots, "lot classification does not reconcile")
    return sleeve


def direct_sleeve(funding, terminal, reserve, tax, cost, coupon_source, auction_yield):
    sleeve = Sleeve()
    schedule = [(date.fromisoformat(row["nominal_coupon_date"]), D(row["coupon_per_100_face_inr"]))
                for row in coupon_source["coupon_events"]]
    maturity = schedule[-1][0]
    prior = date(2026, 5, 11)
    face = D(100)
    nominal_to_effective_multiplier = (ONE + auction_yield / 2) ** 2
    ordinary, ltcg = tax_rates(tax)
    for day, cash in funding:
        sleeve.funded += cash
        if day >= maturity:
            sleeve.contributions_to_cash += cash
            sleeve.before_costs += cash * growth(reserve, day, terminal)
            sleeve.before_tax += cash * growth(reserve, day, terminal)
            sleeve.after_tax += cash * growth(reserve * (ONE - ordinary), day, terminal)
            continue
        pays = [(when, coupon) for when, coupon in schedule if when > day]
        prev = max([prior, *(when for when, _ in schedule if when <= day)])
        # Reprice each lot at the frozen auction yield as it rolls toward par.
        dirty = sum((coupon + (face if when == maturity else ZERO))
                    / nominal_to_effective_multiplier ** (D(accrued_days(day, when)) / 360)
                    for when, coupon in pays)
        accrued = D("6.94") * D(accrued_days(prev, day)) / 360
        clean = dirty - accrued
        is_long = long_term(day, maturity)
        rates = (ordinary, ltcg if is_long else ordinary)
        gross = bond_value(cash, (day, maturity, terminal), pays, face, clean, accrued, ZERO, reserve, rates, "clean_only")
        net = bond_value(cash, (day, maturity, terminal), pays, face, clean, accrued, cost, reserve, rates, "clean_only")
        sleeve.before_costs += gross["pre_tax"]
        sleeve.before_tax += net["pre_tax"]
        sleeve.after_tax += net["post_tax"]
        sleeve.maturity_or_exit_tax += net["redemption_tax"]
        sleeve.coupon_tax += net["coupon_tax_paid"]
        sleeve.acquired_lots += 1
        sleeve.long_lots += int(is_long)
        sleeve.short_lots += int(not is_long)
        gain = net["redemption_gain"]
        sleeve.gains["section197" if is_long else "ordinary_stcg"] += max(ZERO, gain)
        sleeve.realized_losses_excluded += max(ZERO, -gain)
    return sleeve


def reference_funding(schedule, horizon):
    return [(_month_end(schedule.base_month, index), schedule.initial_inr if index == 0 else schedule.monthly_contributions[index])
            for index in range(horizon + 1)]


def scale_funding(funding, weight):
    return [(day, cash * weight) for day, cash in funding] if weight else []


def report(sleeves, funding, contract, months, full_horizon):
    gross, pre, net = [sum(getattr(sleeve, field) for sleeve in sleeves.values())
                       for field in ("before_costs", "before_tax", "after_tax")]
    start, end = funding[0][0], funding[-1][0]
    contributed = sum(cash for _, cash in funding)
    require(abs(contributed - sum(sleeve.funded for sleeve in sleeves.values())) < D("1e-20")
            and gross + D("1e-20") >= pre >= net > ZERO, "portfolio flow or tax/cost reconciliation failed")
    xirr = {}
    for label, amount in (("before_investor_tax", pre), ("after_modeled_tax", net)):
        flows = [(-float(cash), day) for day, cash in funding] + [(float(amount), end)]
        rate = xirr_actual_365(flows)
        check = fsum(value * (1 + rate) ** ((end - day).days / 365) for value, day in flows)
        require(abs(check) < 0.00001, "XIRR terminal-value identity differs")
        xirr[label] = rounded(D(str(rate)) * 100, "0.0001")
    inflation = {}
    for case in contract["inflation_scenarios"]["annual_compound_fractions"]:
        real = net / cpi_factor(D(case), months)
        inflation[case] = {"net_real_inr": rounded(real)}
        if full_horizon:
            for item in contract["targets"]:
                inflation[case][item["target_id"] + "_shortfall_inr"] = rounded(
                    max(ZERO, D(item["real_amount_inr_2026"]) - real))
    return {"start": start.isoformat(), "end": end.isoformat(), "sip_count": months,
            "contributions_inr": rounded(contributed),
            "before_explicit_costs_and_investor_tax_inr": rounded(gross),
            "explicit_cost_effect_at_terminal_inr": rounded(gross - pre),
            "after_costs_before_investor_tax_inr": rounded(pre),
            "tax_effect_at_terminal_inr": rounded(pre - net),
            "after_costs_and_modeled_tax_inr": rounded(net), "nominal_xirr_pct": xirr,
            "after_tax_real_october_2026_reference": inflation,
            "sleeves": {kind: sleeve.report() for kind, sleeve in sleeves.items()}}


def build():
    cfg, coverage, contract = read(INPUT), read(COVERAGE), read(CONTRACT_PATH)
    sbi_audit, sovereign = read(SBI_HOLDINGS), read(SOVEREIGN_INPUT)
    schedule = read_schedule(DEFAULT_SCHEDULE_PATH)
    validate_schedule_contract(schedule, contract)
    cases = [SEPARATE_ACCRUAL, INCLUDED_ACCRUAL]
    require(next(row for row in coverage["candidate_inclusion"] if row["candidate_id"] == SBI_GILT)[
        "forward_accrual_cases"] == cases, "both WP1 SBI accounting cases must feed WP2")
    exceptions = {key: coverage[key] for key in ("live_quote", "paid_silver_history", "rbi_tbill_payment_timing",
                                                 "investment_authorization")}
    require(tuple(exceptions.values()) == ("DEFERRED", "DEFERRED", "OPEN", "NO_GO"), "WP1 scope changed")
    costs = {**cfg["costs"], "sbi_stamp_percent": sovereign["fund"]["stamp_duty_percent_of_subscription"]}
    weights = {case: {name: D(amount) for name, amount in mix.items()} for case, mix in cfg["portfolio_weights"].items()}
    require(all(sum(mix.values()) == ONE and min(mix.values()) >= ZERO for mix in weights.values()), "weights do not fund the portfolio")
    panels = coverage["nav_replay_panels"]
    observed = panels["sbi_plus_gold_silver"]["latest_common_observed_endpoints"]
    require(len(observed) == 49 and observed == panels["lic_plus_gold_silver"]["latest_common_observed_endpoints"][-49:],
            "need the same 48 observed intervals across both gilt candidates")
    observed_days = list(map(date.fromisoformat, observed))
    require(all(b.year * 12 + b.month - a.year * 12 - a.month == 1
                for a, b in zip(observed_days, observed_days[1:])), "replay contains a missing or duplicate month")

    path_ids = {"equity": MOTILAL, "gold": GOLD, "silver": SILVER, "lic": LIC, "sbi": SBI_GILT}
    marks, nav_sources = {}, []
    for kind, cid in path_ids.items():
        source = coverage["source_series"][cid]
        path = ROOT / source["path"]
        require(provenance(path)["sha256_normalized"] == source["sha256_normalized"], f"WP1 NAV hash differs for {cid}")
        daily = load_marks(path, "date", source["value_field"])
        marks[kind] = [daily[day] for day in observed_days]
        nav_sources.append(path)

    replay_funding = reference_funding(schedule, 48)
    require(observed_days[-1] < replay_funding[0][0], "historical moves must be known before the replay scenario begins")
    replay_end = replay_funding[-1][0]
    matched_replays = []
    for gilt, (label, mix) in product(("lic", "sbi"), weights.items()):
        sleeves = {}
        for role, weight in mix.items():
            if not weight:
                continue
            kind = gilt if role == "gilt" else role
            ratios = {day: marks[kind][-1] / mark for (day, _), mark in zip(replay_funding, marks[kind])}
            sleeves[kind] = nav_sleeve(kind, scale_funding(replay_funding, weight), replay_end, ratios.__getitem__,
                                       ratios.__getitem__, costs, cfg["tax_cases"][0], ZERO)
        matched_replays.append({"gilt": gilt, "weights": label, "tax_case": cfg["tax_cases"][0]["label"],
                                **report(sleeves, replay_funding, contract, 48, False)})

    forward = []
    auction_yield = D(read(AUCTION)["primary_quotes"]["weighted_average"]["nominal_ytm_percent"]) / 100
    coupon_source = read(CASHFLOW_PATH)
    maturity = date.fromisoformat(sovereign["fund"]["target_maturity_date"])
    available = maturity + timedelta(days=cfg["sbi_maturity_cash_availability_lag_calendar_days"])
    base_mix = weights["gold_baseline"]
    fixture = contract["illustrative_cashflow_fixture"]
    horizons = fixture["primary_contribution_count"], fixture["sensitivity_contribution_count"]
    for horizon, curve, tax in product(horizons, cfg["forward_returns"], cfg["tax_cases"]):
        funding = reference_funding(schedule, horizon)
        end = funding[-1][0]
        reserve = D(curve["reserve_gross_pct"]) / 100
        common = {}
        for kind in ("equity", "gold"):
            rate = D(curve[f"{kind}_nav_pct"]) / 100
            factor = lambda day: growth(rate, day, end)
            common[kind] = nav_sleeve(kind, scale_funding(funding, base_mix[kind]), end, factor, factor, costs, tax, reserve)
        gilt_funding = scale_funding(funding, base_mix["gilt"])
        lic_rate = D(curve["lic_nav_pct"]) / 100
        factor = lambda day: growth(lic_rate, day, end)
        routes = {"lic_nav_assumption": nav_sleeve("lic", gilt_funding, end, factor, factor, costs, tax, reserve),
                  "direct_gsec_694_2036": direct_sleeve(gilt_funding, end, reserve, tax,
                                                      D(costs["direct_bond_entry_cost_bps"]) / 10_000, coupon_source, auction_yield)}
        for case in cases:
            scenario = next(row for row in sbi_audit["scenarios"] if row["market_value_basis"] == case
                            and not row["residual_earns_reinvestment_rate"]
                            and D(row["ter_percent"]) == D(curve["sbi_ter_pct"])
                            and D(row["reinvest_percent"]) == reserve * 100)
            gross_rate = D(scenario["gross_effective_annual_percent"]) / 100
            net_rate = (ONE + gross_rate) * (ONE - D(curve["sbi_ter_pct"]) / 100) - ONE
            routes[case] = nav_sleeve("sbi", gilt_funding, end,
                                      lambda day: growth(gross_rate, day, maturity),
                                      lambda day: growth(net_rate, day, maturity), costs, tax, reserve, maturity, available)
        for route, gilt in routes.items():
            forward.append({"gilt": route, "curve": curve["label"], "tax_case": tax["label"], "weights": "gold_baseline",
                            **report({**common, "gilt": gilt}, funding, contract, horizon, True)})
    return {"record_id": cfg["record_id"], "status": "BOUNDED_WP2_DETERMINISTIC_COMPARISON",
            "sources": [provenance(path) for path in (Path(__file__).resolve(), INPUT, COVERAGE, CONTRACT_PATH,
                       DEFAULT_SCHEDULE_PATH, SBI_HOLDINGS, SOVEREIGN_INPUT, AUCTION, CASHFLOW_PATH, *nav_sources)],
            "source_replay_endpoints": observed, "replay_cases": matched_replays,
            "forward_cases": forward, "sbi_forward_accrual_cases": cases,
            "direct_auction_nominal_yield_pct": rounded(auction_yield * 100, "0.0001"),
            "supports_actual_personal_outcomes": False, "supports_probability": False, **exceptions}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    with localcontext() as ctx:
        ctx.prec = 45
        result = build()
    text = json.dumps(result, indent=2) + "\n"
    if args.check:
        require(OUT.read_text(encoding="utf-8") == text, "WP2 portfolio result differs")
    else:
        OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"PASS: {len(result['replay_cases'])} matched NAV replays and {len(result['forward_cases'])} forward cases. NO_GO.")


if __name__ == "__main__":
    main()
