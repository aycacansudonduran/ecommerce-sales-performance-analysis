"""
Olist ham CSV dosyalarını SQLite veritabanına yükler.

Kullanım:
    python src/load_data.py

Girdi : data/raw/*.csv  (Kaggle: olistbr/brazilian-ecommerce)
Çıktı : data/processed/olist.db
"""
import os
import sqlite3

import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "..", "data", "raw")
DB_PATH = os.path.join(BASE_DIR, "..", "data", "processed", "olist.db")

# CSV dosyası -> tablo adı
TABLES = {
    "olist_customers_dataset.csv": "customers",
    "olist_orders_dataset.csv": "orders",
    "olist_order_items_dataset.csv": "order_items",
    "olist_order_payments_dataset.csv": "order_payments",
    "olist_order_reviews_dataset.csv": "order_reviews",
    "olist_products_dataset.csv": "products",
    "olist_sellers_dataset.csv": "sellers",
    "olist_geolocation_dataset.csv": "geolocation",
    "product_category_name_translation.csv": "category_translation",
}

# Sorgularda sık kullanılan JOIN / filtre sütunları
INDEXES = {
    "orders": ["order_id", "customer_id"],
    "customers": ["customer_id", "customer_unique_id"],
    "order_items": ["order_id", "product_id"],
    "order_payments": ["order_id"],
    "order_reviews": ["order_id"],
    "products": ["product_id"],
}


def main():
    missing = [f for f in TABLES if not os.path.exists(os.path.join(RAW_DIR, f))]
    if missing:
        raise SystemExit(
            "data/raw klasöründe eksik dosyalar var:\n  - " + "\n  - ".join(missing)
            + "\nVeri seti: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce"
        )

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        for file_name, table in TABLES.items():
            df = pd.read_csv(os.path.join(RAW_DIR, file_name))
            df.to_sql(table, conn, if_exists="replace", index=False)
            print(f"{table:<22} {len(df):>9,} satır")

        for table, cols in INDEXES.items():
            for col in cols:
                conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_{col} ON {table}({col})")

    print(f"\nVeritabanı hazır: {os.path.normpath(DB_PATH)}")


if __name__ == "__main__":
    main()
