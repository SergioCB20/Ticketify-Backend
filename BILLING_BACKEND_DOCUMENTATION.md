# 📊 Sistema de Facturación Backend - Documentación Completa

## 🎯 Descripción General

Sistema completo de facturación para organizadores de eventos integrado con MercadoPago. Permite consultar ingresos, comisiones, transacciones y generar reportes detallados.

---

## 📁 Estructura de Archivos Creados

```
app/
├── api/
│   └── billing.py                      ✅ NUEVO - Endpoints REST API
│
├── services/
│   └── billing_service.py              ✅ NUEVO - Lógica de negocio
│
├── repositories/
│   └── billing_repository.py           ✅ NUEVO - Consultas a DB
│
└── schemas/
    └── billing.py                      ✅ NUEVO - Modelos Pydantic
```

---

## 🔌 Endpoints Disponibles

### Base URL: `/api/organizer/billing`

### 1. **GET** `/events`
📊 Obtener lista de eventos con datos de facturación

**Headers:**
```
Authorization: Bearer {access_token}
```

**Respuesta:**
```json
[
  {
    "id": "uuid",
    "title": "Nombre del Evento",
    "startDate": "2025-01-15T19:00:00Z",
    "totalRevenue": 15000.00,
    "totalTransactions": 50,
    "netAmount": 13425.00,
    "status": "PUBLISHED"
  }
]
```

**Códigos de Estado:**
- `200 OK`: Lista retornada exitosamente
- `403 Forbidden`: Usuario no es organizador
- `500 Internal Server Error`: Error en el servidor

---

### 2. **GET** `/events/{event_id}`
📈 Obtener detalle completo de facturación

**Headers:**
```
Authorization: Bearer {access_token}
```

**Parámetros:**
- `event_id` (path): UUID del evento

**Respuesta:**
```json
{
  "eventId": "uuid",
  "eventName": "Concierto de Rock",
  "eventDate": "2025-01-15T19:00:00Z",
  "summary": {
    "totalRevenue": 15000.00,
    "totalTransactions": 50,
    "commissions": {
      "mercadoPago": {
        "amount": 748.50,
        "percentage": 4.99
      },
      "platform": {
        "amount": 450.00,
        "percentage": 3.0
      },
      "total": 1198.50
    },
    "netAmount": 13801.50,
    "accreditation": {
      "credited": 10000.00,
      "pending": 3801.50,
      "nextDate": "2025-02-05T00:00:00Z"
    }
  },
  "paymentMethods": [
    {
      "method": "CREDIT_CARD",
      "count": 30,
      "amount": 9000.00,
      "percentage": 60.0
    },
    {
      "method": "DEBIT_CARD",
      "count": 20,
      "amount": 6000.00,
      "percentage": 40.0
    }
  ],
  "transactions": [
    {
      "id": "uuid",
      "mpPaymentId": "1234567890",
      "date": "2025-01-10T14:30:00Z",
      "buyerEmail": "comprador@email.com",
      "amount": 300.00,
      "mpCommission": 14.97,
      "platformCommission": 9.00,
      "netAmount": 276.03,
      "status": "approved",
      "paymentMethod": "CREDIT_CARD",
      "accreditationDate": "2025-01-24T14:30:00Z",
      "mpLink": "https://www.mercadopago.com.pe/activities/1234567890"
    }
  ],
  "lastSync": "2025-01-15T10:00:00Z"
}
```

**Códigos de Estado:**
- `200 OK`: Detalle retornado exitosamente
- `400 Bad Request`: ID de evento inválido
- `403 Forbidden`: Usuario no es organizador
- `404 Not Found`: Evento no encontrado o sin permisos
- `500 Internal Server Error`: Error en el servidor

---

### 3. **POST** `/events/{event_id}/sync`
🔄 Sincronizar con MercadoPago

**Headers:**
```
Authorization: Bearer {access_token}
```

**Parámetros:**
- `event_id` (path): UUID del evento

**Respuesta:**
```json
{
  "message": "Sincronización completada. 15 transacciones actualizadas.",
  "transactionsUpdated": 15,
  "lastSync": "2025-01-15T10:30:00Z"
}
```

**Códigos de Estado:**
- `200 OK`: Sincronización exitosa
- `400 Bad Request`: Cuenta de MercadoPago no vinculada o ID inválido
- `403 Forbidden`: Usuario no es organizador
- `404 Not Found`: Evento no encontrado
- `500 Internal Server Error`: Error en la sincronización

---

### 4. **GET** `/events/{event_id}/report`
📥 Descargar reporte (PDF o Excel)

**Headers:**
```
Authorization: Bearer {access_token}
```

**Parámetros:**
- `event_id` (path): UUID del evento
- `format` (query): `pdf` o `excel`

**Ejemplo:**
```
GET /api/organizer/billing/events/{event_id}/report?format=pdf
GET /api/organizer/billing/events/{event_id}/report?format=excel
```

**Respuesta:**
- Archivo binario (PDF o XLSX)
- Header `Content-Disposition`: `attachment; filename=facturacion_evento.pdf`

**Códigos de Estado:**
- `200 OK`: Reporte generado exitosamente
- `400 Bad Request`: Formato inválido o ID inválido
- `403 Forbidden`: Usuario no es organizador
- `404 Not Found`: Evento no encontrado
- `500 Internal Server Error`: Error generando el reporte

---

### 5. **GET** `/status`
🔍 Verificar estado del sistema (Debugging)

**Headers:**
```
Authorization: Bearer {access_token}
```

**Respuesta:**
```json
{
  "status": "operational",
  "organizerId": "uuid",
  "organizerEmail": "organizador@email.com",
  "mercadopagoConnected": true,
  "mercadopagoEmail": "mp@email.com",
  "totalEvents": 5,
  "hasEvents": true
}
```

---

## 💾 Modelos de Base de Datos Utilizados

### Tablas Principales:
- ✅ `events` - Información de eventos
- ✅ `purchases` - Compras realizadas
- ✅ `payments` - Pagos procesados
- ✅ `users` - Usuarios (organizadores)

### Relaciones:
```
Event (1) ──── (N) Purchase
Purchase (1) ──── (1) Payment
User (1) ──── (N) Event (como organizador)
```

---

## 🔐 Autenticación y Autorización

### Requisitos:
1. **Usuario autenticado** con token JWT válido
2. **Rol ORGANIZER** asignado
3. **Propiedad del evento** (el organizador debe ser dueño del evento)

### Ejemplo de Header:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 🔗 Integración con MercadoPago

### Configuración Necesaria:

1. **Token de Acceso del Organizador**
   - Almacenado en: `users.mercadopagoAccessToken`
   - Obtenido vía OAuth de MercadoPago

2. **SDK de MercadoPago**
   ```python
   import mercadopago
   sdk = mercadopago.SDK(access_token)
   ```

3. **Consulta de Pagos**
   - Endpoint usado: `sdk.payment().search()`
   - Filtro: `external_reference` (ID de preferencia)

### Datos Sincronizados:
- ✅ Estado del pago (`approved`, `pending`, `rejected`)
- ✅ ID de transacción de MercadoPago
- ✅ Método de pago usado
- ✅ Fecha de aprobación
- ✅ Detalles de comisiones
- ✅ Fecha de acreditación estimada

---

## 💰 Cálculo de Comisiones

### Comisión de MercadoPago: **4.99%**
```python
mp_commission = total_amount * 0.0499
```

### Comisión de Plataforma: **3%**
```python
platform_commission = total_amount * 0.03
```

### Monto Neto:
```python
net_amount = total_amount - mp_commission - platform_commission
```

### Ejemplo:
- Venta: S/. 100.00
- Com. MP: S/. 4.99
- Com. Plataforma: S/. 3.00
- **Neto Organizador: S/. 92.01**

---

## 📅 Acreditación de Fondos

### Lógica:
- **Tiempo de acreditación:** 14 días después del pago
- **Fondos acreditados:** Pagos con más de 14 días
- **Fondos pendientes:** Pagos con menos de 14 días

### Cálculo:
```python
accreditation_date = payment_date + timedelta(days=14)

if accreditation_date <= now:
    # Fondos acreditados
else:
    # Fondos pendientes
```

---

## 📊 Reportes Generados

### Reporte PDF
**Incluye:**
- Título con nombre del evento
- Fecha del evento
- Tabla de resumen financiero
- Tabla de métodos de pago
- Formato profesional con colores

**Librería:** `reportlab`

### Reporte Excel
**Incluye:**
- Hoja "Facturación"
- Resumen financiero
- Lista completa de transacciones
- Formato con:
  - Encabezados en negrita
  - Formato de moneda (S/.)
  - Anchos de columna ajustados

**Librería:** `openpyxl`

---

## 🧪 Testing

### Dependencias Requeridas:
```bash
pip install mercadopago
pip install reportlab
pip install openpyxl
```

### Probar Endpoints:

#### 1. Obtener lista de eventos:
```bash
curl -X GET "http://localhost:8000/api/organizer/billing/events" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 2. Obtener detalle:
```bash
curl -X GET "http://localhost:8000/api/organizer/billing/events/{EVENT_ID}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 3. Sincronizar:
```bash
curl -X POST "http://localhost:8000/api/organizer/billing/events/{EVENT_ID}/sync" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 4. Descargar PDF:
```bash
curl -X GET "http://localhost:8000/api/organizer/billing/events/{EVENT_ID}/report?format=pdf" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output reporte.pdf
```

#### 5. Descargar Excel:
```bash
curl -X GET "http://localhost:8000/api/organizer/billing/events/{EVENT_ID}/report?format=excel" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output reporte.xlsx
```

---

## 🚨 Manejo de Errores

### Errores Comunes:

#### 1. Usuario no es organizador
```json
{
  "detail": "Solo los organizadores pueden acceder a esta funcionalidad"
}
```
**Solución:** Asignar rol `ORGANIZER` al usuario

#### 2. Evento no encontrado
```json
{
  "detail": "Evento no encontrado o no tienes permisos para verlo"
}
```
**Solución:** Verificar que el evento exista y pertenezca al organizador

#### 3. MercadoPago no vinculado
```json
{
  "detail": "No tienes una cuenta de MercadoPago vinculada"
}
```
**Solución:** Vincular cuenta de MercadoPago desde `/api/mercadopago/connect`

#### 4. ID inválido
```json
{
  "detail": "ID de evento inválido"
}
```
**Solución:** Usar un UUID válido

---

## 🔧 Configuración del Servidor

### Variables de Entorno (.env):
```env
# MercadoPago OAuth
MERCADOPAGO_CLIENT_ID=your_client_id
MERCADOPAGO_CLIENT_SECRET=your_client_secret
MERCADOPAGO_REDIRECT_URI=http://localhost:8000/api/mercadopago/callback

# Base de datos
DATABASE_URL=postgresql://user:pass@localhost/ticketify

# JWT
JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
```

### Iniciar Servidor:
```bash
python run.py
```

O:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📝 Notas Importantes

### 1. Seguridad
- ✅ Todos los endpoints requieren autenticación
- ✅ Verificación de rol ORGANIZER
- ✅ Verificación de propiedad del evento
- ✅ Tokens de MercadoPago encriptados en DB

### 2. Performance
- ✅ Uso de `joinedload` para optimizar queries
- ✅ Cálculos en memoria cuando sea posible
- ✅ Índices en campos clave (`event_id`, `user_id`)

### 3. Escalabilidad
- 📊 Preparado para manejar miles de transacciones
- 🔄 Sincronización asíncrona recomendada para producción
- 📈 Reportes generados on-demand

### 4. Mantenimiento
- 📝 Logging de errores implementado
- 🔍 Endpoint de status para monitoring
- 🧪 Estructura modular para fácil testing

---

## 🚀 Próximos Pasos

### Mejoras Sugeridas:

1. **Caché de Reportes**
   - Redis para cachear reportes generados
   - TTL de 1 hora

2. **Sincronización Automática**
   - Webhook de MercadoPago para actualización en tiempo real
   - Background tasks con Celery

3. **Analytics Avanzados**
   - Gráficos de tendencias
   - Comparativas entre eventos
   - Predicciones de ingresos

4. **Notificaciones**
   - Email cuando se acrediten fondos
   - Alertas de transacciones rechazadas
   - Resumen semanal de ventas

5. **Exportación Masiva**
   - Reportes de múltiples eventos
   - Consolidado mensual/anual
   - Integración con sistemas contables

---

## 📧 Soporte

Para consultas o problemas:
- 📖 Revisar esta documentación
- 🐛 Verificar logs del servidor
- 🔍 Usar endpoint `/api/organizer/billing/status`
- 💬 Contactar al equipo de desarrollo

---

**Versión:** 1.0.0  
**Última actualización:** Noviembre 2025  
**Estado:** ✅ Producción Ready
