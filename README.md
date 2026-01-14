# Medical Telegram Warehouse

End-to-end data pipeline for Ethiopian medical Telegram channels

**Stack:**

- Telegram scraping → Telethon
- Storage → PostgreSQL + File Data Lake
- Transformation → dbt (ELT)
- Image Analysis → YOLOv8
- API → FastAPI
- Orchestration → Dagster

## Getting Started

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize dbt
cd medical_warehouse
dbt init   # only first time
dbt debug

# Start everything with docker-compose (when ready)
# docker-compose up -d
```
