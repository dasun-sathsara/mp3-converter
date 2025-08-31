import httpx
from fastapi import HTTPException, status

from config import settings
from logging_config import logger


async def forward_request(
    method: str,
    url: str,
    headers: dict | None = None,
    data: dict | None = None,
    params: dict | None = None,
) -> dict:
    async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
        try:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=e.response.json(),
            )
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service unavailable",
            )
