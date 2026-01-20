{{
  config(
    materialized = 'table',
    schema = 'public_marts'
  )
}}

SELECT
  y.message_id,
  c.channel_key,
  d.date_key,
  y.image_category,
  y.detected_objects,
  y.processed_at
FROM raw.yolo_detections y
JOIN {{ ref('fct_messages') }} f 
  ON y.message_id::bigint = f.message_id
JOIN {{ ref('dim_channels') }} c 
  ON y.channel_name = c.channel_name
JOIN {{ ref('dim_dates') }} d 
  ON DATE(f.message_timestamp) = d.full_date