"""Audit monthly return endpoints and candidate inclusion using retained G6.3 evidence."""
from __future__ import annotations

import argparse
import json
from datetime import date, datetime
from decimal import Decimal
from itertools import combinations
from pathlib import Path

from audit_g6_3_sbi_gilt_valuation import OUTPUT as SBI_VALUATION
from audit_g6_3_silver_nav_comparison import OUT as SILVER_COMPARISON, month_endpoints
from audit_g6_3_source_inventory import (
    G5_DISPOSITION, NAV_DIR, NSE_TRI, R9_DIR, ROOT, audit_g5_sources, audit_r9,
    read_json, require, rows, sha256,
)
from g3_goal_hurdle import normalized_text_and_sha256


EVIDENCE = ROOT / "research/g6_3/2026-11-27-exact-date-coverage"
OUT = EVIDENCE / "coverage_v1.json"
GOLD_DIR = ROOT / "research/stage512/2026-11-06/hdfcgold_execution_evidence"
CUTOFF = date(2026, 10, 30)
MOTILAL = "MOTILAL_NIFTY500_INDEX_FUND"
SBI_EQUITY = "SBI_NIFTY500_INDEX_FUND"
LIC = "LIC_GSEC_8_13_ETF"
SBI_GILT = "SBI_GILT_JUNE2036_FUND"
GOLD = "HDFC_GOLD_ETF"
SILVER = "ICICI_SILVER_ETF"
GOLD_CLOSE = "HDFCGOLD_NSE_CLOSE"
TRI = "NIFTY500_TRI_BENCHMARK"
DIRECT = "GOI_DIRECT_DATED_GSEC_694_2036"
TBILL = "CASH_HOLD_91D_TBILL_ROLLING"
INCLUSION = {
    MOTILAL: ("PRODUCT_NAV_REPLAY", "Primary broad-equity product history for the matched historical exercises."),
    SBI_EQUITY: ("SHORT_HISTORY_SUBSTITUTION_ONLY", "Shorter alternative for the equity sleeve. Compare with Motilal as a substitution."),
    LIC: ("FUND_NAV_PROXY_REPLAY", "Duration exposure via the fund NAV. ETF execution and direct sovereign returns need separate evidence."),
    SBI_GILT: ("PRODUCT_NAV_REPLAY_AND_CONDITIONAL_CASHFLOWS", "Use the same historical NAV for both forward accrued-interest cases."),
    GOLD: ("PRODUCT_NAV_REPLAY_AND_CLOSE_DIAGNOSTIC", "Use the unit-rebased NAV for product replay. Keep the NSE close history separate."),
    SILVER: ("NAV_SENSITIVITY_ONLY", "Use observed AMFI NAV for the gold-to-silver sensitivity. Full traded history is deferred."),
    "MOTILAL_NIFTY500_ETF": ("ALTERNATIVE_HISTORY_UNQUALIFIED", "Duplicate equity exposure. The dated traded return path has not qualified."),
    "ICICI_GOLD_ETF": ("ALTERNATIVE_HISTORY_UNQUALIFIED", "Gold alternative. Dated holdings alone yield no qualified return path."),
    "SBI_NIFTY10Y_GSEC_ETF": ("ALTERNATIVE_HISTORY_UNQUALIFIED", "Gilt alternative. Dated holdings alone yield no qualified return path."),
    "SBI_GILT_FUND": ("ALTERNATIVE_HISTORY_UNQUALIFIED", "Active-duration alternative. No qualified product path for this comparison."),
    DIRECT: ("CONDITIONAL_CASHFLOWS_ONLY", "Use verified nominal cashflows and explicit clean-price scenarios. Live quote is deferred."),
    "GOI_DIRECT_DATED_GSEC_718_2033": ("CASHFLOW_AND_REINVESTMENT_BLOCKED", "Requires an independently qualified cashflow and 2033-to-2036 rollover path."),
    TBILL: ("AUCTION_AND_ROLLOVER_SENSITIVITY_ONLY", "Auction quotes and conditional cohorts support mechanics tests. Payment timing stays open."),
    TRI: ("BENCHMARK_DIAGNOSTIC_ONLY", "Official rounded monthly TRI returns with secondary mirror endpoint dates. No product or execution path."),
}


def load_marks(path, date_field, value_field, date_parser=date.fromisoformat, expected=None):
    observations = {}
    identity_fields = (expected or {}).items()
    for row in rows(path):
        day = date_parser(row[date_field])
        value = Decimal(row[value_field])
        require(day not in observations and value.is_finite() and value > 0, f"invalid dated mark in {path.name}: {day}")
        require(all(row[key] in accepted for key, accepted in identity_fields),
                f"source identity differs in {path.name}: {day}")
        observations[day] = value
    require(len(observations) >= 2, f"insufficient source rows in {path.name}")
    return observations


def provenance(path):
    return {"path": path.relative_to(ROOT).as_posix(), "sha256_normalized": normalized_text_and_sha256(path)[1]}


def date_summary(intervals):
    bands = []
    for start, end in intervals:
        a, b = start.isoformat(), end.isoformat()
        if bands and bands[-1]["end"] == a:
            bands[-1]["end"] = b
            bands[-1]["intervals"] += 1
        else:
            bands.append({"start": a, "end": b, "intervals": 1})
    return {"intervals": len(intervals), "longest_contiguous_intervals": max(
        (band["intervals"] for band in bands), default=0), "contiguous_bands": bands}


def adjacent_pairs(endpoints):
    months = sorted(endpoints)
    return [(endpoints[a], endpoints[b]) for a, b in zip(months, months[1:])
            if b[0] * 12 + b[1] - a[0] * 12 - a[1] == 1]


def coverage(ids, observations):
    dated = [set(observations[cid]) for cid in ids]
    month_ends = [month_endpoints(days) for days in dated]
    months = sorted(set.intersection(*(set(series) for series in month_ends)))
    same_labels = {month: month_ends[0][month] for month in months}
    strict = {month: day for month, day in same_labels.items() if all(series[month] == day for series in month_ends)}
    common = month_endpoints(set.intersection(*dated))
    shifted = [{"joint_date": day.isoformat(),
                "later_individual_dates": {cid: series[month].isoformat()
                                           for cid, series in zip(ids, month_ends) if series[month] != day}}
               for month, day in sorted(common.items()) if any(series[month] != day for series in month_ends)]
    strict_pairs, joint_pairs = adjacent_pairs(strict), adjacent_pairs(common)
    require(set(strict_pairs) <= set(joint_pairs), "strict return intervals must also be common-date intervals")
    require(all(start in days and end in days for start, end in joint_pairs for days in dated),
            "joined interval has a missing observed endpoint")
    return {
        "series": list(ids),
        "shared_month_labels_for_adjacent_intervals": len(adjacent_pairs(same_labels)),
        "independent_last_dates_equal": date_summary(strict_pairs),
        "latest_common_observed_dates": date_summary(joint_pairs),
        "unmatched_months": [f"{y:04d}-{m:02d}" for y, m in months if (y, m) not in common],
        "common_dates_earlier_than_individual_last": shifted,
    }, common


def load_benchmark_dates():
    dates_file = NSE_TRI.with_name("nse500_tri_month_end_dates_R9.csv")
    r8_file = NSE_TRI.with_name("nse500_tri_validation_R8.json")
    r9_file = NSE_TRI.with_name("r9_nse_gsec_129m_source_bridge.json")
    validation, bridge = read_json(r8_file), read_json(r9_file)
    require(validation["status"] == "PASS_129_OFFICIAL_MONTHLY_ANCHORS"
            and not validation["complete_official_NSE_daily_history_qualified"], "benchmark source status differs")
    require(provenance(NSE_TRI)["sha256_normalized"] == validation["official_table_sha256"]
            and provenance(dates_file)["sha256_normalized"] == bridge["month_end_source_sha256"]
            and provenance(r8_file)["sha256_normalized"] == bridge["official_nse_129m_anchor_validation_sha256"],
            "benchmark return, validation or mirror date hash differs")
    official = rows(NSE_TRI)
    require(len(official) == 129 and all(row["source_status"] == "OFFICIAL_NSE_WHITEPAPER" for row in official),
            "benchmark published return window changed")
    dates = {}
    for row in rows(dates_file):
        day = date.fromisoformat(row["last_nifty500_tri_daily_mirror_date"])
        month = day.strftime("%Y-%m")
        require(month == row["month"] and month not in dates
                and row["git_blob_sha1"] == validation["mirror_git_blob_sha1_expected"],
                f"invalid benchmark mirror date: {day}")
        dates[month] = day
    require(sorted(dates)[1:] == [row["month"] for row in official]
            and len(adjacent_pairs(month_endpoints(dates.values()))) == 129, "benchmark endpoints do not support the official months")
    return set(dates.values()), bridge, [provenance(path) for path in (NSE_TRI, dates_file, r8_file, r9_file)]


def build():
    g5, _ = audit_g5_sources()
    lic, _ = audit_r9()
    observations, sources = {}, {}
    for item in g5["independently_reconciled_histories"]:
        cid, code = item["candidate_id"], item["scheme_code"]
        path = NAV_DIR / f"nav_{code}_daily.csv"
        field = "nav"
        if cid == GOLD:
            adjustment = read_json(GOLD_DIR / "nav_113049_unit_rebase_audit_v1.json")
            path = GOLD_DIR / adjustment["output"]["filename"]
            require(sha256(path.read_bytes()).upper() == adjustment["output"]["sha256"]
                    and item["normalized_csv_sha256"].upper() == adjustment["input"]["sha256"],
                    "HDFC Gold rebase provenance differs")
            field = "nav_current_1_rupee_face_value_basis"
        data = load_marks(path, "date", field, expected={"scheme_code": {code}, "isin": {item["isin"]}})
        require(len(data) == item["observations"] and min(data).isoformat() == item["first"]
                and max(data).isoformat() == item["last"], f"AMFI dates changed for {cid}")
        observations[cid] = set(data)
        sources[cid] = {**provenance(path), "class": "AMFI_GROWTH_NAV", "value_field": field}

    lic_path = R9_DIR / "lic_gsec_133307_amfi_daily.csv"
    observations[LIC] = set(load_marks(lic_path, "date", "nav_inr"))
    require(len(observations[LIC]) == lic["observations"], "LIC NAV dates changed")
    sources[LIC] = {**provenance(lic_path), "class": "AMFI_FUND_NAV_PROXY", "value_field": "nav_inr"}

    exchange = read_json(GOLD_DIR / "hdfcgold_nse_amfi_bridge_v2.json")["source_capture"]
    exchange_path = GOLD_DIR / "hdfcgold_nse_5y.csv"
    require(sha256(exchange_path.read_bytes()).upper() == exchange["sha256"], "HDFC Gold NSE export hash differs")
    observations[GOLD_CLOSE] = set(load_marks(exchange_path, "Date  ", "Close Price  ",
                                             lambda text: datetime.strptime(text, "%d-%b-%Y").date(),
                                             {"Symbol  ": {"HDFCGOLD", "HDFCMFGETF"}, "Series  ": {"EQ"}}))
    sources[GOLD_CLOSE] = {**provenance(exchange_path), "class": "OFFICIAL_NSE_CLOSE_PRICE_ONLY",
                           "value_field": "Close Price  "}

    observations[TRI], old_bridge, tri_artifacts = load_benchmark_dates()
    sources[TRI] = {"class": "OFFICIAL_NSE_MONTHLY_TRI_WITH_SECONDARY_DATE_ANCHORS", "artifacts": tri_artifacts}
    for cid, days in observations.items():
        dates = {day for day in days if day <= CUTOFF}
        observations[cid] = dates
        sources[cid].update(observed_dates=len(dates), first=min(dates).isoformat(), last=max(dates).isoformat(),
                            adjacent_monthly_intervals=len(adjacent_pairs(month_endpoints(dates))))

    nav_ids = (MOTILAL, LIC, SBI_GILT, GOLD, SILVER, SBI_EQUITY)
    strategy_groups = {
        "lic_plus_gold": (MOTILAL, LIC, GOLD),
        "lic_plus_gold_silver": (MOTILAL, LIC, GOLD, SILVER),
        "sbi_plus_gold": (MOTILAL, SBI_GILT, GOLD),
        "sbi_plus_gold_silver": (MOTILAL, SBI_GILT, GOLD, SILVER),
        "sbi_with_equity_alternative": (MOTILAL, SBI_GILT, GOLD, SILVER, SBI_EQUITY),
    }
    nav_panels = {}
    for label, ids in strategy_groups.items():
        panel, dates = coverage(ids, observations)
        nav_panels[label] = {**panel, "latest_common_observed_endpoints": [day.isoformat() for day in sorted(dates.values())]}
    silver_alignment = read_json(SILVER_COMPARISON)["alignment"]["shared_endpoints"]
    require(nav_panels["sbi_plus_gold_silver"]["latest_common_observed_endpoints"] == silver_alignment,
            "SBI matched dates differ from the reproduced silver comparison")
    benchmark = {cid: coverage((TRI, cid), observations)[0] for cid in nav_ids}
    require(benchmark[LIC]["independent_last_dates_equal"]["intervals"] == old_bridge["strictly_date_aligned_months"],
            "strict NSE/LIC endpoint count differs from the retained R9 bridge")

    sbi = read_json(SBI_VALUATION)
    sbi_cases = sorted({row["market_value_basis"] for row in sbi["after_tax_comparison"]["ranges"]})
    require(sbi_cases == ["accrual_in_net_receivables", "market_value_includes_accrual"],
            "both SBI forward accrual cases are required")
    require((sbi["live_quote"], sbi["paid_silver_history"], sbi["rbi_tbill_payment_timing"],
             sbi["investment_authorization"]) == ("DEFERRED", "DEFERRED", "OPEN", "NO_GO"),
            "latest evidence exceptions or authorization differ")
    candidates = read_json(G5_DISPOSITION)["candidates"]
    require({row["candidate_id"] for row in candidates} == set(INCLUSION)
            and sum(bool(row["product_hypothesis"]) for row in candidates) == 10, "G5 screening coverage changed")
    inclusion = []
    for row in candidates:
        cid = row["candidate_id"]
        use, reason = INCLUSION[cid]
        included = {"candidate_id": cid, "identity": row["identity"],
                    "observed_series": [key for key in (cid, GOLD_CLOSE if cid == GOLD else None) if key in sources],
                    "research_use": use, "reason": reason, "executable_shortlist": False}
        if cid == SBI_GILT:
            included["forward_accrual_cases"] = sbi_cases
        inclusion.append(included)
    return {
        "status": "PASS_EXACT_DATE_COVERAGE_AND_RESEARCH_INCLUSION",
        "qualified_for_portfolio_probability": False,
        "coverage_cutoff": CUTOFF.isoformat(),
        "source_series": sources, "g5_candidate_register": provenance(G5_DISPOSITION),
        "sbi_accrual_evidence": provenance(SBI_VALUATION),
        "silver_alignment_control": provenance(SILVER_COMPARISON),
        "code": provenance(Path(__file__).resolve()),
        "candidate_inclusion": inclusion, "nav_replay_panels": nav_panels,
        "nav_pair_coverage": [coverage(ids, observations)[0] for ids in combinations(nav_ids, 2)],
        "benchmark_date_mirror_coverage": [*benchmark.values(), coverage((TRI, LIC, GOLD), observations)[0]],
        "exchange_close_date_diagnostics": [coverage(ids, observations)[0] for ids in
                                            ((GOLD, GOLD_CLOSE), (MOTILAL, LIC, GOLD_CLOSE),
                                             (MOTILAL, SBI_GILT, GOLD_CLOSE))],
        **{key: sbi[key] for key in ("live_quote", "paid_silver_history", "rbi_tbill_payment_timing",
                                    "investment_authorization")},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    payload = json.dumps(result, indent=2) + "\n"
    if args.check:
        require(OUT.read_text(encoding="utf-8") == payload, "exact-date coverage artifact differs")
    else:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(payload, encoding="utf-8", newline="\n")
    print(f"PASS: {len(result['source_series'])} series, {len(result['candidate_inclusion'])} inclusion rows. "
          "Research coverage only. NO_GO.")


if __name__ == "__main__":
    main()
