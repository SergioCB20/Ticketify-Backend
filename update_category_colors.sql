-- Script SQL para actualizar los colores de las categorías
-- Ejecutar este script en PostgreSQL

-- Actualizar colores de categorías con colores HEX de Tailwind CSS

UPDATE event_categories 
SET color = '#8B5CF6', updated_at = NOW() 
WHERE slug = 'arte-cultura';
-- Arte & Cultura: purple-500

UPDATE event_categories 
SET color = '#10B981', updated_at = NOW() 
WHERE slug = 'ayuda-social';
-- Ayuda Social: emerald-500

UPDATE event_categories 
SET color = '#EC4899', updated_at = NOW() 
WHERE slug = 'cine';
-- Cine: pink-500

UPDATE event_categories 
SET color = '#F59E0B', updated_at = NOW() 
WHERE slug = 'comidas-bebidas';
-- Comidas & Bebidas: amber-500

UPDATE event_categories 
SET color = '#EF4444', updated_at = NOW() 
WHERE slug = 'conciertos';
-- Conciertos: red-500

UPDATE event_categories 
SET color = '#06B6D4', updated_at = NOW() 
WHERE slug = 'cursos-talleres';
-- Cursos y talleres: cyan-500

UPDATE event_categories 
SET color = '#3B82F6', updated_at = NOW() 
WHERE slug = 'deportes';
-- Deportes: blue-500

UPDATE event_categories 
SET color = '#F43F5E', updated_at = NOW() 
WHERE slug = 'donacion';
-- Donación: rose-500

UPDATE event_categories 
SET color = '#6366F1', updated_at = NOW() 
WHERE slug = 'entretenimiento';
-- Entretenimiento: indigo-500

UPDATE event_categories 
SET color = '#EAB308', updated_at = NOW() 
WHERE slug = 'festivales';
-- Festivales: yellow-500

-- Verificar los cambios
SELECT id, name, slug, icon, color, updated_at 
FROM event_categories 
ORDER BY sort_order;
