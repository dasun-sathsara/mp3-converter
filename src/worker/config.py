import os
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
    minio_url: str = Field(validation_alias="MINIO_URL", default="http://minio:9000")
    minio_bucket_name: str = Field(validation_alias="MINIO_BUCKET_NAME", default="mp3-converter")
    minio_access_key: str = Field(validation_alias="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(validation_alias="MINIO_SECRET_KEY")


try:
    minio_access_key = os.getenv("MINIO_ACCESS_KEY")
    minio_secret_key = os.getenv("MINIO_SECRET_KEY")

    if not minio_access_key or not minio_secret_key:
        raise ValidationError(
            "MINIO_ACCESS_KEY and MINIO_SECRET_KEY must be set in environment variables."
        )

    settings = Settings(minio_access_key=minio_access_key, minio_secret_key=minio_secret_key)
except ValidationError as exc:
    logger.error(f"Invalid configuration: {exc}")
    sys.exit(1)
