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

# ──────────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────────

# Nifty 50 tickers to fetch OHLC for
# Must match tickers in extract/companies.py (with .NS suffix)
TICKERS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS",
    "LT.NS", "AXISBANK.NS", "BAJFINANCE.NS", "ASIANPAINT.NS", "MARUTI.NS",
    "WIPRO.NS", "HCLTECH.NS", "ULTRACEMCO.NS", "TITAN.NS", "SUNPHARMA.NS",
    "POWERGRID.NS", "NESTLEIND.NS", "NTPC.NS", "ADANIENT.NS", "ADANIPORTS.NS",
    "JSWSTEEL.NS", "TATAMOTORS.NS", "ONGC.NS", "TATASTEEL.NS", "M&M.NS",
    "INDUSINDBK.NS", "COALINDIA.NS", "BRITANNIA.NS", "DIVISLAB.NS", "DRREDDY.NS",
    "CIPLA.NS", "EICHERMOT.NS", "HEROMOTOCO.NS", "BAJAJ-AUTO.NS", "BPCL.NS",
    "APOLLOHOSP.NS", "TECHM.NS", "GRASIM.NS", "TATACONSUM.NS", "BAJAJFINSV.NS",
    "HINDALCO.NS", "SBILIFE.NS", "HDFCLIFE.NS", "UPL.NS", "SHRIRAMFIN.NS",
]

# Date range for historical OHLC data
# Change END_DATE to "today" for daily incremental runs
START_DATE = "2024-01-01"
END_DATE   = "2024-12-31"


# ──────────────────────────────────────────────────────────────
# PIPELINE
# ──────────────────────────────────────────────────────────────

def run():
    print("=" * 55)
    print("  INDIA STOCK DATA PIPELINE  (NSE — Nifty 50)")
    print("=" * 55)

    # STEP 1: Extract companies
    print("\n[1/4] Extracting Nifty 50 company list...")
    df_companies = extract_all_companies()

    # STEP 2: Extract OHLC prices
    print(f"\n[2/4] Extracting OHLC for {len(TICKERS)} tickers ({START_DATE} → {END_DATE})...")
    df_candles = extract_all_ohlc(TICKERS, START_DATE, END_DATE)

    # STEP 3: Extract news
    print("\n[3/4] Extracting news from Economic Times...")
    df_news = scrape_moneycontrol()

    # STEP 4: Load into PostgreSQL
    print("\n[4/4] Loading into PostgreSQL...")
    load_companies(df_companies)
    load_candles(df_candles)
    load_news(df_news)

    print("\n" + "=" * 55)
    print("  PIPELINE COMPLETE!")
    print("  Next step: cd stock_transform && dbt run")
    print("=" * 55)


if __name__ == "__main__":
    run()
