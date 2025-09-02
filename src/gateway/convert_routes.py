from fastapi import APIRouter

from config import settings
from proxy import forward_request

router = APIRouter()


@router.post("/mp3")
async def register(): ...
