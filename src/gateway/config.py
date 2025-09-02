import sys

from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings

from logging_config import logger


class Settings(BaseSettings):
    auth_service_url: str = Field(default="http://auth:8000", validation_alias="AUTH_SERVICE_URL")
    request_timeout: int = Field(default=5)
    rabbitmq_url: str = Field(
        default="amqp://user:pass@rabbitmq:5672/", validation_alias="RABBITMQ_URL"
    )
    audio_in_queue: str = Field(default="audio_in", validation_alias="AUDIO_IN_QUEUE")


try:
    settings = Settings()
except ValidationError as exc:
    logger.error(f"Invalid configuration: {exc}")
    sys.exit(1)
