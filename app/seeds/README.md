# 🌱 Scripts de Base de Datos - Ticketify

Esta carpeta contiene scripts para gestionar la base de datos durante el desarrollo.

## 📜 Scripts Disponibles

### 1. `reset_database.py` - Resetear Base de Datos

**¿Cuándo usar?**
- Cuando los modelos cambian y necesitas sincronizar la BD
- Cuando aparecen errores de "columna no existe"
- Al iniciar un nuevo ambiente de desarrollo
- Cuando la estructura de la BD está corrupta

**Comando:**
```bash
python -m app.seeds.reset_database
```

**⚠️ ADVERTENCIA**: Elimina todos los datos. Solo para desarrollo.

**Qué hace:**
1. Inspecciona las tablas actuales
2. Elimina todas las tablas existentes
3. Recrea las tablas según los modelos actualizados
4. Verifica que se crearon correctamente
5. Muestra un resumen de las tablas creadas

---

### 2. `seed_data.py` - Poblar con Datos de Prueba

**¿Cuándo usar?**
- Después de resetear la base de datos
- Para testing y desarrollo
- Para tener datos de ejemplo consistentes

**Comando:**
```bash
python -m app.seeds.seed_data
```

**Qué crea:**

#### Categorías de Eventos (5)
- 🎵 Conciertos
- ⚽ Deportes  
- 🎭 Teatro
- 💼 Conferencias
- 🎪 Festivales

#### Usuarios de Prueba (3)
1. **Admin** - admin@ticketify.com / admin123
2. **Organizador** - organizador@ticketify.com / org123
3. **Usuario** - usuario@ticketify.com / user123

#### Eventos de Ejemplo (6)
- Concierto de Rock en Vivo (30 días)
- Partido de Fútbol: Clásico Peruano (15 días)
- Festival Gastronómico Mistura (45 días)
- Obra de Teatro: El Avaro (20 días)
- Tech Summit Lima 2025 (60 días)
- Concierto de Salsa: Los Grandes (10 días)

#### Tipos de Tickets
- Automáticamente genera tipos de tickets según capacidad del evento
- General, VIP, Platinum, Preferencial según corresponda

**Características:**
- ✅ Previene duplicados (verifica antes de crear)
- ✅ Muestra qué se creó y qué ya existía
- ✅ Maneja errores graciosamente
- ✅ Datos realistas con fechas futuras

---

### 3. `verify_database.py` - Verificar Sincronización

**¿Cuándo usar?**
- Para diagnosticar problemas de sincronización
- Antes de hacer un deploy
- Para verificar que reset_database funcionó
- Cuando sospechas que hay columnas faltantes

**Comando:**
```bash
python -m app.seeds.verify_database
```

**Qué verifica:**

1. **Tablas**
   - Compara tablas en modelos vs BD
   - Identifica tablas faltantes o extra

2. **Columnas**
   - Verifica columnas de tablas importantes (users, events, tickets, marketplace_listings)
   - Detecta columnas faltantes en BD
   - Detecta columnas extra en BD

3. **Campo Específico**
   - Verifica que `profilePhotoMimeType` existe en la tabla `users`
   - Este es el campo que causaba el error original

**Salida:**
- ✅ Si todo está bien: "BASE DE DATOS CORRECTAMENTE SINCRONIZADA"
- ⚠️ Si hay problemas: Lista detallada de diferencias + solución recomendada

---

## 🚀 Flujo de Trabajo Típico

### Configuración Inicial
```bash
# 1. Resetear base de datos
python -m app.seeds.reset_database
# Responde: SI

# 2. Poblar con datos
python -m app.seeds.seed_data

# 3. Verificar (opcional)
python -m app.seeds.verify_database

# 4. Iniciar servidor
python run.py
```

### Después de Cambios en Modelos
```bash
# 1. Verificar qué cambió
python -m app.seeds.verify_database

# 2. Si hay diferencias, resetear
python -m app.seeds.reset_database

# 3. Repoblar datos
python -m app.seeds.seed_data
```

### Solución de Problemas
```bash
# Si algo falla o ves errores de columnas:
python -m app.seeds.reset_database
python -m app.seeds.seed_data
python run.py
```

---

## 🛠️ Detalles Técnicos

### Modelos Incluidos

Los scripts trabajan con todos los modelos definidos en `app/models/`:

**Core:**
- `User` (usuarios)
- `Role` (roles)
- `Permission` (permisos)

**Eventos:**
- `Event` (eventos)
- `EventCategory` (categorías)
- `EventSchedule` (horarios)

**Tickets:**
- `Ticket` (tickets)
- `TicketType` (tipos de tickets)
- `TicketTransfer` (transferencias)

**Pagos:**
- `Payment` (pagos)
- `Transaction` (transacciones)
- `Purchase` (compras)
- `Promotion` (promociones)

**Marketplace:**
- `MarketplaceListing` (listados)

**Validación:**
- `Validation` (validaciones)
- `QRValidationLog` (logs de QR)

**Soporte:**
- `Dispute` (disputas)
- `SupportTicket` (tickets de soporte)

**Otros:**
- `Notification` (notificaciones)
- `Analytics` (analíticas)
- `Report` (reportes)
- `AuditLog` (logs de auditoría)

### Campos Importantes del Usuario

El modelo `User` ahora incluye:

```python
# Información básica
email, password, firstName, lastName, phoneNumber

# Documento
documentType, documentId  # DNI, CE, Pasaporte

# Ubicación
country, city

# Personal
gender, profilePhoto, profilePhotoMimeType  # ← Este campo causaba el error

# MercadoPago OAuth
mercadopagoUserId, mercadopagoPublicKey
mercadopagoAccessToken, mercadopagoRefreshToken
mercadopagoTokenExpires, isMercadopagoConnected
mercadopagoConnectedAt, mercadopagoEmail

# Estado
isActive, createdAt, lastLogin
```

---

## 📊 Estructura de Datos Generada

### Usuarios
Cada usuario tiene:
- Información completa (nombre, email, teléfono)
- Documento (tipo y número)
- Ubicación (Perú, Lima)
- Género
- Password hasheado con bcrypt

### Eventos
Eventos con:
- Fechas futuras (10-60 días)
- Categorías asignadas
- Capacidades variadas (500-10,000)
- URLs de imágenes de Unsplash
- Organizador asignado

### Tickets
Tipos de tickets con:
- Precios escalonados según categoría
- Cantidades proporcionales a la capacidad
- Límites de compra (1-10)
- Estados activos

---

## 🐛 Troubleshooting

### Error: "no existe la columna..."
```bash
python -m app.seeds.reset_database  # Responde: SI
python -m app.seeds.seed_data
```

### Error: "duplicate key value"
Los datos ya existen. Si quieres empezar de cero:
```bash
python -m app.seeds.reset_database
python -m app.seeds.seed_data
```

### Error: "could not connect to server"
1. Verifica que PostgreSQL esté corriendo
2. Revisa las credenciales en `.env`:
   ```
   DATABASE_URL=postgresql://user:pass@localhost:5432/ticketify
   ```

### Error: "relation does not exist"
La tabla no existe. Resetea la BD:
```bash
python -m app.seeds.reset_database
```

### La verificación encuentra problemas
Sigue las instrucciones que te da el script `verify_database.py`

---

## 📝 Notas

- **Solo Desarrollo**: Estos scripts son para entornos de desarrollo. En producción usa migraciones con Alembic.

- **Backup**: Si tienes datos importantes, haz backup antes de usar `reset_database.py`.

- **Idempotencia**: `seed_data.py` es idempotente - puedes ejecutarlo múltiples veces sin duplicar datos.

- **Passwords**: Las contraseñas de prueba están en texto plano en el código para facilitar el testing. En producción, nunca hagas esto.

- **Imágenes**: Los eventos usan URLs de Unsplash. En producción, usa URLs propias.

---

## 🎯 Resumen Rápido

```bash
# Setup completo
python -m app.seeds.reset_database && \
python -m app.seeds.seed_data && \
python run.py

# Verificar antes de deploy
python -m app.seeds.verify_database

# Limpiar y empezar de nuevo
python -m app.seeds.reset_database
```

---

¿Problemas? Revisa `DATABASE_SETUP.md` en la raíz del proyecto para más detalles.
