-- Database: ticketify

-- DROP DATABASE IF EXISTS ticketify;

CREATE DATABASE ticketify
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'Spanish_Peru.1252'
    LC_CTYPE = 'Spanish_Peru.1252'
    LOCALE_PROVIDER = 'libc'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;

	SELECT * FROM users;

	SELECT * FROM event_categories;

In Database ticketify

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- El nombre de la tabla ahora es 'event_categories'
INSERT INTO event_categories (
    -- Columnas de ID y principales
    id,
    name,
    description,
    slug,

    -- Atributos de visualización
    icon,
    color,
    image_url,

    -- SEO
    meta_title,
    meta_description,

    -- Jerarquía y orden
    parent_id,
    sort_order,
    level,

    -- Estado
    is_active,
    is_featured
    
    -- Omitimos created_at y updated_at para que usen server_default=func.now()
)
VALUES
(
    gen_random_uuid(), -- Aquí generamos el UUID
    'Conciertos',
    'Eventos de música en vivo y conciertos de todos los géneros.',
    'conciertos',
    '🎵',
    '#E74C3C',
    'https://images.unsplash.com/photo-1470225620780-dba8ba36b745?auto=format&fit=crop&w=800',
    'Entradas para Conciertos',
    'Encuentra y compra entradas para los mejores conciertos en tu ciudad.',
    NULL,       -- parent_id NULL (es raíz)
    0,          -- sort_order
    0,          -- level 0 (es raíz)
    true,
    true
),
(
    gen_random_uuid(),
    'Deportes',
    'Partidos, torneos y eventos deportivos.',
    'deportes',
    'fa-futbol',
    '#3498DB',
    'https://tu-cdn.com/imagenes/deportes.jpg',
    'Entradas para Eventos Deportivos',
    'No te pierdas los partidos de tu equipo favorito. Compra entradas aquí.',
    NULL,
    1,
    0,
    true,
    true
),
(
    gen_random_uuid(),
    'Teatro',
    'Obras de teatro, musicales y artes escénicas.',
    'teatro',
    'fa-theater-masks',
    '#8E44AD',
    'https://tu-cdn.com/imagenes/teatro.jpg',
    'Entradas para Obras de Teatro',
    'Descubre la cartelera de teatro y compra tus entradas.',
    NULL,
    2,
    0,
    true,
    false
),
(
    gen_random_uuid(),
    'Conferencias',
    'Charlas, seminarios y conferencias de industria.',
    'conferencias',
    'fa-chalkboard-teacher',
    '#1ABC9C',
    'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=800',
    'Asiste a Conferencias y Seminarios',
    'Encuentra conferencias sobre tecnología, negocios, ciencia y más.',
    NULL,
    3,
    0,
    true,
    false
),
(
    gen_random_uuid(),
    'Festivales',
    'Festivales de música, comida, arte y cultura.',
    'festivales',
    'fa-glass-cheers',
    '#F1C40F',
    'https://tu-cdn.com/imagenes/festivales.jpg',
    'Entradas para Festivales',
    'Compra tus abonos para los festivales más importantes.',
    NULL,
    4,
    0,
    true,
    true
),
(
    gen_random_uuid(),
    'Otros',
    'Eventos varios y de interés general no clasificados.',
    'otros',
    'fa-ellipsis-h',
    '#95A5A6',
    'https://tu-cdn.com/imagenes/otros.jpg',
    'Otros Eventos',
    'Descubre otros eventos de interés en tu ciudad.',
    NULL,
    5,
    0,
    true,
    false
);

Select * from  event_categories;

Select * from events;

Update event_categories
Set icon = '🎵'
Where slug='conciertos'

Update event_categories
Set icon = '📹'
Where slug='otros'

Update event_categories
Set icon = '⚽'
Where slug='deportes'

Update event_categories
Set icon = '🎭'
Where slug='teatro'

Update event_categories
Set icon = '💻'
Where slug='conferencias'

Update event_categories
Set icon = '🎨'
Where slug='festivales'