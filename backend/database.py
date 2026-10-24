
import sqlite3
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "sales_data.csv"
DB_PATH = BASE_DIR / "sales.db"


def initialize_database():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV file not found: {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)

    required_columns = [
        "Transaction_Id",
        "Order_date",
        "Product",
        "Category",
        "Region",
        "Sales_channel",
        "Quantity",
        "Unit_price",
        "Discount_amount",
        "Status",
    ]

    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        raise ValueError(
            f"CSV is missing columns: {sorted(missing_columns)}"
        )

    df = df[required_columns].copy()

    # Clean dates and numeric columns.
    df["Order_date"] = pd.to_datetime(
        df["Order_date"], dayfirst=True, errors="coerce"
    )
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    df["Unit_price"] = pd.to_numeric(df["Unit_price"], errors="coerce")
    df["Discount_amount"] = pd.to_numeric(
        df["Discount_amount"], errors="coerce"
    )

    # Remove rows with missing essential values.
    df = df.dropna(
        subset=[
            "Transaction_Id",
            "Order_date",
            "Product",
            "Region",
            "Quantity",
            "Unit_price",
            "Discount_amount",
            "Status",
        ]
    )

    # Reject invalid numbers and duplicate transaction IDs.
    df = df[
        (df["Quantity"] > 0)
        & (df["Unit_price"] >= 0)
        & (df["Discount_amount"] >= 0)
        & (df["Discount_amount"] <= df["Quantity"] * df["Unit_price"])
    ]
    df = df.drop_duplicates(subset=["Transaction_Id"])

    df["Order_date"] = df["Order_date"].dt.strftime("%Y-%m-%d")

    with sqlite3.connect(DB_PATH) as conn:
        df.to_sql("sales", conn, if_exists="replace", index=False)

    print(f"Database created: {DB_PATH}")
    print(f"Valid transactions loaded: {len(df)}")
    print(f"Invalid or duplicate rows excluded: {len(pd.read_csv(CSV_PATH)) - len(df)}")


if __name__ == "__main__":
    initialize_database()
