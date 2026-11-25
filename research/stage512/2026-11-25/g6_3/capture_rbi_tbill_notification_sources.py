from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


OUT = Path(__file__).parent / "source_raw" / "rbi_notification_attachment_attempts"
MANIFEST = Path(__file__).parent / "rbi_tbill_amendment_access_probe_v1.json"
MAX_BYTES = 5_000_000
TIMEOUT_SECONDS = 25
USER_AGENT = "G6.3-public-source-evidence/1.0"
SOURCES = (
    ("base_notification_attachment_2018", "https://rbidocs.rbi.org.in/rdocs/content/pdfs/GOI27032018_A.pdf"),
    ("amendment_notification_2018_04_05", "https://rbidocs.rbi.org.in/rdocs/content/pdfs/GOI05042018_A.pdf"),
    ("amendment_notification_2021_12_23", "https://rbidocs.rbi.org.in/rdocs/content/pdfs/GOI23122021_A.pdf"),
)


def capture(source_id: str, url: str) -> dict[str, object]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/pdf,*/*;q=0.8",
        },
    )
    retrieved_at = datetime.now(timezone.utc).isoformat()
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(request, timeout=TIMEOUT_SECONDS) as response:
            body = response.read(MAX_BYTES + 1)
            status = response.status
            final_url = response.geturl()
            content_type = response.headers.get("Content-Type", "")
    except urllib.error.HTTPError as error:
        body = error.read(MAX_BYTES + 1)
        status = error.code
        final_url = error.geturl()
        content_type = error.headers.get("Content-Type", "")
    except Exception as error:
        return {
            "source_id": source_id,
            "source_url": url,
            "retrieved_at_utc": retrieved_at,
            "result": "SOURCE_REQUEST_FAILED",
            "error_type": type(error).__name__,
            "error": str(error),
            "raw_response_retained": False,
        }

    if len(body) > MAX_BYTES:
        return {
            "source_id": source_id,
            "source_url": url,
            "final_url": final_url,
            "retrieved_at_utc": retrieved_at,
            "http_status": status,
            "content_type": content_type,
            "response_bytes": len(body),
            "result": "RESPONSE_EXCEEDS_BYTE_CAP",
            "raw_response_retained": False,
        }

    is_pdf = body.startswith(b"%PDF-")
    suffix = ".pdf" if is_pdf else ".html"
    response_path = OUT / f"{source_id}{suffix}"
    response_path.parent.mkdir(parents=True, exist_ok=True)
    response_path.write_bytes(body)
    return {
        "source_id": source_id,
        "source_url": url,
        "final_url": final_url,
        "retrieved_at_utc": retrieved_at,
        "http_status": status,
        "content_type": content_type,
        "response_bytes": len(body),
        "response_sha256": hashlib.sha256(body).hexdigest(),
        "is_pdf": is_pdf,
        "result": "PDF_CAPTURED" if is_pdf else "RESPONSE_NOT_PDF",
        "response_path": response_path.relative_to(Path(__file__).parents[4]).as_posix(),
        "raw_response_retained": True,
    }


def main() -> int:
    records = [capture(source_id, url) for source_id, url in SOURCES]
    manifest = {
        "schema_version": 1,
        "capture_date_local": datetime.now().astimezone().date().isoformat(),
        "purpose": "Capture the exact RBI-linked 2018 T-bill base attachment and 2018/2021 amendment responses for source qualification.",
        "request_policy": "Sequential single GET per URL; direct connection to avoid the configured local proxy; no cookies, authentication, retries, challenge solving, or access-control bypass; 25-second timeout; 5 MB response cap.",
        "sources": records,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
