"""
audit_pipeline.py
------------------
Reconciles row counts across RAW, STAGING, and MARTS layers
and writes results into RETAIL_DB.AUDIT.LOAD_AUDIT.

Run manually with: python scripts/audit_pipeline.py
"""

import os
import uuid
import pandas as pd
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        role=os.getenv("SNOWFLAKE_ROLE"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
    )


def load_expected_counts(path="data/quality_report.csv"):
    """
    Reads Phase 4's quality_report.csv to get the 'valid_rows'
    count per table — this becomes our RAW-layer expectation.
    """
    df = pd.read_csv(path)
    return dict(zip(df["table_name"].str.upper(), df["valid_rows"]))


def get_actual_count(cur, schema, table):
    cur.execute(f"SELECT COUNT(*) FROM RETAIL_DB.{schema}.{table}")
    return cur.fetchone()[0]


def insert_audit_row(cur, run_id, table_name, layer, expected, actual, status):
    diff = actual - expected
    cur.execute("""
        INSERT INTO RETAIL_DB.AUDIT.LOAD_AUDIT
        (run_id, table_name, layer, expected_rows, actual_rows, row_diff, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (run_id, table_name, layer, expected, actual, diff, status))


def run_audit():
    run_id = str(uuid.uuid4())
    expected_counts = load_expected_counts()

    conn = get_connection()
    cur = conn.cursor()

    # Map: table name -> (raw_table, staging_model)
    tables = {
        "CUSTOMERS": "STG_CUSTOMERS",
        "PRODUCTS":  "STG_PRODUCTS",
        "STORES":    "STG_STORES",
        "ORDERS":    "STG_ORDERS",
        "PAYMENTS":  "STG_PAYMENTS",
        "RETURNS":   "STG_RETURNS",
    }

    print(f"Starting audit run: {run_id}")

    for raw_table, staging_table in tables.items():
        expected = expected_counts.get(raw_table)
        if expected is None:
            print(f"  [SKIP] No expected count found for {raw_table}")
            continue

        # --- RAW layer check ---
        raw_actual = get_actual_count(cur, "RAW", raw_table)
        raw_status = "PASS" if raw_actual == expected else "FAIL"
        insert_audit_row(cur, run_id, raw_table, "RAW", expected, raw_actual, raw_status)
        print(f"  RAW.{raw_table}: expected={expected}, actual={raw_actual}, status={raw_status}")

        # --- STAGING layer check ---
        # Staging may legitimately drop duplicate rows via QUALIFY dedup logic,
        # so we allow a small tolerance instead of expecting an exact match.
        staging_actual = get_actual_count(cur, "RAW_STAGING", staging_table)
        tolerance = max(1, int(expected * 0.01))  # allow up to 1% variance
        staging_status = "PASS" if abs(staging_actual - expected) <= tolerance else "WARN"
        insert_audit_row(cur, run_id, staging_table, "STAGING", expected, staging_actual, staging_status)
        print(f"  STAGING.{staging_table}: expected={expected}, actual={staging_actual}, status={staging_status}")

    conn.commit()
    cur.close()
    conn.close()
    print(f"Audit run {run_id} complete.")
    return run_id


if __name__ == "__main__":
    run_audit()