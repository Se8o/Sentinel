"""Domain models for health monitoring."""

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator


class MonitorTarget(BaseModel):
    """Represents an endpoint to monitor.

    This is a domain model that defines what we want to monitor.
    It's framework-agnostic and can be used across the application.
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Human-readable name for the monitor",
    )
    url: HttpUrl = Field(
        ...,
        description="URL to monitor (must be valid HTTP/HTTPS URL)",
    )
    interval: int = Field(
        default=60,
        ge=10,
        le=3600,
        description="Check interval in seconds (10s - 1h)",
    )
    expected_status: int = Field(
        default=200,
        ge=100,
        le=599,
        description="Expected HTTP status code",
    )
    timeout: int = Field(
        default=10,
        ge=1,
        le=60,
        description="Request timeout in seconds",
    )
    enabled: bool = Field(
        default=True,
        description="Whether this monitor is active",
    )

    @field_validator("url")
    @classmethod
    def validate_url_scheme(cls, v: HttpUrl) -> HttpUrl:
        """Ensure only HTTP/HTTPS URLs are allowed."""
        if v.scheme not in ["http", "https"]:
            raise ValueError("Only HTTP and HTTPS URLs are supported")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure name is not just whitespace."""
        if not v.strip():
            raise ValueError("Name cannot be empty or whitespace")
        return v.strip()

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Google",
                    "url": "https://www.google.com",
                    "interval": 60,
                    "expected_status": 200,
                    "timeout": 10,
                    "enabled": True,
                }
            ]
        }
    }


class HealthCheckResult(BaseModel):
    """Result of a health check operation.

    Contains all information about a single health check execution,
    including status, latency, and any errors encountered.
    """

    monitor_name: str = Field(
        ...,
        description="Name of the monitor that was checked",
    )
    url: str = Field(
        ...,
        description="URL that was checked",
    )
    status: Literal["UP", "DOWN", "TIMEOUT", "ERROR"] = Field(
        ...,
        description="Overall health status",
    )
    status_code: int | None = Field(
        default=None,
        description="HTTP status code (if request completed)",
    )
    latency_ms: float | None = Field(
        default=None,
        ge=0,
        description="Response time in milliseconds",
    )
    error_message: str | None = Field(
        default=None,
        description="Error message if check failed",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the check was performed (UTC)",
    )

    @property
    def is_healthy(self) -> bool:
        """Check if the endpoint is considered healthy."""
        return self.status == "UP"

    @property
    def latency_seconds(self) -> float | None:
        """Get latency in seconds."""
        if self.latency_ms is None:
            return None
        return self.latency_ms / 1000.0

    def to_log_dict(self) -> dict:
        """Convert to dictionary suitable for structured logging."""
        return {
            "monitor": self.monitor_name,
            "url": self.url,
            "status": self.status,
            "status_code": self.status_code,
            "latency_ms": self.latency_ms,
            "error": self.error_message,
            "timestamp": self.timestamp.isoformat(),
        }

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "monitor_name": "Google",
                    "url": "https://www.google.com",
                    "status": "UP",
                    "status_code": 200,
                    "latency_ms": 45.2,
                    "error_message": None,
                    "timestamp": "2026-01-30T14:00:00Z",
                }
            ]
        }
    }


class MonitorStats(BaseModel):
    """Aggregated statistics for a monitor.

    Used for reporting and dashboard purposes.
    """

    monitor_name: str
    total_checks: int = Field(ge=0)
    successful_checks: int = Field(ge=0)
    failed_checks: int = Field(ge=0)
    average_latency_ms: float | None = Field(default=None, ge=0)
    uptime_percentage: float = Field(ge=0, le=100)
    last_check_timestamp: datetime | None = None
    last_status: Literal["UP", "DOWN", "TIMEOUT", "ERROR"] | None = None

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_checks == 0:
            return 0.0
        return (self.successful_checks / self.total_checks) * 100

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "monitor_name": "Google",
                    "total_checks": 100,
                    "successful_checks": 98,
                    "failed_checks": 2,
                    "average_latency_ms": 42.5,
                    "uptime_percentage": 98.0,
                    "last_check_timestamp": "2026-01-30T14:00:00Z",
                    "last_status": "UP",
                }
            ]
        }
    }
