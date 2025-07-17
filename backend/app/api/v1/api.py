"""
API v1 router configuration
"""

from fastapi import APIRouter
from app.api.v1.endpoints import upload, processing, results

# Create API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    upload.router,
    prefix="/upload",
    tags=["upload"]
)

api_router.include_router(
    processing.router,
    prefix="/processing",
    tags=["processing"]
)

api_router.include_router(
    results.router,
    prefix="/results",
    tags=["results"]
)
