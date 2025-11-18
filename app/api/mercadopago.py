from fastapi import APIRouter, Depends, HTTPException, status, Query, Response, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.services.mercadopago_oauth_service import MercadoPagoOAuthService
from app.services.purchase_service import PurchaseService
from app.models.user import User
from app.schemas.auth import MessageResponse

router = APIRouter(prefix="/mercadopago", tags=["MercadoPago OAuth"])


@router.get("/connect")
async def connect_mercadopago(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Inicia el flujo OAuth de MercadoPago
    
    Redirige al usuario a MercadoPago para autorizar la aplicación.
    Después de autorizar, MercadoPago redirigirá al callback.
    
    **Flujo:**
    1. Usuario hace clic en "Vincular MercadoPago"
    2. Se redirige a este endpoint
    3. Este endpoint redirige a MercadoPago
    4. Usuario autoriza en MercadoPago
    5. MercadoPago redirige a /mercadopago/callback
    """
    # Verificar si ya tiene cuenta vinculada
    if current_user.isMercadopagoConnected:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya tienes una cuenta de MercadoPago vinculada. Desvincúlala primero."
        )
    
    mp_service = MercadoPagoOAuthService(db)
    
    # Generar URL de autorización (usa MERCADOPAGO_FORCE_LOGOUT del .env)
    auth_url = mp_service.get_authorization_url(str(current_user.id))
    
    # Redirigir a MercadoPago
    return RedirectResponse(url=auth_url)


@router.get("/callback")
async def mercadopago_callback(
    code: str = Query(..., description="Authorization code from MercadoPago"),
    state: str = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Callback de MercadoPago OAuth
    
    MercadoPago redirige aquí después de que el usuario autoriza.
    Este endpoint intercambia el código por tokens y guarda la conexión.
    
    **Parámetros:**
    - code: Código de autorización
    - state: ID del usuario (pasado en el paso anterior)
    
    **Resultado:**
    Redirige al frontend con resultado (success o error)
    """
    import uuid
    import logging
    import traceback
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"🔵 Callback recibido - Code: {code[:20]}..., State: {state}")
        
        # Convertir state a UUID
        user_id = uuid.UUID(state)
        logger.info(f"✅ UUID válido: {user_id}")
        
        # Completar OAuth flow
        mp_service = MercadoPagoOAuthService(db)
        logger.info("🔵 Iniciando connect_account...")
        
        user = mp_service.connect_account(user_id, code)
        
        logger.info(f"✅ Cuenta conectada exitosamente: {user.mercadopagoEmail}")
        
        # Redirigir al frontend con éxito
        return RedirectResponse(
            url=f"http://localhost:3000/panel/profile?mp=success&email={user.mercadopagoEmail}"
        )
    
    except ValueError as e:
        # State inválido
        logger.error(f"❌ ValueError en callback: {str(e)}")
        logger.error(traceback.format_exc())
        return RedirectResponse(
            url="http://localhost:3000/panel/profile?mp=error&reason=invalid_state"
        )
    
    except HTTPException as e:
        # Error en el proceso OAuth
        logger.error(f"❌ HTTPException en callback: {e.detail}")
        logger.error(traceback.format_exc())
        return RedirectResponse(
            url=f"http://localhost:3000/panel/profile?mp=error&reason={e.detail}"
        )
    
    except Exception as e:
        # Error inesperado - LOGGEAR DETALLES COMPLETOS
        logger.error(f"❌ Exception INESPERADA en callback: {type(e).__name__}: {str(e)}")
        logger.error(f"Traceback completo:\n{traceback.format_exc()}")
        return RedirectResponse(
            url=f"http://localhost:3000/panel/profile?mp=error&reason=unknown"
        )


@router.delete("/disconnect", response_model=MessageResponse)
async def disconnect_mercadopago(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Desvincula la cuenta de MercadoPago
    
    Elimina todos los tokens y datos de conexión de MercadoPago.
    El usuario podrá volver a vincular su cuenta después.
    """
    mp_service = MercadoPagoOAuthService(db)
    mp_service.disconnect_account(current_user.id)
    
    return MessageResponse(
        message="Cuenta de MercadoPago desvinculada exitosamente",
        success=True
    )


@router.get("/status")
async def get_mercadopago_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene el estado de conexión de MercadoPago
    
    Retorna información sobre si el usuario tiene una cuenta vinculada,
    el email de la cuenta, fecha de conexión, y si el token está expirado.
    
    **Respuesta:**
    ```json
    {
      "isConnected": true,
      "email": "vendedor@mercadopago.com",
      "connectedAt": "2025-11-05T10:30:00Z",
      "tokenExpired": false
    }
    ```
    """
    mp_service = MercadoPagoOAuthService(db)
    return mp_service.get_connection_status(current_user.id)


@router.get("/test-connect")
async def test_connect_mercadopago(
    token: str = Query(..., description="Access token del usuario"),
    db: Session = Depends(get_db)
):
    """
    **SOLO PARA TESTING** - Endpoint temporal para probar OAuth desde navegador
    
    Acepta token por query param en lugar de header.
    Usar solo en desarrollo.
    
    **Uso:**
    1. Login en /docs y copiar accessToken
    2. python test_mp_connect.py TU_TOKEN
    3. O abrir: http://localhost:8000/api/mercadopago/test-connect?token=TU_TOKEN
    """
    from app.utils.security import verify_token
    from app.core.dependencies import get_current_user
    import uuid
    
    try:
        # Verificar token
        payload = verify_token(token, "access")
        user_id = payload.get("user_id")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
        # Obtener usuario
        from app.repositories.user_repository import UserRepository
        user_repo = UserRepository(db)
        current_user = user_repo.get_by_id(uuid.UUID(user_id))
        
        if not current_user or not current_user.isActive:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado o inactivo"
            )
        
        # Verificar si ya tiene cuenta vinculada
        if current_user.isMercadopagoConnected:
            return RedirectResponse(
                url="http://localhost:3000/panel/profile?mp=error&reason=already_connected"
            )
        
        # Generar URL de autorización (usa MERCADOPAGO_FORCE_LOGOUT del .env)
        mp_service = MercadoPagoOAuthService(db)
        auth_url = mp_service.get_authorization_url(str(current_user.id))
        
        # Redirigir a MercadoPago
        return RedirectResponse(url=auth_url)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido: {str(e)}"
        )

@router.post("/webhook")
async def mercadopago_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Recibe notificaciones de pago de MercadoPago.
    """
    body = await request.json()
    topic = body.get("topic")
    
    if topic == "payment":
        payment_id = body.get("data", {}).get("id")
        if not payment_id:
            return status.HTTP_200_OK # No podemos hacer nada
        try:
            # Inicializar SDK de plataforma para *consultar* el pago
            sdk = mercadopago.SDK(settings.MERCADOPAGO_PRODUCER_TOKEN)
            payment_data = sdk.payment().get(payment_id)["response"]
            
            status_detail = payment_data.get("status")
            external_reference = payment_data.get("external_reference")

            if not external_reference:
                 raise Exception(f"Pago {payment_id} sin external_reference")

            # Buscar la compra en nuestra BBDD
            purchase = db.query(Purchase).filter(Purchase.id == external_reference).first()
            if not purchase:
                raise Exception(f"Compra {external_reference} no encontrada")

            # SI EL PAGO FUE APROBADO
            if status_detail == "approved":
                
                payment_info_dict = {
                    "id": payment_data["id"],
                    "amount": payment_data["transaction_amount"]
                }
                
                # Llamar a nuestro servicio para finalizar la compra
                PurchaseService.finalize_purchase_transaction(
                    db=db,
                    purchase=purchase,
                    payment_info=payment_info_dict
                )
                
                db.commit() # Commit de la transacción completa

                # (Opcional) Manejar otros estados como "rejected", "pending"
                if external_reference.startswith("PURCHASE_"):
                        purchase_id_str = external_reference.split("_")[1]
                        purchase = db.query(Purchase).filter(Purchase.id == uuid.UUID(purchase_id_str)).first()
                        if not purchase:
                            raise Exception(f"Compra {purchase_id_str} no encontrada")

                        PurchaseService.finalize_purchase_transaction(
                            db=db,
                            purchase=purchase,
                            payment_info=payment_info_dict
                        )

                    # Opción 2: Es una compra de marketplace
                elif external_reference.startswith("LISTING_"):
                    parts = external_reference.split("_") # "LISTING", "listing_id", "BUYER", "buyer_id"
                    listing_id_str = parts[1]
                    buyer_id_str = parts[3]

                    # Instanciamos el servicio (no podemos usar Depends en un webhook)
                    marketplace_service = MarketplaceService(db)

                    # Llamamos a la lógica de negocio para transferir el ticket
                    marketplace_service.buy_listing(
                        listing_id=uuid.UUID(listing_id_str),
                        buyer_id=uuid.UUID(buyer_id_str)
                    )

                db.commit() # Commit de la transacción

                # ... (manejo de otros estados) ..

        except Exception as e:
            db.rollback()
            print(f"Error procesando webhook de MP: {str(e)}")
            # Devolvemos 500 para que MP reintente
            raise HTTPException(status_code=500, detail="Error al procesar webhook")

    
    return status.HTTP_200_OK # Siempre responder 200 a MP