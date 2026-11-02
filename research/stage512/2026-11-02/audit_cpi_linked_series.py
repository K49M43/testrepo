"""Independent structural and arithmetic audit of the staged linked CPI CSV.

This verifies the recorded transformation and derived rates. It does not
authenticate the CSV's transcribed source observations against government bytes.
"""

from __future__ import annotations

import csv
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


ROOT = Path(__file__).parent
SOURCE = ROOT / "stage512_cpi_official_linked_2013_2026.csv"
LINK_FACTOR = Decimal("0.5267")
FIVE_DP = Decimal("0.00001")
SIX_DP = Decimal("0.000001")


def rounded(value: Decimal, quantum: Decimal) -> Decimal:
    return value.quantize(quantum, rounding=ROUND_HALF_UP)


def audit() -> dict[str, object]:
    with SOURCE.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 165, f"expected 165 observations, got {len(rows)}"
    months = [row["month"] for row in rows]
    assert months[0] == "2013-01" and months[-1] == "2026-09"
    for previous, current in zip(months, months[1:]):
        py, pm = map(int, previous.split("-"))
        cy, cm = map(int, current.split("-"))
        assert cy * 12 + cm - (py * 12 + pm) == 1, f"gap or duplicate after {previous}"

    linked_count = direct_count = 0
    provisional_months: list[str] = []
    levels: list[Decimal] = []
    for i, row in enumerate(rows):
        level = Decimal(row["index_2024base"])
        levels.append(level)
        month = row["month"]
        if month <= "2024-12":
            old = Decimal(row["old_2012base"])
            assert rounded(old * LINK_FACTOR, FIVE_DP) == level, f"link-factor mismatch: {month}"
            assert row["source_label"] == "OFFICIAL_OLD_X_LINK_FACTOR"
            assert row["linking_url"], f"missing linkage source: {month}"
            linked_count += 1
        else:
            # The CSV retains the contemporaneous 2012-base figure in a
            # separate reference column, but direct 2024-base levels are used.
            assert row["source_label"] == "OFFICIAL_NEW_2024_BASE"
            assert not row["linking_url"], f"old-base linkage applied to new series: {month}"
            assert row["source_url"], f"missing direct-series source: {month}"
            direct_count += 1
        if row["provisional"].lower() == "true":
            provisional_months.append(month)
        if i == 0:
            assert not row["monthly_inflation_pct"] and not row["yoy_inflation_pct"]
            continue
        monthly = rounded((level / levels[i - 1] - 1) * 100, SIX_DP)
        assert rounded(Decimal(row["monthly_inflation_pct"]), SIX_DP) == monthly, f"monthly rate mismatch: {month}"
        if i >= 12:
            yoy = rounded((level / levels[i - 12] - 1) * 100, SIX_DP)
            assert rounded(Decimal(row["yoy_inflation_pct"]), SIX_DP) == yoy, f"YoY rate mismatch: {month}"

    assert linked_count == 144 and direct_count == 21
    assert provisional_months == ["2026-09"], f"unexpected provisional flags: {provisional_months}"
    return {
        "mechanical_audit": "PASS",
        "observation_count": len(rows),
        "coverage": [months[0], months[-1]],
        "linked_old_base_rows": linked_count,
        "direct_2024_base_rows": direct_count,
        "link_factor": str(LINK_FACTOR),
        "monthly_and_yoy_derivations": "PASS",
        "provisional_observations": provisional_months,
        "latest_observation": months[-1],
        "source_transcription_authentication": "OPEN — compare every staged source value with original official release bytes",
        "investor_base_month_alignment": "OPEN — actual cashflow dates/base month not confirmed",
        "real_wealth_qualification": "NOT QUALIFIED",
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
