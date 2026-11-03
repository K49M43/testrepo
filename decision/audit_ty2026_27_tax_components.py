"""Boundary and worked-example audit for TY 2026–27 tax components."""

from __future__ import annotations

import json
from decimal import Decimal

from ty2026_27_tax_components import (
    TaxInput,
    calculate_tax,
    section156_rebate,
    section202_slab_tax,
    section76_specified_fund_gain,
    section516_round_rupees,
)


D = Decimal


def close(actual: Decimal, expected: str) -> None:
    assert actual == D(expected), f"expected {expected}, got {actual}"


def audit() -> dict[str, object]:
    # Section 516 drops paise before rounding to ₹10, with 5 rupees upward.
    for raw, expected in (("4.99", "0"), ("5", "10"), ("14.99", "10"),
                          ("15", "20"), ("19.99", "20"), ("20", "20")):
        close(section516_round_rupees(raw), expected)
    try:
        section516_round_rupees("-0.01")
    except ValueError:
        pass
    else:
        raise AssertionError("section 516 rounding must reject negative amounts")

    # Section 202 slab arithmetic, including statutory band edges.
    close(section202_slab_tax(D("1200000")), "60000.00")
    close(section202_slab_tax(D("2400000")), "300000.00")
    close(section202_slab_tax(D("5000000")), "1080000.00")

    # Section 156 rebate and its marginal-relief boundary.
    close(section156_rebate(D("1200000"), D("60000")), "60000")
    close(section156_rebate(D("1210000"), D("61500")), "51500")
    close(section156_rebate(D("1270588"), section202_slab_tax(D("1270588"))), "0.20")
    close(section156_rebate(D("1270589"), section202_slab_tax(D("1270589"))), "0")

    # Finance Act 2026 ordinary-only surcharge/marginal relief examples A.
    ordinary_cases = (
        ("5000000", "1123200.00", "0"),
        ("5000001", "1123201.04", "107999.33"),
        ("10000000", "2951520.00", "0"),
        ("10000001", "2951521.04", "128999.345"),
        ("20000000", "6673680.00", "0"),
        ("20000001", "6673681.04", "557999.375"),
    )
    for income, total_expected, surcharge_expected in ordinary_cases:
        result = calculate_tax(TaxInput(ordinary_income=D(income)))
        close(result.tax_before_credits, total_expected)
        if income in ("5000001", "10000001", "20000001"):
            close(result.marginal_surcharge_relief, surcharge_expected)

    # Example B: ordinary income plus eligible section 198 LTCG and 15% cap.
    example_b = calculate_tax(TaxInput(
        ordinary_income=D("21000000"),
        section198_ltcg=D("10000000"),
        section198_eligible=True,
    ))
    close(example_b.section202_tax_before_rebate, "5880000.00")
    close(example_b.section198_tax, "1234375.000")
    close(example_b.surcharge_before_relief, "1655156.25000")
    close(example_b.marginal_surcharge_relief, "0")
    close(example_b.tax_before_credits, "9120312.5000000")

    # Standalone capital-gain rates and annual section 198 allowance.
    stcg_example = calculate_tax(TaxInput(
        ordinary_income=D("400000"), section196_stcg=D("100000"), section196_eligible=True,
    ))
    close(stcg_example.section196_tax, "20000.00")
    close(stcg_example.tax_before_credits, "20800.0000")
    standard_ltcg_example = calculate_tax(TaxInput(
        ordinary_income=D("400000"), section197_ltcg=D("200000"), section197_eligible=True,
    ))
    close(standard_ltcg_example.section197_tax, "25000.000")
    equity_ltcg_threshold = calculate_tax(TaxInput(
        ordinary_income=D("400000"), section198_ltcg=D("125000"), section198_eligible=True,
    ))
    close(equity_ltcg_threshold.section198_tax, "0")
    equity_ltcg_over = calculate_tax(TaxInput(
        ordinary_income=D("400000"), section198_ltcg=D("200000"), section198_eligible=True,
    ))
    close(equity_ltcg_over.section198_tax, "9375.000")
    basic_exemption_adjustment = calculate_tax(TaxInput(
        ordinary_income=D("200000"), section198_ltcg=D("500000"), section198_eligible=True,
    ))
    close(basic_exemption_adjustment.section198_tax, "21875.000")
    try:
        calculate_tax(TaxInput(section196_stcg=D("100000")))
    except ValueError:
        pass
    else:
        raise AssertionError("special capital-gain rate must require an explicit eligibility predicate")
    try:
        calculate_tax(TaxInput(resident_individual=False))
    except NotImplementedError:
        pass
    else:
        raise AssertionError("non-resident inputs must fail closed")

    # These combinations are known to need additional legal composition work;
    # keep them as explicit failures rather than producing plausible numbers.
    try:
        calculate_tax(TaxInput(
            ordinary_income=D("200000"),
            section196_stcg=D("50000"), section197_ltcg=D("50000"),
            section196_eligible=True, section197_eligible=True,
        ))
    except NotImplementedError as error:
        assert "basic-exemption allocation" in str(error)
    else:
        raise AssertionError("ambiguous basic-exemption allocation must fail closed")
    try:
        calculate_tax(TaxInput(
            ordinary_income=D("4900000"), section196_stcg=D("200000"), section196_eligible=True,
        ))
    except NotImplementedError as error:
        assert "mixed special-income surcharge marginal relief" in str(error)
    else:
        raise AssertionError("unqualified mixed-income surcharge marginal relief must fail closed")

    # Specified-fund section 76 gains are explicit ordinary-rate inputs; the
    # helper refuses to apply the rule without both legal predicates.
    gain = section76_specified_fund_gain(
        "125000", "100000", "100", acquired_on_or_after_2023_04_01=True,
        specified_mutual_fund_confirmed=True,
    )
    close(gain, "24900")
    try:
        section76_specified_fund_gain(
            "125000", "100000", "100", acquired_on_or_after_2023_04_01=True,
            specified_mutual_fund_confirmed=False,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("section 76 must fail closed without scheme qualification")

    # Withholding is a credit against the final liability, not a tax expense.
    credited = calculate_tax(TaxInput(ordinary_income=D("1500000"), tax_withheld_credit=D("5000")))
    close(credited.tax_before_credits, "109200.0000")
    close(credited.balance_payable, "104200.0000")

    return {
        "audit": "PASS",
        "scope": "TY 2026–27 resident individual research components; section 516 helper audited but not integrated",
        "surcharge_boundary_examples": 6,
        "special_gain_rate_examples": 5,
        "section198_example_b_tax_inr": str(example_b.tax_before_credits),
        "section76_gain_inr": str(gain),
        "section156_rebate_boundary": "PASS",
        "withholding_credit_separate": "PASS",
        "unsupported_mixed_income_boundaries_fail_closed": "PASS",
        "statutory_rounding_primitive": "PASS; isolated section 516 helper audited",
        "statutory_rounding_in_tax_calculator": "OPEN; not yet applied to income or final liability",
        "authorization": "NO-GO",
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
