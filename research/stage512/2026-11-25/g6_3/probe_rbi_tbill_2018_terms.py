from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


URL = "https://rbidocs.rbi.org.in/rdocs/content/pdfs/GOI27032018_TBill.pdf"
OUT = Path("rbi_tbill_2018_terms_probe")
PDF_PATH = OUT / "GOI27032018_TBill.pdf"
MANIFEST_PATH = OUT / "probe_manifest.json"
MAX_BYTES = 5_000_000
TIMEOUT_SECONDS = 30
USER_AGENT = "G6.3-public-source-evidence/1.0"


def write_manifest(record: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(
        json.dumps(record, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        URL,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/pdf,*/*;q=0.8",
        },
    )
    retrieved_at = datetime.now(timezone.utc).isoformat()
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            body = response.read(MAX_BYTES + 1)
            record = {
                "retrieved_at_utc": retrieved_at,
                "source_url": URL,
                "final_url": response.geturl(),
                "method": "GET",
                "http_status": response.status,
                "content_type": response.headers.get("Content-Type", ""),
                "response_bytes": len(body),
                "response_sha256": hashlib.sha256(body).hexdigest(),
                "request_policy": "single sequential GET; no cookies; no challenge or access-control bypass; 30-second timeout; 5 MB cap; no retries",
            }
            if len(body) > MAX_BYTES:
                record.update({"result": "FAIL_RESPONSE_EXCEEDS_BYTE_CAP", "pdf_retained": False})
                write_manifest(record)
                print(json.dumps(record, indent=2))
                return 0
            if not body.startswith(b"%PDF-"):
                record.update({"result": "FAIL_RESPONSE_NOT_PDF", "pdf_retained": False})
                write_manifest(record)
                print(json.dumps(record, indent=2))
                return 0
            PDF_PATH.write_bytes(body)
            record.update(
                {
                    "result": "CAPTURED_OFFICIAL_RBI_LINKED_PDF",
                    "pdf_path": PDF_PATH.as_posix(),
                    "pdf_retained": True,
                }
            )
            write_manifest(record)
            print(json.dumps(record, indent=2))
            return 0
    except urllib.error.HTTPError as error:
        body = error.read(MAX_BYTES + 1)
        record = {
            "retrieved_at_utc": retrieved_at,
            "source_url": URL,
            "final_url": error.geturl(),
            "method": "GET",
            "http_status": error.code,
            "content_type": error.headers.get("Content-Type", ""),
            "response_bytes": len(body),
            "response_sha256": hashlib.sha256(body).hexdigest(),
            "result": "SOURCE_ACCESS_DENIED_OR_THROTTLED",
            "pdf_retained": False,
            "request_policy": "single sequential GET; no cookies; no challenge or access-control bypass; 30-second timeout; 5 MB cap; no retries",
        }
        write_manifest(record)
        print(json.dumps(record, indent=2))
        return 0
    except Exception as error:  # Preserve bounded failure evidence for network/TLS failures.
        record = {
            "retrieved_at_utc": retrieved_at,
            "source_url": URL,
            "method": "GET",
            "result": "SOURCE_REQUEST_FAILED",
            "error_type": type(error).__name__,
            "error": str(error),
            "pdf_retained": False,
            "request_policy": "single sequential GET; no cookies; no challenge or access-control bypass; 30-second timeout; 5 MB cap; no retries",
        }
        write_manifest(record)
        print(json.dumps(record, indent=2))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
