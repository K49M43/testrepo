# G4.3 — G4.2 policy cases on the G2 SQLite boundary

## Purpose

G4.3 connects each frozen G4.2 allocation hypothesis to the accepted Sprint 2 SQLite snapshot and run-manifest contract. It reuses SQLite schema v1 and the existing Python domain code. It adds no database tables or migrations.

The calculation is intentionally bounded to deterministic gross-cash allocation arithmetic. It allocates the mandate-derived illustrative initial corpus and the source-pinned 120- or 122-contribution schedule to each sleeve using the case's exact Decimal weights. It does not simulate investment returns, tax, fees, inflation, volatility, goal success, execution rounding, or product eligibility.

## Run

Install the pinned contract-validation dependency, then run all three cases:

```powershell
python -m pip install -r decision/requirements-g4-validation.txt
python decision/g4_allocation_database_adapter.py --database C:/path/outside/repository/g43.sqlite
```

Run one case by its stable case ID:

```powershell
python decision/g4_allocation_database_adapter.py --database C:/path/outside/repository/g43.sqlite --case-id existing_65_20_10_5_challenger
```

The adapter returns a separate attempt/run key for each case. The database stores a content-addressed canonical snapshot and atomically publishes the manifest and G4 result through G2's existing `calculation_attempts` record. The G2 synthetic tax-ledger result is retained in its own `result` field and explicitly identified as unrelated validation evidence; G4 gross allocations are stored under `additional_results.g4_allocation_arithmetic`.

## Reproducibility and evidence

Each canonical snapshot includes the selected policy case and source links by path and normalized SHA-256. Each run manifest binds:

- G2 SQLite schema version and migration SHA-256;
- G2 calculation code and G4.3 adapter code hashes;
- G4.1 and G4.2 contract versions and fingerprints;
- selected policy case identity and content hash;
- source cashflow fixture hash and accepted dependency merge commits;
- G2's existing input, expected-output, runtime, and Git revision identities.

Historical research fixtures remain immutable and are linked by hash; the adapter does not copy an archive into SQLite. Clean-database replay must reproduce snapshot, run, and output hashes. Repeated attempts retain distinct attempt IDs.

## Interpretation limits

The ₹42 lakh figure is mandate-derived gross initial capital before the unresolved external reserve decision. It is not labeled deployable capital. The calendar dates are unresolved; horizons are relative contribution counts only. G3 outcome semantics are accepted and hash-pinned; the investor's terminal date and exit/access choice remain unresolved. G5 instrument/fee/tax/availability evidence and investor confirmations remain blocked. Investment authorization remains **NO-GO**.

## G4.4 corrective integration note — 4 November 2026

G4.1/G4.2 v1.1 supersede the active contracts while preserving v1.0 files as historical snapshots. They pin accepted G2 schema v1 and G3 outcome contract v1.0.0, including merge commits and normalized hashes. The adapter uses the v1.1 schemas and includes G3 version/hash and both accepted dependency commits in each run context. The independent G4.4 audit recomputes run keys without calling G2's run-key helper and verifies the run-manifest dependency identities. This does not resolve investor date/exit choices or G5 eligibility.
