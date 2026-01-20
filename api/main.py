"""
FastAPI main application
"""

from fastapi import FastAPI
from api.routers.analytics import router as analytics_router

app = FastAPI(
    title="Medical Telegram Warehouse API",
    description="Analytical API for Ethiopian medical Telegram channels data",
    version="1.0.0"
)

app.include_router(analytics_router)


@app.get("/")
def root():
    return {"message": "Welcome to the Medical Telegram Warehouse API. Visit /docs for documentation."}
