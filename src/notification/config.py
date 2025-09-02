import os
import sys

from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings

from logging_config import logger


class Settings(BaseSettings):
    resend_api_key: str = Field(..., validation_alias="RESEND_API_KEY")
    rabbitmq_url: str = Field(
        validation_alias="RABBITMQ_URL", default="amqp://user:pass@rabbitmq:5672/"
    )
    rabbitmq_queue: str = Field(validation_alias="RABBITMQ_QUEUE", default="mp3_out")
    sender_email: str = Field(validation_alias="SENDER_EMAIL", default="noreply@dasunsathsara.com")


try:
    resend_api_key = os.environ.get("RESEND_API_KEY")

    if not resend_api_key:
        raise ValidationError("RESEND_API_KEY environment variable is required.")

    settings = Settings(resend_api_key=resend_api_key)
except ValidationError as exc:
    logger.error(f"Invalid configuration: {exc}")
    sys.exit(1)
