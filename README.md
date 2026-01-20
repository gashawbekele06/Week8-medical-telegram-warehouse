# Medical Telegram Warehouse

End-to-end ELT pipeline for analyzing Ethiopian medical/pharmaceutical Telegram channels  
**All Tasks 1–5 complete** – Scraping, data lake, PostgreSQL loading, dbt star schema, YOLO image enrichment, FastAPI analytical API, Dagster orchestration

## Project Overview

**Goal:** Collect raw Telegram data → store in data lake → load to PostgreSQL → transform with dbt into a dimensional star schema → enrich with YOLO object detection → expose insights via FastAPI → orchestrate full pipeline with Dagster.

**Business Questions Answered:**

- Top 10 most mentioned medical products/drugs
- Price/availability trends per channel
- Channels with most visual content (images of pills/creams)
- Daily/weekly posting trends
- Image content analysis (promotional vs product display)

**Tech Stack:**

- Scraping: Telethon (Telegram API)
- Orchestration: uv (Python env manager), Dagster
- Storage: Local data lake + PostgreSQL
- Transformation: dbt (postgres adapter)
- Enrichment: Ultralytics YOLOv8 (nano model)
- API: FastAPI + SQLAlchemy
- Testing & Docs: dbt built-in, pytest (optional)

## Project Architecture

- **Data Lake** (`data/raw/`): Immutable scraped JSONL + images
- **Raw Warehouse** (`raw.*` tables): Direct copy in PostgreSQL
- **Staging** (`staging.*`): Cleaned, typed views
- **Marts** (`marts.*`): Star schema (dims + facts)
- **Enrichment** (`raw.yolo_detections`): YOLO results joined to facts
- **API** (`api/`): Analytical endpoints querying marts
- **Orchestration** (`pipeline.py`): Dagster assets/jobs/schedules

## Folder Structure

medical-telegram-warehouse/ # Root
├── api/ # FastAPI analytical API (Task 4)
│ ├── **init**.py
│ ├── main.py # FastAPI app
│ ├── database.py # SQLAlchemy connection
│ └── schemas.py # Pydantic models
├── data/ # Centralized data lake
│ ├── raw/ # Original scraped content
│ │ ├── images/ # Downloaded photos (channel_name/message_id.jpg)
│ │ └── telegram_messages/ # Partitioned NDJSON (YYYY-MM-DD/channel.jsonl)
│ └── processed/ # Future cleaned/transformed (optional)
├── logs/ # Runtime logs (scraper, dbt, YOLO, Dagster)
├── medical_warehouse/ # dbt project – dimensional warehouse (Task 2)
│ ├── models/
│ │ ├── staging/ # Cleaning & standardization
│ │ └── marts/ # Star schema (dims + facts)
│ ├── tests/ # Custom dbt tests
│ ├── dbt_project.yml
│ └── ...
├── notebooks/ # Jupyter exploration & ad-hoc analysis
├── src/ # Python scripts
│ ├── scraper.py # Telegram scraper (Task 1)
│ ├── load_raw_to_pg.py # Raw → PostgreSQL loader (Task 2)
│ ├── yolo_detect.py # YOLO object detection (Task 3)
│ └── load_yolo_to_pg.py # Load YOLO results to PostgreSQL (Task 3)
├── pipeline.py # Dagster orchestration (Task 5)
├── tests/ # pytest integration (optional)
├── .env # Secrets & config (gitignored!)
├── docker-compose.yml # PostgreSQL + optional services
├── Dockerfile # Optional containerized Python env
├── pyproject.toml / uv.lock # uv-managed dependencies
├── .gitignore
└── README.md # ← This file

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


# Setup & Run Instructions

```

Prerequisites
Python 3.10+ (pinned via .python-version)
PostgreSQL running (recommended: docker-compose up -d)
uv installed (curl -LsSf https://astral.sh/uv/install.sh | sh)

````

## Install Dependencies

```bash
   uv sync

````

## Scrape Telegram Data (Task 1)

```bash
    uv run python src/scraper.py
    # Results → data/raw/telegram_messages/ and data/raw/images/
```

## Load Raw Data to PostgreSQL

````bash
      uv run python src/load_raw_to_pg.py
      # Loads into schema: raw, table: telegram_messages

      cd medical_warehouse
      dbt debug               # Verify connection
      dbt run                 # Build all models (staging + marts)
      dbt test                # Run all quality tests
      dbt docs generate && dbt docs serve   # View docs at http://localhost:8080
    ```

## Task 3: YOLO Image Enrichment

```bash
      uv run python src/yolo_detect.py
      # Outputs data/yolo_results.csv

      uv run python src/load_yolo_to_pg.py
      # Loads into raw.yolo_detections

      # Integrate with dbt
      cd medical_warehouse
      dbt run --select fct_image_detections
````

## Task 4: Analytical API (FastAPI)

```bash
     uv run uvicorn api.main:app --reload
     # API docs at http://127.0.0.1:8000/docs
```

## Task 5: Pipeline Orchestration (Dagster)

```bash
    dagster dev -f pipeline.py
    # UI at http://127.0.0.1:3000 – materialize assets or run full job
```

## Useful Commands

```bash
      # Rebuild dbt single model
      dbt run --select stg_telegram_messages

      # Run dbt tests
      dbt test --select dim_channels

      # Clean dbt artifacts
      dbt clean

      # Run Dagster with verbose
      dg dev -f pipeline.py --verbose
```

### Summary

    All 5 tasks implemented:
    Task 1: Scraping + data lake
    Task 2: PostgreSQL raw + dbt star schema
    Task 3: YOLO enrichment + warehouse integration
    Task 4: FastAPI endpoints
    Task 5: Dagster orchestration
