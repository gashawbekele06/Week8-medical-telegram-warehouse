{{
  config(
    materialized = 'view',
    schema = 'staging'
  )
}}

WITH source AS (
  SELECT *
  FROM {{ source('raw', 'telegram_messages') }}
)

SELECT
  message_id,
  channel_username,
  channel_title,
  date::timestamptz AS message_timestamp,
  text AS message_text,
  views AS view_count,
  forwards AS forward_count,
  has_media,
  image_path,
  LENGTH(text) AS message_length,
  CASE WHEN image_path IS NOT NULL THEN TRUE ELSE FALSE END AS has_image,
  DATE(date) AS message_date
FROM source
WHERE 
  text IS NOT NULL 
  AND text != ''
  AND date IS NOT NULL