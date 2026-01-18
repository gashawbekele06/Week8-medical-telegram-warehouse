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

Week8-medical-telegram-warehouse/ # ← Project root
├── .github/ # GitHub Actions workflows
│ └── workflows/
│ └── unittests.yml
├── .vscode/ # VS Code workspace settings
│ └── settings.json
├── api/ # Task 4 – FastAPI (future)
│ ├── init.py
│ ├── main.py
│ ├── database.py
│ └── schemas.py
├── data/ # Data lake – all raw data lives here
│ └── raw/
│ ├── images/ # Downloaded photos (by channel)
│ │ ├── chemed123/
│ │ │ ├── 12345.jpg
│ │ │ └── ...
│ │ ├── lobelia4cosmetics/
│ │ ├── tikvahpharma/
│ │ ├── ethio_medical/
│ │ └── pharmacyethiopia/
│ └── telegram_messages/ # Raw message metadata (NDJSON, partitioned by date)
│ ├── 2026-01-14/
│ │ ├── chemed123.jsonl
│ │ ├── lobelia4cosmetics.jsonl
│ │ └── ...
│ └── 2026-01-15/
├── medical_warehouse/ # dbt project – core analytics layer
│ ├── dbt_project.yml # Project config
│ ├── profiles.yml # DB connection (gitignored)
│ ├── models/
│ │ ├── staging/
│ │ │ └── stg_telegram_messages.sql # Cleaning & standardization
│ │ └── marts/
│ │ ├── dim_channels.sql # Channel dimension
│ │ ├── dim_dates.sql # Time dimension
│ │ ├── fct_messages.sql # Main fact table
│ │ └── schema.yml # Tests & documentation
│ ├── tests/ # Custom generic tests
│ │ ├── assert_no_future_messages.sql
│ │ └── assert_positive_views.sql
│ ├── analyses/ # (empty – future ad-hoc queries)
│ ├── macros/ # (empty – future reusable macros)
│ ├── seeds/ # (empty – future static data)
│ ├── snapshots/ # (empty – future snapshots)
│ ├── target/ # dbt build artifacts (gitignored)
│ └── logs/ # dbt logs (gitignored)
├── notebooks/ # (empty – future Jupyter exploration)
│ └── init.py
├── src/ # Python scripts
│ ├── scraper.py # Task 1 – Telegram scraper
│ └── load_raw_to_pg.py # Task 2 – Raw loader to PostgreSQL
├── tests/ # (empty – future pytest if needed)
│ └── init.py
├── .env # Secrets (API keys, DB password) – gitignored
├── .gitignore
├── docker-compose.yml # PostgreSQL container
├── Dockerfile # (optional – future containerized env)
├── requirements.txt / pyproject.toml / uv.lock # Python dependencies
├── .python-version # uv pinned Python version
└── README.md # ← This file

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
