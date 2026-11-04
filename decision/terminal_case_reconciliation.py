"""Synthetic 120/122-month fund-redemption and direct-bond terminal cases.

All cashflows are read from the frozen mathematical schedule. Prices, returns,
bond terms, tax-law persistence, and taxpayer income are explicit fixtures.
This is a mechanics reconciliation, not an investor projection or tax estimate.
"""

from __future__ import annotations

import csv
import hashlib
from calendar import monthrange
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

from after_tax_event_ledger import LedgerEvent, run_ledger, tax_year_for
from ty2026_27_tax_components import TaxInput


D = Decimal
ZERO = D("0")
ROOT = Path(__file__).resolve().parents[1]
SCHEDULE = ROOT / "research/stage512/2026-11-02/cashflow_hurdle_monthly_2026-10_base.csv"
ANNUAL_FUND_RETURN = D("0.05")
DIRECT_BOND_COUPON_RATE = D("0.05")
SYNTHETIC_EXTERNAL_ORDINARY_INCOME = D("3000000")
INITIAL_PRICE = D("100")
SYNTHETIC_INSTRUMENT = "SYNTHETIC-TAXABLE-FUND"
SYNTHETIC_BOND = "SYNTHETIC-DIRECT-BOND"


def month_end(year: int, month: int) -> date:
    return date(year, month, monthrange(year, month)[1])


def add_months(year: int, month: int, count: int) -> tuple[int, int]:
    absolute = year * 12 + month - 1 + count
    result_year, month0 = divmod(absolute, 12)
    return result_year, month0 + 1


def schedule_rows() -> list[dict[str, str]]:
    with SCHEDULE.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def event(
    event_id: str,
    when: date,
    sequence: int,
    kind: str,
    cash: Decimal,
    *,
    instrument: str,
    lot: str | None = None,
    units: Decimal | None = None,
    price: Decimal | None = None,
    income: Decimal = ZERO,
    tax_class: str = "none",
    confirmed: bool = False,
) -> LedgerEvent:
    return LedgerEvent(
        event_id=event_id,
        event_date=when,
        tax_year=tax_year_for(when),
        event_sequence=sequence,
        event_type=kind,
        instrument_id=instrument,
        cash_amount_inr=cash,
        source_or_assumption="SYNTHETIC_FIXTURE; frozen schedule with invented fixture-only price/terms",
        qualification_status="unqualified mechanics fixture; not an investor result",
        lot_id=lot,
        units=units,
        unit_price_inr=price,
        gross_income_inr=income,
        tax_classification=tax_class,
        tax_classification_confirmed=confirmed,
        section76_specified_fund_confirmed=tax_class == "section76" and confirmed,
    )


def external_inputs(years: set[str]) -> dict[str, TaxInput]:
    # Tax rules are held at the TY 2026–27 fixture implementation in every
    # future year solely to isolate ledger mechanics; actual future law is unknown.
    return {year: TaxInput(ordinary_income=SYNTHETIC_EXTERNAL_ORDINARY_INCOME) for year in years}


def sequence_events(events: list[LedgerEvent]) -> list[LedgerEvent]:
    from dataclasses import replace

    priority = {"initial_contribution": 0, "sip_contribution": 0, "acquisition": 1,
                "coupon": 2, "distribution": 2, "withholding": 3,
                "partial_disposal": 4, "terminal_disposal": 4, "maturity": 4}
    ordered = sorted(events, key=lambda item: (item.event_date, priority.get(item.event_type, 5), item.event_id))
    sequence_by_date: dict[date, int] = {}
    sequenced = []
    for item in ordered:
        sequence_by_date[item.event_date] = sequence_by_date.get(item.event_date, 0) + 1
        sequenced.append(replace(item, event_sequence=sequence_by_date[item.event_date]))
    return sequenced


def fund_lots(months: int) -> tuple[list[LedgerEvent], dict[str, tuple[date, Decimal, Decimal]], date]:
    rows = schedule_rows()
    selected = [row for row in rows if int(row["month_index"]) <= months]
    if len(selected) != months + 1 or len(selected[-1]["month_index"]) == 0:
        raise AssertionError(f"schedule does not contain month 0 through {months}")
    lots: dict[str, tuple[date, Decimal, Decimal]] = {}
    events: list[LedgerEvent] = []
    first_month_year, first_month = map(int, selected[0]["calendar_month"].split("-"))
    first_date = month_end(first_month_year, first_month)
    initial = D(selected[0]["initial_investment_inr"])
    units = initial / INITIAL_PRICE
    lots["fund-000"] = (first_date, units, initial)
    events.append(event("fund-contribution-000", first_date, 1, "initial_contribution", initial, instrument=SYNTHETIC_INSTRUMENT))
    events.append(event("fund-buy-000", first_date, 2, "acquisition", initial, instrument=SYNTHETIC_INSTRUMENT,
                        lot="fund-000", units=units, price=INITIAL_PRICE))
    for row in selected[1:]:
        index = int(row["month_index"])
        year, month = map(int, row["calendar_month"].split("-"))
        when = month_end(year, month)
        contribution = D(row["monthly_contribution_inr"])
        elapsed_months = (year - first_month_year) * 12 + month - first_month
        mark = INITIAL_PRICE * (D("1") + ANNUAL_FUND_RETURN * D(elapsed_months) / D(12))
        lot_id = f"fund-{index:03d}"
        lot_units = contribution / mark
        lots[lot_id] = (when, lot_units, contribution)
        events.append(event(f"fund-contribution-{index:03d}", when, 1, "sip_contribution", contribution, instrument=SYNTHETIC_INSTRUMENT))
        events.append(event(f"fund-buy-{index:03d}", when, 2, "acquisition", contribution, instrument=SYNTHETIC_INSTRUMENT,
                            lot=lot_id, units=lot_units, price=mark))
    terminal = month_end(*map(int, selected[-1]["calendar_month"].split("-")))
    return events, lots, terminal


def fund_case(months: int, stage: bool) -> dict[str, Any]:
    events, lots, terminal = fund_lots(months)
    if stage:
        # Snap the second tranche to the following 1 April so the two sales
        # land in separate Indian tax years, independent of terminal month.
        stage_date = date(terminal.year + 1, 4, 1)
        if stage_date <= terminal:
            stage_date = date(terminal.year + 2, 4, 1)
    else:
        stage_date = terminal
    seq_by_date: dict[date, int] = {}
    for lot_id, (_, units, _) in lots.items():
        tranche = units / 2 if stage else units
        for disposal_date, tranche_units, suffix in (
            ((terminal, tranche, "a"), (stage_date, units - tranche, "b")) if stage else ((terminal, units, "all"),)
        ):
            seq_by_date[disposal_date] = seq_by_date.get(disposal_date, 0) + 1
            elapsed_months = (disposal_date.year - 2026) * 12 + disposal_date.month - 10
            mark = INITIAL_PRICE * (D("1") + ANNUAL_FUND_RETURN * D(elapsed_months) / D(12))
            events.append(event(f"sell-{lot_id}-{suffix}", disposal_date, seq_by_date[disposal_date],
                                "partial_disposal" if stage and suffix == "a" else "terminal_disposal",
                                tranche_units * mark, instrument=SYNTHETIC_INSTRUMENT, lot=lot_id,
                                units=tranche_units, price=mark, tax_class="section76", confirmed=True))
    years = {tax_year_for(terminal)}
    if stage:
        years.add(tax_year_for(stage_date))
    result = run_ledger(sequence_events(events), {}, external_tax_inputs=external_inputs(years))
    out = result.as_json()
    out.update({"case": "fund_staged_liquidation" if stage else "fund_one_year_liquidation",
                "horizon_months": months, "terminal_date": terminal.isoformat(),
                "stage_two_date": stage_date.isoformat() if stage else None,
                "annual_synthetic_fund_return": str(ANNUAL_FUND_RETURN),
                "tax_law_fixture": "TY 2026-27 rules held constant; not a future-law forecast"})
    return out


def bond_case(months: int) -> dict[str, Any]:
    rows = schedule_rows()
    selected = [row for row in rows if int(row["month_index"]) <= months]
    terminal = month_end(*map(int, selected[-1]["calendar_month"].split("-")))
    events: list[LedgerEvent] = []
    lots: dict[str, tuple[date, Decimal]] = {}
    events_by_date: dict[date, list[LedgerEvent]] = {}

    def add(item: LedgerEvent) -> None:
        events_by_date.setdefault(item.event_date, []).append(item)

    for row in selected:
        index = int(row["month_index"])
        year, month = map(int, row["calendar_month"].split("-"))
        when = month_end(year, month)
        principal = D(row["initial_investment_inr"] if index == 0 else row["monthly_contribution_inr"])
        lot_id = f"bond-{index:03d}"
        add(event(f"bond-contribution-{index:03d}", when, 0, "initial_contribution" if index == 0 else "sip_contribution",
                  principal, instrument=SYNTHETIC_BOND))
        add(event(f"bond-buy-{index:03d}", when, 0, "acquisition", principal, instrument=SYNTHETIC_BOND,
                  lot=lot_id, units=principal, price=D("1")))
        lots[lot_id] = (when, principal)

    coupon_total = ZERO
    for lot_id, (acquired, principal) in lots.items():
        coupon_year = acquired.year + 1
        while True:
            try:
                coupon_date = date(coupon_year, acquired.month, acquired.day)
            except ValueError:
                coupon_date = month_end(coupon_year, acquired.month)
            if coupon_date > terminal:
                break
            coupon = principal * DIRECT_BOND_COUPON_RATE
            coupon_total += coupon
            add(event(f"bond-coupon-{lot_id}-{coupon_year}", coupon_date, 0, "coupon", coupon,
                      instrument=SYNTHETIC_BOND, lot=lot_id, income=coupon,
                      tax_class="ordinary", confirmed=True))
            coupon_year += 1

    for lot_id, (_, principal) in lots.items():
        add(event(f"bond-maturity-{lot_id}", terminal, 0, "maturity", principal, instrument=SYNTHETIC_BOND,
                  lot=lot_id, units=principal, price=D("1")))

    events = [item for day_events in events_by_date.values() for item in day_events]
    events = sequence_events(events)

    years = {tax_year_for(item.event_date) for item in events if item.event_type == "coupon"}
    result = run_ledger(events, {}, external_tax_inputs=external_inputs(years))
    out = result.as_json()
    out.update({"case": "direct_bond_coupon_and_maturity", "horizon_months": months,
                "terminal_date": terminal.isoformat(), "synthetic_coupon_rate": str(DIRECT_BOND_COUPON_RATE),
                "coupons_paid_inr": str(coupon_total),
                "tax_law_fixture": "TY 2026-27 rules held constant; not a future-law forecast"})
    return out


def reconcile() -> dict[str, Any]:
    rows = schedule_rows()
    outputs = []
    for months in (120, 122):
        selected = [row for row in rows if int(row["month_index"]) <= months]
        total = sum((D(row["initial_investment_inr"]) + D(row["monthly_contribution_inr"]) for row in selected), ZERO)
        if total != D(selected[-1]["cumulative_contributions_inr"]):
            raise AssertionError(f"cashflow schedule does not reconcile at {months} months")
        outputs.extend((fund_case(months, False), fund_case(months, True), bond_case(months)))
    manifest_paths = [
        "decision/terminal_case_reconciliation.py",
        "decision/audit_terminal_case_reconciliation.py",
        "decision/after_tax_event_ledger.py",
        "decision/ty2026_27_tax_components.py",
        "decision/tax_rules_asof.md",
        "research/stage512/2026-11-02/after_tax_ledger_input_contract.json",
        "research/stage512/2026-11-02/cashflow_hurdle_baseline.py",
        "research/stage512/2026-11-02/cashflow_hurdle_monthly_2026-10_base.csv",
    ]
    return {
        "audit": "PASS",
        "analysis_date": "2026-11-03",
        "run_manifest": {
            "rule_vintage": "Act 2025 / Finance Act 2026 component mapping as recorded in tax_rules_asof.md; TY 2026-27 calculator held constant",
            "contract_version": "1.3",
            "source_hash_normalization": "UTF-8 text normalized to LF before SHA-256",
            "source_sha256": {
                relative: hashlib.sha256(
                    (ROOT / relative).read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
                ).hexdigest()
                for relative in manifest_paths
            },
        },
        "scope": "120/122-month synthetic mechanics; no investable return or investor-specific tax/wealth result",
        "assumptions": {
            "cashflow_schedule": str(SCHEDULE.relative_to(ROOT)).replace("\\", "/"),
            "fund_return": "5% per year simple synthetic NAV appreciation, applied linearly by month; no distribution stream is modeled",
            "bond_terms": "par-priced direct-bond fixture; 5% annual cash coupon; principal returned at par",
            "external_ordinary_income_each_tax_year_inr": str(SYNTHETIC_EXTERNAL_ORDINARY_INCOME),
            "external_tax_inputs": "explicit synthetic ₹30 lakh ordinary income in every modeled year; no credits/deductions",
            "staged_sale": "50% of each fund lot at terminal month-end; remaining units sold on following 1 April",
            "fees": "zero solely for mechanics fixture; real fees remain unknown",
            "tax_rule_vintage": "TY 2026-27 component code applied unchanged to all modeled years",
            "cash_tax_timing": "tax liability is deducted from terminal fixture wealth; interim payment/reinvestment is not simulated",
            "real_wealth": "not calculated; CPI base and actual dates are unconfirmed",
        },
        "cases": outputs,
        "authorization": "NO-GO",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(reconcile(), indent=2))
