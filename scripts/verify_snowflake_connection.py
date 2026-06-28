import snowflake.connector
import os
from dotenv import load_dotenv

load_dotenv()

def verify_snowflake_connection():
    """
    Verifies Snowflake connectivity and confirms RAW tables are
    accessible and populated. Run after Phase 5 load to validate
    pipeline state before proceeding to dbt (Phase 6).
    """
    conn = snowflake.connector.connect(
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        role=os.getenv('SNOWFLAKE_ROLE'),
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
        database=os.getenv('SNOWFLAKE_DATABASE'),
        schema='RAW'
    )

    cur = conn.cursor()

    tables = ['CUSTOMERS', 'PRODUCTS', 'STORES', 'ORDERS', 'PAYMENTS', 'RETURNS']

    print("\n--- Snowflake RAW Layer Verification ---\n")

    all_passed = True
    for table in tables:
        cur.execute(f"SELECT COUNT(*) FROM RETAIL_DB.RAW.{table}")
        count = cur.fetchone()[0]
        status = "✅ PASS" if count > 0 else "❌ FAIL — Table is empty"
        print(f"  {table:<15} | Rows: {count:<8} | {status}")
        if count == 0:
            all_passed = False

    print("\n--- Verification Complete ---")
    print(f"Overall Status: {'✅ All tables populated' if all_passed else '❌ One or more tables empty — investigate'}\n")

    cur.close()
    conn.close()

if __name__ == "__main__":
    verify_snowflake_connection()