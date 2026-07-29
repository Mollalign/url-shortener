from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["development", "staging", "production", "test"]


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------

    app_name: str = Field(default="URL Shortener", alias="APP_NAME")
    environment: Environment = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    base_url: str = Field(default="http://localhost:8000", alias="BASE_URL")
    short_code_length: int = Field(default=7, alias="SHORT_CODE_LENGTH")

    # ------------------------------------------------------------------
    # Security
    # ------------------------------------------------------------------

    secret_key: str = Field(
        default="change-me-in-production-use-a-long-random-string",
        alias="SECRET_KEY",
    )
    trusted_hosts: list[str] = Field(default=["*"], alias="TRUSTED_HOSTS")
    allowed_origins: list[str] = Field(default=["*"], alias="ALLOWED_ORIGINS")

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------

    database_url: str = Field(alias="DATABASE_URL")
    db_pool_size: int = Field(default=10, alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=20, alias="DB_MAX_OVERFLOW")
    db_pool_timeout: int = Field(default=30, alias="DB_POOL_TIMEOUT")
    db_echo: bool = Field(default=False, alias="DB_ECHO")

    # ------------------------------------------------------------------
    # Redis
    # ------------------------------------------------------------------

    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    redis_max_connections: int = Field(default=50, alias="REDIS_MAX_CONNECTIONS")
    cache_ttl_seconds: int = Field(default=3600, alias="CACHE_TTL_SECONDS")

    # ------------------------------------------------------------------
    # JWT
    # ------------------------------------------------------------------

    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=60, alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    # ------------------------------------------------------------------
    # Rate limiting
    # ------------------------------------------------------------------

    rate_limit_enabled: bool = Field(default=True, alias="RATE_LIMIT_ENABLED")
    rate_limit_create_per_minute: int = Field(
        default=60, alias="RATE_LIMIT_CREATE_PER_MINUTE"
    )
    rate_limit_redirect_per_minute: int = Field(
        default=600, alias="RATE_LIMIT_REDIRECT_PER_MINUTE"
    )

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_json: bool = Field(default=False, alias="LOG_JSON")

    # ------------------------------------------------------------------
    # Derived
    # ------------------------------------------------------------------

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @model_validator(mode="after")
    def _configure(self) -> Settings:
        if not self.database_url:
            raise ValueError("DATABASE_URL is required.")
        if self.environment == "development":
            self.db_echo = self.debug
        return self

    @model_validator(mode="after")
    def _validate_production_security(self) -> Settings:
        if not self.is_production:
            return self
        if "change-me-in-production" in self.secret_key:
            raise ValueError("SECRET_KEY must be changed in production.")
        if "*" in self.trusted_hosts:
            raise ValueError("TRUSTED_HOSTS must not include '*' in production.")
        if "*" in self.allowed_origins:
            raise ValueError("ALLOWED_ORIGINS must not include '*' in production.")
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()