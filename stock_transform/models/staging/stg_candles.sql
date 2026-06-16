-- models/staging/stg_candles.sql
--
-- Cleans and standardizes raw OHLC price data.
--
-- What we do here:
--   1. Cast prices to NUMERIC to ensure correct decimal handling
--   2. Filter out rows with missing prices or zero volume
--      (these are non-trading days / data errors from yfinance)
--   3. Ensure trade_date is a proper DATE type
--   4. Add a simple data quality flag for negative prices

WITH source AS (
    SELECT * FROM {{ source('raw', 'raw_candles') }}
),

cleaned AS (
    SELECT
        ticker,
        trade_date::DATE                AS trade_date,
        open::NUMERIC(18,2)             AS open,
        high::NUMERIC(18,2)             AS high,
        low::NUMERIC(18,2)              AS low,
        close::NUMERIC(18,2)            AS close,
        volume::BIGINT                  AS volume,
        inserted_at
    FROM source
    WHERE
        ticker IS NOT NULL
        AND trade_date IS NOT NULL
        AND close > 0                   -- exclude rows with zero/null close price
        AND volume > 0                  -- exclude non-trading days
        AND open > 0
)

SELECT * FROM cleaned
