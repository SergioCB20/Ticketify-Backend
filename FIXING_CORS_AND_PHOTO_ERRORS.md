# 🔧 Guía para Solucionar Errores CORS y de Fotos

## 📋 Problemas Identificados

### 1. **Errores CORS**
Los errores que estás viendo son:
```
Access to XMLHttpRequest at 'http://localhost:8000/api/events/my-events' from origin 'http://localhost:3000' has been blocked by CORS policy
Access to XMLHttpRequest at 'http://localhost:8000/api/categories/?active_only=true' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Causa**: La configuración CORS no estaba permitiendo correctamente las peticiones del frontend.

### 2. **Campo `photo` vs `multimedia`**
El modelo de Event tiene dos campos:
- `photo`: LargeBinary (imagen guardada en la base de datos)
- `multimedia`: ARRAY(String) (URLs de imágenes)

Actualmente estamos usando `photo` para almacenar las imágenes.

---

## ✅ Soluciones Aplicadas

### **1. Configuración CORS mejorada**

#### **Archivo `.env` actualizado:**
```env
ALLOWED_HOSTS=["http://localhost:3000","http://localhost:3000/","http://127.0.0.1:3000"]
```

#### **Archivo `app/main.py` actualizado:**
```python
# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)
```

**Cambios realizados:**
- ✅ Se agregó soporte explícito para métodos HTTP (incluyendo OPTIONS para preflight requests)
- ✅ Se agregó `expose_headers` para permitir que el frontend lea headers de respuesta
- ✅ Se agregó `max_age` para cachear las respuestas preflight
- ✅ Se agregaron múltiples orígenes permitidos en el .env

---

### **2. Endpoint de Fotos Corregido**

#### **Archivo `app/api/events.py`:**

```python
@router.get("/{event_id}/photo")
async def get_event_photo(
    event_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Obtener la foto de un evento como respuesta binaria.
    """
    from fastapi.responses import Response
    
    event_service = EventService(db)
    event = event_service.event_repo.get_event_by_id(event_id)
    
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    if not event.photo:
        raise HTTPException(status_code=404, detail="El evento no tiene foto")
    
    # Retornar la imagen como bytes
    return Response(content=event.photo, media_type="image/jpeg")
```

**Cambios realizados:**
- ✅ Endpoint ahora devuelve correctamente los bytes de la imagen
- ✅ Se agregó validación de existencia de evento y foto
- ✅ Se usa `Response` para devolver contenido binario

---

### **3. Servicio de Eventos Corregido**

#### **Archivo `app/services/event_service.py`:**

```python
def _event_to_response(self, event: Event) -> EventResponse:
    """Convierte modelo SQLAlchemy a esquema Pydantic"""
    # Crear diccionario de categoría si existe
    category_dict = None
    if event.category:
        category_dict = {
            "id": str(event.category.id),
            "name": event.category.name,
            "slug": event.category.slug,
            "description": event.category.description,
            "icon": event.category.icon,
            "colorCode": event.category.color_code,
            "isActive": event.category.is_active,
            "isFeatured": event.category.is_featured,
            "sortOrder": event.category.sort_order
        }
    
    return EventResponse(
        id=event.id,
        title=event.title,
        description=event.description,
        startDate=event.startDate,
        endDate=event.endDate,
        venue=event.venue,
        totalCapacity=event.totalCapacity,
        status=event.status.value,
        photoUrl=f"/api/events/{event.id}/photo" if event.photo else None,  # ✅ AGREGADO
        availableTickets=getattr(event, "available_tickets", 0),
        isSoldOut=getattr(event, "is_sold_out", False),
        organizerId=event.organizer_id,
        categoryId=event.category_id,
        category=category_dict,
        minPrice=event.min_price,
        maxPrice=event.max_price,
        createdAt=event.createdAt,
        updatedAt=event.updatedAt,
        ticket_types=[tt.to_dict() for tt in event.ticket_types] if event.ticket_types else []
    )
```

**Cambios realizados:**
- ✅ Se agregó el campo `photoUrl` en la respuesta
- ✅ Se corrigió el error de `category_dict` no definido
- ✅ Se agregó validación para evitar errores con `ticket_types`

---

## 🚀 Pasos para Aplicar los Cambios

### **1. Reiniciar el Backend**

```bash
# Detener el servidor si está corriendo (Ctrl+C)

# Reiniciar el servidor
cd "C:\PUCP FCI ING.INF 2025-2\Ingeniería de Software\Segundo Backend\Ticketify-Backend"
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **2. Verificar que el Backend esté corriendo**

Abre tu navegador y ve a:
```
http://localhost:8000/docs
```

### **3. Limpiar caché del navegador (Frontend)**

1. Abre las DevTools (F12)
2. Haz clic derecho en el botón de "Refresh" (recargar)
3. Selecciona "Empty Cache and Hard Reload"

### **4. Reiniciar el Frontend**

```bash
# Detener el servidor frontend (Ctrl+C)

# Limpiar caché de npm (opcional)
npm cache clean --force

# Reiniciar
npm run dev
```

---

## 🧪 Verificar que Todo Funcione

### **1. Verificar CORS**

Abre la consola del navegador (F12) y ejecuta:

```javascript
fetch('http://localhost:8000/api/categories/?active_only=true')
  .then(res => res.json())
  .then(data => console.log('✅ Categorías:', data))
  .catch(err => console.error('❌ Error:', err));
```

### **2. Verificar Endpoint de Eventos**

```javascript
fetch('http://localhost:8000/api/events/search?limit=5')
  .then(res => res.json())
  .then(data => console.log('✅ Eventos:', data))
  .catch(err => console.error('❌ Error:', err));
```

### **3. Verificar Fotos de Eventos**

Si tienes eventos con fotos, prueba en el navegador:
```
http://localhost:8000/api/events/{event_id}/photo
```

---

## 🔍 Archivos Modificados

1. ✅ `.env` - Configuración de CORS actualizada
2. ✅ `app/main.py` - Middleware CORS mejorado
3. ✅ `app/api/events.py` - Endpoint de fotos corregido
4. ✅ `app/services/event_service.py` - Método `_event_to_response` corregido

---

## 📝 Notas Adicionales

### **Sobre el campo `photo`:**
- Actualmente usamos `photo: LargeBinary` para guardar imágenes directamente en PostgreSQL
- El campo `multimedia: ARRAY(String)` está disponible pero no se usa actualmente
- Si quieres cambiar a usar URLs en vez de binarios, deberías:
  1. Migrar las imágenes a un servicio de archivos (como AWS S3, Cloudinary, etc.)
  2. Guardar las URLs en el campo `multimedia`
  3. Actualizar los endpoints para usar URLs

### **Recomendaciones:**
1. ✅ Para producción, considera usar un servicio de almacenamiento externo para las imágenes
2. ✅ Configura límites de tamaño para las imágenes subidas (actualmente 5MB en `.env`)
3. ✅ Implementa compresión de imágenes antes de guardarlas en la DB

---

## ❓ Si Aún Hay Problemas

### **Error: "Network Error" o "Failed to fetch"**

1. Verifica que el backend esté corriendo en el puerto 8000
2. Verifica que no haya un firewall bloqueando la conexión
3. Prueba acceder directamente a `http://localhost:8000/docs`

### **Error: "CORS policy"**

1. Asegúrate de haber reiniciado el backend después de los cambios
2. Verifica que el archivo `.env` tenga la configuración correcta
3. Limpia el caché del navegador

### **Error: "404 Not Found" en fotos**

1. Verifica que el evento tenga una foto guardada en la DB
2. Usa el endpoint POST `/api/events/{event_id}/upload-photo` para subir una foto
3. Verifica en la base de datos que el campo `photo` no sea NULL

---

## 📞 Contacto

Si sigues teniendo problemas, revisa:
- Los logs del backend en la terminal
- La consola del navegador (F12 → Console)
- La pestaña Network en DevTools para ver las peticiones HTTP

---

**Última actualización:** 2025-01-14
