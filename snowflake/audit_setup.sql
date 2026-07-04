-- ============================================================
-- AUDIT.LOAD_AUDIT
-- Purpose: Tracks row-count reconciliation across every layer
-- of the pipeline, for every run, over time.
-- ============================================================
CREATE OR REPLACE TABLE RETAIL_DB.AUDIT.LOAD_AUDIT (
    audit_id        INT AUTOINCREMENT PRIMARY KEY,
    run_id          STRING,          -- groups all rows from one pipeline execution
    table_name      STRING,          -- e.g. 'CUSTOMERS', 'ORDERS'
    layer           STRING,          -- 'RAW', 'STAGING', 'MARTS'
    expected_rows   INT,
    actual_rows     INT,
    row_diff        INT,             -- actual - expected (useful for trend charts later)
    status          STRING,          -- 'PASS', 'FAIL', 'WARN'
    run_timestamp   TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- ============================================================
-- AUDIT.ANOMALY_LOG
-- Purpose: Stores every anomaly check result, every time it runs,
-- so you have a historical record — not just "the last check."
-- ============================================================
CREATE OR REPLACE TABLE RETAIL_DB.AUDIT.ANOMALY_LOG (
    anomaly_id      INT AUTOINCREMENT PRIMARY KEY,
    run_id          STRING,
    check_name      STRING,          -- e.g. 'revenue_drop_mom'
    metric_value    FLOAT,           -- the actual computed value (e.g. -34.2 for % drop)
    threshold       FLOAT,           -- the limit that was configured
    is_anomaly      BOOLEAN,
    details         STRING,          -- human-readable context, e.g. "Feb revenue $12,300 vs Jan $18,700"
    run_timestamp   TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);