from __future__ import annotations

import csv
import datetime as dt
import decimal
import hashlib
import json
from pathlib import Path

D = decimal.Decimal
ROOT = Path(__file__).resolve().parents[1] / "source_retrieval_followup" / "candidates"
OUT = Path(__file__).with_name("candidate_nav_history_audit.json")
TRI_PATH = Path(__file__).resolve().parents[2] / "data" / "nse500_official_tri_monthly_2015_2025q3_R8.csv"
SPECS = {
    "147625": {"candidate": "MOTILAL_NIFTY500_INDEX_FUND", "isin": "INF247L01957", "scheme": "Motilal Oswal Nifty 500 Index Fund", "nav_tokens": ("Motilal Oswal Nifty 500 Index Fund", "Direct Plan"), "start": "2019-09-06", "end": "2026-10-31", "rows_key": "records"},
    "150681": {"candidate": "SBI_GILT_JUNE2036_FUND", "isin": "INF200KA12Q9", "scheme": "SBI CRISIL IBX Gilt Index - June 2036 Fund", "nav_tokens": ("CRISIL IBX Gilt Index - June 2036 Fund", "Direct Plan", "Growth"), "start": "2022-10-04", "end": "2026-10-31", "rows_key": "records"},
    "113049": {"candidate": "HDFC_GOLD_ETF", "isin": "INF179KC1981", "scheme": "HDFC Gold ETF", "nav_tokens": ("HDFC Gold ETF", "Growth Option"), "start": "2015-01-01", "end": "2026-10-31", "rows_key": "records"},
    "149464": {"candidate": "ICICI_SILVER_ETF", "isin": "INF109KC1Y56", "scheme": "ICICI PRUDENTIAL SILVER ETF", "nav_tokens": ("ICICI PRUDENTIAL SILVER ETF",), "start": "2022-01-24", "end": "2026-10-31", "rows_key": "records"},
    "152908": {"candidate": "SBI_NIFTY500_INDEX_FUND", "isin": "INF200KB1381", "scheme": "SBI Nifty 500 Index Fund", "nav_tokens": ("SBI Nifty 500 Index Fund", "Direct Plan", "Growth"), "start": "2024-09-30", "end": "2026-10-31", "rows_key": "records"},
}


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def norm(x: str) -> str:
    return " ".join(x.casefold().split())


def audit(code: str, spec: dict) -> dict:
    mp = ROOT / f"nav_{code}_manifest.json"
    manifest = json.loads(mp.read_text(encoding="utf-8"))
    assert manifest["scheme_code"] == code and manifest["isin"] == spec["isin"]
    assert manifest["status"] in ("PASS_COMPLETE_DECLARED_WINDOW", "PASS_CONTIGUOUS_PRODUCT_NAV_HISTORY")
    segments = manifest["segments"]
    assert len(segments) == manifest["requested_segments"] == manifest["retrieved_segments"]
    expected_start, expected_end = dt.date.fromisoformat(spec["start"]), dt.date.fromisoformat(spec["end"])
    ordered_segments = sorted(segments, key=lambda x: x["start"])
    assert dt.date.fromisoformat(ordered_segments[0]["start"]) == expected_start
    assert dt.date.fromisoformat(ordered_segments[-1]["end"]) == expected_end
    reconstructed: dict[str, tuple[D, str, str]] = {}
    segment_checks = []
    prev_end = None
    for seg in ordered_segments:
        start, end = dt.date.fromisoformat(seg["start"]), dt.date.fromisoformat(seg["end"])
        assert start <= end
        if prev_end is not None:
            assert start == prev_end + dt.timedelta(days=1), f"non-contiguous request windows before {start}"
        prev_end = end
        raw = (ROOT / f"nav_{code}_{seg['start']}_{seg['end']}.json").read_bytes()
        assert len(raw) == seg["bytes"] and sha(raw) == seg["sha256"]
        payload = json.loads(raw)["data"]
        assert norm(payload["scheme_name"]) == norm(spec["scheme"])
        groups = payload["nav_groups"]
        assert len(groups) == 1
        group = groups[0]
        nav_name = group["nav_name"]
        assert all(norm(token) in norm(nav_name) for token in spec["nav_tokens"]), nav_name
        if code == "152908":
            assert norm(payload.get("isin", spec["isin"])) == norm(spec["isin"])
            assert norm(group.get("historical_records", [{}])[0].get("Plan", "Direct Plan")) == "direct plan"
            rows = group["historical_records"]
        else:
            rows = group["historical_records"]
        assert rows and len(rows) == seg.get("records", seg.get("record_count"))
        dates = []
        for row in rows:
            day = dt.date.fromisoformat(row["date"])
            value = D(str(row["nav"]))
            assert start <= day <= end and value.is_finite() and value > 0
            option = str(row.get("Option") or "").strip().casefold()
            plan = str(row.get("Plan") or "").strip().casefold()
            assert not option or "growth" in option, (day, option)
            assert not plan or "direct" in plan, (day, plan)
            key = day.isoformat()
            assert key not in reconstructed, f"duplicate date across windows: {key}"
            reconstructed[key] = (value, payload["scheme_name"], nav_name)
            dates.append(day)
        assert len(set(dates)) == len(dates)
        assert min(dates).isoformat() == seg["first"] and max(dates).isoformat() == seg["last"]
        segment_checks.append({"start": seg["start"], "end": seg["end"], "rows": len(rows), "sha256": seg["sha256"], "first": min(dates).isoformat(), "last": max(dates).isoformat()})
    assert len(reconstructed) == manifest["observations"]
    csv_path = ROOT / f"nav_{code}_daily.csv"
    csv_bytes = csv_path.read_bytes()
    assert sha(csv_bytes) == manifest["normalized_csv_sha256"]
    normalized = {}
    with csv_path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            day = row["date"]
            assert day not in normalized
            assert row["scheme_code"] == code and row["isin"] == spec["isin"]
            source_hash = row.get("segment_sha256") or row.get("source_segment_sha256")
            assert source_hash in {s["sha256"] for s in segments}
            nav_name = row.get("nav_name") or row.get("plan_option")
            normalized[day] = (D(row["nav"]), row["scheme_name"], nav_name)
    assert normalized == reconstructed, f"normalized CSV differs from raw reconstruction for {code}"
    dates = [dt.date.fromisoformat(x) for x in sorted(reconstructed)]
    gaps = [(a.isoformat(), b.isoformat(), (b-a).days) for a,b in zip(dates, dates[1:]) if (b-a).days > 12]
    assert not gaps, gaps
    assert dates[0] >= expected_start and dates[-1] <= expected_end
    return {"candidate_id": spec["candidate"], "scheme_code": code, "isin": spec["isin"], "status": "PASS_RAW_TO_NORMALIZED_LINEAGE_AND_DATE_CONTINUITY", "request_windows": len(segments), "observations": len(dates), "first_observation": dates[0].isoformat(), "last_observation": dates[-1].isoformat(), "max_gap_days": max((b-a).days for a,b in zip(dates, dates[1:])), "gaps_over_12_days": gaps, "raw_segment_checks": segment_checks, "normalized_csv_sha256": sha(csv_bytes)}


def audit_sbi_exploratory() -> dict:
    code = "152908"
    p = ROOT / "nav_152908_2024-09-30_2025-03-31.json"
    raw = p.read_bytes()
    data = json.loads(raw)["data"]
    rows = data["nav_groups"][0]["historical_records"]
    canonical = {}
    for seg in json.loads((ROOT / "nav_152908_manifest.json").read_text())["segments"]:
        d = json.loads((ROOT / f"nav_{code}_{seg['start']}_{seg['end']}.json").read_bytes())["data"]
        for row in d["nav_groups"][0]["historical_records"]:
            canonical[row["date"]] = D(str(row["nav"]))
    overlap = 0
    for row in rows:
        day, value = row["date"], D(str(row["nav"]))
        assert day in canonical and canonical[day] == value, f"exploratory overlap mismatch {day}"
        overlap += 1
    return {"artifact": p.name, "classification": "EXPLORATORY_OVERLAP_ONLY_NOT_CANONICAL_PARTITION", "sha256": sha(raw), "overlap_observations": overlap, "exact_match": True}


def monthly_alignment() -> list[dict]:
    with TRI_PATH.open(encoding="utf-8", newline="") as f:
        benchmark = {r["month"]: D(r["nifty500_tri_monthly_return_pct"]) for r in csv.DictReader(f)}
    results = []
    for code, spec in SPECS.items():
        monthly = {}
        with (ROOT / f"nav_{code}_daily.csv").open(encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                month = row["date"][:7]
                day = row["date"]
                if month not in monthly or day > monthly[month][0]:
                    monthly[month] = (day, D(row["nav"]))
        fund_returns = {}
        for month, (day, value) in monthly.items():
            year, mon = map(int, month.split("-"))
            prior_month = f"{year-1:04d}-12" if mon == 1 else f"{year:04d}-{mon-1:02d}"
            if prior_month in monthly:
                prior = monthly[prior_month][1]
                fund_returns[month] = (value / prior - D(1)) * D(100)
        common = sorted(set(fund_returns) & set(benchmark))
        assert common
        dates = [dt.date.fromisoformat(month + "-01") for month in common]
        gaps = [(a.isoformat(), b.isoformat()) for a,b in zip(dates, dates[1:]) if (b.year-a.year)*12+b.month-a.month != 1]
        assert not gaps, gaps
        results.append({"candidate_id": spec["candidate"], "benchmark": "NIFTY 500 TRI", "product_measure": "AMFI Growth-option NAV; calendar-month return between the last available AMFI NAV in adjacent months", "benchmark_measure": "official NSE-published monthly TRI return, rounded as published", "common_months": len(common), "first_common_month": common[0], "last_common_month": common[-1], "interior_missing_months": [], "use_limit": "date-aligned descriptive evidence only; not a complete daily benchmark path, not market-price execution evidence, and not a probability or recommendation"})
    return results


def main() -> None:
    results = [audit(code, spec) for code, spec in SPECS.items()]
    exploratory = audit_sbi_exploratory()
    report = {"schema_version": 1, "record_id": "g5-4-candidate-nav-history-independent-audit-2026-11-05-v2", "audit_method": "offline reconstruction from retained raw AMFI JSON; SHA-256, scheme/ISIN/plan/option, date bounds, Decimal NAV, duplicate, normalized CSV equality, request partition and >12-day calendar-gap checks", "results": results, "exploratory_overlap": exploratory, "strict_calendar_month_alignment_to_nse_tri": monthly_alignment(), "overall": "PASS"}
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"overall": report["overall"], "candidates": [{k:r[k] for k in ("candidate_id","status","observations","first_observation","last_observation","max_gap_days")} for r in results], "exploratory_overlap": exploratory}, indent=2))


if __name__ == "__main__":
    main()
