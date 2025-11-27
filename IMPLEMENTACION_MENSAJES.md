# 🚀 INSTRUCCIONES DE IMPLEMENTACIÓN COMPLETA
## Sistema de Mensajes a Asistentes - Ticketify

---

## ✅ PASOS PARA IMPLEMENTAR

### PASO 1: Aplicar Migración de Base de Datos

Abre una terminal en la carpeta del backend:

```bash
cd C:\Users\gonza\Ingesoft\Ticketify\Ticketify-Backend

# Activar entorno virtual (si no está activado)
venv\Scripts\activate

# Ejecutar migración
alembic upgrade head
```

**Resultado esperado:**
```
INFO  [alembic.runtime.migration] Running upgrade 53533509121b -> add_event_messages, add event_messages table
```

---

### PASO 2: Verificar que Todo Funciona

Ejecutar el script de pruebas:

```bash
python test_event_messages.py
```

**Resultado esperado:**
```
🧪 PRUEBAS DEL SISTEMA DE MENSAJES A ASISTENTES
============================================================
🔌 Probando conexión a la base de datos...
✅ Conexión exitosa a la base de datos

📋 Verificando tabla event_messages...
✅ Tabla event_messages existe
📊 Mensajes en la tabla: 0

👥 Probando obtención de asistentes...
✅ Se encontraron X asistentes

💬 Probando creación de mensaje...
✅ Mensaje creado con ID: ...

📊 RESUMEN DE PRUEBAS
============================================================
✅ PASS - Conexión a BD
✅ PASS - Tabla event_messages
✅ PASS - Obtener asistentes
✅ PASS - Crear mensaje

🎯 Resultado: 4/4 pruebas exitosas
🎉 ¡Todas las pruebas pasaron! El sistema está listo para usar.
```

---

### PASO 3: Iniciar el Backend

```bash
# En la carpeta del backend
python run.py
```

**Verificar que inicia sin errores:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [XXXX] using WatchFiles
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

### PASO 4: Iniciar el Frontend

Abre otra terminal en la carpeta del frontend:

```bash
cd C:\Users\gonza\Ingesoft\Ticketify\Ticketify-Frontend

# Instalar dependencias (si no están instaladas)
npm install

# Iniciar servidor de desarrollo
npm run dev
```

**Resultado esperado:**
```
  ▲ Next.js 14.x.x
  - Local:        http://localhost:3000

 ✓ Ready in X.Xs
```

---

### PASO 5: Probar la Funcionalidad

#### 5.1 Acceder al Sistema

1. Abre el navegador en `http://localhost:3000`
2. Inicia sesión como organizador
3. Ve a "Panel" → "Mis Eventos"

#### 5.2 Acceder a Mensajes

**Opción A: URL Directa**
```
http://localhost:3000/panel/my-events/{EVENT_ID}/messages
```

**Opción B: Integrar Botón (ver INTEGRATION_GUIDE_MESSAGES.md)**

#### 5.3 Enviar un Mensaje de Prueba

1. Click en "Enviar Nuevo Mensaje"
2. Completa el formulario:
   - **Asunto:** "Prueba del sistema de mensajes"
   - **Mensaje:** "Este es un mensaje de prueba para verificar que todo funciona correctamente."
3. Verifica que muestre el número de asistentes
4. Click en "Enviar Mensaje"

**Resultado esperado:**
- ✅ Modal muestra "¡Mensaje enviado exitosamente!"
- ✅ Aparece en el historial de mensajes
- ✅ Se muestran las estadísticas (destinatarios, tasa de éxito)
- ✅ Los asistentes reciben el email

#### 5.4 Verificar Email

Revisa la bandeja de entrada de un asistente de prueba. Deberías ver:
- ✅ Email con el asunto del mensaje
- ✅ Template profesional con gradientes
- ✅ Información del evento
- ✅ Contenido del mensaje
- ✅ Botón "Ver Mis Tickets"

---

## 🔍 VERIFICACIÓN DE ENDPOINTS

Puedes probar los endpoints directamente con:

### Swagger UI (Documentación Interactiva)

Abre en el navegador:
```
http://localhost:8000/docs
```

### Endpoints Disponibles

1. **POST** `/api/events/{event_id}/messages` - Enviar mensaje
2. **GET** `/api/events/{event_id}/messages` - Listar mensajes
3. **GET** `/api/events/{event_id}/messages/{message_id}` - Ver detalles
4. **GET** `/api/events/{event_id}/attendees` - Lista de asistentes
5. **GET** `/api/events/{event_id}/messages/stats` - Estadísticas

---

## ⚠️ SOLUCIÓN DE PROBLEMAS COMUNES

### Error: "Tabla event_messages no existe"
**Solución:** Ejecuta la migración:
```bash
alembic upgrade head
```

### Error: "No aparecen asistentes"
**Causas posibles:**
1. El evento no tiene tickets vendidos
2. Los tickets están cancelados (`status != 'ACTIVE'`)
3. Los usuarios están inactivos (`isActive = false`)

**Solución:** Verifica en la BD:
```sql
SELECT COUNT(*) FROM tickets 
WHERE event_id = 'TU_EVENT_ID' AND status = 'ACTIVE';
```

### Error: "Los emails no se envían"
**Causas posibles:**
1. Configuración SMTP incorrecta en `.env`
2. Credenciales de Gmail incorrectas
3. Gmail bloqueando el acceso

**Solución:**
1. Verifica las variables en `.env`:
   ```
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=tu_email@gmail.com
   SMTP_PASSWORD=tu_app_password
   ```
2. Si usas Gmail, genera una "Contraseña de aplicación"

---

## 📝 CHECKLIST FINAL

Antes de considerar completado, verifica:

- [ ] Migración de Alembic ejecutada sin errores
- [ ] Script de pruebas pasa todas las verificaciones
- [ ] Backend inicia sin errores
- [ ] Frontend inicia sin errores
- [ ] Puedes acceder a `/panel/my-events/{id}/messages`
- [ ] Modal de envío se abre correctamente
- [ ] Muestra el número correcto de asistentes
- [ ] Mensaje se envía exitosamente
- [ ] Aparece en el historial
- [ ] Estadísticas se muestran correctamente
- [ ] Emails llegan a los asistentes
- [ ] Template del email se ve bien

---

**Fecha:** Noviembre 26, 2025
**Versión:** 1.0.0
**Estado:** ✅ Implementación Completa
