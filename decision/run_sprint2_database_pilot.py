"""Run the Sprint 2 deterministic fixture from SQLite through the Python ledger."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from sprint2_database_pilot import DEFAULT_EXPECTED_PATH, DEFAULT_INPUT_PATH, execute_pilot


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, required=True,
                        help="SQLite database path; keep pilot databases outside Git")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--expected", type=Path, default=DEFAULT_EXPECTED_PATH)
    args = parser.parse_args()
    result = execute_pilot(args.database, args.input, args.expected)
    ledger = result["output"]["result"]
    print(json.dumps({
        "status": result["status"],
        "attempt_id": result["attempt_id"],
        "run_key_sha256": result["run_key_sha256"],
        "snapshot_sha256": result["snapshot_sha256"],
        "output_sha256": result["output_sha256"],
        "event_count": ledger["event_count"],
        "gross_terminal_wealth_inr": ledger["gross_terminal_wealth_inr"],
        "incremental_portfolio_tax_inr": ledger["incremental_portfolio_tax_inr"],
        "net_accessible_fixture_wealth_inr": ledger["net_accessible_fixture_wealth_inr"],
        "timings_ms": result["timings_ms"],
        "investment_authorization": "NO-GO",
    }, indent=2))


if __name__ == "__main__":
    main()
