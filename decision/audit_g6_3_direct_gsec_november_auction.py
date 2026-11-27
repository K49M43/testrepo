"""Reconcile the second dated 6.94% GS 2036 primary-auction anchor."""
from __future__ import annotations

import argparse
import json
import re
from datetime import date, timedelta
from decimal import Decimal, localcontext

from audit_g6_3_direct_gsec_2036 import (
    CASHFLOW_PATH, PAIR_PATH, ROOT, date_30_360, load_json, require, verify_hash,
)
from audit_g6_3_rbi_tbill_window import Rows, visible


EVIDENCE = ROOT / "research/g6_3/direct_gsec_2036/2026-11-13"
OUT = EVIDENCE / "auction_reconciliation_v1.json"
D = Decimal
CENT = D("0.01")
SECURITY = "6.94% GS 2036"
ISIN = "IN0020260025"
AUCTION = date(2026, 11, 13)
SETTLEMENT = date(2026, 11, 16)
LOT = D(10_000)
SOURCE_NAMES = {
    "rbi_auction_notice.html", "rbi_cutoff_result.html", "rbi_auction_result.html",
    "rbi_outstanding_2026_11_23.html",
}


def row_index(rows, key, column=0):
    matches = [i for i, row in enumerate(rows) if len(row) > column and row[column] == key]
    require(len(matches) == 1, f"expected one source row for {key!r}")
    return matches[0]


def amount(value):
    return D(value.replace(",", ""))


def verify_sources():
    receipts = load_json(EVIDENCE / "source_receipts.json")
    require(set(receipts) == SOURCE_NAMES, "unexpected archived RBI source names")
    bodies, tables = {}, {}
    for name, record in receipts.items():
        file = EVIDENCE / name
        require(record["http_status"] == 200 and record["content_type"] == "text/html"
                and record["retained"] is True, f"invalid receipt for {name}")
        verify_hash(file, record["bytes"], record["sha256"])
        body = file.read_bytes()
        rows = Rows()
        rows.feed(body.decode("utf-8"))
        bodies[name], tables[name] = visible(body), rows.rows

    notice = tables["rbi_auction_notice.html"]
    i = row_index(notice, SECURITY, column=1)
    require(notice[i][2:4] == ["May 11, 2036", "34,000"], "notice maturity or face amount mismatch")
    require(notice[i][5:] == ["November 13, 2026 (Friday)", "November 16, 2026 (Monday)"],
            "unexpected auction or issue date")
    rules = bodies["rbi_auction_notice.html"]
    require(all(text in rules for text in ("multiple price method", "weighted average rate of yield/price",
                                          "10,000/- (nominal)")), "NCB method or lot size mismatch")

    full = tables["rbi_auction_result.html"]
    require(full[row_index(full, "Auction Results")][1] == SECURITY, "security in full result differs")
    require("nov 13, 2026" in bodies["rbi_auction_result.html"], "full result date mismatch")
    i = row_index(full, "Notified Amount", column=1)
    notified = amount(full[i][2])
    i = row_index(full, "Competitive Bids Accepted", column=1)
    competitive = amount(full[i + 2][1])
    i = row_index(full, "Non-Competitive Bids Accepted", column=1)
    accepted_bids, accepted = int(full[i + 1][1]), amount(full[i + 2][1])
    i = row_index(full, "Non-Competitive Bids Received", column=1)
    require((accepted_bids, accepted) == (int(full[i + 1][1]), amount(full[i + 2][1])),
            "noncompetitive aggregate acceptance differs from received bids")
    require(notified == 34_000 and competitive + accepted == notified, "accepted face amounts differ")

    quotes = {}
    for name, label, yield_label in (("cutoff", "Cut-off price", "YTM"),
                                     ("weighted_average", "Weighted Average Price", "WAY")):
        indices = [i for i, row in enumerate(full) if len(row) == 3 and row[1].startswith(label)]
        require(len(indices) == 1, f"ambiguous {name} label")
        i = indices[0]
        match = re.fullmatch(rf"\({yield_label}: (\d+\.\d+)%\)", full[i + 1][0])
        require(match is not None, f"unrecognized {name} yield")
        quotes[name] = {"price_per_100": full[i][2], "nominal_ytm_percent": match[1]}
    short = tables["rbi_cutoff_result.html"]
    require(short[row_index(short, SECURITY, column=2)][2] == SECURITY
            and "nov 13, 2026" in bodies["rbi_cutoff_result.html"], "abridged cutoff identity differs")
    i = row_index(short, "II.")
    cutoff = quotes["cutoff"]
    require(short[i][2] == f"{cutoff['price_per_100']}/{cutoff['nominal_ytm_percent']}%",
            "abridged and full result prices/yields differ")

    securities = tables["rbi_outstanding_2026_11_23.html"]
    i = row_index(securities, ISIN, column=1)
    require(securities[i][2:5] == [SECURITY, "11-May-2026", "11-May-2036"]
            and "november 23, 2026" in bodies["rbi_outstanding_2026_11_23.html"],
            "outstanding security anchor does not match identity and dates")
    return quotes, {"notified_crore": str(notified), "competitive_accepted_crore": str(competitive),
                    "noncompetitive_accepted_crore": str(accepted), "noncompetitive_bids": accepted_bids}


def price_check(quotes):
    contract = load_json(CASHFLOW_PATH)
    require(contract["isin"] == ISIN, "wrong contractual cashflow source")
    events = [(date.fromisoformat(row["nominal_coupon_date"]),
               D(row["coupon_per_100_face_inr"]) + D(row["redemption_per_100_face_inr"]))
              for row in contract["coupon_events"]]
    previous = max(day for day, _ in events if day < SETTLEMENT)
    remaining = [(day, value) for day, value in events if day > SETTLEMENT]
    require(len(remaining) == 19 and remaining[0][0] == date(2027, 5, 11)
            and remaining[-1] == (date(2036, 5, 11), D("103.47")), "cashflow refresh mismatch")
    coupon = D(contract["coupon_rate_percent_per_annum"])
    cutoff = SETTLEMENT - timedelta(days=1)
    alternatives = {
        "last_scheduled_coupon_to_cutoff_date": date_30_360(previous, cutoff),
        "last_scheduled_coupon_to_settlement_date": date_30_360(previous, SETTLEMENT),
        "original_issue_to_cutoff_date_sensitivity": date_30_360(date(2026, 5, 11), cutoff),
    }
    matrix = {}
    for convention, days in alternatives.items():
        accrued = coupon * days / 360
        price_projection = {}
        for name, row in quotes.items():
            semiannual_yield = D(row["nominal_ytm_percent"]) / 200
            pv = sum(value / (1 + semiannual_yield) ** (D(date_30_360(SETTLEMENT, day)) / 180)
                     for day, value in remaining)
            price_projection[name] = str((pv - accrued).quantize(CENT))
        published = {name: row["price_per_100"] for name, row in quotes.items()}
        matrix[convention] = {
            "days_30_360": days,
            "projected_clean_price_rounded_per_100": price_projection,
            "matches_both_published_prices": price_projection == published,
            "hypothetical_debit_for_10000_face_before_fees_inr": str(
                ((D(quotes["weighted_average"]["price_per_100"]) + accrued) * LOT / 100).quantize(CENT)),
        }
    require([key for key, row in matrix.items() if row["matches_both_published_prices"]]
            == ["last_scheduled_coupon_to_settlement_date"], "unexpected quote reconciliation")
    return {
        "last_scheduled_coupon_date": previous.isoformat(), "due_through_date_in_gazette": cutoff.isoformat(),
        "gazette_last_coupon_cell": "New Security", "confirm_final_retail_debit": False,
        "nominal_coupon_count_after_settlement": len(remaining),
        "next_nominal_coupon_date": remaining[0][0].isoformat(),
        "nominal_maturity_date": remaining[-1][0].isoformat(),
        "alternatives": matrix,
    }


def build_record():
    quotes, allotment = verify_sources()
    october = load_json(PAIR_PATH)["auction_result_values"]
    previous_price = D(october["competitive_weighted_average_clean_price_per_100"])
    previous_yield = D(october["competitive_weighted_average_yield_percent"])
    return {
        "record_id": "G6.3-DIRECT-GSEC-NOVEMBER-2026-AUCTION-v1",
        "status": "HISTORICAL_PRIMARY_PRICE_ANCHOR_PASS_RETAIL_DEBIT_AND_SECONDARY_QUOTE_OPEN",
        "isin": ISIN, "auction_date": AUCTION.isoformat(), "settlement_date": SETTLEMENT.isoformat(),
        "notice_and_result_allotment": allotment, "primary_quotes": quotes,
        "change_from_october_weighted_price_per_100": str(D(quotes["weighted_average"]["price_per_100"]) - previous_price),
        "change_from_october_weighted_nominal_ytm_bps": str(
            (D(quotes["weighted_average"]["nominal_ytm_percent"]) - previous_yield) * 100),
        "price_and_accrual_diagnostic": price_check(quotes),
        "secondary_retail_quote_verified": False,
        "investment_authorization": "NO_GO",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    with localcontext() as ctx:
        ctx.prec = 40
        payload = json.dumps(build_record(), indent=2) + "\n"
    if args.check:
        require(OUT.read_text(encoding="utf-8") == payload, "frozen November reconciliation differs")
    else:
        OUT.write_text(payload, encoding="utf-8", newline="\n")
    print("PASS: November primary-auction anchor, arithmetic and declared execution limits. NO_GO.")


if __name__ == "__main__":
    main()
