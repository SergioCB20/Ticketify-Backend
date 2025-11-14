"""
Endpoints para el sistema de correos electrónicos
"""

from app.core.dependencies import get_current_user
from app.models.user import User
from app.utils.email_service import email_service
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/emails", tags=["Emails"])


# ============= SCHEMAS =============

class TestEmailRequest(BaseModel):
    """Request para enviar email de prueba"""
    to_email: EmailStr


class WelcomeEmailRequest(BaseModel):
    """Request para enviar email de bienvenida"""
    to_email: EmailStr
    first_name: str


class TicketConfirmationRequest(BaseModel):
    """Request para enviar email de confirmación de ticket"""
    to_email: EmailStr
    first_name: str
    event_title: str
    event_date: str
    event_venue: str
    ticket_count: int
    total_price: float


# ============= ENDPOINTS =============

@router.post("/test")
async def send_test_email(request: TestEmailRequest):
    """
    Enviar un email de prueba

    Este endpoint te permite probar que el sistema de correos funciona correctamente.
    """
    try:
        success = email_service.send_test_email(request.to_email)

        if success:
            return {
                "success": True,
                "message": f"Email de prueba enviado exitosamente a {request.to_email}",
                "email": request.to_email
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="No se pudo enviar el email. Verifica la configuración SMTP."
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al enviar email: {str(e)}"
        )


@router.post("/welcome")
async def send_welcome_email(request: WelcomeEmailRequest):
    """
    Enviar email de bienvenida

    Este email se envía cuando un usuario crea una cuenta nueva.
    """
    try:
        success = email_service.send_welcome_email(
            to_email=request.to_email,
            first_name=request.first_name
        )

        if success:
            return {
                "success": True,
                "message": f"Email de bienvenida enviado a {request.to_email}",
                "email": request.to_email
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="No se pudo enviar el email de bienvenida"
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al enviar email: {str(e)}"
        )


@router.post("/ticket-confirmation")
async def send_ticket_confirmation(request: TicketConfirmationRequest):
    """
    Enviar email de confirmación de compra de tickets

    Este email se envía después de que un usuario compra tickets.
    """
    try:
        success = email_service.send_ticket_confirmation_email(
            to_email=request.to_email,
            first_name=request.first_name,
            event_title=request.event_title,
            event_date=request.event_date,
            event_venue=request.event_venue,
            ticket_count=request.ticket_count,
            total_price=request.total_price
        )

        if success:
            return {
                "success": True,
                "message": f"Email de confirmación enviado a {request.to_email}",
                "email": request.to_email,
                "event": request.event_title
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="No se pudo enviar el email de confirmación"
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al enviar email: {str(e)}"
        )


@router.post("/test-my-email")
async def test_my_email(current_user: User = Depends(get_current_user)):
    """
    Enviar email de prueba a tu propia cuenta

    Endpoint protegido que envía un email de prueba al usuario autenticado.
    """
    try:
        success = email_service.send_test_email(current_user.email)

        if success:
            return {
                "success": True,
                "message": f"Email de prueba enviado a tu correo: {current_user.email}",
                "email": current_user.email
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="No se pudo enviar el email"
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al enviar email: {str(e)}"
        )
