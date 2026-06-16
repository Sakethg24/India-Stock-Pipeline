"""
extract/yfinance_ohlc.py

PURPOSE:
    Fetch daily OHLC (Open, High, Low, Close) price data for
    Indian stocks using the yfinance library.

WHAT IS OHLC?
    Every trading day, a stock has 4 key price points:
    - Open  : price when market opened (9:15 AM IST on NSE)
    - High  : highest price reached that day
    - Low   : lowest price reached that day
    - Close : price when market closed (3:30 PM IST on NSE)
    + Volume: total number of shares traded

    This is called a "candle" in trading charts. OHLC data is
    the foundation of almost all stock market analysis.

HOW yfinance WORKS:
    yfinance is a Python wrapper around Yahoo Finance's API.
    It's free, needs no API key, and covers NSE/BSE stocks.

    Usage:
        import yfinance as yf
        df = yf.download("RELIANCE.NS", start="2024-01-01", end="2024-12-31")

    The .NS suffix tells Yahoo Finance to look on NSE (National Stock Exchange).

DATA RETURNED:
    - ticker     : stock symbol (e.g. RELIANCE.NS)
    - trade_date : the trading date
    - open, high, low, close : prices in INR (Indian Rupees)
    - volume     : number of shares traded

RUN FREQUENCY:
    Daily after market close (after 3:30 PM IST).
"""

import pandas as pd
import yfinance as yf
import time


def extract_ohlc(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    ticker_obj = yf.Ticker(ticker)
    df = ticker_obj.history(start=start_date, end=end_date, auto_adjust=True)

    if df.empty:
        print(f"[ohlc] {ticker}: no data returned")
        return pd.DataFrame()

    df = df.reset_index()
    df.columns = [col.lower() for col in df.columns]
    df = df.rename(columns={"date": "trade_date"})
    df["ticker"] = ticker
    df["trade_date"] = pd.to_datetime(df["trade_date"]).dt.date

    for col in ["open", "high", "low", "close"]:
        df[col] = df[col].round(2)

    df = df[["ticker", "trade_date", "open", "high", "low", "close", "volume"]]
    return df


def extract_all_ohlc(tickers: list, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetch OHLC data for a list of tickers.

    We fetch one ticker at a time with a small delay to be polite
    to Yahoo Finance's servers (avoid getting rate-limited/blocked).

    Args:
        tickers    : list of Yahoo Finance symbols, e.g. ['RELIANCE.NS', 'TCS.NS']
        start_date : start date in 'YYYY-MM-DD'
        end_date   : end date in 'YYYY-MM-DD'

    Returns:
        Combined DataFrame with OHLC for all tickers
    """
    all_data = []

    for i, ticker in enumerate(tickers):
        try:
            df = extract_ohlc(ticker, start_date, end_date)

            if not df.empty:
                all_data.append(df)
                print(f"[ohlc] {ticker}: {len(df)} trading days fetched")

            # Small delay every 10 tickers to avoid rate limiting
            if (i + 1) % 10 == 0:
                time.sleep(1)

        except Exception as e:
            # If one ticker fails, log it and continue with the rest
            print(f"[ohlc] {ticker}: ERROR - {e}")
            continue

    if not all_data:
        print("[ohlc] No data fetched for any ticker!")
        return pd.DataFrame()

    result = pd.concat(all_data, ignore_index=True)
    print(f"[ohlc] Total: {len(result)} rows from {len(all_data)} tickers")
    return result


if __name__ == "__main__":
    # Quick test with 3 big stocks
    test_tickers = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
    df = extract_all_ohlc(test_tickers, "2026-05-01", "2026-05-31")
    print(df.head(10))
    print(f"\nColumns: {df.columns.tolist()}")
    print(f"Total rows: {len(df)}")
