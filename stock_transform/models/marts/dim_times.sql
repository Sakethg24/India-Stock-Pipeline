-- models/marts/dim_times.sql
--
-- WHAT IS A DATE DIMENSION?
-- A date dimension is one of the most common tables in any data warehouse.
-- It pre-calculates useful date attributes for every trading date in our data.
--
-- WHY NOT JUST EXTRACT YEAR/MONTH IN THE QUERY DIRECTLY?
-- You could write: EXTRACT(YEAR FROM trade_date) in every query.
-- But a date dimension means you write it once here, and every downstream
-- query just does: JOIN dim_times ON trade_date = date_id
-- This is cleaner, faster, and consistent across all fact tables.
--
-- This is generated from the actual dates in raw_candles,
-- so it only contains dates we actually have data for.

WITH all_dates AS (
    -- Get every unique trading date from our candles data
    SELECT DISTINCT trade_date AS date_id
    FROM {{ source('raw', 'raw_candles') }}
    WHERE trade_date IS NOT NULL
)

SELECT
    date_id,
    date_id                                         AS trade_date,

    -- Day of week: 0 = Sunday, 1 = Monday, ..., 6 = Saturday
    -- NSE trading days are Monday–Friday
    EXTRACT(DOW FROM date_id)::INT                  AS day_of_week,
    TO_CHAR(date_id, 'Day')                         AS day_name,       -- 'Monday', 'Tuesday'...

    EXTRACT(DAY FROM date_id)::INT                  AS day,            -- 1–31
    EXTRACT(MONTH FROM date_id)::INT                AS month,          -- 1–12
    TO_CHAR(date_id, 'Month')                       AS month_name,     -- 'January'...

    EXTRACT(QUARTER FROM date_id)::INT              AS quarter,        -- 1–4
    EXTRACT(YEAR FROM date_id)::INT                 AS year,

    -- Financial year in India runs April–March (not Jan–Dec)
    -- FY2024 = April 2023 – March 2024
    CASE
        WHEN EXTRACT(MONTH FROM date_id) >= 4
        THEN EXTRACT(YEAR FROM date_id)::INT
        ELSE EXTRACT(YEAR FROM date_id)::INT - 1
    END                                             AS financial_year,

    -- Is this date in Q1 of the Indian financial year? (April–June)
    CASE
        WHEN EXTRACT(MONTH FROM date_id) IN (4, 5, 6)   THEN 'Q1'
        WHEN EXTRACT(MONTH FROM date_id) IN (7, 8, 9)   THEN 'Q2'
        WHEN EXTRACT(MONTH FROM date_id) IN (10, 11, 12) THEN 'Q3'
        ELSE 'Q4'
    END                                             AS financial_quarter

FROM all_dates
ORDER BY date_id
