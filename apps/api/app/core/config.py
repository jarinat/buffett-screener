"""
Application settings management using Pydantic Settings.

Environment variables are validated and exposed via the global `settings` instance.
Secrets must be provided via environment variables only - never hardcode them.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Settings are validated at startup and accessed via the global `settings` instance.
    Environment variables can be prefixed with APP_ to avoid conflicts.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="Buffett Screener API", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    environment: Literal["development", "staging", "production"] = Field(
        default="development", description="Runtime environment"
    )
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Logging level"
    )

    # API Server
    api_host: str = Field(default="0.0.0.0", description="API server bind address")
    api_port: int = Field(default=8000, description="API server port", ge=1, le=65535)
    api_workers: int = Field(default=1, description="Number of uvicorn workers", ge=1)
    api_reload: bool = Field(
        default=False, description="Enable auto-reload (development only)"
    )

    # CORS
    cors_origins: list[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origins (comma-separated in env)",
    )
    cors_allow_credentials: bool = Field(default=True, description="Allow CORS credentials")

    # Database
    database_url: PostgresDsn = Field(
        default="postgresql://postgres:postgres@localhost:5432/buffett_screener",
        description="PostgreSQL connection URL",
    )
    database_echo: bool = Field(
        default=False, description="Echo SQL queries (development only)"
    )
    database_pool_size: int = Field(
        default=5, description="Database connection pool size", ge=1
    )
    database_max_overflow: int = Field(
        default=10, description="Max database connection overflow", ge=0
    )

    # Scheduler
    scheduler_enabled: bool = Field(
        default=True, description="Enable APScheduler for periodic tasks"
    )
    scheduler_timezone: str = Field(default="UTC", description="Scheduler timezone")

    # Data Ingestion
    ingestion_batch_size: int = Field(
        default=100, description="Batch size for data ingestion", ge=1
    )
    ingestion_retry_attempts: int = Field(
        default=3, description="Number of retry attempts for failed ingestions", ge=0
    )

    # External Data Providers
    yahoo_finance_timeout: int = Field(
        default=30, description="Yahoo Finance API timeout in seconds", ge=1
    )
    yahoo_finance_rate_limit: int = Field(
        default=2000, description="Yahoo Finance requests per hour", ge=1
    )

    # Provider Selection
    default_company_provider: str = Field(
        default="yahoo", description="Default provider for company universe data"
    )
    default_fundamentals_provider: str = Field(
        default="yahoo", description="Default provider for fundamental financial data"
    )
    default_price_provider: str = Field(
        default="yahoo", description="Default provider for price history data"
    )

    # Email (for alerts)
    email_enabled: bool = Field(default=False, description="Enable email notifications")
    smtp_host: str = Field(default="localhost", description="SMTP server host")
    smtp_port: int = Field(default=1025, description="SMTP server port", ge=1, le=65535)
    smtp_user: str = Field(default="", description="SMTP username")
    smtp_password: str = Field(default="", description="SMTP password (use env var)")
    smtp_tls: bool = Field(default=False, description="Use TLS for SMTP")
    smtp_from_email: str = Field(
        default="noreply@buffett-screener.local", description="From email address"
    )

    # Security
    secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        description="Secret key for signing (must be changed in production)",
    )
    allowed_hosts: list[str] = Field(
        default=["*"], description="Allowed host headers (comma-separated in env)"
    )

    @field_validator("cors_origins", "allowed_hosts", mode="before")
    @classmethod
    def parse_comma_separated_list(cls, v: str | list[str]) -> list[str]:
        """Parse comma-separated string into list."""
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

    @field_validator("database_url", mode="after")
    @classmethod
    def validate_database_url(cls, v: PostgresDsn) -> PostgresDsn:
        """Ensure database URL is properly formatted."""
        if not v.scheme or not v.scheme.startswith("postgresql"):
            raise ValueError("Database URL must use postgresql:// or postgresql+psycopg2://")
        return v

    @property
    def database_url_str(self) -> str:
        """Get database URL as string for SQLAlchemy."""
        return str(self.database_url)

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Uses lru_cache to ensure settings are loaded only once.
    This is the recommended way to access settings throughout the application.
    """
    return Settings()


# Global settings instance
# Import and use this in your application code
settings = get_settings()
