"""Compare staged CPI levels with MoSPI/PIB September 2026 Annexure IV.

The comparison capture is a transcription of the official release's published
table, not a preserved PDF or original HTTP response bytes.
"""

from __future__ import annotations

import csv
import hashlib
import json
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).parent
STAGED = ROOT / "stage512_cpi_official_linked_2013_2026.csv"
CAPTURE = ROOT / "cpi_pib_sep2026_annexure_iv_capture.csv"
SOURCE = "https://www.pib.gov.in/PressReleasePage.aspx?PRID=2322244&lang=1&reg=3"


def main() -> None:
    with STAGED.open(encoding="utf-8-sig", newline="") as stream:
        staged = {row["month"]: row for row in csv.DictReader(stream)}
    with CAPTURE.open(encoding="utf-8-sig", newline="") as stream:
        official = list(csv.DictReader(stream))

    assert len(official) == 21, f"expected 21 months, got {len(official)}"
    months = [row["month"] for row in official]
    assert months[0] == "2025-01" and months[-1] == "2026-09"
    assert len(set(months)) == len(months)

    mismatches = []
    for row in official:
        month = row["month"]
        actual = staged[month]
        if Decimal(actual["index_2024base"]) != Decimal(row["index_2024base_combined_displayed"]):
            mismatches.append((month, actual["index_2024base"], row["index_2024base_combined_displayed"]))
        if actual["provisional"].lower() != row["provisional"].lower():
            mismatches.append((month, actual["provisional"], row["provisional"]))
        if actual["source_url"] != SOURCE:
            mismatches.append((month, actual["source_url"], SOURCE))

    result = {
        "audit": "PASS" if not mismatches else "FAIL",
        "capture_date": "2026-11-03",
        "capture_method": "manual transcription from official PIB September 2026 CPI release, Annexure IV, All India Combined index column",
        "source_url": SOURCE,
        "capture_sha256": hashlib.sha256(CAPTURE.read_bytes()).hexdigest(),
        "months_compared": len(official),
        "coverage": [months[0], months[-1]],
        "level_and_provisional_flags_compared": True,
        "mismatches": mismatches,
        "raw_source_bytes_preserved": False,
        "source_qualification": "Observation mapping and published-value reconciliation PASS; original release bytes are not preserved in this capture",
    }
    print(json.dumps(result, indent=2))
    if mismatches:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
