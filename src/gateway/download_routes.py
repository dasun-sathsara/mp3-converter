from __future__ import annotations

import datetime as dt
from typing import Any

import boto3
import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from config import settings

router = APIRouter()


def get_s3_client() -> Any:
    return boto3.client(
        "s3",
        endpoint_url=settings.minio_url,
        aws_access_key_id=settings.minio_access_key,
        aws_secret_access_key=settings.minio_secret_key,
    )


@router.post("/generate-token")
def generate_download_token(payload: dict[str, str]) -> dict[str, str]:
    email = payload.get("email")
    file_key = payload.get("file_key")
    if not email or not file_key:
        raise HTTPException(status_code=400, detail="email and file_key are required")

    expiration = dt.datetime.utcnow() + dt.timedelta(minutes=60)
    to_encode = {"sub": email, "file_key": file_key, "exp": expiration}
    token = jwt.encode(to_encode, settings.download_token_secret, algorithm="HS256")
    return {"token": token}


@router.get("/{token}")
def download_file(token: str, s3_client: Any = Depends(get_s3_client)) -> StreamingResponse:
    try:
        decoded = jwt.decode(
            token,
            settings.download_token_secret,
            algorithms=["HS256"],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_email = decoded.get("sub")
    file_key = decoded.get("file_key")
    if not user_email or not file_key:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    if not file_key.startswith(f"{user_email}/"):
        raise HTTPException(status_code=403, detail="Not authorized for this file")

    try:
        obj = s3_client.get_object(Bucket=settings.minio_bucket_name, Key=file_key)
    except s3_client.exceptions.NoSuchKey:  # type: ignore[attr-defined]
        raise HTTPException(status_code=404, detail="File not found")

    content_type = obj.get("ContentType") or "application/octet-stream"
    filename = file_key.split("/")[-1]

    def stream_body():
        body = obj["Body"]
        while True:
            chunk = body.read(8192)
            if not chunk:
                break
            yield chunk

    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(stream_body(), media_type=content_type, headers=headers)
