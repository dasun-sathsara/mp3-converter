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
    audio_queue: str = Field(validation_alias="AUDIO_OUT_QUEUE", default="audio_out")
    sender_email: str = Field(validation_alias="SENDER_EMAIL", default="noreply@dasunsathsara.com")
    resend_base_url: str = Field(default="https://api.resend.com")
    gateway_external_url: str = Field(validation_alias="GATEWAY_EXTERNAL_URL")


try:
    resend_api_key = os.environ.get("RESEND_API_KEY")

    if not resend_api_key:
        raise ValidationError("RESEND_API_KEY environment variable is required.")

    gateway_external_url = os.environ.get("GATEWAY_EXTERNAL_URL")
    if not gateway_external_url:
        raise ValidationError("GATEWAY_EXTERNAL_URL environment variable is required.")

    settings = Settings(resend_api_key=resend_api_key, gateway_external_url=gateway_external_url)
except ValidationError as exc:
    logger.error(f"Invalid configuration: {exc}")
    sys.exit(1)
