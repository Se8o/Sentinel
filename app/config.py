"""Configuration management using Pydantic Settings."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(default="Sentinel", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    environment: Literal["development", "staging", "production"] = Field(
        default="development", description="Environment name"
    )
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_key: str = Field(default="dev-key-change-me", description="API authentication key")

    database_url: PostgresDsn = Field(
        default="postgresql+asyncpg://sentinel:sentinel@localhost:5432/sentinel",
        description="PostgreSQL connection URL",
    )
    db_pool_size: int = Field(default=10, description="Database connection pool size")
    db_max_overflow: int = Field(default=20, description="Database max overflow connections")

    check_interval: int = Field(
        default=60, ge=10, le=3600, description="Health check interval in seconds"
    )
    default_timeout: int = Field(
        default=10, ge=1, le=60, description="Default HTTP timeout in seconds"
    )
    max_concurrent_checks: int = Field(
        default=50, ge=1, le=500, description="Maximum concurrent health checks"
    )

    alert_providers: str = Field(default="", description="Comma-separated list of alert providers")
    slack_webhook_url: str = Field(default="", description="Slack webhook URL")
    smtp_host: str = Field(default="", description="SMTP server host")
    smtp_port: int = Field(default=587, description="SMTP server port")
    smtp_user: str = Field(default="", description="SMTP username")
    smtp_password: str = Field(default="", description="SMTP password")
    alert_email_from: str = Field(default="", description="Alert sender email")
    alert_email_to: str = Field(default="", description="Alert recipient email")

    enable_metrics: bool = Field(default=True, description="Enable Prometheus metrics")

    worker_enabled: bool = Field(default=True, description="Enable background worker")
    graceful_shutdown_timeout: int = Field(
        default=30, description="Graceful shutdown timeout in seconds"
    )

    @property
    def enabled_alert_providers(self) -> list[str]:
        """Parse enabled alert providers from comma-separated string."""
        if not self.alert_providers:
            return []
        return [p.strip() for p in self.alert_providers.split(",") if p.strip()]

    @classmethod
    def from_docker_secrets(cls) -> "Settings":
        """Load sensitive settings from Docker secrets in production."""
        secrets_dir = Path("/run/secrets")
        if not secrets_dir.exists():
            return cls()

        overrides = {}
        secret_mappings = {
            "db_password": "db_password",
            "api_key": "api_key",
            "smtp_password": "smtp_password",
        }

        for secret_file, setting_name in secret_mappings.items():
            secret_path = secrets_dir / secret_file
            if secret_path.exists():
                overrides[setting_name] = secret_path.read_text().strip()

        return cls(**overrides)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
