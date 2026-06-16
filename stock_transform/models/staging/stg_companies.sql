-- models/staging/stg_companies.sql
--
-- WHAT IS A STAGING MODEL?
-- Staging models are the first transformation step.
-- They clean and standardize raw data without changing its shape.
-- Think of it as "making the data presentable" before analysis.
--
-- What we do here:
--   1. Cast columns to the right data types
--   2. Standardize text (trim whitespace, uppercase sector names)
--   3. Rename columns to consistent naming conventions
--   4. No business logic yet — just cleanup
--
-- This model creates a VIEW (not a table), so it queries raw_companies
-- live each time it's referenced. No data is stored.

WITH source AS (
    -- Read directly from the raw layer
    -- source() is dbt syntax — it references the raw_companies table
    -- and tracks data lineage (you'll see this in the dbt docs graph)
    SELECT * FROM {{ source('raw', 'raw_companies') }}
),

cleaned AS (
    SELECT
        ticker                          AS ticker,
        TRIM(name)                      AS name,           -- remove leading/trailing spaces
        UPPER(TRIM(sector))             AS sector,         -- consistent uppercase
        UPPER(exchange)                 AS exchange,
        COALESCE(is_delisted, FALSE)    AS is_delisted,    -- replace NULL with FALSE
        updated_at
    FROM source
    WHERE ticker IS NOT NULL            -- filter out any bad rows
)

SELECT * FROM cleaned
