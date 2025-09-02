from __future__ import annotations

import json
from typing import Any

import aio_pika
import httpx
from fastapi import APIRouter, Body, Header, HTTPException, status
from pydantic import AnyHttpUrl, BaseModel

from config import settings

router = APIRouter()


class ConvertMp3Request(BaseModel):
    url: AnyHttpUrl


async def _validate_user(authorization: str | None) -> dict[str, Any]:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header"
        )

    async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
        try:
            response = await client.post(
                f"{settings.auth_service_url}/validate",
                headers={"Authorization": authorization},
            )
            response.raise_for_status()
            data = response.json()
            if not data.get("valid"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
                )
            return data
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=exc.response.json())
        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Auth unavailable"
            )


@router.post("/mp3", status_code=status.HTTP_202_ACCEPTED)
async def convert_mp3(
    payload: ConvertMp3Request = Body(...),
    authorization: str | None = Header(default=None),
):
    user = await _validate_user(authorization)

    message = {
        "name": user.get("name"),
        "email": user.get("email"),
        "url": str(payload.url),
    }

    try:
        connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Queue unavailable"
        )

    async with connection:
        channel = await connection.channel()
        await channel.declare_queue(settings.audio_in_queue, durable=True)
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(message).encode(),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=settings.audio_in_queue,
        )

    return {"status": "queued"}
