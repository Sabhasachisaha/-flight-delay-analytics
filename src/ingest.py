"""
ingest.py
---------
Week 1 — Flight Delay Pipeline
Loads BTS on-time performance CSV into a local SQLite database.

Usage:
    python src/ingest.py

Requirements:
    pip install pandas
"""

import pandas as pd
import sqlite3
import os
import sys

# ── Configuration ─────────────────────────────────────────────────────────────

# Path to the CSV you downloaded from BTS
CSV_PATH = os.path.join("data", "flights_raw.csv")

# Where the SQLite database will be created
DB_PATH = os.path.join("data", "flights.db")

# Columns to keep (matches the BTS fields you selected during download)
COLUMNS_TO_KEEP = [
    "Year",
    "Month",
    "DayofMonth",
    "DayOfWeek",
    "UniqueCarrier",
    "Origin",
    "Dest",
    "CRSDepTime",       # scheduled departure time (HHMM format)
    "DepDelay",         # departure delay in minutes
    "ArrDelay",         # arrival delay in minutes
    "Cancelled",        # 1 = cancelled, 0 = not cancelled
    "CarrierDelay",     # delay minutes caused by the carrier
    "WeatherDelay",     # delay minutes caused by weather
    "NASDelay",         # delay minutes caused by National Airspace System
    "Distance",         # flight distance in miles
    "AirTime",          # actual air time in minutes
]


# ── Step 1: Load CSV ───────────────────────────────────────────────────────────

def load_csv(csv_path):
    """Load BTS CSV and keep only the columns we need."""

    if not os.path.exists(csv_path):
        print(f"\nERROR: CSV file not found at '{csv_path}'")
        print("Please follow the instructions in DOWNLOAD_DATA.md first.")
        sys.exit(1)

    print(f"Loading CSV from: {csv_path}")

    # Read only the columns we need (faster on large files)
    df = pd.read_csv(
        csv_path,
        usecols=lambda c: c in COLUMNS_TO_KEEP,
        low_memory=False
    )

    # Keep only the columns we want, in the right order
    existing_cols = [c for c in COLUMNS_TO_KEEP if c in df.columns]
    df = df[existing_cols]

    print(f"  Rows loaded : {len(df):,}")
    print(f"  Columns     : {list(df.columns)}")
    print(f"  Memory usage: {df.memory_usage(deep=True).sum() / 1e6:.1f} MB")

    return df


# ── Step 2: Clean the data ─────────────────────────────────────────────────────

def clean(df):
    """
    Basic cleaning steps:
      - Drop cancelled flights (no delay info available)
      - Fill missing delay values with 0
      - Add IsDelayed column (1 if arrival delay > 15 min) — our ML target label
    """

    print("\nCleaning...")
    original_rows = len(df)

    # Drop cancelled flights
    if "Cancelled" in df.columns:
        df = df[df["Cancelled"] == 0].copy()
        print(f"  Dropped cancelled flights: {original_rows - len(df):,} rows removed")

    # Fill missing delay values with 0
    delay_cols = ["DepDelay", "ArrDelay", "CarrierDelay", "WeatherDelay", "NASDelay"]
    for col in delay_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0)

    # Create target label for ML model (Week 4)
    # Industry standard: a flight is "delayed" if it arrives more than 15 min late
    if "ArrDelay" in df.columns:
        df["IsDelayed"] = (df["ArrDelay"] > 15).astype(int)
        delay_rate = df["IsDelayed"].mean() * 100
        print(f"  Delay rate (ArrDelay > 15 min): {delay_rate:.1f}%")

    print(f"  Final row count: {len(df):,}")
    return df


# ── Step 3: Write to SQLite ────────────────────────────────────────────────────

def write_to_sqlite(df, db_path):
    """Write the cleaned DataFrame to a SQLite database."""

    print(f"\nWriting to SQLite: {db_path}")

    # Remove existing DB so we start fresh
    if os.path.exists(db_path):
        os.remove(db_path)
        print("  Removed existing database.")

    conn = sqlite3.connect(db_path)

    # Write all rows — chunksize helps with memory on large files
    df.to_sql("flights", conn, if_exists="replace", index=False, chunksize=100_000)

    # Verify row count
    count = pd.read_sql("SELECT COUNT(*) as n FROM flights", conn).iloc[0, 0]
    db_size_mb = os.path.getsize(db_path) / 1e6
    print(f"  Rows written  : {count:,}")
    print(f"  Database size : {db_size_mb:.1f} MB")

    conn.close()
    return db_path


# ── Step 4: Sanity check ───────────────────────────────────────────────────────

def sanity_check(db_path):
    """Run a few quick SQL queries to confirm the data looks right."""

    print("\nSanity check queries:")
    conn = sqlite3.connect(db_path)

    # Flights per carrier
    print("\n  Flights per carrier (top 5):")
    result = pd.read_sql("""
        SELECT
            UniqueCarrier,
            COUNT(*)                    AS total_flights,
            ROUND(AVG(ArrDelay), 1)     AS avg_arr_delay_min,
            ROUND(AVG(IsDelayed) * 100, 1) AS pct_delayed
        FROM flights
        GROUP BY UniqueCarrier
        ORDER BY total_flights DESC
        LIMIT 5
    """, conn)
    print(result.to_string(index=False))

    # Flights per month
    print("\n  Flights per month:")
    result = pd.read_sql("""
        SELECT
            Month,
            COUNT(*) AS total_flights
        FROM flights
        GROUP BY Month
        ORDER BY Month
    """, conn)
    print(result.to_string(index=False))

    conn.close()


# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print("  Flight Delay Pipeline — Week 1: Data Ingestion")
    print("=" * 55)

    df = load_csv(CSV_PATH)
    df = clean(df)
    write_to_sqlite(df, DB_PATH)
    sanity_check(DB_PATH)

    print("\nDone. Your SQLite database is ready at:", DB_PATH)
    print("Next step: open notebooks/01_sql_eda.ipynb for Week 2.")
