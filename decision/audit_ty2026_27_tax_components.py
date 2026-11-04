"""Boundary and worked-example audit for TY 2026–27 tax components."""

from __future__ import annotations

import json
from decimal import Decimal

from ty2026_27_tax_components import (
    CESS_RATE,
    TaxInput,
    ZERO,
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

    # Section 516 applies to the final computed total income before statutory
    # threshold tests. The normal-rate base is the rounded total less the
    # separately identified special-rate income. These are arithmetic probes;
    # the mixed-bucket residual convention remains subject to qualified review.
    rounding_down = calculate_tax(TaxInput(ordinary_income=D("5000001")))
    assert rounding_down.raw_total_income == D("5000001")
    assert rounding_down.total_income == D("5000000")
    close(rounding_down.normal_rate_income, "5000000")
    close(rounding_down.tax_before_credits, "1123200.0000")
    rounding_up = calculate_tax(TaxInput(ordinary_income=D("5000005")))
    assert rounding_up.raw_total_income == D("5000005")
    assert rounding_up.total_income == D("5000010")
    close(rounding_up.tax_before_credits, "1123210.4000")
    close(rounding_up.marginal_surcharge_relief, "107993.3000")
    mixed_total_rounding = calculate_tax(TaxInput(
        ordinary_income=D("4900004"), section196_stcg=D("100000"), section196_eligible=True,
    ))
    assert mixed_total_rounding.raw_total_income == D("5000004")
    assert mixed_total_rounding.total_income == D("5000000")
    close(mixed_total_rounding.normal_rate_income, "4900000")
    close(mixed_total_rounding.section202_tax_before_rebate, "1050000.00")
    close(mixed_total_rounding.tax_before_credits, "1112800.0000")
    rounded_rebate_threshold = calculate_tax(TaxInput(
        ordinary_income=D("1190006"), section198_ltcg=D("10000"), section198_eligible=True,
    ))
    assert rounded_rebate_threshold.raw_total_income == D("1200006")
    assert rounded_rebate_threshold.total_income == D("1200010")
    close(rounded_rebate_threshold.section202_tax_before_rebate, "59001.00")
    close(rounded_rebate_threshold.section156_rebate, "58991.00")
    close(rounded_rebate_threshold.tax_before_credits, "10.4000")
    dividend_rounding = calculate_tax(TaxInput(
        ordinary_income=D("5000000"), dividend_income=D("1"),
    ))
    assert dividend_rounding.raw_total_income == D("5000001")
    assert dividend_rounding.total_income == D("5000000")
    close(dividend_rounding.normal_rate_income, "5000000")
    try:
        calculate_tax(TaxInput(dividend_income=D("5000001")))
    except NotImplementedError as error:
        assert "below separately reported dividend income" in str(error)
    else:
        raise AssertionError("negative ordinary residual under dividends must fail closed")
    try:
        calculate_tax(TaxInput(section198_ltcg=D("1000003"), section198_eligible=True))
    except NotImplementedError as error:
        assert "below separately identified special-rate income" in str(error)
    else:
        raise AssertionError("negative normal-rate residual must fail closed")

    # Section 156 rebate and its marginal-relief boundary.
    close(section156_rebate(
        D("500000"), D("0"), income_tax_before_rebate=D("20000"), section198_tax=D("5000"),
    ), "12500")
    close(section156_rebate(
        D("500001"), D("0"), income_tax_before_rebate=D("20000"), section198_tax=D("5000"),
    ), "0")
    section156_1_mix = calculate_tax(TaxInput(
        ordinary_income=D("400000"), section196_stcg=D("100000"),
        section196_eligible=True,
    ))
    close(section156_1_mix.section156_rebate, "12500")
    close(section156_1_mix.section196_tax, "7500")
    close(section156_1_mix.tax_before_credits, "7800")
    close(section156_rebate(D("1200000"), D("60000")), "60000")
    close(section156_rebate(D("1210000"), D("61500")), "51500")
    close(section156_rebate(D("1270588"), section202_slab_tax(D("1270588"))), "0.20")
    close(section156_rebate(D("1270589"), section202_slab_tax(D("1270589"))), "0")
    mixed_rebate_at_limit = calculate_tax(TaxInput(
        ordinary_income=D("1190000"), section198_ltcg=D("10000"), section198_eligible=True,
    ))
    assert mixed_rebate_at_limit.total_income == D("1200000")
    close(mixed_rebate_at_limit.section156_rebate, "59000.00")
    close(mixed_rebate_at_limit.tax_before_credits, "0.0000")
    mixed_rebate_10_over = calculate_tax(TaxInput(
        ordinary_income=D("1190000"), section198_ltcg=D("10010"), section198_eligible=True,
    ))
    assert mixed_rebate_10_over.total_income == D("1200010")
    close(mixed_rebate_10_over.section156_rebate, "58990.00")
    close(mixed_rebate_10_over.tax_before_credits, "10.4000")
    mixed_rebate_edge = calculate_tax(TaxInput(
        ordinary_income=D("1190000"),
        section198_ltcg=D("30000"),
        section198_eligible=True,
    ))
    assert mixed_rebate_edge.total_income == D("1220000")
    close(mixed_rebate_edge.section202_tax_before_rebate, "59000.00")
    close(mixed_rebate_edge.section156_rebate, "39000.00")
    close(mixed_rebate_edge.section198_tax, "0")
    close(mixed_rebate_edge.tax_before_credits, "20800.0000")
    mixed_stcg_rebate = calculate_tax(TaxInput(
        ordinary_income=D("1190000"), section196_stcg=D("50000"),
        section196_eligible=True,
    ))
    close(mixed_stcg_rebate.section202_tax_before_rebate, "59000")
    close(mixed_stcg_rebate.section196_tax, "10000")
    close(mixed_stcg_rebate.section156_rebate, "29000")
    close(mixed_stcg_rebate.tax_before_credits, "41600.0000")

    # Finance Act 2026 ordinary-only surcharge/marginal relief examples A.
    ordinary_cases = (
        ("5000000", "1123200.0000", "0"),
        ("5000001", "1123200.0000", "0"),
        ("5000005", "1123210.4000", "107993.3000"),
        ("10000000", "2951520.0000", "0"),
        ("10000001", "2951520.0000", "0"),
        ("10000005", "2951530.4000", "128993.4500"),
        ("20000000", "6673680.0000", "0"),
        ("20000001", "6673680.0000", "0"),
        ("20000005", "6673690.4000", "557993.7500"),
    )
    for income, total_expected, surcharge_expected in ordinary_cases:
        result = calculate_tax(TaxInput(ordinary_income=D(income)))
        close(result.tax_before_credits, total_expected)
        if income in ("5000005", "10000005", "20000005"):
            close(result.marginal_surcharge_relief, surcharge_expected)

    # Mixed-income probes immediately below, at, and above each total-income
    # surcharge threshold. These assert component invariants, not a legal
    # disposition of the provisional reference-composition convention.
    mixed_boundary_cases = (
        (D("5000000"), "section196_stcg", "section196_eligible"),
        (D("10000000"), "section197_ltcg", "section197_eligible"),
        (D("20000000"), "section198_ltcg", "section198_eligible"),
    )
    for boundary, gain_name, eligibility_name in mixed_boundary_cases:
        for delta in (D("-10"), D("0"), D("10")):
            gain = D("100000")
            tax_input = {
                "ordinary_income": boundary + delta - gain,
                gain_name: gain,
                eligibility_name: True,
            }
            mixed = calculate_tax(TaxInput(**tax_input))
            assert mixed.raw_total_income == boundary + delta
            assert mixed.total_income == section516_round_rupees(boundary + delta)
            assert ZERO <= mixed.marginal_surcharge_relief <= mixed.surcharge_before_relief
            close(mixed.surcharge_after_relief + mixed.marginal_surcharge_relief,
                  str(mixed.surcharge_before_relief))
            close(mixed.cess,
                  str((mixed.income_tax_after_rebate + mixed.surcharge_after_relief) * CESS_RATE))

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
    close(stcg_example.section196_tax, "7500.00")
    close(stcg_example.section156_rebate, "12500")
    close(stcg_example.tax_before_credits, "7800.0000")
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
    # Mixed-income s.3(5) relief uses a transparent reference composition:
    # keep special-rate income fixed and reduce ordinary income to the band
    # threshold. This fixture is deliberately near the ₹50L boundary.
    mixed_relief = calculate_tax(TaxInput(
        ordinary_income=D("4900000"), section196_stcg=D("200000"), section196_eligible=True,
    ))
    close(mixed_relief.income_tax_after_rebate, "1090000.000")
    close(mixed_relief.surcharge_before_relief, "109000.00000")
    close(mixed_relief.marginal_surcharge_relief, "39000.00000")
    close(mixed_relief.surcharge_after_relief, "70000.000")
    close(mixed_relief.tax_before_credits, "1206400.00000")
    mixed_10m_edge = calculate_tax(TaxInput(
        ordinary_income=D("9800005"), section196_stcg=D("200000"), section196_eligible=True,
    ))
    assert mixed_10m_edge.total_income == D("10000010")
    close(mixed_10m_edge.marginal_surcharge_relief, "127993.45000")
    close(mixed_10m_edge.surcharge_after_relief, "256007.00000")
    try:
        calculate_tax(TaxInput(section196_stcg=D("6000000"), section196_eligible=True))
    except NotImplementedError as error:
        assert "cannot preserve special income" in str(error)
    else:
        raise AssertionError("reference composition beyond the threshold must fail closed")

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
    fractional_due = calculate_tax(TaxInput(
        ordinary_income=D("1500001"), tax_withheld_credit=D("5000"),
    ))
    close(fractional_due.balance_payable,
          str(section516_round_rupees(fractional_due.tax_before_credits - D("5000"))))
    fully_credited = calculate_tax(TaxInput(
        ordinary_income=D("1500000"), tax_withheld_credit=credited.tax_before_credits + D("15"),
    ))
    close(fully_credited.balance_payable, "0")
    close(fully_credited.excess_credit, "20")

    return {
        "audit": "PASS",
        "scope": "TY 2026–27 resident individual research components; section 516 total income and final payable/refund rounding integrated; bucket residual is an accepted modeling convention",
        "surcharge_boundary_examples": 9,
        "mixed_surcharge_boundary_probes": 9,
        "special_gain_rate_examples": 5,
        "section198_example_b_tax_inr": str(example_b.tax_before_credits),
        "section76_gain_inr": str(gain),
        "section156_mixed_income_rule": "PASS at fixture scope; sections 156(1)/(2), section 198(7), and section 202(1) cap applied",
        "withholding_credit_separate": "PASS",
        "mixed_income_marginal_relief_reference_case": "PASS; reference mix is an explicit provisional assumption",
        "unsupported_mixed_income_reference_overflow_fails_closed": "PASS",
        "statutory_rounding_primitive": "PASS; section 516 helper applied to deemed total income and settlement amounts",
        "statutory_rounding_final_payable_refund": "PASS; Section 516 applied to settlement amounts",
        "statutory_total_income_rounding": "IMPLEMENTED; accepted residual convention applies to ordinary income while preserving dividend and special-rate buckets; negative residual fails closed",
        "authorization": "NO-GO",
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
