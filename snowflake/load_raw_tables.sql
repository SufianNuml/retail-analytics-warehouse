-- ============================================================
-- FILE: load_raw_tables.sql
-- PURPOSE: Loads cleaned CSV files from the Snowflake external
--          stage into RAW tables using COPY INTO.
-- PROJECT: Retail Analytics Data Warehouse
-- AUTHOR: Sufian Aslam
-- ============================================================


USE DATABASE RETAIL_DB;
USE WAREHOUSE RETAIL_WH;
USE SCHEMA RAW;

-- Load Customers
COPY INTO RAW.CUSTOMERS
(customer_id, name, email, country, created_at)
FROM @RETAIL_DB.RAW.S3_CLEAN_STAGE/customers_clean.csv
FILE_FORMAT = (FORMAT_NAME = RETAIL_DB.RAW.CSV_FORMAT)
ON_ERROR = 'CONTINUE';

-- Load Products
COPY INTO RAW.PRODUCTS
(product_id, product_name, category, price)
FROM @RETAIL_DB.RAW.S3_CLEAN_STAGE/products_clean.csv
FILE_FORMAT = (FORMAT_NAME = RETAIL_DB.RAW.CSV_FORMAT)
ON_ERROR = 'CONTINUE';

-- Load Stores
COPY INTO RAW.STORES
(store_id, city, country)
FROM @RETAIL_DB.RAW.S3_CLEAN_STAGE/stores_clean.csv
FILE_FORMAT = (FORMAT_NAME = RETAIL_DB.RAW.CSV_FORMAT)
ON_ERROR = 'CONTINUE';

-- Load Orders
COPY INTO RAW.ORDERS
(
    order_id,
    customer_id,
    product_id,
    store_id,
    order_date,
    quantity
)
FROM (
    SELECT
        $1,
        $2,
        $3,
        $4,
        $5,
        $6
    FROM @RETAIL_DB.RAW.S3_CLEAN_STAGE/orders_clean.csv
)
FILE_FORMAT = (FORMAT_NAME = RETAIL_DB.RAW.CSV_FORMAT)
ON_ERROR = 'CONTINUE'
FORCE = TRUE;

-- Load Payments
COPY INTO RAW.PAYMENTS
(payment_id, order_id, amount, status)
FROM @RETAIL_DB.RAW.S3_CLEAN_STAGE/payments_clean.csv
FILE_FORMAT = (FORMAT_NAME = RETAIL_DB.RAW.CSV_FORMAT)
ON_ERROR = 'CONTINUE';

-- Load Returns
COPY INTO RAW.RETURNS
(return_id, order_id, product_id, return_date, reason, refund_amount, status)
FROM @RETAIL_DB.RAW.S3_CLEAN_STAGE/returns_clean.csv
FILE_FORMAT = (FORMAT_NAME = RETAIL_DB.RAW.CSV_FORMAT)
ON_ERROR = 'CONTINUE';