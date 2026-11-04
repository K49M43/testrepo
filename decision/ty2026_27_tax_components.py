"""TY 2026–27 resident-individual tax components for deterministic fixtures.

This is a deliberately bounded research calculator, not a return-preparation
engine. It handles section 202 ordinary-rate income, eligible sections 196,
197 and 198 gains, section 76 specified-fund gains entered as ordinary-rate
income, section 156 rebate, the section 202 surcharge schedule, a documented
provisional mixed-income surcharge-relief composition, cess, and withholding
credits. Unsupported losses, deductions, non-resident/age rules, negative
ordinary residuals, and mixed relief cases whose reference composition cannot
fit fail closed. Amounts are Decimal rupees; section 516 total-income and
settlement rounding are implemented with provisional mixed-bucket handling.
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
SECTION156_1_INCOME_LIMIT = Decimal("500000")
SECTION156_1_REBATE_CAP = Decimal("12500")
BASIC_EXEMPTION_202 = Decimal("400000")
SECTION198_ANNUAL_DEDUCTION = Decimal("125000")
CESS_RATE = Decimal("0.04")
SPECIAL_SURCHARGE_CAP = Decimal("0.15")


def section516_round_rupees(amount: Decimal | int | str) -> Decimal:
    """Round non-negative total-income/payable/refundable amounts per s.516.

    Section 516 first ignores paise, then rounds to the nearest ₹10; a final
    rupee digit of 5 or more rounds upward. The helper is used for both deemed
    total income and final payable/refundable balances.
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


def section156_rebate(
    total_income: Decimal | int | str,
    section202_tax: Decimal | int | str,
    *,
    income_tax_before_rebate: Decimal | int | str | None = None,
    section198_tax: Decimal | int | str = ZERO,
) -> Decimal:
    """Calculate section 156 rebate with its section 202 cap.

    Section 156(2) measures the rebate against tax payable on total income;
    subsection (3) caps the deduction at section 202(1) tax. Section 198(7)
    specifically removes the tax payable on qualifying section 198 gains
    before allowing that rebate. The optional total-tax argument preserves
    the ordinary-only helper behavior for direct boundary calculations.
    """
    income = _amount(total_income, "total_income")
    tax = _amount(section202_tax, "section202_tax")
    total_tax = _amount(
        tax if income_tax_before_rebate is None else income_tax_before_rebate,
        "income_tax_before_rebate",
    )
    section198_amount = _amount(section198_tax, "section198_tax")
    rebate_base = max(ZERO, total_tax - section198_amount)
    if income <= SECTION156_1_INCOME_LIMIT:
        return min(rebate_base, SECTION156_1_REBATE_CAP)
    if income <= REBATE_LIMIT:
        return min(tax, REBATE_CAP, rebate_base)
    marginal_relief = max(ZERO, rebate_base - (income - REBATE_LIMIT))
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

    ordinary_income: Decimal = ZERO  # excludes section 76 gains when separately identified
    dividend_income: Decimal = ZERO
    section76_stcg: Decimal = ZERO  # deemed short-term capital gain taxed at rates in force
    section196_stcg: Decimal = ZERO
    section197_ltcg: Decimal = ZERO
    section198_ltcg: Decimal = ZERO
    tax_withheld_credit: Decimal = ZERO
    resident_individual: bool = True
    section196_eligible: bool = False
    section197_eligible: bool = False
    section198_eligible: bool = False
    section76_eligible: bool = False


@dataclass(frozen=True)
class TaxResult:
    raw_total_income: Decimal
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


def _calculate_tax(inputs: TaxInput, *, apply_marginal_relief: bool) -> TaxResult:
    """Calculate components, optionally applying the section 3(5) surcharge cap."""
    if not inputs.resident_individual:
        raise NotImplementedError("this component supports resident individuals only")
    names = (
        "ordinary_income", "dividend_income", "section76_stcg", "section196_stcg", "section197_ltcg",
        "section198_ltcg", "tax_withheld_credit",
    )
    values = {name: _amount(getattr(inputs, name), name) for name in names}
    if values["section196_stcg"] and not inputs.section196_eligible:
        raise ValueError("section 196 rate requires confirmed STT and asset eligibility")
    if values["section76_stcg"] and not inputs.section76_eligible:
        raise ValueError("section 76 treatment requires confirmed specified-fund eligibility")
    if values["section197_ltcg"] and not inputs.section197_eligible:
        raise ValueError("section 197 rate requires confirmed long-term asset eligibility")
    if values["section198_ltcg"] and not inputs.section198_eligible:
        raise ValueError("section 198 rate requires confirmed equity/STT eligibility")

    ordinary = values["ordinary_income"]
    dividends = values["dividend_income"]
    section76 = values["section76_stcg"]
    stcg = values["section196_stcg"]
    other_ltcg = values["section197_ltcg"]
    equity_ltcg = values["section198_ltcg"]
    special_gains = [gain for gain in (stcg, other_ltcg, equity_ltcg) if gain > ZERO]
    raw_normal_income = ordinary + dividends + section76
    raw_total_income = raw_normal_income + sum(special_gains, ZERO)
    total_income = section516_round_rupees(raw_total_income)
    # Section 516 deems the rounded total to be total income. The predecessor
    # return workflow rounds the final total-income field, then computes the
    # normal-rate amount as total income less separately identified special-
    # rate income. Keep the separately reported dividend amount fixed and
    # apply the residual to non-dividend ordinary income. A negative
    # normal-rate or ordinary residual cannot be allocated safely, so fail
    # closed.
    normal_income = total_income - sum(special_gains, ZERO)
    if normal_income < ZERO:
        raise NotImplementedError(
            "section 516 rounded total is below separately identified special-rate income"
        )
    ordinary_for_tax = normal_income - dividends
    if ordinary_for_tax < ZERO:
        raise NotImplementedError(
            "section 516 normal-rate base is below separately reported dividend income"
        )

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
    section196_tax = stcg * Decimal("0.20")
    section197_tax = other_ltcg * Decimal("0.125")
    section198_tax = max(ZERO, equity_ltcg - SECTION198_ANNUAL_DEDUCTION) * Decimal("0.125")
    income_tax_before_rebate = (
        ordinary_tax_before_rebate + section196_tax + section197_tax + section198_tax
    )
    rebate = section156_rebate(
        total_income,
        ordinary_tax_before_rebate,
        income_tax_before_rebate=income_tax_before_rebate,
        section198_tax=section198_tax,
    ) if inputs.resident_individual else ZERO
    normal_tax_after_rebate = max(ZERO, ordinary_tax_before_rebate - rebate)
    rebate_remaining = max(ZERO, rebate - ordinary_tax_before_rebate)
    section196_tax = max(ZERO, section196_tax - rebate_remaining)
    rebate_remaining = max(ZERO, rebate_remaining - (income_tax_before_rebate - ordinary_tax_before_rebate
                                                       - section198_tax - section197_tax))
    section197_tax = max(ZERO, section197_tax - rebate_remaining)

    # Section 3(4)(b), Table row 10: only the incremental slab tax attributable
    # to dividend income is subject to the special-income 15% surcharge cap.
    dividend_tax_before_rebate = ordinary_tax_before_rebate - section202_slab_tax(ordinary_for_tax)
    if ordinary_tax_before_rebate:
        keep_fraction = normal_tax_after_rebate / ordinary_tax_before_rebate
    else:
        keep_fraction = ZERO
    nondividend_s202_tax = section202_slab_tax(ordinary_for_tax) * keep_fraction
    dividend_s202_tax = dividend_tax_before_rebate * keep_fraction

    special_income = dividends + values["section196_stcg"] + values["section197_ltcg"] + values["section198_ltcg"]
    regular_for_25_tier = ordinary_for_tax
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

    if not apply_marginal_relief:
        surcharge_after_relief, relief = surcharge, ZERO
    else:
        surcharge_after_relief, relief = surcharge, ZERO
        # Finance Act 2026 s.3(5): cap tax+surcharge at the tax+surcharge on
        # the applicable threshold plus income above it. For a mixed income
        # fixture, hold dividend and special-rate income fixed at the threshold
        # and reduce ordinary income to construct the reference composition.
        # This is explicit and auditable; cases where that composition cannot
        # fit are fail-closed pending tax-professional confirmation.
        applicable_boundaries = [
            boundary for boundary in (Decimal("5000000"), Decimal("10000000"), Decimal("20000000"))
            if total_income > boundary
        ]
        if applicable_boundaries:
            boundary = applicable_boundaries[-1]
            nonordinary_for_surcharge = (
                dividends + values["section196_stcg"] + values["section197_ltcg"]
                + values["section198_ltcg"]
            )
            if nonordinary_for_surcharge > boundary:
                raise NotImplementedError(
                    "marginal-relief reference composition cannot preserve special income at this threshold"
                )
            reference_inputs = TaxInput(
                ordinary_income=boundary - nonordinary_for_surcharge,
                dividend_income=dividends,
                section196_stcg=values["section196_stcg"],
                section197_ltcg=values["section197_ltcg"],
                section198_ltcg=values["section198_ltcg"],
                resident_individual=inputs.resident_individual,
                section196_eligible=inputs.section196_eligible,
                section197_eligible=inputs.section197_eligible,
                section198_eligible=inputs.section198_eligible,
            )
            reference = _calculate_tax(reference_inputs, apply_marginal_relief=False)
            ceiling = (
                reference.income_tax_after_rebate + reference.surcharge_before_relief
                + total_income - boundary
            )
            uncapped_tax_and_surcharge = income_tax + surcharge
            if uncapped_tax_and_surcharge > ceiling:
                surcharge_after_relief = max(ZERO, ceiling - income_tax)
                relief = surcharge - surcharge_after_relief

    cess = (income_tax + surcharge_after_relief) * CESS_RATE
    tax_before_credits = income_tax + surcharge_after_relief + cess
    credit = values["tax_withheld_credit"]
    # Section 516 applies to the final amount payable/refundable. Keep the
    # pre-credit analytical tax precise for the ledger's marginal comparison;
    # only the statutory settlement amounts are rounded here.
    balance = section516_round_rupees(max(ZERO, tax_before_credits - credit))
    excess = section516_round_rupees(max(ZERO, credit - tax_before_credits))
    return TaxResult(
        raw_total_income=raw_total_income,
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


def calculate_tax(inputs: TaxInput) -> TaxResult:
    """Calculate bounded TY 2026–27 components with explicit eligibility flags."""
    return _calculate_tax(inputs, apply_marginal_relief=True)


def as_of_tax_year() -> str:
    return "2026-27"
