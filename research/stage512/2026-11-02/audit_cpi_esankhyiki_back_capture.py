"""Compare staged linked CPI with values visible in MoSPI's public portal.

The captured source is a UI transcription of the official e-Sankhyiki table,
not a preserved download or original response-byte artifact. This audit
therefore validates displayed values and precision only; it does not qualify
the full CPI source vintage.
"""

from __future__ import annotations

import csv
import hashlib
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


ROOT = Path(__file__).parent
STAGED = ROOT / "stage512_cpi_official_linked_2013_2026.csv"
CAPTURE = ROOT / "cpi_mospi_esankhyiki_back_combined_ui_capture.csv"
QUANTUM = Decimal("0.1")


def main() -> None:
    with STAGED.open(encoding="utf-8-sig", newline="") as stream:
        staged = {r["month"]: Decimal(r["index_2024base"]) for r in csv.DictReader(stream)}
    with CAPTURE.open(encoding="utf-8-sig", newline="") as stream:
        official = list(csv.DictReader(stream))

    assert len(official) == 144, f"expected 144 captured months, got {len(official)}"
    months = [r["month"] for r in official]
    assert months[0] == "2013-01" and months[-1] == "2024-12"
    assert len(set(months)) == 144

    differences: list[tuple[str, str, str, str]] = []
    for row in official:
        month = row["month"]
        displayed = Decimal(row["index_2024base_displayed"])
        candidate = staged[month].quantize(QUANTUM, rounding=ROUND_HALF_UP)
        official_display = displayed.quantize(QUANTUM, rounding=ROUND_HALF_UP)
        if official_display != candidate:
            differences.append((month, str(staged[month]), str(displayed), str(candidate)))

    result = {
        "audit": "PASS" if not differences else "FAIL",
        "capture_date": "2026-11-03",
        "capture_method": "manual transcription from MoSPI e-Sankhyiki visible table, base 2024, Back, All India, Combined, CPI (General)",
        "source_page": "https://esankhyiki.mospi.gov.in/macroindicators?product=cpi",
        "capture_sha256": hashlib.sha256(CAPTURE.read_bytes()).hexdigest(),
        "months_compared": len(official),
        "coverage": [months[0], months[-1]],
        "precision_check": "staged old-base × 0.5267 values rounded to one decimal compared with one-decimal values shown with two trailing display digits on the portal",
        "mismatches": differences,
        "raw_source_bytes_preserved": False,
        "source_qualification": "2013-01 to 2024-12 source-value cross-check PASS at published input precision; original downloaded official file or response bytes are not preserved",
        "investor_base_month_alignment": "OPEN",
        "authorization": "NO-GO",
    }
    print(json.dumps(result, indent=2))
    if differences:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
