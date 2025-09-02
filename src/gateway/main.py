from fastapi import FastAPI

from auth_routes import router as auth_router
from convert_routes import router as convert_router

app = FastAPI(title="Gateway Service", version="0.1.0")

# Mount routes
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(convert_router, prefix="/convert", tags=["convert"])
