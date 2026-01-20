"""
Load raw Telegram messages from NDJSON files to PostgreSQL raw schema
Run: uv run python src/load_raw_to_pg.py
"""

import json
from pathlib import Path
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

# Create raw schema and table (drop if exists for fresh load)
cur.execute("""
DROP TABLE IF EXISTS raw.telegram_messages CASCADE;

CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE raw.telegram_messages (
    message_id       BIGINT,
    channel_username TEXT,
    channel_title    TEXT,
    date             TIMESTAMP WITH TIME ZONE,
    text             TEXT,
    views            INTEGER,
    forwards         INTEGER,
    has_media        BOOLEAN,
    image_path       TEXT,
    loaded_at        TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (message_id, channel_username)
);
""")

# Scan data lake and load NDJSON
data_root = Path("data/raw/telegram_messages")
inserted = 0

for date_folder in data_root.iterdir():
    if not date_folder.is_dir():
        continue

    for jsonl_file in date_folder.glob("*.jsonl"):
        channel_username = jsonl_file.stem

        # ← FIXED: UTF-8 + error handling
        with open(jsonl_file, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if not line.strip():
                    continue  # skip empty lines
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"JSON error in {jsonl_file}: {e} - skipping line")
                    continue

                cur.execute("""
                INSERT INTO raw.telegram_messages (
                    message_id, channel_username, channel_title, date, text, views, forwards, has_media, image_path
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
                """, (
                    msg.get('message_id'),
                    channel_username,
                    msg.get('channel_title'),
                    msg.get('date'),
                    msg.get('text'),
                    msg.get('views'),
                    msg.get('forwards'),
                    msg.get('has_media'),
                    msg.get('image_path')
                ))
                inserted += cur.rowcount

conn.commit()
cur.close()
conn.close()

print(f"Raw data loaded! Inserted/updated: {inserted} rows")
