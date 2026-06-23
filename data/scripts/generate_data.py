import pandas as pd
import numpy as np
from faker import Faker
import random
import os
from datetime import datetime, timedelta

fake = Faker()

Faker.seed(42)
random.seed(42)
np.random.seed(42)

OUTPUT_DIR = "data/raw"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_customers(n=1000):
    data = []

    for i in range(1, n + 1):
        data.append({
            "customer_id": f"CUST-{str(i).zfill(4)}",
            "name": fake.name(),
            "email": fake.email(),
            "country": fake.country(),
            "created_at": fake.date_time_between(
                start_date="-3y",
                end_date="now"
            )
        })

    df = pd.DataFrame(data)

    df.to_csv(
        f"{OUTPUT_DIR}/customers.csv",
        index=False
    )

    print(f"customers.csv - {len(df)} rows")

    return df



def generate_products(n=100):
    categories = [
        "Electronics",
        "Clothing",
        "Home",
        "Sports",
        "Books"
    ]

    data = []

    for i in range(1, n + 1):
        data.append({
            "product_id": f"PROD-{str(i).zfill(3)}",
            "product_name": fake.catch_phrase(),
            "category": random.choice(categories),
            "price": round(
                random.uniform(5.0, 500.0),
                2
            )
        })

    df = pd.DataFrame(data)

    df.to_csv(
        f"{OUTPUT_DIR}/products.csv",
        index=False
    )

    print(f"products.csv - {len(df)} rows")

    return df




def generate_stores(n=15):
    data = []

    for i in range(1, n + 1):
        data.append({
            "store_id": f"STORE-{str(i).zfill(2)}",
            "city": fake.city(),
            "country": fake.country()
        })

    df = pd.DataFrame(data)

    df.to_csv(
        f"{OUTPUT_DIR}/stores.csv",
        index=False
    )

    print(f"stores.csv - {len(df)} rows")

    return df

def generate_orders(customers_df, products_df, stores_df, n=8000):

    customer_ids = customers_df["customer_id"].tolist()
    product_ids = products_df["product_id"].tolist()
    store_ids = stores_df["store_id"].tolist()

    data = []

    for i in range(1, n + 1):
        data.append({
            "order_id": f"ORD-{str(i).zfill(5)}",
            "customer_id": random.choice(customer_ids),
            "product_id": random.choice(product_ids),
            "store_id": random.choice(store_ids),
            "order_date": fake.date_between(
                start_date="-2y",
                end_date="today"
            ),
            "quantity": random.randint(1, 10)
        })

    df = pd.DataFrame(data)

    df.to_csv(
        f"{OUTPUT_DIR}/orders.csv",
        index=False
    )

    print(f"orders.csv - {len(df)} rows")

    return df



def generate_payments(orders_df, products_df):

    merged = orders_df.merge(
        products_df[["product_id", "price"]],
        on="product_id"
    )

    data = []

    for i, row in merged.iterrows():

        data.append({
            "payment_id": f"PAY-{str(i + 1).zfill(5)}",
            "order_id": row["order_id"],
            "amount": round(
                row["quantity"] * row["price"],
                2
            ),
            "status": random.choices(
                ["completed", "pending", "failed"],
                weights=[85, 10, 5]
            )[0]
        })

    df = pd.DataFrame(data)

    df.to_csv(
        f"{OUTPUT_DIR}/payments.csv",
        index=False
    )

    print(f"payments.csv - {len(df)} rows")

    return df



def generate_returns(orders_df):

    reasons = [
        "defective",
        "wrong item",
        "changed mind",
        "damaged",
        "not as described"
    ]

    return_orders = orders_df.sample(
        frac=0.08,
        random_state=42
    )

    data = []

    for i, row in enumerate(
        return_orders.itertuples(),
        1
    ):

        order_date = pd.to_datetime(
            row.order_date
        )

        return_date = (
            order_date +
            timedelta(
                days=random.randint(1, 30)
            )
        )

        data.append({
            "return_id": f"RET-{str(i).zfill(4)}",
            "order_id": row.order_id,
            "product_id": row.product_id,
            "return_date": return_date.date(),
            "reason": random.choice(reasons),
            "refund_amount": round(
                random.uniform(5.0, 200.0),
                2
            ),
            "status": random.choices(
                ["processed", "pending", "rejected"],
                weights=[75, 15, 10]
            )[0]
        })

    df = pd.DataFrame(data)

    df.to_csv(
        f"{OUTPUT_DIR}/returns.csv",
        index=False
    )

    print(f"returns.csv - {len(df)} rows")

    return df








def inject_dirty_data(
    customers_df,
    products_df,
    orders_df,
    payments_df,
    returns_df
):

    # Issue 1 — NULL values

    null_email_idx = customers_df.sample(
        frac=0.03,
        random_state=1
    ).index

    customers_df.loc[
        null_email_idx,
        "email"
    ] = np.nan

    null_price_idx = products_df.sample(
        frac=0.02,
        random_state=2
    ).index

    products_df.loc[
        null_price_idx,
        "price"
    ] = np.nan

    # Issue 2 — Duplicate records

    dup_customers = customers_df.sample(
        frac=0.02,
        random_state=3
    )

    customers_df = pd.concat(
        [customers_df, dup_customers],
        ignore_index=True
    )

    dup_payments = payments_df.sample(
        frac=0.02,
        random_state=4
    )

    payments_df = pd.concat(
        [payments_df, dup_payments],
        ignore_index=True
    )

    # Issue 3 — Foreign key violations

    fk_violation_idx = orders_df.sample(
        frac=0.015,
        random_state=5
    ).index

    orders_df.loc[
        fk_violation_idx,
        "customer_id"
    ] = "CUST-GHOST-999"

    # Issue 4 — Invalid dates

    future_idx = orders_df.sample(
        frac=0.01,
        random_state=6
    ).index

    future_date = fake.date_between(
        start_date="+1d",
        end_date="+180d"
    )

    orders_df.loc[
        future_idx,
        "order_date"
    ] = future_date

    early_return_idx = returns_df.sample(
        frac=0.01,
        random_state=7
    ).index

    returns_df.loc[
        early_return_idx,
        "return_date"
    ] = pd.to_datetime(
        "2020-01-01"
    ).date()

    # Issue 5 — Inconsistent category casing

    def corrupt_category(cat):

        choice = random.random()

        if choice < 0.33:
            return cat.upper()

        elif choice < 0.66:
            return cat.lower()

        else:
            return cat + " "

    casing_idx = products_df.sample(
        frac=0.15,
        random_state=8
    ).index

    products_df.loc[
        casing_idx,
        "category"
    ] = products_df.loc[
        casing_idx,
        "category"
    ].apply(corrupt_category)

    return (
        customers_df,
        products_df,
        orders_df,
        payments_df,
        returns_df
    )



if __name__ == "__main__":

    customers_df = generate_customers()

    products_df = generate_products()

    stores_df = generate_stores()

    orders_df = generate_orders(
        customers_df,
        products_df,
        stores_df
    )

    payments_df = generate_payments(
        orders_df,
        products_df
    )

    returns_df = generate_returns(
        orders_df
    )

    (
        customers_df,
        products_df,
        orders_df,
        payments_df,
        returns_df
    ) = inject_dirty_data(
        customers_df,
        products_df,
        orders_df,
        payments_df,
        returns_df
    )

    customers_df.to_csv(
        f"{OUTPUT_DIR}/customers.csv",
        index=False
    )

    products_df.to_csv(
        f"{OUTPUT_DIR}/products.csv",
        index=False
    )

    stores_df.to_csv(
        f"{OUTPUT_DIR}/stores.csv",
        index=False
    )

    orders_df.to_csv(
        f"{OUTPUT_DIR}/orders.csv",
        index=False
    )

    payments_df.to_csv(
        f"{OUTPUT_DIR}/payments.csv",
        index=False
    )

    returns_df.to_csv(
        f"{OUTPUT_DIR}/returns.csv",
        index=False
    )

    print("\n=== Final Row Counts ===")

    print(f"customers : {len(customers_df)}")
    print(f"products  : {len(products_df)}")
    print(f"stores    : {len(stores_df)}")
    print(f"orders    : {len(orders_df)}")
    print(f"payments  : {len(payments_df)}")
    print(f"returns   : {len(returns_df)}")

    print("\nAll files saved successfully.")