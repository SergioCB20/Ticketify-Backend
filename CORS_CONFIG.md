# Configuración de CORS en Ticketify Backend

## ¿Qué es CORS?

CORS (Cross-Origin Resource Sharing) es un mecanismo de seguridad que permite que un servidor indique a los navegadores web qué orígenes (dominios) tienen permiso para acceder a sus recursos.

## Configuración Actual

El backend de Ticketify ya está configurado con CORS para aceptar peticiones desde el frontend que corre en `http://localhost:3000`.

### Archivos Involucrados

#### 1. `/app/main.py`
Este archivo contiene la configuración principal del middleware de CORS:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Configuración:**
- `allow_origins`: Lista de orígenes permitidos (definidos en el archivo `.env`)
- `allow_credentials`: Permite el envío de cookies y credenciales
- `allow_methods`: Permite todos los métodos HTTP (GET, POST, PUT, DELETE, etc.)
- `allow_headers`: Permite todas las cabeceras HTTP

#### 2. `/app/core/config.py`
Define la estructura de configuración:

```python
ALLOWED_HOSTS: List[str] = ["http://localhost:3000"]
```

#### 3. `.env`
Archivo de configuración de entorno con los orígenes permitidos:

```env
ALLOWED_HOSTS=["http://localhost:3000","http://localhost:3001"]
```

## Orígenes Permitidos Actualmente

- ✅ `http://localhost:3000` - Frontend principal en desarrollo
- ✅ `http://localhost:3001` - Frontend alternativo (opcional)

## Cómo Agregar Más Orígenes

Si necesitas permitir peticiones desde otros dominios, edita el archivo `.env`:

```env
ALLOWED_HOSTS=["http://localhost:3000","http://localhost:3001","http://localhost:4200"]
```

**Nota:** Asegúrate de usar el formato JSON correcto con comillas dobles y corchetes.

## Verificar que CORS Funciona

### 1. Inicia el servidor backend
```bash
cd "C:\PUCP FCI ING.INF 2025-2\Ingeniería de Software\Segundo Backend\Ticketify-Backend"
python run.py
```

### 2. Verifica las cabeceras de respuesta
Abre el navegador y ve a la consola de desarrollador (F12). Realiza una petición desde tu frontend y verifica que las respuestas incluyan estas cabeceras:

```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: *
Access-Control-Allow-Headers: *
```

### 3. Prueba con curl (opcional)
```bash
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     http://localhost:8000/api/auth/login \
     -v
```

## Errores Comunes

### Error: "CORS policy: No 'Access-Control-Allow-Origin' header"

**Solución:**
1. Verifica que el servidor backend esté corriendo en el puerto 8000
2. Confirma que `http://localhost:3000` esté en la lista `ALLOWED_HOSTS`
3. Reinicia el servidor backend después de modificar el archivo `.env`

### Error: "Credentials flag is 'true', but the 'Access-Control-Allow-Credentials' header is empty"

**Solución:**
- El middleware ya tiene `allow_credentials=True`, este error no debería ocurrir
- Si ocurre, verifica que no hayas modificado la configuración del middleware

### Error: "Method not allowed"

**Solución:**
- El middleware permite todos los métodos (`allow_methods=["*"]`)
- Verifica que la ruta del endpoint sea correcta

## Configuración en Producción

⚠️ **IMPORTANTE:** En producción, NO uses `["*"]` para `allow_origins`. Especifica únicamente los dominios necesarios:

```python
# Ejemplo en producción
ALLOWED_HOSTS=["https://ticketify.com","https://www.ticketify.com"]
```

## Testing de CORS

Puedes probar que CORS funciona correctamente desde tu frontend con el siguiente código:

```javascript
// En tu frontend (React, Vue, etc.)
fetch('http://localhost:8000/api/events', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
  },
  credentials: 'include', // Importante para enviar cookies
})
  .then(response => response.json())
  .then(data => console.log('Success:', data))
  .catch(error => console.error('Error:', error));
```

## Recursos Adicionales

- [FastAPI CORS Documentation](https://fastapi.tiangolo.com/tutorial/cors/)
- [MDN CORS Guide](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [CORS Explained](https://www.codecademy.com/article/what-is-cors)

## Soporte

Si encuentras problemas con CORS después de seguir esta guía, verifica:

1. ✅ Servidor backend corriendo en puerto 8000
2. ✅ Frontend corriendo en puerto 3000
3. ✅ Archivo `.env` correctamente configurado
4. ✅ Servidor reiniciado después de cambios en `.env`
5. ✅ No hay proxies o VPNs interfiriendo con las peticiones
