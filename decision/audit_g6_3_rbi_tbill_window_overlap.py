#!/usr/bin/env python3
"""Audit overlap and deduplication across the retained RBI 91-day auction windows."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "research/stage512/2026-11-24/g6_3/rbi_tbill_three_window_overlap_audit_v1.json"
WINDOWS = (
    ("Table 213", ROOT / "research/stage512/2026-11-24/g6_3/rbi_tbill_window_2023_2024", "auction_panel_2023_2024.csv", 60, "2023-07-12", "2024-08-28"),
    ("Table 217", ROOT / "research/stage512/2026-11-19/g6_3/rbi_tbill_window_2024_2025", "auction_panel_2024_2025.csv", 55, "2024-07-03", "2025-07-30"),
    ("Table 218", ROOT / "research/stage512/2026-11-06/g6_3/rbi_tbill_window_2025_2026", "auction_panel_2025_2026.csv", 50, "2025-07-02", "2026-06-24"),
)
COMPARE_FIELDS = (
    "issue_date", "notified_amount_crore", "total_issue_crore", "cutoff_price",
    "cutoff_yield_actual_365_pct", "auction_method", "weighted_price_91",
    "weighted_yield_91", "cutoff_price_91", "cutoff_yield_91", "result_status",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_window(name: str, directory: Path, filename: str, expected_count: int, first: str, last: str):
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    panel_path = directory / filename
    with panel_path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    dates = [row["auction_date"] for row in rows]
    require(len(rows) == expected_count, f"{name}: row count differs")
    require(len(set(dates)) == expected_count, f"{name}: duplicate auction date")
    require(min(dates) == first and max(dates) == last, f"{name}: date endpoints differ")
    require(manifest["expected_auctions"] == expected_count, f"{name}: manifest count differs")
    normalized = manifest.get("normalized_panel")
    if normalized:
        panel_bytes = panel_path.read_bytes()
        require(normalized["path"] == filename and normalized["bytes"] == len(panel_bytes)
                and normalized["sha256"] == digest(panel_bytes), f"{name}: panel hash differs")
    return manifest, panel_path, {row["auction_date"]: row for row in rows}


def overlap_record(left_name: str, left: dict, right_name: str, right: dict) -> dict:
    common = sorted(set(left) & set(right))
    conflicts = []
    for day in common:
        differing = [field for field in COMPARE_FIELDS if left[day].get(field, "") != right[day].get(field, "")]
        if differing:
            conflicts.append({"auction_date": day, "differing_fields": differing})
    require(not conflicts, f"{left_name}/{right_name} overlap conflicts: {conflicts}")
    return {
        "left": left_name,
        "right": right_name,
        "overlap_dates": len(common),
        "first_overlap": common[0] if common else None,
        "last_overlap": common[-1] if common else None,
        "field_mismatches": 0,
    }


def build_record() -> dict:
    loaded = {}
    source_windows = []
    for name, directory, filename, count, first, last in WINDOWS:
        manifest, panel_path, rows = read_window(name, directory, filename, count, first, last)
        loaded[name] = rows
        source_windows.append({
            "name": name,
            "first_auction_date": first,
            "last_auction_date": last,
            "dated_rows": len(rows),
            "manifest": (directory / "manifest.json").relative_to(ROOT).as_posix(),
            "normalized_panel": panel_path.relative_to(ROOT).as_posix(),
            "normalized_panel_sha256": digest(panel_path.read_bytes()),
            "source_date_conflicts": manifest.get("source_discrepancies", {}).get("issue_date_conflicts", []),
        })

    overlap_213_217 = overlap_record("Table 213", loaded["Table 213"], "Table 217", loaded["Table 217"])
    overlap_217_218 = overlap_record("Table 217", loaded["Table 217"], "Table 218", loaded["Table 218"])
    overlap_213_218 = overlap_record("Table 213", loaded["Table 213"], "Table 218", loaded["Table 218"])
    require((overlap_213_217["overlap_dates"], overlap_213_217["first_overlap"], overlap_213_217["last_overlap"]) == (9, "2024-07-03", "2024-08-28"), "Table 213/217 overlap coverage differs")
    require((overlap_217_218["overlap_dates"], overlap_217_218["first_overlap"], overlap_217_218["last_overlap"]) == (5, "2025-07-02", "2025-07-30"), "Table 217/218 overlap coverage differs")
    require(overlap_213_218["overlap_dates"] == 0, "unexpected Table 213/218 overlap")

    # Later official tables supersede earlier duplicate rows only after all
    # common fields agree; each window's original source panel remains intact.
    unique = {}
    for name in ("Table 213", "Table 217", "Table 218"):
        unique.update(loaded[name])
    ordered_dates = sorted(unique)
    positive = [unique[day] for day in ordered_dates if unique[day]["result_status"] == "MATCHED"]
    zero_issues = [day for day in ordered_dates if unique[day]["result_status"] == "ZERO_ISSUE_EXCEPTION"]
    yields = sorted(Decimal(row["weighted_yield_91"]) for row in positive)
    require(len(ordered_dates) == 151, f"expected 151 unique dates, found {len(ordered_dates)}")
    require(len(positive) == 149 and len(zero_issues) == 2, "positive/zero issue counts differ")

    # The 2023-24 handbook conflicts with its contemporaneous auction notice
    # on four issue dates. Preserve both and use the notice date; the 2024-08-14
    # overlap is independently corroborated by Table 217.
    table213_conflicts = source_windows[0]["source_date_conflicts"]
    require(len(table213_conflicts) == 4, f"expected four Table 213 issue-date conflicts, found {len(table213_conflicts)}")
    conflict_20240814 = next((x for x in table213_conflicts if x["auction_date"] == "2024-08-14"), None)
    require(conflict_20240814 is not None and conflict_20240814["notice_issue_date"] == loaded["Table 217"]["2024-08-14"]["issue_date"], "2024-08-14 issue date is not corroborated by Table 217")

    median = statistics.median(yields)
    return {
        "schema_version": 1,
        "record_id": "g6-3-rbi-tbill-three-window-overlap-2026-11-24-v1",
        "as_of": "2026-11-24",
        "result": "PASS_RBI_THREE_WINDOW_OVERLAP_AND_EXACT_DATE_COVERAGE_WITH_LIMITATIONS",
        "source_windows": source_windows,
        "pairwise_overlaps": [overlap_213_217, overlap_217_218, overlap_213_218],
        "deduplicated_panel": {
            "first_auction_date": ordered_dates[0],
            "last_auction_date": ordered_dates[-1],
            "unique_auction_dates": len(ordered_dates),
            "positive_91_day_price_observations": len(positive),
            "zero_issue_exceptions": zero_issues,
            "weighted_average_91_day_yield_levels_pct_actual_365": {
                "minimum": str(min(yields).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)),
                "median": str(median.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)),
                "mean": str((sum(yields) / Decimal(len(yields))).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)),
                "maximum": str(max(yields).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)),
                "classification": "DESCRIPTIVE_QUOTE_LEVELS_NOT_REALIZED_ROLLOVER_RETURNS_OR_RISK_OBSERVATIONS",
            },
        },
        "known_source_conflicts": {
            "table_213_issue_date_conflicts": table213_conflicts,
            "resolution": "retain the original table value and contemporaneous notice value; normalized issue_date follows the auction notice; only 2024-08-14 has an independent Table 217 cross-window corroboration",
        },
        "decision_limits": [
            "Three years of weekly auction quotes do not establish a 2014-2026 rollover history, long-run return distribution, equity-bond covariance, or 2036 success probability.",
            "Weighted-average auction prices assume full NCB allocation and do not establish this investor's allotment, cash timing, fees, tax, or net return.",
            "This audit qualifies source overlap and deduplication only; maturity holiday schedules are audited separately.",
        ],
        "investment_authorization": "NO_GO",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build_record(), indent=2, ensure_ascii=False) + "\n"
    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"Wrote {OUTPUT.relative_to(ROOT)}")
        return 0
    require(OUTPUT.is_file(), "three-window overlap audit artifact is missing")
    require(OUTPUT.read_text(encoding="utf-8") == rendered, "three-window overlap audit differs from reconstructed evidence")
    print("PASS: three RBI 91-day auction windows reconcile, deduplicate to 151 dates, and preserve all explicit source date conflicts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
