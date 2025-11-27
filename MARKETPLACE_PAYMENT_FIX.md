# 🔧 Solución: Error 403 MercadoPago Marketplace

## 📋 Problema
Error 403 al comprar en marketplace, pero compra de eventos funciona ✅

## ✅ Solución Implementada

### Cambio Principal
**ANTES**: Usaba token del vendedor + `application_fee` (requiere certificación)
**AHORA**: Usa token de plataforma (igual que eventos) ✅

### Archivos Modificados

1. **payment_service.py**
```python
# ✅ NUEVO: Usar platform_sdk en lugar de seller_sdk
preference_response = self.platform_sdk.preference().create(preference_data)

# ❌ REMOVIDO: application_fee (causaba error 403)
```

2. **marketplace_service.py**
```python
# ✅ NUEVO: Agregar platform_fee como parámetro
def create_marketplace_payment_and_transfer(
    self, listing, buyer, payment_info, 
    platform_fee: Decimal = None  # <-- Nuevo
):
    # Calcular y loggear división de dinero
    if platform_fee is None:
        platform_fee = Decimal(str(listing.price)) * Decimal("0.05")
    
    logger.info(f"💰 Precio total: S/ {listing.price}")
    logger.info(f"💸 Comisión (5%): S/ {platform_fee}")
    logger.info(f"👤 Vendedor recibe: S/ {listing.price - platform_fee}")
```

3. **marketplace.py (webhook)**
```python
# ✅ NUEVO: Calcular y pasar platform_fee
platform_fee = Decimal(str(listing.price)) * Decimal("0.05")

new_ticket = service.create_marketplace_payment_and_transfer(
    listing=listing,
    buyer=buyer,
    payment_info=payment_info_dict,
    platform_fee=platform_fee  # <-- Nuevo parámetro
)
```

## 💰 Flujo de Dinero

```
Comprador paga: S/ 100
    ↓
Va a Plataforma: S/ 100
    ↓
División:
  - Plataforma: S/ 5 (5% comisión)
  - Vendedor: S/ 95 (pendiente de transferir)
```

## 🎯 Resultado

✅ **Marketplace funciona igual que eventos**
✅ **Sin error 403**
✅ **Tickets transferidos correctamente**
✅ **Comisiones registradas en logs**

## ⚠️ Pendiente

Implementar sistema automatizado de pagos a vendedores:
- Transferencias diarias programadas
- Dashboard de balance para vendedores
- Notificaciones de pagos

## 📝 Logs Generados

```
💰 Precio total: S/ 100.00
💸 Comisión plataforma (5%): S/ 5.00
👤 Pago al vendedor: S/ 95.00
📋 TODO: Procesar transferencia manual al vendedor
```

---
**Status**: ✅ Funcional  
**Fecha**: 21/11/2025
