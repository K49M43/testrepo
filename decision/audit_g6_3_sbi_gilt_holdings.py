"""Reconcile the SBI June 2036 gilt holdings and challenge the direct-bond hurdle."""
from __future__ import annotations

import argparse
import json
from datetime import date, datetime
from decimal import localcontext
from itertools import product
from pathlib import Path

from audit_g6_3_direct_gsec_2036 import CASHFLOW_PATH, load_json, require, verify_hash
from compare_g6_3_gilt_routes import (
    D, INPUT as COMPARISON_INPUT, OUTPUT as COMPARISON_OUTPUT, ONE, ROOT, ZERO,
    bond_value, fund_break_even_rate, fund_value, growth, rounded, tax_rates, years,
)
from g3_goal_hurdle import normalized_text_and_sha256


EVIDENCE = ROOT / "research/g6_3/direct_gsec_2036/2026-11-26-sbi-holdings"
INPUT = EVIDENCE / "snapshot_v1.json"
OUTPUT = EVIDENCE / "cashflow_audit_v1.json"
RATE_PLACES = "0.0001"


def verify_workbook(source, path):
    # Optional independent source verification. Frozen calculations require only stdlib.
    from openpyxl import load_workbook

    verify_hash(path, source["bytes"], source["sha256"])
    workbook = load_workbook(path, read_only=True, data_only=True)
    try:
        sheet = workbook[source["sheet"]]
        for cell, expected in source["cells"].items():
            actual = sheet[cell].value
            if isinstance(actual, datetime):
                actual = actual.date().isoformat()
            require(str(actual) == expected, f"worksheet source cell {cell} differs")
        rows = list(sheet.iter_rows(min_row=7, max_row=60, min_col=3, max_col=7, values_only=True))
        isins = [isin for _, isin, _, _, _ in rows if isinstance(isin, str) and len(isin) == 12 and isin.startswith("IN")]
        require(isins == [source["cells"]["D24"]], "unreconciled ISIN in portfolio")
        valued_positions = [label for label, _, _, _, mark in rows
                            if isinstance(mark, (int, float)) and mark != 0 and label != "Total"]
        require(valued_positions == [source["cells"][cell] for cell in ("C24", "C53", "C58")],
                "unreconciled portfolio line with a nonzero market value")
    finally:
        workbook.close()


def accrued_days(start, end):
    """30E/360 convention for a month-end valuation sensitivity."""
    return (end.year - start.year) * 360 + (end.month - start.month) * 30 + min(end.day, 30) - min(start.day, 30)


def solve_rate(value_at_rate, target, low=ZERO, high=D("0.20")):
    require(value_at_rate(low) <= target <= value_at_rate(high), "break-even outside tested search bracket")
    for _ in range(48):
        middle = (low + high) / 2
        if value_at_rate(middle) < target:
            low = middle
        else:
            high = middle
    rate = (low + high) / 2
    require(abs(value_at_rate(rate) - target) < D("0.000001"), "break-even did not round trip")
    return rate


def build(snapshot):
    cfg = load_json(COMPARISON_INPUT)
    original = load_json(COMPARISON_OUTPUT)
    cells = snapshot["portfolio"]["cells"]
    terms = snapshot["bond_terms"]
    factsheet = snapshot["sbi_factsheet_comparison"]
    entry = date.fromisoformat(snapshot["portfolio"]["as_of"])
    end = date.fromisoformat(cfg["common_valuation_date"])
    maturity = date.fromisoformat(terms["maturity"])
    require(cells["D4"] == entry.isoformat() and cells["D24"] == terms["isin"] == "IN0020220029",
            "holding identity or as-of date changed")
    require(cells["D24"] != cfg["bond"]["isin"] and cells["G37"] == cells["E90"] == "NIL",
            "unexpected direct bond, T-bills or derivatives")

    bond_mark, treps, net_receivable, aum = (D(cells[cell]) for cell in ("G24", "G53", "G58", "G61"))
    require(bond_mark + treps + net_receivable == aum, "portfolio line items do not sum to AUM")
    for amount, cell in zip((bond_mark, treps, net_receivable, aum), ("H24", "H53", "H58", "H61")):
        require(rounded(amount / aum * 100) == rounded(D(cells[cell])), f"weight {cell} disagrees with AUM")
    require(cells["H24"] == factsheet["government_weight_percent"] ==
            cfg["fund"]["factsheet_government_securities_percent"]
            and cells["E83"] == factsheet["direct_growth_nav_inr"]
            and factsheet["date"] == cfg["fund"]["factsheet_valuation_date"]
            and factsheet["portfolio_ytm_percent"] == cfg["fund"]["factsheet_portfolio_ytm_percent"],
            "factsheet anchors changed")

    budget = D(cfg["contribution_inr"])
    lakh = D(100_000)
    aum_gap = aum - D(factsheet["aum_inr_lakh"])
    face = D(terms["par_inr_per_quantity_unit"])
    quantity = D(cells["F24"])
    semiannual_coupon = face * D(terms["coupon_annual_percent"]) / 200
    mark_per_unit = bond_mark * lakh / quantity
    require(face == 100 and D("90") < mark_per_unit < D("110"), "portfolio quantity-to-par interpretation failed")
    dates = [date(year, month, terms["coupon_day"])
             for year in range(date.fromisoformat(terms["issue"]).year + 1, maturity.year + 1)
             for month in terms["coupon_months"]]
    coupon_dates = [day for day in dates if entry < day <= maturity]
    previous_coupon = max(day for day in dates if day <= entry)
    require(len(coupon_dates) == 20 and coupon_dates[0] == date(2026, 11, 23)
            and coupon_dates == sorted(set(coupon_dates)) and coupon_dates[-1] == maturity and maturity < end,
            "invalid nominal coupon or maturity schedule")
    bond_accrued_per_unit = semiannual_coupon * D(accrued_days(previous_coupon, entry)) / 180
    bond_accrued_lakh = bond_accrued_per_unit * quantity / lakh

    # All contractual coupon receipts are counted once. If accrued interest sits in
    # net receivables, carve it out before assigning the residual a terminal value.
    mark_bases = {
        "market_value_includes_accrual": ZERO,
        "accrual_in_net_receivables": bond_accrued_lakh,
    }
    scale = budget / (aum * lakh)
    flows = [(day, semiannual_coupon * quantity * scale) for day in coupon_dates]
    flows[-1] = (maturity, flows[-1][1] + face * quantity * scale)
    require(abs(sum(amount for _, amount in flows)
                - (face + semiannual_coupon * len(coupon_dates)) * quantity * scale) < D("1e-24"),
            "cashflow total does not reconcile")

    base_tax = next(row for row in cfg["tax_cases"] if row["label"] == "30_slab")
    rates = tax_rates(base_tax)
    stamp = D(cfg["fund"]["stamp_duty_percent_of_subscription"]) / 100
    reference = next(row for row in original["bond_cases"] if row["tax_case"] == "30_slab"
                     and row["clean_per_100"] == "97.46" and row["entry_fee_bps"] == "10"
                     and row["reserve_gross_percent"] == "4" and row["redemption_basis"] == "clean_only")
    prior_hurdle = D(reference["break_even_fund_gross_percent_by_ter_percent"]["0.28"]) / 100
    require(prior_hurdle == D("0.066069") and original["valuation_date"] == end.isoformat(),
            "prior hurdle changed, requalify comparison scope")
    direct_source = load_json(CASHFLOW_PATH)
    require(direct_source["isin"] == cfg["bond"]["isin"], "direct schedule identity changed")
    direct_dates = [date.fromisoformat(row["nominal_coupon_date"]) for row in direct_source["coupon_events"]]
    direct_coupon = D(direct_source["coupon_per_100_face_inr"])
    direct_schedule = [(day, direct_coupon) for day in direct_dates if day > entry]
    require(direct_schedule[0][0] == date(2026, 11, 11)
            and len(direct_schedule) == 20 and direct_schedule[-1][0] == date.fromisoformat(cfg["bond"]["maturity_date"]),
            "matched-date direct bond coupon schedule changed")
    direct_accrued = D(cfg["bond"]["coupon_annual_percent"]) * D(accrued_days(
        date(2026, 5, 11), entry)) / 360
    reinvestments = [D(rate) / 100 for rate in snapshot["coupon_reinvestment_percent_cases"]]
    expenses = [D(rate) / 100 for rate in cfg["fund"]["annual_ter_percent_cases"]]
    matched_bonds = {rate: bond_value(budget, (entry, direct_dates[-1], end), direct_schedule, face,
                                     D(reference["clean_per_100"]), direct_accrued, D("0.001"),
                                     rate, rates, "clean_only")["post_tax"] for rate in reinvestments}
    window = (entry, end)

    def gross_terminal(reinvest, remaining, residual_earns):
        investable = treps * lakh * scale
        residual = remaining * lakh * scale
        rate = reinvest if residual_earns else ZERO
        value = investable * growth(reinvest, *window) + residual * growth(rate, *window)
        return value + sum(amount * growth(reinvest, day, end) for day, amount in flows)

    def verify_rollforward(reinvest, remaining, residual_earns, gross):
        cash, last = treps * lakh * scale, entry
        for day, amount in flows:
            cash = cash * growth(reinvest, last, day) + amount
            last = day
        residual = remaining * lakh * scale * growth(reinvest if residual_earns else ZERO, *window)
        require(abs(gross - (cash * growth(reinvest, last, end) + residual)) < D("1e-24"),
                "terminal cashflow roll-forward differs")

    cases, thresholds, valuation = [], [], {}
    all_in_cashflows = [(day, semiannual_coupon + (face if day == maturity else ZERO)) for day in coupon_dates]
    quoted = D(cells["I24"]) / 100
    pv_at_quoted = sum(amount / growth((ONE + quoted / 2) ** 2 - ONE, entry, day)
                       for day, amount in all_in_cashflows)
    for basis, accrued in mark_bases.items():
        remaining = net_receivable - accrued
        dirty_mark = mark_per_unit + accrued * lakh / quantity
        valuation[basis] = {
            "dirty_mark_per_100": rounded(dirty_mark, "0.0001"),
            "residual_net_assets_lakh": rounded(remaining),
            "dirty_mark_minus_pv_at_disclosed_holding_ytm_inr": rounded(dirty_mark - pv_at_quoted, "0.0001"),
        }
        for residual_earns, ter in product((False, True), expenses):
            matched_hurdle = fund_break_even_rate(matched_bonds[D("0.04")], budget, *window, ter, stamp, rates[0])
            prior_required = solve_rate(lambda r: gross_terminal(r, remaining, residual_earns),
                                        budget * growth(prior_hurdle, *window))
            matched_required = solve_rate(lambda r: gross_terminal(r, remaining, residual_earns),
                                          budget * growth(matched_hurdle, *window))
            labels = {"market_value_basis": basis, "residual_earns_reinvestment_rate": residual_earns,
                      "ter_percent": rounded(ter * 100)}
            thresholds.append({**labels,
                               "matched_4pct_direct_gross_fund_hurdle_percent": rounded(matched_hurdle * 100, RATE_PLACES),
                               "reinvest_to_reach_prior_6_6069pct_percent": rounded(prior_required * 100, RATE_PLACES),
                               "reinvest_to_match_fixed_4pct_direct_percent": rounded(matched_required * 100, RATE_PLACES)})
            for rate in reinvestments:
                gross = gross_terminal(rate, remaining, residual_earns)
                verify_rollforward(rate, remaining, residual_earns, gross)
                annual = (gross / budget) ** (ONE / years(*window)) - ONE
                fund = fund_value(budget, *window, annual, ter, stamp, rates[0])
                require(fund["pre_tax"] <= gross and fund["post_tax"] <= fund["pre_tax"],
                        "expenses and taxes increased terminal value")
                cases.append({**labels, "reinvest_percent": rounded(rate * 100),
                              "gross_effective_annual_percent": rounded(annual * 100, RATE_PLACES),
                              "gross_margin_to_prior_hurdle_bps": rounded((annual - prior_hurdle) * 10_000),
                              "gross_terminal_inr": rounded(gross),
                              "fund_after_cost_pre_tax_inr": rounded(fund["pre_tax"]),
                              "fund_after_cost_and_tax_inr": rounded(fund["post_tax"]),
                              "fund_minus_fixed_4pct_direct_after_tax_inr": rounded(fund["post_tax"] - matched_bonds[D("0.04")]),
                              "fund_minus_same_rate_direct_after_tax_inr": rounded(fund["post_tax"] - matched_bonds[rate])})

    return {
        "status": "HOLDINGS_AND_NOMINAL_TERMS_QUALIFIED_REALIZATION_CONDITIONAL",
        "record_id": snapshot["record_id"], "start": entry.isoformat(), "end": end.isoformat(),
        "snapshot_sha256_normalized": normalized_text_and_sha256(INPUT)[1],
        "comparison_sha256_normalized": normalized_text_and_sha256(COMPARISON_OUTPUT)[1],
        "direct_cashflow_sha256_normalized": normalized_text_and_sha256(CASHFLOW_PATH)[1],
        "code_sha256_normalized": normalized_text_and_sha256(Path(__file__))[1],
        "portfolio_aum_lakh": str(aum), "portfolio_minus_prior_day_factsheet_aum_lakh": str(aum_gap),
        "portfolio_weights_percent": {"gilt": cells["H24"], "treps": cells["H53"], "net_receivable": cells["H58"]},
        "gilt_isin": cells["D24"], "reported_market_mark_per_100": rounded(mark_per_unit, "0.0001"),
        "modeled_accrued_per_100": rounded(bond_accrued_per_unit, "0.0001"),
        "modeled_accrued_lakh": rounded(bond_accrued_lakh),
        "face_principal_at_par_lakh": rounded(quantity * face / lakh),
        "semiannual_coupon_lakh": rounded(quantity * semiannual_coupon / lakh, "0.0001"),
        "nominal_coupon_dates": [day.isoformat() for day in coupon_dates],
        "nominal_principal_due": maturity.isoformat(),
        "portfolio_factsheet_ytm_percent": factsheet["portfolio_ytm_percent"],
        "disclosed_holding_ytm_percent": cells["I24"],
        "dirty_pv_at_disclosed_bond_ytm_nominal_semiannual_actual365": rounded(pv_at_quoted, "0.0001"),
        "mark_convention_sensitivities": valuation,
        "prior_hurdle_gross_percent_at_0_28pct_ter": rounded(prior_hurdle * 100, RATE_PLACES),
        "prior_26_nov_direct_reference_post_tax_inr": reference["post_tax_nominal_inr"],
        "matched_31_oct_direct_fixed_4pct_post_tax_inr": rounded(matched_bonds[D("0.04")]),
        "breakevens": thresholds, "scenarios": cases,
        "live_quote": "DEFERRED", "paid_silver_history": "DEFERRED",
        "rbi_tbill_payment_timing": "OPEN", "investment_authorization": "NO_GO",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--workbook", type=Path, help="verify the locally saved SBI source workbook and worksheet")
    args = parser.parse_args()
    snapshot = load_json(INPUT)
    if args.workbook:
        verify_workbook(snapshot["portfolio"], args.workbook.resolve())
    with localcontext() as ctx:
        ctx.prec = 45
        result = build(snapshot)
    payload = json.dumps(result, indent=2) + "\n"
    if args.check:
        require(OUTPUT.read_text(encoding="utf-8") == payload, "frozen SBI holdings audit differs")
    else:
        OUTPUT.write_text(payload, encoding="utf-8", newline="\n")
    print(f"PASS: SBI October portfolio, {len(result['nominal_coupon_dates'])} nominal coupons, "
          f"{len(result['scenarios'])} scenario checks. NO_GO.")


if __name__ == "__main__":
    main()
