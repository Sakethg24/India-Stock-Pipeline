"""
main_cloud.py — Cloud Pipeline Entry Point (GitHub Actions)
Runs full pipeline using Alpaca for OHLC (works from cloud servers).
"""
from extract.companies import extract_all_companies
from extract.yfinance_ohlc import extract_all_ohlc
from extract.news_scraper import scrape_moneycontrol
from load.postgres_loader import load_companies, load_candles, load_news
from datetime import date, timedelta

START_DATE = str(date.today() - timedelta(days=5))
END_DATE   = str(date.today())

def run():
    print("=" * 55)
    print("  US STOCK PIPELINE — CLOUD RUN (S&P 500)")
    print("=" * 55)

    print("\n[1/4] Extracting S&P 500 company list...")
    df_companies = extract_all_companies()

    tickers = df_companies["ticker"].tolist()
    print(f"\n[2/4] Extracting OHLC for {len(tickers)} tickers...")
    df_candles = extract_all_ohlc(tickers, START_DATE, END_DATE)

    print("\n[3/4] Extracting news...")
    df_news = scrape_moneycontrol()

    print("\n[4/4] Loading into Supabase...")
    load_companies(df_companies)
    load_candles(df_candles)
    load_news(df_news)

    print("\n" + "=" * 55)
    print("  CLOUD PIPELINE COMPLETE!")
    print("=" * 55)

if __name__ == "__main__":
    run()
