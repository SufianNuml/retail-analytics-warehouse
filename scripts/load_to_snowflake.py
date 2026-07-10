import os
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()


def load_to_snowflake():

    conn = snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        role=os.getenv("SNOWFLAKE_ROLE"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema="RAW"
    )

    cur = conn.cursor()

    print("Loading RAW tables into Snowflake...\n")

    sql_commands = [

        """
        COPY INTO RAW.CUSTOMERS
        (customer_id,name,email,country,created_at)
        FROM @RETAIL_DB.RAW.S3_CLEAN_STAGE/customers_clean.csv
        FILE_FORMAT=(FORMAT_NAME=RETAIL_DB.RAW.CSV_FORMAT)
        ON_ERROR='CONTINUE';
        """,

        """
        COPY INTO RAW.PRODUCTS
        (product_id,product_name,category,price)
        FROM @RETAIL_DB.RAW.S3_CLEAN_STAGE/products_clean.csv
        FILE_FORMAT=(FORMAT_NAME=RETAIL_DB.RAW.CSV_FORMAT)
        ON_ERROR='CONTINUE';
        """,

        """
        COPY INTO RAW.STORES
        (store_id,city,country)
        FROM @RETAIL_DB.RAW.S3_CLEAN_STAGE/stores_clean.csv
        FILE_FORMAT=(FORMAT_NAME=RETAIL_DB.RAW.CSV_FORMAT)
        ON_ERROR='CONTINUE';
        """,

        """
        COPY INTO RAW.ORDERS
        (
            order_id,
            customer_id,
            product_id,
            store_id,
            order_date,
            quantity
        )
        FROM
        (
            SELECT
                $1,$2,$3,$4,$5,$6
            FROM @RETAIL_DB.RAW.S3_CLEAN_STAGE/orders_clean.csv
        )
        FILE_FORMAT=(FORMAT_NAME=RETAIL_DB.RAW.CSV_FORMAT)
        ON_ERROR='CONTINUE'
        FORCE=TRUE;
        """,

        """
        COPY INTO RAW.PAYMENTS
        (payment_id,order_id,amount,status)
        FROM @RETAIL_DB.RAW.S3_CLEAN_STAGE/payments_clean.csv
        FILE_FORMAT=(FORMAT_NAME=RETAIL_DB.RAW.CSV_FORMAT)
        ON_ERROR='CONTINUE';
        """,

        """
        COPY INTO RAW.RETURNS
        (
            return_id,
            order_id,
            product_id,
            return_date,
            reason,
            refund_amount,
            status
        )
        FROM @RETAIL_DB.RAW.S3_CLEAN_STAGE/returns_clean.csv
        FILE_FORMAT=(FORMAT_NAME=RETAIL_DB.RAW.CSV_FORMAT)
        ON_ERROR='CONTINUE';
        """
    ]

    tables = [
        "CUSTOMERS",
        "PRODUCTS",
        "STORES",
        "ORDERS",
        "PAYMENTS",
        "RETURNS"
    ]

    for table, sql in zip(tables, sql_commands):

        print(f"Loading {table}...")

        # Remove old data before loading new data
        cur.execute(f"TRUNCATE TABLE RAW.{table};")

        # Load fresh data
        cur.execute(sql)

        print(f"✅ {table} loaded")

    conn.commit()

    cur.close()
    conn.close()

    print("\nAll RAW tables loaded successfully.")


def main():
    load_to_snowflake()


if __name__ == "__main__":
    main()