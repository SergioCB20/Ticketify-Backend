# 🚀 Quick Start Guide - Ticketify Backend

Guía rápida para levantar el backend con datos de prueba en menos de 5 minutos.

---

## ⚡ Setup Rápido (5 minutos)

### 1️⃣ Clonar y Configurar (1 min)

```bash
# Navegar al directorio del backend
cd C:\Users\gonza\Ingesoft\Ticketify-Backend

# Activar entorno virtual
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Instalar dependencias (si no están instaladas)
pip install -r requirements.txt
```

---

### 2️⃣ Configurar Base de Datos (1 min)

```bash
# Crear base de datos en PostgreSQL
psql -U postgres
```

En PostgreSQL:
```sql
CREATE DATABASE ticketify_db;
CREATE USER ticketify_user WITH PASSWORD 'ticketify123';
GRANT ALL PRIVILEGES ON DATABASE ticketify_db TO ticketify_user;
\q
```

---

### 3️⃣ Configurar Variables de Entorno (30 seg)

Edita tu `.env`:
```env
DATABASE_URL=postgresql://ticketify_user:ticketify123@localhost:5432/ticketify_db
SECRET_KEY=tu-clave-secreta-super-segura-aqui
```

---

### 4️⃣ Ejecutar Migraciones (30 seg)

```bash
# Aplicar migraciones
alembic upgrade head
```

---

### 5️⃣ Poblar con Datos de Prueba (1 min)

```bash
# Ejecutar script maestro
python seed_all.py
```

**✅ Esto creará**:
- 4 Roles y 8 Permisos
- 10 Categorías de eventos
- 3 Usuarios organizadores
- 18+ Eventos variados
- Múltiples tipos de tickets

---

### 6️⃣ Iniciar Servidor (10 seg)

```bash
# Iniciar en modo desarrollo
uvicorn app.main:app --reload
```

🎉 **¡Listo!** Tu servidor está corriendo en: http://localhost:8000

---

## 📝 Verificación Rápida

### Ver documentación API:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Verificar datos:
```bash
python check_database.py
```

### Hacer login:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "organizador1@test.com",
    "password": "Test123!"
  }'
```

---

## 🔐 Credenciales de Prueba

```
Email: organizador1@test.com
Email: organizador2@test.com
Email: organizador3@test.com
Password: Test123!
```

---

## 📊 Datos Disponibles

- ✅ **10 Categorías**: Conciertos, Deportes, Arte, Festivales, etc.
- ✅ **18+ Eventos**: Variados por categoría, precio y fecha
- ✅ **Múltiples Tickets**: Diferentes tipos por evento
- ✅ **Optimizado para Testing**: Filtros, búsqueda, paginación

---

## 🧪 Probar Búsquedas

### Buscar todos los eventos:
```
GET http://localhost:8000/api/events
```

### Buscar conciertos:
```
GET http://localhost:8000/api/events?category=conciertos
```

### Buscar eventos gratuitos:
```
GET http://localhost:8000/api/events?minPrice=0&maxPrice=0
```

### Buscar en Miraflores:
```
GET http://localhost:8000/api/events?location=Miraflores
```

Ver más ejemplos en: [TESTING_EXAMPLES.md](TESTING_EXAMPLES.md)

---

## 🔄 Reset de Datos

Si necesitas empezar de nuevo:

```bash
# 1. Limpiar datos
python clean_database.py

# 2. Volver a poblar
python seed_all.py

# 3. Verificar
python check_database.py
```

---

## 📚 Documentación Completa

- [README.md](README.md) - Documentación principal
- [SEEDING_README.md](SEEDING_README.md) - Guía de seeding
- [TESTING_EXAMPLES.md](TESTING_EXAMPLES.md) - Ejemplos de testing
- [SCRIPTS_SUMMARY.md](SCRIPTS_SUMMARY.md) - Resumen de scripts

---

## 🐛 Problemas Comunes

### Error: "No module named 'app'"
```bash
# Asegúrate de estar en el directorio raíz
cd C:\Users\gonza\Ingesoft\Ticketify-Backend
python seed_all.py
```

### Error: "Could not connect to database"
```bash
# Verifica que PostgreSQL esté corriendo
# Revisa tu DATABASE_URL en .env
```

### Error: "Alembic not initialized"
```bash
# Inicializar Alembic
alembic init alembic
```

---

## 🎯 Siguiente Paso

Ya tienes todo configurado! Ahora puedes:

1. **Explorar la API**: http://localhost:8000/docs
2. **Hacer login**: Usar organizador1@test.com / Test123!
3. **Probar búsquedas**: Ver [TESTING_EXAMPLES.md](TESTING_EXAMPLES.md)
4. **Conectar Frontend**: El backend está listo para recibir peticiones

---

## 💡 Tips

- Usa **Postman** o **Thunder Client** para probar endpoints
- El token JWT expira en 24 horas (configurable)
- Los datos son persistentes (no se borran al reiniciar)
- Puedes regenerar datos cuando quieras con `seed_all.py`

---

**✨ ¡Happy Coding!**

Si tienes problemas, revisa la documentación completa en los archivos mencionados.
