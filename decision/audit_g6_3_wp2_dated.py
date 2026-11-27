"""Independently roll the frozen WP2 event trace and challenge its boundary cases."""
from __future__ import annotations

import argparse
import calendar
import hashlib
import json
from collections import defaultdict
from dataclasses import replace
from datetime import date, timedelta
from decimal import Decimal as D, localcontext
from pathlib import Path

from capital_gain_loss_schedule import Gain, Loss
from g6_3_wp2_dated import (
    BASE_INPUT, OUT, SOVEREIGN_INPUT, Policy, allocate_losses, check_funding, check_settlement, dated_xirr, require, simulate,
)


ZERO = D(0)
TOLERANCE = D("0.00501")


def near(left, right, label):
    require(abs(left - right) <= TOLERANCE, f"{label}: {left} != {right}")


def independent_tax(ordinary, gains, cess):
    """Check the synthetic resident fixture without the production tax calculator."""
    def statutory_round(value):
        return D(((int(value) + 5) // 10) * 10)

    special = [gains.get(bucket, ZERO) for bucket in ("section196", "section197", "section198")]
    total = statutory_round(ordinary + sum(special))
    require(total > 1_200_000, "outside independent no-rebate scope")

    def tax_and_surcharge(income):
        normal = income - sum(special)
        adjusted = list(special)
        shortfall = max(ZERO, D(400000) - normal)
        if shortfall:
            positive = [i for i, value in enumerate(adjusted) if value]
            require(len(positive) <= 1, "unsupported basic exemption composition")
            if positive:
                index = positive[0]
                adjusted[index] = max(ZERO, adjusted[index] - shortfall)
        normal_tax = sum(max(ZERO, normal - start) * D("0.05") for start in range(400000, 2400001, 400000))
        special_tax = adjusted[0] * D("0.20") + (adjusted[1] + max(ZERO, adjusted[2] - 125000)) * D("0.125")
        surcharge = (D("0.25") if income > 20_000_000 and normal > 20_000_000 else
                     D("0.15") if income > 10_000_000 else D("0.10") if income > 5_000_000 else ZERO)
        return normal_tax * (1 + surcharge) + special_tax * (1 + min(surcharge, D("0.15")))

    due = tax_and_surcharge(total)
    threshold = max((D(x) for x in (5_000_000, 10_000_000, 20_000_000) if total > x), default=None)
    if threshold is not None and due > total - threshold:
        excess = total - threshold
        require(sum(special) <= threshold, "marginal relief needs an unsupported reference")
        due = min(due, tax_and_surcharge(threshold) + excess)
    return statutory_round(due * (1 + cess))


def check_trace(path, expected, charges, sbi_stamp):
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == expected["trace_sha256"], f"trace digest mismatch: {path.name}")
    events = [json.loads(line) for line in raw.splitlines()]
    require(len(events) == expected["event_count"], "trace length changed")
    cash = contributions = withdrawals = tax = ZERO
    lots, receipts, flows = {}, {}, []
    sales, ordinary_income = {}, defaultdict(D)
    withholding, expected_withholding = defaultdict(D), {}
    withholding_rate = D(expected["coupon_withholding_rate"])
    cess = D(expected["cess"])
    friction = {asset: D(expected["etf_friction_bps_per_side"]) / 10_000 for asset in ("lic", "gold", "silver")}
    friction["bond"] = D(expected["bond_friction_bps_per_side"]) / 10_000
    entry_rates = {**friction, "sbi": sbi_stamp, "equity": D(charges["equity_fund_entry_stamp_percent"]) / 100}
    exit_rates = {**friction, "equity": D(charges["equity_fund_exit_stt_percent"]) / 100, "sbi": ZERO}
    loads = {"equity": "equity_fund", "sbi": "sbi"}
    pending_settlements = []
    end = date.fromisoformat(expected["end"])
    first = date.fromisoformat(expected["first"])
    previous = first
    for i, row in enumerate(events, 1):
        when = date.fromisoformat(row["date"])
        year_start = when.year - int(when.month < 4)
        year = f"{year_start}-{(year_start + 1) % 100:02d}"
        kind = row["event"]
        delta = D(row["cash_delta"])
        require(row["id"] == i and previous <= when <= end and row["tax_year"] == year, "event or fiscal sequence changed")
        previous = when
        if kind == "acquisition":
            units, mark, fee, basis = (D(row[key]) for key in ("units", "mark", "fee", "basis"))
            require(row["lot"] not in lots and units > ZERO and mark > ZERO, "duplicate or invalid purchased lot")
            if row["asset"] in ("bond", "lic", "gold", "silver"):
                require(units == int(units), "fractional exchange lot")
            near(units * mark * entry_rates[row["asset"]], fee, "product entry fee")
            near(units * mark + fee, -delta, "acquisition debit")
            near(D(row["budget"]) + delta, D(row["unspent"]), "unspent allocation")
            near(units * mark - (D(row["accrued_paid"]) if row["basis_case"] == "clean" else ZERO),
                 basis, "acquisition tax basis")
            lots[row["lot"]] = [row["asset"], when, units, basis]
        elif kind in ("sale", "maturity"):
            lot_id = row["lot"]
            asset, bought, balance, basis = lots[lot_id]
            require(lot_id == next(key for key, lot in lots.items() if lot[0] == asset), "FIFO order changed")
            units, price, removed = (D(row[k]) for k in ("units", "mark", "basis"))
            ready = date.fromisoformat(row["available"])
            require(bought < when <= ready <= end and ZERO < units <= balance and not delta, "invalid disposal timing or units")
            anniversary = date(bought.year + 1, bought.month,
                               min(bought.day, calendar.monthrange(bought.year + 1, bought.month)[1]))
            if asset in ("lic", "sbi"):
                bucket = "section76"
            elif asset == "equity":
                bucket = "section198" if when > anniversary else "section196"
            else:
                bucket = "section197" if when > anniversary else "ordinary_stcg"
            require(row["bucket"] == bucket, "capital-gain bucket or holding period changed")
            near(removed, basis / balance * units, "disposed basis")
            near(units * price, D(row["proceeds"]), "sale gross")
            fee = D(row["fee"])
            load = ZERO
            if asset in loads and (when - bought).days <= charges[f"{loads[asset]}_exit_load_up_to_days"]:
                parameter = "sbi_exit_load_percent_sensitivity" if asset == "sbi" else "equity_fund_exit_load_percent"
                load = units * price * D(charges[parameter]) / 100
            exit_rate = ZERO if asset == "bond" and kind == "maturity" else exit_rates[asset]
            near(units * price * exit_rate + load, fee, "product exit fee")
            cash_due = units * price - fee
            receipts[str(i)] = (ready, cash_due)
            pending_settlements.append((when, ready))
            # Only the exit load reduces sale consideration under this
            # fixture. The residual charge is kept outside tax basis.
            near(units * price - removed - D(row["ordinary_accrued_inr"]) - load, D(row["gain"]), "realized gain")
            sales[str(i)] = (year, row["bucket"], D(row["gain"]))
            ordinary_income[year] += D(row["ordinary_accrued_inr"])
            if units == balance:
                del lots[lot_id]
            else:
                lots[lot_id][2:] = [balance - units, basis - removed]
        elif kind == "cash_release":
            ready, due = receipts.pop(row["trade_event"])
            require(when == ready, "sale moved into cash before its release date")
            near(delta, due, "cash release")
        elif kind == "coupon":
            asset, acquired, qty, _ = lots[row["lot"]]
            require(asset == "bond" and acquired < when and when.month in (5, 11) and when.day == 11,
                    "coupon timing or entitlement differs")
            near(qty * D("3.47"), delta, "coupon amount")
            near(delta, D(row["gross_coupon"]), "coupon gross")
            if withholding_rate:
                expected_withholding[(when, row["lot"])] = delta * withholding_rate
            ordinary_income[year] += delta
        elif kind == "coupon_withholding":
            due = expected_withholding.pop((when, row["lot"]))
            near(-delta, due, "coupon withholding")
            withholding[year] -= delta
            tax -= delta
        elif kind == "reserve_interest":
            interest_start = date.fromisoformat(row["interest_start"])
            require(first <= interest_start < when, "invalid reserve accrual interval")
            factor = (1.0 + float(expected["reserve_rate"])) ** ((when - interest_start).days / 365)
            near(delta, D(str(float(cash) * (factor - 1))), "reserve compounding")
            ordinary_income[year] += delta
        elif kind == "tax_reserve":
            require((when.month, when.day) == (3, 31) or when == end, "tax checkpoint moved")
            year_gains = defaultdict(D)
            for _, (fy, bucket, value) in sales.items():
                if fy == year and value > ZERO:
                    year_gains[bucket] += value
            used_losses, used_gains = defaultdict(D), defaultdict(D)
            for offset in row["offsets"]:
                loss_id, gain_id = offset["loss_event_id"], offset["gain_event_id"]
                loss, gain = sales[loss_id], sales[gain_id]
                amount = D(offset["amount_inr"])
                require(loss[0] == gain[0] == year and loss[2] < ZERO < gain[2] and amount > ZERO
                        and (loss[1] not in ("section197", "section198") or gain[1] in ("section197", "section198")),
                        "illegal capital loss allocation")
                used_losses[loss_id] += amount
                used_gains[gain_id] += amount
                require(used_losses[loss_id] + loss[2] <= D("1e-25") and used_gains[gain_id] - gain[2] <= D("1e-25"),
                        "double use of a tax offset")
                year_gains[gain[1]] -= amount
            require({k for k, value in year_gains.items() if value} <= set(row["net_capital_gains"]), "missing tax gain bucket")
            for bucket, amount in row["net_capital_gains"].items():
                near(year_gains[bucket], D(amount), "annual net gain")
            near(ordinary_income[year], D(row["annual_income"]), "coupon/interest annual total")
            external = D(expected["synthetic_external_ordinary_income"])
            ordinary = external + ordinary_income[year] + year_gains["ordinary_stcg"] + year_gains["section76"]
            near(independent_tax(ordinary, year_gains, cess), D(row["tax_with_external"]), "independent annual tax")
            near(independent_tax(external, {}, cess), D(row["external_only_tax"]), "independent external-only tax")
            credit = withholding.pop(year, ZERO)
            near(credit, D(row["withholding_credit"]), "withholding credit")
            near(D(row["tax_with_external"]) - D(row["external_only_tax"]) - credit,
                 -delta, "incremental remaining tax set-aside")
            tax -= delta
        elif kind == "contribution":
            contributions += delta
            flows.append((when, -delta))
        elif kind == "withdrawal":
            require(not receipts, "withdrawal relies on unsettled proceeds")
            withdrawals -= delta
            flows.append((when, -delta))
        else:
            require(kind == "unfilled_lot_to_reserve" and delta == ZERO
                    and D(row["budget"]) < D(row["one_unit_total_cost"]),
                    f"unexpected event {kind}")
        cash += delta
        near(cash, D(row["cash_after"]), "cash balance")
        require(cash >= -TOLERANCE, "cash became negative")
    require(not lots and not receipts and not expected_withholding and not withholding,
            "unclosed units, receivables or withholding")
    near(cash, D(expected["remaining_after_tax_set-aside"]), "terminal wealth")
    near(contributions, D(expected["contributed"]), "funding")
    near(withdrawals, D(expected["withdrawn"]), "withdrawals")
    near(tax, D(expected["tax_set_aside"]), "total nominal tax")
    for inflation, result in expected["inflation"].items():
        real = float(cash) / (1 + float(inflation)) ** (expected["payments"] / 12)
        near(D(str(real)), D(result["remaining_real"]), "real purchasing power")
    xirr = expected["xirr_after_tax"]
    if xirr["status"] == "PASS":
        ratio = 1 + float(xirr["annual_percent"]) / 100
        residual = sum(float(amt) * ratio ** (-(day - first).days / 365) for day, amt in [*flows, (end, cash)])
        # Rounded XIRRs use four decimal percentage points. The associated
        # NPV bound scales with dates and cash amounts.
        bound = sum(abs(float(amt)) * ((day - first).days / 365) / ratio
                    * ratio ** (-(day - first).days / 365) for day, amt in [*flows, (end, cash)]) * 0.000000501
        require(abs(residual) <= bound + 0.01, "XIRR independently disagrees with event trace")
    if expected["case"].endswith("-staged"):
        require(withdrawals == D("500000") and any(a < date(2036, 4, 1) and a < b for a, b in pending_settlements)
                and xirr["status"] == "AMBIGUOUS_MULTIPLE_SIGN_CHANGES", "staged withdrawal, sale or XIRR status lost")


def reject(function, *args):
    try:
        function(*args)
    except ValueError:
        return
    raise AssertionError(f"invalid case accepted by {function.__name__}")


def boundary_checks():
    a = date(2036, 3, 31)
    b = a + timedelta(days=1)
    reject(check_settlement, b, a, b)
    reject(check_settlement, a, b, a)
    reject(check_funding, [(b, D(1))], a)
    reject(check_funding, [(a, D(1)), (a, D(2))], b)
    one_year = (date(2026, 1, 1), date(2027, 1, 1))
    require(dated_xirr([(one_year[0], -100), (one_year[1], 250)])["annual_percent"] == "150.0000",
            "valid return outside old fixed bracket")
    require(dated_xirr([(one_year[0], -100), (one_year[1], 100)])["annual_percent"] == "0.0000",
            "zero-return XIRR case")
    require(dated_xirr([(one_year[0], -100), (one_year[1], 0)])["annual_percent"] is None, "zero recovery has no root")
    gain = Gain("g", "g", "lot", "2034-35", D(10), "short", "ordinary_stcg")
    valid = Loss("l", "l", "lot2", "2026-27", D(10), "short", True, "synthetic timely return evidence")
    result = allocate_losses("2034-35", [gain], [], [valid])
    require(result.candidate_gains_after_explicit_offsets_by_bucket["ordinary_stcg"] == ZERO, "eighth-year expiry boundary")
    reject(allocate_losses, "2035-36", [], [], [valid])
    unverified = Loss("l", "l", "lot2", "2026-27", D(10), "short", False)
    reject(allocate_losses, "2034-35", [gain], [], [unverified])
    long_loss = Loss("ll", "ll", "lot3", "2034-35", D(10), "long", False)
    result = allocate_losses("2034-35", [gain], [long_loss])
    require(result.candidate_gains_after_explicit_offsets_by_bucket["ordinary_stcg"] == D(10),
            "long-term loss offset short-term gain")
    fractional_gain = replace(gain, amount_inr=D("1.00001"))
    fractional_losses = [replace(valid, loss_id=key, origin_tax_year="2034-35", amount_inr=D(amount))
                         for key, amount in (("a", "0.00002"), ("b", "2"))]
    with localcontext() as reduced:
        reduced.prec = 3
        result = allocate_losses("2034-35", [fractional_gain], fractional_losses)
    require(sum(D(row["amount_inr"]) for row in result.offset_trace) == fractional_gain.amount_inr
            and result.candidate_gains_after_explicit_offsets_by_bucket["ordinary_stcg"] == ZERO,
            "fractional offsets must exactly exhaust the gain")
    fixture = Policy(b, b, 0, 0, None, ZERO, None, ZERO, ZERO, D("3000000"), ZERO, ZERO, "clean", ZERO)
    reject(simulate, [(a, D(50))], {"bond": D(1)}, fixture, {"bond": lambda day: D(100)},
           {"bond": b - timedelta(days=2)}, {"coupons": {}, "accrued": lambda day: ZERO}, {})
    result = simulate([(a, D(50))], {"bond": D(1)}, fixture, {"bond": lambda day: D(100)}, {},
                      {"coupons": {}, "accrued": lambda day: ZERO}, {})
    require(result["cash"] == D(50) and any(row["event"] == "unfilled_lot_to_reserve" for row in result["trace"]),
            "below-one-unit allocation was lost or borrowed")
    result = simulate([(a, D(250)), (b, D(150))], {"gold": D(1)}, fixture, {"gold": lambda day: D(100)}, {}, {}, {},
                      apply_tax=False)
    require(result["cash"] == D(400) and result["xirr"]["annual_percent"] == "0.0000",
            "zero return, tax and cost did not preserve funded capital")
    staged = replace(fixture, end=date(2036, 4, 9), sale=date(2036, 4, 6), sale_lag=3,
                     early_sale=date(2036, 3, 30), early_fraction=D("0.5"),
                     withdrawal_date=date(2036, 4, 3), withdrawal=D(100))
    funding = [(date(2035, 3, 31), D(400))]
    prices = {"gold": lambda day: D(100)}
    reject(simulate, funding, {"gold": D(1)}, replace(staged, withdrawal_date=a), prices, {}, {}, {})
    reject(simulate, funding, {"gold": D(1)}, staged, {}, {}, {}, {})
    outcome = simulate(funding, {"gold": D(1)}, staged, prices, {}, {}, {}, apply_tax=False)
    sale = next(row for row in outcome["trace"] if row["event"] == "sale")
    receipt = next(row for row in outcome["trace"] if row["event"] == "cash_release"
                   and row["trade_event"] == str(sale["id"]))
    require((sale["tax_year"], sale["bucket"], receipt["tax_year"], receipt["date"]) ==
            ("2035-36", "ordinary_stcg", "2036-37", "2036-04-02"), "cross-year receipt changed the trade's tax year")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace_dir", type=Path)
    args = parser.parse_args()
    charges = json.loads(BASE_INPUT.read_text(encoding="utf-8"))["costs"]
    sbi_stamp = D(json.loads(SOVEREIGN_INPUT.read_text(encoding="utf-8"))["fund"]["stamp_duty_percent_of_subscription"]) / 100
    with localcontext() as ctx:
        ctx.prec = 42
        boundary_checks()
        cases = json.loads(OUT.read_text(encoding="utf-8"))["results"]
        for case in cases:
            check_trace(args.trace_dir / f"{case['case']}.jsonl", case, charges, sbi_stamp)
    print(f"PASS: independently reconciled {len(cases)} dated event traces, XIRRs, and tax/date boundaries")


if __name__ == "__main__":
    main()
