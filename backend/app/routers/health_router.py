"""
Health Check Endpoint Router
Provides endpoint for monitoring application health and dependencies.
"""

from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException
import time
import psycopg2
from psycopg2 import sql
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])

# Global variable to track application start time
_app_start_time: float = time.time()


class DatabaseHealthStatus(BaseModel):
    """Database health status information."""
    connected: bool = Field(..., description="Whether database is connected")
    latency_ms: float = Field(..., description="Database query latency in milliseconds")
    version: str = Field(..., description="PostgreSQL version")


class HealthCheckResponse(BaseModel):
    """Health check response model."""
    status: str = Field(
        ...,
        description="Overall health status",
        pattern="^(healthy|degraded|unhealthy)$"
    )
    timestamp: datetime = Field(..., description="Timestamp of health check")
    database: DatabaseHealthStatus = Field(..., description="Database health status")
    version: str = Field(..., description="Application version")
    uptime_seconds: float = Field(..., description="Application uptime in seconds")


async def check_database_health(
    database_url: str,
) -> Optional[DatabaseHealthStatus]:
    """
    Check database connection and health.

    Args:
        database_url: PostgreSQL connection string

    Returns:
        DatabaseHealthStatus or None if check fails
    """
    try:
        # Measure latency
        start_time = time.time()

        # Establish connection
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        # Check connection with simple query
        cursor.execute("SELECT 1")
        result = cursor.fetchone()

        # Get PostgreSQL version
        cursor.execute("SELECT version()")
        version_string = cursor.fetchone()[0]

        latency_ms = (time.time() - start_time) * 1000

        cursor.close()
        conn.close()

        return DatabaseHealthStatus(
            connected=True,
            latency_ms=round(latency_ms, 2),
            version=version_string
        )
    except Exception as e:
        logger.warning(f"Database health check failed: {str(e)}")
        return None


def get_uptime_seconds() -> float:
    """
    Get application uptime in seconds.

    Returns:
        Uptime in seconds since application start
    """
    return time.time() - _app_start_time


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    responses={
        200: {"description": "Application is healthy"},
        503: {"description": "Application is degraded or unhealthy"},
    }
)
async def health_check(database_url: str) -> HealthCheckResponse:
    """
    Health check endpoint for monitoring application and dependencies.

    Returns:
        HealthCheckResponse with:
        - status: "healthy" (all systems OK), "degraded" (some issues), "unhealthy" (critical issues)
        - timestamp: Current UTC timestamp
        - database: Database connectivity and latency
        - version: Application version
        - uptime_seconds: Time since application start

    HTTP Status Codes:
        - 200: Healthy
        - 503: Degraded or unhealthy

    Example Response (healthy):
    ```json
    {
        "status": "healthy",
        "timestamp": "2026-02-08T10:30:45.123456Z",
        "database": {
            "connected": true,
            "latency_ms": 2.5,
            "version": "PostgreSQL 15.2"
        },
        "version": "1.0.0",
        "uptime_seconds": 3600.5
    }
    ```
    """
    # Check database health
    db_health = await check_database_health(database_url)

    # Determine overall status
    if db_health is None or not db_health.connected:
        status = "unhealthy"
        status_code = 503
    elif db_health.latency_ms > 100:
        status = "degraded"
        status_code = 503
    else:
        status = "healthy"
        status_code = 200

    response = HealthCheckResponse(
        status=status,
        timestamp=datetime.now(timezone.utc),
        database=db_health or DatabaseHealthStatus(
            connected=False,
            latency_ms=0.0,
            version="Unknown"
        ),
        version="1.0.0",
        uptime_seconds=round(get_uptime_seconds(), 2)
    )

    # Return appropriate status code
    if status_code == 503:
        raise HTTPException(status_code=status_code, detail=response.dict())

    return response
