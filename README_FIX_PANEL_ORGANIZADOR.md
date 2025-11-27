# 🔧 Corrección del Panel de Organizador - Ticketify

## 📋 Problema Reportado

Al hacer clic en "Ver Panel" o "Editar" en un evento creado desde el panel del organizador, se producían errores 404 y el sistema no encontraba los eventos.

## 🔍 Diagnóstico

El problema tenía múltiples causas:

1. **Endpoint faltante**: El frontend llamaba a `/api/events/my-events` pero este endpoint no existía en el backend
2. **Método de servicio faltante**: El servicio `EventService` no tenía el método `get_events_by_organizer()`
3. **Integración incompleta**: El endpoint existía parcialmente pero con errores de implementación

## ✅ Soluciones Implementadas

### 1. Agregado Método al Servicio (event_service.py)

```python
def get_events_by_organizer(self, organizer_id: UUID) -> List[Event]:
    """
    Obtiene todos los eventos de un organizador específico
    """
    events = self.db.query(Event).filter(
        Event.organizer_id == organizer_id
    ).order_by(Event.startDate.desc()).all()
    
    return events

def get_events_vigentes_by_organizer(self, organizer_id: UUID) -> List[Event]:
    """
    Obtiene eventos vigentes (futuros y no cancelados) de un organizador
    """
    now = datetime.now(timezone.utc)
    events = self.db.query(Event).filter(
        Event.organizer_id == organizer_id,
        Event.startDate >= now,
        Event.status != EventStatus.CANCELLED
    ).order_by(Event.startDate.asc()).all()
    
    return events
```

### 2. Corregido Endpoint en API (events.py)

```python
@router.get("/my-events", response_model=List[OrganizerEventResponse])
async def get_my_events(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener todos los eventos creados por el usuario organizador autenticado
    """
    event_service = EventService(db)
    events = event_service.get_events_by_organizer(current_user.id)

    # Convertir Event → OrganizerEventResponse
    organizer_events = []
    for ev in events:
        # Calcular tickets vendidos sumando sold_quantity de todos los ticket_types
        sold_tickets = sum(tt.sold_quantity or 0 for tt in ev.ticket_types if ev.ticket_types else [])
        
        organizer_events.append(OrganizerEventResponse(
            id=str(ev.id),
            title=ev.title,
            date=ev.startDate.isoformat(),
            location=ev.venue,
            totalTickets=ev.totalCapacity,
            soldTickets=sold_tickets,
            status=ev.status.value if hasattr(ev.status, "value") else ev.status,
            imageUrl=f"/api/events/{ev.id}/photo" if ev.photo else None
        ))

    return organizer_events
```

### 3. Agregado Método en Frontend (events.ts)

```typescript
async getMyEvents(): Promise<OrganizerEventResponse[]> {
  try {
    const { data } = await api.get<OrganizerEventResponse[]>('/events/my-events')
    return data
  } catch (error) {
    throw handleApiError(error)
  }
}
```

## 🧪 Cómo Probar la Corrección

### Opción 1: Desde la Aplicación Web

1. Inicia el backend:
   ```bash
   cd Ticketify-Backend
   python run.py
   ```

2. Inicia el frontend:
   ```bash
   cd Ticketify-Frontend
   npm run dev
   ```

3. Inicia sesión como organizador

4. Ve a "Panel" → "Mis Eventos"

5. Deberías ver tu evento creado con:
   - Botón "Editar" funcional
   - Botón "Ver Panel" funcional
   - Información correcta de tickets vendidos

### Opción 2: Prueba del Endpoint Directa

Ejecuta el script de prueba:

```bash
cd Ticketify-Backend
python test_my_events_endpoint.py
```

Este script:
- Busca un usuario organizador
- Hace login y obtiene el token
- Llama al endpoint `/api/events/my-events`
- Muestra todos los eventos del organizador

### Opción 3: Prueba con cURL

```bash
# 1. Login (reemplaza con tus datos)
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"organizador@test.com","password":"tu_password"}'

# 2. Copiar el access_token de la respuesta

# 3. Llamar a my-events
curl -X GET http://localhost:8000/api/events/my-events \
  -H "Authorization: Bearer TU_TOKEN_AQUI"
```

## 📊 Estructura de Respuesta

El endpoint `/api/events/my-events` devuelve:

```json
[
  {
    "id": "uuid-del-evento",
    "title": "Nombre del Evento",
    "date": "2025-11-28T22:27:00",
    "location": "Lugar del evento",
    "totalTickets": 60,
    "soldTickets": 2,
    "status": "PUBLISHED",
    "imageUrl": "/api/events/uuid/photo"
  }
]
```

## 🔗 Rutas Disponibles Ahora

### Backend:
- `GET /api/events/my-events` - Obtener eventos del organizador autenticado ✅
- `GET /api/events/by-organizer/{organizer_id}` - Obtener eventos por ID de organizador ✅
- `GET /api/events/{event_id}` - Detalle de evento ✅
- `PUT /api/events/{event_id}` - Actualizar evento ✅
- `PATCH /api/events/{event_id}/status` - Cambiar estado ✅

### Frontend:
- `/panel/my-events` - Lista de eventos del organizador ✅
- `/panel/my-events/crear` - Crear nuevo evento ✅
- `/panel/my-events/[id]/edit` - Editar evento ✅
- `/panel/my-events/[id]/messages` - Mensajes del evento ✅

## 🚨 Solución de Problemas

### Error: "No tienes permisos de organizador"

**Causa**: El usuario no tiene el rol ORGANIZER asignado

**Solución**:
```bash
python asignar_rol_organizador.py email@usuario.com
```

O manualmente:
```python
from app.models.user import User
from app.models.role import Role

user = db.query(User).filter(User.email == "tu@email.com").first()
organizer_role = db.query(Role).filter(Role.name == "ORGANIZER").first()
user.roles.append(organizer_role)
db.commit()
```

### Error: "Token inválido" o 401

**Causa**: Sesión expirada o token incorrecto

**Solución**: Cierra sesión y vuelve a iniciar sesión

### Error 404 en "Ver Panel"

**Causa**: La ruta del panel puede estar mal configurada

**Solución**: Verifica que la ruta en el botón sea:
```typescript
<Link href={`/organizer/events/${event.id}`}>
```

Si tu estructura de rutas es diferente, ajusta según sea necesario.

## 📝 Archivos Modificados

1. ✅ `Ticketify-Backend/app/services/event_service.py`
   - Agregado `get_events_by_organizer()`
   - Agregado `get_events_vigentes_by_organizer()`

2. ✅ `Ticketify-Backend/app/api/events.py`
   - Corregido endpoint `/my-events`
   - Mejorada conversión a `OrganizerEventResponse`

3. ✅ `Ticketify-Frontend/src/services/api/events.ts`
   - Agregado método `getMyEvents()`

4. ✅ `Ticketify-Backend/test_my_events_endpoint.py`
   - Script de prueba del endpoint

## 🎯 Siguientes Pasos

Ahora que el panel funciona, puedes:

1. **Enviar mensajes a asistentes**:
   - Ve a "Mis Eventos"
   - Clic en "Ver Panel"
   - Busca el botón de "Enviar Mensaje" o similar

2. **Gestionar tickets del evento**:
   - Editar tipos de tickets
   - Ver estadísticas de ventas
   - Cambiar estado del evento

3. **Crear más eventos**:
   ```bash
   python crear_evento_organizador.py
   ```

## 🔍 Verificación Rápida

Ejecuta estos comandos para verificar que todo esté bien:

```bash
# 1. Verificar que hay organizadores
python verificar_sistema_eventos.py

# 2. Crear un evento si no existe
python crear_evento_organizador.py

# 3. Probar el endpoint
python test_my_events_endpoint.py

# 4. Abrir el navegador en el panel
# http://localhost:3000/panel/my-events
```

---

**Autor:** Sistema Ticketify  
**Fecha:** Noviembre 2025  
**Versión:** 1.0 - Panel Organizador Corregido
