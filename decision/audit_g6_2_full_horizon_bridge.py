"""Independent G6.2 full-horizon arithmetic and fail-closed audit."""
from __future__ import annotations

import copy
import hashlib
import json
from calendar import monthrange
from datetime import date
from decimal import Decimal, ROUND_DOWN, localcontext
from pathlib import Path
from typing import Any

from g3_goal_hurdle import DEFAULT_SCHEDULE_PATH, CONTRACT_PATH, read_schedule, validate_schedule_contract
from g6_2_full_horizon_bridge import (
    DEFAULT_FIXTURE, DEFAULT_OUTPUT, FIXTURE_LABEL, _validate_fixture,
    load_fixture, load_fixture_text, run_fixture, run_scenario,
)

ROOT=Path(__file__).resolve().parents[1]
AUDIT_OUTPUT=ROOT/"research/stage512/2026-11-05/g6_2/audit.json"
D=Decimal
ZERO=D("0")
TOL=D("0.0000000001")


def _month_end(base_month: str, offset: int) -> date:
    year,month=(int(part) for part in base_month.split("-"))
    absolute=year*12+month-1+offset
    out_year,month0=divmod(absolute,12)
    out_month=month0+1
    return date(out_year,out_month,monthrange(out_year,out_month)[1])


def independent_tax_year(event_date: date) -> str:
    """Independently map a date to an Indian FY without the ledger helper."""
    start_year=event_date.year if event_date.month>=4 else event_date.year-1
    return f"{start_year}-{str(start_year+1)[-2:]}"


def _section516_round(value: Decimal) -> Decimal:
    whole=value.to_integral_value(rounding=ROUND_DOWN)
    lower=(whole//D("10"))*D("10")
    return lower+(D("10") if whole-lower>=D("5") else ZERO)


def independent_ordinary_tax(income: Decimal) -> Decimal:
    """Independent fixture slab/cess formula; fail outside the supported band."""
    rounded=_section516_round(income)
    if not D("1200000")<rounded<=D("5000000"):
        raise ValueError("G6.2 independent tax audit only supports ordinary income above rebate and at/below surcharge thresholds")
    slabs=((D("400000"),D("0")),(D("800000"),D("0.05")),(D("1200000"),D("0.10")),
           (D("1600000"),D("0.15")),(D("2000000"),D("0.20")),(D("2400000"),D("0.25")),(None,D("0.30")))
    tax=ZERO; lower=ZERO
    for upper,rate in slabs:
        end=rounded if upper is None else min(rounded,upper)
        if end>lower: tax+=(end-lower)*rate
        if upper is None or rounded<=upper: break
        lower=upper
    return tax*D("1.04")


def independent_expected(raw: dict[str,Any],horizon: int,scenario: dict[str,Any])->dict[str,Any]:
    with localcontext() as ctx:
        ctx.prec=50
        schedule=read_schedule(DEFAULT_SCHEDULE_PATH)
        contract=json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        validate_schedule_contract(schedule,contract)
        fee=D(raw["costs"]["account_fee_per_contribution_inr"])
        exit_fee=D(raw["costs"]["terminal_transaction_cost_inr"])
        growth=D(scenario["monthly_mark_growth_rate"])
        starting=D(raw["starting_mark_inr"])
        total_contributions=schedule.cumulative_contributions[horizon]
        expected_lots=[]
        total_units=ZERO; basis=ZERO; proceeds=ZERO
        for month in range(horizon+1):
            contribution=schedule.initial_inr if month==0 else schedule.monthly_contributions[month]
            if contribution==ZERO: continue
            principal=contribution-fee
            mark=starting*(D("1")+growth)**month
            terminal=starting*(D("1")+growth)**horizon
            units=principal/mark
            sale=units*terminal
            gain=sale-principal
            acquired=_month_end(schedule.base_month,month)
            lot_id=f"{scenario['scenario_id']}-h{horizon}-lot-{month:03d}"
            disposed=_month_end(schedule.base_month,horizon)
            expected_lots.append({
                "lot_id":lot_id,"acquired_date":acquired.isoformat(),
                "disposed_date":disposed.isoformat(),
                "acquired_tax_year":independent_tax_year(acquired),
                "disposal_tax_year":independent_tax_year(disposed),
                "units_disposed":str(units),"unit_price_inr":str(terminal),
                "proceeds_inr":str(sale),"tax_basis_removed_inr":str(principal),
                "deductible_transfer_expenses_inr":"0","signed_realized_result_inr":str(gain),
            })
            total_units+=units; basis+=principal; proceeds+=sale
        gains=proceeds-basis
        external=D(raw["tax_assumptions"]["external_ordinary_income_by_tax_year"][
            independent_tax_year(_month_end(schedule.base_month,horizon))])
        external_tax=independent_ordinary_tax(external)
        combined_tax=independent_ordinary_tax(external+gains)
        incremental=combined_tax-external_tax
        recorded_fees=fee*D(len(expected_lots))+exit_fee
        cpi_factor=(D("1")+D(raw["cpi"]["annual_inflation_fraction"]))**(D(horizon)/D("12"))
        # Account fees are removed before unit acquisition; subtract them from
        # the cashflow only once. Terminal sale cost is charged at disposal.
        pre_tax_after_exit_fee=proceeds-exit_fee
        net_nominal=pre_tax_after_exit_fee-incremental
        return {
            "contributions_inr":str(total_contributions),"lot_count":len(expected_lots),
            "units_at_exit":str(total_units),"basis_inr":str(basis),"gross_sale_proceeds_inr":str(proceeds),
            "recorded_costs_inr":str(recorded_fees),"gross_after_recorded_costs_inr":str(pre_tax_after_exit_fee),"taxable_gain_inr":str(gains),
            "external_tax_before_credits_inr":str(external_tax),"combined_tax_before_credits_inr":str(combined_tax),
            "incremental_fixture_tax_inr":str(incremental),"net_nominal_inr":str(net_nominal),
            "cpi_factor":str(cpi_factor),"net_real_inr":str(net_nominal/cpi_factor),
            "lot_disposal_trace":expected_lots,
        }


def audit()->dict[str,Any]:
    raw=load_fixture()
    schedule,_,years=_validate_fixture(raw)
    assert raw["input_classification"]==FIXTURE_LABEL
    independent_years=sorted({independent_tax_year(_month_end(schedule.base_month,month)) for month in range(123)})
    assert years==independent_years==[f"{year}-{str(year+1)[-2:]}" for year in range(2026,2037)]
    assert independent_tax_year(date(2027,3,31))=="2026-27"
    assert independent_tax_year(date(2027,4,1))=="2027-28"
    actual=run_fixture()
    assert actual["source_hashes"]["capital_loss_schedule_code"]["path"]=="decision/capital_gain_loss_schedule.py"
    assert actual["source_hashes"]["capital_loss_schedule_code"]["sha256"]==hashlib.sha256((ROOT/"decision/capital_gain_loss_schedule.py").read_bytes()).hexdigest()
    assert len(actual["scenarios"])==4
    committed=json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8"))
    assert actual==committed
    formula_results={}
    expected_totals={120:D("8981227.380300000"),122:D("9110914.503305000")}
    for row in actual["scenarios"]:
        horizon=row["horizon_months"]
        scenario=next(item for item in raw["scenarios"] if item["scenario_id"]==row["scenario_id"])
        expected=independent_expected(raw,horizon,scenario)
        formula_results[f"{horizon}:{row['scenario_id']}"]=expected
        assert D(row["contributions_inr"])==expected_totals[horizon]==D(expected["contributions_inr"])
        mappings={
            "gross_terminal_sale_proceeds_before_terminal_cost_and_tax_inr":"gross_sale_proceeds_inr",
            "gross_terminal_wealth_after_recorded_costs_before_tax_inr":"gross_after_recorded_costs_inr",
            "recorded_account_fees_inr":"recorded_costs_inr",
            "incremental_fixture_tax_inr":"incremental_fixture_tax_inr",
            "net_nominal_after_costs_and_incremental_fixture_tax_inr":"net_nominal_inr",
            "net_real_2026_base_fixture_value_inr":"net_real_inr",
        }
        for key,want in mappings.items():
            actual_value=D(row[key])
            expected_value=D(expected[want])
            if key=="gross_terminal_wealth_after_recorded_costs_before_tax_inr":
                expected_value=D(expected["gross_sale_proceeds_inr"])-D(raw["costs"]["terminal_transaction_cost_inr"])
            elif key=="recorded_account_fees_inr":
                expected_value=D(raw["costs"]["account_fee_per_contribution_inr"])*D(expected["lot_count"])
            assert abs(actual_value-expected_value)<=TOL,(horizon,row["scenario_id"],key,actual_value,expected_value)
        assert D(row["recorded_transaction_costs_inr"])==D(raw["costs"]["terminal_transaction_cost_inr"])
        assert abs(D(row["reconciliation_residual_inr"]))<=D("0.000000000001")
        assert row["event_count"]==4*expected["lot_count"]
        assert row["lot_count_including_initial"]==expected["lot_count"]==horizon+1
        assert row["monthly_contribution_count"]==horizon
        assert row["terminal_date"]==_month_end(schedule.base_month,horizon).isoformat()
        assert row["modeled_tax_years"]==years and row["tax_year_count"]==11
        actual_lots={lot["lot_id"]:lot for lot in row["lot_disposal_trace"]}
        expected_lots={lot["lot_id"]:lot for lot in expected["lot_disposal_trace"]}
        assert set(actual_lots)==set(expected_lots) and len(actual_lots)==horizon+1
        for lot_id,want in expected_lots.items():
            got=actual_lots[lot_id]
            for field in ("acquired_date","disposed_date","acquired_tax_year","disposal_tax_year"):
                assert got[field]==want[field],(horizon,lot_id,field)
            for field in ("units_disposed","unit_price_inr","proceeds_inr","tax_basis_removed_inr","deductible_transfer_expenses_inr","signed_realized_result_inr"):
                assert abs(D(got[field])-D(want[field]))<=TOL,(horizon,lot_id,field)
        exit_year=independent_tax_year(_month_end(schedule.base_month,horizon))
        assert list(row["tax_year_trace"])==years
        for event in row["tax_event_trace"]:
            assert event["tax_year"]==independent_tax_year(date.fromisoformat(event["event_date"]))
        for year in years:
            tax=row["tax_year_trace"][year]
            income=D(raw["tax_assumptions"]["external_ordinary_income_by_tax_year"][year])
            baseline=independent_ordinary_tax(income)
            expected_incr=expected["incremental_fixture_tax_inr"] if year==exit_year else "0"
            assert abs(D(tax["external_only_tax_before_credits"])-baseline)<=TOL
            assert abs(D(tax["incremental_portfolio_tax"])-D(expected_incr))<=TOL
            assert abs(D(tax["total_tax_before_credits"])-(baseline+D(expected_incr)))<=TOL
        expected_tax_lots={lot["lot_id"]:lot for lot in expected["lot_disposal_trace"] if D(lot["signed_realized_result_inr"])>TOL}
        all_trace_lots={entry["lot_id"]:entry for entry in row["tax_event_trace"] if "realized_disposal" in entry}
        trace_lots={lot_id:entry for lot_id,entry in all_trace_lots.items() if abs(D(entry["taxable_amount_inr"]))>TOL}
        assert set(trace_lots)==set(expected_tax_lots)
        assert all(abs(D(entry["taxable_amount_inr"]))<=TOL for lot_id,entry in all_trace_lots.items() if lot_id not in expected_tax_lots)
        traced_taxable_gain=sum((D(entry["taxable_amount_inr"]) for entry in trace_lots.values()),ZERO)
        assert abs(traced_taxable_gain-D(expected["taxable_gain_inr"]))<=TOL
        for lot_id,lot in expected_tax_lots.items():
            event=trace_lots[lot_id]
            assert event["tax_year"]==exit_year and event["tax_category"]=="ordinary" and event["tax_classification"]=="section76"
            assert abs(D(event["taxable_amount_inr"])-D(lot["signed_realized_result_inr"]))<=TOL
        assert row["investment_authorization"]=="NO_GO"
    # Fail-closed mutation cases.
    failures={}
    def rejected(label:str, mutate, stage="validate"):
        bad=copy.deepcopy(raw); mutate(bad)
        try:
            if stage=="load": load_fixture_text(json.dumps(bad))
            elif stage=="scenario": run_scenario(bad,120,bad["scenarios"][0])
            else: _validate_fixture(bad)
        except (ValueError,KeyError): failures[label]="PASS"
        else: raise AssertionError(f"mutation unexpectedly passed: {label}")
    rejected("actual_data_label_rejected",lambda x:x.__setitem__("input_classification","ACTUAL_MARKET_DATA"),"load")
    rejected("direct_scenario_rejects_actual_label",lambda x:x.__setitem__("input_classification","ACTUAL_MARKET_DATA"),"scenario")
    rejected("direct_scenario_rejects_nonsynthetic_price_basis",lambda x:x.__setitem__("price_path_basis","Official sourced returns"),"scenario")
    rejected("unsupported_121_month_horizon_rejected",lambda x:x.__setitem__("horizons_months",[120,121]),"load")
    rejected("missing_tax_year_input_rejected",lambda x:x["tax_assumptions"]["external_ordinary_income_by_tax_year"].pop("2036-37"))
    rejected("extra_tax_year_input_rejected",lambda x:x["tax_assumptions"]["external_ordinary_income_by_tax_year"].__setitem__("2037-38","1500000"))
    rejected("missing_residency_rejected",lambda x:x["tax_assumptions"].pop("resident_individual"))
    rejected("nonresident_rejected",lambda x:x["tax_assumptions"].__setitem__("resident_individual",False))
    rejected("future_law_promotion_rejected",lambda x:x["tax_assumptions"].__setitem__("rule_set","2036 statutory tax law"))
    rejected("wrong_cpi_base_month_rejected",lambda x:x["cpi"].__setitem__("base_month","2026-11"))
    rejected("negative_100pct_inflation_rejected",lambda x:x["cpi"].__setitem__("annual_inflation_fraction","-1"))
    rejected("missing_scenario_growth_rejected",lambda x:x["scenarios"][0].pop("monthly_mark_growth_rate"))
    downside=copy.deepcopy(raw["scenarios"][0]); downside["scenario_id"]="declining-loss-path"; downside["monthly_mark_growth_rate"]="-0.01"
    try: run_scenario(raw,120,downside)
    except ValueError as error:
        assert ("realized losses require" in str(error) or "eligible capital losses remain" in str(error)); failures["unallocated_loss_path_blocks_result"]="PASS"
    else: raise AssertionError("loss path unexpectedly produced a result")
    report={
        "audit":"PASS","record_id":"g6-2-independent-full-horizon-audit-v1",
        "scope":"120/122-month synthetic full liquidation; four horizon/path runs; eleven modeled FYs; no market or personal data",
        "scenario_count":4,"modeled_tax_years":years,
        "source_manifest_includes_loss_schedule": bool(
            run_fixture()["source_hashes"].get("capital_loss_schedule_code",{}).get("path")=="decision/capital_gain_loss_schedule.py"
        ),
        "independent_cashflow_unit_cost_cpi_reconciliation":"PASS",
        "independent_tax_year_mapping_and_boundaries":"PASS",
        "independent_fixture_tax_slab_cess_reconciliation":"PASS; fixture arithmetic only, not tax-law forecast",
        "complete_per_lot_and_tax_year_trace_reconciliation":"PASS",
        "cash_ledger_residuals_within_1e_12_inr":all(abs(D(row["reconciliation_residual_inr"]))<=D("0.000000000001") for row in actual["scenarios"]),
        "mutation_cases":failures,"decision_grade_g6":"NOT_READY","investment_authorization":"NO_GO",
        "audit_code_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "result_sha256":hashlib.sha256(DEFAULT_OUTPUT.read_bytes()).hexdigest(),
        "independent_results":formula_results,
    }
    AUDIT_OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    AUDIT_OUTPUT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8",newline="\n")
    return report


if __name__=="__main__":
    print(json.dumps(audit(),indent=2,ensure_ascii=False))


