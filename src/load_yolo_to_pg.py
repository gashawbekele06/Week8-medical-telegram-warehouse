"""
Load YOLO detection results from CSV to PostgreSQL
Run: uv run python src/load_yolo_to_pg.py
"""

import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME", "medical_warehouse"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", 5432)
)
cur = conn.cursor()

# Create table (drop if exists to start fresh)
cur.execute("""
DROP TABLE IF EXISTS raw.yolo_detections;

CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE raw.yolo_detections (
    message_id       TEXT,
    channel_name     TEXT,
    image_path       TEXT,
    image_category   TEXT,
    detected_objects JSONB,
    processed_at     TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (message_id, channel_name)
);
""")

df = pd.read_csv("data/yolo_results.csv")

inserted = 0
for _, row in df.iterrows():
    detected_json = row["detected_objects"] if pd.notna(
        row["detected_objects"]) else None

    cur.execute("""
    INSERT INTO raw.yolo_detections 
        (message_id, channel_name, image_path, image_category, detected_objects)
    VALUES (%s, %s, %s, %s, %s::jsonb)
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
