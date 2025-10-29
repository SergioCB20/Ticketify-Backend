from fastapi import APIRouter
from .auth import router as auth_router
from app.api import promotions


# Main API router
api_router = APIRouter(prefix="/api")

# Include routers
api_router.include_router(auth_router)

api_router.include_router(promotions.router)

__all__ = ["api_router"]
