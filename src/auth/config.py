import sys

from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings

from logging_config import logger


class Settings(BaseSettings):
    database_url: str = Field(
        default="postgresql+psycopg://user:pass@localhost:5432/auth",
        validation_alias="DATABASE_URL",
    )

    # JWT settings
    jwt_secret: str = Field(default="changeme", validation_alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", validation_alias="JWT_ALGORITHM")
    jwt_expires_minutes: int = Field(default=60, validation_alias="JWT_EXPIRES_MINUTES")


try:
    settings = Settings()
except ValidationError as exc:
    logger.error(f"Invalid configuration: {exc}")
    sys.exit(1)
