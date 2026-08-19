import logging
from fastapi import FastAPI
from src.api.routes import router as api_router
from src.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(
    title="Инструкция к себе V1.3 Backend",
    description="Психометрический бэкенд и API вебхуков",
    version="1.3.0"
)

app.include_router(api_router)


@app.get("/")
async def root():
    return {
        "title": "Инструкция к себе V1.3",
        "status": "running",
        "docs": "/docs"
    }
