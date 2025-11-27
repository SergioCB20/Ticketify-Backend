# 🎟️ Script de Asignación de Tickets - Ticketify

Script para asignar tickets de eventos a usuarios asistentes de forma rápida y sencilla.

## 📋 Descripción

`asignar_ticket_usuario.py` permite crear tickets completos (con compra y pago) para usuarios asistentes de manera interactiva o automática. Es ideal para:

- Pruebas de funcionalidad de tickets
- Crear tickets de demostración
- Asignar tickets manualmente a usuarios
- Poblar la base de datos con datos de prueba

## 🎯 Características

✅ **Modo Interactivo:**
- Selecciona usuario asistente de una lista
- Selecciona evento publicado disponible
- Selecciona tipo de ticket específico
- Confirmación antes de crear
- Resumen detallado al finalizar

✅ **Modo Rápido:**
- Asigna automáticamente el primer usuario asistente
- Con el primer evento publicado
- Y el primer tipo de ticket disponible
- Ideal para testing rápido

✅ **Crea automáticamente:**
- 🎫 Ticket con estado ACTIVE
- 💰 Purchase (compra) completada
- 💳 Payment (pago) procesado
- 🔢 Código QR generado
- 📊 Actualiza inventario de tickets

## 🚀 Uso

### Modo Interactivo (Recomendado)

```bash
cd Ticketify-Backend
python asignar_ticket_usuario.py
# Seleccionar opción 1
```

### Modo Rápido

```bash
cd Ticketify-Backend
python asignar_ticket_usuario.py
# Seleccionar opción 2
```

## 📖 Ejemplo de Ejecución

### Modo Interactivo:

```
🎟️  ASIGNADOR DE TICKETS - TICKETIFY
======================================================================

Modos disponibles:
1. Asignación interactiva (seleccionar usuario, evento y ticket)
2. Asignación rápida (primer usuario, primer evento, primer ticket)
3. Salir

Selecciona una opción (1-3): 1

======================================================================
👥 USUARIOS ASISTENTES DISPONIBLES
======================================================================

1. usuario@test.com
   Nombre: Carlos López
   ID: 123e4567-e89b-12d3-a456-426614174000
   Activo: Sí
   Tickets comprados: 2

2. maria@test.com
   Nombre: María García
   ID: 234e5678-e89b-12d3-a456-426614174001
   Activo: Sí
   Tickets comprados: 0

📝 Selecciona el usuario (1-2): 2

✅ Usuario seleccionado: María García (maria@test.com)

======================================================================
🎉 EVENTOS DISPONIBLES
======================================================================

1. Concierto Rock 2025
   Lugar: Estadio Nacional, Lima
   Fecha: 2025-12-15 20:00
   Organizador: Juan Pérez
   Capacidad: 1000 personas
   Estado: PUBLISHED
   📋 Tipos de tickets disponibles (3):
      • General: S/ 50.0 - 600/600 disponibles
      • VIP: S/ 150.0 - 300/300 disponibles
      • Platea: S/ 100.0 - 100/100 disponibles

📝 Selecciona el evento (1-1): 1

✅ Evento seleccionado: Concierto Rock 2025

======================================================================
🎫 TIPOS DE TICKETS - Concierto Rock 2025
======================================================================

1. General
   Precio: S/ 50.0
   Descripción: Entrada general
   Disponibles: 600/600
   Límite por compra: 1 - 10

2. VIP
   Precio: S/ 150.0
   Descripción: Entrada VIP con acceso preferencial
   Disponibles: 300/300
   Límite por compra: 1 - 10

3. Platea
   Precio: S/ 100.0
   Descripción: Entrada platea
   Disponibles: 100/100
   Límite por compra: 1 - 10

📝 Selecciona el tipo de ticket (1-3): 2

✅ Tipo de ticket seleccionado: VIP (S/ 150.0)

======================================================================
📋 RESUMEN DE LA COMPRA
======================================================================
Usuario: María García
Email: maria@test.com
Evento: Concierto Rock 2025
Lugar: Estadio Nacional, Lima
Fecha: 2025-12-15 20:00
Ticket: VIP
Precio: S/ 150.0
======================================================================

¿Confirmar la creación del ticket? (s/N): s

💰 Creando compra...
✅ Compra creada con ID: abc12345...
💳 Creando pago...
✅ Pago creado con ID: def67890...
🎟️  Creando ticket...
✅ Ticket creado con ID: ghi54321...

======================================================================
✨ TICKET CREADO EXITOSAMENTE
======================================================================

📋 DETALLES DEL TICKET
──────────────────────────────────────────────────────────────────────
ID Ticket: ghi54321-e89b-12d3-a456-426614174002
Usuario: María García
Email: maria@test.com
Evento: Concierto Rock 2025
Lugar: Estadio Nacional, Lima
Fecha del evento: 2025-12-15 20:00
Tipo de ticket: VIP
Precio: S/ 150.0
Estado: ACTIVE
Válido: Sí ✅
Fecha de compra: 2025-11-26 22:30:15
QR generado: Sí

💳 INFORMACIÓN DE PAGO
──────────────────────────────────────────────────────────────────────
ID Compra: abc12345...
ID Pago: def67890...
Método de pago: CREDIT_CARD
Estado: COMPLETED
──────────────────────────────────────────────────────────────────────

✅ El usuario puede ver este ticket iniciando sesión con:
   📧 maria@test.com
======================================================================
```

## 📊 Estructura de Datos Creados

```
┌─────────────────────────────────────────────────────────────┐
│                        TICKET                               │
│  • ID, user_id, event_id, ticket_type_id                   │
│  • price, purchaseDate, status (ACTIVE)                     │
│  • isValid: true                                            │
│  • qr_code: generado automáticamente                        │
│                           ↓                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              PURCHASE (Compra)                      │   │
│  │  • quantity: 1                                      │   │
│  │  • total_amount, subtotal, unit_price               │   │
│  │  • buyer_email                                      │   │
│  │  • status: COMPLETED                                │   │
│  │  • payment_method: CREDIT_CARD                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                           ↓                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              PAYMENT (Pago)                         │   │
│  │  • amount                                           │   │
│  │  • status: COMPLETED                                │   │
│  │  • paymentMethod: CREDIT_CARD                       │   │
│  │  • transactionId: TEST_timestamp                    │   │
│  │  • paymentDate                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ADEMÁS: actualiza sold_quantity del TicketType            │
└─────────────────────────────────────────────────────────────┘
```

## 🔑 Requisitos Previos

1. **Usuario con rol ATTENDEE:**
   ```python
   # Verificar o crear usuario asistente
   from app.models.role import Role
   from app.models.user import User, UserRole
   
   attendee_role = db.query(Role).filter(Role.name == UserRole.ATTENDEE).first()
   user.roles.append(attendee_role)
   db.commit()
   ```

2. **Evento publicado con tickets disponibles:**
   ```bash
   # Crear evento si no existe
   python crear_evento_organizador.py
   ```

3. **Base de datos configurada:**
   ```bash
   # Migraciones al día
   alembic upgrade head
   ```

## 🚨 Solución de Problemas

### Error: "No hay usuarios con rol ATTENDEE"

**Solución 1 - Desde la aplicación:**
- Registra un nuevo usuario
- Los usuarios nuevos tienen rol ATTENDEE por defecto

**Solución 2 - Desde la base de datos:**
```python
from app.models.user import User
from app.models.role import Role

user = db.query(User).filter(User.email == "usuario@test.com").first()
attendee_role = db.query(Role).filter(Role.name == "ATTENDEE").first()
user.roles.append(attendee_role)
db.commit()
```

### Error: "No hay eventos publicados"

**Solución:**
```bash
# Crear un evento de prueba
python crear_evento_organizador.py
# Seleccionar opción 2 (modo rápido)
```

### Error: "No hay tipos de tickets disponibles"

**Causa:** El evento no tiene tipos de tickets o están agotados

**Solución:**
```python
# Agregar tipos de tickets al evento
from app.models.ticket_type import TicketType
from decimal import Decimal

ticket_type = TicketType(
    event_id=event_id,
    name="General",
    price=Decimal("50.00"),
    quantity_available=100,
    sold_quantity=0,
    is_active=True
)
db.add(ticket_type)
db.commit()
```

## 💡 Casos de Uso

### Testing de Funcionalidad
```bash
# Crear varios tickets para diferentes usuarios
python asignar_ticket_usuario.py
# Opción 1, seleccionar diferentes usuarios y eventos
```

### Datos de Demostración
```bash
# Crear tickets rápidamente
for i in {1..5}
do
  python asignar_ticket_usuario.py
  # Ingresar: 2 (modo rápido)
done
```

### Asignación Manual
```bash
# Asignar ticket específico a usuario específico
python asignar_ticket_usuario.py
# Opción 1, elegir usuario y ticket deseados
```

## ⚠️ Errores Conocidos y Soluciones

### Error: 'Ticket' object has no attribute 'qr_code'

**Solución:** ✅ Corregido en versión actual

El atributo correcto es `qrCode` (camelCase), no `qr_code` (snake_case).

### Error: AttributeError con 'is_sold_out'

**Causa:** Propiedad calculada que depende de `quantity_available` y `sold_quantity`

**Solución:** El script verifica manualmente: `(quantity_available - sold_quantity) > 0`

---

## 🔗 Scripts Relacionados

- `verificar_tickets_disponibles.py` - **¡Ejecuta primero!** Verifica asistentes y eventos
- `verificar_sistema_eventos.py` - Verificación general del sistema
- `crear_evento_organizador.py` - Crea eventos con tipos de tickets
- `crear_ticket_prueba.py` - Script original de creación de tickets

## 📝 Notas Importantes

1. **Los tickets se crean con estado ACTIVE** - están listos para usar
2. **El QR se genera automáticamente** - el usuario puede validar entrada
3. **Se actualiza el inventario** - reduce tickets disponibles
4. **No se valida stock real** - es para pruebas, no valida sobre-venta
5. **Método de pago ficticio** - siempre usa CREDIT_CARD para pruebas

## 🎯 Diferencias con crear_ticket_prueba.py

| Característica | asignar_ticket_usuario.py | crear_ticket_prueba.py |
|----------------|---------------------------|------------------------|
| Selección de usuario | ✅ Interactiva de lista | ❌ Solo muestra y elige |
| Selección de evento | ✅ Lista de disponibles | ⚠️ Usa primero o crea |
| Selección de ticket | ✅ Muestra tipos disponibles | ⚠️ Usa primero |
| Verificación de stock | ✅ Solo muestra disponibles | ❌ No verifica |
| Modos | 2 (Interactivo + Rápido) | 1 (Solo interactivo) |
| Confirmación | ✅ Pide confirmación | ❌ Crea directo |
| Interfaz | ⭐⭐⭐⭐⭐ Muy pulida | ⭐⭐⭐ Básica |

---

**Autor:** Sistema Ticketify  
**Fecha:** Noviembre 2025  
**Versión:** 1.0
