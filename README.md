# Backend de Ticketify

API REST para el sistema de gestión de tickets y eventos construido con FastAPI, PostgreSQL y SQLAlchemy.

## 🚀 Tecnologías

- **FastAPI** - Framework web moderno y rápido para APIs
- **PostgreSQL** - Base de datos relacional
- **SQLAlchemy** - ORM para Python
- **Alembic** - Migraciones de base de datos
- **Pydantic** - Validación de datos
- **JWT** - Autenticación con tokens
- **bcrypt** - Hashing de contraseñas
- **MercadoPago** - Procesamiento de pagos
- **Redis** - Cache y tareas en background
- **Celery** - Procesamiento asíncrono

## 📁 Estructura del Proyecto

```
app/
├── api/                    # Endpoints de la API
│   ├── auth.py            # Rutas de autenticación
│   └── __init__.py        # Router principal
├── core/                   # Configuración central
│   ├── config.py          # Configuración de la aplicación
│   ├── database.py        # Configuración de base de datos
│   └── dependencies.py    # Dependencias de FastAPI
├── models/                 # Modelos de SQLAlchemy
│   ├── user.py            # Modelo de usuarios
│   ├── event.py           # Modelo de eventos
│   ├── ticket.py          # Modelo de tickets
│   ├── purchase.py        # Modelo de compras
│   └── ...                # Otros modelos
├── repositories/           # Capa de acceso a datos
│   ├── user_repository.py # Repositorio de usuarios
│   └── __init__.py
├── schemas/               # Esquemas Pydantic
│   ├── auth.py           # Esquemas de autenticación
│   └── __init__.py
├── services/              # Lógica de negocio
│   ├── auth_service.py   # Servicio de autenticación
│   └── __init__.py
├── utils/                 # Utilidades
│   ├── security.py       # Utilidades de seguridad
│   └── __init__.py
└── main.py               # Punto de entrada
```

## 🏗️ Modelos de Base de Datos

### Entidades Principales (según diagrama de clases):

1. **User** - Usuarios del sistema (Admin, Organizer, Customer)
2. **Event** - Eventos organizados
3. **EventCategory** - Categorías de eventos
4. **TicketType** - Tipos de tickets por evento
5. **Purchase** - Compras realizadas
6. **Ticket** - Tickets individuales
7. **Promotion** - Promociones y descuentos
8. **Notification** - Notificaciones del sistema
9. **Verification** - Verificaciones (email, teléfono, etc.)
10. **MarketplaceListing** - Listados del marketplace de reventa

### Relaciones:
- Un Usuario puede tener múltiples Eventos (organizer)
- Un Evento puede tener múltiples TicketTypes
- Una Compra genera múltiples Tickets
- Los Tickets pueden listarse en el Marketplace

## 🛠️ Configuración Inicial

### 1. Requisitos previos
- Python 3.11+
- PostgreSQL 14+
- Redis (opcional, para cache)

### 2. Instalación

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configuración de la base de datos

```bash
# Crear base de datos en PostgreSQL
psql -U postgres
CREATE DATABASE ticketify_db;
CREATE USER ticketify_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE ticketify_db TO ticketify_user;
\q
```

### 4. Variables de entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar variables según tu configuración
nano .env
```

### 5. Ejecutar migraciones

```bash
# Inicializar Alembic (solo primera vez)
alembic init alembic

# Crear migración inicial
python init_db.py

# O manualmente:
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 6. Ejecutar servidor

```bash
# Desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# O usando el script
python app/main.py
```

## 🔐 Autenticación

### Endpoints disponibles:

```
POST /api/auth/register      # Registro de usuarios
POST /api/auth/login         # Login
POST /api/auth/refresh       # Refresh token
POST /api/auth/logout        # Logout
GET  /api/auth/profile       # Obtener perfil
PUT  /api/auth/profile       # Actualizar perfil
POST /api/auth/change-password    # Cambiar contraseña
POST /api/auth/forgot-password    # Solicitar reset
POST /api/auth/reset-password     # Reset contraseña
POST /api/auth/verify-email       # Verificar email
DELETE /api/auth/account          # Eliminar cuenta
```

### Flujo de autenticación:

1. **Registro**: `POST /api/auth/register`
2. **Login**: `POST /api/auth/login` → Retorna JWT tokens
3. **Acceso protegido**: Incluir `Authorization: Bearer <token>` en headers
4. **Refresh**: `POST /api/auth/refresh` cuando el token expire

### Roles de usuario:
- **ADMIN**: Acceso completo al sistema
- **ORGANIZER**: Puede crear y gestionar eventos
- **CUSTOMER**: Puede comprar y revender tickets

## 📊 Base de Datos

### Comandos Alembic útiles:

```bash
# Crear nueva migración
alembic revision --autogenerate -m "Descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Ver historial
alembic history

# Rollback
alembic downgrade -1
```

## 🔧 Desarrollo

### Estructura de un nuevo endpoint:

1. **Modelo**: Definir en `models/`
2. **Schema**: Validaciones en `schemas/`
3. **Repository**: Acceso a datos en `repositories/`
4. **Service**: Lógica de negocio en `services/`
5. **API**: Endpoint en `api/`

### Ejemplo de endpoint protegido:

```python
@router.get("/protected")
async def protected_endpoint(
    current_user: User = Depends(get_current_active_user)
):
    return {"message": f"Hola {current_user.first_name}!"}
```

### Ejemplo con roles:

```python
@router.get("/admin-only")
async def admin_only(
    current_user: User = Depends(get_admin_user)
):
    return {"message": "Solo administradores"}
```

## 🧪 Testing

```bash
# Instalar dependencias de testing
pip install pytest pytest-asyncio httpx

# Ejecutar tests
pytest

# Con coverage
pytest --cov=app
```

## 📝 API Documentation

Una vez que el servidor esté corriendo:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔄 Próximos Pasos

- [ ] Endpoints de eventos (CRUD)
- [ ] Sistema de compras y pagos
- [ ] Marketplace de reventa
- [ ] Sistema de notificaciones
- [ ] WebSockets para actualizaciones en tiempo real
- [ ] Sistema de archivos para imágenes
- [ ] Tests unitarios y de integración
- [ ] Documentación de API con OpenAPI
- [ ] Deploy con Docker

## 🚀 Deploy

### Con Docker:

```bash
# Crear imagen
docker build -t ticketify-backend .

# Ejecutar contenedor
docker run -p 8000:8000 ticketify-backend
```

### Variables de entorno para producción:

```env
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql://user:pass@prod-db:5432/ticketify
SECRET_KEY=super-secure-production-key
```

## 🤝 Contribución

1. Fork del repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto es parte del curso de Ingeniería de Software - 2025-2

---

**Estado actual**: ✅ Autenticación completa y modelos base implementados
