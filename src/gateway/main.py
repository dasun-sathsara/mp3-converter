from fastapi import FastAPI

from auth_routes import router as auth_router
from convert_routes import router as convert_router
from download_routes import router as download_router

app = FastAPI(title="Gateway Service", version="0.1.0")

# Mount routes
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(convert_router, prefix="/convert", tags=["convert"])
app.include_router(download_router, prefix="/download", tags=["download"])
