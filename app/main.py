"""FastAPI application entry point."""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(get_settings().log_level),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    logger.info("application_startup", environment=get_settings().environment)
    
    # TODO: Initialize database
    # TODO: Run migrations
    # TODO: Seed default monitors
    
    yield
    
    logger.info("application_shutdown")
    # TODO: Close database connections
    # TODO: Cleanup resources


settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Infrastructure Health Monitor - Monitor endpoint availability and performance",
    lifespan=lifespan,
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.enable_metrics:
    from prometheus_fastapi_instrumentator import Instrumentator
    
    Instrumentator().instrument(app).expose(app)


@app.get("/health", tags=["Health"])
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }


# TODO: Include API routers
# from app.api.routes import monitors
# app.include_router(monitors.router, prefix="/api/v1", tags=["Monitors"])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
