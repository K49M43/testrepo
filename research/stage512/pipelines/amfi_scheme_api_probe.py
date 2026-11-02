#!/usr/bin/env python3
"""Bounded, non-production official-AMFI scheme API discovery.

Undocumented public endpoint may change or require additional identifiers.
It is an exploratory source probe ONLY. Never use unqualified responses
as investable NAV histories or forecasts.
"""
from __future__ import annotations
import datetime as dt
import hashlib, json, urllib.parse, urllib.request
from pathlib import Path

BASE = "https://www.amfiindia.com/api/nav-history"
SPECS = [
    ("147625", "2023-09-25", "2026-10-30"),
    ("105463", "2023-09-25", "2026-10-30"),
]
OUTPUT = Path("research/stage512/data/amfi_api_probe.json")
def fetch(code: str, start: str, end: str) -> dict:
    url = BASE + "?" + urllib.parse.urlencode({
        "query_type": "historical_period", "from_date": start,
        "to_date": end, "sd_id": code
    })
    item = {"code": code, "start": start, "end": end, "url": url,
            "status": "FAIL_UNQUALIFIED"}
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (research evidence, AMFI public NAV)",
            "Accept": "application/json,text/plain,*/*",
            "Referer": "https://www.amfiindia.com/net-asset-value/nav-history",
            "Accept-Encoding": "identity"
        })
        with urllib.request.urlopen(req, timeout=28) as rsp:
            raw = rsp.read(2_000_001)
            item.update(http_status=rsp.status, content_type=rsp.headers.get("content-type", ""),
                        body_sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
        if len(raw) > 2_000_000:
            raise ValueError("Response larger than probe cap")
        body = json.loads(raw.decode("utf-8-sig"))
        if not isinstance(body, dict):
            raise ValueError("Expected JSON dictionary")
        item["top_level_keys"] = sorted(body.keys())
        d = body.get("data")
        item["data_type"] = type(d).__name__
        if isinstance(d, dict):
            item["data_keys"] = sorted(d.keys())
            nav_groups = d.get("nav_groups")
            if isinstance(nav_groups, list):
                item["nav_group_count"] = len(nav_groups)
                item["group_key_examples"] = [sorted(g.keys()) for g in nav_groups[:2] if isinstance(g, dict)]
                item["historical_record_counts"] = [
                    len(g.get("historical_records", []))
                    for g in nav_groups if isinstance(g, dict) and isinstance(g.get("historical_records"), list)
                ]
                item["nav_record_examples"] = [
                    {"nav_name": g.get("nav_name"), "first": g["historical_records"][0]}
                    for g in nav_groups[:2] if isinstance(g, dict)
                    and isinstance(g.get("historical_records"), list) and g["historical_records"]
                ]
        item["body_prefix"] = raw[:160].decode("utf-8", "replace")
        item["status"] = "RESPONDED_JSON_UNVALIDATED"
    except Exception as exc:
        item["error"] = f"{type(exc).__name__}: {exc}"
    return item

def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    out = {"run_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
           "purpose": "Official AMFI alternate API discovery, not approval",
           "probes": [fetch(*s) for s in SPECS],
           "qualified_as_official_NAV_series": False,
           "investment_gate": "NO_GO"}
    OUTPUT.write_text(json.dumps(out, indent=2))
    print(json.dumps({"status": [r["status"] for r in out["probes"]]}, indent=2))

if __name__ == "__main__":
    main()
