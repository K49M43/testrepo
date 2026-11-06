from __future__ import annotations

import hashlib
import http.cookiejar
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

OUT = Path("rbi_tbill_capture")
SOURCES = {
    "table218_20260731.html": "https://www.rbi.org.in/Scripts/PublicationsView.aspx?id=24043",
    "auction_notice_20261030.html": "https://rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=63895",
    "full_result_20261104.html": "https://rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=63918",
    "cutoff_result_20261104.html": "https://rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=63917",
    "retail_ncb_faq.html": "https://m.rbi.org.in/commonman/english/scripts/FAQs.aspx?Id=711",
    "press_release_archive.html": "https://rbi.org.in/scripts/FS_PressRelease.aspx?fn=2757",
}
MAX_BYTES = 5_000_000


def fetch(url: str) -> tuple[bytes, str, int]:
    request = urllib.request.Request(url, headers={"User-Agent": "G6.3-public-source-evidence/1.0", "Accept": "text/html,*/*"})
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



class ArchiveForm(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active = False
        self.action = ""
        self.fields = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "form" and not self.action:
            self.active = True
            self.action = a.get("action", "")
        elif self.active and tag == "input":
            name = a.get("name", "")
            kind = (a.get("type", "text") or "text").lower()
            if name and kind in {"hidden", "text", "submit"}:
                self.fields.append((name, a.get("value", "")))

    def handle_endtag(self, tag):
        if tag == "form" and self.active:
            self.active = False


def capture_archive_month():
    url = "https://rbi.org.in/scripts/FS_PressRelease.aspx?fn=2757"
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    headers = {"User-Agent": "G6.3-public-source-evidence/1.0", "Accept": "text/html,*/*"}
    with opener.open(urllib.request.Request(url, headers=headers), timeout=30) as response:
        initial = response.read(MAX_BYTES + 1)
    if not initial or len(initial) > MAX_BYTES:
        raise RuntimeError("invalid RBI archive form response")
    form = ArchiveForm()
    form.feed(initial.decode("utf-8", errors="replace"))
    if not form.action or not any(k == "__VIEWSTATE" for k, _ in form.fields):
        raise RuntimeError("RBI archive standard form state missing")
    values = dict(form.fields)
    values.update({"hdnYear": "2025", "hdnMonth": "11", "ddlGSA": "0", "ddlRDSSGB": "0"})
    time.sleep(2)
    action = urllib.parse.urljoin(url, form.action)
    data = urllib.parse.urlencode(values).encode("ascii")
    request = urllib.request.Request(action, data=data, headers={**headers, "Content-Type": "application/x-www-form-urlencoded", "Referer": url}, method="POST")
    with opener.open(request, timeout=30) as response:
        body = response.read(MAX_BYTES + 1)
        content_type, status = response.headers.get("Content-Type", ""), response.status
    if status != 200 or not body or len(body) > MAX_BYTES or body == initial:
        raise RuntimeError("RBI archive month form failed or returned unfiltered page")
    name = "archive_month_202511.html"
    (OUT / name).write_bytes(body)
    return {"url": action, "method": "POST", "parameters": {"hdnYear": "2025", "hdnMonth": "11"}, "path": name, "http_status": status, "content_type": content_type, "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest()}

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {"schema_version": 1, "captured_at_utc": datetime.now(timezone.utc).isoformat(), "scope": "bounded official RBI source sample, archive index, and November 2025 archive form probe; not a historical series", "request_policy": "sequential; 2 seconds between requests; max 3 attempts for HTTP 429 only; 30-second timeout; 5 MB response cap", "sources": []}
    for index, (filename, url) in enumerate(SOURCES.items()):
        body, content_type, status = fetch(url)
        if status != 200 or not body:
            raise RuntimeError(f"invalid response: status={status}, bytes={len(body)}, url={url}")
        if filename.startswith("table218_"):
            normalized = body.lower().replace(b"-", b"").replace(b" ", b"")
            if b"table218" not in normalized or b"treasurybills" not in normalized:
                raise RuntimeError("RBI publication response did not identify Table 218 Treasury bills")
        (OUT / filename).write_bytes(body)
        manifest["sources"].append({"url": url, "path": filename, "http_status": status, "content_type": content_type, "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest()})
        if index + 1 < len(SOURCES):
            time.sleep(2)
    manifest["sources"].append(capture_archive_month())
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()