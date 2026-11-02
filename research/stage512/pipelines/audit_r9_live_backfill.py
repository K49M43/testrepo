#!/usr/bin/env python3
"""Independently audit the committed artifacts from the R9 AMFI NAV backfill.

This validator does not call the AMFI acquisition code or access the network.
It recomputes raw hashes and reconstructs the accepted daily NAV observations
from the original response bytes before comparing the daily/monthly outputs.
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import statistics
from urllib.parse import parse_qs, urlparse

BASE = Path("research/stage512/data/r9_lic_gsec_etf")
MANIFEST = BASE / "qualification_manifest.json"
DAILY = BASE / "lic_gsec_133307_amfi_daily.csv"
MONTHLY = BASE / "lic_gsec_133307_monthly_returns.csv"
OUT = BASE / "r93_independent_artifact_audit.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[str] = []
    if manifest.get("status") != "PASS_OFFICIAL_NAV_11YR_RESEARCH_ONLY":
        raise ValueError("The source manifest is not a complete R9 research-only pass")
    if manifest.get("scheme_code") != "133307" or manifest.get("isin") != "INF767K01MV5":
        raise ValueError("Unexpected scheme code or ISIN")
    checks.append("manifest status and scheme identity")

    intervals = manifest.get("segments", [])
    if len(intervals) != 24 or any(x.get("status") != "PASS_SOURCE_SEGMENT" for x in intervals):
        raise ValueError("Expected 24 accepted six-month source segments")

    reconstructed: dict[dt.date, float] = {}
    raw_hashes: list[str] = []
    raw_bytes = 0
    null_option_records = 0
    explicit_growth_records = 0
    previous_end: dt.date | None = None
    for segment in intervals:
        start = dt.date.fromisoformat(segment["start"])
        end = dt.date.fromisoformat(segment["end"])
        if previous_end is not None and start != previous_end + dt.timedelta(days=1):
            raise ValueError(f"Non-contiguous source windows at {start}")
        previous_end = end
        query = parse_qs(urlparse(segment["url"]).query)
        if query.get("sd_id") != ["133307"]:
            raise ValueError("Segment URL does not request AMFI scheme 133307")
        raw_path = BASE / "raw" / f"{start}_{end}.json"
        raw = raw_path.read_bytes()
        actual_sha = hashlib.sha256(raw).hexdigest()
        if actual_sha != segment.get("sha256") or len(raw) != segment.get("bytes"):
            raise ValueError(f"Raw source integrity mismatch for {start} to {end}")
        raw_hashes.append(actual_sha)
        raw_bytes += len(raw)
        payload = json.loads(raw)
        body = payload.get("data") if isinstance(payload, dict) else None
        groups = body.get("nav_groups") if isinstance(body, dict) else None
        if body.get("scheme_name") != "LIC MF Nifty 8-13 yr G-Sec ETF" or not isinstance(groups, list) or len(groups) != 1:
            raise ValueError(f"Unexpected AMFI response identity for {start} to {end}")
        group = groups[0]
        if group.get("nav_name") != "LIC MF Nifty 8-13 yr G-Sec ETF":
            raise ValueError(f"Unexpected NAV group identity for {start} to {end}")
        records = group.get("historical_records")
        if not isinstance(records, list) or len(records) != segment.get("n"):
            raise ValueError(f"Source record count mismatch for {start} to {end}")
        segment_dates: list[dt.date] = []
        for record in records:
            date = dt.date.fromisoformat(record["date"])
            nav = float(record["nav"])
            if date < start or date > end or not math.isfinite(nav) or nav <= 0:
                raise ValueError(f"Invalid source date/NAV: {date} {nav}")
            option = record.get("Option")
            if option is None or not str(option).strip():
                null_option_records += 1
            elif "growth" in str(option).strip().lower():
                explicit_growth_records += 1
            else:
                raise ValueError(f"Unexpected non-growth option: {option}")
            if date in reconstructed and abs(reconstructed[date] - nav) > 0.0002:
                raise ValueError(f"Conflicting NAV on {date}")
            reconstructed[date] = nav
            segment_dates.append(date)
        if len(set(segment_dates)) != len(segment_dates):
            raise ValueError(f"Duplicate source dates inside {start} to {end}")
    checks.append("24 raw AMFI response byte hashes, sizes, identity, options and record totals")

    daily_rows = list(csv.DictReader(DAILY.open(newline="", encoding="utf-8")))
    daily_hash = sha256(DAILY)
    if daily_hash != manifest.get("daily_source_sha256"):
        raise ValueError("Daily NAV output hash differs from the manifest")
    if len(daily_rows) != len(reconstructed) or len(daily_rows) != manifest.get("observations"):
        raise ValueError("Daily NAV output row count does not match source reconstruction")
    daily_dates: list[dt.date] = []
    for row in daily_rows:
        date = dt.date.fromisoformat(row["date"])
        nav = float(row["nav_inr"])
        if row["amfi_scheme_code"] != "133307" or row["source_type"] != "AMFI_OFFICIAL_NAV":
            raise ValueError(f"Unexpected output identity at {date}")
        if date not in reconstructed or abs(nav - reconstructed[date]) > 0.000000006:
            raise ValueError(f"Output NAV does not reproduce raw source at {date}")
        daily_dates.append(date)
    if daily_dates != sorted(set(daily_dates)):
        raise ValueError("Daily NAV output is not uniquely date-sorted")
    gaps = [(b - a).days for a, b in zip(daily_dates, daily_dates[1:])]
    if not gaps or max(gaps) > 12:
        raise ValueError("Daily NAV series contains a gap greater than 12 calendar days")
    daily_returns = [float(b["nav_inr"]) / float(a["nav_inr"]) - 1 for a, b in zip(daily_rows, daily_rows[1:])]
    if any(r < -0.5 or r > 1.0 for r in daily_returns):
        raise ValueError("Daily NAV series contains a split-sized price discontinuity")
    checks.append("daily CSV reconstructed from source bytes, date continuity and jump screen")

    monthly_rows = list(csv.DictReader(MONTHLY.open(newline="", encoding="utf-8")))
    monthly_hash = sha256(MONTHLY)
    if monthly_hash != manifest.get("monthly_source_sha256") or len(monthly_rows) != manifest.get("months_of_return"):
        raise ValueError("Monthly return output hash or row count mismatch")
    month_ends: dict[str, tuple[dt.date, float]] = {}
    for date, nav in zip(daily_dates, [float(r["nav_inr"]) for r in daily_rows]):
        month_ends[date.strftime("%Y-%m")] = (date, nav)
    if len(month_ends) != len(monthly_rows) + 1:
        raise ValueError("Monthly return rows do not represent each adjacent NAV month")
    for prior, current, row in zip(sorted(month_ends), sorted(month_ends)[1:], monthly_rows):
        previous_date, previous_nav = month_ends[prior]
        end_date, end_nav = month_ends[current]
        if row["month"] != current or row["end_nav_date"] != end_date.isoformat():
            raise ValueError(f"Monthly return date mismatch for {current}")
        if not math.isclose(float(row["log_nav_return"]), math.log(end_nav / previous_nav), abs_tol=1e-12):
            raise ValueError(f"Monthly log return mismatch for {current}")
    checks.append("monthly returns independently recomputed from month-end NAVs")

    recent = [
        row for row in monthly_rows
        if "2023-11" <= row["month"] <= "2026-10"
    ]
    if len(recent) != 36 or recent[0]["month"] != "2023-11" or recent[-1]["month"] != "2026-10":
        raise ValueError("Expected the common R7 36-month return window")
    lic_recent_vol = statistics.stdev(float(row["log_nav_return"]) for row in recent) * math.sqrt(12) * 100
    r7 = json.loads(Path("research/stage512/data/official_nav_independent_R7.json").read_text(encoding="utf-8"))
    hdfc_recent_vol = r7["full_period_annualized_log_return_volatility_pct"]["gilt_fund"]
    checks.append("same-window 36-month LIC ETF NAV and HDFC Gilt Fund volatility comparison")

    cagr = manifest.get("official_lic_factsheet_cagr_comparisons", [])
    if [x.get("period_years") for x in cagr] != [1, 3, 5] or any(x.get("abs_difference_pp", 999) > 0.14 for x in cagr):
        raise ValueError("LIC published 1/3/5-year factsheet reconciliation did not pass")
    checks.append("LIC March 2026 published 1/3/5-year NAV CAGR arithmetic")

    result = {
        "status": "PASS_INDEPENDENT_ARTIFACT_AUDIT_RESEARCH_ONLY",
        "investment_authorization": "NO_GO",
        "source_manifest_sha256": sha256(MANIFEST),
        "raw_segments": len(intervals),
        "raw_source_bytes_total": raw_bytes,
        "raw_segment_sha256_list": raw_hashes,
        "reconstructed_observations": len(reconstructed),
        "first_date": daily_dates[0].isoformat(),
        "last_date": daily_dates[-1].isoformat(),
        "maximum_gap_calendar_days": max(gaps),
        "minimum_daily_simple_return_pct": round(min(daily_returns) * 100, 6),
        "maximum_daily_simple_return_pct": round(max(daily_returns) * 100, 6),
        "null_or_absent_option_records": null_option_records,
        "explicit_growth_option_records": explicit_growth_records,
        "daily_csv_sha256": daily_hash,
        "monthly_csv_sha256": monthly_hash,
        "factsheet_comparisons": cagr,
        "recent_36_month_risk_comparison": {
            "return_window": [recent[0]["month"], recent[-1]["month"]],
            "observations": len(recent),
            "lic_gsec_etf_nav_annualized_log_volatility_pct": round(lic_recent_vol, 5),
            "hdfc_gilt_fund_annualized_log_volatility_pct": hdfc_recent_vol,
            "warning": "Descriptive NAV volatility only; different funds and no forward-risk inference.",
        },
        "checks": checks,
        "limitations": [
            "AMFI returns are scheme NAV, not ETF exchange market prices or the NSE G-Sec total-return index.",
            "The daily jump screen is a diagnostic, not a separately sourced corporate-action/event ledger.",
            "LIC factsheet reconciliation covers only the published March 2026 1/3/5-year NAV CAGR anchors.",
            "This source and artifact pass does not validate forward returns, taxes, real-wealth probability or investment suitability.",
        ],
    }
    with OUT.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("status", "raw_segments", "reconstructed_observations", "first_date", "last_date", "maximum_gap_calendar_days")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
