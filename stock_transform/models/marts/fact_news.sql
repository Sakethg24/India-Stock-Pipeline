-- models/marts/fact_news.sql
--
-- News articles enriched with time dimension attributes.
-- Useful for:
--   - Counting news volume per day (are there more articles on volatile days?)
--   - Filtering news by month/quarter for trend analysis
--   - Future sentiment analysis (once you add an NLP column)

WITH news AS (
    SELECT * FROM {{ ref('stg_news') }}
),

times AS (
    SELECT * FROM {{ ref('dim_times') }}
)

SELECT
    n.id            AS news_id,
    n.title,
    n.url,
    n.source,
    n.published_at,
    n.summary,

    -- Time breakdown (denormalized from dim_times)
    t.day_of_week,
    t.day_name,
    t.day,
    t.month,
    t.month_name,
    t.quarter,
    t.year,
    t.financial_year,
    t.financial_quarter

FROM news n
-- LEFT JOIN so we keep news articles even if their date isn't in dim_times
-- (e.g. weekend news when market was closed)
LEFT JOIN times t ON n.published_at::DATE = t.date_id
