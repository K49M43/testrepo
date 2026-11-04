CREATE TABLE schema_migrations (
    version INTEGER PRIMARY KEY CHECK (version > 0),
    migration_name TEXT NOT NULL UNIQUE,
    sha256 TEXT NOT NULL CHECK (length(sha256) = 64),
    applied_at_utc TEXT NOT NULL
);

CREATE TABLE fixture_snapshots (
    snapshot_sha256 TEXT PRIMARY KEY CHECK (length(snapshot_sha256) = 64),
    fixture_id TEXT NOT NULL,
    fixture_version TEXT NOT NULL,
    canonical_payload_json TEXT NOT NULL,
    event_count INTEGER NOT NULL CHECK (event_count >= 0),
    created_at_utc TEXT NOT NULL
);

CREATE TABLE ledger_events (
    snapshot_sha256 TEXT NOT NULL,
    event_id TEXT NOT NULL,
    event_order INTEGER NOT NULL CHECK (event_order >= 0),
    event_date TEXT NOT NULL CHECK (length(event_date) = 10),
    tax_year TEXT NOT NULL CHECK (length(tax_year) = 7),
    event_sequence INTEGER NOT NULL CHECK (event_sequence > 0),
    event_type TEXT NOT NULL,
    instrument_id TEXT NOT NULL,
    cash_amount_inr TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    PRIMARY KEY (snapshot_sha256, event_id),
    UNIQUE (snapshot_sha256, event_date, event_sequence),
    FOREIGN KEY (snapshot_sha256) REFERENCES fixture_snapshots(snapshot_sha256)
);

CREATE TABLE auxiliary_inputs (
    snapshot_sha256 TEXT NOT NULL,
    input_kind TEXT NOT NULL CHECK (input_kind IN (
        'external_tax_input', 'valuation_price', 'capital_loss_offset', 'carried_loss'
    )),
    tax_year TEXT NOT NULL,
    row_key TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    PRIMARY KEY (snapshot_sha256, input_kind, tax_year, row_key),
    FOREIGN KEY (snapshot_sha256) REFERENCES fixture_snapshots(snapshot_sha256)
);

CREATE TABLE calculation_attempts (
    attempt_id TEXT PRIMARY KEY,
    run_key_sha256 TEXT NOT NULL CHECK (length(run_key_sha256) = 64),
    snapshot_sha256 TEXT NOT NULL CHECK (length(snapshot_sha256) = 64),
    code_sha256 TEXT NOT NULL CHECK (length(code_sha256) = 64),
    status TEXT NOT NULL CHECK (status IN ('RUNNING', 'COMPLETE', 'FAILED')),
    output_json TEXT,
    output_sha256 TEXT CHECK (output_sha256 IS NULL OR length(output_sha256) = 64),
    timings_json TEXT,
    failure_message TEXT,
    started_at_utc TEXT NOT NULL,
    finished_at_utc TEXT,
    CHECK (
        (status = 'RUNNING' AND output_json IS NULL AND output_sha256 IS NULL AND failure_message IS NULL)
        OR (status = 'COMPLETE' AND output_json IS NOT NULL AND output_sha256 IS NOT NULL AND failure_message IS NULL)
        OR (status = 'FAILED' AND output_json IS NULL AND output_sha256 IS NULL AND failure_message IS NOT NULL)
    )
);

CREATE INDEX calculation_attempts_by_run_key
    ON calculation_attempts(run_key_sha256, status);
