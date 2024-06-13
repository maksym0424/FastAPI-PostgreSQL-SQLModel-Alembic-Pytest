import os
from functools import lru_cache
from enum import Enum
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"


class Settings(BaseSettings):
    # model_config = SettingsConfigDict(env_file=".env.local", extra="allow")

    # Required settings
    PG_DATABASE_URL: str
    SENDGRID_API_KEY: str
    SENDGRID_FROM_EMAIL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_EXPIRATION_MINUTES: int
    URL_PREFIX: str

    # Optional settings
    ENVIRONMENT: str = Environment.PRODUCTION.value
    ORIGINS: list[str] = ["*"]


@lru_cache
def get_settings():
    return Settings()
