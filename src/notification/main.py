from __future__ import annotations

import asyncio
import json

import aio_pika
import httpx

from config import settings
from logging_config import logger


async def send_email(name: str | None, email: str, mp3_url: str) -> None:
    subject = "Your MP3 is ready"
    text = (
        f"Hello {name or 'there'},\n\nYour MP3 file is ready: {mp3_url}\n\nRegards,\nMP3 Converter"
    )
    async with httpx.AsyncClient(base_url=settings.resend_base_url, timeout=10) as client:
        headers = {"Authorization": f"Bearer {settings.resend_api_key}"}
        data = {
            "from": settings.sender_email,
            "to": [email],
            "subject": subject,
            "text": text,
        }
        resp = await client.post("/emails", headers=headers, json=data)
        resp.raise_for_status()


async def process_message(message: aio_pika.abc.AbstractIncomingMessage) -> None:
    async with message.process(requeue=False):
        try:
            payload = json.loads(message.body.decode())
            await send_email(payload.get("name"), payload["email"], payload["mp3_url"])
        except Exception as exc:
            logger.error(f"Failed to send email: {exc}")


async def run() -> None:
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    channel = await connection.channel()
    queue = await channel.declare_queue(settings.audio_queue, durable=True)
    await queue.consume(process_message, no_ack=False)
    try:
        await asyncio.Future()
    finally:
        await connection.close()


def main() -> None:
    logger.info("Notification consumer starting")
    asyncio.run(run())


if __name__ == "__main__":
    main()
