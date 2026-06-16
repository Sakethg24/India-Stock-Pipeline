-- models/staging/stg_news.sql
--
-- Cleans raw news articles.
--
-- What we do here:
--   1. Trim whitespace from title and summary
--   2. Filter out rows missing a title or URL (useless records)
--   3. Normalize published_at to a consistent timestamp

WITH source AS (
    SELECT * FROM {{ source('raw', 'raw_news') }}
),

cleaned AS (
    SELECT
        id,
        TRIM(title)                 AS title,
        url,
        source,
        published_at::TIMESTAMP     AS published_at,
        TRIM(summary)               AS summary,
        inserted_at
    FROM source
    WHERE
        title IS NOT NULL
        AND title != ''
        AND url IS NOT NULL
        AND url != ''
)

SELECT * FROM cleaned
