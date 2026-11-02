"""Reconcile the Sprint 1 input contract to the pre-tax cashflow fixture."""

from __future__ import annotations

import csv
import json
from decimal import Decimal
from pathlib import Path

from cashflow_hurdle_baseline import INITIAL_INR, STARTING_SIP_INR, STEP_UP, contribution_schedule


ROOT = Path(__file__).parent
CONTRACT = ROOT / "after_tax_ledger_input_contract.json"
FIXTURE = ROOT / "cashflow_hurdle_monthly_2026-10_base.csv"


def reconcile() -> dict[str, object]:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    fixture = list(csv.DictReader(FIXTURE.open(encoding="utf-8", newline="")))
    horizons = contract["cashflow_fixture"]["horizons_months"]
    expected = contribution_schedule(max(horizons))
    assert len(fixture) == max(horizons) + 1, "fixture row count mismatch"
    first = fixture[0]
    assert first["calendar_month"] == contract["cashflow_fixture"]["initial_reference_month"]
    assert Decimal(first["initial_investment_inr"]) == INITIAL_INR
    cumulative = INITIAL_INR
    for month_index, (row, amount) in enumerate(zip(fixture[1:], expected, strict=True), start=1):
        assert int(row["month_index"]) == month_index
        assert Decimal(row["monthly_contribution_inr"]) == amount
        cumulative += amount
        assert Decimal(row["cumulative_contributions_inr"]) == cumulative
    horizon_totals = {
        str(horizon): {
            "sip_contributions_inr": str(sum(contribution_schedule(horizon), Decimal("0"))),
            "initial_plus_sips_inr": str(INITIAL_INR + sum(contribution_schedule(horizon), Decimal("0"))),
        }
        for horizon in horizons
    }
    return {
        "status": "PASS",
        "fixture_rows": len(fixture),
        "horizon_months": horizons,
        "total_contributions_inr": horizon_totals,
        "payment_dates": "unconfirmed; fixture month labels are mathematical placeholders",
        "transaction_rounding": "not assumed",
        "sip_parameters": {"start_inr": str(STARTING_SIP_INR), "annual_step_up": str(STEP_UP)},
    }


if __name__ == "__main__":
    print(json.dumps(reconcile(), indent=2))
