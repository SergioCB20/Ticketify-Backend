"""
Repositorio para el sistema de facturación
Maneja consultas a la base de datos relacionadas con facturación
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import uuid

from app.models.event import Event, EventStatus
from app.models.purchase import Purchase, PurchaseStatus
from app.models.payment import Payment, PaymentStatus
from app.models.user import User


class BillingRepository:
    """Repositorio para operaciones de facturación"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ============================================================
    # Consultas de Eventos
    # ============================================================
    
    def get_organizer_events(self, organizer_id: uuid.UUID) -> List[Event]:
        """
        Obtener todos los eventos de un organizador con sus datos de facturación
        """
        return (
            self.db.query(Event)
            .filter(Event.organizer_id == organizer_id)
            .options(
                joinedload(Event.purchases).joinedload(Purchase.payment),
                joinedload(Event.ticket_types)
            )
            .all()
        )
    
    def get_event_by_id(self, event_id: uuid.UUID, organizer_id: uuid.UUID) -> Optional[Event]:
        """
        Obtener un evento específico con verificación de propiedad
        """
        return (
            self.db.query(Event)
            .filter(
                Event.id == event_id,
                Event.organizer_id == organizer_id
            )
            .options(
                joinedload(Event.purchases).joinedload(Purchase.payment),
                joinedload(Event.ticket_types)
            )
            .first()
        )
    
    # ============================================================
    # Consultas de Compras y Pagos
    # ============================================================
    
    def get_event_purchases(
        self, 
        event_id: uuid.UUID,
        status: Optional[PurchaseStatus] = None
    ) -> List[Purchase]:
        """
        Obtener todas las compras de un evento
        """
        query = (
            self.db.query(Purchase)
            .filter(Purchase.event_id == event_id)
            .options(
                joinedload(Purchase.user),
                joinedload(Purchase.payment)
            )
        )
        
        if status:
            query = query.filter(Purchase.status == status)
        
        return query.all()
    
    def get_completed_purchases(self, event_id: uuid.UUID) -> List[Purchase]:
        """
        Obtener solo las compras completadas de un evento
        """
        return self.get_event_purchases(event_id, PurchaseStatus.COMPLETED)
    
    # ============================================================
    # Cálculos de Facturación
    # ============================================================
    
    def calculate_event_revenue(self, event_id: uuid.UUID) -> Dict[str, Any]:
        """
        Calcular los ingresos totales de un evento
        Retorna: {total_revenue, total_transactions, total_tickets}
        """
        result = (
            self.db.query(
                func.coalesce(func.sum(Purchase.total_amount), 0).label('total_revenue'),
                func.count(Purchase.id).label('total_transactions'),
                func.coalesce(func.sum(Purchase.quantity), 0).label('total_tickets')
            )
            .filter(
                Purchase.event_id == event_id,
                Purchase.status == PurchaseStatus.COMPLETED
            )
            .first()
        )
        
        return {
            'total_revenue': Decimal(str(result.total_revenue)),
            'total_transactions': result.total_transactions,
            'total_tickets': result.total_tickets
        }
    
    def calculate_event_commissions(self, event_id: uuid.UUID) -> Dict[str, Decimal]:
        """
        Calcular las comisiones totales (MercadoPago + Plataforma)
        Retorna: {mp_commission, platform_commission, total_commission}
        """
        purchases = self.get_completed_purchases(event_id)
        
        mp_commission = Decimal('0')
        platform_commission = Decimal('0')
        
        for purchase in purchases:
            if purchase.payment and purchase.payment.transactionId:
                # Aquí se calcularían las comisiones reales de MP
                # Por ahora usamos un porcentaje fijo del 5% para MP
                mp_commission += purchase.total_amount * Decimal('0.05')
            
            # Comisión de plataforma (ejemplo: 3%)
            platform_commission += purchase.total_amount * Decimal('0.03')
        
        return {
            'mp_commission': mp_commission,
            'platform_commission': platform_commission,
            'total_commission': mp_commission + platform_commission
        }
    
    def calculate_payment_methods_distribution(self, event_id: uuid.UUID) -> List[Dict[str, Any]]:
        """
        Calcular la distribución de métodos de pago
        """
        result = (
            self.db.query(
                Purchase.payment_method,
                func.count(Purchase.id).label('count'),
                func.sum(Purchase.total_amount).label('amount')
            )
            .filter(
                Purchase.event_id == event_id,
                Purchase.status == PurchaseStatus.COMPLETED,
                Purchase.payment_method.isnot(None)
            )
            .group_by(Purchase.payment_method)
            .all()
        )
        
        # Calcular el total para porcentajes
        total_amount = sum(Decimal(str(row.amount)) for row in result)
        
        return [
            {
                'method': row.payment_method.value if hasattr(row.payment_method, 'value') else str(row.payment_method),
                'count': row.count,
                'amount': Decimal(str(row.amount)),
                'percentage': (Decimal(str(row.amount)) / total_amount * 100) if total_amount > 0 else Decimal('0')
            }
            for row in result
        ]
    
    # ============================================================
    # Consultas de Acreditación
    # ============================================================
    
    def calculate_accreditation_status(self, event_id: uuid.UUID) -> Dict[str, Any]:
        """
        Calcular el estado de acreditación de fondos
        """
        purchases = self.get_completed_purchases(event_id)
        
        credited = Decimal('0')
        pending = Decimal('0')
        next_date = None
        
        for purchase in purchases:
            if purchase.payment and purchase.payment.status == PaymentStatus.COMPLETED:
                # Asumimos que los pagos se acreditan después de 14 días
                if purchase.payment_date:
                    accreditation_date = purchase.payment_date + timedelta(days=14)
                    
                    if accreditation_date <= datetime.now(timezone.utc):
                        credited += purchase.total_amount
                    else:
                        pending += purchase.total_amount
                        if not next_date or accreditation_date < next_date:
                            next_date = accreditation_date
        
        return {
            'credited': credited,
            'pending': pending,
            'next_date': next_date
        }
    
    # ============================================================
    # Actualización de Datos
    # ============================================================
    
    def update_purchase_from_mercadopago(
        self,
        purchase_id: uuid.UUID,
        mp_data: Dict[str, Any]
    ) -> Purchase:
        """
        Actualizar una compra con datos de MercadoPago
        """
        purchase = self.db.query(Purchase).filter(Purchase.id == purchase_id).first()
        
        if not purchase:
            return None
        
        # Actualizar campos según datos de MP
        if 'status' in mp_data:
            status_map = {
                'approved': PurchaseStatus.COMPLETED,
                'pending': PurchaseStatus.PENDING,
                'rejected': PurchaseStatus.REJECTED,
                'refunded': PurchaseStatus.REFUNDED
            }
            purchase.status = status_map.get(mp_data['status'], PurchaseStatus.PENDING)
        
        if 'payment_method_id' in mp_data:
            purchase.payment_reference = mp_data.get('id')
        
        if 'date_approved' in mp_data:
            purchase.payment_date = datetime.fromisoformat(
                mp_data['date_approved'].replace('Z', '+00:00')
            )
        
        self.db.commit()
        self.db.refresh(purchase)
        
        return purchase
    
    # ============================================================
    # Búsqueda y Filtrado
    # ============================================================
    
    def search_transactions(
        self,
        event_id: uuid.UUID,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Purchase]:
        """
        Buscar transacciones con filtros opcionales
        """
        query = (
            self.db.query(Purchase)
            .filter(Purchase.event_id == event_id)
            .options(
                joinedload(Purchase.user),
                joinedload(Purchase.payment)
            )
        )
        
        if status:
            query = query.filter(Purchase.status == status)
        
        if start_date:
            query = query.filter(Purchase.created_at >= start_date)
        
        if end_date:
            query = query.filter(Purchase.created_at <= end_date)
        
        return query.order_by(Purchase.created_at.desc()).all()
