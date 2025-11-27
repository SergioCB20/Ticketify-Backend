from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.models.user import User
from app.models.event_category import EventCategory
from app.models.user_category_preference import UserCategoryPreference
from app.schemas.preferences import (
    CategoryPreferenceResponse,
    UserPreferencesResponse,
    UpdateCategoryPreferenceRequest
)


class PreferencesService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_preferences(self, user_id: UUID) -> UserPreferencesResponse:
        """Obtener todas las preferencias del usuario"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        # Obtener preferencias de categorías
        preferences = self.db.query(UserCategoryPreference).filter(
            UserCategoryPreference.user_id == user_id
        ).all()

        # Convertir a respuesta
        category_preferences = []
        for pref in preferences:
            category = self.db.query(EventCategory).filter(
                EventCategory.id == pref.category_id
            ).first()

            if category:
                category_preferences.append(CategoryPreferenceResponse(
                    id=str(pref.id),
                    userId=str(pref.user_id),
                    categoryId=str(pref.category_id),
                    categoryName=category.name,
                    isActive=pref.is_active,
                    lastNotificationSentAt=pref.last_notification_sent_at,
                    createdAt=pref.created_at,
                    updatedAt=pref.updated_at
                ))

        return UserPreferencesResponse(
            userId=str(user_id),
            emailNotifications=user.emailNotifications,
            categories=category_preferences
        )

    def update_email_notifications(self, user_id: UUID, enabled: bool) -> User:
        """Actualizar preferencia de notificaciones por email"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        user.emailNotifications = enabled
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_category_preference(
        self,
        user_id: UUID,
        category_id: UUID,
        is_active: bool
    ) -> CategoryPreferenceResponse:
        """
        Actualizar preferencia de una categoría.
        Si no existe, la crea. Si existe, actualiza is_active.
        """
        # Verificar que la categoría existe y está activa
        category = self.db.query(EventCategory).filter(
            EventCategory.id == category_id,
            EventCategory.is_active == True
        ).first()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada o inactiva"
            )

        # Buscar preferencia existente
        preference = self.db.query(UserCategoryPreference).filter(
            and_(
                UserCategoryPreference.user_id == user_id,
                UserCategoryPreference.category_id == category_id
            )
        ).first()

        if preference:
            # Actualizar existente
            preference.is_active = is_active
            preference.updated_at = datetime.utcnow()
        else:
            # Crear nueva
            preference = UserCategoryPreference(
                user_id=user_id,
                category_id=category_id,
                is_active=is_active
            )
            self.db.add(preference)

        self.db.commit()
        self.db.refresh(preference)

        return CategoryPreferenceResponse(
            id=str(preference.id),
            userId=str(preference.user_id),
            categoryId=str(preference.category_id),
            categoryName=category.name,
            isActive=preference.is_active,
            lastNotificationSentAt=preference.last_notification_sent_at,
            createdAt=preference.created_at,
            updatedAt=preference.updated_at
        )

    def bulk_update_category_preferences(
        self,
        user_id: UUID,
        preferences: List[UpdateCategoryPreferenceRequest]
    ) -> List[CategoryPreferenceResponse]:
        """Actualizar múltiples preferencias de categorías"""
        results = []
        for pref in preferences:
            try:
                result = self.update_category_preference(
                    user_id=user_id,
                    category_id=UUID(pref.categoryId),
                    is_active=pref.isActive
                )
                results.append(result)
            except HTTPException:
                # Continuar con las demás si una falla
                continue

        return results

    def get_users_subscribed_to_category(
        self,
        category_id: UUID,
        hours_since_last_notification: int = 24
    ) -> List[User]:
        """
        Obtener usuarios suscritos a una categoría que:
        1. Tienen la categoría como favorita activa
        2. Tienen notificaciones por email activas
        3. No han recibido notificación recientemente (según hours_since_last_notification)
        """
        from datetime import timedelta

        cutoff_time = datetime.utcnow() - timedelta(hours=hours_since_last_notification)

        # Query para obtener usuarios que cumplen todos los criterios
        preferences = self.db.query(UserCategoryPreference).filter(
            and_(
                UserCategoryPreference.category_id == category_id,
                UserCategoryPreference.is_active == True,
                # O nunca han recibido notificación, o fue hace más de X horas
                (
                    (UserCategoryPreference.last_notification_sent_at == None) |
                    (UserCategoryPreference.last_notification_sent_at < cutoff_time)
                )
            )
        ).all()

        # Filtrar usuarios con emailNotifications activos
        users = []
        for pref in preferences:
            user = self.db.query(User).filter(
                and_(
                    User.id == pref.user_id,
                    User.isActive == True,
                    User.emailNotifications == True
                )
            ).first()

            if user:
                users.append(user)

        return users

    def mark_notification_sent(self, user_id: UUID, category_id: UUID) -> None:
        """Marcar que se envió una notificación para esta preferencia"""
        preference = self.db.query(UserCategoryPreference).filter(
            and_(
                UserCategoryPreference.user_id == user_id,
                UserCategoryPreference.category_id == category_id
            )
        ).first()

        if preference:
            preference.last_notification_sent_at = datetime.utcnow()
            self.db.commit()
