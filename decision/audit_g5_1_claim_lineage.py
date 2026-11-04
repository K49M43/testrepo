"""G5.1 audit: verify correction lineage against the pinned original and fresh rerun."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
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
QUARANTINE = "QUARANTINED_NOT_FOR_INVESTMENT_DECISION"
CORRECTION_PATH = "research/stage512/2026-11-05/g5_1_118_claim_lineage_v1.json"
TEXT_SUFFIXES = {".csv", ".json", ".md", ".py", ".txt", ".yml", ".yaml"}
OLD_CLAIM_RE = re.compile(r"historical\s+11\.8%\s+(?:equity\s+)?replay", re.IGNORECASE)
OLD_CLAIM_ALLOWLIST = {
    "research/stage512/2026-11-05/G5_1_118_CLAIM_LINEAGE.md",
    CORRECTION_PATH,
}


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


def _json_close(actual: Any, expected: Any, tolerance: float = 1e-12) -> bool:
    if isinstance(actual, dict) and isinstance(expected, dict):
        return actual.keys() == expected.keys() and all(
            _json_close(actual[key], expected[key], tolerance) for key in actual
        )
    if isinstance(actual, list) and isinstance(expected, list):
        return len(actual) == len(expected) and all(
            _json_close(left, right, tolerance) for left, right in zip(actual, expected)
        )
    if isinstance(actual, bool) or isinstance(expected, bool):
        return actual is expected
    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        return math.isclose(actual, expected, rel_tol=0.0, abs_tol=tolerance)
    return actual == expected


def _scenario_rows(rows: list[dict[str, str]], label: str) -> list[dict[str, str]]:
    return [row for row in rows if row["scenario"] == label]


def _compare_baseline_rows(baseline_rows, corrected_rows) -> bool:
    original = _scenario_rows(baseline_rows, OLD_LABEL)
    corrected = _scenario_rows(corrected_rows, NEW_LABEL)
    _require(len(original) == len(corrected) == 6,
             "pinned baseline and corrected output must each contain six affected cases")
    old_index = {(row["portfolio"], row["month"]): row for row in original}
    new_index = {(row["portfolio"], row["month"]): row for row in corrected}
    _require(set(old_index) == set(new_index), "corrected scenario cases differ from the pinned baseline")
    measures = [key for key in original[0] if key not in {"scenario", "portfolio", "month"}]
    _require(all(key in corrected[0] for key in measures), "corrected result omits baseline numeric columns")
    exact = all(old_index[key][column] == new_index[key][column]
                for key in old_index for column in measures)
    _require(exact, "corrected values differ from the pinned pre-correction output")
    return exact


def _repo_wide_claim_scan() -> list[str]:
    offenders = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        relative = path.relative_to(ROOT).as_posix()
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if OLD_CLAIM_RE.search(content) and relative not in OLD_CLAIM_ALLOWLIST:
            offenders.append(relative)
    return sorted(offenders)


def audit(baseline_dir: Path, reproduced_dir: Path) -> dict[str, Any]:
    assumption_rel = "research/stage512/2026-11-02/stage512_assumption_register.json"
    model_rel = "research/stage512/2026-11-02/stage512_risk_audit.py"
    result_rel = "research/stage512/2026-11-02/stage512_risk_scenarios.csv"
    report_rel = "research/stage512/2026-11-02/stage512_blocker_resolution_report.md"
    assumption_path = ROOT / assumption_rel
    model_path = ROOT / model_rel
    result_path = ROOT / result_rel
    assumption = _json(assumption_path)
    model = model_path.read_text(encoding="utf-8")
    results = _rows(result_path)
    rerun_results = _rows(RERUN_DIR / "stage512_risk_scenarios.csv")
    rerun_assumption = _json(RERUN_DIR / "stage512_assumption_register.json")

    baseline_paths = {path: baseline_dir / path for path in PRE_CORRECTION_HASHES}
    _require(all(path.is_file() for path in baseline_paths.values()),
             "all baseline files must be materialized from the pinned pre-correction commit")
    baseline_hashes = {key: _sha256(path) for key, path in baseline_paths.items()}
    _require(baseline_hashes == PRE_CORRECTION_HASHES,
             "materialized baseline files do not match the pinned pre-correction SHA-256 manifest")
    baseline_rows = _rows(baseline_paths[result_rel])
    baseline_numeric_preserved = _compare_baseline_rows(baseline_rows, results)

    synthetic = [row for row in assumption["models"] if row["scenario"] == NEW_LABEL]
    _require(len(synthetic) == 1, "current assumption register must contain one corrected scenario")
    _require(synthetic[0]["equity_return_geometric_assumed"] == 0.118,
             "corrected scenario must retain the original 0.118 parameter value")
    _require(synthetic[0]["scenario_classification"] == "SYNTHETIC_ASSUMPTION_NOT_HISTORICAL_REPLAY"
             and synthetic[0]["equity_return_provenance_status"] ==
             "UNVERIFIED_THIRD_PARTY_REPORTED_CAGR_USED_AS_SYNTHETIC_ASSUMPTION",
             "corrected assumption register must label the scenario and input provenance explicitly")
    _require(synthetic[0]["decision_evidence_status"] == QUARANTINE
             and synthetic[0]["claim_lineage_record"] == CORRECTION_PATH,
             "assumption register must carry explicit quarantine and correction-link fields")
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

    current_synthetic = _scenario_rows(results, NEW_LABEL)
    rerun_synthetic = _scenario_rows(rerun_results, NEW_LABEL)
    _require(len(current_synthetic) == len(rerun_synthetic) == 6,
             "corrected result must contain the three portfolios at both 120 and 122 months")
    metadata = {"scenario", "scenario_classification", "equity_return_provenance_status",
                "decision_evidence_status", "claim_lineage_record"}
    numeric_columns = [key for key in rerun_synthetic[0] if key not in metadata]
    current_index = {(row["portfolio"], row["month"]): row for row in current_synthetic}
    rerun_index = {(row["portfolio"], row["month"]): row for row in rerun_synthetic}
    _require(set(current_index) == set(rerun_index), "corrected scenario output cases do not match the rerun")
    exact_rerun_match = all(current_index[key][column] == rerun_index[key][column]
                            for key in current_index for column in numeric_columns)
    _require(exact_rerun_match, "corrected scenario values differ from the saved seeded rerun")
    _require(all(row["scenario_classification"] == "SYNTHETIC_ASSUMPTION_NOT_HISTORICAL_REPLAY"
                 and row["equity_return_provenance_status"] ==
                 "UNVERIFIED_THIRD_PARTY_REPORTED_CAGR_USED_AS_SYNTHETIC_ASSUMPTION"
                 and row["decision_evidence_status"] == QUARANTINE
                 and row["claim_lineage_record"] == CORRECTION_PATH
                 for row in current_synthetic + rerun_synthetic),
             "affected output rows lack explicit machine-readable quarantine or correction link")
    _require(all(row["decision_evidence_status"] == QUARANTINE
                 and row["claim_lineage_record"] == CORRECTION_PATH for row in synthetic),
             "assumption-register scenario lacks quarantine or correction link")

    reproduced_csv = reproduced_dir / "stage512_risk_scenarios.csv"
    reproduced_assumption_path = reproduced_dir / "stage512_assumption_register.json"
    committed_rerun_csv = RERUN_DIR / "stage512_risk_scenarios.csv"
    committed_rerun_assumption = RERUN_DIR / "stage512_assumption_register.json"
    _require(reproduced_csv.is_file() and reproduced_assumption_path.is_file(),
             "fresh model rerun must emit both expected artifacts")
    _require(_normalized_bytes(reproduced_csv) == _normalized_bytes(committed_rerun_csv),
             "fresh pinned-runtime scenario CSV does not reproduce committed rows exactly")
    assumption_register_within_tolerance = _json_close(
        _json(reproduced_assumption_path), _json(committed_rerun_assumption)
    )
    _require(assumption_register_within_tolerance,
             "fresh assumption register differs beyond the 1e-12 absolute floating-point tolerance")

    official_rows = _rows(ROOT / NSE_SERIES)
    validation = _json(ROOT / NSE_VALIDATION)
    _require(len(official_rows) == 129 and official_rows[0]["month"] == "2015-01"
             and official_rows[-1]["month"] == "2025-09",
             "official NSE monthly-anchor evidence no longer has the documented 129-month coverage")
    _require(validation["complete_official_NSE_daily_history_qualified"] is False
             and validation["full_2036_probability_qualified"] is False
             and validation["verified_months"] == 129,
             "NSE evidence must not be represented as a full since-1995 return path or probability qualification")
    report_text = (ROOT / report_rel).read_text(encoding="utf-8")
    _require("G5.1 correction" in report_text and "quarantined from investment-decision evidence" in report_text,
             "the historical report lacks an explicit visible correction notice")
    index_text = (ROOT / "research/stage512/2026-11-02/README.md").read_text(encoding="utf-8")
    _require("G5.1 evidence correction" in index_text
             and "../2026-11-05/g5_1_118_claim_lineage_v1.json" in index_text,
             "research archive index does not route readers to the correction record")
    old_claim_offenders = _repo_wide_claim_scan()
    _require(not old_claim_offenders,
             "repository contains the former replay claim outside the dated correction records: "
             + ", ".join(old_claim_offenders))

    evidence_paths = [
        ".github/workflows/g5-1-claim-lineage.yml",
        "decision/audit_g5_1_claim_lineage.py",
        "docs/DECISION_LOG.md",
        assumption_rel, model_rel, result_rel, report_rel,
        "research/stage512/2026-11-02/README.md", NSE_SERIES, NSE_VALIDATION,
        "research/stage512/2026-11-05/g5_1_118_assumption_rerun/stage512_assumption_register.json",
        "research/stage512/2026-11-05/g5_1_118_assumption_rerun/stage512_risk_scenarios.csv",
        "research/stage512/2026-11-05/G5_1_118_CLAIM_LINEAGE.md",
        "research/stage512/2026-11-05/g5_1_qcsae_v1.json",
    ]
    evidence_hashes = {path: _sha256(ROOT / path) for path in evidence_paths}
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
            "decision_evidence_status": QUARANTINE,
            "correction_record": CORRECTION_PATH,
        },
        "method_trace": {
            "model_path": model_rel,
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
            {"path": assumption_rel, "impact": "scenario relabeled; unverified provenance, quarantine status and correction link are explicit"},
            {"path": model_rel, "impact": "future runs emit corrected labels and row-level quarantine metadata; separate output directory is required"},
            {"path": result_rel, "impact": "six affected scenario rows relabeled and tagged; numeric results match the pinned original"},
            {"path": report_rel, "impact": "visible correction notice, source interpretation and quarantine links; numeric table values retained"},
            {"path": "research/stage512/2026-11-05/G5_1_118_CLAIM_LINEAGE.md", "impact": "dated human-readable correction and reproduction record"},
            {"path": "research/stage512/2026-11-05/g5_1_qcsae_v1.json", "impact": "counter-case, falsification checks, reopening evidence and NO-GO disposition"},
        ],
        "reproduction": {
            "runtime": "Python 3.13; NumPy 2.3.2",
            "command": "python research/stage512/2026-11-02/stage512_risk_audit.py --output-dir <fresh-output-directory>",
            "corrected_scenario_rows": 6,
            "numeric_values_match_pinned_original": baseline_numeric_preserved,
            "fresh_scenario_csv_matches_committed_output_exactly": True,
            "assumption_register_matches_with_abs_tolerance": 1e-12,
            "assumption_register_within_tolerance": assumption_register_within_tolerance,
            "pre_correction_source_hashes_verified_at_pinned_commit": baseline_hashes,
        },
        "current_source_hashes_sha256_utf8_lf": evidence_hashes,
        "repository_wide_former_claim_scan": {"status": "PASS", "offenders_outside_correction_records": []},
        "qcsae_record": "research/stage512/2026-11-05/g5_1_qcsae_v1.json",
        "g5_1_disposition": "PASS_FOR_LINEAGE_AND_LABEL_CORRECTION; INPUT_VALUE_REMAINS_UNVERIFIED; ALL_SCENARIO_OUTPUTS_REMAIN_RESEARCH_ONLY",
        "investment_authorization": "NO_GO",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    parser.add_argument("--baseline-dir", type=Path, required=True,
                        help="Pinned pre-correction files extracted from the recorded base commit")
    parser.add_argument("--reproduced-dir", type=Path, required=True,
                        help="Fresh outputs generated with the pinned Python/NumPy runtime")
    args = parser.parse_args()
    rendered = json.dumps(audit(args.baseline_dir, args.reproduced_dir), indent=2, ensure_ascii=False) + "\n"
    if args.check:
        _require(RECORD.read_text(encoding="utf-8") == rendered,
                 "committed G5.1 lineage record differs from regenerated audit output")
        print("G5.1 lineage, pinned original, fresh rerun, and row-level quarantine checks passed")
    elif args.write:
        RECORD.parent.mkdir(parents=True, exist_ok=True)
        RECORD.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"Wrote {RECORD.relative_to(ROOT)}")
