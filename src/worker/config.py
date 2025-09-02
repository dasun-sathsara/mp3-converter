import sys

from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings

from logging_config import logger


class Settings(BaseSettings):
    rabbitmq_url: str = Field(
        validation_alias="RABBITMQ_URL", default="amqp://user:pass@rabbitmq:5672/"
    )
    audio_in_queue: str = Field(validation_alias="AUDIO_IN_QUEUE", default="audio_in")
    mp3_out_queue: str = Field(validation_alias="AUDIO_OUT_QUEUE", default="audio_out")


try:
    settings = Settings()
except ValidationError as exc:
    logger.error(f"Invalid configuration: {exc}")
    sys.exit(1)
