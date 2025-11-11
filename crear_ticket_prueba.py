"""
Script para crear tickets de prueba en Ticketify
Usar para testing del Marketplace
"""
import sys
from datetime import datetime, timedelta
from decimal import Decimal

# Configurar el path para importar los módulos de la app
sys.path.append('.')

from app.core.database import SessionLocal
from app.models.user import User
from app.models.event import Event, EventStatus
from app.models.ticket import Ticket, TicketStatus
from app.models.ticket_type import TicketType
from app.models.payment import Payment, PaymentStatus, PaymentMethod as PaymentPaymentMethod
from app.models.purchase import Purchase, PurchaseStatus, PaymentMethod

def crear_ticket_para_usuario():
    """
    Crea un ticket de prueba para un usuario existente
    """
    db = SessionLocal()
    
    try:
        # 1. Mostrar usuarios disponibles
        print("\n=== USUARIOS DISPONIBLES ===")
        users = db.query(User).all()
        
        if not users:
            print("❌ No hay usuarios en la base de datos")
            return
        
        for i, user in enumerate(users, 1):
            print(f"{i}. {user.email} - {user.firstName} {user.lastName}")
        
        # 2. Seleccionar usuario
        user_index = int(input("\nSelecciona el número del usuario (1-{}): ".format(len(users)))) - 1
        selected_user = users[user_index]
        print(f"✅ Usuario seleccionado: {selected_user.email}")
        
        # 3. Verificar si hay eventos, si no, crear uno
        event = db.query(Event).first()
        
        if not event:
            print("\n📅 No hay eventos, creando evento de prueba...")
            event = Event(
                title="Concierto Rock 2025",
                description="Evento de prueba para marketplace",
                startDate=datetime.now() + timedelta(days=30),
                endDate=datetime.now() + timedelta(days=30, hours=4),
                venue="Estadio Nacional, Lima",
                totalCapacity=1000,
                status=EventStatus.PUBLISHED,
                organizer_id=selected_user.id,
                multimedia=["https://example.com/poster.jpg"]
            )
            db.add(event)
            db.commit()
            print(f"✅ Evento creado: {event.title}")
        else:
            print(f"\n✅ Usando evento existente: {event.title}")
        
        # 4. Verificar/crear tipo de ticket
        ticket_type = db.query(TicketType).filter_by(event_id=event.id).first()
        
        if not ticket_type:
            print("\n🎫 Creando tipo de ticket...")
            ticket_type = TicketType(
                event_id=event.id,
                name="General",
                description="Entrada general",
                price=Decimal("50.00"),
                quantity=500,
                sold_quantity=0
            )
            db.add(ticket_type)
            db.commit()
            print(f"✅ Tipo de ticket creado: {ticket_type.name}")
        
        # 5. Crear un Purchase (compra)
        print("\n💰 Creando compra...")
        purchase = Purchase(
            user_id=selected_user.id,
            event_id=event.id,
            ticket_type_id=ticket_type.id,
            total_amount=ticket_type.price,
            subtotal=ticket_type.price,  # Requerido
            unit_price=ticket_type.price,  # Requerido
            tax_amount=Decimal("0.00"),
            service_fee=Decimal("0.00"),
            discount_amount=Decimal("0.00"),
            quantity=1,
            buyer_email=selected_user.email,  # Requerido
            status=PurchaseStatus.COMPLETED,
            payment_method=PaymentMethod.CREDIT_CARD,
            purchase_date=datetime.now()
        )
        db.add(purchase)
        db.commit()
        print(f"✅ Compra creada con ID: {purchase.id}")
        
        # 6. Crear un Payment (pago)
        print("\n💳 Creando pago...")
        payment = Payment(
            user_id=selected_user.id,
            amount=ticket_type.price,
            status=PaymentStatus.COMPLETED,
            paymentMethod=PaymentPaymentMethod.CREDIT_CARD,
            transactionId=f"TEST_{datetime.now().timestamp()}",
            paymentDate=datetime.now()
        )
        db.add(payment)
        db.commit()
        print(f"✅ Pago creado con ID: {payment.id}")
        
        # 7. Crear el Ticket
        print("\n🎟️ Creando ticket...")
        ticket = Ticket(
            user_id=selected_user.id,
            event_id=event.id,
            ticket_type_id=ticket_type.id,
            payment_id=payment.id,
            purchase_id=purchase.id,
            price=ticket_type.price,
            purchaseDate=datetime.now(),
            status=TicketStatus.ACTIVE,
            isValid=True
        )
        db.add(ticket)
        db.commit()
        
        # Generar QR
        ticket.generate_qr()
        db.commit()
        
        print(f"✅ Ticket creado exitosamente!")
        print(f"\n{'='*50}")
        print(f"📋 RESUMEN")
        print(f"{'='*50}")
        print(f"Usuario: {selected_user.firstName} {selected_user.lastName}")
        print(f"Email: {selected_user.email}")
        print(f"Evento: {event.title}")
        print(f"Ticket ID: {ticket.id}")
        print(f"Precio: S/ {ticket.price}")
        print(f"Estado: {ticket.status.value}")
        print(f"{'='*50}")
        print(f"\n✅ Ahora puedes iniciar sesión con este usuario y ver tu ticket!")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    print("🎫 CREADOR DE TICKETS DE PRUEBA - TICKETIFY")
    print("=" * 50)
    crear_ticket_para_usuario()
