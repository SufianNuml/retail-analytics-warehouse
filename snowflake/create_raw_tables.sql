-- ============================================================
-- FILE: create_raw_tables.sql
-- PURPOSE: Creates RAW tables used to store cleaned retail data
--          loaded from Amazon S3.
-- PROJECT: Retail Analytics Data Warehouse
-- AUTHOR: Sufian Aslam
-- ============================================================

USE DATABASE RETAIL_DB;
USE SCHEMA RAW;

CREATE OR REPLACE TABLE RAW.CUSTOMERS (
    customer_id STRING,
    name STRING,
    email STRING,
    country STRING,
    created_at TIMESTAMP,
    _loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

CREATE OR REPLACE TABLE RAW.PRODUCTS (
    product_id STRING,
    product_name STRING,
    category STRING,
    price FLOAT,
    _loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
CREATE OR REPLACE TABLE RAW.STORES (
    store_id STRING,
    city STRING,
    country STRING,
    _loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
CREATE OR REPLACE TABLE RAW.ORDERS (
    order_id STRING,
    customer_id STRING,
    product_id STRING,
    store_id STRING,
    order_date DATE,
    quantity INT,
    _loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
CREATE OR REPLACE TABLE RAW.PAYMENTS (
    payment_id STRING,
    order_id STRING,
    amount FLOAT,
    status STRING,
    _loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
CREATE OR REPLACE TABLE RAW.RETURNS (
    return_id STRING,
    order_id STRING,
    product_id STRING,
    return_date DATE,
    reason STRING,
    refund_amount FLOAT,
    status STRING,
    _loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
