"""Audit a fully synthetic two-lot event ledger and tax-year reconciliation."""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal

from after_tax_event_ledger import LedgerEvent, run_ledger, tax_year_for
from ty2026_27_tax_components import TaxInput


D = Decimal


def event(
    event_id: str,
    when: date,
    seq: int,
    kind: str,
    cash: str,
    *,
    instrument: str = "SYNTHETIC-FIXTURE",
    lot: str | None = None,
    units: str | None = None,
    price: str | None = None,
    fee: str = "0",
    basis_addition: str = "0",
    gross_income: str = "0",
    withholding: str = "0",
    deductible_transfer_expenses: str = "0",
    tax_class: str = "none",
    confirmed: bool = False,
    section76_fund: bool = False,
    section196_eligible: bool = False,
    section197_eligible: bool = False,
    section198_eligible: bool = False,
) -> LedgerEvent:
    return LedgerEvent(
        event_id=event_id,
        event_date=when,
        tax_year=tax_year_for(when),
        event_sequence=seq,
        event_type=kind,
        instrument_id=instrument,
        cash_amount_inr=D(cash),
        source_or_assumption="SYNTHETIC_FIXTURE; not investor cashflow, security, price, or fee",
        qualification_status="fixture-only; no investable result",
        lot_id=lot,
        units=D(units) if units is not None else None,
        unit_price_inr=D(price) if price is not None else None,
        transaction_cost_inr=D(fee),
        tax_basis_addition_inr=D(basis_addition),
        gross_income_inr=D(gross_income),
        tax_withheld_inr=D(withholding),
        deductible_transfer_expenses_inr=D(deductible_transfer_expenses),
        tax_classification=tax_class,
        tax_classification_confirmed=confirmed,
        section76_specified_fund_confirmed=section76_fund,
        section196_eligibility_confirmed=section196_eligible,
        section197_eligibility_confirmed=section197_eligible,
        section198_eligibility_confirmed=section198_eligible,
    )


def audit() -> dict[str, object]:
    assert tax_year_for(date(2027, 3, 31)) == "2026-27"
    assert tax_year_for(date(2027, 4, 1)) == "2027-28"
    events = [
        event("cash-1", date(2026, 10, 31), 1, "initial_contribution", "1000"),
        event("buy-a", date(2026, 10, 31), 2, "acquisition", "505", lot="lot-a", units="5", price="100", fee="5", basis_addition="5"),
        event("coupon", date(2027, 3, 31), 1, "coupon", "1000", gross_income="1000", tax_class="ordinary", confirmed=True),
        event("coupon-tds", date(2027, 3, 31), 2, "withholding", "100", withholding="100"),
        event("dividend", date(2027, 4, 1), 1, "distribution", "500", gross_income="500", tax_class="dividend", confirmed=True),
        event("dividend-tds", date(2027, 4, 1), 2, "withholding", "50", withholding="50"),
        event("reinvest", date(2027, 4, 1), 3, "reinvestment", "450", lot="lot-b", units="1", price="450"),
        event("sell-a", date(2027, 9, 30), 1, "partial_disposal", "240", lot="lot-a", units="2", price="120", fee="2", tax_class="section197", confirmed=True, section197_eligible=True),
        event("custody-fee", date(2027, 9, 30), 2, "fee", "10"),
    ]
    external = {
        "2026-27": TaxInput(ordinary_income=D("3000000")),
        "2027-28": TaxInput(ordinary_income=D("3000000")),
    }
    result = run_ledger(events, {"lot-a": D("120"), "lot-b": D("450")}, external_tax_inputs=external)
    assert result.ledger_status == "PASS"
    assert result.event_count == 9
    assert result.cash_contributions_inr == D("1000")
    assert result.gross_income_inr == D("1500")
    assert result.portfolio_withholding_inr == D("150")
    assert result.transaction_costs_inr == D("7")
    assert result.other_fees_inr == D("10")
    assert result.ending_cash_inr == D("1623")
    assert result.ending_market_value_inr == D("810")
    assert result.realized_economic_gain_inr == D("40")
    assert result.unrealized_gain_inr == D("60")
    assert result.gross_terminal_wealth_inr == D("2433")
    assert result.reconciliation_residual_inr == D("0")
    assert D(result.tax_years["2026-27"]["incremental_portfolio_tax"]) == D("312")
    assert D(result.tax_years["2026-27"]["remaining_incremental_tax_after_portfolio_withholding"]) == D("212")
    assert D(result.tax_years["2027-28"]["portfolio_income"]["section197_ltcg"]) == D("38")
    assert D(result.tax_years["2027-28"]["incremental_portfolio_tax"]) == D("160.9400")
    assert result.incremental_portfolio_tax_inr == D("472.9400")
    assert result.remaining_incremental_tax_after_withholding_inr == D("322.9400")
    assert result.net_accessible_fixture_wealth_inr == D("2110.0600")
    assert any(lot["lot_id"] == "lot-a" and D(lot["unrealized_gain_inr"]) == D("60") for lot in result.open_lots)

    # A positive gain with no explicit tax classification must not pass.
    unknown_class = [
        event("cash", date(2026, 10, 31), 1, "initial_contribution", "1000"),
        event("buy", date(2026, 10, 31), 2, "acquisition", "100", lot="unknown-lot", units="1", price="100"),
        event("sell", date(2027, 5, 1), 1, "terminal_disposal", "110", lot="unknown-lot", units="1", price="110"),
    ]
    try:
        run_ledger(unknown_class, {}, external_tax_inputs={"2026-27": TaxInput(), "2027-28": TaxInput()})
    except ValueError as error:
        assert "confirmed statutory tax class" in str(error)
    else:
        raise AssertionError("unconfirmed realized gains must fail closed")

    return {
        "audit": "PASS",
        "scope": "synthetic two-lot, two-tax-year fixture; no investor result",
        "event_count": result.event_count,
        "gross_terminal_wealth_inr": str(result.gross_terminal_wealth_inr),
        "incremental_portfolio_tax_inr": str(result.incremental_portfolio_tax_inr),
        "net_accessible_fixture_wealth_inr": str(result.net_accessible_fixture_wealth_inr),
        "unrealized_gain_taxed": False,
        "withholding_is_credit": True,
        "authorization": "NO-GO",
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
