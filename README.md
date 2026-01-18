# Medical Telegram Warehouse

End-to-end ELT pipeline for analyzing Ethiopian medical/pharmaceutical Telegram channels  
**Tasks 1–2 complete** – Scraping, data lake, PostgreSQL loading, dbt star schema

## Project Architecture Overview

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

medical-telegram-warehouse/ # Root
├── api/ # Future FastAPI analytical API (Task 4)
├── data/ # Centralized data lake (immutable raw + future processed)
│ ├── raw/ # Original scraped content
│ │ ├── images/ # Downloaded photos (channel_name/message_id.jpg)
│ │ └── telegram_messages/ # Partitioned NDJSON (YYYY-MM-DD/channel.jsonl)
│ └── processed/ # Future cleaned/transformed data
├── logs/ # Runtime logs (scraper, dbt, YOLO, etc.)
├── medical_warehouse/ # dbt project – dimensional warehouse
│ ├── models/
│ │ ├── staging/ # Cleaning & standardization
│ │ └── marts/ # Star schema (dims + facts)
│ ├── tests/ # Custom dbt tests
│ ├── dbt_project.yml
│ └── ...
├── notebooks/ # Jupyter exploration & ad-hoc analysis (currently empty)
├── src/ # Python scripts
│ ├── scraper.py # Telegram scraper (Task 1)
│ └── load_raw_to_pg.py # Raw → PostgreSQL loader (Task 2)
├── tests/ # Future pytest integration (currently empty)
├── .env # Secrets & config (gitignored!)
├── docker-compose.yml # PostgreSQL + optional services
├── Dockerfile # Optional containerized Python env
├── pyproject.toml / uv.lock # uv-managed dependencies
├── .gitignore
└── README.md # ← This file

**Key Layers Explained:**

- **Data Lake** (`data/raw/`): Immutable storage of scraped JSONL + images
- **Raw Warehouse** (`raw.*` tables): Direct 1:1 copy in PostgreSQL
- **Staging** (`staging.*`): Cleaned, typed, filtered view
- **Marts** (`marts.*`): Star schema for analytics (dims + fact)

## Environment Variables (.env – gitignored!)

```env
# Telegram API (required for scraper)
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+2519xxxxxxxx   # optional, for initial login

# PostgreSQL connection
DB_HOST=localhost
DB_PORT=5432
DB_NAME=medical_warehouse
DB_USER=postgres
DB_PASSWORD=your_secure_password_here

```

# Setup & Run Instructions

```
Prerequisites

Python 3.10+ (pinned via .python-version)
PostgreSQL running (recommended: docker-compose up -d)
uv installed (curl -LsSf https://astral.sh/uv/install.sh | sh)
```

## Install Dependencies

```bash
   uv sync
```

## Scrape Telegram Data (Task 1)

```bash
  uv run python src/scraper.py
  # Results → data/raw/telegram_messages/ and data/raw/images/
```

## Load Raw Data to PostgreSQL

```bash
   uv run python src/load_raw_to_pg.py
   # Loads into schema: raw, table: telegram_messages
```

## Build & Test dbt Warehouse (Task 2)

```bash
    cd medical_warehouse
    dbt debug               # Verify connection
    dbt run                 # Build all models (staging + marts)
    dbt test                # Run all quality tests
    dbt docs generate && dbt docs serve   # View docs + interactive lineage graph at http://localhost:8080
```

## Useful Commands

```bash
      # Rebuild single model
      dbt run --select stg_telegram_messages
      # Run specific tests
      dbt test --select dim_channels
      # Clean dbt artifacts
      dbt clean
```

### Summary of Changes Made

- Added **all missing folders** (`data`, `logs`, `notebooks`) with `.gitkeep`
- **Greatly expanded README** with:
  - Full visual folder tree
  - Clear architecture overview
  - Detailed `.env` variable documentation
  - Precise, copy-paste setup & run instructions for each component
- Made the repo feel **complete, professional, and easy to onboard**

After these updates:

- Run `git add . && git commit -m "Improve repo structure + comprehensive README per feedback"`
- Push → your repo will look significantly stronger

Let me know if you want to add screenshots, badges (e.g., Python version, dbt version), or anything else! You're very close to top marks. 🚀
