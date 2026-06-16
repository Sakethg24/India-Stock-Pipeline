-- models/marts/dim_companies.sql
--
-- WHAT IS A DIMENSION TABLE?
-- In a data warehouse, data is split into "facts" and "dimensions".
--
-- Dimension tables describe THINGS (people, places, products, companies).
-- They answer: WHO? WHAT? WHERE? WHICH?
--
-- Fact tables store EVENTS or MEASUREMENTS (transactions, prices, events).
-- They answer: HOW MUCH? HOW MANY? WHEN?
--
-- dim_companies describes each stock/company in our watchlist.
-- It's referenced by fact_candles via a foreign key (company_id).
--
-- This model creates a TABLE (physically stored), so dashboards
-- can query it fast without re-processing raw data every time.

WITH stg AS (
    -- Reference the staging model using dbt's ref() function
    -- ref() tracks dependencies: dbt knows dim_companies depends on stg_companies
    -- and will always build stg_companies first
    SELECT * FROM {{ ref('stg_companies') }}
)

SELECT
    ticker              AS company_id,   -- primary key
    ticker,
    name,
    sector,
    exchange,
    is_delisted,
    updated_at
FROM stg
