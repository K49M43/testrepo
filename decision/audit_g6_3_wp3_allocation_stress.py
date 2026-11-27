"""Challenge the frozen G6.3 allocation design and check its financial outputs."""
from __future__ import annotations

import hashlib
from datetime import date, timedelta
from decimal import Decimal as D, localcontext
from itertools import product
from math import fsum

from g6_3_wp2_dated import OUT as WP2_RESULTS
from g6_3_wp3_allocation_stress import (
    DEFAULT_SCHEDULE_PATH, FROZEN_PROTOCOL_COMMIT, PROTOCOL, RESULTS, bond_terms, drawdown, mark_path,
    matched_dates, read, read_schedule, reference_funding, require, snapshots,
)


PROTOCOL_SHA256 = "50b944c892b097032ab5ca3222e74486d9b9015b2d49abf16932f2b5515cc1b0"


def near(left, right, label, tolerance=D("0.00501")):
    require(abs(D(left) - D(right)) <= tolerance, f"{label}: {left} != {right}")


def reject(function, *args):
    try:
        function(*args)
    except ValueError:
        return
    raise AssertionError(f"invalid input accepted by {function.__name__}")


def boundary_checks():
    a = date(2034, 1, 31)
    b, c = a + timedelta(days=30), a + timedelta(days=60)
    near(drawdown([(a, D(100), D(100)), (b, D(180), D(100)), (c, D(220), D(40))])["percent"],
         20, "cash-flow adjustment must expose drawdown")
    near(drawdown([(a, D(100), D(100)), (b, D(230), D(130))])["percent"],
         0, "flat investments with contributions must have no drawdown")
    reject(drawdown, [(a, D(100), D(0))])
    taper = mark_path(D(100), D(0), a, b, D("0.8"), c)
    require([taper(day) for day in (a, b, b + timedelta(days=15), c)] == list(map(D, (100, 80, 90, 100))),
            "SBI maturity taper or shock order changed")
    unshifted, shifted = bond_terms(D(0)), bond_terms(D("0.015"))
    require(unshifted["coupons"] == shifted["coupons"] and unshifted["maturity"] == shifted["maturity"]
            and shifted["mark"](b) < unshifted["mark"](b), "yield shock must leave coupons and maturity intact")
    sample = {"nav_replay_panels": {"test": {"latest_common_observed_endpoints": ["2026-01-30", "2026-03-31"]}}}
    spec = {"panel": "test", "first_interval": 0, "interval_count": 1}
    reject(matched_dates, sample, spec, date(2026, 4, 30))
    sample["nav_replay_panels"]["test"]["latest_common_observed_endpoints"][1] = "2026-02-27"
    reject(matched_dates, sample, spec, date(2026, 2, 27))
    events = [{"id": 1, "date": a.isoformat(), "event": "contribution", "cash_delta": "100"},
              {"id": 2, "date": a.isoformat(), "event": "acquisition", "asset": "gold",
               "lot": "lot", "units": "1", "cash_delta": "-100"},
              {"id": 3, "date": b.isoformat(), "event": "sale", "lot": "lot", "units": "1",
               "proceeds": "90", "fee": "1", "cash_delta": "0"},
              {"id": 4, "date": c.isoformat(), "event": "cash_release", "trade_event": "3", "cash_delta": "89"}]
    observed = snapshots(events, [(a, D(100)), (b, D(0)), (c, D(0))], {"gold": lambda day: D(100)}, D(89))
    require([row[1] for row in observed] == list(map(D, (100, 89, 89))), "sale settlement double-counted or lost its claim")


def amounts(row, schedule, historical):
    payments = row["payments"]
    funding = reference_funding(schedule, payments)
    require(row["end"] == funding[-1][0].isoformat(), "report end changed")
    near(row["contributions"], sum(amount for _, amount in funding), "frozen funding")
    nominal = D(row["after_tax_nominal"])
    real = nominal / (1 + D(row["inflation"])) ** (D(payments) / 12)
    near(row["after_tax_real"], real, "real conversion", D("0.01001"))
    require(D(row["pre_tax_nominal_after_product_costs"]) >= nominal > 0 and
            0 <= D(row["monthly_max_drawdown"]["percent"]) <= 100, "wealth or drawdown outside bounds")
    for metric, target in (("floor_shortfall", 9_000_000), ("stretch_shortfall", 10_000_000)):
        if historical:
            require(row[metric] is None, "historical tape published a 2036 shortfall")
        else:
            near(row[metric], max(D(0), target - real), metric, D("0.01001"))
    xirr = row["xirr_nominal_after_modeled_tax"]
    require(xirr["status"] == "PASS", "expected single-sign-change portfolio XIRR")
    base = 1 + float(xirr["annual_percent"]) / 100
    last = funding[-1][0]
    factors = [((last - day).days / 365, float(amount)) for day, amount in funding]
    residual = float(nominal) - fsum(amount * base ** t for t, amount in factors)
    bound = fsum(t * amount * (base + 0.000000501) ** (t - 1) for t, amount in factors) * 0.000000501
    require(abs(residual) <= bound + 0.01, "dated money-weighted return does not reconcile")


def main():
    protocol, results = read(PROTOCOL), read(RESULTS)
    frozen = hashlib.sha256(PROTOCOL.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    require(frozen == PROTOCOL_SHA256 and results["protocol_commit"] == FROZEN_PROTOCOL_COMMIT,
            "stress protocol diverged from its pre-results version")
    require(not results["probability_qualified"] and not results["decision_grade_personal_output"]
            and all(results[key] == value for key, value in protocol["evidence"].items()),
            "unqualified uses or source status changed")
    schedule = read_schedule(DEFAULT_SCHEDULE_PATH)
    boundary_checks()
    forward = {(r["scenario"], r["route"], r["policy"]): r for r in results["forward"]}
    expected = set(product((s["id"] for s in protocol["forward"]), protocol["sovereign_routes"], protocol["policies"]))
    require(len(forward) == len(results["forward"]) and set(forward) == expected, "forward matrix incomplete or duplicated")
    historical = {(r["scenario"], r["route"], r["policy"]): r for r in results["historical"]}
    expected_history = {(s["id"], s["gilt"], p) for s in protocol["historical"] for p in protocol["policies"]}
    expected_history.update(("matched_full", route, "diversified_silver") for route in ("lic", "sbi"))
    require(len(historical) == len(results["historical"]) and set(historical) == expected_history,
            "historical design incomplete or duplicated")
    for row in forward.values():
        amounts(row, schedule, False)
    for row in historical.values():
        amounts(row, schedule, True)
    prior = {row["case"]: row for row in read(WP2_RESULTS)["results"]}
    for route in protocol["sovereign_routes"]:
        reference = forward["reference", route, "diversified"]
        earlier = prior[f"120-{route}-full"]
        near(reference["after_tax_nominal"], earlier["remaining_after_tax_set-aside"], "WP2 nominal baseline")
        near(reference["after_tax_real"], earlier["inflation"]["0.06"]["remaining_real"], "WP2 real baseline")
    print(f"PASS: audited the frozen design, {len(forward)} forward stresses, {len(historical)} replays and WP2 anchors.")


if __name__ == "__main__":
    with localcontext() as context:
        context.prec = 42
        main()
