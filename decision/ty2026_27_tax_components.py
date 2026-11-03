"""TY 2026–27 resident-individual tax components for deterministic fixtures.

This is a deliberately bounded research calculator, not a return-preparation
engine. It handles section 202 ordinary-rate income, eligible sections 196,
197 and 198 gains, section 76 specified-fund gains entered as ordinary-rate
income, section 156 rebate, the section 202 surcharge schedule, cess, and tax
withholding credits. Unsupported losses, deductions, non-resident/age rules,
and mixed special-income marginal-relief cases fail closed or remain outside
this component. Amounts are Decimal rupees; statutory rupee rounding is not
applied in the fixture calculations.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal, ROUND_DOWN
from typing import Any


ZERO = Decimal("0")
ONE = Decimal("1")
SECTION202_SLABS = (
    (Decimal("400000"), Decimal("0")),
    (Decimal("800000"), Decimal("0.05")),
    (Decimal("1200000"), Decimal("0.10")),
    (Decimal("1600000"), Decimal("0.15")),
    (Decimal("2000000"), Decimal("0.20")),
    (Decimal("2400000"), Decimal("0.25")),
    (None, Decimal("0.30")),
)

REBATE_LIMIT = Decimal("1200000")
REBATE_CAP = Decimal("60000")
BASIC_EXEMPTION_202 = Decimal("400000")
SECTION198_ANNUAL_DEDUCTION = Decimal("125000")
CESS_RATE = Decimal("0.04")
SPECIAL_SURCHARGE_CAP = Decimal("0.15")


def section516_round_rupees(amount: Decimal | int | str) -> Decimal:
    """Round non-negative total-income/payable/refundable amounts per s.516.

    Section 516 first ignores paise, then rounds to the nearest ₹10; a final
    rupee digit of 5 or more rounds upward. This primitive is intentionally
    isolated: the tax component calculator does not yet apply it because the
    ordering and allocation across mixed income components needs qualification.
    """
    value = amount if isinstance(amount, Decimal) else Decimal(str(amount))
    if not value.is_finite() or value < ZERO:
        raise ValueError("section 516 amount must be finite and non-negative")
    whole_rupees = value.to_integral_value(rounding=ROUND_DOWN)
    lower_ten = (whole_rupees // Decimal("10")) * Decimal("10")
    remainder = whole_rupees - lower_ten
    return lower_ten + (Decimal("10") if remainder >= Decimal("5") else ZERO)


def _amount(value: Decimal | int | str, name: str) -> Decimal:
    result = value if isinstance(value, Decimal) else Decimal(str(value))
    if not result.is_finite() or result < ZERO:
        raise ValueError(f"{name} must be a finite, non-negative amount")
    return result


def section202_slab_tax(taxable_income: Decimal | int | str) -> Decimal:
    """Tax under section 202(1), before rebate, surcharge, and cess."""
    income = _amount(taxable_income, "taxable_income")
    tax = ZERO
    lower = ZERO
    for upper, rate in SECTION202_SLABS:
        slice_end = income if upper is None else min(income, upper)
        if slice_end > lower:
            tax += (slice_end - lower) * rate
        if upper is None or income <= upper:
            break
        lower = upper
    return tax


def section156_rebate(normal_rate_income: Decimal | int | str, section202_tax: Decimal | int | str) -> Decimal:
    """Section 156(2) rebate against section 202(1) tax only.

    Special-rate capital gains are excluded from ``normal_rate_income`` and
    their tax is never reduced by this function. The ₹12 lakh threshold and
    marginal relief therefore use the income taxed at section 202(1).
    """
    income = _amount(normal_rate_income, "normal_rate_income")
    tax = _amount(section202_tax, "section202_tax")
    if income <= REBATE_LIMIT:
        return min(tax, REBATE_CAP)
    marginal_relief = max(ZERO, tax - (income - REBATE_LIMIT))
    return min(tax, marginal_relief)


def section76_specified_fund_gain(
    proceeds: Decimal | int | str,
    cost: Decimal | int | str,
    eligible_transfer_expenses: Decimal | int | str,
    *,
    acquired_on_or_after_2023_04_01: bool,
    specified_mutual_fund_confirmed: bool,
) -> Decimal:
    """Return section 76 deemed-ST gain for a qualifying post-1-Apr-2023 unit.

    The caller must separately establish the scheme's statutory definition.
    This function does not classify an ETF or assume that a G-Sec fund meets it.
    """
    proceeds_amount = _amount(proceeds, "proceeds")
    cost_amount = _amount(cost, "cost")
    expenses = _amount(eligible_transfer_expenses, "eligible_transfer_expenses")
    if not acquired_on_or_after_2023_04_01 or not specified_mutual_fund_confirmed:
        raise ValueError("section 76 requires a qualifying unit acquired on/after 1 April 2023")
    gain = proceeds_amount - cost_amount - expenses
    if gain < ZERO:
        raise NotImplementedError("capital-loss set-off and carry-forward are outside this component")
    return gain


@dataclass(frozen=True)
class TaxInput:
    """Annual aggregated taxable income for the supported TY 2026–27 fixture."""

    ordinary_income: Decimal = ZERO  # includes interest/coupons and section 76 gains
    dividend_income: Decimal = ZERO
    section196_stcg: Decimal = ZERO
    section197_ltcg: Decimal = ZERO
    section198_ltcg: Decimal = ZERO
    tax_withheld_credit: Decimal = ZERO
    resident_individual: bool = True
    section196_eligible: bool = False
    section197_eligible: bool = False
    section198_eligible: bool = False


@dataclass(frozen=True)
class TaxResult:
    total_income: Decimal
    normal_rate_income: Decimal
    section202_tax_before_rebate: Decimal
    section156_rebate: Decimal
    section196_tax: Decimal
    section197_tax: Decimal
    section198_tax: Decimal
    income_tax_after_rebate: Decimal
    surcharge_before_relief: Decimal
    marginal_surcharge_relief: Decimal
    surcharge_after_relief: Decimal
    cess: Decimal
    tax_before_credits: Decimal
    withholding_credit: Decimal
    balance_payable: Decimal
    excess_credit: Decimal
    calculation_scope: str = "RESEARCH_COMPONENT_ONLY; not a personal tax result"

    def as_json(self) -> dict[str, Any]:
        return {key: str(value) if isinstance(value, Decimal) else value for key, value in asdict(self).items()}


def _surcharge_rate(total_income: Decimal, ordinary_ex_dividend_and_special_gains: Decimal) -> Decimal:
    if total_income <= Decimal("5000000"):
        return ZERO
    if total_income <= Decimal("10000000"):
        return Decimal("0.10")
    if total_income <= Decimal("20000000"):
        return Decimal("0.15")
    if ordinary_ex_dividend_and_special_gains > Decimal("20000000"):
        return Decimal("0.25")
    return Decimal("0.15")


def _ordinary_surcharge_relief(
    ordinary_income: Decimal,
    tax_after_rebate: Decimal,
    surcharge_before_relief: Decimal,
) -> tuple[Decimal, Decimal]:
    """Return (surcharge after relief, relief) for ordinary-only income."""
    boundaries = (
        (Decimal("5000000"), ZERO),
        (Decimal("10000000"), Decimal("0.10")),
        (Decimal("20000000"), Decimal("0.15")),
    )
    for boundary, threshold_rate in boundaries:
        if ordinary_income <= boundary:
            continue
        baseline_tax = section202_slab_tax(boundary)
        baseline_surcharge = baseline_tax * threshold_rate
        ceiling = baseline_tax + baseline_surcharge + (ordinary_income - boundary)
        uncapped = tax_after_rebate + surcharge_before_relief
        if uncapped > ceiling:
            allowed_surcharge = max(ZERO, ceiling - tax_after_rebate)
            return allowed_surcharge, surcharge_before_relief - allowed_surcharge
    return surcharge_before_relief, ZERO


def calculate_tax(inputs: TaxInput) -> TaxResult:
    """Calculate bounded TY 2026–27 components with explicit eligibility flags."""
    if not inputs.resident_individual:
        raise NotImplementedError("this component supports resident individuals only")
    names = (
        "ordinary_income", "dividend_income", "section196_stcg", "section197_ltcg",
        "section198_ltcg", "tax_withheld_credit",
    )
    values = {name: _amount(getattr(inputs, name), name) for name in names}
    if values["section196_stcg"] and not inputs.section196_eligible:
        raise ValueError("section 196 rate requires confirmed STT and asset eligibility")
    if values["section197_ltcg"] and not inputs.section197_eligible:
        raise ValueError("section 197 rate requires confirmed long-term asset eligibility")
    if values["section198_ltcg"] and not inputs.section198_eligible:
        raise ValueError("section 198 rate requires confirmed equity/STT eligibility")

    ordinary = values["ordinary_income"]
    dividends = values["dividend_income"]
    stcg = values["section196_stcg"]
    other_ltcg = values["section197_ltcg"]
    equity_ltcg = values["section198_ltcg"]
    special_gains = [gain for gain in (stcg, other_ltcg, equity_ltcg) if gain > ZERO]
    normal_income = ordinary + dividends
    total_income = normal_income + sum(special_gains, ZERO)

    basic_shortfall = max(ZERO, BASIC_EXEMPTION_202 - normal_income) if inputs.resident_individual else ZERO
    if basic_shortfall and len(special_gains) > 1:
        raise NotImplementedError("basic-exemption allocation across multiple special-gain sections is not specified")
    if basic_shortfall and special_gains:
        if stcg:
            stcg = max(ZERO, stcg - basic_shortfall)
        elif other_ltcg:
            other_ltcg = max(ZERO, other_ltcg - basic_shortfall)
        else:
            equity_ltcg = max(ZERO, equity_ltcg - basic_shortfall)

    ordinary_tax_before_rebate = section202_slab_tax(normal_income)
    rebate = section156_rebate(normal_income, ordinary_tax_before_rebate) if inputs.resident_individual else ZERO
    normal_tax_after_rebate = ordinary_tax_before_rebate - rebate
    section196_tax = stcg * Decimal("0.20")
    section197_tax = other_ltcg * Decimal("0.125")
    section198_tax = max(ZERO, equity_ltcg - SECTION198_ANNUAL_DEDUCTION) * Decimal("0.125")

    # Section 3(4)(b), Table row 10: only the incremental slab tax attributable
    # to dividend income is subject to the special-income 15% surcharge cap.
    dividend_tax_before_rebate = ordinary_tax_before_rebate - section202_slab_tax(ordinary)
    if ordinary_tax_before_rebate:
        keep_fraction = normal_tax_after_rebate / ordinary_tax_before_rebate
    else:
        keep_fraction = ZERO
    nondividend_s202_tax = section202_slab_tax(ordinary) * keep_fraction
    dividend_s202_tax = dividend_tax_before_rebate * keep_fraction

    special_income = dividends + values["section196_stcg"] + values["section197_ltcg"] + values["section198_ltcg"]
    regular_for_25_tier = ordinary
    rate = _surcharge_rate(total_income, regular_for_25_tier)
    special_rate = min(rate, SPECIAL_SURCHARGE_CAP)
    surcharge = (
        nondividend_s202_tax * rate
        + dividend_s202_tax * special_rate
        + section196_tax * special_rate
        + section197_tax * special_rate
        + section198_tax * special_rate
    )
    income_tax = normal_tax_after_rebate + section196_tax + section197_tax + section198_tax

    if special_income == ZERO:
        surcharge_after_relief, relief = _ordinary_surcharge_relief(ordinary, income_tax, surcharge)
    elif total_income > Decimal("5000000") and income_tax + surcharge > total_income - max(
        threshold for threshold in (Decimal("5000000"), Decimal("10000000"), Decimal("20000000"))
        if total_income > threshold
    ):
        # A mixed-income marginal-relief base depends on the statutory tax
        # composition at the threshold. Do not invent that allocation.
        # Example cases below the excess-income lower bound need no relief.
        raise NotImplementedError("mixed special-income surcharge marginal relief needs a threshold-composition audit")
    else:
        surcharge_after_relief, relief = surcharge, ZERO

    cess = (income_tax + surcharge_after_relief) * CESS_RATE
    tax_before_credits = income_tax + surcharge_after_relief + cess
    credit = values["tax_withheld_credit"]
    balance = max(ZERO, tax_before_credits - credit)
    excess = max(ZERO, credit - tax_before_credits)
    return TaxResult(
        total_income=total_income,
        normal_rate_income=normal_income,
        section202_tax_before_rebate=ordinary_tax_before_rebate,
        section156_rebate=rebate,
        section196_tax=section196_tax,
        section197_tax=section197_tax,
        section198_tax=section198_tax,
        income_tax_after_rebate=income_tax,
        surcharge_before_relief=surcharge,
        marginal_surcharge_relief=relief,
        surcharge_after_relief=surcharge_after_relief,
        cess=cess,
        tax_before_credits=tax_before_credits,
        withholding_credit=credit,
        balance_payable=balance,
        excess_credit=excess,
    )


def as_of_tax_year() -> str:
    return "2026-27"
