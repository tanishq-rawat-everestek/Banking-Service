"""
Application configuration settings shared by Python services.
"""

import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = os.getenv("AGILERY_PROJECT_NAME", "Example Service API")
    APPLICATION_VERSION: str = os.getenv("AGILERY_APPLICATION_VERSION", "1.0.0")
    APP_VERSION: str = os.getenv("AGILERY_APP_VERSION", APPLICATION_VERSION)
    SERVICE_NAME: str = os.getenv("AGILERY_SERVICE_NAME", "")
    SERVICE_DESCRIPTION: str = os.getenv(
        "AGILERY_SERVICE_DESCRIPTION",
        "Example python service",
    )
    PORT: int = int(os.getenv("AGILERY_PORT_NUMBER", "8080"))
    CORS_ALLOW_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:3000").split(",")
        if origin.strip()
    ]

    DATABASE_TYPE: str = os.getenv("AGILERY_DATABASE_TYPE", "sqlite")
    DATABASE_USERNAME: str = os.getenv("AGILERY_DATABASE_USERNAME", "")
    DATABASE_PASSWORD: str = os.getenv("AGILERY_DATABASE_PASSWORD", "")
    DATABASE_NAME: str = os.getenv("AGILERY_DATABASE_NAME", "exampledb")
    DATABASE_HOST: str = os.getenv("AGILERY_DATABASE_HOST", "localhost")
    DATABASE_PORT: int = int(os.getenv("AGILERY_DATABASE_PORT", "3306"))

    # Agilery JWT Validation Configuration
    ALLOWED_JWT_ALGORITHM: str = os.getenv(
        "ALLOWED_JWT_ALGORITHM",
        "RS256",
    )
    JWKS_URL: str = os.getenv(
        "JWKS_URL",
        "https://api.dev.agilery.ai/auth-service/oauth2/jwks",
    )
    JWT_AUDIENCE: str = os.getenv(
        "JWT_AUDIENCE",
        "agilery-portal",
    )
    JWT_ISSUER: str = os.getenv(
        "JWT_ISSUER",
        "https://api.dev.agilery.ai/auth-service",
    )

    RETRY_MAX_ATTEMPTS: int = 3
    RETRY_BACKOFF_PERIOD: int = 2
    RETRY_MAX_PERIOD: int = 30

    @property
    def DATABASE_URL(self) -> str:
        if self.DATABASE_TYPE == "sqlite":
            return f"sqlite:///./{self.DATABASE_NAME}.db"
        return (
            f"mysql+pymysql://{self.DATABASE_USERNAME}:"
            f"{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:"
            f"{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
