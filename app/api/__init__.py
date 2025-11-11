from fastapi import APIRouter
from .auth import router as auth_router
from .admin import router as admin_users_router
from .marketplace import router as marketplace_router
from .categories import router as categories_router
from .events import router as event_router
from .promotions import router as promotions_router
from .tickets import router as tickets_router
from .purchases import router as purchases_router
from .mercadopago import router as mercadopago_router

# Main API router
api_router = APIRouter(prefix="/api")

# Include routers
api_router.include_router(auth_router)
api_router.include_router(admin_users_router)
api_router.include_router(marketplace_router)
api_router.include_router(categories_router)
api_router.include_router(event_router)
api_router.include_router(promotions_router)
api_router.include_router(tickets_router)
api_router.include_router(purchases_router)
api_router.include_router(mercadopago_router)
__all__ = ["api_router"]