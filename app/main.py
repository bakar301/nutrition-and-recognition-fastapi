from fastapi import FastAPI
from .routes import image_router

app = FastAPI()

app.include_router(image_router, tags=["images"], prefix="/api/v1")
