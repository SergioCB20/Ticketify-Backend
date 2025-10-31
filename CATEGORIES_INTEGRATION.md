# 🎯 Integración de Categorías - Ticketify

Integración completa de las categorías de eventos de la base de datos PostgreSQL en Frontend y Backend.

## ✅ Implementación Completada

### 1️⃣ Backend - API de Categorías

#### Archivos Creados:

**`app/schemas/category.py`**
- `EventCategoryResponse`: Schema de respuesta con todos los campos
- `EventCategoryListResponse`: Schema para lista de categorías

**`app/repositories/category_repository.py`**
- `get_all_categories()`: Obtener todas las categorías
- `get_featured_categories()`: Obtener categorías destacadas
- `get_category_by_id()`: Obtener por ID
- `get_category_by_slug()`: Obtener por slug
- `get_root_categories()`: Obtener categorías raíz (nivel 0)

**`app/services/category_service.py`**
- Lógica de negocio para categorías
- Conversión de modelos a responses
- Manejo de errores

**`app/api/categories.py`**
- 4 endpoints REST para categorías
- Documentación OpenAPI completa

#### Endpoints Disponibles:

```
GET /api/categories/                    # Listar todas las categorías
GET /api/categories/featured            # Categorías destacadas
GET /api/categories/{category_id}       # Obtener por ID
GET /api/categories/slug/{slug}         # Obtener por slug
```

---

### 2️⃣ Frontend - Integración en Crear Eventos

#### Archivos Creados/Modificados:

**`src/services/api/categories.ts`** ✨ NUEVO
- `getCategories()`: Obtener todas las categorías
- `getFeaturedCategories()`: Categorías destacadas
- `getCategoryById()`: Obtener por ID
- `getCategoryBySlug()`: Obtener por slug
- Types: `Category`, `CategoriesResponse`

**`src/app/events/crear/page.tsx`** 📝 ACTUALIZADO
- Carga dinámica de categorías al montar el componente
- Select poblado con categorías de la BD
- Loading state mientras carga categorías
- Manejo de errores

---

## 🗄️ Datos en Base de Datos

Las siguientes categorías ya están insertadas en PostgreSQL:

| Nombre | Slug | Icon | Color | Featured |
|--------|------|------|-------|----------|
| Conciertos | conciertos | fa-music | #E74C3C | ✅ |
| Deportes | deportes | fa-futbol | #3498DB | ✅ |
| Teatro | teatro | fa-theater-masks | #8E44AD | ❌ |
| Conferencias | conferencias | fa-chalkboard-teacher | #1ABC9C | ❌ |
| Festivales | festivales | fa-glass-cheers | #F1C40F | ✅ |
| Otros | otros | fa-ellipsis-h | #95A5A6 | ❌ |

---

## 🔄 Flujo de Creación de Eventos

### Antes (Hardcoded):
```tsx
<Select>
  <option value="">Elige una categoría</option>
  <option value="conciertos">🎵 Conciertos</option>
  <option value="deportes">⚽ Deportes</option>
  // ... más opciones hardcodeadas
</Select>
```

### Ahora (Dinámico):
```tsx
// 1. Cargar categorías al montar componente
useEffect(() => {
  const loadCategories = async () => {
    const data = await getCategories()
    setCategories(data.categories)
  }
  loadCategories()
}, [])

// 2. Renderizar dinámicamente
<Select disabled={loadingCategories}>
  <option value="">{loadingCategories ? 'Cargando...' : 'Elige una categoría'}</option>
  {categories.map(category => (
    <option key={category.id} value={category.id}>
      {category.icon} {category.name}
    </option>
  ))}
</Select>
```

### Al crear evento:
```javascript
const eventData = {
  title: formData.nombre,
  description: formData.descripcion,
  startDate: constructDateISO(formData.fechaInicio),
  endDate: constructDateISO(formData.fechaFin),
  venue: formData.ubicacion,
  totalCapacity: parseInt(formData.capacidad),
  multimedia: [],
  category_id: formData.categoria // ✅ UUID de la categoría seleccionada
}

await createEvent(eventData)
```

---

## 🧪 Cómo Probar

### Backend:

1. **Iniciar el servidor:**
```bash
cd "Backend Actualizado/Ticketify-Backend"
python run.py
```

2. **Probar endpoints:**
```bash
# Listar todas las categorías
curl http://localhost:8000/api/categories/

# Categorías destacadas
curl http://localhost:8000/api/categories/featured

# Por ID
curl http://localhost:8000/api/categories/{uuid}

# Por slug
curl http://localhost:8000/api/categories/slug/conciertos
```

3. **Swagger UI:**
```
http://localhost:8000/docs
```

### Frontend:

1. **Iniciar el servidor:**
```bash
cd "Frontend Actualizado/Ticketify-Frontend"
npm run dev
```

2. **Visitar página:**
```
http://localhost:3000/events/crear
```

3. **Verificar:**
- ✅ El select de categorías debe mostrar "Cargando categorías..." inicialmente
- ✅ Luego debe cargar las 6 categorías de la BD
- ✅ Cada opción muestra: `{icon} {nombre}`
- ✅ Al seleccionar y crear evento, se envía el UUID de la categoría

---

## 📊 Estructura de Datos

### Category Response (Backend):
```json
{
  "id": "uuid",
  "name": "Conciertos",
  "description": "Eventos de música en vivo...",
  "slug": "conciertos",
  "icon": "fa-music",
  "color": "#E74C3C",
  "imageUrl": "https://...",
  "metaTitle": "Entradas para Conciertos",
  "metaDescription": "Encuentra y compra...",
  "parentId": null,
  "sortOrder": 0,
  "level": 0,
  "isActive": true,
  "isFeatured": true,
  "eventCount": 25,
  "createdAt": "2025-10-30T10:00:00",
  "updatedAt": "2025-10-30T10:00:00"
}
```

### Category Type (Frontend):
```typescript
interface Category {
  id: string
  name: string
  description: string | null
  slug: string
  icon: string | null
  color: string | null
  imageUrl: string | null
  metaTitle: string | null
  metaDescription: string | null
  parentId: string | null
  sortOrder: number
  level: number
  isActive: boolean
  isFeatured: boolean
  eventCount: number
  createdAt: string
  updatedAt: string
}
```

---

## 🎨 Uso de Categorías en Otras Vistas

### Homepage - Mostrar categorías destacadas:
```tsx
import { getFeaturedCategories } from '@/services/api/categories'

const HomePage = () => {
  const [categories, setCategories] = useState([])
  
  useEffect(() => {
    const load = async () => {
      const featured = await getFeaturedCategories()
      setCategories(featured)
    }
    load()
  }, [])
  
  return (
    <div className="grid grid-cols-3 gap-4">
      {categories.map(cat => (
        <CategoryCard 
          key={cat.id}
          name={cat.name}
          icon={cat.icon}
          color={cat.color}
          eventCount={cat.eventCount}
        />
      ))}
    </div>
  )
}
```

### Filtrar eventos por categoría:
```tsx
import { getEvents } from '@/services/api/events'

const EventList = ({ categorySlug }: { categorySlug?: string }) => {
  const [events, setEvents] = useState([])
  
  useEffect(() => {
    const load = async () => {
      // Si hay slug, obtener categoría y filtrar por ID
      let categoryId = undefined
      if (categorySlug) {
        const category = await getCategoryBySlug(categorySlug)
        categoryId = category.id
      }
      
      const data = await getEvents({ 
        category_id: categoryId,
        page: 1,
        page_size: 10
      })
      setEvents(data.events)
    }
    load()
  }, [categorySlug])
  
  // Render events...
}
```

---

## 🔐 Validación del Backend

El backend valida que `category_id` sea válido:

```python
# En event_service.py
def create_event(self, event_data: EventCreate, organizer_id: UUID):
    # Si se proporciona category_id, verificar que exista
    if event_data.category_id:
        category = self.db.query(EventCategory).filter(
            EventCategory.id == event_data.category_id,
            EventCategory.is_active == True
        ).first()
        
        if not category:
            raise HTTPException(
                status_code=400,
                detail="Categoría no válida o inactiva"
            )
    
    # Crear evento...
```

---

## ✅ Checklist de Integración

### Backend:
- [x] Schema de categorías creado
- [x] Repository con queries
- [x] Service con lógica de negocio
- [x] Router con endpoints
- [x] Integrado en API principal
- [x] Documentación OpenAPI

### Frontend:
- [x] Service API de categorías
- [x] Types TypeScript
- [x] Integración en página crear eventos
- [x] Loading states
- [x] Error handling
- [x] Validación de categoría al crear evento

### Base de Datos:
- [x] Tabla event_categories poblada
- [x] 6 categorías insertadas
- [x] Relaciones configuradas

---

## 🚀 Próximos Pasos

### Opcional - Mejoras:
1. **Caché de categorías** en frontend (React Query, SWR)
2. **Iconos mejorados** - usar librería de iconos real
3. **Colores en UI** - aplicar color de categoría en cards
4. **Imágenes de categoría** - mostrar imageUrl en grid
5. **Subcategorías** - usar parentId y level para jerarquía
6. **Admin panel** - CRUD de categorías

### Upload de Archivos:
- Implementar endpoint de upload para imágenes/videos
- Integrar con S3, Cloudinary, o storage local
- Actualizar página de crear eventos para subir archivos

---

## 📝 Notas Importantes

1. **UUIDs**: La base de datos genera UUIDs automáticamente con `gen_random_uuid()`

2. **Categoría Opcional**: Los eventos pueden crearse sin categoría (category_id es opcional)

3. **Filtros**: La API de eventos soporta filtrado por category_id

4. **Event Count**: El campo `eventCount` se calcula dinámicamente con la relación

5. **Activos**: Por defecto, solo se muestran categorías activas (is_active=true)

---

**¡La integración de categorías está completa y funcionando! 🎉**
