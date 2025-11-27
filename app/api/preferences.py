from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.services.preferences_service import PreferencesService
from app.schemas.preferences import (
    UserPreferencesResponse,
    CategoryPreferenceResponse,
    UpdateCategoryPreferenceRequest,
    UpdateEmailNotificationsRequest,
    BulkUpdateCategoryPreferencesRequest
)

router = APIRouter(prefix="/preferences", tags=["User Preferences"])


@router.get("", response_model=UserPreferencesResponse)
async def get_my_preferences(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener todas las preferencias del usuario actual

    Incluye:
    - emailNotifications: si quiere recibir emails
    - categories: lista de categorías favoritas con su estado
    """
    service = PreferencesService(db)
    return service.get_user_preferences(current_user.id)


@router.patch("/email-notifications", response_model=dict)
async def update_email_notifications(
    request: UpdateEmailNotificationsRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Activar o desactivar notificaciones por email
    """
    service = PreferencesService(db)
    user = service.update_email_notifications(
        user_id=current_user.id,
        enabled=request.emailNotifications
    )

    return {
        "message": "Preferencia de notificaciones actualizada",
        "emailNotifications": user.emailNotifications
    }


@router.post("/categories", response_model=CategoryPreferenceResponse)
async def update_category_preference(
    request: UpdateCategoryPreferenceRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Marcar/desmarcar una categoría como favorita

    Si la preferencia no existe, la crea.
    Si existe, actualiza is_active (no hace INSERT, solo UPDATE)
    """
    service = PreferencesService(db)
    return service.update_category_preference(
        user_id=current_user.id,
        category_id=UUID(request.categoryId),
        is_active=request.isActive
    )


@router.post("/categories/bulk", response_model=List[CategoryPreferenceResponse])
async def bulk_update_category_preferences(
    request: BulkUpdateCategoryPreferencesRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar múltiples preferencias de categorías a la vez
    """
    service = PreferencesService(db)
    return service.bulk_update_category_preferences(
        user_id=current_user.id,
        preferences=request.preferences
    )
