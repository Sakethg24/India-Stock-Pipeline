"""
load/postgres_loader.py

PURPOSE:
    Take DataFrames from the extract/ scripts and write them
    into PostgreSQL (the raw layer).

KEY CONCEPT — IDEMPOTENCY:
    An operation is "idempotent" if running it multiple times
    produces the same result as running it once.

    Why does this matter?
    - Pipelines fail. Networks drop. APIs time out.
    - When you re-run a failed pipeline, you don't want duplicate data.
    - Solution: use "upsert" instead of plain INSERT.

    Upsert = INSERT ... ON CONFLICT DO NOTHING (or DO UPDATE)
    - If the row doesn't exist → insert it normally
    - If the row already exists → skip it (DO NOTHING) or update it (DO UPDATE)

KEY CONCEPT — CONNECTION MANAGEMENT:
    Every time we connect to PostgreSQL, we use a connection object.
    We must always close it when done, even if an error occurs.
    This prevents "connection leaks" that slow down your database.

FUNCTIONS:
    get_connection()   → creates a PostgreSQL connection
    load_companies()   → upsert company list (DO UPDATE — company info can change)
    load_candles()     → insert OHLC (DO NOTHING — prices don't change after close)
    load_news()        → insert news (DO NOTHING — old articles don't change)
"""

import os
import psycopg2
import psycopg2.extras
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file
# This lets us keep credentials out of the code
load_dotenv()


def get_connection():
    """
    Create and return a PostgreSQL connection.

    Reads credentials from environment variables (.env file).
    Never hardcode database credentials in your code — use env vars.

    Returns:
        psycopg2 connection object
    """
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "stock_raw"),
        user=os.getenv("POSTGRES_USER", "admin"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )


def load_companies(df: pd.DataFrame) -> None:
    """
    Upsert company list into raw_companies.

    Uses DO UPDATE because company info can change:
    - A company might be relisted (is_delisted → False)
    - A company might rename itself
    - Sector classification might be corrected

    Args:
        df : DataFrame from extract/companies.py
    """
    if df.empty:
        print("[load] companies: empty DataFrame, skipping.")
        return

    conn = get_connection()
    cur = conn.cursor()

    sql = """
        INSERT INTO raw_companies (ticker, name, sector, exchange, is_delisted, updated_at)
        VALUES (%s, %s, %s, %s, %s, NOW())
        ON CONFLICT (ticker)
        DO UPDATE SET
            name        = EXCLUDED.name,
            sector      = EXCLUDED.sector,
            exchange    = EXCLUDED.exchange,
            is_delisted = EXCLUDED.is_delisted,
            updated_at  = NOW();
    """

    # Convert DataFrame to a list of tuples for batch insert
    # itertuples() is faster than iterrows() for this use case
    records = [
        (row.ticker, row.name, row.sector, row.exchange, row.is_delisted)
        for row in df.itertuples(index=False)
    ]

    # executemany inserts all rows in one batch — much faster than a loop
    cur.executemany(sql, records)
    conn.commit()

    print(f"[load] companies: upserted {len(records)} rows.")
    cur.close()
    conn.close()


def load_candles(df: pd.DataFrame) -> None:
    """
    Insert OHLC data into raw_candles.

    Uses DO NOTHING because historical prices are immutable:
    - Once a trading day ends, the OHLC values are final
    - If we re-run the pipeline for the same date, just skip existing rows

    Args:
        df : DataFrame from extract/yfinance_ohlc.py
    """
    if df.empty:
        print("[load] candles: empty DataFrame, skipping.")
        return

    conn = get_connection()
    cur = conn.cursor()

    sql = """
        INSERT INTO raw_candles (ticker, trade_date, open, high, low, close, volume)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (ticker, trade_date)
        DO NOTHING;
    """

    records = [
        (row.ticker, row.trade_date, row.open, row.high, row.low, row.close, row.volume)
        for row in df.itertuples(index=False)
    ]

    cur.executemany(sql, records)
    conn.commit()

    print(f"[load] candles: attempted {len(records)} rows (duplicates skipped automatically).")
    cur.close()
    conn.close()


def load_news(df: pd.DataFrame) -> None:
    """
    Insert news articles into raw_news.

    Uses DO NOTHING because the URL is unique:
    - If the same article URL already exists, skip it
    - This prevents duplicate headlines in the database

    Args:
        df : DataFrame from extract/news_scraper.py
    """
    if df.empty:
        print("[load] news: empty DataFrame, skipping.")
        return

    conn = get_connection()
    cur = conn.cursor()

    sql = """
        INSERT INTO raw_news (title, url, source, published_at, summary)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (url)
        DO NOTHING;
    """

    records = [
        (row.title, row.url, row.source, row.published_at, row.summary)
        for row in df.itertuples(index=False)
    ]

    cur.executemany(sql, records)
    conn.commit()

    print(f"[load] news: inserted {len(records)} articles.")
    cur.close()
    conn.close()


if __name__ == "__main__":
    # Test the database connection
    try:
        conn = get_connection()
        params = conn.get_dsn_parameters()
        print(f"[load] Connected to PostgreSQL!")
        print(f"[load] Host: {params['host']}  DB: {params['dbname']}")
        conn.close()
    except Exception as e:
        print(f"[load] Connection failed: {e}")
        print("[load] Make sure Docker is running and .env is configured correctly.")
