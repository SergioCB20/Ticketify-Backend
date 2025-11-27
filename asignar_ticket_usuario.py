"""
Script para asignar tickets de eventos a usuarios asistentes
Permite seleccionar un usuario, un evento y crear un ticket completo con compra y pago
Uso: python asignar_ticket_usuario.py
"""
import sys
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

sys.path.append('.')

from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.models.event import Event, EventStatus
from app.models.ticket import Ticket, TicketStatus
from app.models.ticket_type import TicketType
from app.models.payment import Payment, PaymentStatus, PaymentMethod as PaymentPaymentMethod
from app.models.purchase import Purchase, PurchaseStatus, PaymentMethod
from app.models.role import Role


def mostrar_usuarios_asistentes(db):
    """Muestra todos los usuarios que tienen el rol de asistente"""
    print("\n" + "=" * 70)
    print("👥 USUARIOS ASISTENTES DISPONIBLES")
    print("=" * 70)
    
    # Buscar el rol de asistente
    attendee_role = db.query(Role).filter(Role.name == UserRole.ATTENDEE).first()
    
    if not attendee_role:
        print("❌ No existe el rol ATTENDEE en la base de datos")
        return []
    
    # Obtener usuarios con rol asistente
    attendees = db.query(User).join(User.roles).filter(Role.name == UserRole.ATTENDEE).all()
    
    if not attendees:
        print("⚠️  No hay usuarios con rol ATTENDEE")
        print("\n💡 Tip: Crea un usuario desde la aplicación o modifica un usuario existente")
        return []
    
    for i, user in enumerate(attendees, 1):
        tickets_count = len(user.tickets) if user.tickets else 0
        print(f"\n{i}. {user.email}")
        print(f"   Nombre: {user.firstName} {user.lastName}")
        print(f"   ID: {user.id}")
        print(f"   Activo: {'Sí' if user.isActive else 'No'}")
        print(f"   Tickets comprados: {tickets_count}")
    
    print()
    return attendees


def mostrar_eventos_disponibles(db):
    """Muestra todos los eventos publicados disponibles"""
    print("\n" + "=" * 70)
    print("🎉 EVENTOS DISPONIBLES")
    print("=" * 70)
    
    # Obtener eventos publicados con tipos de tickets disponibles
    events = db.query(Event).filter(
        Event.status == EventStatus.PUBLISHED
    ).order_by(Event.startDate).all()
    
    if not events:
        print("⚠️  No hay eventos publicados en la base de datos")
        print("\n💡 Tip: Crea un evento con crear_evento_organizador.py")
        return []
    
    events_con_tickets = []
    
    for i, event in enumerate(events, 1):
        # Verificar si tiene tipos de tickets activos
        ticket_types = [tt for tt in event.ticket_types if tt.is_active and not tt.is_sold_out]
        
        if not ticket_types:
            continue
        
        events_con_tickets.append(event)
        idx = len(events_con_tickets)
        
        print(f"\n{idx}. {event.title}")
        print(f"   Lugar: {event.venue}")
        print(f"   Fecha: {event.startDate.strftime('%Y-%m-%d %H:%M')}")
        print(f"   Organizador: {event.organizer.firstName} {event.organizer.lastName}")
        print(f"   Capacidad: {event.totalCapacity} personas")
        print(f"   Estado: {event.status.value}")
        print(f"   ID: {event.id}")
        
        # Mostrar tipos de tickets disponibles
        print(f"   📋 Tipos de tickets disponibles ({len(ticket_types)}):")
        for tt in ticket_types:
            disponibles = tt.quantity_available - tt.sold_quantity
            print(f"      • {tt.name}: S/ {tt.price} - {disponibles}/{tt.quantity_available} disponibles")
    
    if not events_con_tickets:
        print("⚠️  No hay eventos con tickets disponibles")
        return []
    
    print()
    return events_con_tickets


def mostrar_tipos_tickets(event, db):
    """Muestra los tipos de tickets disponibles para un evento"""
    print("\n" + "=" * 70)
    print(f"🎫 TIPOS DE TICKETS - {event.title}")
    print("=" * 70)
    
    ticket_types = [tt for tt in event.ticket_types if tt.is_active and not tt.is_sold_out]
    
    if not ticket_types:
        print("❌ No hay tipos de tickets disponibles para este evento")
        return []
    
    for i, tt in enumerate(ticket_types, 1):
        disponibles = tt.quantity_available - tt.sold_quantity
        print(f"\n{i}. {tt.name}")
        print(f"   Precio: S/ {tt.price}")
        print(f"   Descripción: {tt.description or 'Sin descripción'}")
        print(f"   Disponibles: {disponibles}/{tt.quantity_available}")
        print(f"   Límite por compra: {tt.min_purchase} - {tt.max_purchase}")
        print(f"   ID: {tt.id}")
    
    print()
    return ticket_types


def crear_ticket_para_usuario():
    """
    Proceso principal: seleccionar usuario, evento y crear ticket
    """
    db = SessionLocal()
    
    try:
        print("\n" + "=" * 70)
        print("🎟️  ASIGNADOR DE TICKETS - TICKETIFY")
        print("=" * 70)
        
        # 1. Seleccionar usuario asistente
        attendees = mostrar_usuarios_asistentes(db)
        
        if not attendees:
            print("\n❌ No se puede continuar sin usuarios asistentes")
            return
        
        user_choice = input(f"📝 Selecciona el usuario (1-{len(attendees)}): ").strip()
        try:
            user_index = int(user_choice) - 1
            if user_index < 0 or user_index >= len(attendees):
                print("❌ Selección inválida")
                return
            selected_user = attendees[user_index]
        except ValueError:
            print("❌ Por favor ingresa un número válido")
            return
        
        print(f"\n✅ Usuario seleccionado: {selected_user.firstName} {selected_user.lastName} ({selected_user.email})")
        
        # 2. Seleccionar evento
        events = mostrar_eventos_disponibles(db)
        
        if not events:
            print("\n❌ No hay eventos disponibles")
            return
        
        event_choice = input(f"📝 Selecciona el evento (1-{len(events)}): ").strip()
        try:
            event_index = int(event_choice) - 1
            if event_index < 0 or event_index >= len(events):
                print("❌ Selección inválida")
                return
            selected_event = events[event_index]
        except ValueError:
            print("❌ Por favor ingresa un número válido")
            return
        
        print(f"\n✅ Evento seleccionado: {selected_event.title}")
        
        # 3. Seleccionar tipo de ticket
        ticket_types = mostrar_tipos_tickets(selected_event, db)
        
        if not ticket_types:
            print("\n❌ No hay tipos de tickets disponibles para este evento")
            return
        
        tt_choice = input(f"📝 Selecciona el tipo de ticket (1-{len(ticket_types)}): ").strip()
        try:
            tt_index = int(tt_choice) - 1
            if tt_index < 0 or tt_index >= len(ticket_types):
                print("❌ Selección inválida")
                return
            selected_ticket_type = ticket_types[tt_index]
        except ValueError:
            print("❌ Por favor ingresa un número válido")
            return
        
        print(f"\n✅ Tipo de ticket seleccionado: {selected_ticket_type.name} (S/ {selected_ticket_type.price})")
        
        # 4. Confirmar creación
        print("\n" + "=" * 70)
        print("📋 RESUMEN DE LA COMPRA")
        print("=" * 70)
        print(f"Usuario: {selected_user.firstName} {selected_user.lastName}")
        print(f"Email: {selected_user.email}")
        print(f"Evento: {selected_event.title}")
        print(f"Lugar: {selected_event.venue}")
        print(f"Fecha: {selected_event.startDate.strftime('%Y-%m-%d %H:%M')}")
        print(f"Ticket: {selected_ticket_type.name}")
        print(f"Precio: S/ {selected_ticket_type.price}")
        print("=" * 70)
        
        confirmar = input("\n¿Confirmar la creación del ticket? (s/N): ").strip().lower()
        
        if confirmar != 's':
            print("\n❌ Operación cancelada")
            return
        
        # 5. Crear Purchase (Compra)
        print("\n💰 Creando compra...")
        purchase = Purchase(
            user_id=selected_user.id,
            event_id=selected_event.id,
            ticket_type_id=selected_ticket_type.id,
            quantity=1,
            unit_price=selected_ticket_type.price,
            subtotal=selected_ticket_type.price,
            tax_amount=Decimal("0.00"),
            service_fee=Decimal("0.00"),
            discount_amount=Decimal("0.00"),
            total_amount=selected_ticket_type.price,
            buyer_email=selected_user.email,
            status=PurchaseStatus.COMPLETED,
            payment_method=PaymentMethod.CREDIT_CARD,
            purchase_date=datetime.now()
        )
        db.add(purchase)
        db.flush()
        print(f"✅ Compra creada con ID: {purchase.id}")
        
        # 6. Crear Payment (Pago)
        print("💳 Creando pago...")
        payment = Payment(
            user_id=selected_user.id,
            amount=selected_ticket_type.price,
            status=PaymentStatus.COMPLETED,
            paymentMethod=PaymentPaymentMethod.CREDIT_CARD,
            transactionId=f"TEST_{datetime.now().timestamp()}",
            paymentDate=datetime.now()
        )
        db.add(payment)
        db.flush()
        print(f"✅ Pago creado con ID: {payment.id}")
        
        # 7. Crear Ticket
        print("🎟️  Creando ticket...")
        ticket = Ticket(
            user_id=selected_user.id,
            event_id=selected_event.id,
            ticket_type_id=selected_ticket_type.id,
            payment_id=payment.id,
            purchase_id=purchase.id,
            price=selected_ticket_type.price,
            purchaseDate=datetime.now(),
            status=TicketStatus.ACTIVE,
            isValid=True
        )
        db.add(ticket)
        db.flush()
        
        # Generar código QR
        ticket.generate_qr()
        
        # 8. Actualizar cantidad vendida
        selected_ticket_type.sold_quantity += 1
        
        # 9. Commit de todas las operaciones
        db.commit()
        
        print(f"✅ Ticket creado con ID: {ticket.id}")
        
        # 10. Resumen final
        print("\n" + "=" * 70)
        print("✨ TICKET CREADO EXITOSAMENTE")
        print("=" * 70)
        print(f"\n📋 DETALLES DEL TICKET")
        print(f"{'─' * 70}")
        print(f"ID Ticket: {ticket.id}")
        print(f"Usuario: {selected_user.firstName} {selected_user.lastName}")
        print(f"Email: {selected_user.email}")
        print(f"Evento: {selected_event.title}")
        print(f"Lugar: {selected_event.venue}")
        print(f"Fecha del evento: {selected_event.startDate.strftime('%Y-%m-%d %H:%M')}")
        print(f"Tipo de ticket: {selected_ticket_type.name}")
        print(f"Precio: S/ {ticket.price}")
        print(f"Estado: {ticket.status.value}")
        print(f"Válido: {'Sí'  if ticket.isValid else 'No '}")
        print(f"Fecha de compra: {ticket.purchaseDate.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"QR generado: {'Sí' if ticket.qrCode else 'No'}")
        print(f"\n💳 INFORMACIÓN DE PAGO")
        print(f"{'─' * 70}")
        print(f"ID Compra: {purchase.id}")
        print(f"ID Pago: {payment.id}")
        print(f"Método de pago: {payment.paymentMethod.value}")
        print(f"Estado: {payment.status.value}")
        print(f"{'─' * 70}")
        print(f"\n✅ El usuario puede ver este ticket iniciando sesión con:")
        print(f"   📧 {selected_user.email}")
        print("=" * 70 + "\n")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


def crear_ticket_rapido():
    """
    Crea un ticket rápidamente para el primer usuario asistente y primer evento
    """
    db = SessionLocal()
    
    try:
        print("\n🚀 CREACIÓN RÁPIDA DE TICKET")
        print("=" * 70)
        
        # Obtener primer asistente
        attendee_role = db.query(Role).filter(Role.name == UserRole.ATTENDEE).first()
        if not attendee_role:
            print("❌ No existe el rol ATTENDEE")
            return
        
        attendee = db.query(User).join(User.roles).filter(Role.name == UserRole.ATTENDEE).first()
        if not attendee:
            print("❌ No hay usuarios asistentes")
            return
        
        print(f"Usuario: {attendee.email}")
        
        # Obtener primer evento publicado
        event = db.query(Event).filter(Event.status == EventStatus.PUBLISHED).first()
        if not event:
            print("❌ No hay eventos publicados")
            return
        
        print(f"Evento: {event.title}")
        
        # Obtener primer tipo de ticket disponible
        ticket_type = None
        for tt in event.ticket_types:
            if tt.is_active and not tt.is_sold_out:
                ticket_type = tt
                break
        
        if not ticket_type:
            print("❌ No hay tipos de tickets disponibles")
            return
        
        print(f"Tipo de ticket: {ticket_type.name} (S/ {ticket_type.price})")
        
        # Crear compra
        purchase = Purchase(
            user_id=attendee.id,
            event_id=event.id,
            ticket_type_id=ticket_type.id,
            quantity=1,
            unit_price=ticket_type.price,
            subtotal=ticket_type.price,
            tax_amount=Decimal("0.00"),
            service_fee=Decimal("0.00"),
            discount_amount=Decimal("0.00"),
            total_amount=ticket_type.price,
            buyer_email=attendee.email,
            status=PurchaseStatus.COMPLETED,
            payment_method=PaymentMethod.CREDIT_CARD,
            purchase_date=datetime.now()
        )
        db.add(purchase)
        db.flush()
        
        # Crear pago
        payment = Payment(
            user_id=attendee.id,
            amount=ticket_type.price,
            status=PaymentStatus.COMPLETED,
            paymentMethod=PaymentPaymentMethod.CREDIT_CARD,
            transactionId=f"QUICK_{datetime.now().timestamp()}",
            paymentDate=datetime.now()
        )
        db.add(payment)
        db.flush()
        
        # Crear ticket
        ticket = Ticket(
            user_id=attendee.id,
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
        db.flush()
        
        ticket.generate_qr()
        ticket_type.sold_quantity += 1
        
        db.commit()
        
        print(f"\n✅ Ticket creado exitosamente!")
        print(f"   ID: {ticket.id}")
        print(f"   Usuario: {attendee.email}")
        print(f"   Evento: {event.title}")
        print(f"   Tipo: {ticket_type.name}")
        print(f"   Precio: S/ {ticket.price}")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🎟️  ASIGNADOR DE TICKETS - TICKETIFY")
    print("=" * 70)
    print("\nModos disponibles:")
    print("1. Asignación interactiva (seleccionar usuario, evento y ticket)")
    print("2. Asignación rápida (primer usuario, primer evento, primer ticket)")
    print("3. Salir")
    
    opcion = input("\nSelecciona una opción (1-3): ").strip()
    
    if opcion == "1":
        crear_ticket_para_usuario()
    elif opcion == "2":
        crear_ticket_rapido()
    elif opcion == "3":
        print("\n👋 ¡Hasta luego!")
    else:
        print("\n❌ Opción inválida")
