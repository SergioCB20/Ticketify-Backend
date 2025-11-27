from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class CategoryPreferenceResponse(BaseModel):
    """Respuesta de preferencia de categoría individual"""
    id: str
    userId: str = Field(..., alias="userId")
    categoryId: str = Field(..., alias="categoryId")
    categoryName: str = Field(..., alias="categoryName")  # Nombre de la categoría para UI
    isActive: bool = Field(..., alias="isActive")
    lastNotificationSentAt: Optional[datetime] = Field(None, alias="lastNotificationSentAt")
    createdAt: datetime = Field(..., alias="createdAt")
    updatedAt: datetime = Field(..., alias="updatedAt")

    class Config:
        from_attributes = True
        populate_by_name = True


class UserPreferencesResponse(BaseModel):
    """Respuesta con todas las preferencias del usuario"""
    userId: str = Field(..., alias="userId")
    emailNotifications: bool = Field(..., alias="emailNotifications")
    categories: List[CategoryPreferenceResponse] = []

    class Config:
        from_attributes = True
        populate_by_name = True


class UpdateCategoryPreferenceRequest(BaseModel):
    """Request para actualizar preferencia de una categoría"""
    categoryId: str = Field(..., alias="categoryId")
    isActive: bool = Field(..., alias="isActive")

    class Config:
        populate_by_name = True


class UpdateEmailNotificationsRequest(BaseModel):
    """Request para actualizar preferencia de notificaciones por email"""
    emailNotifications: bool = Field(..., alias="emailNotifications")

    class Config:
        populate_by_name = True


class BulkUpdateCategoryPreferencesRequest(BaseModel):
    """Request para actualizar múltiples preferencias de categorías"""
    preferences: List[UpdateCategoryPreferenceRequest]

    class Config:
        populate_by_name = True
