"""
FastAPI main application.

This module initializes the FastAPI application with middleware, routers,
and lifecycle management. It serves as the entry point for the API server.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.health import router as health_router
from app.core.config import settings
from app.core.db import dispose_db, init_db

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.

    Handles startup and shutdown events for the FastAPI application.
    Use this for initializing database connections, schedulers, etc.
    """
    # Startup
    logger.info(
        "Starting %s v%s in %s mode",
        settings.app_name,
        settings.app_version,
        settings.environment,
    )

    # Initialize resources here (database, scheduler, etc.)
    logger.info("Initializing database connection pool")
    init_db()
    logger.info("Database initialized successfully")
    # TODO: Initialize APScheduler if enabled

    yield

    # Shutdown
    logger.info("Shutting down %s", settings.app_name)

    # Cleanup resources here
    logger.info("Closing database connections")
    dispose_db()
    logger.info("Database connections closed")
    # TODO: Shutdown scheduler


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Backend API for Buffett-style stock screening platform",
    debug=settings.debug,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, tags=["health"])


@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for unhandled errors.

    Logs the error and returns a generic error response to the client.
    In production, avoid leaking internal error details.
    """
    logger.error(
        "Unhandled exception: %s",
        str(exc),
        exc_info=True,
        extra={"path": request.url.path, "method": request.method},
    )

    # Return generic error in production, detailed error in development
    if settings.is_production:
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc), "type": type(exc).__name__},
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower(),
    )
