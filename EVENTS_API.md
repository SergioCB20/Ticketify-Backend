# 🎫 Events API - Ticketify Backend

Implementación completa del API de eventos para Ticketify.

## 📋 Endpoints Implementados

### **POST /api/events/**
Crear un nuevo evento (requiere autenticación)

**Body:**
```json
{
  "title": "Concierto Rock en Vivo 2025",
  "description": "Las mejores bandas de rock en un solo lugar",
  "startDate": "2025-11-15T20:00:00",
  "endDate": "2025-11-15T23:00:00",
  "venue": "Estadio Nacional, Lima",
  "totalCapacity": 5000,
  "multimedia": ["https://example.com/image1.jpg"],
  "category_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Response:** `201 Created` - EventResponse

---

### **GET /api/events/**
Obtener lista de eventos con filtros y paginación

**Query Parameters:**
- `page` (int, default=1): Número de página
- `page_size` (int, default=10, max=100): Elementos por página
- `status` (string): Filtrar por estado (DRAFT, PUBLISHED, CANCELLED, COMPLETED)
- `category_id` (UUID): Filtrar por categoría
- `organizer_id` (UUID): Filtrar por organizador
- `search` (string): Buscar en título, descripción, venue
- `start_date_from` (datetime): Eventos desde esta fecha
- `start_date_to` (datetime): Eventos hasta esta fecha

**Response:** `200 OK` - EventListResponse

---

### **GET /api/events/upcoming**
Obtener eventos próximos publicados

**Query Parameters:**
- `page` (int, default=1)
- `page_size` (int, default=10)

**Response:** `200 OK` - EventListResponse

---

### **GET /api/events/featured**
Obtener eventos destacados

**Query Parameters:**
- `limit` (int, default=6, max=20): Número de eventos

**Response:** `200 OK` - List[EventResponse]

---

### **GET /api/events/my-events**
Obtener mis eventos (requiere autenticación)

**Query Parameters:**
- `page` (int, default=1)
- `page_size` (int, default=10)

**Response:** `200 OK` - EventListResponse

---

### **GET /api/events/search**
Buscar eventos

**Query Parameters:**
- `q` (string, min=2): Término de búsqueda
- `page` (int, default=1)
- `page_size` (int, default=10)

**Response:** `200 OK` - EventListResponse

---

### **GET /api/events/{event_id}**
Obtener evento por ID

**Response:** `200 OK` - EventResponse

---

### **PUT /api/events/{event_id}**
Actualizar evento (requiere autenticación, solo organizador o admin)

**Body:**
```json
{
  "title": "Concierto Rock ACTUALIZADO",
  "totalCapacity": 6000
}
```

**Response:** `200 OK` - EventResponse

---

### **PATCH /api/events/{event_id}/status**
Actualizar estado del evento (requiere autenticación, solo organizador o admin)

**Body:**
```json
{
  "status": "PUBLISHED"
}
```

**Response:** `200 OK` - EventResponse

---

### **DELETE /api/events/{event_id}**
Eliminar evento (requiere autenticación, solo organizador o admin)

**Response:** `200 OK` - MessageResponse

---

## 📦 Estructura de Archivos Creados

```
app/
├── api/
│   ├── events.py          ✅ Router con todos los endpoints
│   └── __init__.py        ✅ Actualizado para incluir events router
├── models/
│   └── event.py           ✅ Ya existía
├── schemas/
│   └── event.py           ✅ NUEVO - Schemas de request/response
├── repositories/
│   └── event_repository.py ✅ NUEVO - Capa de acceso a datos
└── services/
    └── event_service.py    ✅ NUEVO - Lógica de negocio
```

## 🔐 Autenticación

Endpoints que requieren autenticación:
- `POST /api/events/` - Crear evento
- `GET /api/events/my-events` - Mis eventos
- `PUT /api/events/{event_id}` - Actualizar evento
- `PATCH /api/events/{event_id}/status` - Cambiar estado
- `DELETE /api/events/{event_id}` - Eliminar evento

**Header requerido:**
```
Authorization: Bearer {access_token}
```

## 🎯 Estados de Evento

- **DRAFT**: Borrador (recién creado)
- **PUBLISHED**: Publicado (visible para usuarios)
- **CANCELLED**: Cancelado
- **COMPLETED**: Completado

## 📊 Response Schemas

### EventResponse
```json
{
  "id": "uuid",
  "title": "string",
  "description": "string | null",
  "startDate": "datetime",
  "endDate": "datetime",
  "venue": "string",
  "totalCapacity": "integer",
  "status": "string",
  "multimedia": ["string"],
  "availableTickets": "integer",
  "isSoldOut": "boolean",
  "organizerId": "uuid",
  "categoryId": "uuid | null",
  "createdAt": "datetime",
  "updatedAt": "datetime"
}
```

### EventListResponse
```json
{
  "events": [EventResponse],
  "total": "integer",
  "page": "integer",
  "pageSize": "integer",
  "totalPages": "integer"
}
```

## 🚀 Pruebas con cURL

### Crear evento
```bash
curl -X POST "http://localhost:8000/api/events/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Mi Evento de Prueba",
    "description": "Descripción del evento",
    "startDate": "2025-12-01T20:00:00",
    "endDate": "2025-12-01T23:00:00",
    "venue": "Lima, Perú",
    "totalCapacity": 100
  }'
```

### Listar eventos
```bash
curl -X GET "http://localhost:8000/api/events/?page=1&page_size=10"
```

### Buscar eventos
```bash
curl -X GET "http://localhost:8000/api/events/search?q=concierto"
```

### Obtener evento por ID
```bash
curl -X GET "http://localhost:8000/api/events/{event_id}"
```

## 📝 Validaciones

### Crear/Actualizar Evento
- ✅ `title`: 3-200 caracteres
- ✅ `startDate`: Debe ser fecha futura
- ✅ `endDate`: Debe ser posterior a startDate
- ✅ `venue`: 3-200 caracteres
- ✅ `totalCapacity`: Mayor a 0
- ✅ Solo organizador o admin puede editar
- ✅ No se puede eliminar evento con tickets vendidos

### Permisos
- ✅ Solo usuarios autenticados pueden crear eventos
- ✅ Solo el organizador o admin pueden editar/eliminar
- ✅ Cualquiera puede ver eventos publicados

## 🔄 Integración con Frontend

El frontend en `/events/crear` debe hacer una petición POST a:

```javascript
const response = await fetch('http://localhost:8000/api/events/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${accessToken}`
  },
  body: JSON.stringify({
    title: formData.nombre,
    description: formData.descripcion,
    startDate: constructDate(formData.fechaInicio),
    endDate: constructDate(formData.fechaFin),
    venue: formData.ubicacion,
    totalCapacity: parseInt(formData.capacidad),
    multimedia: [imageUrl, videoUrl], // URLs de archivos subidos
    category_id: formData.categoria
  })
})
```

## 🐛 Códigos de Error

- `400 Bad Request`: Datos inválidos o validación fallida
- `401 Unauthorized`: No autenticado
- `403 Forbidden`: Sin permisos
- `404 Not Found`: Evento no encontrado
- `500 Internal Server Error`: Error del servidor

## ✅ Testing

Para probar la API:

1. Iniciar el servidor:
```bash
cd Backend\ Actualizado/Ticketify-Backend
python run.py
```

2. Acceder a la documentación interactiva:
```
http://localhost:8000/docs
```

3. Primero autenticarse en `/api/auth/login` para obtener el token

4. Usar el token en el botón "Authorize" de Swagger

5. Probar los endpoints de eventos

## 📚 Documentación Adicional

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

**Implementado por:** Claude AI
**Fecha:** 30 de Octubre, 2025
**Versión:** 1.0.0
