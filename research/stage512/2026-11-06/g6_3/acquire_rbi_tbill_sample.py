from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

OUT = Path("rbi_tbill_capture")
SOURCES = {
    "table218_20260731.xlsx": "https://rbidocs.rbi.org.in/rdocs/Publications/DOCs/218T_HBIE31072026D5086AE4949E4B9E80DEE6FC431C0761.XLSX",
    "auction_notice_20261030.html": "https://rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=63895",
    "full_result_20261104.html": "https://rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=63918",
    "cutoff_result_20261104.html": "https://rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=63917",
    "retail_ncb_faq.html": "https://m.rbi.org.in/commonman/english/scripts/FAQs.aspx?Id=711",
}
MAX_BYTES = 5_000_000


def fetch(url: str) -> tuple[bytes, str, int]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "G6.3-public-source-evidence/1.0", "Accept": "*/*"},
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read(MAX_BYTES + 1)
                if len(body) > MAX_BYTES:
                    raise RuntimeError(f"response exceeds {MAX_BYTES} byte cap: {url}")
                return body, response.headers.get("Content-Type", ""), response.status
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or attempt == 2:
                raise
            retry_after = min(int(exc.headers.get("Retry-After", "2")), 60)
            time.sleep(max(retry_after, 1))
    raise RuntimeError(f"unreachable fetch state: {url}")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": 1,
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "bounded official RBI T-bill route sample; not a historical series",
        "request_policy": "sequential; 2 seconds between requests; max 3 attempts for HTTP 429 only; 30-second timeout; 5 MB response cap",
        "sources": [],
    }
    for index, (filename, url) in enumerate(SOURCES.items()):
        body, content_type, status = fetch(url)
        if status != 200 or not body:
            raise RuntimeError(f"invalid response: status={status}, bytes={len(body)}, url={url}")
        if filename.endswith(".xlsx") and not body.startswith(b"PK"):
            raise RuntimeError("RBI Table 218 response is not an XLSX/ZIP payload")
        target = OUT / filename
        target.write_bytes(body)
        manifest["sources"].append({
            "url": url,
            "path": filename,
            "http_status": status,
            "content_type": content_type,
            "bytes": len(body),
            "sha256": hashlib.sha256(body).hexdigest(),
        })
        if index + 1 < len(SOURCES):
            time.sleep(2)
    (OUT / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()