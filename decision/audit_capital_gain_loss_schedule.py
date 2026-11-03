"""Independent acceptance audit for the source-linked loss schedule."""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal

from after_tax_event_ledger import LedgerEvent, run_ledger
from capital_gain_loss_schedule import (
    Gain, Loss, Offset, build_schedule, build_schedule_from_disposal_traces,
)


D = Decimal


def rejects(call, message: str, error_type: type[Exception] = ValueError) -> None:
    try:
        call()
    except error_type as error:
        assert message in str(error), str(error)
    else:
        raise AssertionError(f"expected rejection containing {message!r}")


def audit() -> dict[str, object]:
    gains = [
        Gain("g-st", "event-g-st", "lot-g-st", "2026-27", D("100"), "short", "section196"),
        Gain("g-lt", "event-g-lt", "lot-g-lt", "2026-27", D("120"), "long", "section198"),
    ]
    losses = [
        Loss("l-current-st", "event-l-current-st", "lot-l-current-st", "2026-27", D("80"), "short", False),
        Loss("l-current-lt", "event-l-current-lt", "lot-l-current-lt", "2026-27", D("50"), "long", False),
    ]
    allocations = [
        Offset("l-current-st", "g-st", D("30")),
        Offset("l-current-st", "g-lt", D("50")),
        Offset("l-current-lt", "g-lt", D("40")),
    ]
    result = build_schedule("2026-27", gains, losses, allocations)
    assert result.gross_gains_by_bucket == {
        "section76": D("0"), "section196": D("100"),
        "section197": D("0"), "section198": D("120"),
    }
    assert result.candidate_gains_after_explicit_offsets_by_bucket["section196"] == D("70")
    assert result.candidate_gains_after_explicit_offsets_by_bucket["section198"] == D("30")
    assert result.tax_application_allowed is False
    assert result.unallocated_losses == {"l-current-lt": D("10")}
    assert result.carryforward_losses == {}
    assert result.offset_trace[0]["loss_event_id"] == "event-l-current-st"
    assert result.offset_trace[0]["gain_event_id"] == "event-g-st"
    assert result.loss_trace[0]["lot_id"] == "lot-l-current-st"

    # The same-year ST loss may cross to LT gains only when explicitly allocated.
    # A same-year LT loss may not offset ST gain.
    rejects(lambda: build_schedule("2026-27", gains, losses,
                                   [Offset("l-current-lt", "g-st", D("1"))]),
            "cannot offset short-term gain")
    rejects(lambda: build_schedule("2026-27",
                                   [Gain("bad76", "event-bad76", "lot-bad76", "2026-27", D("1"), "long", "section76")],
                                   [], []),
            "character conflicts")
    # Carried ST loss may offset either character; carried LT remains LT-only.
    carried_st = Loss("carry-st", "event-carry-st", "lot-carry-st", "2026-27", D("10"), "short", True, "fixture:return-263-1")
    carried_lt = Loss("carry-lt", "event-carry-lt", "lot-carry-lt", "2026-27", D("10"), "long", True, "fixture:return-263-1")
    carry_result = build_schedule("2026-27", gains, [carried_st, carried_lt],
                                  [Offset("carry-st", "g-st", D("5")),
                                   Offset("carry-lt", "g-lt", D("5"))])
    assert carry_result.candidate_gains_after_explicit_offsets_by_bucket["section196"] == D("95")
    assert carry_result.candidate_gains_after_explicit_offsets_by_bucket["section198"] == D("115")

    rejects(lambda: build_schedule("2035-36", [],
                                   [Loss("late", "event-late", "lot-late", "2026-27", D("1"), "short", True,
                                         "fixture:return-263-1")], []),
            "not eligible for carry-forward")
    rejects(lambda: build_schedule("2026-27", [],
                                   [Loss("legacy", "event-legacy", "lot-legacy", "2025-26", D("1"), "short", True,
                                         "fixture:legacy-return")], []),
            "section 536 transition record", NotImplementedError)
    rejects(lambda: build_schedule("2027-28", [],
                                   [Loss("no-return", "event-no-return", "lot-no-return", "2026-27", D("1"), "short", False)], []),
            "not eligible for carry-forward")
    rejects(lambda: build_schedule("2027-28", gains=[Gain("next", "event-next", "lot-next", "2027-28", D("10"), "short", "section196")],
                                   losses=[Loss("no-proof", "event-no-proof", "lot-no-proof", "2026-27", D("1"), "short", True)], offsets=[]),
            "evidence reference")
    rejects(lambda: build_schedule("2026-27", gains, [losses[0]],
                                   [Offset("l-current-st", "g-st", D("81"))]),
            "offsets exceed loss")
    rejects(lambda: build_schedule("2026-27", gains,
                                   [Loss("large-loss", "event-large-loss", "lot-large-loss", "2026-27", D("150"), "short", True,
                                         "fixture:return-263-1")],
                                   [Offset("large-loss", "g-st", D("101"))]),
            "offsets exceed gain")

    # Eight succeeding years are available; the balance expires after use in year 8.
    year8_loss = Loss("year8", "event-year8", "lot-year8", "2026-27", D("10"), "short", True, "fixture:return-263-1")
    year8 = build_schedule("2034-35", [], [year8_loss], [])
    assert year8.unallocated_losses == {"year8": D("10")}
    assert year8.carryforward_losses == {}
    rejects(lambda: build_schedule("2035-36", [], [year8_loss], []),
            "not eligible for carry-forward")

    # Empty allocation schedule cannot silently net gains or erase losses.
    untouched = build_schedule("2026-27", gains, losses, [])
    assert untouched.candidate_gains_after_explicit_offsets_by_bucket == untouched.gross_gains_by_bucket
    assert untouched.unallocated_losses == {"l-current-st": D("80"), "l-current-lt": D("50")}

    # End-to-end boundary: actual signed ledger records feed the schedule,
    # while coupons and dividends stay outside capital-gain netting.
    def ledger_event(event_id, when, seq, kind, cash, **kwargs):
        return LedgerEvent(
            event_id=event_id, event_date=when, tax_year="2026-27", event_sequence=seq,
            event_type=kind, instrument_id="SYNTHETIC", cash_amount_inr=D(cash),
            source_or_assumption="synthetic integration fixture",
            qualification_status="mechanics only", **kwargs,
        )

    integration_events = [
        ledger_event("capital", date(2026, 10, 31), 1, "initial_contribution", "1000"),
        ledger_event("buy-loss", date(2026, 10, 31), 2, "acquisition", "100",
                     lot_id="lot-loss", units=D("1"), unit_price_inr=D("100")),
        ledger_event("buy-gain", date(2026, 10, 31), 3, "acquisition", "100",
                     lot_id="lot-gain", units=D("1"), unit_price_inr=D("100")),
        ledger_event("coupon", date(2027, 3, 30), 1, "coupon", "10", gross_income_inr=D("10"),
                     tax_classification="ordinary", tax_classification_confirmed=True),
        ledger_event("dividend", date(2027, 3, 30), 2, "distribution", "5", gross_income_inr=D("5"),
                     tax_classification="dividend", tax_classification_confirmed=True),
        ledger_event("sale-loss", date(2027, 3, 31), 1, "partial_disposal", "90",
                     lot_id="lot-loss", units=D("1"), unit_price_inr=D("90"),
                     tax_classification="section196", tax_classification_confirmed=True,
                     section196_eligibility_confirmed=True),
        ledger_event("sale-gain", date(2027, 3, 31), 2, "partial_disposal", "120",
                     lot_id="lot-gain", units=D("1"), unit_price_inr=D("120"),
                     tax_classification="section196", tax_classification_confirmed=True,
                     section196_eligibility_confirmed=True),
    ]
    ledger = run_ledger(integration_events, {}, external_tax_inputs={})
    assert ledger.ledger_status == "ECONOMIC_PASS_TAX_UNQUALIFIED"
    integrated = build_schedule_from_disposal_traces(
        "2026-27", ledger.tax_event_trace, ledger.capital_loss_trace,
        [Offset("sale-loss", "sale-gain", D("10"))],
    )
    assert integrated.gross_gains_by_bucket["section196"] == D("20")
    assert integrated.offsets_by_bucket["section196"] == D("10")
    assert integrated.candidate_gains_after_explicit_offsets_by_bucket["section196"] == D("10")
    assert integrated.tax_application_allowed is False
    assert not any(row.get("event_id") in {"coupon", "dividend"} for row in integrated.offset_trace)

    # The adapter must reject a tampered magnitude or a non-loss signed result
    # before either can create candidate offsets.
    loss_row = ledger.capital_loss_trace[0]
    mismatched_loss = [{**loss_row, "loss_amount_inr": "11"}]
    rejects(lambda: build_schedule_from_disposal_traces(
        "2026-27", ledger.tax_event_trace, mismatched_loss, []),
        "does not reconcile")
    wrong_sign_loss = [{**loss_row, "signed_realized_result_inr": "10"}]
    rejects(lambda: build_schedule_from_disposal_traces(
        "2026-27", ledger.tax_event_trace, wrong_sign_loss, []),
        "must be finite and negative")

    return {
        "audit": "PASS",
        "explicit_cross_bucket_allocation": "PASS; no priority inferred",
        "same_year_and_carried_character_restrictions": "PASS",
        "eight_succeeding_year_expiry_and_return_gate": "PASS",
        "gain_loss_caps_and_traceability": "PASS",
        "ledger_to_schedule_contract": "PASS; coupon/dividend excluded, tax application still barred",
        "loss_trace_amount_reconciliation": "PASS; mismatched amount and non-loss sign rejected",
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
