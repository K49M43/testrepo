"""Dated WP2 research scenarios with FIFO lots, settlements and annual tax."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from datetime import date, timedelta
from decimal import ROUND_FLOOR, localcontext
from functools import cache
from itertools import product
from math import exp, expm1, fsum
from pathlib import Path

from after_tax_event_ledger import LotState, tax_year_for
from audit_g6_3_exact_date_coverage import GOLD, LIC, MOTILAL, SBI_GILT, SILVER, load_marks, provenance
from capital_gain_loss_schedule import Gain, Loss, Offset, build_schedule
from g6_3_wp2_portfolio import (
    AUCTION, CASHFLOW_PATH, CONTRACT_PATH, COVERAGE, DEFAULT_SCHEDULE_PATH, D, INCLUDED_ACCRUAL,
    INPUT as BASE_INPUT, ONE, ROOT, SBI_HOLDINGS, SEPARATE_ACCRUAL, SOVEREIGN_INPUT, ZERO, accrued_days,
    cpi_factor, growth, long_term, read, read_schedule, reference_funding, require, rounded, validate_schedule_contract,
)
from ty2026_27_tax_components import TaxInput, _calculate_tax, calculate_tax, section516_round_rupees


EVIDENCE = ROOT / "research/g6_3/2026-11-27-wp2-dated"
INPUT = EVIDENCE / "inputs_v2.json"
OUT = EVIDENCE / "results_v2.json"
ACCRUAL_CASES = (SEPARATE_ACCRUAL, INCLUDED_ACCRUAL)
IDS = {"equity": MOTILAL, "gold": GOLD, "silver": SILVER, "lic": LIC, "sbi": SBI_GILT, "bond": "IN0020260025"}
INSTRUMENT_LINKS = {"equity": "Motilal SID and WP1 NAV", "gold": "WP1 unit-rebased AMFI NAV",
                    "silver": "WP1 AMFI NAV sensitivity", "lic": "WP1 AMFI NAV and LIC SID",
                    "sbi": "SBI SID and frozen-holdings accrual scenarios", "bond": "GoI coupon schedule and November RBI auction"}


def pct(value):
    return D(value) / 100


def check_funding(funding, end):
    days = [day for day, _ in funding]
    require(days and days == sorted(set(days)) and days[-1] <= end, "funding dates must be unique, ordered and within the horizon")
    require(all(amount.is_finite() and amount > ZERO for _, amount in funding), "invalid contribution amount")


def check_settlement(trade, settlement, end):
    require(trade <= settlement <= end, "settlement must follow trade and fall within this settled-cash scenario")


def dated_xirr(flows):
    """Solve single-sign-change cashflows in log-rate space. Flag ambiguous cases."""
    combined = defaultdict(float)
    for when, value in flows:
        combined[when] += float(value)
    dated = sorted((day, value) for day, value in combined.items() if value)
    if not dated or dated[0][1] >= 0 or dated[-1][1] <= 0:
        return {"status": "UNDEFINED_CASHFLOW_SIGNS", "annual_percent": None}
    if sum((a > 0) != (b > 0) for (_, a), (_, b) in zip(dated, dated[1:])) != 1:
        return {"status": "AMBIGUOUS_MULTIPLE_SIGN_CHANGES", "annual_percent": None}
    if fsum(amount for _, amount in dated) == 0:
        return {"status": "PASS", "annual_percent": "0.0000"}
    origin, end = dated[0][0], dated[-1][0]

    def npv(log_rate):
        # Anchor at the first or final date to avoid overflowing powers.
        anchor = origin if log_rate >= 0 else end
        return fsum(amt * exp(-log_rate * (day - anchor).days / 365)
                    for day, amt in dated)

    lo, hi = -1., 1.
    while npv(lo) < 0:
        lo *= 2
    while npv(hi) > 0:
        hi *= 2
    for _ in range(100):
        mid = (lo + hi) / 2
        if npv(mid) > 0:
            lo = mid
        else:
            hi = mid
    log_rate = (lo + hi) / 2
    require(abs(npv(log_rate)) < 0.001, "XIRR residual failed")
    if not -700 < log_rate < 70:
        return {"status": "LOG_RATE_OUTSIDE_FINITE_REPORTING_RANGE", "annual_percent": None}
    return {"status": "PASS", "annual_percent": rounded(D(str(expm1(log_rate))) * 100, "0.0001")}


def capital_bucket(kind, acquired, sold):
    if kind in ("lic", "sbi"):
        require(acquired >= date(2023, 4, 1), "pre-transition specified fund not supported")
        return "section76", "short"
    is_long = long_term(acquired, sold)
    if kind == "equity":
        return ("section198", "long") if is_long else ("section196", "short")
    return ("section197", "long") if is_long else ("ordinary_stcg", "short")


def allocate_losses(year, gains, losses, carried=()):
    # Allocation subtracts an offset while the validator adds it back. Both
    # operations must agree exactly, including fractions below a paisa.
    amounts = [row.amount_inr for row in (*gains, *losses, *carried)]
    if not amounts:
        return _allocate_losses(year, gains, losses, carried)
    require(all(amount.is_finite() for amount in amounts), "nonfinite capital gain or loss")
    exponent = min(amount.as_tuple().exponent for amount in amounts)
    digits = max(amount.adjusted() for amount in amounts) - exponent + 1
    with localcontext() as context:
        context.prec = max(context.prec, digits + len(str(len(amounts))))
        return _allocate_losses(year, gains, losses, carried)


def _allocate_losses(year, gains, losses, carried):
    # Explicit fixture policy. Constrained long losses first, then flexible short
    # losses. Within a class prefer older losses and the listed gain buckets.
    priority = {key: i for i, key in enumerate(("ordinary_stcg", "section76", "section196", "section197", "section198"))}
    remaining = {gain.gain_id: gain.amount_inr for gain in gains}
    ordered_gains = sorted(gains, key=lambda gain: (priority[gain.tax_bucket], gain.gain_id))
    all_losses = [*losses, *carried]
    offsets = []
    for loss in sorted(all_losses, key=lambda row: (row.character != "long", row.origin_tax_year, row.loss_id)):
        left = loss.amount_inr
        for gain in ordered_gains:
            if left and (loss.character == "short" or gain.character == "long"):
                used = min(left, remaining[gain.gain_id])
                if used:
                    offsets.append(Offset(loss.loss_id, gain.gain_id, used))
                    remaining[gain.gain_id] -= used
                    left -= used
    # The legacy validator has no ordinary-rate STCG bucket. Its compatibility
    # and expiry rules depend on short/long character, not on the rate. Verify
    # the amounts through its short-term bucket, then restore every real bucket
    # from the source gain ID before computing or reporting any tax.
    validated = build_schedule(
        year, [replace(gain, tax_bucket="section76") if gain.tax_bucket == "ordinary_stcg" else gain
               for gain in gains], all_losses, offsets,
    )
    actual_buckets = {gain.gain_id: gain.tax_bucket for gain in gains}
    gross = {bucket: ZERO for bucket in (*validated.gross_gains_by_bucket, "ordinary_stcg")}
    for gain in gains:
        gross[gain.tax_bucket] += gain.amount_inr
    allocations = {bucket: ZERO for bucket in gross}
    restored = []
    for row in validated.offset_trace:
        bucket = actual_buckets[row["gain_id"]]
        restored.append({**row, "tax_bucket": bucket})
        allocations[bucket] += D(row["amount_inr"])
    return replace(validated, gross_gains_by_bucket=gross, offsets_by_bucket=allocations, offset_trace=restored,
                   candidate_gains_after_explicit_offsets_by_bucket=
                   {key: amount - allocations[key] for key, amount in gross.items()})


def assessed_tax(inputs, cess):
    scope = "SUPPORTED_COMPONENT"
    try:
        result = calculate_tax(inputs)
    except NotImplementedError as error:
        if str(error) not in (
            "marginal-relief reference composition cannot preserve special income at this threshold",
            "basic-exemption allocation across multiple special-gain sections is not specified",
        ):
            raise
        result = _calculate_tax(inputs, apply_marginal_relief=False)
        boundary = max((D(x) for x in (5_000_000, 10_000_000, 20_000_000) if result.total_income > x), default=None)
        # Finance Act section 3(5). Tax at the boundary is nonnegative. If
        # excess income alone covers tax plus surcharge, relief cannot bind.
        if boundary is None or result.income_tax_after_rebate + result.surcharge_before_relief > result.total_income - boundary:
            raise
        scope = "RELIEF_CANNOT_BIND_BY_NONNEGATIVE_BOUND"
    return section516_round_rupees((result.income_tax_after_rebate + result.surcharge_after_relief) * (ONE + cess)), scope


@dataclass(frozen=True)
class Policy:
    end: date
    sale: date
    sale_lag: int
    sbi_lag: int
    early_sale: date | None
    early_fraction: D
    withdrawal_date: date | None
    withdrawal: D
    reserve: D
    ordinary_external: D
    etf_bps: D
    bond_bps: D
    bond_basis: str
    sbi_ter: D
    bond_redemption_lag: int = 0
    cess: D = D("0.04")
    coupon_withholding: D = ZERO

    def validate(self, first):
        require(first <= self.sale and (self.early_sale is None or first <= self.early_sale < self.sale),
                "invalid sale dates")
        require(all(isinstance(i, int) and i >= 0 for i in (self.sale_lag, self.sbi_lag, self.bond_redemption_lag)),
                "negative or non-integer settlement lag")
        for when in (self.sale, self.early_sale):
            if when:
                check_settlement(when, when + timedelta(days=self.sale_lag), self.end)
        require((self.early_sale is None and self.early_fraction == ZERO) or
                (self.early_sale is not None and ZERO < self.early_fraction < ONE), "invalid partial sale fraction")
        require((self.withdrawal_date is None and self.withdrawal == ZERO) or
                (self.withdrawal > ZERO and self.early_sale is not None and
                 self.early_sale + timedelta(days=self.sale_lag) <= self.withdrawal_date <= self.end),
                "withdrawal requires settled early proceeds")
        require(self.bond_basis in ("clean", "dirty") and ZERO <= self.reserve
                and ZERO <= self.etf_bps < 10_000 and ZERO <= self.bond_bps < 10_000
                and ZERO <= self.sbi_ter < ONE and self.ordinary_external.is_finite()
                and self.ordinary_external >= ZERO and ZERO <= self.cess < ONE
                and ZERO <= self.coupon_withholding < ONE, "invalid costs, tax context or bond basis")


def instrument_marks(observed, coverage):
    marks = {}
    for kind in ("equity", "gold", "silver", "lic", "sbi"):
        source = coverage["source_series"][IDS[kind]]
        path = ROOT / source["path"]
        require(provenance(path)["sha256_normalized"] == source["sha256_normalized"], "WP1 NAV source hash mismatch")
        series = load_marks(path, "date", source["value_field"])
        marks[kind] = [series[day] for day in observed]
    return marks


def simulate(funding, weights, policy, paths, maturities, bond, costs, *, opening_losses=(), apply_tax=True):
    """Record acquisitions, FIFO disposals, releases and a nonnegative cash balance."""
    end = policy.end
    check_funding(funding, end)
    first = funding[0][0]
    policy.validate(first)
    require(sum(weights.values()) == ONE and set(paths) == set(weights)
            and all(value > ZERO for value in weights.values()), "invalid allocation or missing asset price path")
    first_tax_year = int(tax_year_for(first)[:4])
    require(all(row.return_filed_under_263_1 and row.return_evidence_reference
                and 0 < first_tax_year - int(row.origin_tax_year[:4]) <= 8
                for row in opening_losses), "unverified, future-dated or expired opening carryforward")

    amounts = dict(funding)
    coupons = bond["coupons"] if "bond" in paths else {}
    cutoffs = {asset: min(policy.sale, maturities.get(asset, policy.sale)) for asset in paths}
    require(all(first <= day <= end for day in cutoffs.values()), "instrument exit is outside the funding horizon")
    fiscal_ends = {date(y, 3, 31) for y in range(first.year, end.year + 1) if first <= date(y, 3, 31) <= end}
    trade_dates = {policy.sale, *cutoffs.values(), *amounts, *fiscal_ends, end}
    trade_dates.update(day for day in coupons if first <= day <= cutoffs.get("bond", end))
    trade_dates.update(day for day in (policy.early_sale, policy.withdrawal_date) if day)
    dates = set(trade_dates)
    for day, lag in [(policy.sale, policy.sale_lag), (policy.early_sale, policy.sale_lag)]:
        if day is not None:
            dates.add(day + timedelta(days=lag))
    for asset, when in cutoffs.items():
        if maturities.get(asset) == when:
            lag = policy.sbi_lag if asset == "sbi" else policy.bond_redemption_lag
            available = when + timedelta(days=lag)
            check_settlement(when, available, end)
            dates.add(available)
    holdings = {asset: [] for asset in paths}
    claims, gains, losses, income = (defaultdict(list), defaultdict(list), defaultdict(list), defaultdict(D))
    withholding = defaultdict(D)
    trace, tax_summary, external_flows = [], {}, []
    cash = ZERO
    previous = first
    sequence = 0
    accrued_tax = ZERO

    def emit(day, event, delta=ZERO, **details):
        nonlocal cash, sequence
        sequence += 1
        cash += delta
        require(cash >= -D("0.000000001"), f"unfunded event {event} on {day}")
        trace.append({"id": sequence, "date": day.isoformat(), "tax_year": tax_year_for(day), "event": event,
                      "cash_delta": str(delta), "cash_after": str(cash), **details})
        return str(sequence)

    def release(day):
        for related, amount in claims.pop(day, []):
            emit(day, "cash_release", amount, trade_event=related)

    def sell(asset, day, qty, maturity):
        if qty == ZERO:
            return
        full = qty is None
        available = day + timedelta(days=(policy.sbi_lag if asset == "sbi" else policy.bond_redemption_lag)
                                   if maturity else policy.sale_lag)
        check_settlement(day, available, end)
        price = D(100) if asset == "bond" and maturity else paths[asset](day)
        require(price.is_finite() and price > ZERO, "invalid sale mark")
        if asset == "bond" and not maturity:
            clean = price - bond["accrued"](day)
            require(clean > ZERO, "nonpositive dirty-to-clean price bridge")
        for lot in holdings[asset]:
            if not full and not qty:
                break
            units = lot.units if full else min(qty, lot.units)
            ratio = units / lot.units
            basis, acquisition = lot.tax_basis_inr * ratio, lot.cash_basis_inr * ratio
            window = (day - lot.acquired).days
            require(window > 0, "sale before acquisition or same-day round trip")
            load = (pct(costs["equity_fund_exit_load_percent"]) if asset == "equity"
                    and window <= costs["equity_fund_exit_load_up_to_days"] else
                    pct(costs["sbi_exit_load_percent_sensitivity"]) if asset == "sbi"
                    and window <= costs["sbi_exit_load_up_to_days"] else ZERO)
            gross = units * price
            deduction = gross * load
            friction = gross * (pct(costs["equity_fund_exit_stt_percent"]) if asset == "equity" else
                                policy.bond_bps / 10_000 if asset == "bond" and not maturity else
                                policy.etf_bps / 10_000 if asset in ("gold", "silver", "lic") else ZERO)
            accrued_received = units * bond["accrued"](day) if asset == "bond" and not maturity else ZERO
            realized = gross - deduction - basis - accrued_received
            bucket, character = capital_bucket(asset, lot.acquired, day)
            event = emit(day, "maturity" if maturity else "sale", asset=asset, lot=lot.lot_id, units=str(units),
                         mark=str(price), basis=str(basis), proceeds=str(gross), fee=str(friction + deduction),
                         ordinary_accrued_inr=str(accrued_received), gain=str(realized), bucket=bucket,
                         available=available.isoformat())
            claims[available].append((event, gross - deduction - friction))
            year = tax_year_for(day)
            income[year] += accrued_received
            if realized > ZERO:
                gains[year].append(Gain(event, event, lot.lot_id, year, realized, character, bucket))
            elif realized < ZERO:
                losses[year].append(Loss(event, event, lot.lot_id, year, -realized, character, False))
            lot.units -= units
            lot.cash_basis_inr -= acquisition
            lot.tax_basis_inr -= basis
            if not full:
                qty -= units
        require(full or qty == ZERO, "FIFO sale exceeded the available units")
        holdings[asset] = [lot for lot in holdings[asset] if lot.units]

    carried = list(opening_losses)
    for day in sorted(dates):
        year = tax_year_for(day)
        accrued = cash * (growth(policy.reserve, previous, day) - ONE)
        if accrued:
            emit(day, "reserve_interest", accrued, interest_start=previous.isoformat())
            income[year] += accrued
        previous = day
        release(day)
        if day in coupons:
            for lot in holdings["bond"]:
                amt = lot.units * coupons[day]
                if amt:
                    withheld = amt * policy.coupon_withholding if apply_tax else ZERO
                    emit(day, "coupon", amt, asset="bond", lot=lot.lot_id, units=str(lot.units),
                         gross_coupon=str(amt))
                    if withheld:
                        emit(day, "coupon_withholding", -withheld, lot=lot.lot_id)
                        withholding[year] += withheld
                    income[year] += amt
        for asset in paths:
            units = sum((lot.units for lot in holdings[asset]), ZERO)
            if day == cutoffs[asset]:
                sell(asset, day, None, maturities.get(asset) == day)
            elif day == policy.early_sale and day < cutoffs[asset]:
                amount = units * policy.early_fraction
                sell(asset, day, amount.to_integral_value(rounding=ROUND_FLOOR)
                     if asset in ("bond", "lic", "gold", "silver") else amount, False)
        release(day)
        if day in amounts:
            contribution = amounts[day]
            emit(day, "contribution", contribution)
            external_flows.append((day, -contribution))
            for asset, weight in weights.items():
                if day >= cutoffs[asset]:
                    continue
                budget = contribution * weight
                mark = paths[asset](day)
                require(mark.is_finite() and mark > ZERO, f"invalid acquisition mark for {asset} on {day}")
                fee_rate = (pct(costs["equity_fund_entry_stamp_percent"]) if asset == "equity" else
                            pct(costs["sbi_stamp_percent"]) if asset == "sbi" else
                            (policy.bond_bps if asset == "bond" else policy.etf_bps) / 10_000)
                units = budget / (mark * (ONE + fee_rate))
                if asset in ("bond", "lic", "gold", "silver"):
                    units = units.to_integral_value(rounding=ROUND_FLOOR)
                if not units:
                    emit(day, "unfilled_lot_to_reserve", asset=asset, budget=str(budget),
                         one_unit_total_cost=str(mark * (ONE + fee_rate)))
                    continue
                principal, fee = units * mark, units * mark * fee_rate
                if asset in ("equity", "sbi"):
                    principal = budget / (ONE + fee_rate)
                    fee = budget - principal
                purchased_accrual = units * bond["accrued"](day) if asset == "bond" else ZERO
                basis = principal if asset != "bond" or policy.bond_basis == "dirty" else principal - purchased_accrual
                lot_id = f"{asset}-{day}"
                emit(day, "acquisition", -principal - fee, asset=asset, lot=lot_id, units=str(units), mark=str(mark),
                     basis=str(basis), fee=str(fee), budget=str(budget), unspent=str(budget - principal - fee),
                     accrued_paid=str(purchased_accrual), basis_case=policy.bond_basis if asset == "bond" else "invested")
                holdings[asset].append(LotState(lot_id, IDS[asset], day, units, principal, basis,
                                                INSTRUMENT_LINKS[asset], "SCENARIO"))
        if day == policy.withdrawal_date:
            emit(day, "withdrawal", -policy.withdrawal)
            external_flows.append((day, policy.withdrawal))
        if apply_tax and (day in fiscal_ends or day == end):
            eligible = [loss for loss in carried if 0 < int(year[:4]) - int(loss.origin_tax_year[:4]) <= 8]
            schedule = allocate_losses(year, gains[year], losses[year], eligible)
            buckets = schedule.candidate_gains_after_explicit_offsets_by_bucket
            external, _ = assessed_tax(TaxInput(ordinary_income=policy.ordinary_external), policy.cess)
            assessed, tax_scope = assessed_tax(TaxInput(
                ordinary_income=policy.ordinary_external + income[year] + buckets.get("ordinary_stcg", ZERO),
                section76_stcg=buckets["section76"], section196_stcg=buckets["section196"],
                section197_ltcg=buckets["section197"], section198_ltcg=buckets["section198"],
                section76_eligible=True, section196_eligible=True, section197_eligible=True,
                section198_eligible=True), policy.cess)
            liability = assessed - external
            already_paid = withholding[year]
            require(liability >= already_paid, "refund or negative incremental tax outside this fixture")
            accrued_tax += liability
            emit(day, "tax_reserve", already_paid - liability, assessment="year_end" if day in fiscal_ends else "terminal",
                 withholding_credit=str(already_paid),
                 tax_scope=tax_scope, annual_income=str(income[year]), tax_with_external=str(assessed),
                 external_only_tax=str(external), net_capital_gains={key: str(value) for key, value in buckets.items()},
                 offsets=schedule.offset_trace, unallocated_losses={key: str(value)
                                                                    for key, value in schedule.unallocated_losses.items()})
            tax_summary[year] = {"incremental_tax": str(liability), "ordinary_income": str(income[year]),
                                 "net_capital_gains": {key: str(value) for key, value in buckets.items()},
                                 "offsets": schedule.offset_trace, "unallocated_losses":
                                     {key: str(value) for key, value in schedule.unallocated_losses.items()}}
            eligible_ids = {loss.loss_id for loss in eligible}
            carried = [loss for loss in carried if loss.loss_id not in eligible_ids]
            carried += [Loss(loss.loss_id, loss.source_event_id, loss.lot_id, loss.origin_tax_year,
                             schedule.carryforward_losses[loss.loss_id], loss.character, True,
                             loss.return_evidence_reference) for loss in eligible
                        if loss.loss_id in schedule.carryforward_losses]
    require(not claims and not any(holdings.values()), "unsettled cash or residual units at the endpoint")
    require(abs(sum((D(event["cash_delta"]) for event in trace), ZERO) - cash) < D("0.000000001"),
            "cash trace does not reconcile")
    return {"cash": cash, "total_tax": accrued_tax, "tax_years": tax_summary, "trace": trace,
            "xirr": dated_xirr([*external_flows, (end, cash)])}


def stable_json(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def summarize(case, executed, before_tax, before_costs, funding, months, policy, contract, trace_dir):
    trace = executed["trace"]
    contents = "".join(stable_json(row) + "\n" for row in trace)
    if trace_dir is not None:
        trace_dir.mkdir(parents=True, exist_ok=True)
        (trace_dir / f"{case}.jsonl").write_text(contents, encoding="utf-8", newline="\n")
    settled = executed["cash"]
    require(settled <= before_tax["cash"] + D("0.000001") and settled >= ZERO, "tax increased assessed cash")
    cpi = {}
    for inflation in contract["inflation_scenarios"]["annual_compound_fractions"]:
        factor = cpi_factor(D(inflation), months)
        real = settled / factor
        real_withdrawal = (policy.withdrawal / (ONE + D(inflation)) **
                           (D((policy.withdrawal_date - funding[0][0]).days) / 365)
                           if policy.withdrawal_date else ZERO)
        cpi[inflation] = {"remaining_real": rounded(real), "real_withdrawals_separate": rounded(real_withdrawal),
                          "floor_shortfall_before_withdrawals_credit": rounded(max(ZERO, D(9_000_000) - real))
                          if months > 48 else None}
    return {"case": case, "first": funding[0][0].isoformat(), "end": policy.end.isoformat(), "payments": months,
            "reserve_rate": str(policy.reserve), "synthetic_external_ordinary_income": str(policy.ordinary_external),
            "cess": str(policy.cess), "coupon_withholding_rate": str(policy.coupon_withholding),
            "etf_friction_bps_per_side": str(policy.etf_bps), "bond_friction_bps_per_side": str(policy.bond_bps),
            "contributed": rounded(sum(amount for _, amount in funding)), "withdrawn": rounded(policy.withdrawal),
            "before_explicit_costs_and_taxes_remaining": rounded(before_costs["cash"]),
            "after_explicit_costs_before_taxes_remaining": rounded(before_tax["cash"]),
            "remaining_after_tax_set-aside": rounded(settled), "tax_set_aside": rounded(executed["total_tax"]),
            "xirr_before_tax": before_tax["xirr"], "xirr_after_tax": executed["xirr"], "inflation": cpi,
            "same_year_loss_offsets": rounded(sum((D(offset["amount_inr"]) for year in executed["tax_years"].values()
                                                      for offset in year["offsets"]), ZERO)),
            "cash_invariants": {"unsettled_at_endpoint": 0, "unclosed_lots_at_endpoint": 0},
            "event_count": len(trace), "trace_sha256": hashlib.sha256(contents.encode()).hexdigest(),
            "event_types": dict(sorted(Counter(row["event"] for row in trace).items()))}


def bond_terms(auction_shift):
    source = read(CASHFLOW_PATH)
    coupons = {date.fromisoformat(row["nominal_coupon_date"]): D(row["coupon_per_100_face_inr"])
               for row in source["coupon_events"]}
    maturity = max(coupons)
    require(source["isin"] == IDS["bond"] and len(coupons) == 20, "unexpected government bond terms")
    ytm = pct(read(AUCTION)["primary_quotes"]["weighted_average"]["nominal_ytm_percent"]) + auction_shift
    require(ytm > ZERO, "nonpositive assumed bond yield")
    days = sorted(coupons)
    first = date(2026, 5, 11)

    @cache
    def mark(day):
        require(first <= day < maturity, "bond has no modeled trade mark outside its life")
        return sum((coupons[d] + (100 if d == maturity else 0)) /
                   (ONE + ytm / 2) ** (D(accrued_days(day, d)) / 180) for d in days if d > day)

    def accrued(day):
        return D("6.94") * D(accrued_days(max([first, *(d for d in days if d <= day)]), day)) / 360

    return {"coupons": coupons, "maturity": maturity, "mark": mark, "accrued": accrued}


def build(trace_dir=None):
    cfg, base, coverage, contract = read(INPUT), read(BASE_INPUT), read(COVERAGE), read(CONTRACT_PATH)
    terms, holdings = read(SOVEREIGN_INPUT), read(SBI_HOLDINGS)
    schedule = read_schedule(DEFAULT_SCHEDULE_PATH)
    validate_schedule_contract(schedule, contract)
    expected_flags = {"live_quote": "DEFERRED", "paid_silver_history": "DEFERRED",
                      "rbi_tbill_payment_timing": "OPEN", "investment_authorization": "NO_GO"}
    require(all(coverage[key] == value for key, value in expected_flags.items()), "evidence exceptions differ")
    selected = next(row for row in coverage["candidate_inclusion"] if row["candidate_id"] == SBI_GILT)
    require(tuple(selected["forward_accrual_cases"]) == ACCRUAL_CASES, "both SBI accrual cases required")
    panels = coverage["nav_replay_panels"]
    points = panels["sbi_plus_gold_silver"]["latest_common_observed_endpoints"]
    require(points == panels["lic_plus_gold_silver"]["latest_common_observed_endpoints"][-49:] and len(points) == 49,
            "expected 48 matched NAV intervals")
    observed = list(map(date.fromisoformat, points))
    require(all((b.year - a.year) * 12 + b.month - a.month == 1
                for a, b in zip(observed, observed[1:])), "gap or duplicate in NAV replay")
    marks = instrument_marks(observed, coverage)
    prices_free = {**base["costs"], "equity_fund_entry_stamp_percent": "0", "equity_fund_exit_stt_percent": "0",
                   "equity_fund_exit_load_percent": "0", "sbi_exit_load_percent_sensitivity": "0", "sbi_stamp_percent": "0"}
    costs = {**base["costs"], "sbi_stamp_percent": terms["fund"]["stamp_duty_percent_of_subscription"]}
    rows = []

    def run(case, funding, weights, policy, paths, paths_free, maturities, bond, horizon):
        actual = simulate(funding, weights, policy, paths, maturities, bond, costs)
        pretax = simulate(funding, weights, policy, paths, maturities, bond, costs, apply_tax=False)
        no_costs = simulate(funding, weights, replace(policy, etf_bps=ZERO, bond_bps=ZERO), paths_free,
                            maturities, bond, prices_free, apply_tax=False)
        rows.append(summarize(case, actual, pretax, no_costs, funding, horizon, policy, contract, trace_dir))

    funding = reference_funding(schedule, 48)
    end = funding[-1][0]
    require(observed[-1] < funding[0][0], "NAV replay has a source-date look-ahead")
    external = D(cfg["ordinary_external_income"])
    default_etf = D(base["costs"]["etf_assumed_all_in_friction_bps_per_side"])
    default_bond = D(base["costs"]["direct_bond_entry_cost_bps"])
    replay = Policy(end, end, 0, 0, None, ZERO, None, ZERO, ZERO, external, default_etf, default_bond, "clean", ZERO)
    for gilt, (label, mix) in product(("lic", "sbi"), base["portfolio_weights"].items()):
        weights = {gilt if role == "gilt" else role: D(value) for role, value in mix.items() if D(value)}
        paths = {asset: dict(zip((day for day, _ in funding), marks[asset])).__getitem__ for asset in weights}
        run(f"replay-{gilt}-{label}", funding, weights, replay, paths, paths, {}, {}, 48)

    reference = next(row for row in base["forward_returns"] if row["label"] == "reference")
    for horizon, route in product((120, 122), ("lic", "bond", *ACCRUAL_CASES)):
        funding = reference_funding(schedule, horizon)
        end, first = funding[-1][0], funding[0][0]
        policy = Policy(end, end - timedelta(days=cfg["sale_lag_calendar_days"]), cfg["sale_lag_calendar_days"],
                        base["sbi_maturity_cash_availability_lag_calendar_days"], None, ZERO, None, ZERO,
                        pct(reference["reserve_gross_pct"]), external, default_etf, default_bond, "clean",
                        pct(reference["sbi_ter_pct"]), cfg["bond_redemption_lag_calendar_days"])
        cases = {"full": (policy, ZERO),
                 "staged": (replace(policy, early_sale=date.fromisoformat(cfg["early_sale"]),
                                    early_fraction=D(cfg["early_fraction"]),
                                    withdrawal_date=date.fromisoformat(cfg["withdrawal_date"]),
                                    withdrawal=D(cfg["withdrawal_inr"])), ZERO)}
        if horizon == 120:
            cases.update({"higher_etf_friction": (replace(policy, etf_bps=D(25)), ZERO),
                          "higher_reserve": (replace(policy, reserve=D("0.06")), ZERO),
                          "tax_context": (replace(policy, ordinary_external=D(cfg["stress_external_income"])), ZERO),
                          "higher_cess": (replace(policy, cess=D(cfg["stress_cess"])), ZERO),
                          "lower_equity_tracking": (policy, ZERO)})
            if route == "bond":
                cases.update({"dirty_basis": (replace(policy, bond_basis="dirty"), ZERO),
                              "higher_bond_friction": (replace(policy, bond_bps=D(25)), ZERO),
                              "higher_bond_yield": (policy, D("0.01")),
                              "coupon_withholding": (replace(policy, coupon_withholding=D(cfg["stress_coupon_withholding"])), ZERO)})
            if route in ACCRUAL_CASES:
                cases.update({"longer_sbi_release": (replace(policy, sbi_lag=14), ZERO),
                              "higher_sbi_ter": (replace(policy, sbi_ter=D("0.005")), ZERO),
                              "higher_sbi_reinvestment": (policy, ZERO)})
        asset = "sbi" if route in ACCRUAL_CASES else route
        weights = {asset if role == "gilt" else role: D(value)
                   for role, value in base["portfolio_weights"]["gold_baseline"].items() if D(value)}
        for label, (assumption, auction_shift) in cases.items():
            bond = bond_terms(auction_shift) if asset == "bond" else {}
            maturities = {}

            def path(kind, rate):
                level = marks[kind][-1]
                return cache(lambda day: level * growth(rate, first, day))

            paths = {kind: path(kind, pct(reference[f"{kind}_nav_pct"])) for kind in ("equity", "gold")}
            if label == "lower_equity_tracking":
                paths["equity"] = path("equity", pct(reference["equity_nav_pct"]) - D(cfg["stress_equity_tracking_drag"]))
            paths_free = dict(paths)
            if asset == "sbi":
                mat = date.fromisoformat(terms["fund"]["target_maturity_date"])
                maturities[asset] = mat
                source = next(row for row in holdings["scenarios"] if row["market_value_basis"] == route
                              and not row["residual_earns_reinvestment_rate"]
                              and pct(row["reinvest_percent"]) == (D("0.06") if label == "higher_sbi_reinvestment"
                                                                  else pct(reference["reserve_gross_pct"]))
                              and pct(row["ter_percent"]) == assumption.sbi_ter)
                gross = pct(source["gross_effective_annual_percent"])
                paths[asset] = path(asset, (ONE + gross) * (ONE - assumption.sbi_ter) - ONE)
                paths_free[asset] = path(asset, gross)
            else:
                if asset == "bond":
                    maturities[asset] = bond["maturity"]
                    paths[asset] = bond["mark"]
                else:
                    paths[asset] = path(asset, pct(reference["lic_nav_pct"]))
                paths_free[asset] = paths[asset]
            run(f"{horizon}-{route}-{label}", funding, weights, assumption, paths, paths_free, maturities, bond, horizon)
    return {"record_id": cfg["record_id"], "status": "WP2_CONDITIONAL_RESEARCH_SCENARIOS_ONLY",
            "decision_grade_personal_outputs": False, "eligible_probability_input": False,
            "sources": [provenance(path) for path in (INPUT, BASE_INPUT, COVERAGE, CONTRACT_PATH, DEFAULT_SCHEDULE_PATH,
                        CASHFLOW_PATH, AUCTION, SBI_HOLDINGS, SOVEREIGN_INPUT, Path(__file__).resolve(),
                        ROOT / "decision/after_tax_event_ledger.py", ROOT / "decision/g6_3_wp2_portfolio.py",
                        ROOT / "decision/audit_g6_3_wp2_dated.py",
                        ROOT / "decision/capital_gain_loss_schedule.py", ROOT / "decision/ty2026_27_tax_components.py")],
            "sbi_forward_accrual_cases": list(ACCRUAL_CASES), "results": rows, **expected_flags}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--trace-dir", type=Path)
    args = parser.parse_args()
    with localcontext() as ctx:
        ctx.prec = 42
        result = build(args.trace_dir)
    payload = json.dumps(result, indent=2) + "\n"
    if args.check:
        require(OUT.read_text(encoding="utf-8") == payload, "dated WP2 artifact differs")
    else:
        OUT.write_text(payload, encoding="utf-8", newline="\n")
    print(f"PASS: {len(result['results'])} dated research cases, including both SBI accrual treatments. NO_GO.")


if __name__ == "__main__":
    main()
