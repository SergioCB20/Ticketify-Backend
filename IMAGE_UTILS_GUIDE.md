# Guía de Uso: Utilidades de Imagen (image_utils.py)

## ✅ Problema Resuelto

Antes el error era:
```
pydantic_core._pydantic_core.ValidationError: 1 validation error for MarketplaceListingResponse
seller.profilePhoto
  Input should be a valid string, unable to parse raw data as a unicode string 
  [type=string_unicode, input_value=b'RIFF...', input_type=bytes]
```

Ahora las fotos se convierten automáticamente de **bytes** a **base64 string**.

---

## 📦 Funciones Disponibles

### 1. `bytes_to_base64_url(data, mime_type='image/webp')`

Convierte bytes de imagen a data URL base64.

**Uso:**
```python
from app.utils.image_utils import bytes_to_base64_url

# Convertir bytes a base64
photo_bytes = b'\x89PNG...'
photo_base64 = bytes_to_base64_url(photo_bytes, 'image/png')
# Resultado: 'data:image/png;base64,iVBORw0KGgo...'
```

---

### 2. `process_user_photo(user, field_name='profilePhoto')`

Procesa la foto de un usuario **en el lugar** (modifica el objeto directamente).

**Uso básico:**
```python
from app.utils.image_utils import process_user_photo

# Cargar usuario de la BD
user = db.query(User).filter(User.id == user_id).first()

# Convertir profilePhoto de bytes a base64
process_user_photo(user)

# Ahora user.profilePhoto es un string base64
return user
```

**Con campo personalizado:**
```python
# Si tu foto se llama 'avatar' en lugar de 'profilePhoto'
process_user_photo(user, field_name='avatar')
```

---

### 3. `process_user_photos_list(users, field_name='profilePhoto')`

Procesa fotos de **múltiples usuarios** a la vez.

**Uso:**
```python
from app.utils.image_utils import process_user_photos_list

# Obtener lista de usuarios
users = db.query(User).all()

# Procesar todas las fotos
process_user_photos_list(users)

# Retornar usuarios con fotos convertidas
return users
```

---

### 4. `process_nested_user_photo(obj, user_field, photo_field='profilePhoto')`

Procesa la foto de un **usuario anidado** en otro objeto.

**Uso en Marketplace (ya implementado):**
```python
from app.utils.image_utils import process_nested_user_photo

# listing tiene un campo 'seller' que es un User con profilePhoto
listing = db.query(MarketplaceListing).first()

# Procesar foto del seller
process_nested_user_photo(listing, 'seller')

# Ahora listing.seller.profilePhoto está en base64
return listing
```

**Otros casos de uso:**
```python
# Order con buyer
order = db.query(Order).first()
process_nested_user_photo(order, 'buyer')

# Event con organizer
event = db.query(Event).first()
process_nested_user_photo(event, 'organizer')

# Ticket con user
ticket = db.query(Ticket).first()
process_nested_user_photo(ticket, 'user')
```

---

## 🎯 Ejemplos de Implementación

### Ejemplo 1: Endpoint de Perfil de Usuario

```python
@router.get("/auth/profile", response_model=UserResponse)
async def get_profile(
    current_user: User = Depends(get_current_active_user)
):
    # Procesar foto antes de retornar
    process_user_photo(current_user)
    
    return current_user
```

### Ejemplo 2: Endpoint de Lista de Usuarios (Admin)

```python
@router.get("/admin/users", response_model=List[UserResponse])
async def get_users(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_admin_user)
):
    users = db.query(User).all()
    
    # Procesar todas las fotos de una vez
    process_user_photos_list(users)
    
    return users
```

### Ejemplo 3: Endpoint de Eventos con Organizador

```python
@router.get("/events/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: UUID,
    db: Session = Depends(get_db)
):
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Procesar foto del organizador
    process_nested_user_photo(event, 'organizer')
    
    return event
```

### Ejemplo 4: Endpoint de Tickets con Usuario

```python
@router.get("/tickets/my-tickets", response_model=List[TicketResponse])
async def get_my_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    tickets = db.query(Ticket).filter(
        Ticket.user_id == current_user.id
    ).options(
        joinedload(Ticket.user)
    ).all()
    
    # Procesar fotos de usuarios en cada ticket
    for ticket in tickets:
        process_nested_user_photo(ticket, 'user')
    
    return tickets
```

### Ejemplo 5: Actualizar Perfil

```python
@router.put("/auth/profile", response_model=UserResponse)
async def update_profile(
    profile_data: UpdateProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Si se envía nueva foto en base64, convertirla a bytes para guardar
    if profile_data.profilePhoto:
        # Extraer base64 y convertir a bytes
        if profile_data.profilePhoto.startswith('data:image'):
            base64_data = profile_data.profilePhoto.split(',')[1]
            current_user.profilePhoto = base64.b64decode(base64_data)
        
    # Actualizar otros campos...
    current_user.firstName = profile_data.firstName
    current_user.lastName = profile_data.lastName
    
    db.commit()
    db.refresh(current_user)
    
    # Convertir bytes a base64 antes de retornar
    process_user_photo(current_user)
    
    return current_user
```

---

## 🔧 Aplicar a Todos los Endpoints Existentes

Si tienes muchos endpoints que devuelven usuarios, aplica esta función en cada uno:

### Buscar en tu código:
```bash
# Buscar endpoints que devuelvan User
grep -r "response_model.*User" app/api/

# Buscar queries de User
grep -r "db.query(User)" app/api/
```

### Agregar en cada endpoint:
```python
# Después de obtener el/los usuario(s)
process_user_photo(user)  # Para un solo usuario
# o
process_user_photos_list(users)  # Para lista de usuarios
```

---

## 🚀 Resultado Final

### Antes (Error):
```json
{
  "seller": {
    "profilePhoto": "b'RIFF\\xe2\\x1c\\x00\\x00WEB...'"  // ❌ Bytes
  }
}
```

### Después (Correcto):
```json
{
  "seller": {
    "profilePhoto": "data:image/webp;base64,UklGRuIcAABXRUJQ..."  // ✅ Base64
  }
}
```

---

## 📝 Notas Importantes

1. **Las funciones modifican el objeto en el lugar** - No retornan nada
2. **Son seguras** - Verifican si el campo es bytes antes de convertir
3. **Funcionan con None** - Si la foto es None, se mantiene None
4. **Funcionan con strings** - Si ya es string, no se modifica
5. **No rompen si el campo no existe** - Usan hasattr() para verificar

---

## ✅ Checklist de Implementación

- [x] Archivo `app/utils/image_utils.py` creado
- [x] Archivo `app/utils/__init__.py` creado
- [x] Endpoint `/marketplace/listings` actualizado
- [x] Endpoint `/marketplace/listings` POST actualizado
- [ ] Revisar otros endpoints que devuelvan User
- [ ] Aplicar en endpoint de perfil (`/auth/profile`)
- [ ] Aplicar en endpoint de admin users (`/admin/users`)
- [ ] Aplicar en cualquier endpoint que devuelva eventos con organizador
- [ ] Aplicar en cualquier endpoint que devuelva tickets con usuario

---

## 🐛 Troubleshooting

### Si aún ves el error de bytes:

1. Verifica que importaste la función:
   ```python
   from app.utils.image_utils import process_nested_user_photo
   ```

2. Verifica que la estás llamando ANTES del return:
   ```python
   process_nested_user_photo(listing, 'seller')
   return listing  # Debe ser DESPUÉS
   ```

3. Verifica que el objeto tiene el campo cargado:
   ```python
   .options(joinedload(MarketplaceListing.seller))  # Debe estar en el query
   ```

### Si la imagen no se muestra en el frontend:

El formato correcto debe ser:
```
data:image/webp;base64,UklGRuIcAABXRUJQ...
```

No debe ser:
```
UklGRuIcAABXRUJQ...  (falta el prefijo)
```

---

## 💡 Mejora Futura (Opcional)

Para no tener que llamar manualmente en cada endpoint, puedes crear un **middleware** o usar **@after_request** en SQLAlchemy para que se aplique automáticamente.

Pero por ahora, la solución manual es más simple y directa. 🚀
