from __future__ import annotations

import asyncio
import json

import aio_pika
import httpx

from config import settings
from logging_config import logger

GATEWAY_INTERNAL_URL = "http://gateway-service:80"


async def send_email(name: str | None, email: str, file_key: str) -> None:
    async with httpx.AsyncClient(timeout=10) as http_client:
        try:
            token_resp = await http_client.post(
                f"{GATEWAY_INTERNAL_URL}/download/generate-token",
                json={"email": email, "file_key": file_key},
                timeout=10,
            )
            token_resp.raise_for_status()
            download_token = token_resp.json().get("token")
            if not download_token:
                raise RuntimeError("Invalid token response from gateway")
        except (httpx.HTTPStatusError, httpx.RequestError) as exc:
            logger.error(f"Failed to obtain download token: {exc}")
            raise

    download_url = f"{settings.gateway_external_url}/download/{download_token}"

    subject = "Your MP3 is ready"
    html = (
        f"<p>Hello {name or 'there'},</p>"
        f'<p>Your MP3 file is ready: <a href="{download_url}">Download</a></p>'
        f"<p>Regards,<br/>MP3 Converter</p>"
    )
    async with httpx.AsyncClient(base_url=settings.resend_base_url, timeout=10) as client:
        headers = {
            "Authorization": f"Bearer {settings.resend_api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "from": f"MP3 Converter <{settings.sender_email}>",
            "to": [email],
            "subject": subject,
            "html": html,
        }
        try:
            resp = await client.post("/emails", headers=headers, json=data)
            if resp.status_code >= 400:
                try:
                    error_body = resp.json()
                except ValueError:
                    error_body = resp.text
                logger.error(f"Resend API error {resp.status_code}: {error_body}")
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            request_id = exc.response.headers.get("x-request-id") or exc.response.headers.get(
                "X-Request-ID"
            )
            try:
                body = exc.response.json()
            except ValueError:
                body = exc.response.text
            logger.error(
                f"Failed to send via Resend ({exc.response.status_code}) "
                f"request_id={request_id} body={body}"
            )
            raise


async def process_message(message: aio_pika.abc.AbstractIncomingMessage) -> None:
    async with message.process(requeue=False):
        try:
            payload = json.loads(message.body.decode())
            await send_email(payload.get("name"), payload["email"], payload["file_key"])
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
