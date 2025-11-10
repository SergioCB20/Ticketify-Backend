# Quick Summary 2 – Backend: Simulación de compra y procesamiento de pago

## ✅ ¿Qué se implementó?
- Simulación completa del proceso de compra de entradas desde el lado del asistente (`/api/purchases/process`)
- Validación de evento, disponibilidad y tipo de ticket
- Simulación de procesamiento de tarjeta (fallo para terminaciones 0000 y 1111)
- Registro de `Payment`, `Purchase` y `Ticket` en base de datos
- Generación de QR por ticket
- Descuento de stock (`available` y `sold`) del tipo de ticket

## 🗂 Archivos modificados o creados:
- `app/api/purchases.py` ➝ endpoint `POST /api/purchases/process`
- `app/models/purchase.py` ➝ se agregó columna `payment_id`
- `app/models/payment.py` ➝ se usa para registrar el pago simulado
- `alembic/versions/..._add_payment_id_to_purchase.py` ➝ migración para relacionar `Purchase` con `Payment`
- `app/models/ticket.py` ➝ se asegura que se genere el QR al crear ticket
- Otros: validaciones menores y relaciones de modelo

## 🔧 Cambios técnicos:
- Se agregó `payment_id` como FK en `Purchase`
- Se creó nuevo `Payment` al procesar compra
- Se usa `datetime.now(timezone.utc)` para fechas
- Se asegura `TicketType.available` y `sold` se actualicen correctamente

## 🧪 Cómo probar:
1. Iniciar backend (`alembic upgrade head` si es nueva migración)
2. Autenticarse como `attendee@test.com`
3. Hacer POST a `/api/purchases/process` desde frontend
4. Tarjetas para prueba:
   - `**** **** **** 0000`: Rechazada
   - `**** **** **** 1111`: Fondos insuficientes
   - `**** **** **** 1234`: Éxito
5. Verificar tablas: `payments`, `purchases`, `tickets`, `ticket_types`

## ⚠️ Notas:
- Asegurarse que el ticket tenga `ticket.generate_qr()` antes del `db.commit()`
- Se descarta la compra si falla alguna parte (`db.rollback()` controlado)
- Se actualizó correctamente el modelo SQL y la relación entre `Purchase` y `Payment`
