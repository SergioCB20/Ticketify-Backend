import mercadopago
from app.core.config import settings
from app.models.purchase import Purchase
from app.models.user import User
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class PaymentService:
    
    def __init__(self):
        """
        Inicializa el SDK de la PLATAFORMA.
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
                "success": f"{settings.FRONTEND_URL}/events/checkout/success?purchase_id={purchase.id}",
                "failure": f"{settings.FRONTEND_URL}/events/checkout/failure?purchase_id={purchase.id}",
                "pending": f"{settings.FRONTEND_URL}/events/checkout/pending?purchase_id={purchase.id}"
            },
            "auto_return": "approved",
            "external_reference": str(purchase.id),
            "notification_url": f"{settings.BACKEND_URL}/api/purchases/webhook",
            "statement_descriptor": "Ticketify",
            "expires": False,
            "binary_mode": True
        }
        
        logger.info(f"📝 Creando preferencia de pago para compra {purchase.id}")
        logger.debug(f"Preference data: {preference_data}")
        
        preference_response = self.platform_sdk.preference().create(preference_data)
        
        if preference_response["status"] not in [200, 201]:
            logger.error(f"❌ Error al crear preferencia MP: {preference_response}")
            raise Exception(f"Error al crear preferencia MP: {preference_response.get('response')}")
        
        logger.info(f"✅ Preferencia creada exitosamente: {preference_response['response']['id']}")
        return preference_response["response"]


    def create_marketplace_preference(
        self, 
        listing_id: str, 
        items: list, 
        buyer_email: str,
        buyer_id: str,
        seller: User,
        platform_fee: Decimal
    ) -> dict:
        """
        Crea una preferencia de pago para una compra en el Marketplace.
        El dinero va a la cuenta del VENDEDOR, con una comisión para la plataforma.
        
        Args:
            listing_id: ID del listing del marketplace
            items: Lista de items para MercadoPago
            buyer_email: Email del comprador
            buyer_id: ID del comprador
            seller: Usuario vendedor con cuenta de MercadoPago conectada
            platform_fee: Comisión que se queda la plataforma
            
        Returns:
            dict: Respuesta de MercadoPago con la preferencia creada
        """
        
        seller_token = seller.get_decrypted_access_token()
        if not seller_token:
            logger.error(f"❌ Vendedor {seller.id} no tiene token de MercadoPago")
            raise Exception("El vendedor no tiene una cuenta de MercadoPago conectada.")

        logger.info(f"📝 Creando preferencia de marketplace para listing {listing_id}")
        
        seller_sdk = mercadopago.SDK(seller_token)

        preference_data = {
            "items": items,
            "payer": {
                "email": buyer_email,
            },
            "back_urls": {
                "success": f"{settings.FRONTEND_URL}/marketplace/checkout/success?listing_id={listing_id}",
                "failure": f"{settings.FRONTEND_URL}/marketplace/checkout/failure?listing_id={listing_id}",
                "pending": f"{settings.FRONTEND_URL}/marketplace/checkout/pending?listing_id={listing_id}"
            },
            "auto_return": "approved",
            "external_reference": f"LISTING_{listing_id}_BUYER_{buyer_id}",
            "notification_url": f"{settings.BACKEND_URL}/api/marketplace/webhook",
            "statement_descriptor": "Ticketify Marketplace",
            "expires": False,
            "binary_mode": True,
            "application_fee": float(platform_fee)
        }
        
        logger.debug(f"Marketplace preference data: {preference_data}")
        
        preference_response = seller_sdk.preference().create(preference_data)
        
        if preference_response["status"] not in [200, 201]:
            logger.error(f"❌ Error al crear preferencia de marketplace: {preference_response}")
            raise Exception(f"Error al crear preferencia MP: {preference_response.get('response')}")

        logger.info(f"✅ Preferencia de marketplace creada: {preference_response['response']['id']}")
        return preference_response["response"]
    
    
    def get_payment_info(self, payment_id: str) -> dict:
        """
        Consulta la información de un pago en MercadoPago.
        """
        try:
            payment_response = self.platform_sdk.payment().get(payment_id)
            
            if payment_response["status"] != 200:
                logger.error(f"❌ Error al consultar pago {payment_id}: {payment_response}")
                raise Exception(f"Error al consultar pago: {payment_response}")
            
            return payment_response["response"]
            
        except Exception as e:
            logger.error(f"❌ Error al obtener info del pago {payment_id}: {str(e)}")
            raise
