"""
extract/companies.py

PURPOSE:
    Dynamically fetch the full S&P 500 company list from Wikipedia.
"""

import pandas as pd
import requests
import io


def extract_all_companies() -> pd.DataFrame:
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    tables = pd.read_html(io.StringIO(response.text))
    df = tables[0]

    df = df.rename(columns={
        "Symbol":      "ticker",
        "Security":    "name",
        "GICS Sector": "sector",
    })

    # Alpaca uses - instead of . in tickers (e.g. BRK.B → BRK-B)
    df["ticker"] = df["ticker"].str.replace(".", "-", regex=False)
    df["exchange"] = "NASDAQ/NYSE"
    df["is_delisted"] = False

    df = df[["ticker", "name", "sector", "exchange", "is_delisted"]]

    print(f"[companies] {len(df)} companies loaded from S&P 500 Wikipedia list")
    return df


if __name__ == "__main__":
    df = extract_all_companies()
    print(df.head(10))
    print(f"\nTotal: {len(df)} companies")
    print(f"Sectors: {df['sector'].unique().tolist()}")
