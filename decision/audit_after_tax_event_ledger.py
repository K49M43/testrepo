"""Audit a fully synthetic two-lot event ledger and tax-year reconciliation."""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal

from after_tax_event_ledger import LedgerEvent, run_ledger, tax_year_for
from capital_gain_loss_schedule import Loss, Offset
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
        event("coupon", date(2027, 3, 31), 1, "coupon", "1000", lot="lot-a", gross_income="1000", tax_class="ordinary", confirmed=True),
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
    assert D(result.tax_years["2027-28"]["incremental_portfolio_tax"]) == D("161.5640")
    assert D(result.tax_years["2027-28"]["excess_portfolio_withholding_not_valued_as_refund"]) == D("0")
    assert result.tax_years["2026-27"]["portfolio_income_source_event_ids"] == {
        "ordinary": ["coupon"], "withholding_credit": ["coupon-tds"]
    }
    assert result.tax_years["2027-28"]["portfolio_income_source_event_ids"] == {
        "dividend": ["dividend"], "section197_ltcg": ["sell-a"],
        "withholding_credit": ["dividend-tds"]
    }
    trace_by_id = {line["event_id"]: line for line in result.tax_event_trace}
    assert trace_by_id["sell-a"]["lot_id"] == "lot-a"
    assert trace_by_id["sell-a"]["lot_acquired"] == "2026-10-31"
    assert D(trace_by_id["sell-a"]["taxable_amount_inr"]) == D("38")
    assert trace_by_id["sell-a"]["rule_reference"].startswith("TY 2026-27 component model: section 197")
    assert trace_by_id["coupon"]["lot_id"] == "lot-a"
    assert trace_by_id["coupon"]["lot_acquired"] == "2026-10-31"
    assert trace_by_id["coupon-tds"]["tax_category"] == "withholding_credit"
    for year in ("2026-27", "2027-28"):
        by_category: dict[str, Decimal] = {}
        for line in result.tax_event_trace:
            if line["tax_year"] == year:
                by_category[line["tax_category"]] = by_category.get(line["tax_category"], D("0")) + D(line["taxable_amount_inr"])
        for category, amount in by_category.items():
            assert D(result.tax_years[year]["portfolio_income"][category]) == amount
    assert result.incremental_portfolio_tax_inr == D("473.5640")
    assert result.remaining_incremental_tax_after_withholding_inr == D("323.5640")
    assert result.excess_portfolio_withholding_not_valued_inr == D("0")
    assert result.net_accessible_fixture_wealth_inr == D("2109.4360")
    assert any(lot["lot_id"] == "lot-a" and D(lot["unrealized_gain_inr"]) == D("60") for lot in result.open_lots)

    # A supplied carried loss enters the validated schedule even when the
    # current ledger has no realized loss event.
    carried_only_result = run_ledger(
        events, {"lot-a": D("120"), "lot-b": D("450")},
        external_tax_inputs=external,
        carried_losses_by_year={"2027-28": [
            Loss("carried-st", "prior-loss-event", "prior-loss-lot", "2026-27",
                 D("10"), "short", True, "fixture:return-263-1")
        ]},
        capital_loss_offsets_by_year={
            "2027-28": [Offset("carried-st", "sell-a", D("10"))],
        },
    )
    assert carried_only_result.ledger_status == "PASS"
    assert carried_only_result.tax_years["2027-28"]["tax_qualification_status"] == \
        "RESEARCH_FIXTURE_EXPLICIT_LOSS_SCHEDULE_APPLIED"
    carried_candidate = carried_only_result.capital_loss_candidate_schedules["2027-28"]
    assert carried_candidate["gross_gains_by_bucket"]["section197"] == "38"
    assert carried_candidate["offsets_by_bucket"]["section197"] == "10"
    assert carried_candidate["candidate_gains_after_explicit_offsets_by_bucket"]["section197"] == "28"
    assert carried_candidate["unallocated_losses"] == {}
    assert carried_candidate["carryforward_losses"] == {}
    assert carried_candidate["tax_application_allowed"] is True
    assert D(carried_only_result.tax_years["2027-28"]["incremental_portfolio_tax"]) == D("160.2640")
    assert D(carried_only_result.tax_years["2027-28"]["remaining_incremental_tax_after_portfolio_withholding"]) == D("110.2640")

    # Repeated partial disposals from the same lot must remove basis in
    # proportion to the units remaining at each event, without losing units
    # or basis through fractional Decimal division.
    repeated_sales = [
        event("cash", date(2026, 10, 31), 1, "initial_contribution", "500"),
        event("buy", date(2026, 10, 31), 2, "acquisition", "300", lot="repeat-lot", units="3", price="100"),
        event("sell-1", date(2027, 3, 31), 1, "partial_disposal", "120", lot="repeat-lot", units="1", price="120",
              tax_class="section196", confirmed=True, section196_eligible=True),
        event("sell-2", date(2027, 3, 31), 2, "partial_disposal", "130", lot="repeat-lot", units="1", price="130",
              tax_class="section196", confirmed=True, section196_eligible=True),
    ]
    repeated_result = run_ledger(
        repeated_sales, {"repeat-lot": D("100")},
        external_tax_inputs={"2026-27": TaxInput(ordinary_income=D("400000"))},
    )
    assert repeated_result.ending_cash_inr == D("450")
    assert repeated_result.ending_market_value_inr == D("100")
    assert abs(repeated_result.realized_economic_gain_inr - D("50")) <= D("0.000000000001")
    assert repeated_result.reconciliation_residual_inr == D("0")
    assert abs(D(repeated_result.tax_years["2026-27"]["portfolio_income"]["section196_stcg"]) - D("50")) <= D("0.000000000001")
    assert D(repeated_result.tax_years["2026-27"]["incremental_portfolio_tax"]) == D("0.0000")
    gain_trace = [row for row in repeated_result.tax_event_trace if row["event_id"] in {"sell-1", "sell-2"}]
    assert len(gain_trace) == 2
    assert abs(sum((D(row["realized_disposal"]["signed_realized_result_inr"]) for row in gain_trace), D("0"))
               - D("50")) <= D("0.000000000001")
    assert len(repeated_result.open_lots) == 1
    assert D(repeated_result.open_lots[0]["units"]) == D("1")
    assert D(repeated_result.open_lots[0]["tax_basis_inr"]) == D("100")

    # The sale now completes economic cash/lot reconciliation, but its tax
    # result includes only explicit validated offsets, never an inferred one.
    loss_events = [
        event("loss-cash", date(2026, 10, 31), 1, "initial_contribution", "500"),
        event("loss-buy", date(2026, 10, 31), 2, "acquisition", "300", lot="loss-lot", units="3", price="100"),
        event("gain-buy", date(2026, 10, 31), 3, "acquisition", "100", lot="gain-lot", units="1", price="100"),
        event("loss-sale", date(2027, 3, 31), 1, "partial_disposal", "90", lot="loss-lot", units="1", price="90",
              tax_class="section196", confirmed=True, section196_eligible=True),
        event("gain-sale", date(2027, 3, 31), 2, "partial_disposal", "120", lot="gain-lot", units="1", price="120",
              tax_class="section196", confirmed=True, section196_eligible=True),
    ]
    loss_result = run_ledger(loss_events, {"loss-lot": D("100")},
                             external_tax_inputs={"2026-27": TaxInput(ordinary_income=D("500000"))},
                             capital_loss_offsets_by_year={
                                 "2026-27": [Offset("loss-sale", "gain-sale", D("10"))]
                             })
    assert loss_result.ledger_status == "PASS"
    assert loss_result.ending_cash_inr == D("310")
    assert loss_result.ending_market_value_inr == D("200")
    assert abs(loss_result.realized_economic_gain_inr - D("10")) <= D("0.000000000001")
    assert loss_result.gross_terminal_wealth_inr == D("510")
    assert loss_result.reconciliation_residual_inr == D("0")
    assert loss_result.incremental_portfolio_tax_inr == D("2.0800")
    assert loss_result.remaining_incremental_tax_after_withholding_inr == D("2.0800")
    assert loss_result.net_accessible_fixture_wealth_inr == D("507.9200")
    assert loss_result.open_lots[0]["units"] == "2"
    assert D(loss_result.open_lots[0]["tax_basis_inr"]) == D("200")
    assert loss_result.capital_loss_trace[0]["event_id"] == "loss-sale"
    assert abs(D(loss_result.capital_loss_trace[0]["loss_amount_inr"]) - D("10")) <= D("0.000000000001")
    assert loss_result.capital_loss_trace[0]["proceeds_inr"] == "90"
    assert abs(D(loss_result.capital_loss_trace[0]["tax_basis_removed_inr"]) - D("100")) <= D("0.000000000001")
    assert loss_result.capital_loss_trace[0]["tax_basis_removed_inr"] == "100"
    assert loss_result.capital_loss_trace[0]["lot_id"] == "loss-lot"
    assert loss_result.capital_loss_trace[0]["carryforward_eligibility"] == {
        "status": "UNDETERMINED_RETURN_EVIDENCE_NOT_SUPPLIED",
        "return_filed_under_263_1": None,
        "evidence_reference": None,
    }
    assert loss_result.tax_years["2026-27"]["tax_qualification_status"] == \
        "RESEARCH_FIXTURE_EXPLICIT_LOSS_SCHEDULE_APPLIED"
    candidate = loss_result.capital_loss_candidate_schedules["2026-27"]
    assert candidate["gross_gains_by_bucket"]["section196"] == "20"
    assert candidate["offsets_by_bucket"]["section196"] == "10"
    assert candidate["candidate_gains_after_explicit_offsets_by_bucket"]["section196"] == "10"
    assert candidate["tax_application_allowed"] is True
    assert D(loss_result.tax_years["2026-27"]["total_tax_before_credits"]) == D("2.0800")
    assert not any(row["event_id"] == "loss-sale" for row in loss_result.tax_event_trace)
    gross_gain_result = run_ledger(
        loss_events, {"loss-lot": D("100")},
        external_tax_inputs={"2026-27": TaxInput(ordinary_income=D("500000"))},
    )
    assert gross_gain_result.incremental_portfolio_tax_inr == D("4.1600")
    assert loss_result.incremental_portfolio_tax_inr == gross_gain_result.incremental_portfolio_tax_inr / 2

    try:
        run_ledger(
            loss_events, {"loss-lot": D("100")},
            external_tax_inputs={"2026-27": TaxInput(
                ordinary_income=D("500000"), section196_stcg=D("100"), section196_eligible=True,
            )},
            capital_loss_offsets_by_year={"2026-27": [Offset("loss-sale", "gain-sale", D("10"))]},
        )
    except NotImplementedError as error:
        assert "source-linked external capital-gain traces" in str(error)
    else:
        raise AssertionError("loss offsets must fail closed when external gains are not source-traced")

    # An explicitly allocated short-term loss can net against a section 76
    # specified-fund gain. Its net gain must enter ordinary-rate income once.
    section76_events = [
        event("s76-cash", date(2026, 10, 31), 1, "initial_contribution", "1000"),
        event("s76-loss-buy", date(2026, 10, 31), 2, "acquisition", "100", lot="s76-loss-lot", units="1", price="100"),
        event("s76-gain-buy", date(2026, 10, 31), 3, "acquisition", "100", lot="s76-gain-lot", units="1", price="100"),
        event("s76-loss-sale", date(2027, 3, 31), 1, "partial_disposal", "90", lot="s76-loss-lot", units="1", price="90",
              tax_class="section196", confirmed=True, section196_eligible=True),
        event("s76-fund-sale", date(2027, 3, 31), 2, "partial_disposal", "120", lot="s76-gain-lot", units="1", price="120",
              tax_class="section76", confirmed=True, section76_fund=True),
    ]
    s76_net_result = run_ledger(
        section76_events, {},
        external_tax_inputs={"2026-27": TaxInput(ordinary_income=D("1200000"))},
        capital_loss_offsets_by_year={
            "2026-27": [Offset("s76-loss-sale", "s76-fund-sale", D("10"))],
        },
    )
    assert s76_net_result.ledger_status == "PASS"
    s76_schedule = s76_net_result.capital_loss_candidate_schedules["2026-27"]
    assert s76_schedule["gross_gains_by_bucket"]["section76"] == "20"
    assert s76_schedule["offsets_by_bucket"]["section76"] == "10"
    assert s76_schedule["candidate_gains_after_explicit_offsets_by_bucket"]["section76"] == "10"
    assert s76_net_result.tax_years["2026-27"]["portfolio_income"]["ordinary"] == "20"
    assert D(s76_net_result.tax_years["2026-27"]["incremental_portfolio_tax"]) == D("10.40000")
    s76_gross_result = run_ledger(
        section76_events, {}, external_tax_inputs={"2026-27": TaxInput(ordinary_income=D("1200000"))},
    )
    assert s76_gross_result.incremental_portfolio_tax_inr == D("20.80000")

    # A long-term loss explicitly allocated to a section 198 gain must reduce
    # the taxable gain before the annual section 198 deduction.
    section198_events = [
        event("s198-cash", date(2025, 1, 1), 1, "initial_contribution", "20000"),
        event("s198-loss-buy", date(2025, 1, 1), 2, "acquisition", "11000",
              lot="s198-loss-lot", units="1", price="11000"),
        event("s198-gain-buy", date(2025, 1, 1), 3, "acquisition", "100",
              lot="s198-gain-lot", units="1", price="100"),
        event("s198-loss-sale", date(2026, 10, 31), 1, "partial_disposal", "1000",
              lot="s198-loss-lot", units="1", price="1000", tax_class="section198",
              confirmed=True, section198_eligible=True),
        event("s198-gain-sale", date(2026, 10, 31), 2, "partial_disposal", "200100",
              lot="s198-gain-lot", units="1", price="200100", tax_class="section198",
              confirmed=True, section198_eligible=True),
    ]
    s198_net_result = run_ledger(
        section198_events, {},
        external_tax_inputs={"2026-27": TaxInput(ordinary_income=D("3000000"))},
        capital_loss_offsets_by_year={
            "2026-27": [Offset("s198-loss-sale", "s198-gain-sale", D("10000"))],
        },
    )
    s198_schedule = s198_net_result.capital_loss_candidate_schedules["2026-27"]
    assert s198_schedule["gross_gains_by_bucket"]["section198"] == "200000"
    assert s198_schedule["offsets_by_bucket"]["section198"] == "10000"
    assert s198_schedule["candidate_gains_after_explicit_offsets_by_bucket"]["section198"] == "190000"
    assert D(s198_net_result.tax_years["2026-27"]["incremental_portfolio_tax"]) == D("8450.00000")
    s198_gross_result = run_ledger(
        section198_events, {}, external_tax_inputs={"2026-27": TaxInput(ordinary_income=D("3000000"))},
    )
    assert D(s198_gross_result.tax_years["2026-27"]["incremental_portfolio_tax"]) == D("9750.00000")

    unqualified_loss_events = loss_events[:-1] + [
        event("unqualified-loss-sale", date(2027, 3, 31), 3, "partial_disposal", "90",
              lot="loss-lot", units="1", price="90")
    ]
    try:
        run_ledger(unqualified_loss_events, {"loss-lot": D("100")},
                   external_tax_inputs={"2026-27": TaxInput()})
    except ValueError as error:
        assert "confirmed statutory tax class" in str(error)
    else:
        raise AssertionError("a disposal loss without confirmed tax character must fail closed")

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
        "repeated_partial_sales_same_lot": "PASS",
        "signed_disposal_trace": "PASS; realized loss economically reconciled and explicit offset applied",
        "loss_schedule_pipeline": "PASS; explicit same-bucket and section76 cross-bucket offsets are reflected in bounded fixture tax",
        "section198_loss_pipeline": "PASS; explicit long-term same-bucket offset reduces eligible gain before annual allowance",
        "carried_loss_only_pipeline": "PASS; supplied evidence and explicit carried-loss allocation reduce section197 tax, withholding reconciles",
        "unrealized_gain_taxed": False,
        "withholding_is_credit": True,
        "authorization": "NO-GO",
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
