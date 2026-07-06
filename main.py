"""
main.py — Pipeline Entry Point

PURPOSE:
    Run the full Extract → Load pipeline in sequence.
    This is the script you run every day after market close.

    The dbt transformation (T in ELT) is a separate step:
        cd stock_transform && dbt run

HOW TO RUN:
    python main.py

PIPELINE STEPS:
    1. Extract companies  → DataFrame of Nifty 50 stocks
    2. Extract OHLC       → DataFrame of daily prices
    3. Extract news       → DataFrame of articles
    4. Load all           → upsert into PostgreSQL

CONCEPT — ELT vs ETL:
    Old approach (ETL): Extract → Transform → Load
        Transform data BEFORE loading it into the database.
        Downside: if transform logic changes, you lose the original data.

    Modern approach (ELT): Extract → Load → Transform
        Load RAW data first, then transform inside the database using SQL.
        Benefits:
        - Raw data is always preserved (re-run transforms anytime)
        - SQL (via dbt) is better than Python for set-based transformations
        - Easier to debug (you can see the raw data in the DB)
"""

from extract.companies import extract_all_companies
from extract.yfinance_ohlc import extract_all_ohlc
from extract.news_scraper import scrape_moneycontrol
from load.postgres_loader import load_companies, load_candles, load_news
from datetime import date, timedelta

# ──────────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────────




# Date range for historical OHLC data

START_DATE = str(date.today() - timedelta(days=5))  
END_DATE   = str(date.today())                       # today


# ──────────────────────────────────────────────────────────────
# PIPELINE
# ──────────────────────────────────────────────────────────────
def run():
    print("=" * 55)
    print("  US STOCK DATA PIPELINE  (S&P 500)")
    print("=" * 55)

    # STEP 1: Extract companies
    print("\n[1/4] Extracting S&P 500 company list...")
    df_companies = extract_all_companies()

    # STEP 2: Extract OHLC prices
    tickers = df_companies["ticker"].tolist()
    print(f"\n[2/4] Extracting OHLC for {len(tickers)} tickers ({START_DATE} → {END_DATE})...")
    df_candles = extract_all_ohlc(tickers, START_DATE, END_DATE)

    # STEP 3: Extract news
    print("\n[3/4] Extracting news...")
    df_news = scrape_moneycontrol()

    # STEP 4: Load into PostgreSQL
    print("\n[4/4] Loading into PostgreSQL...")
    load_companies(df_companies)
    load_candles(df_candles)
    load_news(df_news)

    print("\n" + "=" * 55)
    print("  PIPELINE COMPLETE!")
    print("=" * 55)


if __name__ == "__main__":
    run()