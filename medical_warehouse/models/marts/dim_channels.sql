{{
  config(
    materialized = 'table',
    schema = 'marts'
  )
}}

WITH channel_stats AS (
  SELECT
    channel_username,
    channel_title,
    MIN(message_timestamp) AS first_post_date,
    MAX(message_timestamp) AS last_post_date,
    COUNT(*) AS total_posts,
    AVG(view_count) AS avg_views
  FROM {{ ref('stg_telegram_messages') }}
  GROUP BY channel_username, channel_title
)

SELECT
  ROW_NUMBER() OVER (ORDER BY channel_username) AS channel_key,
  channel_username AS channel_name,
  channel_title,
  CASE 
    WHEN LOWER(channel_title) LIKE '%pharma%' OR LOWER(channel_username) LIKE '%pharma%' THEN 'Pharmaceutical'
    WHEN LOWER(channel_title) LIKE '%cosmetic%' THEN 'Cosmetics'
    ELSE 'Medical'
  END AS channel_type,
  first_post_date,
  last_post_date,
  total_posts,
  avg_views
FROM channel_stats