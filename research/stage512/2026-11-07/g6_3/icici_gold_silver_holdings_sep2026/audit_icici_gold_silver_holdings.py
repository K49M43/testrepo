from __future__ import annotations

import hashlib
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parent
AS_OF = "Portfolio as on Sep 30,2026"
FILES = {
    "gold": ("ICICI Prudential Gold ETF.xlsx", "GOLD", "Gold", "Gold (995 Purity) ^"),
    "silver": ("ICICI PRUDENTIAL SILVER ETF.xlsx", "SILVER", "Silver", "Silver ^"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dec(value) -> Decimal:
    return Decimal(str(value))


def as_pct(value: Decimal) -> str:
    return str((value * Decimal(100)).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP))


def read_rows(path: Path, sheet_name: str):
    book = load_workbook(path, data_only=True, read_only=True)
    assert book.sheetnames == [sheet_name], (path.name, book.sheetnames)
    ws = book[sheet_name]
    assert ws["B3"].value == AS_OF, (path.name, ws["B3"].value)
    rows = {}
    footnotes = []
    for row in ws.iter_rows(values_only=True):
        label = row[1]
        if label is not None:
            label = str(label).strip()
            rows[label] = row
            if label.startswith("^"):
                footnotes.append(label)
    return rows, footnotes


results = {}
for metal, (filename, sheet, rollup_label, physical_label) in FILES.items():
    path = ROOT / filename
    rows, footnotes = read_rows(path, sheet)
    rollup = rows[rollup_label]
    physical = rows[physical_label]
    treps = rows["TREPS"]
    nca = rows["Net Current Assets"]
    total = rows["Total Net Assets"]

    rollup_value = dec(rollup[5])
    physical_value = dec(physical[5])
    physical_weight = dec(physical[6])
    treps_value = dec(treps[5])
    total_value = dec(total[5])
    nca_value = dec(nca[5])
    reported_treps_weight = treps[6]
    treps_weight = treps_value / total_value
    nca_weight = dec(nca[6])

    # The workbook's first metal row is a roll-up repeated by the detailed physical holding.
    # Count the detailed holding only; never add both rows together.
    assert abs(rollup_value - physical_value) < Decimal("0.000001"), filename
    assert abs(rollup[6] - physical[6]) < 1e-12, filename
    assert abs(physical_value + treps_value + nca_value - total_value) < Decimal("0.000001"), filename
    assert abs(physical_weight + treps_weight + nca_weight - Decimal(1)) < Decimal("0.00000001"), filename

    if metal == "silver":
        assert reported_treps_weight == "^", (filename, reported_treps_weight)
        assert any("less than 0.01% of nav" in note.lower() for note in footnotes), footnotes
        assert treps_weight < Decimal("0.0001"), treps_weight
    else:
        assert isinstance(reported_treps_weight, (float, int)), (filename, reported_treps_weight)
        assert abs(dec(reported_treps_weight) - treps_weight) < Decimal("0.00000001"), filename

    results[metal] = {
        "source_file": filename,
        "sheet": sheet,
        "source_sha256": sha256(path),
        "as_of": "2026-09-30",
        "rollup_and_detail_are_equal": True,
        "physical_holding_label": physical_label,
        "physical_holding_value_lakh_rupees": str(physical_value),
        "physical_holding_weight_percent": as_pct(physical_weight),
        "treps_value_lakh_rupees": str(treps_value),
        "treps_weight_percent_source_or_derived": as_pct(treps_weight),
        "treps_percent_source_cell": reported_treps_weight,
        "net_current_assets_lakh_rupees": str(nca_value),
        "net_current_assets_weight_percent": as_pct(nca_weight),
        "total_net_assets_lakh_rupees": str(total_value),
        "exposure_reconciles_to_total": True,
        "weight_reconciles_to_100_percent": True,
        "quantity_as_reported": physical[4],
    }

out = {
    "schema_version": "1.0",
    "evidence_id": "G6.3-ICICI-GOLD-SILVER-HOLDINGS-2026-09",
    "audit_method": "Exact workbook cells; Decimal arithmetic for reconciliation; no return inference.",
    "results": results,
    "limitations": [
        "This is a 2026-09-30 holdings snapshot, not current holdings after that date.",
        "It does not establish ETF market price, NAV tracking, premium/discount, bid-ask spread, depth, slippage, or investor execution.",
        "It does not establish long-run return history, covariance, tax, or suitability.",
        "Physical metal holdings are reported without a bar-level serial/lot inventory.",
        "The source quantity fields are retained as reported; no unit is inferred.",
    ],
}
(ROOT / "holdings_audit.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(out, indent=2, sort_keys=True))