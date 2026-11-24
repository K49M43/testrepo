from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "research/stage512/2026-11-25/g6_3"
URL = "https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=56455"
USER_AGENT = "G6.3-public-source-evidence/1.0"
GAP_SECONDS = 2
MAX_BYTES = 2_000_000


class VisibleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self.skip += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self.skip:
            self.skip -= 1

    def handle_data(self, data: str) -> None:
        if not self.skip:
            self.parts.append(data)


def fetch() -> tuple[bytes, dict[str, object]]:
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
    last_request = 0.0
    for attempt in range(3):
        delay = GAP_SECONDS - (time.monotonic() - last_request)
        if delay > 0:
            time.sleep(delay)
        request = urllib.request.Request(URL, headers={"User-Agent": USER_AGENT, "Accept": "text/html,*/*"})
        retrieved = datetime.now(timezone.utc).isoformat()
        try:
            with opener.open(request, timeout=30) as response:
                body = response.read(MAX_BYTES + 1)
                if response.status != 200 or len(body) > MAX_BYTES or not body:
                    raise RuntimeError(f"invalid RBI exception response: status={response.status}, bytes={len(body)}")
                metadata = {
                    "url": URL,
                    "method": "GET",
                    "http_status": response.status,
                    "content_type": response.headers.get("Content-Type", ""),
                    "response_date": response.headers.get("Date"),
                    "retrieved_at_utc": retrieved,
                    "bytes": len(body),
                    "sha256": hashlib.sha256(body).hexdigest(),
                }
                return body, metadata
        except urllib.error.HTTPError as exc:
            last_request = time.monotonic()
            if exc.code != 429 or attempt == 2:
                raise
            time.sleep(min(max(int(exc.headers.get("Retry-After", "2")), 1), 60))
    raise RuntimeError("RBI source retry state exhausted")


def main() -> None:
    body, source = fetch()
    parser = VisibleText()
    parser.feed(body.decode("utf-8", errors="replace"))
    text = " ".join(" ".join(parser.parts).split())
    required_phrases = (
        "September 29, 2023 as a public holiday",
        "Government securities market",
        "operational on September 29, 2023",
        "treasury bills conducted on September 27, 2023 will take place on September 29, 2023",
        "2023-2024/1005",
    )
    missing = [phrase for phrase in required_phrases if phrase.casefold() not in text.casefold()]
    if missing:
        raise RuntimeError(f"official RBI G-Sec exception page lacks required terms: {missing}")
    OUT.mkdir(parents=True, exist_ok=True)
    source_path = OUT / "source_raw/rbi_gsec_market_open_exception_2023_09_29.html"
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.write_bytes(body)
    manifest = {
        "schema_version": 1,
        "captured_at_utc": source["retrieved_at_utc"],
        "source_class": "OFFICIAL_RBI_PRESS_RELEASE",
        "scope": "One specific G-Sec market-operational exception: 29-Sep-2023 was a Maharashtra NI Act public holiday, but RBI kept Government-securities markets operational and explicitly set settlement for the 27-Sep-2023 GoI T-bill auction on 29-Sep-2023.",
        "operational_exception_dates": [
            {
                "date": "2023-09-29",
                "status": "GSEC_MARKET_OPERATIONAL_DESPITE_NI_ACT_PUBLIC_HOLIDAY",
                "auction_settlement": {"auction_date": "2023-09-27", "settlement_date": "2023-09-29"},
                "rbi_press_release_number": "2023-2024/1005",
            }
        ],
        "sources": [{
            **source,
            "path": "source_raw/rbi_gsec_market_open_exception_2023_09_29.html",
            "supports": "RBI's explicit market-operational exception and the T-bill auction's stated 29-Sep-2023 settlement date.",
        }],
        "interpretation_limit": "This is a date-specific override, not a complete historical G-Sec business-day calendar. Do not infer that other Mumbai NI Act holidays were market-open or market-closed without the applicable RBI source.",
    }
    manifest_path = OUT / "rbi_gsec_calendar_exceptions_v1.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"result": "CAPTURED_RBI_GSEC_OPERATIONAL_EXCEPTION", "source": source, "manifest": str(manifest_path.relative_to(ROOT))}, indent=2))


if __name__ == "__main__":
    main()
