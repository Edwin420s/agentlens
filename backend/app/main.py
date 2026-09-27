import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

import app.schemas  # noqa: F401 - ensures forward-ref models are rebuilt
from app.ai.analyzer import provider_available
from app.config import get_settings
from app.db.mongo import close_mongo_connection, connect_to_mongo
from app.db.indexes import ensure_indexes
from app.exceptions import AgentLensError
from app.logging_config import setup_logging
from app.middleware import RequestLoggingMiddleware
from app.schemas.common import APIError, APIResponse

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    await ensure_indexes()
    if not provider_available():
        logger.warning(
            "AI provider is not configured. Session/group AI analysis will be skipped."
        )
    logger.info("AgentLens backend started.")
    yield
    await close_mongo_connection()
    logger.info("AgentLens backend stopped.")


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AgentLens API",
    version="1.0.0",
    description="AI Agent Failure Detection & Investigation Platform",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)


# ---- exception handlers ----

@app.exception_handler(AgentLensError)
async def agentlens_error_handler(request: Request, exc: AgentLensError):
    payload = APIResponse(
        success=False,
        data=None,
        error=APIError(code=exc.code, message=exc.message, details=exc.details),
    )
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    from fastapi.encoders import jsonable_encoder

    sanitized_errors = []
    for err in exc.errors():
        clean_err = dict(err)
        if "ctx" in clean_err and isinstance(clean_err["ctx"], dict):
            clean_err["ctx"] = {
                k: str(v) if isinstance(v, Exception) else v
                for k, v in clean_err["ctx"].items()
            }
        sanitized_errors.append(jsonable_encoder(clean_err))

    payload = APIResponse(
        success=False,
        data=None,
        error=APIError(
            code="VALIDATION_ERROR",
            message="Request validation failed.",
            details=sanitized_errors,
        ),
    )
    return JSONResponse(status_code=422, content=payload.model_dump())


@app.exception_handler(Exception)
async def generic_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception: %s", exc)
    payload = APIResponse(
        success=False,
        data=None,
        error=APIError(code="INTERNAL_ERROR", message=str(exc)[:1000] or "Internal error."),
    )
    return JSONResponse(status_code=500, content=payload.model_dump())


# ---- routers ----

from app.api.routers import (  # noqa: E402
    assistant, dashboard, datasets, export,
    failure_groups, failures, health, investigations, sessions,
)

app.include_router(health.router, tags=["health"])
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(investigations.router, prefix="/api/v1", tags=["investigations"])
app.include_router(datasets.router, prefix="/api/v1", tags=["datasets"])
app.include_router(sessions.router, prefix="/api/v1", tags=["sessions"])
app.include_router(failures.router, prefix="/api/v1", tags=["failures"])
app.include_router(failure_groups.router, prefix="/api/v1", tags=["failure-groups"])
app.include_router(dashboard.router, prefix="/api/v1", tags=["dashboard"])
app.include_router(assistant.router, prefix="/api/v1", tags=["assistant"])
app.include_router(export.router, prefix="/api/v1", tags=["export"])
