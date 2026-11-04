"""G5.1 audit: trace the former 11.8% replay label and preserve its correction lineage."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "research/stage512/2026-11-05/g5_1_118_claim_lineage_v1.json"
RERUN_DIR = ROOT / "research/stage512/2026-11-05/g5_1_118_assumption_rerun"
OLD_LABEL = "Historical 11.8% " + "replay"
NEW_LABEL = "Synthetic 11.8% equity geometric-return assumption"
BASE_COMMIT = "765b4c84cc006c98dd374b49b9dd324f82187123"
PRE_CORRECTION_HASHES = {
    "research/stage512/2026-11-02/stage512_assumption_register.json": "e5d1af01137b14d7a17336af89cee8f6b5c3e1490e4cd9b5c619e512116c6c47",
    "research/stage512/2026-11-02/stage512_risk_audit.py": "99e624f1b093bc7cf81f297c922b092534ca860a3731534d2beeb5b4994b50e2",
    "research/stage512/2026-11-02/stage512_risk_scenarios.csv": "4c642f6b691138fd9836162a42f96288bab5e518c5586fccef7fad30ec8cc243",
    "research/stage512/2026-11-02/stage512_blocker_resolution_report.md": "6378d289762355472353f145b9f89180ebc7901acbd58f7728fd334f8ba5e483",
}
NSE_SERIES = "research/stage512/data/nse500_official_tri_monthly_2015_2025q3_R8.csv"
NSE_VALIDATION = "research/stage512/data/nse500_tri_validation_R8.json"


def _normalized_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def _sha256(path: Path) -> str:
    return hashlib.sha256(_normalized_bytes(path)).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def audit() -> dict[str, Any]:
    assumption_path = ROOT / "research/stage512/2026-11-02/stage512_assumption_register.json"
    model_path = ROOT / "research/stage512/2026-11-02/stage512_risk_audit.py"
    result_path = ROOT / "research/stage512/2026-11-02/stage512_risk_scenarios.csv"
    report_path = ROOT / "research/stage512/2026-11-02/stage512_blocker_resolution_report.md"
    assumption = _json(assumption_path)
    model = model_path.read_text(encoding="utf-8")
    results = _rows(result_path)
    rerun_results = _rows(RERUN_DIR / "stage512_risk_scenarios.csv")
    rerun_assumption = _json(RERUN_DIR / "stage512_assumption_register.json")

    synthetic = [row for row in assumption["models"] if row["scenario"] == NEW_LABEL]
    _require(len(synthetic) == 1, "current assumption register must contain one corrected scenario")
    _require(synthetic[0]["equity_return_geometric_assumed"] == 0.118,
             "corrected scenario must retain the original 0.118 parameter value")
    _require(synthetic[0]["scenario_classification"] == "SYNTHETIC_ASSUMPTION_NOT_HISTORICAL_REPLAY"
             and synthetic[0]["equity_return_provenance_status"] ==
             "UNVERIFIED_THIRD_PARTY_REPORTED_CAGR_USED_AS_SYNTHETIC_ASSUMPTION",
             "corrected assumption register must label the scenario and input provenance explicitly")
    _require(assumption["model_run_type"] == "SYNTHETIC_ASSUMPTION_SCENARIOS_ONLY_NO_HISTORICAL_REPLAY",
             "model register does not explicitly state its generated-path type")

    _require(OLD_LABEL not in model and NEW_LABEL in model,
             "future model runs must not emit the former replay label")
    _require("--output-dir" in model and "required=True" in model,
             "reruns must require a separate output directory and avoid overwriting preserved artifacts")
    _require("rng.standard_normal((N,MONTHS,5)" in model and "equity_geo':.118" in model,
             "synthetic RNG and fixed geometric-return parameter are not visible in the model source")
    _require("read_csv(" not in model and "np.load(" not in model and "np.loadtxt(" not in model,
             "model unexpectedly reads an observed return path")

    current_synthetic = [row for row in results if row["scenario"] == NEW_LABEL]
    rerun_synthetic = [row for row in rerun_results if row["scenario"] == NEW_LABEL]
    _require(len(current_synthetic) == len(rerun_synthetic) == 6,
             "corrected result must contain the three portfolios at both 120 and 122 months")
    numeric_columns = [key for key in rerun_synthetic[0] if key not in {
        "scenario", "scenario_classification", "equity_return_provenance_status"
    }]
    current_index = {(row["portfolio"], row["month"]): row for row in current_synthetic}
    rerun_index = {(row["portfolio"], row["month"]): row for row in rerun_synthetic}
    _require(set(current_index) == set(rerun_index), "corrected scenario output cases do not match the rerun")
    exact_numeric_match = all(
        current_index[key][column] == rerun_index[key][column]
        for key in current_index for column in numeric_columns
    )
    _require(exact_numeric_match, "corrected scenario values differ from the independent seeded rerun")
    _require(all(row["scenario_classification"] == "SYNTHETIC_ASSUMPTION_NOT_HISTORICAL_REPLAY"
                 and row["equity_return_provenance_status"] ==
                 "UNVERIFIED_THIRD_PARTY_REPORTED_CAGR_USED_AS_SYNTHETIC_ASSUMPTION"
                 for row in current_synthetic), "corrected scenario rows lack quarantine provenance fields")

    official_rows = _rows(ROOT / NSE_SERIES)
    validation = _json(ROOT / NSE_VALIDATION)
    _require(len(official_rows) == 129 and official_rows[0]["month"] == "2015-01"
             and official_rows[-1]["month"] == "2025-09",
             "official NSE monthly-anchor evidence no longer has the documented 129-month coverage")
    _require(validation["complete_official_NSE_daily_history_qualified"] is False
             and validation["full_2036_probability_qualified"] is False
             and validation["verified_months"] == 129,
             "NSE evidence must not be represented as a full since-1995 return path or probability qualification")
    report_text = report_path.read_text(encoding="utf-8")
    _require("G5.1 correction" in report_text and "quarantined from investment-decision evidence" in report_text,
             "the historical report lacks an explicit visible correction notice")
    index_text = (ROOT / "research/stage512/2026-11-02/README.md").read_text(encoding="utf-8")
    _require("G5.1 evidence correction" in index_text and "2026-11-05/g5_1_118_claim_lineage_v1.json" in index_text,
             "research archive index does not route readers to the correction record")

    old_output_rows = 6
    evidence_hashes = {
        path: _sha256(ROOT / path) for path in [
            "research/stage512/2026-11-02/stage512_assumption_register.json",
            "research/stage512/2026-11-02/stage512_risk_audit.py",
            "research/stage512/2026-11-02/stage512_risk_scenarios.csv",
            "research/stage512/2026-11-02/stage512_blocker_resolution_report.md",
            "research/stage512/2026-11-02/README.md",
            NSE_SERIES,
            NSE_VALIDATION,
            "research/stage512/2026-11-05/g5_1_118_assumption_rerun/stage512_assumption_register.json",
            "research/stage512/2026-11-05/g5_1_118_assumption_rerun/stage512_risk_scenarios.csv",
        ]
    }
    return {
        "schema_version": 1,
        "record_id": "g5-1-118-claim-lineage-2026-11-05-v1",
        "as_of": "2026-11-05",
        "base_main_commit_before_correction": BASE_COMMIT,
        "claim": {
            "former_label": OLD_LABEL,
            "corrected_label": NEW_LABEL,
            "classification": "SYNTHETIC_ASSUMPTION_MISLABELED_AS_HISTORICAL_REPLAY",
            "equity_geometric_return_fraction": "0.118",
            "current_input_provenance": "UNVERIFIED_THIRD_PARTY_REPORTED_CAGR",
            "forecast_status": "NOT_A_FORECAST",
            "decision_evidence_status": "QUARANTINED_NOT_FOR_INVESTMENT_DECISION",
        },
        "method_trace": {
            "model_path": "research/stage512/2026-11-02/stage512_risk_audit.py",
            "scenario_paths": 25000,
            "monthly_steps": 122,
            "seed": 20261102,
            "equity_parameter_use": "The scalar 0.118 is inserted as the assumed geometric equity return; simulated monthly shocks are generated from a seeded normal distribution.",
            "observed_historical_path_loaded": False,
            "portfolio_results_rebalanced_from_observed_holdings": False,
        },
        "official_and_reported_source_assessment": {
            "original_report_source": "https://tipsheet.markets/indices/nifty-500/",
            "original_source_snapshot_hash": None,
            "original_report_value_status": "UNVERIFIED; exact source version and 30 October 2026 endpoint were not archived.",
            "live_third_party_page_as_of_2026_11_03": "11.9% annualized since 1995; live value is not an as-of-2026-11-02 snapshot.",
            "official_nifty_indices_whitepaper": "https://www.niftyindices.com/docs/default-source/indices/nifty-500/nifty-500-whitepaper_2025.pdf",
            "official_reported_tri_return": "12.39% annualized from 1995-01-01 through 2025-09-30",
            "official_repo_series_coverage": "129 published monthly TRI anchors from 2015-01 through 2025-09; no complete official daily since-1995 path is qualified in this repository.",
            "comparison_limit": "Different end dates prevent treating the third-party 11.8% claim and official 12.39% report as like-for-like or as proof of the exact 0.118 input.",
        },
        "affected_artifacts": [
            {"path": "research/stage512/2026-11-02/stage512_assumption_register.json", "impact": "scenario assumption name and provenance status corrected; numeric input remains 0.118"},
            {"path": "research/stage512/2026-11-02/stage512_risk_audit.py", "impact": "future runs use corrected label, require a new output directory, and emit provenance metadata"},
            {"path": "research/stage512/2026-11-02/stage512_risk_scenarios.csv", "impact": "six affected scenario rows relabeled and tagged; numeric results unchanged"},
            {"path": "research/stage512/2026-11-02/stage512_blocker_resolution_report.md", "impact": "visible correction notice and corrected source/interpretation text; numeric table values retained"},
        ],
        "reproduction": {
            "command": "python research/stage512/2026-11-02/stage512_risk_audit.py --output-dir research/stage512/2026-11-05/g5_1_118_assumption_rerun",
            "corrected_scenario_rows": 6,
            "exact_numeric_reproduction_against_saved_output": exact_numeric_match,
            "pre_correction_source_hashes": PRE_CORRECTION_HASHES,
        },
        "current_source_hashes_sha256_utf8_lf": evidence_hashes,
        "qcsae_record": "research/stage512/2026-11-05/g5_1_qcsae_v1.json",
        "g5_1_disposition": "PASS_FOR_LINEAGE_AND_LABEL_CORRECTION; INPUT_VALUE_REMAINS_UNVERIFIED; ALL_SCENARIO_OUTPUTS_REMAIN_RESEARCH_ONLY",
        "investment_authorization": "NO_GO",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(audit(), indent=2, ensure_ascii=False) + "\n"
    if args.check:
        _require(RECORD.read_text(encoding="utf-8") == rendered,
                 "committed G5.1 lineage record differs from regenerated audit output")
        print("G5.1 claim-lineage evidence matches the independently regenerated audit")
    elif args.write:
        RECORD.parent.mkdir(parents=True, exist_ok=True)
        RECORD.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"Wrote {RECORD.relative_to(ROOT)}")
    else:
        print(rendered, end="")
