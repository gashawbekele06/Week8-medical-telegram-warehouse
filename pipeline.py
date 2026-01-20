"""
Dagster pipeline for Medical Telegram Warehouse
Runs: scrape → load raw → dbt build → YOLO enrichment
"""

from dagster import job, op, schedule, repository, define_asset_job, AssetGroup
from dagster import RunConfig
import subprocess
import os

# Change to project root if needed (Dagster runs from where you launch)
os.chdir(os.path.dirname(os.path.abspath(__file__)))


@op
def scrape_telegram_data():
    """Run the Telegram scraper (Task 1)"""
    result = subprocess.run(
        ["uv", "run", "python", "src/scraper.py"], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Scraper failed: {result.stderr}")
    print("Scrape completed")
    print(result.stdout)


@op
def load_raw_to_postgres():
    """Load raw JSONL to PostgreSQL (Task 1 loader)"""
    result = subprocess.run(
        ["uv", "run", "python", "src/load_raw_to_pg.py"], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Raw load failed: {result.stderr}")
    print("Raw load completed")
    print(result.stdout)


@op
def run_dbt_transformations():
    """Run dbt models (Task 2 warehouse build)"""
    os.chdir("medical_warehouse")
    result = subprocess.run(
        ["dbt", "run", "--full-refresh"], capture_output=True, text=True)
    os.chdir("..")  # back to root
    if result.returncode != 0:
        raise Exception(f"dbt run failed: {result.stderr}")
    print("dbt transformations completed")
    print(result.stdout)


@op
def run_yolo_enrichment():
    """Run YOLO detection and load to DB (Task 3)"""
    # Detection
    detect_result = subprocess.run(
        ["uv", "run", "python", "src/yolo_detect.py"], capture_output=True, text=True)
    if detect_result.returncode != 0:
        raise Exception(f"YOLO detection failed: {detect_result.stderr}")

    # Loader
    load_result = subprocess.run(
        ["uv", "run", "python", "src/load_yolo_to_pg.py"], capture_output=True, text=True)
    if load_result.returncode != 0:
        raise Exception(f"YOLO load failed: {load_result.stderr}")

    print("YOLO enrichment completed")
    print(detect_result.stdout)
    print(load_result.stdout)


@job
def medical_warehouse_pipeline():
    """Full pipeline job with dependencies"""
    run_yolo_enrichment(run_dbt_transformations(
        load_raw_to_postgres(scrape_telegram_data())))

# Optional: Daily schedule (runs at 2 AM EAT)


@schedule(cron_schedule="0 2 * * *", job=medical_warehouse_pipeline, execution_timezone="Africa/Addis_Ababa")
def daily_pipeline_schedule():
    return RunConfig()


@repository
def medical_warehouse_repo():
    return [medical_warehouse_pipeline, daily_pipeline_schedule]
