from fastapi import APIRouter, Header

from config import settings
from proxy import forward_request

router = APIRouter()


@router.post("/register")
async def register(user: dict):
    return await forward_request("POST", f"{settings.auth_service_url}/register", data=user)


@router.post("/login")
async def login(authorization: str = Header(...)):
    headers = {"Authorization": authorization}
    return await forward_request("POST", f"{settings.auth_service_url}/login", headers=headers)


@router.post("/validate")
async def validate(authorization: str = Header(...)):
    headers = {"Authorization": authorization}
    return await forward_request("POST", f"{settings.auth_service_url}/validate", headers=headers)
