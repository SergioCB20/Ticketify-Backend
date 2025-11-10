from fastapi import APIRouter
from .auth import router as auth_router
from .admin.users import router as admin_users_router
from .marketplace import router as marketplace_router
from .categories import router as categories_router
from .tickets import router as tickets_router
# Main API router
api_router = APIRouter(prefix="/api")

# Include routers
api_router.include_router(auth_router)
api_router.include_router(admin_users_router)
api_router.include_router(marketplace_router)
api_router.include_router(categories_router)
api_router.include_router(tickets_router)

__all__ = ["api_router"]