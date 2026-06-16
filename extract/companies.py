"""
extract/companies.py

PURPOSE:
    Build a list of Nifty 50 companies with their metadata.

    Why Nifty 50?
    - It's India's benchmark index (top 50 companies on NSE)
    - Covers all major sectors: banking, IT, energy, FMCG, pharma
    - Great for a portfolio project — well known, publicly discussed

    Why hardcode the list instead of fetching dynamically?
    - NSE's official API requires login and has rate limits
    - yfinance doesn't have a "list all stocks" endpoint
    - Nifty 50 composition changes only 2-4 times a year
    - For a portfolio project, a hardcoded list is perfectly fine
      (production systems would fetch from NSE directly)

DATA RETURNED:
    - ticker   : stock symbol with .NS suffix for NSE (e.g. RELIANCE.NS)
    - name     : company name
    - sector   : broad business sector
    - exchange : always NSE for Nifty 50

HOW yfinance TICKER SYMBOLS WORK:
    yfinance uses Yahoo Finance's naming convention:
    - NSE stocks → append .NS  (e.g. RELIANCE.NS, TCS.NS)
    - BSE stocks → append .BO  (e.g. RELIANCE.BO)
    We use .NS because NSE has better liquidity and data coverage.
"""

import pandas as pd


# Nifty 50 companies as of 2024
# Format: (ticker_with_suffix, company_name, sector)
NIFTY_50 = [
    ("RELIANCE.NS",   "Reliance Industries",          "Energy"),
    ("TCS.NS",        "Tata Consultancy Services",    "IT"),
    ("HDFCBANK.NS",   "HDFC Bank",                    "Banking"),
    ("INFY.NS",       "Infosys",                      "IT"),
    ("ICICIBANK.NS",  "ICICI Bank",                   "Banking"),
    ("HINDUNILVR.NS", "Hindustan Unilever",            "FMCG"),
    ("ITC.NS",        "ITC Limited",                  "FMCG"),
    ("SBIN.NS",       "State Bank of India",          "Banking"),
    ("BHARTIARTL.NS", "Bharti Airtel",                "Telecom"),
    ("KOTAKBANK.NS",  "Kotak Mahindra Bank",          "Banking"),
    ("LT.NS",         "Larsen & Toubro",              "Infrastructure"),
    ("AXISBANK.NS",   "Axis Bank",                    "Banking"),
    ("BAJFINANCE.NS", "Bajaj Finance",                "Finance"),
    ("ASIANPAINT.NS", "Asian Paints",                 "Consumer"),
    ("MARUTI.NS",     "Maruti Suzuki India",          "Automobile"),
    ("WIPRO.NS",      "Wipro",                        "IT"),
    ("HCLTECH.NS",    "HCL Technologies",             "IT"),
    ("ULTRACEMCO.NS", "UltraTech Cement",             "Materials"),
    ("TITAN.NS",      "Titan Company",                "Consumer"),
    ("SUNPHARMA.NS",  "Sun Pharmaceutical Industries","Pharma"),
    ("POWERGRID.NS",  "Power Grid Corporation",       "Utilities"),
    ("NESTLEIND.NS",  "Nestle India",                 "FMCG"),
    ("NTPC.NS",       "NTPC Limited",                 "Utilities"),
    ("ADANIENT.NS",   "Adani Enterprises",            "Conglomerate"),
    ("ADANIPORTS.NS", "Adani Ports & SEZ",            "Infrastructure"),
    ("JSWSTEEL.NS",   "JSW Steel",                    "Metals"),
    ("TATAMOTORS.NS", "Tata Motors",                  "Automobile"),
    ("ONGC.NS",       "Oil & Natural Gas Corporation","Energy"),
    ("TATASTEEL.NS",  "Tata Steel",                   "Metals"),
    ("M&M.NS",        "Mahindra & Mahindra",          "Automobile"),
    ("INDUSINDBK.NS", "IndusInd Bank",                "Banking"),
    ("COALINDIA.NS",  "Coal India",                   "Energy"),
    ("BRITANNIA.NS",  "Britannia Industries",         "FMCG"),
    ("DIVISLAB.NS",   "Divi's Laboratories",          "Pharma"),
    ("DRREDDY.NS",    "Dr. Reddy's Laboratories",     "Pharma"),
    ("CIPLA.NS",      "Cipla",                        "Pharma"),
    ("EICHERMOT.NS",  "Eicher Motors",                "Automobile"),
    ("HEROMOTOCO.NS", "Hero MotoCorp",                "Automobile"),
    ("BAJAJ-AUTO.NS", "Bajaj Auto",                   "Automobile"),
    ("BPCL.NS",       "Bharat Petroleum Corporation", "Energy"),
    ("APOLLOHOSP.NS", "Apollo Hospitals Enterprise",  "Healthcare"),
    ("TECHM.NS",      "Tech Mahindra",                "IT"),
    ("GRASIM.NS",     "Grasim Industries",            "Materials"),
    ("TATACONSUM.NS", "Tata Consumer Products",       "FMCG"),
    ("BAJAJFINSV.NS", "Bajaj Finserv",                "Finance"),
    ("HINDALCO.NS",   "Hindalco Industries",          "Metals"),
    ("SBILIFE.NS",    "SBI Life Insurance",           "Insurance"),
    ("HDFCLIFE.NS",   "HDFC Life Insurance",          "Insurance"),
    ("UPL.NS",        "UPL Limited",                  "Chemicals"),
    ("SHRIRAMFIN.NS", "Shriram Finance",              "Finance"),
]


def extract_all_companies() -> pd.DataFrame:
    """
    Return a DataFrame of all Nifty 50 companies.

    Returns:
        DataFrame with columns: ticker, name, sector, exchange
    """
    df = pd.DataFrame(NIFTY_50, columns=["ticker", "name", "sector"])
    df["exchange"] = "NSE"
    df["is_delisted"] = False

    print(f"[companies] {len(df)} companies loaded from Nifty 50 list")
    return df


if __name__ == "__main__":
    df = extract_all_companies()
    print(df.head(50))
    print(f"\nSectors: {df['sector'].unique().tolist()}")
