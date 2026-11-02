#!/usr/bin/env python3
"""Stage 5.12 official AMFI evidence pilot; not an investable portfolio or return forecast.

Source: official AMFI NAVAll and DownloadNAVHistoryReport_Po, not third-party NAV mirrors.
Use only provenance-checked observations. Never substitute prices, guess missing NAVs,
or declare a 2036 probability from pilot windows. Standard-library-only.
"""
from __future__ import annotations
import argparse, csv, datetime as dt, hashlib, json, re, sys, time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

HOST = "https://portal.amfiindia.com"
CURRENT_URL = HOST + "/spages/NAVAll.txt"
HISTORY_URL = HOST + "/DownloadNAVHistoryReport_Po.aspx"
MAX_BYTES = 15_000_000
DATE_FMT = "%d-%b-%Y"
CODE = re.compile(r"^[0-9]{5,8}$")
ISO_UTC = dt.timezone.utc

@dataclass(frozen=True)
class NavRow:
    code: str
    scheme_name: str
    nav: float
    asof: dt.date
    isin_growth_or_payout: str

def parse_date(value: str) -> dt.date:
    return dt.datetime.strptime(value.strip(), DATE_FMT).date()

def parse_nav_text(raw: bytes, *, history: bool) -> tuple[list[NavRow], dict]:
    text = raw.decode("utf-8-sig", errors="strict")
    data = []
    rejected = []
    duplicate_key = set()
    for line_no, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("Scheme Code;") or "Schemes(" in line or "Schemes (" in line:
            continue
        x = line.split(";")
        if not x or not CODE.fullmatch(x[0].strip()):
            continue
        if history:
            if len(x) != 8:
                rejected.append([line_no, "expected eight columns"]); continue
            code, name, isin, _, price, _, _, day = x
        else:
            if len(x) != 6:
                rejected.append([line_no, "expected six columns"]); continue
            code, isin, _, name, price, day = x
        try:
            nav = float(price)
            date = parse_date(day)
            if not (0 < nav < 1_000_000_000) or not name.strip():
                raise ValueError("missing name / invalid NAV")
            k = (code.strip(), date)
            if k in duplicate_key:
                rejected.append([line_no, "duplicate scheme/date"]); continue
            duplicate_key.add(k)
            data.append(NavRow(code.strip(), name.strip(), nav, date, isin.strip()))
        except (ValueError, OverflowError):
            rejected.append([line_no, "invalid NAV or date"])
    stats = {"parsed": len(data), "rejected": len(rejected), "rejection_sample": rejected[:20]}
    return data, stats

def fetch(url: str, *, retries: int = 2, timeout: int = 70) -> tuple[bytes, dict]:
    request = Request(url, headers={
        "User-Agent": "Stage512ResearchAudit/1.0 (+public GitHub Actions archival; source attribution)",
        "Accept": "text/plain,text/csv,*/*",
        "Accept-Language": "en-IN,en;q=0.9",
        "Accept-Encoding": "identity",
    })
    errors = []
    for n in range(retries + 1):
        try:
            with urlopen(request, timeout=timeout) as response:
                raw = response.read(MAX_BYTES + 1)
                if len(raw) > MAX_BYTES:
                    raise ValueError("AMFI response exceeds audited size cap")
                if response.status != 200 or not raw:
                    raise ValueError(f"Bad HTTP {response.status} or empty response")
                meta = {
                    "source_url": url, "http_status": response.status,
                    "content_type": response.headers.get("content-type", ""),
                    "response_bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                    "retrieved_utc": dt.datetime.now(ISO_UTC).isoformat(),
                }
            return raw, meta
        except Exception as exc:
            errors.append(f"{type(exc).__name__}: {exc}")
            if n < retries: time.sleep(2 * (n + 1))
    raise RuntimeError("; ".join(errors))

def classify_name(name: str) -> list[str]:
    low = name.casefold()
    labels = []
    if "nifty 500" in low or "nifty500" in low: labels.append("NIFTY500_NAMED")
    if "gilt" in low and "fund" in low: labels.append("GILT_NAMED")
    if "gold" in low and ("etf" in low or "exchange traded" in low): labels.append("GOLD_ETF_NAMED")
    if "silver" in low and ("etf" in low or "exchange traded" in low): labels.append("SILVER_ETF_NAMED")
    return labels

def windows_from_args(values: list[str]) -> list[tuple[dt.date, dt.date]]:
    result = []
    for value in values:
        a, b = value.split(":")
        start, end = dt.date.fromisoformat(a), dt.date.fromisoformat(b)
        if not start <= end or (end - start).days > 89:
            raise ValueError("AMFI pilot requires ordered, at most 90-day windows")
        result.append((start, end))
    return result

def run(out: Path, windows: list[tuple[dt.date, dt.date]]) -> int:
    out.mkdir(parents=True, exist_ok=True)
    raw_dir = out / "raw"; raw_dir.mkdir(exist_ok=True)
    events = []
    rows_out = []
    failed = 0
    jobs = [("latest", CURRENT_URL, None, None)] + [
        (f"history_{s.isoformat()}_{e.isoformat()}", HISTORY_URL + "?" + urlencode({
            "tp": "1", "frmdt": s.strftime(DATE_FMT), "todt": e.strftime(DATE_FMT)
        }), s, e) for s, e in windows
    ]
    for label, url, start, end in jobs:
        entry = {"label": label, "status": "FAIL", "start": str(start) if start else None,
                 "end": str(end) if end else None, "source_url": url}
        try:
            raw, meta = fetch(url)
            path = raw_dir / (label + ".txt")
            path.write_bytes(raw)
            data, stats = parse_nav_text(raw, history=start is not None)
            entry.update(meta); entry.update(stats)
            if stats["rejected"] > 0:
                raise ValueError(f"Malformed NAV rows: {stats['rejected']}")
            if len(data) < 100:
                raise ValueError(f"Only {len(data)} valid NAV observations; likely HTML or blocked")
            if start is not None:
                if any(not start <= z.asof <= end for z in data):
                    raise ValueError("Historical data escaped requested range")
                if len({z.asof for z in data}) < 2:
                    raise ValueError("Historical window has fewer than two distinct trading dates")
            entry.update(status="PASS", first_observation=min(z.asof for z in data).isoformat(),
                         last_observation=max(z.asof for z in data).isoformat(),
                         unique_schemes=len({z.code for z in data}),
                         unique_dates=len({z.asof for z in data}))
            for z in data:
                labels = classify_name(z.scheme_name)
                if not labels:
                    continue
                for category in labels:
                    rows_out.append([label, category, z.code, z.isin_growth_or_payout,
                                     z.scheme_name, z.asof.isoformat(), f"{z.nav:.6f}", meta["sha256"]])
        except Exception as exc:
            entry["error"] = f"{type(exc).__name__}: {exc}"
            failed += 1
        events.append(entry)
    with (out / "named_scheme_observations.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["source_window", "name_matching_category_NOT_verified_taxonomy", "scheme_code", "isin", "scheme_name", "date", "NAV", "source_sha256"])
        w.writerows(sorted(rows_out, key=lambda x: (x[2], x[5], x[0])))
    manifest = {
        "status": "PASS_PILOT_ONLY" if failed == 0 else "FAIL_INCOMPLETE",
        "run_utc": dt.datetime.now(ISO_UTC).isoformat(), "source_ownership": "AMFI official portal",
        "readme": "Named-scheme classes are keyword matches, not approved candidate identity. NAVs do not validate tracking error or scheme taxonomy.",
        "windows": events, "matched_rows": len(rows_out), "failed_windows": failed,
        "investment_authorization": "NO_GO",
        "full_investable_series_reconciled": False,
        "2036_real_world_probability_validated": False,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "retrievals": [{"label": e["label"], "status": e["status"], "obs": e.get("parsed"), "error": e.get("error")} for e in events]}, indent=2))
    return 0 if not failed else 2

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="research/stage512/data/amfi_pilot")
    ap.add_argument("--window", action="append", default=["2024-01-02:2024-01-05", "2026-10-19:2026-10-23"])
    args = ap.parse_args()
    return run(Path(args.output), windows_from_args(args.window))

if __name__ == "__main__": sys.exit(main())
