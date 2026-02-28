"""
Health check endpoints.

Provides health and readiness check endpoints for monitoring and load balancers.
These endpoints should be lightweight and indicate the overall health of the service.
"""

from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app import __version__
from app.core.config import settings

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""

    status: Literal["healthy", "unhealthy"] = Field(
        description="Overall health status of the service"
    )
    version: str = Field(description="Application version")
    environment: str = Field(description="Runtime environment")
    timestamp: datetime = Field(description="Current server timestamp in UTC")


class ReadinessResponse(BaseModel):
    """Readiness check response model."""

    ready: bool = Field(description="Whether the service is ready to accept requests")
    checks: dict[str, bool] = Field(description="Individual component readiness checks")
    timestamp: datetime = Field(description="Current server timestamp in UTC")


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns the health status of the API service",
)
async def health_check() -> HealthResponse:
    """
    Basic health check endpoint.

    Returns the current health status of the service. This is a lightweight
    endpoint that should always return 200 OK if the service is running.

    Returns:
        HealthResponse: Service health information
    """
    return HealthResponse(
        status="healthy",
        version=__version__,
        environment=settings.environment,
        timestamp=datetime.now(timezone.utc),
    )


@router.get(
    "/readiness",
    response_model=ReadinessResponse,
    summary="Readiness check",
    description="Returns whether the service is ready to accept requests",
)
async def readiness_check() -> ReadinessResponse:
    """
    Readiness check endpoint.

    Checks whether the service and its dependencies (database, external services)
    are ready to handle requests. Used by load balancers and orchestrators.

    Returns:
        ReadinessResponse: Service readiness information
    """
    checks = {
        "api": True,  # API is running if this endpoint is reachable
        # TODO: Add database connectivity check
        # "database": await check_database_connection(),
        # TODO: Add scheduler health check if enabled
        # "scheduler": check_scheduler_status() if settings.scheduler_enabled else True,
    }

    return ReadinessResponse(
        ready=all(checks.values()),
        checks=checks,
        timestamp=datetime.now(timezone.utc),
    )
