"""Compare two 2036 sovereign exposure routes under frozen price, cost and tax cases."""
from __future__ import annotations

import argparse
import json
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP, localcontext
from itertools import product
from pathlib import Path

from audit_g6_3_direct_gsec_2036 import (
    CASHFLOW_PATH, PAIR_PATH, ROOT, date_30_360, load_json, require,
)
from audit_g6_3_direct_gsec_november_auction import OUT as NOVEMBER_RESULT
from g3_goal_hurdle import normalized_text_and_sha256
from ty2026_27_tax_components import section76_specified_fund_gain


D = Decimal
ONE, ZERO = D(1), D(0)
EVIDENCE = ROOT / "research/g6_3/direct_gsec_2036/2026-11-26-gilt-comparison"
INPUT = EVIDENCE / "inputs_v1.json"
OUTPUT = EVIDENCE / "comparison_v1.json"


def rounded(value, places="0.01"):
    return str(value.quantize(D(places), rounding=ROUND_HALF_UP))


def years(start, end):
    return D((end - start).days) / 365


def growth(annual_rate, start, end):
    return (ONE + annual_rate) ** years(start, end)


def tax_rates(case):
    multiplier = (ONE + D(case["surcharge_percent"]) / 100) * (ONE + D(case["cess_percent"]) / 100)
    return D(case["ordinary_percent"]) * multiplier / 100, D(case["bond_ltcg_percent"]) * multiplier / 100


def load_coupon_schedule(source, entry, maturity, coupon_rate_per_unit):
    all_dates = [date.fromisoformat(row["nominal_coupon_date"]) for row in source["coupon_events"]]
    schedule = []
    for row in source["coupon_events"]:
        pay_date = date.fromisoformat(row["nominal_coupon_date"])
        if pay_date > entry:
            amount = D(row["coupon_per_100_face_inr"])
            require(amount * 2 == coupon_rate_per_unit, "coupon does not match contractual rate")
            schedule.append((pay_date, amount))
    require(all_dates == sorted(set(all_dates)) and len(schedule) == 19
            and schedule[0][0] == date(2027, 5, 11) and schedule[-1][0] == maturity, "invalid dated coupons")
    return schedule, max(day for day in all_dates if day <= entry)


def bond_value(budget, dates, schedule, face, clean, accrued, fee_rate, reserve, rates, basis):
    entry, maturity, end = dates
    ordinary, ltcg = rates
    dirty = clean + accrued
    units = budget // (dirty * (ONE + fee_rate))
    require(units >= ONE, "scenario could not buy a government bond unit")
    consideration = units * dirty
    fee = consideration * fee_rate
    cash = budget - consideration - fee
    require(ZERO <= cash < dirty * (ONE + fee_rate), "whole-unit entry cash does not reconcile")
    principal = units * face
    gain = principal - units * (dirty if basis == "dirty" else clean)
    redemption_tax = max(ZERO, gain) * ltcg
    net_reserve = reserve * (ONE - ordinary)
    gross_terminal = (cash * growth(reserve, entry, end)
                      + principal * growth(reserve, maturity, end)
                      + sum(units * coupon * growth(reserve, day, end) for day, coupon in schedule))
    net_terminal = (cash * growth(net_reserve, entry, end)
                    + (principal - redemption_tax) * growth(net_reserve, maturity, end)
                    + sum(units * coupon * (ONE - ordinary) * growth(net_reserve, day, end)
                          for day, coupon in schedule))
    return {"units": int(units), "dirty_per_unit": dirty, "unused_budget": cash, "entry_fee": fee,
            "principal": principal, "total_nominal_coupon": sum(c * units for _, c in schedule),
            "redemption_gain": gain, "redemption_tax": redemption_tax,
            "coupon_tax_paid": sum(coupon * units * ordinary for _, coupon in schedule),
            "pre_tax": gross_terminal, "post_tax": net_terminal}


def fund_value(budget, entry, end, gross_return, ter, stamp_rate, ordinary):
    invested = budget * (ONE - stamp_rate)
    gross = budget * growth(gross_return, entry, end)
    redemption = invested * growth((ONE + gross_return) * (ONE - ter) - ONE, entry, end)
    gain = section76_specified_fund_gain(redemption, invested, ZERO,
                                       acquired_on_or_after_2023_04_01=entry >= date(2023, 4, 1),
                                       specified_mutual_fund_confirmed=True)
    return {"pre_cost_pre_tax": gross, "pre_tax": redemption, "post_tax": redemption - gain * ordinary,
            "stamp_duty": budget - invested, "tax_basis": invested,
            "section76_gain": gain, "redemption_tax": gain * ordinary}


def fund_break_even_rate(bond_post_tax, budget, entry, end, ter, stamp_rate, ordinary):
    invested = budget * (ONE - stamp_rate)
    require(bond_post_tax >= invested, "break-even targets a fund loss, outside the tax scope")
    gross_exit = invested + (bond_post_tax - invested) / (ONE - ordinary)
    return (gross_exit / invested) ** (ONE / years(entry, end)) / (ONE - ter) - ONE


def report_value(value, pre_cost, budget, entry, end, cpi_cases):
    for key in ("pre_tax", "post_tax"):
        require(value[key] > ZERO, f"invalid terminal amount: {key}")
    require(pre_cost + D("1e-24") >= value["pre_tax"] >= value["post_tax"],
            "terminal costs or taxes increased wealth")
    return {"pre_cost_pre_tax_inr": rounded(pre_cost), "pre_tax_nominal_inr": rounded(value["pre_tax"]),
            "cost_effect_at_endpoint_inr": rounded(max(ZERO, pre_cost - value["pre_tax"])),
            "tax_effect_at_endpoint_inr": rounded(value["pre_tax"] - value["post_tax"]),
            "post_tax_nominal_inr": rounded(value["post_tax"]),
            "after_cost_nominal_annualized_percent": {
                label: rounded(((value[key] / budget) ** (ONE / years(entry, end)) - ONE) * 100, "0.0001")
                for label, key in (("before_tax", "pre_tax"), ("after_tax", "post_tax"))},
            "post_tax_real_inr_by_inflation_percent": {
                inflation: rounded(value["post_tax"] / growth(D(inflation) / 100, entry, end))
                for inflation in cpi_cases}}


def build():
    config = load_json(INPUT)
    bond, fund = config["bond"], config["fund"]
    october = load_json(PAIR_PATH)["auction_result_values"]["competitive_weighted_average_clean_price_per_100"]
    november = load_json(NOVEMBER_RESULT)["primary_quotes"]["weighted_average"]["price_per_100"]
    require({october, november}.issubset(bond["clean_prices_per_100_face"]), "historical anchors missing")
    entry, maturity, end = (date.fromisoformat(value) for value in (
        config["hypothetical_investment_date"], bond["maturity_date"], config["common_valuation_date"]))
    budget, face, coupon = map(D, (config["contribution_inr"], bond["unit_face_inr"], bond["coupon_annual_percent"]))
    source = load_json(CASHFLOW_PATH)
    require(source["isin"] == bond["isin"] and face == 100 and (maturity - entry).days > 366,
            "unsupported bond classification or denomination")
    require(maturity < end and end.isoformat() == fund["target_maturity_date"]
            and D(fund["exit_load_after_30_days_percent"]) == ZERO, "common maturity/exit constraint failed")
    require(fund["isin"] == "INF200KA12Q9" and D(fund["factsheet_government_securities_percent"]) > 65,
            "fund identity or observed debt exposure is inconsistent with modeled scope")
    schedule, last = load_coupon_schedule(source, entry, maturity, coupon)
    require(last.isoformat() == bond["last_scheduled_coupon_before_entry"], "incorrect coupon cycle for settlement")
    days_accrued = date_30_360(last, entry)
    accrued = coupon * days_accrued / 360
    stamp = D(fund["stamp_duty_percent_of_subscription"]) / 100
    inflation = config["inflation_annual_percent_cases"]

    bond_cases = []
    for tax, price, fee, reserve, basis in product(
        config["tax_cases"], bond["clean_prices_per_100_face"], bond["purchase_costs_bps_of_dirty_consideration"],
        config["reserve_gross_annual_percent_cases"], bond["accrued_interest_basis_cases"]
    ):
        rates = tax_rates(tax)
        dates = (entry, maturity, end)
        case = bond_value(budget, dates, schedule, face, D(price), accrued, D(fee) / 10_000, D(reserve) / 100, rates, basis)
        pre_cost = bond_value(budget, dates, schedule, face, D(price), accrued, ZERO, D(reserve) / 100, rates, basis)["pre_tax"]
        break_even = {}
        for fee_pct in fund["annual_ter_percent_cases"]:
            ter = D(fee_pct) / 100
            rate = fund_break_even_rate(case["post_tax"], budget, entry, end, ter, stamp, rates[0])
            opposite = fund_value(budget, entry, end, rate, ter, stamp, rates[0])["post_tax"]
            require(abs(opposite - case["post_tax"]) < D("1e-24"), "fund break-even failed round trip")
            break_even[fee_pct] = rounded(rate * 100, "0.0001")
        bond_cases.append({
            "tax_case": tax["label"], "clean_per_100": price, "entry_fee_bps": fee,
            "reserve_gross_percent": reserve, "redemption_basis": basis, "units": case["units"],
            **{f"{key}_inr": rounded(case[key]) for key in (
                "dirty_per_unit", "unused_budget", "entry_fee", "principal", "total_nominal_coupon",
                "redemption_gain", "coupon_tax_paid", "redemption_tax")},
            **report_value(case, pre_cost, budget, entry, end, inflation),
            "break_even_fund_gross_percent_by_ter_percent": break_even,
        })

    fund_cases = []
    for tax, annual, ter in product(config["tax_cases"], fund["gross_annual_effective_return_percent_cases"],
                                    fund["annual_ter_percent_cases"]):
        case = fund_value(budget, entry, end, D(annual) / 100, D(ter) / 100, stamp, tax_rates(tax)[0])
        fund_cases.append({"tax_case": tax["label"], "gross_annual_percent": annual, "ter_annual_percent": ter,
                           **{f"{key}_inr": rounded(case[key]) for key in ("stamp_duty", "tax_basis", "section76_gain", "redemption_tax")},
                           **report_value(case, case["pre_cost_pre_tax"], budget, entry, end, inflation)})

    # Challenge nominal dates with a Monday-Friday-only calendar. Actual holidays remain unqualified.
    base_tax = next(tax for tax in config["tax_cases"] if tax["label"] == "30_slab")
    weekday_principal = maturity - timedelta(days=max(0, maturity.weekday() - 4))
    weekday_coupons = [(day + timedelta(days=7 - day.weekday()) if day.weekday() >= 5 else day, value)
                       for day, value in schedule]
    weekday_case = bond_value(budget, (entry, weekday_principal, end), weekday_coupons,
                              face, D(november), accrued, D("0.001"), D("0.04"), tax_rates(base_tax), "clean_only")
    nominal_case = bond_value(budget, (entry, maturity, end), schedule,
                              face, D(november), accrued, D("0.001"), D("0.04"), tax_rates(base_tax), "clean_only")
    return {
        "status": "CONDITIONAL_LUMP_SUM_COMPARISON_ONLY",
        "input_sha256_normalized": normalized_text_and_sha256(INPUT)[1],
        "cashflow_source_sha256_normalized": normalized_text_and_sha256(CASHFLOW_PATH)[1],
        "code_sha256_normalized": normalized_text_and_sha256(Path(__file__))[1],
        "invested_budget_inr": str(budget), "investment_date": entry.isoformat(), "valuation_date": end.isoformat(),
        "bond_accrual_days_30_360": days_accrued,
        "bond_accrued_interest_inr_per_unit": rounded(accrued, "0.000001"),
        "bond_principal_bridge_days": (end - maturity).days,
        "nominal_bond_coupon_count_after_entry": len(schedule),
        "monday_friday_calendar_sensitivity_for_reference_bond": {
            "principal_payment_assumption": weekday_principal.isoformat(),
            "last_coupon_payment_assumption": weekday_coupons[-1][0].isoformat(),
            "post_tax_nominal_difference_vs_nominal_dates_inr": rounded(weekday_case["post_tax"] - nominal_case["post_tax"]),
        },
        "bond_cases": bond_cases, "fund_cases": fund_cases,
        "live_quote_verified": False, "paid_silver_history": "DEFERRED", "rbi_tbill_payment_timing": "OPEN",
        "investment_authorization": "NO_GO",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    with localcontext() as ctx:
        ctx.prec = 45
        result = build()
    # One line per case keeps the evidence grid readable in version control.
    bond_cases, fund_cases = result.pop("bond_cases"), result.pop("fund_cases")
    prefix = json.dumps(result, indent=2)[:-2]
    payload = prefix + ",\n  \"bond_cases\": [\n    " + ",\n    ".join(map(json.dumps, bond_cases))
    payload += "\n  ],\n  \"fund_cases\": [\n    " + ",\n    ".join(map(json.dumps, fund_cases)) + "\n  ]\n}\n"
    if args.check:
        require(OUTPUT.read_text(encoding="utf-8") == payload, "frozen gilt comparison differs")
    else:
        OUTPUT.write_text(payload, encoding="utf-8", newline="\n")
    print(f"PASS: {len(bond_cases)} bond and {len(fund_cases)} fund cases reproduced. NO_GO.")


if __name__ == "__main__":
    main()
