"""
Load raw Telegram JSONL files into PostgreSQL raw.telegram_messages
Run with: uv run python src/load_raw_to_pg.py
"""

import json
import os
import psycopg2
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# ─── CONFIG ─────────────────────────────────────────────────────────────────────

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "medical_warehouse")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DATA_ROOT = Path("data/raw/telegram_messages")

# ─── CONNECTION ─────────────────────────────────────────────────────────────────

conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)
conn.autocommit = False
cur = conn.cursor()

# Create schema & table if not exists
cur.execute("""
CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.telegram_messages (
    message_id          BIGINT,
    channel_username    TEXT,
    channel_title       TEXT,
    date                TIMESTAMP WITH TIME ZONE,
    text                TEXT,
    views               INTEGER,
    forwards            INTEGER,
    has_media           BOOLEAN,
    image_path          TEXT,
    loaded_at           TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (message_id, channel_username)
);
""")

# ─── LOAD ALL JSONL FILES ──────────────────────────────────────────────────────

inserted = 0
skipped = 0

for date_dir in DATA_ROOT.iterdir():
    if not date_dir.is_dir():
        continue

    for file_path in date_dir.glob("*.jsonl"):
        channel = file_path.stem

        print(f"Loading {file_path} ...")

        with open(file_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue
                try:
                    msg = json.loads(line)

                    cur.execute("""
                    INSERT INTO raw.telegram_messages (
                        message_id, channel_username, channel_title, date,
                        text, views, forwards, has_media, image_path
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT ON CONSTRAINT telegram_messages_pkey DO NOTHING;
                    """, (
                        msg.get("message_id"),
                        msg.get("channel_username"),
                        msg.get("channel_title"),
                        # ISO string → auto cast to timestamptz
                        msg.get("date"),
                        msg.get("text"),
                        msg.get("views"),
                        msg.get("forwards"),
                        msg.get("has_media"),
                        msg.get("image_path")
                    ))

                    inserted += cur.rowcount
                except (json.JSONDecodeError, KeyError, psycopg2.Error) as e:
                    print(f"  Skip line {line_num} in {file_path}: {e}")
                    skipped += 1

conn.commit()
cur.close()
conn.close()

print(f"\nDone! Inserted: {inserted:,} | Skipped/duplicate: {skipped:,}")
