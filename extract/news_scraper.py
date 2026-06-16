"""
extract/news_scraper.py

PURPOSE:
    Fetch financial news headlines from Google News RSS.

    Why Google News RSS?
    - Always fresh (updated in real time)
    - Never blocks automated requests
    - Aggregates from all major sources: ET, Moneycontrol, Business Standard, etc.
    - Free, no API key needed

DATA RETURNED:
    - title        : article headline
    - url          : link to the full article
    - source       : news outlet (ET, Moneycontrol, etc.)
    - published_at : when the article was published
    - summary      : short description
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from email.utils import parsedate_to_datetime

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q=india+stock+market+NSE&hl=en-IN&gl=IN&ceid=IN:en"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def parse_pubdate(pubdate_str: str) -> datetime:
    try:
        return parsedate_to_datetime(pubdate_str)
    except Exception:
        return datetime.now()


def scrape_moneycontrol() -> pd.DataFrame:
    print("[news] Fetching from Google News RSS...")

    try:
        response = requests.get(GOOGLE_NEWS_RSS, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[news] Request failed: {e}")
        return pd.DataFrame()

    soup = BeautifulSoup(response.text, "xml")
    items = soup.find_all("item")

    if not items:
        print("[news] No articles found in RSS feed")
        return pd.DataFrame()

    articles = []
    for item in items:
        try:
            title = item.find("title").get_text(strip=True) if item.find("title") else ""
            url   = item.find("link").get_text(strip=True) if item.find("link") else ""

            # Google News includes source name in <source> tag
            source_tag = item.find("source")
            source = source_tag.get_text(strip=True) if source_tag else "Google News"

            pubdate_tag  = item.find("pubDate")
            published_at = parse_pubdate(pubdate_tag.text) if pubdate_tag else datetime.now()

            desc_tag = item.find("description")
            summary  = desc_tag.get_text(strip=True) if desc_tag else ""

            articles.append({
                "title":        title,
                "url":          url,
                "source":       source,
                "published_at": published_at,
                "summary":      summary,
            })
        except Exception as e:
            print(f"[news] Failed to parse one article: {e}")
            continue

    df = pd.DataFrame(articles)
    df = df.drop_duplicates(subset="url")

    print(f"[news] Fetched {len(df)} articles from Google News")
    return df


if __name__ == "__main__":
    df = scrape_moneycontrol()
    if not df.empty:
        print(df[["title", "published_at", "source"]].head(10))
    print(f"\nTotal rows: {len(df)}")