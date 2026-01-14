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

### Step 5: First Commit & Push

```bash
# Stage everything
git add .

# First commit
git commit -m "Initial project structure for medical telegram data warehouse"

# Push to GitHub
git push origin main
# or: git push origin master   (depending on your default branch name)

```

#### Step 6: Recommended Next Steps

Create docker-compose.yml with PostgreSQL + (optionally) pgAdmin
Initialize proper dbt project inside medical_warehouse/ folder
Create your first scraper script src/scraper.py
Add GitHub Actions workflow (.github/workflows/unittests.yml)
Protect .env and data/ folder forever
