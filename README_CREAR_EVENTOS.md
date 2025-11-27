# 🎉 Scripts de Creación de Eventos - Ticketify

Scripts para crear eventos de prueba en la base de datos de Ticketify para testing y desarrollo.

## 📋 Descripción

Estos scripts te permiten crear eventos completos con tipos de tickets directamente en la base de datos, asignándolos a usuarios organizadores específicos. Son útiles para:

- Pruebas de desarrollo
- Demos y presentaciones
- Población inicial de datos
- Testing del flujo de eventos

## 📦 Scripts Disponibles

### 0. `verificar_sistema_eventos.py` (Verificación)

**EJECUTA ESTE PRIMERO** antes de crear eventos.

Script de diagnóstico que verifica:
- ✅ Conexión a base de datos
- ✅ Existencia de roles (especialmente ORGANIZER)
- ✅ Usuarios registrados y activos
- ✅ Usuarios con rol de organizador
- ✅ Categorías de eventos disponibles
- ℹ️ Eventos existentes y sus estados

#### Uso:
```bash
python verificar_sistema_eventos.py
```

#### Salida Ejemplo:
```
🔍 VERIFICACIÓN DEL SISTEMA - TICKETIFY

1️⃣  Verificando conexión a base de datos...
   ✅ Conexión exitosa

2️⃣  Verificando roles en la base de datos...
   ✅ 2 roles encontrados
      • ATTENDEE
      • ORGANIZER

3️⃣  Verificando usuarios...
   ✅ 5 usuarios encontrados
      • 5 usuarios activos

4️⃣  Verificando usuarios organizadores...
   ✅ 2 organizadores encontrados:
      • org@test.com - Juan Pérez
        ID: 123e4567...
        Activo: Sí
        Eventos creados: 3

5️⃣  Verificando categorías de eventos...
   ✅ 8 categorías encontradas
      • 8 categorías activas

✅ ¡TODO ESTÁ LISTO!
```

---

### 1. `crear_evento_organizador.py` (Interactivo/Completo)

Script principal con dos modos de operación:

**Modo Interactivo:**
- Selecciona el organizador de una lista
- Personaliza todos los detalles del evento
- Crea tipos de tickets personalizados
- Control total sobre el evento

**Modo Rápido:**
- Crea un evento con valores predefinidos
- Usa el primer organizador disponible
- 3 tipos de tickets automáticos (General, VIP, Platea)
- Ideal para pruebas rápidas

#### Uso:
```bash
# Desde la carpeta Ticketify-Backend
python crear_evento_organizador.py
```

#### Ejemplo de Ejecución:
```
🎉 CREADOR DE EVENTOS - TICKETIFY
============================================================

Modos disponibles:
1. Creación interactiva (personalizada)
2. Creación rápida (valores predefinidos)
3. Salir

Selecciona una opción (1-3): 1

=== USUARIOS ORGANIZADORES ===
1. organizador@example.com - Juan Pérez
   ID: 123e4567-e89b-12d3-a456-426614174000
   Activo: Sí
   Eventos creados: 2

📝 Selecciona el organizador (1-1): 1
✅ Organizador seleccionado: Juan Pérez

============================================================
📋 INFORMACIÓN DEL EVENTO
============================================================

📌 Título del evento: Concierto Rock 2025
📝 Descripción: Las mejores bandas en un solo lugar
📍 Lugar (ej: Estadio Nacional, Lima): Estadio Nacional
¿En cuántos días será el evento? (default: 30): 15
¿Cuántas horas durará? (default: 4): 3
   Inicio: 2025-12-11 17:00
   Fin: 2025-12-11 20:00

👥 Capacidad total del evento (default: 1000): 800

🏷️  Selecciona una categoría (1-5, o Enter para omitir): 1
✅ Categoría: Conciertos

============================================================
🎬 CREANDO EVENTO...
============================================================
✅ Evento 'Concierto Rock 2025' creado con ID: abc12345...

============================================================
🎫 TIPOS DE TICKETS
============================================================

¿Deseas crear tipos de tickets ahora? (s/N): s
¿Cuántos tipos de tickets? (default: 3): 3

--- Tipo de Ticket #1 ---
Nombre (default: General): 
Precio en soles (default: 50.0): 
Cantidad disponible (default: 480): 
Descripción (opcional): Entrada general
✅ Tipo de ticket 'General' creado (S/ 50.0, 480 disponibles)

...
```

### 2. `crear_evento_simple.py` (Por Email)

Script simplificado que crea un evento rápido para un organizador específico por email.

#### Uso:
```bash
# Desde la carpeta Ticketify-Backend
python crear_evento_simple.py email@organizador.com
```

#### Ejemplo:
```bash
python crear_evento_simple.py organizador@ticketify.com
```

#### Salida:
```
📋 Creando evento para: Juan Pérez (organizador@ticketify.com)
✅ Evento creado: Evento de Prueba 20251126_143022
   ID: def45678-e89b-12d3-a456-426614174000
   Fecha: 2025-12-11 14:30

🎫 Creando tipos de tickets...
   ✓ General: S/ 40.00 (300 disponibles)
   ✓ Preferencial: S/ 80.00 (150 disponibles)
   ✓ VIP: S/ 120.00 (50 disponibles)

============================================================
✨ EVENTO CREADO EXITOSAMENTE
============================================================
Organizador: Juan Pérez
Email: organizador@ticketify.com
Evento ID: def45678-e89b-12d3-a456-426614174000
Título: Evento de Prueba 20251126_143022
Estado: PUBLISHED
Tipos de tickets: 3
============================================================
```

## 🎯 Características de los Eventos Creados

### Evento:
- ✅ **Título personalizable** (o automático con timestamp)
- ✅ **Descripción** opcional
- ✅ **Fechas** configurables (default: +30 días, 4 horas de duración)
- ✅ **Lugar** personalizable
- ✅ **Capacidad total** configurable
- ✅ **Estado** PUBLISHED por defecto (listo para vender)
- ✅ **Categoría** asignable (si existen en la BD)

### Tipos de Tickets:
- ✅ **Múltiples tipos** (General, VIP, Platea, etc.)
- ✅ **Precios configurables**
- ✅ **Cantidades disponibles**
- ✅ **Límites de compra** (min: 1, max: 8-10)
- ✅ **Estado activo** por defecto

## 📝 Requisitos Previos

1. **Base de datos configurada:**
   ```bash
   # El backend debe estar configurado con PostgreSQL
   # Verificar .env tiene DATABASE_URL correcto
   ```

2. **Usuario organizador existente:**
   - Debe existir al menos un usuario con rol `ORGANIZER` en la base de datos
   - Si no existe, el script puede agregarlo automáticamente

3. **Dependencias instaladas:**
   ```bash
   cd Ticketify-Backend
   pip install -r requirements.txt
   ```

## 🔧 Verificar Usuarios Organizadores

Para ver qué usuarios tienen rol de organizador:

```python
# Desde Python o psql
from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.models.role import Role

db = SessionLocal()
organizer_role = db.query(Role).filter(Role.name == UserRole.ORGANIZER).first()
organizers = db.query(User).join(User.roles).filter(Role.name == UserRole.ORGANIZER).all()

for org in organizers:
    print(f"{org.email} - {org.firstName} {org.lastName}")
```

## 🚨 Solución de Problemas

### Error: "No hay usuarios organizadores"
**Solución:** Crea un usuario organizador desde la app o agrega el rol manualmente:
```python
from app.models.user import User
from app.models.role import Role

user = db.query(User).filter(User.email == "tu@email.com").first()
organizer_role = db.query(Role).filter(Role.name == "ORGANIZER").first()
user.roles.append(organizer_role)
db.commit()
```

### Error: "No existe el rol ORGANIZER"
**Solución:** Ejecuta las migraciones de Alembic:
```bash
cd Ticketify-Backend
alembic upgrade head
```

### Error de conexión a la base de datos
**Solución:** Verifica tu archivo `.env`:
```env
DATABASE_URL=postgresql://usuario:password@localhost:5432/ticketify
```

## 📊 Estructura del Evento Creado

```
Evento
├── ID (UUID)
├── Título
├── Descripción
├── Organizador (User con rol ORGANIZER)
├── Fechas (inicio/fin)
├── Lugar (venue)
├── Capacidad total
├── Estado (PUBLISHED)
├── Categoría (opcional)
└── Tipos de Tickets
    ├── General (60% capacidad)
    ├── VIP (30% capacidad)
    └── Platea (10% capacidad)
```

## 💡 Tips de Uso

1. **Para desarrollo:** Usa el modo rápido para crear eventos test rápidamente
2. **Para demos:** Usa el modo interactivo para crear eventos con datos realistas
3. **Para múltiples eventos:** Ejecuta el script simple varias veces con el mismo email
4. **Para limpieza:** Los eventos se pueden eliminar desde la interfaz del organizador o directamente en la BD

## 🔗 Relacionado

- `verificar_sistema_eventos.py` - **¡Ejecuta primero!** Verifica que todo esté listo
- `crear_ticket_prueba.py` - Script para crear tickets de prueba para usuarios
- `seed_categories.py` - Script para poblar categorías de eventos
- `check_user_roles.py` - Script para verificar roles de usuarios

## 📚 Documentación Adicional

Para más información sobre el modelo de datos:
- Ver `app/models/event.py` - Modelo de Event
- Ver `app/models/ticket_type.py` - Modelo de TicketType
- Ver `app/models/user.py` - Modelo de User y roles

---

**Autor:** Sistema Ticketify  
**Fecha:** Noviembre 2025  
**Versión:** 1.0
