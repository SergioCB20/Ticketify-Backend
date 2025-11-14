# 🗄️ Configuración de Base de Datos - Ticketify

## 📋 Descripción del Problema Resuelto

El error que estabas experimentando:
```
psycopg2.errors.UndefinedColumn: no existe la columna users_1.profilePhotoMimeType
```

**Causa**: El modelo `User` en SQLAlchemy tiene campos que no existen en la base de datos PostgreSQL. Esto sucede cuando:
- Se actualizan los modelos Python pero no se ejecutan las migraciones
- La base de datos está desincronizada con el código

**Solución**: Resetear y recrear la base de datos con la estructura actualizada.

---

## 🚀 Pasos para Configurar la Base de Datos

### 1️⃣ Resetear la Base de Datos

Este comando eliminará TODAS las tablas y las recreará con la estructura actualizada:

```bash
python -m app.seeds.reset_database
```

**⚠️ ADVERTENCIA**: Esto eliminará todos los datos existentes. Solo úsalo en desarrollo.

**Qué hace:**
- Elimina todas las tablas existentes
- Recrea todas las tablas según los modelos actualizados
- Sincroniza la estructura de la base de datos con los modelos Python
- Verifica que las tablas se crearon correctamente

### 2️⃣ Poblar con Datos de Prueba

Después de resetear, ejecuta el seeder para agregar datos de prueba:

```bash
python -m app.seeds.seed_data
```

**Qué crea:**
- 5 categorías de eventos (Conciertos, Deportes, Teatro, Conferencias, Festivales)
- 3 usuarios de prueba
- 6 eventos de ejemplo
- Tipos de tickets para cada evento

### 3️⃣ Iniciar el Servidor

```bash
python run.py
```

Accede a la documentación de la API:
- 📚 Swagger UI: http://localhost:8000/docs
- 📖 ReDoc: http://localhost:8000/redoc

---

## 👥 Credenciales de Prueba

### Administrador
- **Email**: admin@ticketify.com
- **Password**: admin123
- **Nombre**: Admin Ticketify

### Organizador
- **Email**: organizador@ticketify.com
- **Password**: org123
- **Nombre**: Carlos Promotor

### Usuario Regular
- **Email**: usuario@ticketify.com
- **Password**: user123
- **Nombre**: María González

---

## 🔧 Cambios Implementados en los Scripts

### `reset_database.py`
✅ Inspección de la base de datos antes de resetear
✅ Muestra el número de tablas que se eliminarán
✅ Verifica las tablas creadas después del reset
✅ Muestra las tablas principales creadas
✅ Proporciona instrucciones claras de los siguientes pasos

### `seed_data.py`
✅ Importa enums necesarios (`DocumentType`, `Gender`)
✅ Agrega campos completos para usuarios (documentType, country, city, gender)
✅ Inicializa correctamente `profilePhoto` y `profilePhotoMimeType` como NULL
✅ Maneja campos opcionales con `.get()`
✅ Previene duplicados verificando si ya existen registros

### `user.py` (Modelo)
✅ Eliminó el campo duplicado `documentId`
✅ Mantiene todos los campos de MercadoPago
✅ Incluye `profilePhotoMimeType` para almacenar el tipo MIME de las fotos

---

## 📊 Estructura de la Base de Datos

### Tablas Principales Creadas

| Tabla | Descripción |
|-------|-------------|
| `users` | Usuarios del sistema (con todos los campos actualizados) |
| `events` | Eventos publicados |
| `event_categories` | Categorías de eventos |
| `tickets` | Tickets comprados |
| `ticket_types` | Tipos de tickets por evento |
| `marketplace_listings` | Listados del marketplace |
| `payments` | Pagos procesados |
| `purchases` | Compras realizadas |
| `notifications` | Notificaciones del sistema |

---

## 🔍 Verificación

Después de ejecutar los scripts, puedes verificar que todo funciona:

1. **Verificar conexión a la base de datos**:
   ```bash
   python -c "from app.core.database import engine; print(engine.url)"
   ```

2. **Verificar tablas creadas**:
   ```bash
   python -c "from app.core.database import engine; from sqlalchemy import inspect; print(inspect(engine).get_table_names())"
   ```

3. **Verificar usuarios creados**:
   - Inicia el servidor: `python run.py`
   - Ve a: http://localhost:8000/docs
   - Prueba el endpoint: `POST /api/auth/login` con cualquiera de las credenciales de prueba

---

## 🐛 Solución de Problemas

### Error: "no existe la columna..."
**Solución**: Ejecuta `python -m app.seeds.reset_database` para recrear las tablas

### Error: "duplicate key value violates unique constraint"
**Solución**: Ya existen datos. Ejecuta reset_database primero

### Error: "could not connect to server"
**Solución**: Verifica que PostgreSQL esté corriendo y las credenciales en `.env` sean correctas

### Los datos no se muestran
**Solución**: 
1. Verifica que el servidor esté corriendo
2. Ejecuta `seed_data.py` si no hay datos
3. Revisa los logs del servidor en la consola

---

## 📝 Notas Importantes

1. **Solo para Desarrollo**: Estos scripts son para desarrollo. En producción usa migraciones con Alembic.

2. **Backup**: Si tienes datos importantes, haz un backup antes de ejecutar `reset_database.py`.

3. **Sincronización**: Cada vez que modifiques los modelos, ejecuta reset_database para sincronizar.

4. **Campos Nuevos**: El modelo User ahora incluye:
   - `profilePhotoMimeType`: Tipo MIME de la foto de perfil
   - `documentType`: Tipo de documento (DNI, CE, Pasaporte)
   - `country`: País del usuario
   - `city`: Ciudad del usuario
   - `gender`: Género del usuario
   - Campos de integración con MercadoPago

---

## 🎯 Resumen Rápido

```bash
# 1. Resetear la base de datos
python -m app.seeds.reset_database
# Escribe: SI

# 2. Poblar con datos de prueba
python -m app.seeds.seed_data

# 3. Iniciar el servidor
python run.py

# 4. ¡Listo! Accede a http://localhost:8000/docs
```

---

¿Necesitas ayuda? Revisa los logs en la consola o contacta al equipo de desarrollo.
