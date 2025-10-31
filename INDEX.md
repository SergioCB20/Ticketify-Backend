# 📖 Documentación - Índice General

Bienvenido a la documentación del Backend de Ticketify. Este índice te ayudará a encontrar rápidamente lo que necesitas.

---

## 🚀 Para Empezar

### ¿Primera vez aquí?
👉 **[QUICKSTART.md](QUICKSTART.md)** - Setup en 5 minutos

### ¿Necesitas entender el proyecto?
👉 **[README.md](README.md)** - Documentación principal completa

---

## 📂 Documentación por Tema

### 🌱 Seeding y Datos de Prueba

| Documento | Descripción |
|-----------|-------------|
| **[SEEDING_README.md](SEEDING_README.md)** | Guía completa de scripts de seeding |
| **[SCRIPTS_SUMMARY.md](SCRIPTS_SUMMARY.md)** | Resumen rápido de todos los scripts |
| **[TESTING_EXAMPLES.md](TESTING_EXAMPLES.md)** | Ejemplos prácticos de testing con datos |

### 🔧 Scripts Disponibles

| Script | Propósito |
|--------|-----------|
| `seed_all.py` ⭐ | Ejecuta todo el seeding de una vez |
| `seed_initial_data.py` | Crea roles, permisos y categorías |
| `seed_events_for_testing.py` | Crea usuarios y eventos de prueba |
| `check_database.py` | Verifica estado de la base de datos |
| `clean_database.py` | Limpia datos de prueba |

### 📚 Documentación Técnica

| Documento | Descripción |
|-----------|-------------|
| **[API_SEARCH_GUIDE.md](API_SEARCH_GUIDE.md)** | Guía de filtros y búsqueda (si existe) |
| **[MODELS_COMPLETED.md](MODELS_COMPLETED.md)** | Documentación de modelos (si existe) |
| **[TESTING_GUIDE.md](TESTING_GUIDE.md)** | Guía de testing (si existe) |

---

## 🎯 Guías por Escenario

### Estoy configurando el proyecto por primera vez
1. Lee: [QUICKSTART.md](QUICKSTART.md)
2. Ejecuta: `python seed_all.py`
3. Verifica: `python check_database.py`
4. Explora: http://localhost:8000/docs

### Necesito datos de prueba
1. Lee: [SEEDING_README.md](SEEDING_README.md)
2. Ejecuta: `python seed_all.py`
3. Consulta: [TESTING_EXAMPLES.md](TESTING_EXAMPLES.md)

### Quiero entender los modelos de datos
1. Lee: [README.md](README.md) - Sección "Modelos de Base de Datos"
2. Revisa: `app/models/` - Código fuente
3. Consulta: [MODELS_COMPLETED.md](MODELS_COMPLETED.md) (si existe)

### Necesito ejemplos de búsqueda/filtros
1. Lee: [TESTING_EXAMPLES.md](TESTING_EXAMPLES.md)
2. Consulta: [API_SEARCH_GUIDE.md](API_SEARCH_GUIDE.md) (si existe)
3. Prueba: http://localhost:8000/docs

### Quiero resetear los datos
1. Ejecuta: `python clean_database.py`
2. Vuelve a poblar: `python seed_all.py`
3. Verifica: `python check_database.py`

### Necesito contribuir al proyecto
1. Lee: [README.md](README.md) - Sección "Contribución"
2. Revisa: [README.md](README.md) - Sección "Desarrollo"

---

## 🔍 Búsqueda Rápida

### Por Concepto:

#### Autenticación
- 📖 [README.md](README.md) - Sección "Autenticación"
- 👤 Credenciales de prueba: organizador1@test.com / Test123!

#### Eventos
- 🎭 [TESTING_EXAMPLES.md](TESTING_EXAMPLES.md) - Consultas de eventos
- 📊 [SCRIPTS_SUMMARY.md](SCRIPTS_SUMMARY.md) - Eventos disponibles

#### Categorías
- 📂 [SEEDING_README.md](SEEDING_README.md) - Lista de categorías
- 🔍 [TESTING_EXAMPLES.md](TESTING_EXAMPLES.md) - Búsqueda por categoría

#### Filtros y Búsqueda
- 🔎 [TESTING_EXAMPLES.md](TESTING_EXAMPLES.md) - Ejemplos completos
- 📋 [API_SEARCH_GUIDE.md](API_SEARCH_GUIDE.md) - Guía técnica (si existe)

#### Base de Datos
- 🗄️ [README.md](README.md) - Sección "Base de Datos"
- 🛠️ Comandos Alembic en [README.md](README.md)

#### Scripts
- 📜 [SCRIPTS_SUMMARY.md](SCRIPTS_SUMMARY.md) - Todos los scripts
- 🌱 [SEEDING_README.md](SEEDING_README.md) - Guía detallada

---

## 📊 Datos Disponibles (Quick Reference)

### Credenciales:
```
organizador1@test.com / Test123!
organizador2@test.com / Test123!
organizador3@test.com / Test123!
```

### Categorías (10):
🎨 Arte & Cultura | 🤝 Ayuda Social | 🎬 Cine | 🍽️ Comidas & Bebidas | 🎵 Conciertos | 📚 Cursos | ⚽ Deportes | ❤️ Donación | 🎪 Entretenimiento | 🎉 Festivales

### Eventos: 18+
Optimizados para testing de filtros por:
- Categoría (todas las 10)
- Precio (Gratis hasta S/ 3,500)
- Fecha (Pasados, próximos días/semanas/meses)
- Ubicación (Lima, Miraflores, Barranco, San Isidro, etc.)
- Capacidad (25 hasta 50,000)

---

## 🆘 Ayuda y Soporte

### Problemas Comunes:
- 🐛 [QUICKSTART.md](QUICKSTART.md) - Sección "Problemas Comunes"
- 🔧 [SEEDING_README.md](SEEDING_README.md) - Sección "Solución de Problemas"

### Comandos Útiles:
```bash
# Ver estado de datos
python check_database.py

# Resetear datos
python clean_database.py

# Poblar datos
python seed_all.py

# Iniciar servidor
uvicorn app.main:app --reload

# Ver migraciones
alembic history

# Aplicar migraciones
alembic upgrade head
```

---

## 🔗 Enlaces Rápidos

### Documentación Local:
- 📖 [README Principal](README.md)
- 🚀 [Quick Start](QUICKSTART.md)
- 🌱 [Guía Seeding](SEEDING_README.md)
- 🧪 [Ejemplos Testing](TESTING_EXAMPLES.md)
- 📋 [Resumen Scripts](SCRIPTS_SUMMARY.md)

### API (cuando el servidor esté corriendo):
- 📚 [Swagger UI](http://localhost:8000/docs)
- 📄 [ReDoc](http://localhost:8000/redoc)

### Repositorio:
- Frontend: `C:\Users\gonza\Ingesoft\Ticketify-Frontend`
- Backend: `C:\Users\gonza\Ingesoft\Ticketify-Backend`

---

## 📝 Mapa del Proyecto

```
Ticketify-Backend/
│
├── 📖 Documentación
│   ├── README.md                    ⭐ Inicio aquí
│   ├── QUICKSTART.md                🚀 Setup rápido
│   ├── SEEDING_README.md            🌱 Guía de datos
│   ├── SCRIPTS_SUMMARY.md           📋 Resumen scripts
│   ├── TESTING_EXAMPLES.md          🧪 Ejemplos testing
│   └── INDEX.md                     📖 Este archivo
│
├── 🔧 Scripts
│   ├── seed_all.py                  ⭐ Script maestro
│   ├── seed_initial_data.py         📋 Datos base
│   ├── seed_events_for_testing.py   🎭 Eventos prueba
│   ├── check_database.py            🔍 Verificador
│   └── clean_database.py            🧹 Limpiador
│
├── 📦 Aplicación
│   └── app/
│       ├── api/                     🌐 Endpoints
│       ├── models/                  🗄️ Modelos
│       ├── schemas/                 ✅ Validaciones
│       ├── services/                ⚙️ Lógica negocio
│       ├── repositories/            📊 Acceso datos
│       └── core/                    🔧 Configuración
│
└── 🗃️ Configuración
    ├── .env                         🔐 Variables entorno
    ├── alembic.ini                  🗄️ Config migraciones
    └── requirements.txt             📦 Dependencias
```

---

## 💡 Tips de Navegación

1. **Nuevo en el proyecto**: Empieza por [QUICKSTART.md](QUICKSTART.md)
2. **Necesitas referencia**: Usa [README.md](README.md)
3. **Testing específico**: Consulta [TESTING_EXAMPLES.md](TESTING_EXAMPLES.md)
4. **Problema con scripts**: Revisa [SEEDING_README.md](SEEDING_README.md)
5. **Resumen rápido**: Lee [SCRIPTS_SUMMARY.md](SCRIPTS_SUMMARY.md)

---

## 🎯 Objetivos por Rol

### Desarrollador Frontend
- [ ] Leer [QUICKSTART.md](QUICKSTART.md)
- [ ] Ejecutar `seed_all.py`
- [ ] Explorar http://localhost:8000/docs
- [ ] Revisar [TESTING_EXAMPLES.md](TESTING_EXAMPLES.md) para endpoints

### Desarrollador Backend
- [ ] Leer [README.md](README.md) completo
- [ ] Entender estructura en `app/`
- [ ] Revisar modelos en `app/models/`
- [ ] Familiarizarse con [SEEDING_README.md](SEEDING_README.md)

### QA/Tester
- [ ] Leer [TESTING_EXAMPLES.md](TESTING_EXAMPLES.md)
- [ ] Ejecutar `seed_all.py`
- [ ] Usar credenciales de prueba
- [ ] Probar casos de [TESTING_EXAMPLES.md](TESTING_EXAMPLES.md)

### DevOps
- [ ] Revisar [README.md](README.md) sección Deploy
- [ ] Configurar variables de entorno
- [ ] Entender migraciones Alembic
- [ ] Verificar scripts de inicialización

---

**✨ ¡Esperamos que esta documentación te sea útil!**

Si encuentras algo que falta o está confuso, no dudes en mejorar la documentación.
