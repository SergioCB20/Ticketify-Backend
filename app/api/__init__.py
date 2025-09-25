from fastapi import APIRouter
from .auth import router as auth_router

# Main API router
api_router = APIRouter(prefix="/api")

# Include routers
api_router.include_router(auth_router)

__all__ = ["api_router"]
