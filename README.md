# Medical Telegram Warehouse Project

**End-to-End Data Pipeline for Ethiopian Medical Telegram Channels**  
**Tasks 1 & 2 – Interim Report**

This project builds a modern ELT data platform to extract insights from public Ethiopian Telegram channels selling medical/pharmaceutical products.

**Current Status:** Tasks 1 & 2 completed (scraping + dbt star schema warehouse)

## Project Overview

**Goal:** Collect raw Telegram data → store in data lake → load to PostgreSQL → transform with dbt into a dimensional star schema → enable analytical queries and future enrichment (YOLO image detection).

**Tech Stack (Tasks 1–2):**

- Scraping: Telethon (Telegram API)
- Orchestration: uv (Python project & env manager)
- Storage: Local data lake + PostgreSQL
- Transformation: dbt (postgres adapter)
- Testing & Docs: dbt built-in

## Folder Structure

Week8-medical-telegram-warehouse/
├── .github/ # GitHub Actions (e.g., unit tests)
├── .vscode/ # VS Code settings
├── api/ # FastAPI (Task 4)
├── data/ # Data lake
│ └── raw/
│ ├── images/ # Downloaded photos (channel/message_id.jpg)
│ └── telegram_messages/ # Partitioned NDJSON (YYYY-MM-DD/channel.jsonl)
├── medical_warehouse/ # dbt project (core analytics layer)
│ ├── dbt_project.yml
│ ├── profiles.yml # (gitignored)
│ ├── models/
│ │ ├── staging/
│ │ │ └── stg_telegram_messages.sql
│ │ └── marts/
│ │ ├── dim_channels.sql
│ │ ├── dim_dates.sql
│ │ ├── fct_messages.sql
│ │ └── schema.yml # Tests & documentation
│ ├── tests/ # Custom tests (e.g., assert_no_future_messages.sql)
│ └── ...
├── src/
│ ├── scraper.py # Task 1 – Telegram scraper
│ └── load_raw_to_pg.py # Task 2 – Raw loader to PostgreSQL
├── .env # Secrets (gitignored)
├── docker-compose.yml # PostgreSQL container
├── requirements.txt / pyproject.toml / uv.lock
└── README.md

## Task 1 – Data Scraping & Collection

**Objective:** Extract messages + images from public Telegram channels into a partitioned data lake.

**Channels scraped (working as of Jan 2026):**

- chemed123
- lobelia4cosmetics
- tikvahpharma
- ethio_medical
- pharmacyethiopia

**Data Lake Structure:**

## Task 1 – Data Scraping & Collection

**Objective:** Extract messages + images from public Telegram channels into a partitioned data lake.

**Channels scraped (working as of Jan 2026):**

- chemed123
- lobelia4cosmetics
- tikvahpharma
- ethio_medical
- pharmacyethiopia

**Data Lake Structure:**

**Format:**

- Messages: NDJSON (one JSON per line)
- Fields: message_id, channel_username, channel_title, date, text, views, forwards, has_media, image_path
- Partitioned by date (YYYY-MM-DD) for scalability
- Images saved as `{channel}/{message_id}.jpg`

**Key Script:** `src/scraper.py` (Telethon + tqdm progress + flood wait handling)

**Results (example run):**

- ~487 messages
- ~100–150 images
- Logs in `logs/scraper.log`

## Task 2 – Data Modeling & Transformation

**Objective:** Transform raw messy data into a clean, trusted dimensional star schema using dbt.

**Layers:**

1. **Raw** → `raw.telegram_messages` (table) — direct load from JSONL
2. **Staging** → `staging.stg_telegram_messages` (view) — cleaning, type casting, renaming, filtering invalid
3. **Marts** → Star schema tables in `marts` schema:
   - `dim_dates` — time dimension
   - `dim_channels` — channel dimension with aggregates
   - `fct_messages` — fact table (1 row per message)

## Getting Started (Quick Commands)

```bash
# Activate environment
uv sync

# Scrape more data (Task 1)
uv run python src/scraper.py

# Load raw to PostgreSQL
uv run python src/load_raw_to_pg.py

# Build & test dbt warehouse (Task 2)
cd medical_warehouse
dbt run
dbt test


```
