from fastapi import FastAPI
from src.endpoints.router import router as api_router
from src.endpoints.router_auth import router as auth_router

app = FastAPI(
    title="Interactive Story Generator",
    version="1.0",
    description="An API for generating interactive stories using AI."
)

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(api_router, prefix="/stories", tags=["Stories"])
