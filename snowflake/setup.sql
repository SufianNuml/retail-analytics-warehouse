
-- ============================================================
-- FILE: setup.sql
-- PURPOSE: Creates Snowflake warehouse, database, schemas,
--          file format, and external S3 stage for RAW layer
-- CREDENTIALS: Replace placeholder values with actual credentials
--              before executing this script.
-- PROJECT: Retail Analytics Data Warehouse
-- AUTHOR: Sufian Aslam
-- ============================================================



CREATE WAREHOUSE IF NOT EXISTS RETAIL_WH
  WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  COMMENT = 'Warehouse for Retail Analytics pipeline - auto-suspends after 60s';

CREATE DATABASE IF NOT EXISTS RETAIL_DB
  COMMENT = 'Retail Analytics Data Warehouse - portfolio project';

USE DATABASE RETAIL_DB;

CREATE SCHEMA IF NOT EXISTS RAW
  COMMENT = 'Raw ingestion layer - data loaded directly from S3 clean zone';

CREATE SCHEMA IF NOT EXISTS STAGING
  COMMENT = 'Staging layer - managed by dbt, cleaned and typed';

CREATE SCHEMA IF NOT EXISTS MARTS
  COMMENT = 'Mart layer - managed by dbt, business-ready star schema';

CREATE SCHEMA IF NOT EXISTS AUDIT
  COMMENT = 'Audit and observability layer - row counts, anomaly flags';

-- ============================
-- STEP 3
-- Create CSV File Format
-- ============================

USE DATABASE RETAIL_DB;
USE SCHEMA RAW;

CREATE OR REPLACE FILE FORMAT RETAIL_DB.RAW.CSV_FORMAT
TYPE = 'CSV'
FIELD_DELIMITER = ','
SKIP_HEADER = 1
FIELD_OPTIONALLY_ENCLOSED_BY = '"'
NULL_IF = ('', 'NULL', 'null', 'None')
TRIM_SPACE = TRUE
COMMENT = 'Standard CSV format for retail clean data loaded from S3';

-- ===========================================
-- STEP 4 - Create External Stage
-- ===========================================

CREATE OR REPLACE STAGE RETAIL_DB.RAW.S3_CLEAN_STAGE
URL='s3://retail-analytics-sufian/clean/'

CREDENTIALS = (
  AWS_KEY_ID='YOUR_AWS_ACCESS_KEY_ID_HERE'
AWS_SECRET_KEY='YOUR_AWS_SECRET_ACCESS_KEY_HERE'
)

FILE_FORMAT = RETAIL_DB.RAW.CSV_FORMAT

COMMENT = 'External stage pointing to S3 clean zone';