from fastapi import APIRouter
from .auth import router as auth_router
from .admin.users import router as admin_users_router
from app.api.events import router as events_router
# Main API router
api_router = APIRouter(prefix="/api")

# Include routers
api_router.include_router(auth_router)
api_router.include_router(admin_users_router)
api_router.include_router(events_router, tags=["Events"])
__all__ = ["api_router"]
