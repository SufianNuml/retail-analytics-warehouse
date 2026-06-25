# ==========================
# IMPORTS
# ==========================

import pandas as pd
import numpy as np
import boto3
import os
import json

from datetime import datetime
from dotenv import load_dotenv

# ==========================
# ENVIRONMENT
# ==========================

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

RAW_PATH = "data/raw"
CLEAN_PATH = "data/clean"
QUARANTINE_PATH = "data/quarantine"

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

# ==========================
# HELPER FUNCTIONS
# ==========================
def check_nulls(df, columns):
    return df[columns].isnull().any(axis=1)


def check_duplicates(df, subset_columns):
    return df.duplicated(
        subset=subset_columns,
        keep="first"
    )


def check_future_dates(df, date_column):
    today = pd.Timestamp(datetime.today().date())

    return pd.to_datetime(
        df[date_column],
        errors="coerce"
    ) > today


def check_negative_values(df, column):
    return pd.to_numeric(
        df[column],
        errors="coerce"
    ) <= 0


def check_foreign_key(
    df,
    fk_column,
    valid_ids
):
    return ~df[fk_column].isin(valid_ids)


def standardize_category(
    df,
    column
):
    df = df.copy()

    df[column] = (
        df[column]
        .str.strip()
        .str.title()
    )

    return df



def assign_quality_flag(
    df,
    flag_conditions
):
    df = df.copy()

    # Default value
    df["quality_flag"] = "valid"

    # First condition should win
    for condition_mask, flag_label in reversed(flag_conditions):
        df.loc[condition_mask, "quality_flag"] = flag_label

    return df

def split_and_save(
    df,
    table_name
):
    clean_df = df[
        df["quality_flag"] == "valid"
    ].copy()

    quarantine_df = df[
        df["quality_flag"] != "valid"
    ].copy()

    clean_path = (
        f"{CLEAN_PATH}/{table_name}_clean.csv"
    )

    quarantine_path = (
        f"{QUARANTINE_PATH}/{table_name}_quarantine.csv"
    )

    clean_df.to_csv(
        clean_path,
        index=False
    )

    quarantine_df.to_csv(
        quarantine_path,
        index=False
    )

    issue_breakdown = (
        quarantine_df["quality_flag"]
        .value_counts()
        .to_dict()
    )

    summary = {
        "table_name": table_name,
        "total_rows": len(df),
        "valid_rows": len(clean_df),
        "quarantined_rows": len(quarantine_df),
        "issue_breakdown": issue_breakdown
    }

    print(
        f"\n[{table_name.upper()}] "
        f"Total: {summary['total_rows']} | "
        f"Valid: {summary['valid_rows']} | "
        f"Quarantined: {summary['quarantined_rows']}"
    )

    if issue_breakdown:
        for reason, count in issue_breakdown.items():
            print(
                f"   └─ {reason}: {count} rows"
            )

    return summary



print("All helper functions loaded successfully.")




# ==========================
# CUSTOMERS CLEANING
# ==========================

def clean_customers():

    print("\n" + "=" * 50)
    print("CLEANING: customers")
    print("=" * 50)

    df = pd.read_csv(
        f"{RAW_PATH}/customers.csv"
    )

    print(
        f"Loaded {len(df)} rows from customers.csv"
    )

    # Standardization
    df["email"] = (
        df["email"]
        .str.strip()
        .str.lower()
    )

    df["name"] = (
        df["name"]
        .str.strip()
    )

    df["country"] = (
        df["country"]
        .str.strip()
    )

    # Validation Masks
    null_email_mask = check_nulls(
        df,
        ["email"]
    )

    null_name_mask = check_nulls(
        df,
        ["name"]
    )

    duplicate_mask = check_duplicates(
        df,
        subset_columns=["email"]
    )

    # Quality Flags
    flag_conditions = [
        (duplicate_mask, "duplicate"),
        (null_name_mask, "missing_name"),
        (null_email_mask, "missing_email")
    ]

    df = assign_quality_flag(
        df,
        flag_conditions
    )

    summary = split_and_save(
        df,
        "customers"
    )

    return summary





# ==========================
# PRODUCTS CLEANING
# ==========================

def clean_products():

    print("\n" + "=" * 50)
    print("CLEANING: products")
    print("=" * 50)

    df = pd.read_csv(
        f"{RAW_PATH}/products.csv"
    )

    print(
        f"Loaded {len(df)} rows from products.csv"
    )

    # Standardization
    df = standardize_category(
        df,
        "category"
    )

    df["product_name"] = (
        df["product_name"]
        .str.strip()
    )

    # Convert price to numeric
    df["price"] = pd.to_numeric(
        df["price"],
        errors="coerce"
    )

    # Validation Masks
    null_price_mask = check_nulls(
        df,
        ["price"]
    )

    negative_price_mask = check_negative_values(
        df,
        "price"
    )

    null_name_mask = check_nulls(
        df,
        ["product_name"]
    )

    duplicate_mask = check_duplicates(
        df,
        subset_columns=["product_id"]
    )

    # Quality Flags
    flag_conditions = [
        (duplicate_mask, "duplicate"),
        (null_name_mask, "missing_product_name"),
        (negative_price_mask, "invalid_price"),
        (null_price_mask, "missing_price")
    ]

    df = assign_quality_flag(
        df,
        flag_conditions
    )

    summary = split_and_save(
        df,
        "products"
    )

    return summary


def clean_stores():
    print("\n" + "="*50)
    print("CLEANING: stores")
    print("="*50)

    df = pd.read_csv(f"{RAW_PATH}/stores.csv")
    print(f"Loaded {len(df)} rows from stores.csv")

    # Standardize
    df["city"] = df["city"].str.strip()
    df["country"] = df["country"].str.strip()

    # Validation
    null_city_mask = check_nulls(df, ["city"])
    null_country_mask = check_nulls(df, ["country"])
    duplicate_mask = check_duplicates(df, subset_columns=["store_id"])

    flag_conditions = [
        (duplicate_mask, "duplicate"),
        (null_city_mask, "missing_city"),
        (null_country_mask, "missing_country"),
    ]
    df = assign_quality_flag(df, flag_conditions)

    summary = split_and_save(df, "stores")
    return summary






def clean_orders():
    print("\n" + "="*50)
    print("CLEANING: orders")
    print("="*50)

    df = pd.read_csv(f"{RAW_PATH}/orders.csv")
    print(f"Loaded {len(df)} rows from orders.csv")

    # Load valid customer and product IDs from the already-cleaned tables
    # This is why order matters — customers and products must be cleaned first
    valid_customers = pd.read_csv(f"{CLEAN_PATH}/customers_clean.csv")
    valid_products = pd.read_csv(f"{CLEAN_PATH}/products_clean.csv")

    valid_customer_ids = set(valid_customers["customer_id"].astype(str))
    valid_product_ids = set(valid_products["product_id"].astype(str))

    # Convert order_date to datetime
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

    # Validation
    invalid_customer_fk_mask = check_foreign_key(
        df, "customer_id", valid_customer_ids
    )
    invalid_product_fk_mask = check_foreign_key(
        df, "product_id", valid_product_ids
    )
    future_date_mask = check_future_dates(df, "order_date")
    null_date_mask = check_nulls(df, ["order_date"])
    duplicate_mask = check_duplicates(df, subset_columns=["order_id"])

    flag_conditions = [
        (duplicate_mask, "duplicate"),
        (null_date_mask, "missing_order_date"),
        (future_date_mask, "future_date"),
        (invalid_customer_fk_mask, "invalid_customer_fk"),
        (invalid_product_fk_mask, "invalid_product_fk"),
    ]
    df = assign_quality_flag(df, flag_conditions)

    summary = split_and_save(df, "orders")
    return summary







def clean_payments():
    print("\n" + "="*50)
    print("CLEANING: payments")
    print("="*50)

    df = pd.read_csv(f"{RAW_PATH}/payments.csv")
    print(f"Loaded {len(df)} rows from payments.csv")

    # Load valid order IDs from cleaned orders
    valid_orders = pd.read_csv(f"{CLEAN_PATH}/orders_clean.csv")
    valid_order_ids = set(valid_orders["order_id"].astype(str))

    # Convert amount to numeric
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    # Validation
    null_amount_mask = check_nulls(df, ["amount"])
    negative_amount_mask = check_negative_values(df, "amount")
    orphan_payment_mask = check_foreign_key(df, "order_id", valid_order_ids)
    duplicate_mask = check_duplicates(df, subset_columns=["payment_id"])

    flag_conditions = [
        (duplicate_mask, "duplicate"),
        (null_amount_mask, "missing_amount"),
        (negative_amount_mask, "invalid_amount"),
        (orphan_payment_mask, "orphan_payment"),
    ]
    df = assign_quality_flag(df, flag_conditions)

    summary = split_and_save(df, "payments")
    return summary


def clean_returns():
    print("\n" + "="*50)
    print("CLEANING: returns")
    print("="*50)

    df = pd.read_csv(f"{RAW_PATH}/returns.csv")
    print(f"Loaded {len(df)} rows from returns.csv")

    # Load clean orders to validate FKs and date logic
    valid_orders = pd.read_csv(f"{CLEAN_PATH}/orders_clean.csv")
    valid_order_ids = set(valid_orders["order_id"].astype(str))

    # Convert dates
    df["return_date"] = pd.to_datetime(df["return_date"], errors="coerce")
    valid_orders["order_date"] = pd.to_datetime(valid_orders["order_date"], errors="coerce")

    # Join return rows with their corresponding order dates
    df = df.merge(
        valid_orders[["order_id", "order_date"]],
        on="order_id",
        how="left"
    )

    # Validation
    orphan_return_mask = check_foreign_key(df, "order_id", valid_order_ids)
    null_date_mask = check_nulls(df, ["return_date"])

    # Return date before order date — the date logic check
    invalid_date_sequence_mask = (
        df["return_date"].notna() &
        df["order_date"].notna() &
        (df["return_date"] < df["order_date"])
    )

    duplicate_mask = check_duplicates(df, subset_columns=["return_id"])

    flag_conditions = [
        (duplicate_mask, "duplicate"),
        (null_date_mask, "missing_return_date"),
        (invalid_date_sequence_mask, "return_before_order_date"),
        (orphan_return_mask, "orphan_return"),
    ]
    df = assign_quality_flag(df, flag_conditions)

    # Drop the joined order_date column before saving (it was only for validation)
    df = df.drop(columns=["order_date"])

    summary = split_and_save(df, "returns")
    return summary



def generate_quality_report(summaries):
    """
    Takes a list of summary dictionaries from split_and_save()
    and writes them to a single quality_report.json and
    quality_report.csv file.
    """
    print("\n" + "="*50)
    print("GENERATING QUALITY REPORT")
    print("="*50)

    # Save as JSON (preserves the issue_breakdown dict cleanly)
    report_json_path = "data/quality_report.json"
    with open(report_json_path, "w") as f:
        json.dump(summaries, f, indent=4)

    # Also save as CSV (flat format — easier to view in Excel/Sheets)
    report_rows = []
    for s in summaries:
        report_rows.append({
            "table_name": s["table_name"],
            "total_rows": s["total_rows"],
            "valid_rows": s["valid_rows"],
            "quarantined_rows": s["quarantined_rows"],
            "issue_breakdown": json.dumps(s["issue_breakdown"])
        })

    report_df = pd.DataFrame(report_rows)
    report_csv_path = "data/quality_report.csv"
    report_df.to_csv(report_csv_path, index=False)

    print(f"\nQuality report saved:")
    print(f"  → {report_json_path}")
    print(f"  → {report_csv_path}")
    print("\nSummary Table:")
    print(report_df.to_string(index=False))



def upload_clean_to_s3():
    """
    Uploads all *_clean.csv files from data/clean/ to
    s3://<bucket>/clean/ prefix.
    """
    print("\n" + "="*50)
    print("UPLOADING CLEAN FILES TO S3")
    print("="*50)

    clean_files = [f for f in os.listdir(CLEAN_PATH) if f.endswith("_clean.csv")]

    if not clean_files:
        print("No clean files found. Skipping S3 upload.")
        return

    for filename in clean_files:
        local_path = f"{CLEAN_PATH}/{filename}"
        s3_key = f"clean/{filename}"

        try:
            s3_client.upload_file(local_path, S3_BUCKET_NAME, s3_key)
            file_size = os.path.getsize(local_path)
            print(f"  ✓ Uploaded: {filename} ({file_size:,} bytes) → s3://{S3_BUCKET_NAME}/{s3_key}")
        except Exception as e:
            print(f"  ✗ Failed to upload {filename}: {str(e)}")

    print("\nS3 upload complete.")


def main():
    print("\n" + "█"*60)
    print("  PHASE 4: DATA CLEANING & QUALITY LAYER")
    print("  Retail Analytics Data Warehouse")
    print("█"*60)
    print(f"  Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("█"*60)

    summaries = []

    # Run each table cleaning function in dependency order
    summaries.append(clean_customers())
    summaries.append(clean_products())
    summaries.append(clean_stores())
    summaries.append(clean_orders())
    summaries.append(clean_payments())
    summaries.append(clean_returns())

    # Generate the quality report
    generate_quality_report(summaries)

    # Upload clean files to S3
    upload_clean_to_s3()

    print("\n" + "█"*60)
    print("  PHASE 4 COMPLETE")
    print(f"  Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("█"*60)


if __name__ == "__main__":
    main()
    
    