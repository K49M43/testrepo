from __future__ import annotations

import csv
import argparse
import hashlib
import http.cookiejar
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TABLE218 = ROOT / "research/stage512/2026-11-06/g6_3/source_raw/rbi_tbill_sample/table218_20260731.html"
OUT = Path("rbi_tbill_window_capture")
ARCHIVE_URL = "https://rbi.org.in/scripts/FS_PressRelease.aspx?fn=2757"
USER_AGENT = "G6.3-public-source-evidence/1.0"
MAX_BYTES = 5_000_000
REQUEST_GAP_SECONDS = 2


class TableRows(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[list[str]] = []
        self.row: list[str] | None = None
        self.cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag == "tr":
            self.row = []
        elif tag in {"td", "th"} and self.row is not None:
            self.cell = []

    def handle_data(self, data: str) -> None:
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"td", "th"} and self.cell is not None and self.row is not None:
            self.row.append(re.sub(r"\s+", " ", " ".join(self.cell)).strip())
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.row = None


class PlainText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"script", "style"}:
            self.skip += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self.skip:
            self.skip -= 1

    def handle_data(self, data: str) -> None:
        if not self.skip:
            self.parts.append(data)


def visible_text(body: bytes) -> str:
    parser = PlainText()
    parser.feed(body.decode("utf-8", errors="replace"))
    return re.sub(r"\s+", " ", " ".join(parser.parts)).casefold()


def parse_table218(
    body: bytes,
    expected_count: int = 50,
    first_date: str = "2025-07-02",
    last_date: str = "2026-06-24",
) -> dict[str, dict[str, str]]:
    parser = TableRows()
    parser.feed(body.decode("utf-8", errors="replace"))
    panel: dict[str, dict[str, str]] = {}
    for row in parser.rows:
        if len(row) < 12 or not re.fullmatch(r"\d{1,2}-[A-Za-z]{3}-\d{4}", row[0]):
            continue
        auction = datetime.strptime(row[0], "%d-%b-%Y").date()
        issue = datetime.strptime(row[1], "%d-%b-%Y").date()
        panel[auction.isoformat()] = {
            "auction_date": auction.isoformat(), "issue_date": issue.isoformat(),
            "notified_amount_crore": row[2].replace(",", ""),
            "total_issue_crore": row[-3].replace(",", ""),
            "cutoff_price": row[-2], "cutoff_yield_actual_365_pct": row[-1],
        }
    if len(panel) != expected_count:
        raise RuntimeError(f"expected {expected_count} dated table rows, found {len(panel)}")
    if min(panel) != first_date or max(panel) != last_date:
        raise RuntimeError(f"unexpected Table 218 coverage: {min(panel)} to {max(panel)}")
    return panel


class ArchiveForm(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.active = False
        self.done = False
        self.action = ""
        self.fields: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        a = dict(attrs)
        if tag == "form" and not self.done:
            self.active = True
            self.action = a.get("action", "") or ""
        elif self.active and tag == "input":
            name = a.get("name", "") or ""
            kind = (a.get("type", "text") or "text").lower()
            if name and kind in {"hidden", "text", "submit"}:
                self.fields.append((name, a.get("value", "") or ""))

    def handle_endtag(self, tag: str) -> None:
        if tag == "form" and self.active:
            self.active = False
            self.done = True


class Client:
    def __init__(self) -> None:
        jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
        self.last_request = 0.0

    def request(self, url: str, data: bytes | None = None, referer: str | None = None) -> tuple[bytes, str, int]:
        headers = {"User-Agent": USER_AGENT, "Accept": "text/html,*/*"}
        if data is not None:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        if referer:
            headers["Referer"] = referer
        for attempt in range(3):
            wait = REQUEST_GAP_SECONDS - (time.monotonic() - self.last_request)
            if wait > 0:
                time.sleep(wait)
            req = urllib.request.Request(url, data=data, headers=headers, method="POST" if data is not None else "GET")
            try:
                with self.opener.open(req, timeout=30) as response:
                    self.last_request = time.monotonic()
                    body = response.read(MAX_BYTES + 1)
                    if len(body) > MAX_BYTES:
                        raise RuntimeError(f"response exceeds {MAX_BYTES} byte cap: {url}")
                    return body, response.headers.get("Content-Type", ""), response.status
            except urllib.error.HTTPError as exc:
                self.last_request = time.monotonic()
                if exc.code != 429 or attempt == 2:
                    raise
                retry = min(int(exc.headers.get("Retry-After", "2")), 60)
                time.sleep(max(retry, 1))
        raise RuntimeError(f"unreachable request state: {url}")


def capture_month(client: Client, page: bytes, year: int, month: int) -> bytes:
    form = ArchiveForm()
    form.feed(page.decode("utf-8", errors="replace"))
    if not form.action or not any(k == "__VIEWSTATE" for k, _ in form.fields):
        raise RuntimeError("RBI archive standard form state missing")
    values = dict(form.fields)
    values.update({"hdnYear": str(year), "hdnMonth": str(month), "ddlGSA": "0", "ddlRDSSGB": "0"})
    action = urllib.parse.urljoin(ARCHIVE_URL, form.action)
    data = urllib.parse.urlencode(values).encode("ascii")
    body, _, status = client.request(action, data=data, referer=ARCHIVE_URL)
    if status != 200 or not body or body == page:
        raise RuntimeError(f"RBI archive form did not return a filtered page for {year}-{month:02d}")
    return body


def is_tbill_notice_title(title: str) -> bool:
    lower = title.casefold()
    return (
        "result" not in lower
        and "auction" in lower
        and ("treasury bills" in lower or "t-bill" in lower)
        and re.search(r"\b91\s*[- ]?\s*days?\b", lower) is not None
    )


def archive_items(body: bytes) -> list[dict[str, str]]:
    text = body.decode("utf-8", errors="replace")
    heads = list(re.finditer(r"(?is)<th\b[^>]*>\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4})\s*</th>", text))
    items: list[dict[str, str]] = []
    for i, head in enumerate(heads):
        block = text[head.end():heads[i + 1].start() if i + 1 < len(heads) else len(text)]
        day = datetime.strptime(head.group(1), "%b %d, %Y").date().isoformat()
        for a in re.finditer(r"(?is)<a\b[^>]*href\s*=\s*[\"']?([^\"' >]+)[\"']?[^>]*>(.*?)</a>", block):
            title = re.sub(r"<[^>]+>", " ", a.group(2))
            title = re.sub(r"\s+", " ", unescape(title)).strip()
            lower = title.casefold()
            if "full auction result" not in lower and not is_tbill_notice_title(lower):
                continue
            parsed = urllib.parse.parse_qs(urllib.parse.urlparse(a.group(1)).query)
            prid = parsed.get("prid", [""])[0]
            if prid:
                items.append({"archive_date": day, "title": title, "prid": prid, "url": urllib.parse.urljoin(ARCHIVE_URL, a.group(1))})
    return items


def source_record(path: str, url: str, method: str, body: bytes, content_type: str, **extra) -> dict:
    return {"path": path, "url": url, "method": method, "http_status": 200, "content_type": content_type, "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(), **extra}


def notice_data(body: bytes) -> dict[str, str]:
    parser = TableRows()
    parser.feed(body.decode("utf-8", errors="replace"))
    row = next((r for r in parser.rows if len(r) >= 5 and r[0] == "1" and re.sub(r"[^a-z0-9]", "", r[1].casefold()) in {"91day", "91days"}), None)
    if row is None:
        raise RuntimeError("91-Day row missing from auction notice")
    auction_match = re.search(r"([A-Za-z]+\s+\d{1,2},\s+\d{4})", row[3])
    issue_match = re.search(r"([A-Za-z]+\s+\d{1,2},\s+\d{4})", row[4])
    if not auction_match or not issue_match:
        raise RuntimeError("auction/settlement date missing from notice row")
    auction = datetime.strptime(auction_match.group(1), "%B %d, %Y").date().isoformat()
    issue = datetime.strptime(issue_match.group(1), "%B %d, %Y").date().isoformat()
    text = visible_text(body)
    # Some archived RBI notices split the final word across an inline span
    # boundary (for example, ``metho</span>d``). ``visible_text`` separates
    # text nodes with spaces, so allow that single-word split and normalize the
    # method back to its canonical wording before storing it.
    method_match = re.search(r"(price|yield) based using ([a-z -]+?) metho\s*d", text)
    if not method_match:
        raise RuntimeError("auction method missing from notice")
    release = re.search(r"date\s*:\s*([a-z]{3}\s+\d{1,2},\s+\d{4})", text)
    method = f"{method_match.group(1)} based using {method_match.group(2).strip()} method"
    return {"auction_date": auction, "issue_date": issue, "notified_amount_crore": row[2].replace(",", ""), "auction_method": method, "notice_date": datetime.strptime(release.group(1).title(), "%b %d, %Y").date().isoformat() if release else "", "retail_route": str("retail investors" in text or "individual investors" in text)}


def result_data(body: bytes) -> dict[str, str]:
    text = visible_text(body)
    release = re.search(r"date\s*:\s*([a-z]{3}\s+\d{1,2},\s+\d{4})", text)
    if not release:
        raise RuntimeError("result publication date missing")
    result_date = datetime.strptime(release.group(1).title(), "%b %d, %Y").date().isoformat()
    rows = TableRows()
    rows.feed(body.decode("utf-8", errors="replace"))
    cutoff: list[tuple[str, str]] = []
    weighted: list[tuple[str, str]] = []
    for index, row in enumerate(rows.rows[:-1]):
        label = " ".join(row).casefold()
        target = cutoff if "cut-off price" in label and "yield" in label else weighted if "weighted average price" in label and "yield" in label else None
        if target is None:
            continue
        price_cells = row[-3:]
        yield_cells = rows.rows[index + 1][-3:]
        for price_cell, yield_cell in zip(price_cells, yield_cells):
            price_match = re.search(r"(?<![\d.])[\d]+\.[\d]{1,4}(?![\d.])", price_cell)
            yield_match = re.search(r"([\d.]+)%", yield_cell)
            target.append((price_match.group(0) if price_match else "", yield_match.group(1) if yield_match else ""))
    out = {"result_date": result_date}
    for tenor, slot in (("91", 0), ("182", 1), ("364", 2)):
        if len(cutoff) > slot:
            if cutoff[slot][0]: out[f"cutoff_price_{tenor}"] = cutoff[slot][0]
            if cutoff[slot][1]: out[f"cutoff_yield_{tenor}"] = cutoff[slot][1]
        if len(weighted) > slot:
            if weighted[slot][0]: out[f"weighted_price_{tenor}"] = weighted[slot][0]
            if weighted[slot][1]: out[f"weighted_yield_{tenor}"] = weighted[slot][1]
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture and reconcile an official RBI 91-day T-bill auction window.")
    parser.add_argument("--table-path", type=Path, default=TABLE218)
    parser.add_argument("--table-url")
    parser.add_argument("--output-dir", type=Path, default=OUT)
    parser.add_argument("--table-name", default="Table 218")
    parser.add_argument("--window-tag", default="2025_2026")
    parser.add_argument("--expected-auctions", type=int, default=50)
    parser.add_argument("--first-date", default="2025-07-02")
    parser.add_argument("--last-date", default="2026-06-24")
    args = parser.parse_args()
    table_path = args.table_path.resolve()
    out = args.output_dir
    client = Client()
    table_http = None
    if args.table_url:
        retrieved_at_utc = datetime.now(timezone.utc).isoformat()
        table_bytes, table_content_type, table_status = client.request(args.table_url)
        if table_status != 200 or not table_bytes:
            raise RuntimeError(f"invalid {args.table_name} source response: {table_status}")
        table_path.parent.mkdir(parents=True, exist_ok=True)
        table_path.write_bytes(table_bytes)
        table_http = {"url": args.table_url, "method": "GET", "http_status": table_status, "content_type": table_content_type, "retrieved_at_utc": retrieved_at_utc}
    if not table_path.is_file():
        raise RuntimeError(f"authoritative {args.table_name} bytes missing: {table_path}")
    table_bytes = table_path.read_bytes()
    expected = parse_table218(table_bytes, args.expected_auctions, args.first_date, args.last_date)
    out.mkdir(parents=True, exist_ok=True)
    (out / "archive").mkdir(exist_ok=True)
    (out / "notices").mkdir(exist_ok=True)
    (out / "results").mkdir(exist_ok=True)
    body, content_type, status = client.request(ARCHIVE_URL)
    if status != 200 or not body:
        raise RuntimeError("RBI archive initial form GET failed")
    index_path = out / "archive_index.html"
    index_path.write_bytes(body)
    records: list[dict] = [source_record("archive_index.html", ARCHIVE_URL, "GET", body, content_type)]
    months: set[tuple[int, int]] = set()
    dates = [date.fromisoformat(d) for d in expected]
    first = min(dates).replace(day=1) - timedelta(days=1)
    first = first.replace(day=1)
    last = max(dates).replace(day=1)
    cursor = first
    while cursor <= last:
        months.add((cursor.year, cursor.month))
        cursor = (cursor.replace(day=28) + timedelta(days=4)).replace(day=1)
    for idx, (year, month) in enumerate(sorted(months)):
        if idx:
            pass
        body = capture_month(client, body, year, month)
        name = f"archive_{year}_{month:02d}.html"
        (out / "archive" / name).write_bytes(body)
        records.append(source_record(f"archive/{name}", ARCHIVE_URL, "POST", body, "text/html", parameters={"hdnYear": str(year), "hdnMonth": str(month)}))
    all_items: list[dict[str, str]] = []
    for path in sorted((out / "archive").glob("archive_*.html")):
        all_items.extend(archive_items(path.read_bytes()))
    notice_start = min(dates) - timedelta(days=7)
    notice_end = max(dates)
    notices = {
        x["prid"]: x
        for x in all_items
        if is_tbill_notice_title(x["title"])
        and notice_start.isoformat() <= x["archive_date"] <= notice_end.isoformat()
    }
    result_links = {x["prid"]: x for x in all_items if "full auction result" in x["title"].casefold() and x["archive_date"] in expected}
    if len(result_links) < 45:
        raise RuntimeError(f"too few full result links in Table 218 period: {len(result_links)}")
    notice_by_date: dict[str, list[dict[str, str]]] = {}
    for prid, item in notices.items():
        url = item["url"]
        body, ctype, status = client.request(url)
        if status != 200 or not body:
            raise RuntimeError(f"invalid notice response {prid}: {status}")
        name = f"notice_prid{prid}.html"
        (out / "notices" / name).write_bytes(body)
        records.append(source_record(f"notices/{name}", url, "GET", body, ctype))
        detail = notice_data(body)
        if detail["auction_date"] in expected:
            detail.update({"prid": prid, "path": f"notices/{name}", "url": url})
            notice_by_date.setdefault(detail["auction_date"], []).append(detail)
    result_by_date: dict[str, dict[str, str]] = {}
    for prid, item in result_links.items():
        body, ctype, status = client.request(item["url"])
        if status != 200 or not body:
            raise RuntimeError(f"invalid full result response {prid}: {status}")
        name = f"full_result_prid{prid}.html"
        (out / "results" / name).write_bytes(body)
        records.append(source_record(f"results/{name}", item["url"], "GET", body, ctype))
        detail = result_data(body)
        if detail["result_date"] != item["archive_date"]:
            raise RuntimeError(f"archive/result date mismatch for {prid}: {item['archive_date']} vs {detail['result_date']}")
        detail.update({"prid": prid, "path": f"results/{name}", "url": item["url"]})
        if detail["result_date"] in result_by_date:
            raise RuntimeError(f"duplicate full results for {detail['result_date']}")
        result_by_date[detail["result_date"]] = detail
    output_rows = []
    exceptions = []
    issue_date_conflicts = []
    for auction_date, t218 in sorted(expected.items()):
        candidates = notice_by_date.get(auction_date, [])
        if len(candidates) != 1:
            raise RuntimeError(f"expected exactly one contemporaneous notice for {auction_date}, found {len(candidates)}")
        notice = candidates[0]
        if notice["notified_amount_crore"] != t218["notified_amount_crore"]:
            raise RuntimeError(f"notice/{args.table_name} notified amount mismatch for {auction_date}")
        if notice["issue_date"] != t218["issue_date"]:
            issue_date_conflicts.append({
                "auction_date": auction_date,
                "table_issue_date": t218["issue_date"],
                "notice_issue_date": notice["issue_date"],
                "resolution": "RETAIN_BOTH; USE_CONTEMPORANEOUS_AUCTION_NOTICE_FOR_ACTUAL_ISSUE_DATE",
            })
        total_issue = t218["total_issue_crore"].replace("-", "0")
        result = result_by_date.get(auction_date)
        row = {
            **t218,
            "table_issue_date": t218["issue_date"],
            "issue_date": notice["issue_date"],
            "issue_date_resolution": "NOTICE_AND_TABLE_AGREE" if notice["issue_date"] == t218["issue_date"] else "NOTICE_OVERRIDES_TABLE_DATE_CONFLICT",
            "notice_prid": notice["prid"], "notice_date": notice["notice_date"],
            "auction_method": notice["auction_method"], "retail_route_stated": notice["retail_route"],
            "notice_path": notice["path"], "result_status": "MATCHED" if result else "NO_RESULT_PAGE",
        }
        if total_issue in {"0", "0.00"}:
            row["result_status"] = "ZERO_ISSUE_EXCEPTION"
            if result and result.get("weighted_price_91"):
                raise RuntimeError(f"Table 218 zero-issue exception has positive weighted result for {auction_date}")
            exceptions.append({"auction_date": auction_date, "status": "ZERO_ISSUE_EXCEPTION", "reason": f"{args.table_name} reports zero 91-day total issue and no investable 91-day price/yield."})
        else:
            if not result:
                raise RuntimeError(f"missing full result for positive-issue auction {auction_date}")
            if result.get("result_date") != auction_date:
                raise RuntimeError(f"result date mismatch for {auction_date}")
            if result.get("cutoff_yield_91") != t218["cutoff_yield_actual_365_pct"]:
                raise RuntimeError(f"91-day cutoff yield mismatch against Table 218 for {auction_date}")
            row.update({k: v for k, v in result.items() if k.startswith("weighted_") or k.startswith("cutoff_")})
            result_price = result.get("cutoff_price_91")
            if result_price and Decimal(result_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) != Decimal(t218["cutoff_price"]):
                raise RuntimeError(f"91-day cutoff price rounding mismatch against Table 218 for {auction_date}")
            row["result_path"] = result["path"]
            row["result_prid"] = result["prid"]
        output_rows.append(row)
    fields = sorted({key for row in output_rows for key in row})
    panel_name = f"auction_panel_{args.window_tag}.csv"
    with (out / panel_name).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(output_rows)
    table_reference = {"path": table_path.relative_to(ROOT).as_posix(), "bytes": len(table_bytes), "sha256": hashlib.sha256(table_bytes).hexdigest()}
    if table_http:
        table_reference.update(table_http)
    manifest = {
        "schema_version": 1,
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": f"official RBI T-bill notice/full-result pairs for {args.expected_auctions} rows in {args.table_name} ({args.first_date} through {args.last_date}); table/notice issue-date conflicts retain both source values and use the contemporaneous auction notice for the normalized issue date; auction-yield levels only, not a calibrated risk history",
        "request_policy": "sequential; minimum 2 seconds between requests; max 3 attempts for HTTP 429 only; 30-second timeout; 5 MB body cap",
        "reference_table": args.table_name,
        "table_reference": table_reference,
        "window": {"first_date": args.first_date, "last_date": args.last_date},
        "expected_auctions": len(expected), "matched_notice_dates": len(notice_by_date), "matched_full_result_dates": len(result_by_date),
        "exceptions": exceptions,
        "source_discrepancies": {"issue_date_conflicts": issue_date_conflicts},
        "sources": records,
    }
    if args.table_name == "Table 218":
        manifest["table218_reference"] = manifest["table_reference"]
    elif args.table_name == "Table 217":
        manifest["table217_reference"] = manifest["table_reference"]
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"result": "CAPTURED_RBI_TBILL_WINDOW", "reference_table": args.table_name, "expected_auctions": len(expected), "notices": len(notice_by_date), "full_results": len(result_by_date), "exceptions": exceptions, "manifest_sources": len(records), "csv": str(out / panel_name)}, indent=2))


if __name__ == "__main__":
    main()
