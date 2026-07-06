"""
extract/yfinance_ohlc.py

PURPOSE:
    Fetch daily OHLC price data for US stocks using Alpaca API.
    Replaced yfinance because Yahoo Finance blocks cloud server IPs.
    Alpaca works from both local and cloud environments.

DATA RETURNED:
    - ticker     : stock symbol (e.g. AAPL, MSFT)
    - trade_date : date of the trading day
    - open       : opening price in USD
    - high       : highest price of the day
    - low        : lowest price of the day
    - close      : closing price of the day
    - volume     : number of shares traded
"""

import os
import pandas as pd
from datetime import datetime
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from dotenv import load_dotenv

load_dotenv()


def get_client():
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")
    return StockHistoricalDataClient(api_key, secret_key)


def extract_ohlc(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    client = get_client()

    request = StockBarsRequest(
        symbol_or_symbols=ticker,
        timeframe=TimeFrame.Day,
        start=datetime.strptime(start_date, "%Y-%m-%d"),
        end=datetime.strptime(end_date, "%Y-%m-%d"),
    )

    bars = client.get_stock_bars(request)
    df = bars.df

    if df.empty:
        print(f"[ohlc] {ticker}: no data returned")
        return pd.DataFrame()

    df = df.reset_index()
    df = df.rename(columns={"symbol": "ticker", "timestamp": "trade_date"})
    df["trade_date"] = pd.to_datetime(df["trade_date"]).dt.date

    for col in ["open", "high", "low", "close"]:
        df[col] = df[col].round(2)

    df = df[["ticker", "trade_date", "open", "high", "low", "close", "volume"]]
    return df


def extract_all_ohlc(tickers: list, start_date: str, end_date: str) -> pd.DataFrame:
    all_data = []

    for ticker in tickers:
        try:
            df = extract_ohlc(ticker, start_date, end_date)
            if not df.empty:
                all_data.append(df)
               
        except Exception as e:
            print(f"[ohlc] {ticker}: ERROR - {e}")
            continue

    if not all_data:
        print("[ohlc] No data fetched for any ticker!")
        return pd.DataFrame()

    result = pd.concat(all_data, ignore_index=True)
    print(f"[ohlc] Total: {len(result)} rows from {len(all_data)} tickers")
    return result


if __name__ == "__main__":
    test_tickers = ["AAPL", "MSFT", "GOOGL"]
    df = extract_all_ohlc(test_tickers, "2024-01-01", "2024-01-31")
    print(df.head(10))
    print(f"\nTotal rows: {len(df)}")
