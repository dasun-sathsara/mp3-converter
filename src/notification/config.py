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
    # Pydantic will automatically read from environment variables
    # based on the validation_alias settings in the Settings class
    settings = Settings()
except (ValidationError, ValueError) as exc:
    logger.error(f"Invalid configuration: {exc}")
    sys.exit(1)
