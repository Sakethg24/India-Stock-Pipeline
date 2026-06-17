"""
main_cloud.py — Cloud Pipeline (GitHub Actions)
Runs news scraping only. OHLC skipped (Yahoo Finance blocks cloud IPs).
Run main.py locally for full pipeline.
"""
from extract.companies import extract_all_companies
from extract.news_scraper import scrape_moneycontrol
from load.postgres_loader import load_companies, load_news

def run():
    print("=" * 55)
    print("  INDIA STOCK PIPELINE — CLOUD RUN (News Only)")
    print("=" * 55)

    print("\n[1/3] Extracting Nifty 50 company list...")
    df_companies = extract_all_companies()

    print("\n[2/3] Extracting news from Google News...")
    df_news = scrape_moneycontrol()

    print("\n[3/3] Loading into Supabase...")
    load_companies(df_companies)
    load_news(df_news)

    print("\n" + "=" * 55)
    print("  CLOUD PIPELINE COMPLETE!")
    print("=" * 55)

if __name__ == "__main__":
    run()
