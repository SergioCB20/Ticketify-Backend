# 📊 Análisis de Modelos - Ticketify Backend

## Comparación: Modelos Actuales vs Diagrama de Clases

---

## ✅ MODELOS QUE ESTÁN CORRECTOS (Sin cambios necesarios)

### 1. **EventCategory** (Category en diagrama)
- ✅ Campos coinciden
- ✅ No requiere cambios

### 2. **Notification**
- ✅ Campos coinciden con el diagrama
- ✅ Incluye tipo, título, mensaje, isRead, sentAt
- ✅ No requiere cambios

### 3. **MarketplaceListing**  
- ✅ Todos los campos del diagrama están implementados
- ✅ price, description, status, listedAt presentes
- ✅ No requiere cambios

---

## 🔄 MODELOS QUE NECESITAN MODIFICACIONES

### 1. **User** ⚠️ REQUIERE CAMBIOS IMPORTANTES

**Campos faltantes según diagrama:**
- `phoneNumber` (String) - Falta
- `documentId` (String) - Falta  
- `profilePhoto` (String) - Existe como `avatar`

**Campos que NO están en el diagrama pero existen:**
- `is_verified`, `verification_token`, `reset_token` (mover a Verification)
- `login_count` (innecesario)
- `avatar` (renombrar a `profilePhoto`)

**Enum actualizado:**
- Diagrama: ATTENDEE, ORGANIZER (simples)
- Actual: ADMIN, ORGANIZER, CUSTOMER

**Relaciones faltantes:**
- Role (Many-to-Many con Permission)
- Role tiene AdminRole enum (SUPER_ADMIN, SUPPORT_ADMIN, etc.)

### 2. **Event** ⚠️ REQUIERE CAMBIOS IMPORTANTES

**Campos faltantes:**
- `startDate` (DateTime) - Actualmente solo `date`
- `endDate` (DateTime) - No existe
- `venue` (String) - Existe como `location`
- `totalCapacity` (Integer) - Existe como `capacity`
- `multimedia` (List<String>) - No existe

**Campos que cambiar/eliminar:**
- `date` → Separar en `startDate` y `endDate`
- `location` → Renombrar a `venue`
- `capacity` → Renombrar a `totalCapacity`
- Eliminar: `short_description`, `address`, `city`, `country`, `base_price`, `image_url`, `banner_url`, `is_featured`, `slug`, `tags`, `published_at`

**Nueva relación:**
- EventSchedule (uno a muchos)

### 3. **Ticket** ⚠️ CAMBIOS MODERADOS

**Campos a mantener del diagrama:**
- ✅ `price` (Decimal) - No existe actualmente
- ✅ `qrCode` (String) - Existe como `qr_code`
- ✅ `purchaseDate` (DateTime) - No existe
- ✅ `status` (String) - Existe
- ✅ `isValid` (Boolean) - Existe como property

**Campos a eliminar:**
- `ticket_number`, `barcode`, `seat_number`, `section`, `row_number`
- `is_transferable`, `is_refundable`
- `used_at`, `validated_by`, `entry_gate`
- `original_owner_id`, `transferred_at`, `transfer_reason`
- `notes`, `special_requirements`, `expires_at`

**Simplificar a:**
```python
- id
- price
- qrCode
- purchaseDate
- status
- isValid (Boolean)
```

### 4. **TicketType** ✅ MODELO CORRECTO
- Coincide con el diagrama
- name, price, quantity, available
- No requiere cambios

### 5. **Purchase** → **Payment** 🔄 RENOMBRAR Y MODIFICAR

**Este modelo debe llamarse "Payment" según el diagrama**

**Campos del diagrama:**
- id
- amount
- paymentMethod
- transactionId
- status
- paymentDate

**Cambios necesarios:**
- Renombrar modelo de `Purchase` a `Payment`
- Simplificar campos (eliminar billing info, buyer info detallada)
- Mantener solo: amount, paymentMethod, transactionId, status, paymentDate

---

## 🆕 MODELOS FALTANTES (Crear desde cero)

### 1. **Role** ⭐ NUEVO

```python
class Role(Base):
    __tablename__ = "roles"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("User", secondary="user_roles", back_populates="roles")
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")
```

### 2. **Permission** ⭐ NUEVO

```python
class Permission(Base):
    __tablename__ = "permissions"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    code = Column(String(100), nullable=False, unique=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationships
    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")
```

### 3. **AdminRole** (Enum)

```python
class AdminRole(str, enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    SUPPORT_ADMIN = "SUPPORT_ADMIN"
    SECURITY_ADMIN = "SECURITY_ADMIN"
    CONTENT_ADMIN = "CONTENT_ADMIN"
```

### 4. **UserRole** (Enum - Actualizar)

```python
class UserRole(str, enum.Enum):
    ATTENDEE = "ATTENDEE"  # Cliente/Asistente
    ORGANIZER = "ORGANIZER"  # Organizador
```

### 5. **EventSchedule** ⭐ NUEVO

```python
class EventSchedule(Base):
    __tablename__ = "event_schedules"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    dateTime = Column(DateTime(timezone=True), nullable=False)
    duration = Column(Integer, nullable=False)  # Minutes
    
    # Foreign key
    event_id = Column(UUID, ForeignKey("events.id"), nullable=False)
    
    # Relationship
    event = relationship("Event", back_populates="schedules")
```

### 6. **TicketTransfer** ⭐ NUEVO

```python
class TicketTransfer(Base):
    __tablename__ = "ticket_transfers"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    transferDate = Column(DateTime(timezone=True), server_default=func.now())
    oldQR = Column(String, nullable=False)
    newQR = Column(String, nullable=False)
    
    # Foreign keys
    ticket_id = Column(UUID, ForeignKey("tickets.id"), nullable=False)
    from_user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    to_user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    ticket = relationship("Ticket")
    from_user = relationship("User", foreign_keys=[from_user_id])
    to_user = relationship("User", foreign_keys=[to_user_id])
```

### 7. **Transaction** ⭐ NUEVO

```python
class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    type = Column(String(50), nullable=False)  # SALE, REFUND, TRANSFER
    amount = Column(Numeric(10, 2), nullable=False)
    commission = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), nullable=False)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    
    # Foreign keys
    payment_id = Column(UUID, ForeignKey("payments.id"), nullable=True)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    payment = relationship("Payment")
    user = relationship("User")
```

### 8. **Validation** ⭐ NUEVO

```python
class Validation(Base):
    __tablename__ = "validations"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    scanTime = Column(DateTime(timezone=True), server_default=func.now())
    scannedBy = Column(String(255), nullable=False)
    isValid = Column(Boolean, nullable=False)
    location = Column(String(255), nullable=True)
    
    # Foreign keys
    ticket_id = Column(UUID, ForeignKey("tickets.id"), nullable=False)
    
    # Relationship
    ticket = relationship("Ticket")
    validation_logs = relationship("QRValidationLog", back_populates="validation")
```

### 9. **QRValidationLog** ⭐ NUEVO

```python
class QRValidationLog(Base):
    __tablename__ = "qr_validation_logs"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    attemptTime = Column(DateTime(timezone=True), server_default=func.now())
    success = Column(Boolean, nullable=False)
    ipAddress = Column(String(45), nullable=True)
    device = Column(String(255), nullable=True)
    
    # Foreign key
    validation_id = Column(UUID, ForeignKey("validations.id"), nullable=False)
    
    # Relationship
    validation = relationship("Validation", back_populates="validation_logs")
```

### 10. **Dispute** ⭐ NUEVO

```python
class DisputeType(str, enum.Enum):
    FRAUD = "FRAUD"
    REFUND_REQUEST = "REFUND_REQUEST"
    INVALID_TICKET = "INVALID_TICKET"
    DUPLICATE_QR = "DUPLICATE_QR"
    PAYMENT_ISSUE = "PAYMENT_ISSUE"

class DisputeStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_REVIEW = "IN_REVIEW"
    RESOLVED = "RESOLVED"
    REJECTED = "REJECTED"
    ESCALATED = "ESCALATED"

class Dispute(Base):
    __tablename__ = "disputes"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    type = Column(Enum(DisputeType), nullable=False)
    status = Column(Enum(DisputeStatus), default=DisputeStatus.PENDING)
    description = Column(Text, nullable=False)
    evidence = Column(Text, nullable=True)  # JSON array of file URLs
    adminNotes = Column(Text, nullable=True)
    resolution = Column(Text, nullable=True)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    resolvedAt = Column(DateTime(timezone=True), nullable=True)
    
    # Foreign keys
    ticket_id = Column(UUID, ForeignKey("tickets.id"), nullable=False)
    reported_by = Column(UUID, ForeignKey("users.id"), nullable=False)
    assigned_admin = Column(UUID, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    ticket = relationship("Ticket")
    reporter = relationship("User", foreign_keys=[reported_by])
    admin = relationship("User", foreign_keys=[assigned_admin])
```

### 11. **SupportTicket** ⭐ NUEVO

```python
class SupportTicket(Base):
    __tablename__ = "support_tickets"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="OPEN")
    priority = Column(String(50), nullable=False, default="MEDIUM")
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    
    # Foreign keys
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    assigned_to = Column(UUID, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    admin = relationship("User", foreign_keys=[assigned_to])
```

### 12. **Report** ⭐ NUEVO

```python
class Report(Base):
    __tablename__ = "reports"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    type = Column(String(100), nullable=False)
    generatedAt = Column(DateTime(timezone=True), server_default=func.now())
    data = Column(Text, nullable=True)  # JSON data
    
    # Foreign key
    generated_by = Column(UUID, ForeignKey("users.id"), nullable=False)
    
    # Relationship
    user = relationship("User")
```

### 13. **Analytics** ⭐ NUEVO

```python
class Analytics(Base):
    __tablename__ = "analytics"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    totalSales = Column(Integer, default=0)
    revenue = Column(Numeric(10, 2), default=0)
    attendees = Column(Integer, default=0)
    salesByDate = Column(Text, nullable=True)  # JSON
    
    # Foreign key
    event_id = Column(UUID, ForeignKey("events.id"), nullable=False)
    
    # Relationship
    event = relationship("Event")
```

### 14. **AuditLog** ⭐ NUEVO

```python
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    action = Column(String(100), nullable=False)
    resource = Column(String(100), nullable=False)
    ipAddress = Column(String(45), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    metadata = Column(Text, nullable=True)  # JSON
    
    # Foreign key
    user_id = Column(UUID, ForeignKey("users.id"), nullable=True)
    
    # Relationship
    user = relationship("User")
```

---

## 🗑️ MODELOS A ELIMINAR

### 1. **Promotion**
- No está en el diagrama actualizado
- ELIMINAR archivo: `app/models/promotion.py`

### 2. **Verification** 
- Funcionalidad debe estar en User
- ELIMINAR archivo: `app/models/verification.py`

---

## 📋 RESUMEN DE ACCIONES

### Modificar (6 modelos):
1. ✏️ User - Agregar phoneNumber, documentId, actualizar role system
2. ✏️ Event - Cambiar date por startDate/endDate, agregar multimedia
3. ✏️ Ticket - Simplificar dramáticamente
4. ✏️ Purchase → Payment - Renombrar y simplificar
5. ✏️ Notification - Actualizar tipo enum
6. ✏️ EventCategory - Mantener como está

### Crear (14 modelos nuevos):
1. ⭐ Role
2. ⭐ Permission
3. ⭐ EventSchedule
4. ⭐ TicketTransfer
5. ⭐ Transaction
6. ⭐ Validation
7. ⭐ QRValidationLog
8. ⭐ Dispute
9. ⭐ SupportTicket
10. ⭐ Report
11. ⭐ Analytics
12. ⭐ AuditLog
13. ⭐ AdminRole (enum)
14. ⭐ UserRole (actualizar enum)

### Eliminar (2 modelos):
1. ❌ Promotion
2. ❌ Verification

### Mantener sin cambios (3 modelos):
1. ✅ TicketType
2. ✅ MarketplaceListing
3. ✅ EventCategory (Category)

---

## 🎯 Prioridades de Implementación

### FASE 1 - Core (Alta prioridad):
1. User (modificar)
2. Role & Permission (crear)
3. Event (modificar)
4. Ticket (modificar)
5. Payment (renombrar Purchase)

### FASE 2 - Transacciones (Media prioridad):
6. Transaction (crear)
7. TicketTransfer (crear)
8. EventSchedule (crear)

### FASE 3 - Validación y Seguridad (Media prioridad):
9. Validation (crear)
10. QRValidationLog (crear)
11. AuditLog (crear)

### FASE 4 - Soporte (Baja prioridad):
12. Dispute (crear)
13. SupportTicket (crear)

### FASE 5 - Analytics (Baja prioridad):
14. Report (crear)
15. Analytics (crear)

---

## ⚠️ IMPORTANTE - Migraciones de Base de Datos

Después de hacer estos cambios, deberás:

1. **Crear migraciones de Alembic** para cada cambio
2. **Respaldar la base de datos** antes de aplicar cambios
3. **Probar en ambiente de desarrollo** primero
4. **Actualizar seeds/fixtures** con datos de ejemplo

```bash
# Crear nueva migración
alembic revision --autogenerate -m "Update models according to class diagram"

# Aplicar migración
alembic upgrade head
```

---

**Fecha de análisis**: Octubre 2025  
**Estado**: Requiere implementación de cambios
