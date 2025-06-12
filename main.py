import logging
from fastapi import FastAPI
from app.api.router import router as api_router

logging.basicConfig(
    level=logging.info,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

app = FastAPI(
    title="SkillSync Backend",
    description="APIs for SkillSync: AI-driven professional platform",
    version="0.1.0"
)

app.include_router(api_router, prefix="/api")
