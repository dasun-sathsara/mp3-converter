import os
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
    minio_url: str = Field(default="http://minio:9000", validation_alias="MINIO_URL")
    minio_bucket_name: str = Field(default="mp3-converter", validation_alias="MINIO_BUCKET_NAME")
    minio_access_key: str = Field(validation_alias="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(validation_alias="MINIO_SECRET_KEY")
    download_token_secret: str = Field(validation_alias="DOWNLOAD_TOKEN_SECRET")


try:
    minio_access_key = os.getenv("MINIO_ACCESS_KEY")
    minio_secret_key = os.getenv("MINIO_SECRET_KEY")
    download_token_secret = os.getenv("DOWNLOAD_TOKEN_SECRET")

    if not minio_access_key or not minio_secret_key:
        raise ValidationError("MINIO_ACCESS_KEY and MINIO_SECRET_KEY must be set.")
    if not download_token_secret:
        raise ValidationError("DOWNLOAD_TOKEN_SECRET must be set.")

    settings = Settings(
        minio_access_key=minio_access_key,
        minio_secret_key=minio_secret_key,
        download_token_secret=download_token_secret,
    )
except ValidationError as exc:
    logger.error(f"Invalid configuration: {exc}")
    sys.exit(1)
