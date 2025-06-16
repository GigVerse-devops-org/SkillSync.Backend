from datetime import datetime
import json
import logging
from logtail import LogtailHandler
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api import api_router
from app.core.config import settings
from app.core.exceptions import AppException

class JSONFormatter(logging.Formatter):
    def format(self, record) -> str:
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        if hasattr(record, "extra"):
            log_record.update(record.extra)
        return json.dumps(log_record)

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Add Logtail handler
logtail_handler = LogtailHandler(
    source_token=settings.LOGTAIL_SOURCE_TOKEN,
    host=settings.LOGTAIL_INGESTING_HOST
)
logger.addHandler(logtail_handler)

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="APIs for SkillSync: AI-driven professional platform",
    version="0.1.0"
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle application exceptions."""
    logger.error(
        f"Application error: {exc.message}",
        extra={
            "error_type": "application_error",
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method
        }
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(
        f"Unexpected error: {str(exc)}",
        extra={
            "error_type": "unexpected_error",
            "path": request.url.path,
            "method": request.method
        }
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"}
    )
