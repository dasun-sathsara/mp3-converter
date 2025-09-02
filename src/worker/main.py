from __future__ import annotations

import asyncio
import json
import tempfile
from pathlib import Path

import aio_pika
import aiohttp
import boto3
from aiohttp import ClientTimeout

from config import settings
from logging_config import logger


async def process_message(message: aio_pika.abc.AbstractIncomingMessage) -> None:
    async with message.process(requeue=False):
        try:
            payload = json.loads(message.body.decode())
            url = payload["url"]
            user_name = payload.get("name")
            user_email = payload.get("email")

            # Download file
            async with aiohttp.ClientSession() as session:
                timeout = ClientTimeout(total=120)
                async with session.get(url, timeout=timeout) as resp:
                    resp.raise_for_status()
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as in_file:
                        while True:
                            chunk = await resp.content.read(1 << 15)
                            if not chunk:
                                break
                            in_file.write(chunk)
                        input_path = Path(in_file.name)

            # Convert to mp3 using ffmpeg
            output_path = Path(tempfile.mkstemp(suffix=".mp3")[1])
            cmd = f'ffmpeg -y -i "{input_path}" -vn -ar 44100 -ac 2 -b:a 192k "{output_path}"'
            proc = await asyncio.create_subprocess_shell(
                cmd, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL
            )
            rc = await proc.wait()
            if rc != 0 or not output_path.exists() or output_path.stat().st_size == 0:
                raise RuntimeError("ffmpeg conversion failed")

            # Upload to S3 (MinIO)
            s3 = boto3.client(
                "s3",
                endpoint_url=settings.minio_url,
                aws_access_key_id=settings.minio_access_key,
                aws_secret_access_key=settings.minio_secret_key,
            )

            object_key = f"{user_email}/{output_path.name}"
            s3.upload_file(
                str(output_path),
                settings.minio_bucket_name,
                object_key,
                ExtraArgs={"ContentType": "audio/mpeg"},
            )

            # Publish to audio_out
            connection = await aio_pika.connect_robust(settings.rabbitmq_url)
            async with connection:
                channel = await connection.channel()
                await channel.declare_queue(settings.mp3_out_queue, durable=True)
                out_message = {
                    "name": user_name,
                    "email": user_email,
                    "file_key": object_key,
                }
                await channel.default_exchange.publish(
                    aio_pika.Message(
                        body=json.dumps(out_message).encode(),
                        content_type="application/json",
                        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                    ),
                    routing_key=settings.mp3_out_queue,
                )

            try:
                input_path.unlink(missing_ok=True)
            except Exception:
                logger.warning(f"Failed to delete temp file {input_path}", exc_info=True)
            try:
                Path(output_path).unlink(missing_ok=True)
            except Exception:
                logger.warning(f"Failed to delete temp file {output_path}", exc_info=True)

        except Exception as exc:
            logger.error(f"Failed to process message: {exc}")


async def run() -> None:
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    channel = await connection.channel()
    queue = await channel.declare_queue(settings.audio_in_queue, durable=True)
    await queue.consume(process_message, no_ack=False)
    try:
        await asyncio.Future()
    finally:
        await connection.close()


def main() -> None:
    logger.info("Worker starting")
    asyncio.run(run())


if __name__ == "__main__":
    main()
