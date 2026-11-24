from __future__ import annotations

import calendar
import argparse
import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
URL = "https://www.rbi.org.in/scripts/HolidayMatrixDisplay.aspx?regoff=Mumbai"
USER_AGENT = "G6.3-public-source-evidence/1.0"
MAX_BYTES = 2_000_000
GAP_SECONDS = 2


class HolidayForm(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_form = False
        self.form_done = False
        self.action = ""
        self.fields: list[tuple[str, str]] = []
        self.select_name = ""
        self.select_values: dict[str, str] = {}
        self.option_value = ""
        self.option_selected = False
        self.option_text: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "form" and not self.form_done:
            self.in_form = True
            self.action = a.get("action", "") or ""
        elif self.in_form and tag == "input":
            name = a.get("name", "") or ""
            if name and (a.get("type", "").lower() == "hidden"):
                self.fields.append((name, a.get("value", "") or ""))
        elif self.in_form and tag == "select":
            self.select_name = a.get("name", "") or ""
        elif self.in_form and tag == "option" and self.select_name:
            self.option_value = a.get("value", "") or ""
            self.option_selected = "selected" in a
            self.option_text = []

    def handle_data(self, data):
        if self.option_value or self.option_selected:
            self.option_text.append(data)

    def handle_endtag(self, tag):
        if tag == "option" and self.select_name:
            if self.option_selected:
                self.select_values[self.select_name] = self.option_value
            self.option_value = ""
            self.option_selected = False
            self.option_text = []
        elif tag == "select":
            self.select_name = ""
        elif tag == "form" and self.in_form:
            self.in_form = False
            self.form_done = True


class Rows(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows: list[list[str]] = []
        self.row: list[str] | None = None
        self.cell: list[str] | None = None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.row = []
        elif tag in {"td", "th"} and self.row is not None:
            self.cell = []

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in {"td", "th"} and self.cell is not None and self.row is not None:
            self.row.append(" ".join(" ".join(self.cell).split()))
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.row = None


class Client:
    def __init__(self):
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
        self.last_request = 0.0

    def request(self, url: str, data: bytes | None = None, referer: str | None = None):
        for attempt in range(3):
            delay = GAP_SECONDS - (time.monotonic() - self.last_request)
            if delay > 0:
                time.sleep(delay)
            headers = {"User-Agent": USER_AGENT, "Accept": "text/html,*/*"}
            if data is not None:
                headers["Content-Type"] = "application/x-www-form-urlencoded"
            if referer:
                headers["Referer"] = referer
            req = urllib.request.Request(url, data=data, headers=headers, method="POST" if data is not None else "GET")
            try:
                with self.opener.open(req, timeout=30) as response:
                    self.last_request = time.monotonic()
                    body = response.read(MAX_BYTES + 1)
                    if len(body) > MAX_BYTES:
                        raise RuntimeError(f"holiday response exceeds {MAX_BYTES} bytes")
                    return body, response.status, response.headers.get("Content-Type", "")
            except urllib.error.HTTPError as exc:
                self.last_request = time.monotonic()
                if exc.code != 429 or attempt == 2:
                    raise
                time.sleep(min(max(int(exc.headers.get("Retry-After", "2")), 1), 60))
        raise RuntimeError("unreachable request state")


def month_url(year: int, month: int) -> str:
    return URL


def form_post(page: bytes, year: int, month: int) -> tuple[str, bytes]:
    parser = HolidayForm()
    parser.feed(page.decode("utf-8", errors="replace"))
    values = dict(parser.fields)
    values.update(parser.select_values)
    if not parser.action or "__VIEWSTATE" not in values:
        raise RuntimeError("RBI holiday matrix form state missing")
    if "drRegionalOffice" not in parser.select_values or "drMonth" not in parser.select_values or "drYear" not in parser.select_values:
        raise RuntimeError("RBI holiday matrix selectors missing")
    values.update({"drRegionalOffice": "28", "drMonth": str(month), "drYear": str(year), "btnGo": "GO"})
    action = urllib.parse.urljoin(URL, parser.action)
    return action, urllib.parse.urlencode(values).encode("ascii")


def parse_holidays(body: bytes, year: int, month: int) -> list[dict[str, str]]:
    page_text = " ".join(body.decode("utf-8", errors="replace").split()).casefold()
    parser = Rows()
    parser.feed(body.decode("utf-8", errors="replace"))
    header = f"{calendar.month_name[month]} {year}"
    no_holidays_message = f"there are no holidays in mumbai in {header}".casefold()
    if no_holidays_message in page_text:
        return []
    if not any(row and row[0] == header for row in parser.rows):
        raise RuntimeError(f"RBI holiday matrix header missing for {header}")
    if not any(row and row[0].casefold() == "mumbai" for row in parser.rows):
        raise RuntimeError(f"RBI holiday matrix does not show Mumbai for {header}")
    start = next((i for i, row in enumerate(parser.rows) if len(row) >= 2 and row[0].casefold() == "holiday description" and row[1].casefold() == "day"), None)
    if start is None:
        raise RuntimeError(f"RBI holiday description table missing for {header}")
    out = []
    for row in parser.rows[start + 1:]:
        if len(row) < 2:
            if out:
                break
            continue
        try:
            day = int(row[1])
        except ValueError:
            if out:
                break
            continue
        if not 1 <= day <= calendar.monthrange(year, month)[1]:
            raise RuntimeError(f"invalid holiday day {day} for {header}")
        out.append({"date": f"{year:04d}-{month:02d}-{day:02d}", "description": row[0]})
    if len({row["date"] for row in out}) != len(out):
        raise RuntimeError(f"duplicate holiday dates in {header}")
    return out


def main():
    parser = argparse.ArgumentParser(description="Capture official RBI Mumbai holiday-matrix months sequentially.")
    parser.add_argument("--start", default="2024-10", help="First month as YYYY-MM")
    parser.add_argument("--end", default="2026-09", help="Last month as YYYY-MM")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    try:
        start_year, start_month = map(int, args.start.split("-", 1))
        end_year, end_month = map(int, args.end.split("-", 1))
        start_date, end_date = datetime(start_year, start_month, 1), datetime(end_year, end_month, 1)
    except (ValueError, TypeError):
        parser.error("--start and --end must be valid YYYY-MM months")
    if start_date > end_date:
        parser.error("--start must be on or before --end")
    out = args.output_dir or (Path(__file__).resolve().parent / "rbi_mumbai_holidays_2024_2026")
    out.mkdir(parents=True, exist_ok=True)
    client = Client()
    initial_retrieved = datetime.now(timezone.utc).isoformat()
    page, status, content_type = client.request(URL)
    if status != 200 or not page:
        raise RuntimeError(f"RBI holiday initial GET failed: {status}")
    initial_name = "holiday_matrix_initial.html"
    (out / initial_name).write_bytes(page)
    records = [{
        "path": initial_name, "url": URL, "method": "GET", "parameters": {}, "http_status": status,
        "content_type": content_type, "retrieved_at_utc": initial_retrieved, "bytes": len(page), "sha256": hashlib.sha256(page).hexdigest(),
    }]
    parsed_months = []
    year, month = start_year, start_month
    while (year, month) <= (end_year, end_month):
        target_url, data = form_post(page, year, month)
        retrieved = datetime.now(timezone.utc).isoformat()
        body, status, content_type = client.request(target_url, data=data, referer=URL)
        if status != 200 or not body:
            raise RuntimeError(f"invalid RBI holiday response for {year}-{month:02d}: {status}")
        holidays = parse_holidays(body, year, month)
        name = f"mumbai_{year}_{month:02d}.html"
        (out / name).write_bytes(body)
        records.append({
            "path": name, "url": target_url, "method": "POST", "parameters": {"drRegionalOffice": "28", "drMonth": str(month), "drYear": str(year)},
            "http_status": status, "content_type": content_type, "retrieved_at_utc": retrieved, "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(),
        })
        parsed_months.append({"year": year, "month": month, "holiday_dates": holidays})
        if month == 12:
            year, month = year + 1, 1
        else:
            month += 1
        page = body
    manifest = {
        "schema_version": 1,
        "source_url": URL,
        "regional_office": "Mumbai",
        "regional_office_value": "28",
        "coverage": {"first_month": args.start, "last_month": args.end, "months": len(parsed_months)},
        "request_policy": "sequential; minimum 2 seconds between requests; max 3 attempts for HTTP 429 only; 30-second timeout; 2 MB response cap",
        "sources": records,
        "parsed_mumbai_holidays": parsed_months,
        "interpretation_limit": "Holiday dates are source inputs only. Business-day maturity adjustment must also use the governing RBI security terms and settlement calendar; do not infer investor settlement or market access from this matrix alone.",
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"result": "CAPTURED_RBI_MUMBAI_HOLIDAY_MATRIX", "months": len(parsed_months), "raw_sources": len(records), "holiday_date_count": sum(len(m["holiday_dates"]) for m in parsed_months), "first": parsed_months[0], "last": parsed_months[-1], "manifest": str(out / "manifest.json")}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
