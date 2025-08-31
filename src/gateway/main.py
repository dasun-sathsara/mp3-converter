from fastapi import FastAPI

from routes import router

app = FastAPI(title="Gateway Service", version="0.1.0")

# Mount routes
app.include_router(router, prefix="/auth", tags=["auth"])
