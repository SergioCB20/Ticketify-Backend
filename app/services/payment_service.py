import mercadopago
from app.core.config import settings
from app.models.purchase import Purchase # (Ejemplo de modelo)
from app.models.user import User # (Ejemplo de modelo)
from decimal import Decimal

class PaymentService:
    
    def __init__(self):
        """
        Inicializa el SDK de la PLATAFORMA.
        Este SDK se usa para pagos donde la plataforma es la vendedora
        (ej. compra directa de tickets de evento).
        """
        self.platform_sdk = mercadopago.SDK(settings.MERCADOPAGO_PRODUCER_TOKEN)

    def create_event_preference(
        self, 
        purchase: Purchase, 
        items: list, 
        buyer_email: str
    ) -> dict:
        """
        Crea una preferencia de pago para la compra de un evento.
        El dinero va a la cuenta de la PLATAFORMA.
        """
        preference_data = {
            "items": items,
            "payer": {
                "email": buyer_email,
            },
            "back_urls": {
                "success": "http://localhost:3000/checkout/success",
                "failure": "http://localhost:3000/checkout/failure",
                "pending": "http://localhost:3000/checkout/pending"
            },
            "auto_return": "approved",
            "external_reference": str(purchase.id),
            "notification_url": f"https://URL_DE_TU_API/api/mercadopago/webhook" 
        }
        
        # Usamos el SDK de la plataforma
        preference_response = self.platform_sdk.preference().create(preference_data)
        
        if preference_response["status"] != 201:
            raise Exception(f"Error al crear preferencia MP: {preference_response.get('response')}")
            
        return preference_response["response"]


    def create_marketplace_preference(
        self, 
        listing_id: str, 
        items: list, 
        buyer_email: str, 
        seller: User,
        platform_fee: Decimal
    ) -> dict:
        """
        Crea una preferencia de pago para una compra en el Marketplace.
        El dinero va a la cuenta del VENDEDOR, con una comisión para la plataforma.
        """
        
        # ¡Clave! Obtenemos el token desencriptado del VENDEDOR
        seller_token = seller.get_decrypted_access_token()
        if not seller_token:
            raise Exception("El vendedor no tiene una cuenta de MercadoPago conectada.")

        # Inicializamos un SDK temporal con el TOKEN DEL VENDEDOR
        seller_sdk = mercadopago.SDK(seller_token)

        preference_data = {
            "items": items,
            "payer": {
                "email": buyer_email,
            },
            "back_urls": {
                "success": "http://localhost:3000/checkout/success",
                "failure": "http://localhost:3000/checkout/failure",
                "pending": "http://localhost:3000/checkout/pending"
            },
            "auto_return": "approved",
            "external_reference": str(listing_id), # O un ID de compra de marketplace
            "notification_url": f"https://URL_DE_TU_API/api/mercadopago/webhook",
            
            # ¡Aquí está la magia del marketplace!
            "application_fee": float(platform_fee)
        }
        
        # Usamos el SDK del VENDEDOR para crear la preferencia
        preference_response = seller_sdk.preference().create(preference_data)
        
        if preference_response["status"] != 201:
            raise Exception(f"Error al crear preferencia MP: {preference_response.get('response')}")

        return preference_response["response"]