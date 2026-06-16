-- ============================================================
-- RAW LAYER — India Stock Data Pipeline
-- Run this once after Docker starts to create the tables.
-- ============================================================

-- CONCEPT: The "raw layer" is where we dump data exactly as
-- received from the source — no cleaning, no transformation.
-- This is the "E" and "L" in ELT. The "T" (transform) happens
-- later in dbt.
--
-- Why keep raw data untouched?
-- - If our transformation logic has a bug, we can re-run dbt
--   without re-fetching data from the API.
-- - We preserve the original data for auditing.
-- - It's the standard practice in modern data engineering.

-- ============================================================
-- TABLE 1: raw_companies
-- Stores the list of companies in our watchlist (Nifty 50).
-- ============================================================
CREATE TABLE IF NOT EXISTS raw_companies (
    ticker       VARCHAR(30) PRIMARY KEY,  -- e.g. RELIANCE.NS
    name         VARCHAR(255),             -- Reliance Industries
    sector       VARCHAR(100),             -- Energy, IT, Banking...
    exchange     VARCHAR(20),              -- NSE or BSE
    is_delisted  BOOLEAN DEFAULT FALSE,    -- still listed?
    updated_at   TIMESTAMP DEFAULT NOW()   -- when we last updated this row
);

-- ============================================================
-- TABLE 2: raw_candles
-- Stores daily OHLC price data for each stock.
-- "Candles" is the trading term for OHLC bars on a price chart.
-- ============================================================
CREATE TABLE IF NOT EXISTS raw_candles (
    id           SERIAL PRIMARY KEY,
    ticker       VARCHAR(30),              -- e.g. RELIANCE.NS
    trade_date   DATE,                     -- 2024-01-15
    open         NUMERIC(18, 2),           -- opening price in INR
    high         NUMERIC(18, 2),           -- highest price in INR
    low          NUMERIC(18, 2),           -- lowest price in INR
    close        NUMERIC(18, 2),           -- closing price in INR
    volume       BIGINT,                   -- shares traded
    inserted_at  TIMESTAMP DEFAULT NOW(),  -- when we inserted this row

    -- UNIQUE constraint: one price record per stock per day
    -- This is what makes our inserts idempotent (safe to re-run)
    UNIQUE (ticker, trade_date)
);

-- ============================================================
-- TABLE 3: raw_news
-- Stores news article headlines fetched from RSS feeds.
-- ============================================================
CREATE TABLE IF NOT EXISTS raw_news (
    id           SERIAL PRIMARY KEY,
    title        TEXT,                     -- article headline
    url          TEXT UNIQUE,              -- article URL (unique = no duplicates)
    source       VARCHAR(100),             -- Economic Times, etc.
    published_at TIMESTAMP,               -- when the article was published
    summary      TEXT,                     -- article summary/description
    inserted_at  TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- INDEXES
-- Indexes make queries faster by pre-sorting the data.
-- Without an index, PostgreSQL scans every row (slow).
-- With an index, it jumps directly to matching rows (fast).
-- ============================================================

-- Speeds up: WHERE ticker = 'RELIANCE.NS' AND trade_date BETWEEN ...
CREATE INDEX IF NOT EXISTS idx_candles_ticker_date
    ON raw_candles (ticker, trade_date);

-- Speeds up: WHERE trade_date = '2024-01-15'
CREATE INDEX IF NOT EXISTS idx_candles_date
    ON raw_candles (trade_date);

-- Speeds up: WHERE published_at >= '2024-01-01'
CREATE INDEX IF NOT EXISTS idx_news_published
    ON raw_news (published_at);
