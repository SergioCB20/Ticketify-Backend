# Scripts de Mantenimiento del Marketplace

Este directorio contiene scripts útiles para mantenimiento y corrección del marketplace.

---

## 📜 Scripts Disponibles

### 1. `quick_clean_marketplace.py` ⚡ (RECOMENDADO PARA TI)

**Script rápido y simple** que elimina todos los listings activos y restaura los tickets.

```bash
python -m app.scripts.quick_clean_marketplace
```

**Qué hace:**
- ✅ Elimina TODOS los listings con status `ACTIVE`
- ✅ Restaura los tickets a estado `ACTIVE` e `isValid = True`
- ✅ Rápido y sin opciones complicadas

**Úsalo cuando:**
- Quieres limpiar completamente el marketplace de pruebas
- Tus tickets están en estado incorrecto
- Quieres empezar de cero

---

### 2. `delete_marketplace_listings.py` 🛠️ (AVANZADO)

Script interactivo con múltiples opciones.

```bash
python -m app.scripts.delete_marketplace_listings
```

**Opciones disponibles:**
1. **Cancelar listings activos** - Marca como CANCELLED (preserva historial)
2. **Eliminar listings activos** - Elimina solo los activos
3. **Eliminar TODOS los listings** - Limpieza total
4. **Eliminar por usuario** - Solo de un usuario específico
5. **Eliminar TODO** - Listings + Tickets ⚠️ PELIGROSO

**Úsalo cuando:**
- Necesitas control fino sobre qué eliminar
- Quieres preservar el historial (opción 1)
- Necesitas limpiar solo un usuario específico

---

### 3. `fix_marketplace_tickets.py` 🔧

Corrige tickets que quedaron en estado `TRANSFERRED` por el bug anterior.

```bash
python -m app.scripts.fix_marketplace_tickets
```

**Qué hace:**
- Busca listings con status `ACTIVE`
- Si el ticket asociado está `TRANSFERRED`, lo cambia a `ACTIVE`
- Útil después de aplicar el fix del código

**Úsalo cuando:**
- Acabas de aplicar el fix del código
- Tienes tickets viejos con estado incorrecto

---

## 🚀 Guía Rápida

### Para limpiar el marketplace completamente:

```bash
# 1. Ve al directorio del backend
cd C:\Users\gonza\Ingesoft\Ticketify\Ticketify-Backend

# 2. Ejecuta el script rápido
python -m app.scripts.quick_clean_marketplace

# 3. Confirma con 's'
```

---

## ⚠️ Advertencias

### Antes de ejecutar cualquier script:

1. **Haz un backup de la base de datos** (opcional pero recomendado)
2. **Cierra el backend** para evitar conflictos
3. **Lee lo que hace cada opción** antes de confirmar
4. **Verifica** que tienes los permisos necesarios

### Scripts peligrosos:

- ⚠️ `delete_marketplace_listings.py` opción 5: Elimina listings Y tickets
- ⚠️ Cualquier opción que diga "ELIMINAR TODO"

---

## 📊 Resumen de Acciones

| Script | Elimina Listings | Elimina Tickets | Restaura Tickets | Velocidad |
|--------|-----------------|-----------------|------------------|-----------|
| `quick_clean_marketplace` | ✅ (Activos) | ❌ | ✅ | ⚡ Rápido |
| `delete_marketplace_listings` (op.1) | ❌ (Cancela) | ❌ | ✅ | 🐢 Interactivo |
| `delete_marketplace_listings` (op.2) | ✅ (Activos) | ❌ | ✅ | 🐢 Interactivo |
| `delete_marketplace_listings` (op.5) | ✅ (Todos) | ✅ | ❌ | 🐢 Interactivo |
| `fix_marketplace_tickets` | ❌ | ❌ | ✅ | ⚡ Rápido |

---

## 🎯 Casos de Uso

### "Quiero empezar de cero con el marketplace"
```bash
python -m app.scripts.quick_clean_marketplace
```

### "Tengo tickets con estado incorrecto"
```bash
python -m app.scripts.fix_marketplace_tickets
```

### "Quiero eliminar solo mis listings"
```bash
python -m app.scripts.delete_marketplace_listings
# Luego selecciona opción 4 e ingresa tu email
```

### "Quiero preservar el historial"
```bash
python -m app.scripts.delete_marketplace_listings
# Luego selecciona opción 1 (Cancelar)
```

---

## 🔍 Verificación Post-Ejecución

Después de ejecutar cualquier script:

1. **Abre pgAdmin** o tu cliente de base de datos
2. **Verifica la tabla `marketplace_listings`:**
   ```sql
   SELECT COUNT(*) FROM marketplace_listings WHERE status = 'ACTIVE';
   ```
   Debería ser 0 si limpiaste correctamente

3. **Verifica los tickets:**
   ```sql
   SELECT status, COUNT(*) 
   FROM tickets 
   GROUP BY status;
   ```
   Los tickets deberían estar en `ACTIVE`

---

## 💡 Tips

- 🔄 **Siempre puedes volver a publicar** los tickets después de limpiar
- 📝 **Los tickets NO se pierden** con estos scripts (excepto opción 5)
- 🎨 **El historial se preserva** si usas "Cancelar" en lugar de "Eliminar"
- ⚡ **El script rápido es seguro** y recomendado para desarrollo

---

## 📞 Ayuda

Si tienes problemas:

1. Verifica que el backend esté **detenido**
2. Revisa los **logs de error** en la consola
3. Verifica tu **conexión a la base de datos**
4. Intenta con el **script rápido primero**

---

**Última actualización:** 6 de noviembre, 2025
