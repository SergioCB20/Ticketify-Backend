# Script de Verificación: Conversión de profilePhoto a Base64

## ✅ Estado Actual de Correcciones

### Archivos Corregidos:

1. **`app/api/marketplace.py`** ✅
   - Línea 58-60: `process_nested_user_photo(listing, 'seller')` en `get_active_listings`
   - Línea 134: `process_nested_user_photo(new_listing, 'seller')` en `create_listing`

2. **`app/services/admin_service.py`** ✅
   - Línea 74: `profilePhoto=user.get_profile_photo_base64()` en `get_user_by_id`

3. **`app/api/auth.py`** ✅
   - Ya estaba correcto usando `user.get_profile_photo_base64()`

### Verificación del Método `ban_user`:

El método `ban_user` en `admin_service.py` (líneas 93-104) **YA está correcto** porque:

```python
def ban_user(self, user_id: UUID, is_active: bool, ...) -> UserDetailResponse:
    user = self.user_repo.get_by_id(user_id)
    if not user:
        return None
    
    updated_user = self.user_repo.update(user, {"isActive": is_active})
    
    # 👇 ESTO YA USA LA CONVERSIÓN CORRECTA
    return self.get_user_by_id(updated_user.id)
```

El método `get_user_by_id` en la línea 74 ya tiene la conversión correcta:
```python
profilePhoto=user.get_profile_photo_base64()  # ✅ Correcto
```

Por lo tanto, **tanto BANEAR como DESBANEAR ya funcionan correctamente**.

---

## 🔍 Otros Lugares a Verificar

Si el error persiste, puede estar en otros endpoints. Aquí están los lugares comunes:

### 1. Endpoints de Eventos (si devuelven organizador)
**Archivo**: `app/api/events.py`

**Buscar**:
```python
# Si hay algo como:
return EventResponse(
    organizer=event.organizer  # ❌ Incorrecto
)

# Debería ser:
from app.utils.image_utils import process_user_photo
process_user_photo(event.organizer)
return EventResponse(
    organizer=event.organizer  # ✅ Correcto (después de procesar)
)
```

### 2. Endpoints de Tickets (si devuelven usuario)
**Archivo**: `app/api/tickets.py`

**Buscar**:
```python
# Si hay algo como:
tickets = db.query(Ticket).all()
return tickets  # ❌ Puede tener profilePhoto como bytes

# Debería ser:
from app.utils.image_utils import process_nested_user_photo
for ticket in tickets:
    process_nested_user_photo(ticket, 'user')
return tickets  # ✅ Correcto
```

### 3. Cualquier Schema de Pydantic con profilePhoto
**Archivos**: `app/schemas/*.py`

**Verificar que los schemas tengan**:
```python
from pydantic import BaseModel, field_validator
import base64

class UserResponse(BaseModel):
    profilePhoto: Optional[str] = None
    
    @field_validator('profilePhoto', mode='before')
    @classmethod
    def convert_photo(cls, v):
        if v is None:
            return None
        if isinstance(v, bytes):
            encoded = base64.b64encode(v).decode('utf-8')
            return f"data:image/jpeg;base64,{encoded}"
        return v
```

---

## 🧪 Cómo Diagnosticar el Error

Si el error persiste, sigue estos pasos:

### Paso 1: Identifica el endpoint exacto
Busca en los logs del backend la URL que causa el error:
```
INFO: 127.0.0.1:63733 - "GET /api/XXXXX HTTP/1.1" 500 Internal Server Error
```

### Paso 2: Encuentra el archivo
- `/api/admin/users/{id}` → `app/api/admin.py`
- `/api/events/{id}` → `app/api/events.py`
- `/api/tickets/...` → `app/api/tickets.py`
- `/api/auth/profile` → `app/api/auth.py`

### Paso 3: Aplica la solución

**Si el endpoint devuelve UN usuario**:
```python
from app.utils.image_utils import process_user_photo

user = db.query(User).first()
process_user_photo(user)  # Convertir bytes a base64
return user
```

**Si el endpoint devuelve MÚLTIPLES usuarios**:
```python
from app.utils.image_utils import process_user_photos_list

users = db.query(User).all()
process_user_photos_list(users)  # Convertir todos
return users
```

**Si el endpoint devuelve un objeto con usuario anidado**:
```python
from app.utils.image_utils import process_nested_user_photo

event = db.query(Event).first()
process_nested_user_photo(event, 'organizer')  # Convertir foto del organizador
return event
```

---

## ✅ Confirmación de Correcciones

### Ban/Unban Usuario:
```
POST /api/admin/users/{user_id}/ban
{
  "isActive": false  // Para banear
}
```

```
POST /api/admin/users/{user_id}/ban
{
  "isActive": true  // Para desbanear
}
```

**Ambos** ahora deberían funcionar sin el error de `profilePhoto` porque:
1. `ban_user()` llama a `get_user_by_id()`
2. `get_user_by_id()` usa `user.get_profile_photo_base64()`
3. `get_profile_photo_base64()` convierte bytes → base64

---

## 📝 Resumen

### ✅ Ya Corregido:
- Marketplace listings (vendedor)
- Admin: obtener usuario por ID
- Admin: banear/desbanear usuario
- Auth: perfil de usuario

### ⚠️ Verificar si es necesario:
- Events (si devuelven organizador)
- Tickets (si devuelven usuario)
- Purchases (si devuelven usuario)
- Cualquier otro endpoint que devuelva usuarios

---

## 🔧 Comando de Prueba Rápida

```bash
# Prueba banear un usuario
curl -X PATCH http://localhost:8000/api/admin/users/{user_id}/ban \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"isActive": false, "reason": "Test"}'

# Prueba desbanear un usuario
curl -X PATCH http://localhost:8000/api/admin/users/{user_id}/ban \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"isActive": true}'
```

Si estos funcionan sin error, significa que ban/unban están correctos. ✅
