"""Deterministic event/lot ledger for explicitly qualified research fixtures.

The ledger does not infer trade dates, instrument classifications, deductible
charges, or market prices. Event cash amounts are positive magnitudes; event
type determines direction. Same-day order uses an explicit sequence number.
Unrealized gains affect valuation only and never enter taxable income.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from decimal import Decimal
from typing import Any, Iterable, Mapping

from ty2026_27_tax_components import TaxInput, calculate_tax


ZERO = Decimal("0")
# Finite Decimal division can leave a sub-picorupee residue when units are
# derived from cash / NAV. This is a computation tolerance, not transaction or
# statutory rupee rounding; it is three orders below this schedule's 1e-9 INR precision.
ARITHMETIC_TOLERANCE = Decimal("0.000000000001")
TAX_CLASSES = {"ordinary", "dividend", "section76", "section196", "section197", "section198", "none"}
CONTRIBUTIONS = {"initial_contribution", "sip_contribution"}
ACQUISITIONS = {"acquisition", "reinvestment"}
DISPOSALS = {"partial_disposal", "maturity", "terminal_disposal"}
INCOME_EVENTS = {"coupon", "distribution"}
ALLOWED_EVENTS = CONTRIBUTIONS | ACQUISITIONS | DISPOSALS | INCOME_EVENTS | {"fee", "withholding", "withdrawal"}


def amount(value: Decimal | int | str, name: str) -> Decimal:
    result = value if isinstance(value, Decimal) else Decimal(str(value))
    if not result.is_finite() or result < ZERO:
        raise ValueError(f"{name} must be a finite non-negative amount")
    return result


def tax_year_for(event_date: date) -> str:
    """Return Indian tax-year label beginning 1 April (e.g. 2026-27)."""
    start_year = event_date.year if event_date.month >= 4 else event_date.year - 1
    return f"{start_year}-{str(start_year + 1)[-2:]}"


@dataclass(frozen=True)
class LedgerEvent:
    event_id: str
    event_date: date
    tax_year: str
    event_sequence: int
    event_type: str
    instrument_id: str
    cash_amount_inr: Decimal
    source_or_assumption: str
    qualification_status: str
    lot_id: str | None = None
    units: Decimal | None = None
    unit_price_inr: Decimal | None = None
    transaction_cost_inr: Decimal = ZERO
    tax_basis_addition_inr: Decimal = ZERO
    gross_income_inr: Decimal = ZERO
    tax_withheld_inr: Decimal = ZERO
    deductible_transfer_expenses_inr: Decimal = ZERO
    tax_classification: str = "none"
    tax_classification_confirmed: bool = False
    section76_specified_fund_confirmed: bool = False
    section196_eligibility_confirmed: bool = False
    section197_eligibility_confirmed: bool = False
    section198_eligibility_confirmed: bool = False


@dataclass
class LotState:
    lot_id: str
    instrument_id: str
    acquired: date
    units: Decimal
    cash_basis_inr: Decimal
    tax_basis_inr: Decimal
    source_or_assumption: str
    qualification_status: str


@dataclass
class YearIncome:
    ordinary_income: Decimal = ZERO
    dividend_income: Decimal = ZERO
    section196_stcg: Decimal = ZERO
    section197_ltcg: Decimal = ZERO
    section198_ltcg: Decimal = ZERO
    withholding_credit: Decimal = ZERO
    section196_eligible: bool = False
    section197_eligible: bool = False
    section198_eligible: bool = False


@dataclass(frozen=True)
class EventLedgerResult:
    ledger_status: str
    event_count: int
    tax_years: dict[str, dict[str, Any]]
    cash_contributions_inr: Decimal
    gross_income_inr: Decimal
    portfolio_withholding_inr: Decimal
    transaction_costs_inr: Decimal
    other_fees_inr: Decimal
    withdrawals_inr: Decimal
    ending_cash_inr: Decimal
    ending_market_value_inr: Decimal
    realized_economic_gain_inr: Decimal
    unrealized_gain_inr: Decimal
    gross_terminal_wealth_inr: Decimal
    incremental_portfolio_tax_inr: Decimal | None
    remaining_incremental_tax_after_withholding_inr: Decimal | None
    net_accessible_fixture_wealth_inr: Decimal | None
    reconciliation_residual_inr: Decimal
    open_lots: list[dict[str, str]]
    tax_event_trace: list[dict[str, Any]]
    capital_loss_trace: list[dict[str, Any]]
    tax_scope: str = "Synthetic fixture only; external investor income defaults to zero only when explicitly supplied as fixture input"

    def as_json(self) -> dict[str, Any]:
        result = asdict(self)

        def convert(item: Any) -> Any:
            if isinstance(item, Decimal):
                return str(item)
            if isinstance(item, dict):
                return {key: convert(value) for key, value in item.items()}
            if isinstance(item, list):
                return [convert(value) for value in item]
            return item

        return convert(result)


def _merge_tax_inputs(external: TaxInput, portfolio: YearIncome) -> TaxInput:
    return TaxInput(
        ordinary_income=amount(external.ordinary_income, "external ordinary income") + portfolio.ordinary_income,
        dividend_income=amount(external.dividend_income, "external dividend income") + portfolio.dividend_income,
        section196_stcg=amount(external.section196_stcg, "external section196 gains") + portfolio.section196_stcg,
        section197_ltcg=amount(external.section197_ltcg, "external section197 gains") + portfolio.section197_ltcg,
        section198_ltcg=amount(external.section198_ltcg, "external section198 gains") + portfolio.section198_ltcg,
        tax_withheld_credit=amount(external.tax_withheld_credit, "external withholding") + portfolio.withholding_credit,
        resident_individual=external.resident_individual,
        section196_eligible=external.section196_eligible or portfolio.section196_eligible,
        section197_eligible=external.section197_eligible or portfolio.section197_eligible,
        section198_eligible=external.section198_eligible or portfolio.section198_eligible,
    )


def run_ledger(
    events: Iterable[LedgerEvent],
    valuation_prices: Mapping[str, Decimal | int | str],
    *,
    external_tax_inputs: Mapping[str, TaxInput],
) -> EventLedgerResult:
    """Run events, value remaining lots, and calculate incremental fixture tax.

    External income/credits are required explicitly for each tax year in which
    the taxpayer-level tax result is requested. Pass an explicit zero-valued
    ``TaxInput`` for a synthetic year; actual personal facts must not default.
    """
    event_list = list(events)
    if not event_list:
        raise ValueError("at least one ledger event is required")
    ids = [event.event_id for event in event_list]
    if len(ids) != len(set(ids)):
        raise ValueError("event_id values must be unique")
    sequences = [(event.event_date, event.event_sequence) for event in event_list]
    if len(sequences) != len(set(sequences)):
        raise ValueError("event_sequence must be unique within each date")
    event_list.sort(key=lambda event: (event.event_date, event.event_sequence, event.event_id))

    lots: dict[str, LotState] = {}
    incomes: dict[str, YearIncome] = {}
    cash = contributions = gross_income = withholding = transaction_costs = other_fees = withdrawals = ZERO
    realized_economic_gain = ZERO
    event_withholding_by_year: dict[str, Decimal] = {}
    tax_event_trace: list[dict[str, Any]] = []
    capital_loss_trace: list[dict[str, Any]] = []
    has_realized_loss = False
    tax_event_ids_by_year: dict[str, dict[str, list[str]]] = {}

    def record_tax_source(event: LedgerEvent, category: str, taxable_amount: Decimal, rule_reference: str,
                          *, acquired: date | None = None,
                          disposal_details: Mapping[str, str] | None = None) -> None:
        source_row = {
            "event_id": event.event_id,
            "event_date": event.event_date.isoformat(),
            "tax_year": event.tax_year,
            "instrument_id": event.instrument_id,
            "event_type": event.event_type,
            "lot_id": event.lot_id,
            "lot_acquired": acquired.isoformat() if acquired else None,
            "tax_category": category,
            "taxable_amount_inr": str(taxable_amount),
            "tax_classification": event.tax_classification,
            "tax_classification_confirmed": event.tax_classification_confirmed,
            "eligibility_confirmed": {
                "section76_specified_fund": event.section76_specified_fund_confirmed,
                "section196": event.section196_eligibility_confirmed,
                "section197": event.section197_eligibility_confirmed,
                "section198": event.section198_eligibility_confirmed,
            },
            "rule_reference": rule_reference,
            "source_or_assumption": event.source_or_assumption,
            "qualification_status": event.qualification_status,
        }
        if disposal_details is not None:
            source_row["realized_disposal"] = dict(disposal_details)
        tax_event_trace.append(source_row)
        year_sources = tax_event_ids_by_year.setdefault(event.tax_year, {})
        year_sources.setdefault(category, []).append(event.event_id)

    def year_income(value: str) -> YearIncome:
        return incomes.setdefault(value, YearIncome())

    for event in event_list:
        if event.event_type not in ALLOWED_EVENTS:
            raise ValueError(f"unsupported event type: {event.event_type}")
        if not event.source_or_assumption.strip() or not event.qualification_status.strip():
            raise ValueError(f"event {event.event_id} requires source/assumption and qualification status")
        year = tax_year_for(event.event_date)
        if event.tax_year != year:
            raise ValueError(f"tax_year does not match event date for {event.event_id}: {event.tax_year} != {year}")
        cash_amount = amount(event.cash_amount_inr, "cash_amount_inr")
        fee = amount(event.transaction_cost_inr, "transaction_cost_inr")
        basis_addition = amount(event.tax_basis_addition_inr, "tax_basis_addition_inr")
        if event.tax_classification not in TAX_CLASSES:
            raise ValueError(f"unsupported tax classification: {event.tax_classification}")

        if event.event_type in CONTRIBUTIONS:
            if event.lot_id or event.units is not None or fee or cash_amount == ZERO:
                raise ValueError(f"invalid contribution fields: {event.event_id}")
            cash += cash_amount
            contributions += cash_amount
            continue

        if event.event_type in ACQUISITIONS:
            if not event.lot_id or event.lot_id in lots or event.units is None or event.unit_price_inr is None:
                raise ValueError(f"acquisition requires a new lot ID, units, and unit price: {event.event_id}")
            units = amount(event.units, "units")
            price = amount(event.unit_price_inr, "unit_price_inr")
            if units == ZERO or price == ZERO or event.tax_withheld_inr or event.gross_income_inr:
                raise ValueError(f"invalid acquisition amounts: {event.event_id}")
            if basis_addition > fee:
                raise ValueError(f"tax basis addition cannot exceed the recorded acquisition transaction cost: {event.event_id}")
            principal = units * price
            if abs(cash_amount - (principal + fee)) > ARITHMETIC_TOLERANCE:
                raise ValueError(f"acquisition cash must equal principal plus fee: {event.event_id}")
            if cash < cash_amount:
                raise ValueError(f"insufficient cash for acquisition: {event.event_id}")
            cash -= cash_amount
            transaction_costs += fee
            lots[event.lot_id] = LotState(
                lot_id=event.lot_id,
                instrument_id=event.instrument_id,
                acquired=event.event_date,
                units=units,
                cash_basis_inr=cash_amount - fee,
                tax_basis_inr=cash_amount - fee + basis_addition,
                source_or_assumption=event.source_or_assumption,
                qualification_status=event.qualification_status,
            )
            continue

        if event.event_type in INCOME_EVENTS:
            gross = amount(event.gross_income_inr, "gross_income_inr")
            if cash_amount != gross or gross == ZERO or event.tax_withheld_inr:
                raise ValueError(f"income event cash must equal positive gross income; withholding is separate: {event.event_id}")
            if event.lot_id and (event.lot_id not in lots or lots[event.lot_id].instrument_id != event.instrument_id):
                raise ValueError(f"income event lot must identify an open lot of the same instrument: {event.event_id}")
            if not event.tax_classification_confirmed or event.tax_classification not in {"ordinary", "dividend"}:
                raise ValueError(f"income event requires confirmed ordinary/dividend treatment: {event.event_id}")
            cash += gross
            gross_income += gross
            income = year_income(year)
            if event.tax_classification == "dividend":
                income.dividend_income += gross
                record_tax_source(event, "dividend", gross, "TY 2026-27 component model: section 202 ordinary-rate income",
                                  acquired=lots[event.lot_id].acquired if event.lot_id else None)
            else:
                income.ordinary_income += gross
                record_tax_source(event, "ordinary", gross, "TY 2026-27 component model: section 202 ordinary income",
                                  acquired=lots[event.lot_id].acquired if event.lot_id else None)
            continue

        if event.event_type == "withholding":
            withheld = cash_amount
            if withheld == ZERO or event.tax_withheld_inr != withheld or cash < withheld:
                raise ValueError(f"invalid or unfunded withholding event: {event.event_id}")
            cash -= withheld
            withholding += withheld
            year_income(year).withholding_credit += withheld
            event_withholding_by_year[year] = event_withholding_by_year.get(year, ZERO) + withheld
            record_tax_source(event, "withholding_credit", withheld,
                              "TY 2026-27 component model: tax withheld is a credit, not a reduction in gross income")
            continue

        if event.event_type == "fee":
            if cash_amount == ZERO or cash < cash_amount:
                raise ValueError(f"invalid or unfunded fee event: {event.event_id}")
            cash -= cash_amount
            other_fees += cash_amount
            continue

        if event.event_type == "withdrawal":
            if cash_amount == ZERO or cash < cash_amount:
                raise ValueError(f"invalid or unfunded withdrawal event: {event.event_id}")
            cash -= cash_amount
            withdrawals += cash_amount
            continue

        if event.event_type in DISPOSALS:
            if not event.lot_id or event.lot_id not in lots or event.units is None or event.unit_price_inr is None:
                raise ValueError(f"disposal requires an existing lot ID, units, and unit price: {event.event_id}")
            lot = lots[event.lot_id]
            units = amount(event.units, "units")
            price = amount(event.unit_price_inr, "unit_price_inr")
            proceeds = cash_amount
            transfer_expenses = amount(event.deductible_transfer_expenses_inr, "deductible_transfer_expenses_inr")
            if units == ZERO or units > lot.units or price == ZERO or proceeds != units * price:
                raise ValueError(f"disposal units/proceeds do not reconcile: {event.event_id}")
            if transfer_expenses > fee:
                raise ValueError(f"deductible transfer expenses cannot exceed total sale transaction cost: {event.event_id}")
            fraction = units / lot.units
            cash_basis_removed = lot.cash_basis_inr * fraction
            tax_basis_removed = lot.tax_basis_inr * fraction
            realized_gain = proceeds - tax_basis_removed - transfer_expenses
            if realized_gain < ZERO and abs(realized_gain) <= ARITHMETIC_TOLERANCE:
                realized_gain = ZERO
            if realized_gain != ZERO:
                if not event.tax_classification_confirmed or event.tax_classification not in {"section76", "section196", "section197", "section198"}:
                    raise ValueError(f"realized gain requires a confirmed statutory tax class: {event.event_id}")
                if event.tax_classification == "section76":
                    if lot.acquired < date(2023, 4, 1) or not event.section76_specified_fund_confirmed:
                        raise ValueError("section 76 requires a qualifying specified mutual fund and a lot acquired on/after 1 April 2023")
                    bucket = "section76"
                    character = "short"
                elif event.tax_classification == "section196":
                    if not event.section196_eligibility_confirmed:
                        raise ValueError("section 196 requires confirmed STT and asset eligibility")
                    bucket = "section196"
                    character = "short"
                elif event.tax_classification == "section197":
                    if not event.section197_eligibility_confirmed:
                        raise ValueError("section 197 requires confirmed long-term asset eligibility")
                    bucket = "section197"
                    character = "long"
                else:
                    if not event.section198_eligibility_confirmed:
                        raise ValueError("section 198 requires confirmed equity and STT eligibility")
                    bucket = "section198"
                    character = "long"
                if realized_gain < ZERO:
                    capital_loss_trace.append({
                        "event_id": event.event_id,
                        "event_date": event.event_date.isoformat(),
                        "tax_year": year,
                        "instrument_id": event.instrument_id,
                        "lot_id": event.lot_id,
                        "lot_acquired": lot.acquired.isoformat(),
                        "units_disposed": str(units),
                        "proceeds_inr": str(proceeds),
                        "tax_basis_removed_inr": str(tax_basis_removed),
                        "deductible_transfer_expenses_inr": str(transfer_expenses),
                        "signed_realized_result_inr": str(realized_gain),
                        "loss_amount_inr": str(-realized_gain),
                        "tax_bucket": bucket,
                        "character": character,
                        "tax_classification": event.tax_classification,
                        "tax_classification_confirmed": event.tax_classification_confirmed,
                        "carryforward_eligibility": {
                            "status": "UNDETERMINED_RETURN_EVIDENCE_NOT_SUPPLIED",
                            "return_filed_under_263_1": None,
                            "evidence_reference": None,
                        },
                        "eligibility_confirmed": {
                            "section76_specified_fund": event.section76_specified_fund_confirmed,
                            "section196": event.section196_eligibility_confirmed,
                            "section197": event.section197_eligibility_confirmed,
                            "section198": event.section198_eligibility_confirmed,
                        },
                        "source_or_assumption": event.source_or_assumption,
                        "qualification_status": event.qualification_status,
                    })
                if realized_gain < ZERO:
                    has_realized_loss = True
                else:
                    income = year_income(year)
                    if event.tax_classification == "section76":
                        income.ordinary_income += realized_gain
                        category = "ordinary"
                        rule_reference = "TY 2026-27 component model: section 76 specified-fund gain treated as ordinary income"
                    elif event.tax_classification == "section196":
                        income.section196_stcg += realized_gain
                        income.section196_eligible = True
                        category = "section196_stcg"
                        rule_reference = "TY 2026-27 component model: section 196 short-term gain"
                    elif event.tax_classification == "section197":
                        income.section197_ltcg += realized_gain
                        income.section197_eligible = True
                        category = "section197_ltcg"
                        rule_reference = "TY 2026-27 component model: section 197 long-term gain"
                    else:
                        income.section198_ltcg += realized_gain
                        income.section198_eligible = True
                        category = "section198_ltcg"
                        rule_reference = "TY 2026-27 component model: section 198 long-term gain"
                    record_tax_source(
                        event, category, realized_gain, rule_reference, acquired=lot.acquired,
                        disposal_details={
                            "units_disposed": str(units),
                            "proceeds_inr": str(proceeds),
                            "tax_basis_removed_inr": str(tax_basis_removed),
                            "deductible_transfer_expenses_inr": str(transfer_expenses),
                            "signed_realized_result_inr": str(realized_gain),
                        },
                    )
            elif event.tax_classification != "none" and not event.tax_classification_confirmed:
                raise ValueError("zero-gain event cannot carry an unconfirmed tax classification")

            if cash < fee:
                # The disposal's own gross proceeds can fund its transaction cost.
                if proceeds < fee - cash:
                    raise ValueError(f"disposal does not fund its transaction cost: {event.event_id}")
            cash += proceeds - fee
            transaction_costs += fee
            realized_economic_gain += proceeds - cash_basis_removed
            lot.units -= units
            lot.cash_basis_inr -= cash_basis_removed
            lot.tax_basis_inr -= tax_basis_removed
            if lot.units == ZERO:
                del lots[event.lot_id]
            continue

    # Validate each year's withholding independently of whether some other
    # year has a realized loss. A loss keeps tax application unqualified; it
    # must not disable input validation for otherwise unrelated years.
    for year, withheld in event_withholding_by_year.items():
        taxable_gross = incomes[year].ordinary_income + incomes[year].dividend_income
        if withheld > taxable_gross:
            raise ValueError(f"withholding exceeds recorded ordinary/distribution income in tax year {year}")

    prices = {lot_id: amount(price, f"valuation_prices[{lot_id}]") for lot_id, price in valuation_prices.items()}
    missing_marks = set(lots) - set(prices)
    extra_marks = set(prices) - set(lots)
    if missing_marks or extra_marks:
        raise ValueError(f"valuation lot map mismatch; missing={sorted(missing_marks)}, extra={sorted(extra_marks)}")
    ending_market_value = sum((lots[lot_id].units * prices[lot_id] for lot_id in lots), ZERO)
    remaining_cash_basis = sum((lot.cash_basis_inr for lot in lots.values()), ZERO)
    unrealized_gain = ending_market_value - remaining_cash_basis
    gross_terminal = cash + ending_market_value
    reconciliation_residual = (
        contributions + gross_income + realized_economic_gain + unrealized_gain
        - withholding - transaction_costs - other_fees - withdrawals - gross_terminal
    )
    if abs(reconciliation_residual) > ARITHMETIC_TOLERANCE:
        raise AssertionError(f"portfolio reconciliation failed by {reconciliation_residual} INR")

    open_lot_rows = [
        {
            "lot_id": lot.lot_id,
            "instrument_id": lot.instrument_id,
            "acquired": lot.acquired.isoformat(),
            "units": str(lot.units),
            "cash_basis_inr": str(lot.cash_basis_inr),
            "tax_basis_inr": str(lot.tax_basis_inr),
            "valuation_inr": str(lot.units * prices[lot.lot_id]),
            "unrealized_gain_inr": str(lot.units * prices[lot.lot_id] - lot.cash_basis_inr),
        }
        for lot in sorted(lots.values(), key=lambda item: (item.acquired, item.lot_id))
    ]

    # Preserve a reconciled economic ledger while preventing unqualified loss
    # treatment from leaking into annual tax or accessible-wealth results.
    if has_realized_loss:
        unqualified_years = sorted(set(incomes) | set(external_tax_inputs)
                                   | {row["tax_year"] for row in capital_loss_trace})
        return EventLedgerResult(
            ledger_status="ECONOMIC_PASS_TAX_UNQUALIFIED",
            event_count=len(event_list),
            tax_years={year: {"tax_qualification_status": "UNQUALIFIED_CAPITAL_LOSS_SET_OFF_NOT_APPLIED"}
                       for year in unqualified_years},
            cash_contributions_inr=contributions,
            gross_income_inr=gross_income,
            portfolio_withholding_inr=withholding,
            transaction_costs_inr=transaction_costs,
            other_fees_inr=other_fees,
            withdrawals_inr=withdrawals,
            ending_cash_inr=cash,
            ending_market_value_inr=ending_market_value,
            realized_economic_gain_inr=realized_economic_gain,
            unrealized_gain_inr=unrealized_gain,
            gross_terminal_wealth_inr=gross_terminal,
            incremental_portfolio_tax_inr=None,
            remaining_incremental_tax_after_withholding_inr=None,
            net_accessible_fixture_wealth_inr=None,
            reconciliation_residual_inr=reconciliation_residual,
            open_lots=open_lot_rows,
            tax_event_trace=tax_event_trace,
            capital_loss_trace=capital_loss_trace,
        )

    all_years = sorted(set(incomes) | set(external_tax_inputs))
    tax_year_results: dict[str, dict[str, Any]] = {}
    incremental_tax = remaining_incremental_tax = ZERO
    for year in all_years:
        if year not in external_tax_inputs:
            raise ValueError(f"explicit external tax inputs (including zero fixture values) required for {year}")
        portfolio = incomes.get(year, YearIncome())
        external = external_tax_inputs[year]
        external_only_tax = calculate_tax(external).tax_before_credits
        total_tax_input = _merge_tax_inputs(external, portfolio)
        total_tax = calculate_tax(total_tax_input)
        year_incremental_tax = total_tax.tax_before_credits - external_only_tax
        if year_incremental_tax < ZERO:
            raise NotImplementedError("portfolio loss relief and negative incremental tax are not modeled")
        year_net_after_tds = max(ZERO, year_incremental_tax - portfolio.withholding_credit)
        incremental_tax += year_incremental_tax
        remaining_incremental_tax += year_net_after_tds
        tax_year_results[year] = {
            "portfolio_income": {
                "ordinary": str(portfolio.ordinary_income),
                "dividend": str(portfolio.dividend_income),
                "section196_stcg": str(portfolio.section196_stcg),
                "section197_ltcg": str(portfolio.section197_ltcg),
                "section198_ltcg": str(portfolio.section198_ltcg),
                "withholding_credit": str(portfolio.withholding_credit),
            },
            "portfolio_income_source_event_ids": {
                category: ids for category, ids in sorted(tax_event_ids_by_year.get(year, {}).items())
            },
            "total_tax_before_credits": str(total_tax.tax_before_credits),
            "external_only_tax_before_credits": str(external_only_tax),
            "incremental_portfolio_tax": str(year_incremental_tax),
            "remaining_incremental_tax_after_portfolio_withholding": str(year_net_after_tds),
            "tax_component_scope": total_tax.calculation_scope,
        }

    fixture_wealth = gross_terminal - remaining_incremental_tax

    return EventLedgerResult(
        ledger_status="PASS",
        event_count=len(event_list),
        tax_years=tax_year_results,
        cash_contributions_inr=contributions,
        gross_income_inr=gross_income,
        portfolio_withholding_inr=withholding,
        transaction_costs_inr=transaction_costs,
        other_fees_inr=other_fees,
        withdrawals_inr=withdrawals,
        ending_cash_inr=cash,
        ending_market_value_inr=ending_market_value,
        realized_economic_gain_inr=realized_economic_gain,
        unrealized_gain_inr=unrealized_gain,
        gross_terminal_wealth_inr=gross_terminal,
        incremental_portfolio_tax_inr=incremental_tax,
        remaining_incremental_tax_after_withholding_inr=remaining_incremental_tax,
        net_accessible_fixture_wealth_inr=fixture_wealth,
        reconciliation_residual_inr=reconciliation_residual,
        open_lots=open_lot_rows,
        tax_event_trace=tax_event_trace,
        capital_loss_trace=capital_loss_trace,
    )
