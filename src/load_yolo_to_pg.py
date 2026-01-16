import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os
import json  # ← ADD THIS IMPORT

load_dotenv()

conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", 5432)
)
cur = conn.cursor()

# Create table (JSONB for detected_objects)
cur.execute("""
CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.yolo_detections (
    message_id      TEXT,
    channel_name    TEXT,
    image_path      TEXT,
    image_category  TEXT,
    detected_objects JSONB,
    processed_at    TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (message_id, channel_name)
);
""")

# Load CSV
df = pd.read_csv("data/yolo_results.csv")

inserted = 0
for _, row in df.iterrows():
    # Convert Python list/dict → valid JSON string
    detected_json = json.dumps(row["detected_objects"]) if pd.notna(
        row["detected_objects"]) else None

    cur.execute("""
    INSERT INTO raw.yolo_detections (
        message_id, channel_name, image_path, image_category, detected_objects
    ) VALUES (%s, %s, %s, %s, %s::jsonb)
    ON CONFLICT DO NOTHING;
    """, (
        row["message_id"],
        row["channel_name"],
        row["image_path"],
        row["image_category"],
        detected_json
    ))
    inserted += cur.rowcount

conn.commit()
cur.close()
conn.close()

print(f"YOLO results loaded! Inserted/updated: {inserted} rows")
