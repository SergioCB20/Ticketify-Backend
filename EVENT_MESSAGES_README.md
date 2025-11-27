# Sistema de Mensajes a Asistentes - Ticketify

## 📋 Descripción

Sistema completo para que los organizadores puedan enviar mensajes a los asistentes de sus eventos. Incluye envío de emails, historial de mensajes, estadísticas y preview de destinatarios.

## ✅ Implementación Completada

### Backend

1. **Modelo EventMessage** (`app/models/event_message.py`)
   - Almacena mensajes con estadísticas de envío
   - Tipos: BROADCAST, FILTERED, INDIVIDUAL
   - Tracking de éxito/fallos

2. **Schema Pydantic** (`app/schemas/event_message.py`)
   - EventMessageCreate
   - EventMessageResponse
   - EventAttendeeResponse
   - MessageStatsResponse

3. **Repository** (`app/repositories/event_message_repository.py`)
   - CRUD completo para mensajes
   - Consultas optimizadas
   - Estadísticas agregadas

4. **Service** (`app/services/event_message_service.py`)
   - Lógica de negocio para envío de mensajes
   - Obtención de asistentes
   - Validación de permisos

5. **Email Service** (extendido en `app/utils/email_service.py`)
   - Template profesional para mensajes del organizador
   - Incluye información del evento
   - Footer con branding

6. **API Endpoints** (`app/api/event_messages.py`)
   - `POST /api/events/{event_id}/messages` - Enviar mensaje
   - `GET /api/events/{event_id}/messages` - Historial (paginado)
   - `GET /api/events/{event_id}/messages/{message_id}` - Detalles
   - `GET /api/events/{event_id}/attendees` - Lista de asistentes
   - `GET /api/events/{event_id}/messages/stats` - Estadísticas

7. **Migración Alembic** (`alembic/versions/20251126_1200_add_event_messages.py`)
   - Crea tabla `event_messages`
   - Índices optimizados
   - Enum MessageType

### Frontend

1. **Servicio API** (`src/services/eventMessageService.ts`)
   - Métodos TypeScript para todos los endpoints
   - Tipos e interfaces definidos

2. **Modal de Envío** (`src/components/organizer/SendMessageModal.tsx`)
   - Editor de mensaje con validación
   - Preview de destinatarios
   - Contador de caracteres
   - Estados de carga y éxito
   - Manejo de errores

3. **Página de Historial** (`src/app/panel/my-events/[id]/messages/page.tsx`)
   - Dashboard con estadísticas
   - Lista de mensajes enviados
   - Paginación
   - Tarjetas de estadísticas (total mensajes, destinatarios, tasa de éxito)

4. **Botón de Acceso Rápido** (`src/components/organizer/EventMessagesButton.tsx`)
   - Botón para integrar en dashboards de eventos

## 🚀 Cómo Usar

### 1. Ejecutar Migración de Base de Datos

```bash
cd Ticketify-Backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
alembic upgrade head
```

### 2. Iniciar Backend

```bash
python run.py
```

El backend estará disponible en `http://localhost:8000`

### 3. Iniciar Frontend

```bash
cd ../Ticketify-Frontend
npm install
npm run dev
```

El frontend estará disponible en `http://localhost:3000`

### 4. Usar el Sistema

1. **Acceder como Organizador:**
   - Ve a "Mis Eventos"
   - Selecciona un evento
   - Click en "Mensajes" o ir a `/panel/my-events/{event_id}/messages`

2. **Enviar Mensaje:**
   - Click en "Enviar Nuevo Mensaje"
   - Completa el asunto (máx 200 caracteres)
   - Escribe el mensaje (máx 5000 caracteres)
   - El sistema mostrará cuántos asistentes recibirán el mensaje
   - Click en "Enviar Mensaje"

3. **Ver Historial:**
   - La página principal muestra todos los mensajes enviados
   - Ver estadísticas: total mensajes, destinatarios, tasa de éxito
   - Cada mensaje muestra: asunto, fecha, destinatarios, éxitos/fallos

## 📊 Características

### Seguridad
- ✅ Validación de que el usuario es el organizador del evento
- ✅ Sanitización de contenido HTML
- ✅ Límite de caracteres (200 asunto, 5000 mensaje)
- ✅ Solo asistentes con tickets activos reciben mensajes

### Performance
- ✅ Paginación en historial (10 mensajes por página)
- ✅ Queries optimizadas con índices
- ✅ Carga asíncrona de asistentes

### UX/UI
- ✅ Preview de destinatarios antes de enviar
- ✅ Estados de carga con indicadores visuales
- ✅ Mensajes de éxito/error claros
- ✅ Contador de caracteres en tiempo real
- ✅ Dashboard con estadísticas visuales
- ✅ Design responsive (móvil y desktop)

### Emails
- ✅ Template profesional con gradientes
- ✅ Información del evento incluida
- ✅ Botón de CTA a "Ver Mis Tickets"
- ✅ Footer con branding de Ticketify
- ✅ Versión texto plano como fallback

## 🔧 Integración en Dashboard Existente

Para agregar el botón de mensajes en la vista de detalles de un evento:

```tsx
import EventMessagesButton from "@/components/organizer/EventMessagesButton";

// Dentro de tu componente:
<EventMessagesButton eventId={eventId} />
```

## 📝 Notas Técnicas

### Base de Datos
- Tabla: `event_messages`
- Relaciones: Event (CASCADE DELETE), User (organizador)
- Índices en: id, event_id, organizer_id

### Validaciones
- Solo usuarios con `isActive = true` reciben mensajes
- Solo tickets con `status = 'ACTIVE'` se consideran
- Evita duplicados (usuarios con múltiples tickets)

### Estadísticas
- `totalRecipients`: Suma de todos los destinatarios
- `successfulSends`: Emails enviados exitosamente
- `failedSends`: Emails que fallaron
- `successRate`: Porcentaje calculado automáticamente

## 🎯 Endpoints API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/events/{id}/messages` | Enviar mensaje a asistentes |
| GET | `/api/events/{id}/messages` | Listar mensajes (paginado) |
| GET | `/api/events/{id}/messages/{msg_id}` | Detalles de un mensaje |
| GET | `/api/events/{id}/attendees` | Lista de asistentes |
| GET | `/api/events/{id}/messages/stats` | Estadísticas de mensajes |

## ⚠️ Consideraciones

1. **Rate Limiting**: Actualmente no implementado. Considerar agregar para producción (max 10 mensajes/hora por organizador)

2. **Envío Asíncrono**: Los emails se envían síncronamente. Para eventos con +100 asistentes, considerar usar Celery o background tasks

3. **Tracking de Aperturas**: No implementado. Para analytics avanzados, agregar tracking pixels

4. **Respuestas**: Los asistentes no pueden responder directamente. Considerar agregar esta funcionalidad

## 🐛 Troubleshooting

### Error: "MERCADOPAGO_PRODUCER_TOKEN field required"
- Asegúrate de que el `.env` tenga todas las variables requeridas
- La migración ya está lista, solo ejecutar `alembic upgrade head`

### Emails no se envían
- Verificar configuración SMTP en `.env`
- Revisar logs del backend para errores específicos
- Comprobar que `SMTP_USERNAME` y `SMTP_PASSWORD` sean correctos

### No aparecen asistentes
- Verificar que el evento tenga tickets vendidos
- Confirmar que los tickets tengan `status = 'ACTIVE'`
- Revisar que los usuarios tengan `isActive = true`

## 📈 Futuras Mejoras (Opcional)

1. **Plantillas Guardadas**: Permitir guardar mensajes como plantillas reutilizables
2. **Programación de Envíos**: Enviar mensajes en fecha/hora específica
3. **Segmentación Avanzada**: Filtrar por tipo de ticket, fecha de compra, etc.
4. **Analytics**: Tasa de apertura de emails (requiere tracking)
5. **Respuestas**: Inbox para que organizadores reciban respuestas
6. **Adjuntos**: Permitir adjuntar archivos (PDFs, imágenes)
7. **Notificaciones Push**: Enviar también como notificaciones in-app

## ✨ Créditos

Sistema implementado para Ticketify - Plataforma de venta de tickets.

---

**Fecha de Implementación:** Noviembre 26, 2025
**Versión:** 1.0.0
