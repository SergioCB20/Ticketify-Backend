# 🚀 Guía de Implementación Paso a Paso - Sistema de Facturación

## ✅ Checklist de Implementación

Sigue estos pasos en orden para implementar completamente el sistema de facturación.

---

## 📋 Fase 1: Instalación de Dependencias

### Paso 1.1: Instalar librerías de Python
```bash
cd Ticketify-Backend
pip install -r billing_requirements.txt
```

**Verificar instalación:**
```bash
python -c "import reportlab, openpyxl, cryptography; print('✅ Dependencias instaladas')"
```

---

## 🔐 Fase 2: Configuración de Seguridad

### Paso 2.1: Generar clave de encriptación
```bash
python -c "from app.utils.encryption import generate_new_encryption_key; print(generate_new_encryption_key())"
```

**Copiar la clave generada** (ejemplo: `abc123def456...`)

### Paso 2.2: Actualizar archivo .env
Agregar al final del archivo `.env`:

```env
# ============================================================
# Sistema de Facturación
# ============================================================

# Encriptación de tokens (GENERAR CON EL SCRIPT)
ENCRYPTION_KEY=<pegar_clave_aqui>

# Webhook de MercadoPago (obtener del panel de MP)
MERCADOPAGO_WEBHOOK_SECRET=<obtener_de_mercadopago>

# Modo debug (solo desarrollo)
DEBUG=True
```

### Paso 2.3: Migrar tokens existentes (si hay usuarios con MP conectado)
```python
# Ejecutar en Python shell
from app.core.database import SessionLocal
from app.utils.encryption import migrate_existing_tokens_to_encrypted

db = SessionLocal()
migrate_existing_tokens_to_encrypted(db)
db.close()
```

---

## 💾 Fase 3: Optimización de Base de Datos

### Paso 3.1: Crear índices de performance
```bash
python create_billing_indexes.py
```

**Salida esperada:**
```
✅ Índice idx_purchases_event_status creado
✅ Índice idx_purchases_payment_date creado
✅ Índice idx_purchases_created_at_desc creado
✅ Índice idx_purchases_user_event creado
✅ Índice idx_purchases_payment_reference creado
✅ Índice idx_events_organizer creado
✅ Índice idx_payments_transaction creado
```

### Paso 3.2: Verificar índices creados
```sql
-- Ejecutar en PostgreSQL
SELECT tablename, indexname 
FROM pg_indexes 
WHERE indexname LIKE 'idx_%' 
ORDER BY tablename, indexname;
```

---

## 🔔 Fase 4: Configuración de Webhooks

### Paso 4.1: Exponer URL pública (desarrollo)
Para desarrollo local, usar **ngrok** o similar:

```bash
# Instalar ngrok
# https://ngrok.com/download

# Exponer puerto 8000
ngrok http 8000
```

**Copiar la URL HTTPS** que ngrok proporciona (ejemplo: `https://abc123.ngrok.io`)

### Paso 4.2: Registrar webhook en MercadoPago

1. Ir a: https://www.mercadopago.com/developers/panel/webhooks
2. Hacer clic en **"Nueva integración"**
3. Configurar:
   - **Nombre:** Ticketify Webhooks
   - **URL:** `https://tu-url.ngrok.io/api/webhooks/mercadopago`
   - **Eventos:** Seleccionar **"Payment"**
4. Hacer clic en **"Crear"**
5. **Copiar el Secret** generado

### Paso 4.3: Actualizar .env con el secret
```env
MERCADOPAGO_WEBHOOK_SECRET=<secret_copiado>
```

### Paso 4.4: Reiniciar servidor
```bash
# Detener servidor (Ctrl+C)
# Iniciar nuevamente
python run.py
```

---

## 🧪 Fase 5: Verificación del Sistema

### Paso 5.1: Ejecutar verificación completa
```bash
python verify_billing_complete.py
```

**Salida esperada:**
```
============================================================
Sistema de Facturación - Verificación Completa
============================================================

============================ Python ============================
✅ Python 3.10.x

====================== Dependencias ========================
✅ FastAPI
✅ SQLAlchemy
✅ Pydantic
✅ MercadoPago SDK
✅ ReportLab (PDF)
✅ OpenPyXL (Excel)
✅ Cryptography (Encriptación)
✅ Requests

... (continúa)

Resultado: 9/9 verificaciones exitosas
🎉 ¡Todos los componentes están correctamente configurados!
```

### Paso 5.2: Probar endpoint de status
```bash
# Obtener token de un usuario organizador
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Probar endpoint
curl http://localhost:8000/api/organizer/billing/status \
  -H "Authorization: Bearer $TOKEN"
```

**Salida esperada:**
```json
{
  "status": "operational",
  "organizerId": "uuid...",
  "organizerEmail": "organizador@ejemplo.com",
  "mercadopagoConnected": true,
  "totalEvents": 5,
  "hasEvents": true
}
```

### Paso 5.3: Verificar documentación interactiva
Abrir en navegador:
```
http://localhost:8000/docs
```

Buscar sección **"Billing - Organizador"** y **"Webhooks"**

---

## 🎯 Fase 6: Testing Funcional

### Paso 6.1: Crear datos de prueba (si no existen)

```python
# Ejecutar en Python shell
from app.core.database import SessionLocal
from app.models.user import User
from app.models.event import Event
from app.models.purchase import Purchase, PurchaseStatus
from datetime import datetime
from decimal import Decimal
import uuid

db = SessionLocal()

# Buscar un organizador
organizer = db.query(User).join(User.roles).filter(
    User.roles.any(name='ORGANIZER')
).first()

if organizer:
    # Crear evento de prueba
    event = Event(
        id=uuid.uuid4(),
        title="Evento de Prueba - Facturación",
        description="Evento para probar el sistema de facturación",
        startDate=datetime.now(),
        endDate=datetime.now(),
        organizer_id=organizer.id,
        # ... otros campos requeridos
    )
    db.add(event)
    db.commit()
    
    print(f"✅ Evento creado: {event.id}")
```

### Paso 6.2: Probar endpoints

#### 6.2.1: Listar eventos
```bash
curl http://localhost:8000/api/organizer/billing/events \
  -H "Authorization: Bearer $TOKEN"
```

#### 6.2.2: Ver detalle de evento
```bash
EVENT_ID="uuid-del-evento"

curl http://localhost:8000/api/organizer/billing/events/$EVENT_ID \
  -H "Authorization: Bearer $TOKEN"
```

#### 6.2.3: Sincronizar con MercadoPago
```bash
curl -X POST http://localhost:8000/api/organizer/billing/events/$EVENT_ID/sync \
  -H "Authorization: Bearer $TOKEN"
```

#### 6.2.4: Descargar reporte PDF
```bash
curl "http://localhost:8000/api/organizer/billing/events/$EVENT_ID/report?format=pdf" \
  -H "Authorization: Bearer $TOKEN" \
  --output reporte_prueba.pdf
```

#### 6.2.5: Descargar reporte Excel
```bash
curl "http://localhost:8000/api/organizer/billing/events/$EVENT_ID/report?format=excel" \
  -H "Authorization: Bearer $TOKEN" \
  --output reporte_prueba.xlsx
```

### Paso 6.3: Probar webhook (desarrollo)
```bash
# Simular notificación de pago
PAYMENT_ID="12345678"

curl -X POST "http://localhost:8000/api/webhooks/mercadopago/test?payment_id=$PAYMENT_ID"
```

---

## 🔄 Fase 7: Prueba de Refresh de Tokens

### Paso 7.1: Verificar fecha de expiración de tokens
```python
from app.core.database import SessionLocal
from app.models.user import User
from datetime import datetime

db = SessionLocal()

# Buscar usuarios con MP conectado
users = db.query(User).filter(
    User.isMercadopagoConnected == True
).all()

for user in users:
    if user.mercadopagoTokenExpires:
        days_left = (user.mercadopagoTokenExpires - datetime.utcnow()).days
        print(f"Usuario: {user.email}")
        print(f"Días hasta expiración: {days_left}")
        print("---")
```

### Paso 7.2: Forzar refresh manual (opcional)
```python
from app.services.billing_service import BillingService
from app.core.database import SessionLocal

db = SessionLocal()
billing_service = BillingService(db)

# Renovar token de un usuario
user_id = "uuid-del-usuario"
success = billing_service.refresh_mercadopago_token(user_id)

if success:
    print("✅ Token renovado exitosamente")
else:
    print("❌ Error al renovar token")

db.close()
```

---

## 📊 Fase 8: Monitoreo y Logs

### Paso 8.1: Configurar logging
Agregar al archivo `app/main.py`:

```python
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("billing.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("billing")
```

### Paso 8.2: Revisar logs
```bash
# Ver logs en tiempo real
tail -f billing.log

# Filtrar solo logs de facturación
grep "billing" billing.log

# Filtrar errores
grep "ERROR" billing.log
```

---

## 🚀 Fase 9: Deployment (Producción)

### Paso 9.1: Checklist pre-deployment

- [ ] HTTPS configurado y funcionando
- [ ] Clave de encriptación generada y guardada de forma segura
- [ ] Variables de entorno configuradas en servidor de producción
- [ ] Índices de base de datos creados
- [ ] Tokens existentes migrados a formato encriptado
- [ ] Webhook registrado en MercadoPago con URL de producción
- [ ] Backups de base de datos configurados
- [ ] Monitoring configurado (opcional)
- [ ] Rate limiting configurado (opcional)

### Paso 9.2: Configurar servidor de producción

```bash
# En servidor de producción

# 1. Clonar repositorio
git clone <url-del-repo>
cd Ticketify-Backend

# 2. Instalar dependencias
pip install -r requirements.txt
pip install -r billing_requirements.txt

# 3. Configurar .env
nano .env
# Agregar todas las variables necesarias

# 4. Crear índices
python create_billing_indexes.py

# 5. Verificar
python verify_billing_complete.py

# 6. Iniciar con gunicorn (ejemplo)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

### Paso 9.3: Registrar webhook de producción

1. Ir a: https://www.mercadopago.com/developers/panel/webhooks
2. Editar la integración existente
3. Cambiar URL a: `https://tu-dominio-produccion.com/api/webhooks/mercadopago`
4. Guardar cambios

---

## ✅ Checklist Final

### Desarrollo
- [x] Dependencias instaladas
- [x] Clave de encriptación generada
- [x] Variables de entorno configuradas
- [x] Índices de base de datos creados
- [x] Webhook registrado (ngrok)
- [x] Verificación completa exitosa
- [x] Endpoints probados

### Pre-Producción
- [ ] HTTPS configurado
- [ ] Servidor de producción listo
- [ ] Variables de entorno en producción
- [ ] Webhook de producción registrado
- [ ] Backups configurados
- [ ] Monitoring configurado

### Producción
- [ ] Sistema desplegado
- [ ] Pruebas de smoke test
- [ ] Documentación entregada
- [ ] Equipo capacitado

---

## 🎉 ¡Implementación Completada!

Si has seguido todos los pasos, el sistema de facturación está completamente funcional y listo para usar.

### Próximos pasos:
1. Revisar documentación completa en `SISTEMA_FACTURACION_FINAL.md`
2. Completar checklist de producción en `CHECKLIST_PRODUCCION.md`
3. Capacitar al equipo en el uso del sistema

---

## 📞 Soporte

Si encuentras problemas durante la implementación:

1. **Revisar logs:** `tail -f billing.log`
2. **Ejecutar verificación:** `python verify_billing_complete.py`
3. **Consultar troubleshooting:** Ver `SISTEMA_FACTURACION_FINAL.md`
4. **Revisar documentación:** Ver todos los archivos MD en el proyecto

---

**Guía creada:** 25 de Noviembre de 2025  
**Versión:** 1.0  
**Estado:** ✅ COMPLETA  

**¡Éxito con tu implementación!** 🚀
