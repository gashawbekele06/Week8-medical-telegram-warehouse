{{
  config(
    materialized = 'table',
    schema = 'marts'
  )
}}

SELECT
  s.message_id,
  c.channel_key,
  d.date_key,
  s.message_text,
  s.message_length,
  s.view_count,
  s.forward_count,
  s.has_image
FROM {{ ref('stg_telegram_messages') }} s
JOIN {{ ref('dim_channels') }} c ON s.channel_username = c.channel_name   -- ← FIXED: use c.channel_name
JOIN {{ ref('dim_dates') }} d ON s.message_date = d.full_date