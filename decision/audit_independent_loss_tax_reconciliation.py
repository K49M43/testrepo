"""Independent Decimal hand-reconciliation of bounded TY 2026-27 cases.

This audit deliberately re-derives slab tax, section 156 rebate, surcharge
relief, cess, and withholding without calling production calculation helpers.
It imports the production tax component only as the comparison target.
Capital-loss allocation itself is separately checked by the event-ledger audit.
"""

from __future__ import annotations

import json
from decimal import Decimal, ROUND_DOWN

from ty2026_27_tax_components import TaxInput, calculate_tax


D = Decimal
ZERO = D("0")
CESS = D("0.04")


def round_s516(value: Decimal) -> Decimal:
    whole = value.to_integral_value(rounding=ROUND_DOWN)
    lower = (whole // D("10")) * D("10")
    return lower + (D("10") if whole - lower >= D("5") else ZERO)


def slab_202(value: Decimal) -> Decimal:
    bands = (
        (D("400000"), D("0")), (D("800000"), D("0.05")),
        (D("1200000"), D("0.10")), (D("1600000"), D("0.15")),
        (D("2000000"), D("0.20")), (D("2400000"), D("0.25")),
        (None, D("0.30")),
    )
    tax = ZERO
    lower = ZERO
    for upper, rate in bands:
        end = value if upper is None else min(value, upper)
        if end > lower:
            tax += (end - lower) * rate
        if upper is None or value <= upper:
            break
        lower = upper
    return tax


def hand_tax(
    *, ordinary: Decimal = ZERO, dividend: Decimal = ZERO, section76: Decimal = ZERO,
    section196: Decimal = ZERO, section197: Decimal = ZERO, section198: Decimal = ZERO,
    withholding: Decimal = ZERO,
) -> dict[str, Decimal]:
    """Hand formula for cases kept within this audit's supported composition."""
    raw_total = ordinary + dividend + section76 + section196 + section197 + section198
    total = round_s516(raw_total)
    normal = total - section196 - section197 - section198
    tax202 = slab_202(normal)
    tax196 = section196 * D("0.20")
    tax197 = section197 * D("0.125")
    tax198 = max(ZERO, section198 - D("125000")) * D("0.125")
    total_tax_pre_rebate = tax202 + tax196 + tax197 + tax198
    rebate_base = total_tax_pre_rebate - tax198

    if total <= D("500000"):
        rebate = min(rebate_base, D("12500"))
    elif total <= D("1200000"):
        rebate = min(tax202, D("60000"), rebate_base)
    else:
        rebate = min(tax202, max(ZERO, rebate_base - (total - D("1200000"))))

    normal_after_rebate = max(ZERO, tax202 - rebate)
    remaining_rebate = max(ZERO, rebate - tax202)
    tax196_after_rebate = max(ZERO, tax196 - remaining_rebate)
    remaining_rebate = max(ZERO, remaining_rebate - tax196)
    tax197_after_rebate = max(ZERO, tax197 - remaining_rebate)
    income_tax = normal_after_rebate + tax196_after_rebate + tax197_after_rebate + tax198

    rate = D("0.10") if total > D("5000000") else ZERO
    surcharge = (normal_after_rebate + tax196_after_rebate + tax197_after_rebate) * rate
    surcharge += tax198 * min(rate, D("0.15"))
    relief = ZERO
    if total > D("5000000") and total <= D("10000000"):
        threshold = D("5000000")
        fixed_special = section196 + section197 + section198
        reference_ordinary = threshold - dividend - fixed_special
        reference_202 = slab_202(reference_ordinary + dividend)
        reference_special = section196 * D("0.20") + section197 * D("0.125")
        reference_special += max(ZERO, section198 - D("125000")) * D("0.125")
        reference_tax = reference_202 + reference_special
        cap = reference_tax + (total - threshold)
        relief = max(ZERO, income_tax + surcharge - cap)
        relief = min(relief, surcharge)
    surcharge_after_relief = surcharge - relief
    cess = (income_tax + surcharge_after_relief) * CESS
    gross_tax = income_tax + surcharge_after_relief + cess
    payable = max(ZERO, gross_tax - withholding)
    excess = max(ZERO, withholding - gross_tax)
    return {
        "total_income": total, "tax202": tax202, "rebate": rebate,
        "section196_tax": tax196_after_rebate, "section197_tax": tax197_after_rebate,
        "section198_tax": tax198,
        "income_tax_after_rebate": income_tax, "surcharge": surcharge,
        "marginal_relief": relief, "surcharge_after_relief": surcharge_after_relief,
        "cess": cess, "gross_tax": gross_tax,
        "balance_payable": round_s516(payable), "excess_credit": round_s516(excess),
    }


def close(actual: Decimal, expected: Decimal, label: str) -> None:
    if abs(actual - expected) > D("0.000000001"):
        raise AssertionError(f"{label}: actual {actual}, independent {expected}")


def compare(input_values: dict[str, Decimal], label: str) -> dict[str, str]:
    expected = hand_tax(**input_values)
    actual = calculate_tax(TaxInput(
        ordinary_income=input_values.get("ordinary", ZERO),
        dividend_income=input_values.get("dividend", ZERO),
        section76_stcg=input_values.get("section76", ZERO),
        section196_stcg=input_values.get("section196", ZERO),
        section197_ltcg=input_values.get("section197", ZERO),
        section198_ltcg=input_values.get("section198", ZERO),
        tax_withheld_credit=input_values.get("withholding", ZERO),
        section76_eligible=bool(input_values.get("section76", ZERO)),
        section196_eligible=bool(input_values.get("section196", ZERO)),
        section197_eligible=bool(input_values.get("section197", ZERO)),
        section198_eligible=bool(input_values.get("section198", ZERO)),
    ))
    actual_map = {
        "total_income": actual.total_income,
        "tax202": actual.section202_tax_before_rebate,
        "rebate": actual.section156_rebate,
        "section196_tax": actual.section196_tax,
        "section197_tax": actual.section197_tax,
        "section198_tax": actual.section198_tax,
        "income_tax_after_rebate": actual.income_tax_after_rebate,
        "surcharge": actual.surcharge_before_relief,
        "marginal_relief": actual.marginal_surcharge_relief,
        "surcharge_after_relief": actual.surcharge_after_relief,
        "cess": actual.cess,
        "gross_tax": actual.tax_before_credits,
        "balance_payable": actual.balance_payable,
        "excess_credit": actual.excess_credit,
    }
    for component, value in actual_map.items():
        close(value, expected[component], f"{label}.{component}")
    return {component: str(value) for component, value in expected.items()}


def audit() -> dict[str, object]:
    s156_1 = compare({"ordinary": D("400000"), "section196": D("100000")}, "section156(1)")
    s156_2 = compare({"ordinary": D("1190000"), "section196": D("50000")}, "section156(2)")
    mixed_relief = compare({"ordinary": D("4900000"), "section196": D("200000")}, "mixed_surcharge")
    s76_gross = compare({"ordinary": D("1200000"), "section76": D("20")}, "section76_gross")
    s76_net = compare({"ordinary": D("1200000"), "section76": D("10")}, "section76_net")
    s198_gross = compare({"ordinary": D("3000000"), "section198": D("200000")}, "section198_gross")
    s198_net = compare({"ordinary": D("3000000"), "section198": D("190000")}, "section198_net")
    carried_gross = compare({
        "ordinary": D("3000000"), "dividend": D("500"), "section197": D("38"),
    }, "carried_loss_gross")
    carried_net = compare({
        "ordinary": D("3000000"), "dividend": D("500"), "section197": D("28"),
        "withholding": D("50"),
    }, "carried_loss_net")
    carried_external = compare({"ordinary": D("3000000")}, "carried_loss_external_only")
    close(D(carried_gross["gross_tax"]) - D(carried_external["gross_tax"]), D("161.564"), "carried_loss.gross_increment")
    close(D(carried_net["gross_tax"]) - D(carried_external["gross_tax"]), D("160.264"), "carried_loss.net_increment")
    close(D(carried_net["gross_tax"]) - D(carried_external["gross_tax"]) - D("50"),
          D("110.264"), "carried_loss.net_increment_after_withholding")
    close(D(carried_net["balance_payable"]) - D(carried_external["balance_payable"]), D("110"),
          "carried_loss.rounded_balance_increment")

    return {
        "audit": "PASS",
        "method": "independent Decimal formulas; production calculator imported only as comparison target",
        "section156_1_mixed_case": s156_1,
        "section156_2_mixed_case": s156_2,
        "mixed_surcharge_reference_case": mixed_relief,
        "section76_gross_case": s76_gross,
        "section76_after_short_loss_case": s76_net,
        "section198_gross_case": s198_gross,
        "section198_after_long_loss_case": s198_net,
        "carried_section197_gross_case": carried_gross,
        "carried_section197_net_of_10_loss_case": carried_net,
        "carried_section197_external_only_baseline": carried_external,
        "carried_loss_incremental_tax_before_after": ["161.564", "160.264"],
        "carried_loss_increment_after_50_withholding": "110.264",
        "investment_authorization": "NO-GO",
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
