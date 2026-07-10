import os
import glob
import uuid

import snowflake.connector

from dotenv import load_dotenv

load_dotenv()


CHECK_THRESHOLDS = {
    "revenue_drop_mom": -30.0,
    "return_rate_spike": 1.5,
    "payment_failure_rate": 10.0,
    "null_customer_spike": 5.0,
}


def get_connection():

    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        role=os.getenv("SNOWFLAKE_ROLE"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
    )


def run_anomaly_checks():

    run_id = str(uuid.uuid4())

    conn = get_connection()

    cur = conn.cursor()

    sql_files = glob.glob("snowflake/anomaly_checks/*.sql")

    for filepath in sql_files:

        check_name = os.path.splitext(
            os.path.basename(filepath)
        )[0]

        with open(filepath, "r") as f:
            query = f.read()

        print(f"\nRunning {check_name}...")

        cur.execute(query)

        rows = cur.fetchall()

        is_anomaly = len(rows) > 0

        threshold = CHECK_THRESHOLDS.get(check_name)

        details = (
            f"{len(rows)} anomalous period(s) found"
            if is_anomaly
            else "No anomalies detected"
        )

        cur.execute(
            """
            INSERT INTO RETAIL_DB.AUDIT.ANOMALY_LOG
            (
                RUN_ID,
                CHECK_NAME,
                METRIC_VALUE,
                THRESHOLD,
                IS_ANOMALY,
                DETAILS
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                run_id,
                check_name,
                None,
                threshold,
                is_anomaly,
                details,
            ),
        )

        if is_anomaly:
            print(f"🚨 {check_name}: {details}")
        else:
            print(f"✅ {check_name}: {details}")

    conn.commit()

    cur.close()

    conn.close()

    print("\nFinished.")
    print("Run ID:", run_id)


if __name__ == "__main__":
    run_anomaly_checks()