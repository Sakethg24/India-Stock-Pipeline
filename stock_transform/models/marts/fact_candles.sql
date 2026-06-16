-- models/marts/fact_candles.sql
--
-- WHAT IS A FACT TABLE?
-- Fact tables store measurable events — in our case, each trading day's
-- price data for a stock. They contain:
--   1. Foreign keys → link to dimension tables (company, date)
--   2. Measures → the actual numbers analysts care about (prices, volume)
--   3. Derived metrics → calculated from raw measures (price_change, returns)
--
-- This is the CORE table of our warehouse.
-- Analysts use it to answer questions like:
--   - "What was RELIANCE.NS's close price on 15 Jan 2024?"
--   - "Which stocks had the highest volume last week?"
--   - "Show me all IT sector stocks that went up >2% yesterday"
--
-- DENORMALIZATION:
-- We deliberately copy company_name, sector, exchange INTO this fact table
-- even though they already exist in dim_companies. This is called
-- "denormalization" and it makes queries faster (fewer JOINs needed).
-- It's a standard practice in analytical warehouses.

WITH candles AS (
    SELECT * FROM {{ ref('stg_candles') }}
),

companies AS (
    SELECT * FROM {{ ref('dim_companies') }}
),

times AS (
    SELECT * FROM {{ ref('dim_times') }}
),

joined AS (
    SELECT
        -- Foreign keys
        c.ticker            AS company_id,
        t.date_id,

        -- Denormalized company info (so you don't always need to JOIN dim_companies)
        comp.name           AS company_name,
        comp.sector,
        comp.exchange,

        -- Denormalized time info (so you don't always need to JOIN dim_times)
        t.day_of_week,
        t.day_name,
        t.day,
        t.month,
        t.month_name,
        t.quarter,
        t.year,
        t.financial_year,
        t.financial_quarter,

        -- Raw OHLC prices (in INR)
        c.open,
        c.high,
        c.low,
        c.close,
        c.volume,

        -- DERIVED METRICS
        -- Price change: how much the stock moved during the day
        ROUND(c.close - c.open, 2)                              AS price_change,

        -- Price change as a percentage
        -- Formula: ((close - open) / open) * 100
        ROUND(((c.close - c.open) / NULLIF(c.open, 0)) * 100, 4) AS price_change_pct,

        -- Intraday range: how wide was the price swing?
        ROUND(c.high - c.low, 2)                                AS intraday_range,

        -- Price range as percentage of close (volatility indicator)
        ROUND(((c.high - c.low) / NULLIF(c.close, 0)) * 100, 4) AS intraday_range_pct

    FROM candles c
    LEFT JOIN companies comp ON c.ticker = comp.company_id
    LEFT JOIN times t ON c.trade_date = t.date_id
)

SELECT * FROM joined
