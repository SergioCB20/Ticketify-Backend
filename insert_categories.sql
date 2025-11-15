-- =====================================================
-- SCRIPT PARA INSERTAR CATEGORÍAS CON ICONOS
-- Ejecutar en PostgreSQL (pgAdmin, psql, etc.)
-- =====================================================

-- Asegurarse de que la extensión UUID esté habilitada
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Opción 1: Limpiar categorías existentes (DESCOMENTAR SI QUIERES EMPEZAR DE CERO)
-- DELETE FROM event_categories;

-- Opción 2: Insertar o actualizar categorías con iconos
INSERT INTO event_categories (
    id, 
    name, 
    description, 
    slug, 
    icon, 
    color, 
    sort_order, 
    level,
    is_active, 
    is_featured,
    created_at,
    updated_at
) VALUES
    -- Conciertos
    (
        uuid_generate_v4(), 
        'Conciertos', 
        'Eventos musicales y conciertos en vivo', 
        'conciertos', 
        '🎵', 
        '#FF6B6B', 
        1, 
        0,
        true, 
        true,
        CURRENT_TIMESTAMP,
        CURRENT_TIMESTAMP
    ),
    -- Deportes
    (
        uuid_generate_v4(), 
        'Deportes', 
        'Eventos deportivos y competencias', 
        'deportes', 
        '⚽', 
        '#4ECDC4', 
        2, 
        0,
        true, 
        true,
        CURRENT_TIMESTAMP,
        CURRENT_TIMESTAMP
    ),
    -- Teatro
    (
        uuid_generate_v4(), 
        'Teatro', 
        'Obras de teatro y espectáculos', 
        'teatro', 
        '🎭', 
        '#95E1D3', 
        3, 
        0,
        true, 
        true,
        CURRENT_TIMESTAMP,
        CURRENT_TIMESTAMP
    ),
    -- Conferencias
    (
        uuid_generate_v4(), 
        'Conferencias', 
        'Conferencias y eventos profesionales', 
        'conferencias', 
        '📊', 
        '#F38181', 
        4, 
        0,
        true, 
        false,
        CURRENT_TIMESTAMP,
        CURRENT_TIMESTAMP
    ),
    -- Festivales
    (
        uuid_generate_v4(), 
        'Festivales', 
        'Festivales y eventos culturales', 
        'festivales', 
        '🎉', 
        '#AA96DA', 
        5, 
        0,
        true, 
        true,
        CURRENT_TIMESTAMP,
        CURRENT_TIMESTAMP
    ),
    -- Arte
    (
        uuid_generate_v4(), 
        'Arte', 
        'Exposiciones y eventos artísticos', 
        'arte', 
        '🎨', 
        '#FCBAD3', 
        6, 
        0,
        true, 
        false,
        CURRENT_TIMESTAMP,
        CURRENT_TIMESTAMP
    ),
    -- Comedia
    (
        uuid_generate_v4(), 
        'Comedia', 
        'Shows de comedia y stand-up', 
        'comedia', 
        '😄', 
        '#FFE66D', 
        7, 
        0,
        true, 
        false,
        CURRENT_TIMESTAMP,
        CURRENT_TIMESTAMP
    ),
    -- Familia
    (
        uuid_generate_v4(), 
        'Familia', 
        'Eventos familiares y para niños', 
        'familia', 
        '👨‍👩‍👧‍👦', 
        '#A8E6CF', 
        8, 
        0,
        true, 
        false,
        CURRENT_TIMESTAMP,
        CURRENT_TIMESTAMP
    )
ON CONFLICT (slug) DO UPDATE SET
    icon = EXCLUDED.icon,
    color = EXCLUDED.color,
    description = EXCLUDED.description,
    is_active = EXCLUDED.is_active,
    is_featured = EXCLUDED.is_featured,
    sort_order = EXCLUDED.sort_order,
    updated_at = CURRENT_TIMESTAMP;

-- Verificar que las categorías se insertaron correctamente
SELECT 
    name, 
    icon, 
    slug, 
    color,
    is_active, 
    is_featured,
    sort_order
FROM event_categories 
ORDER BY sort_order;

-- Contar categorías insertadas
SELECT COUNT(*) as total_categorias FROM event_categories;

-- Ver categorías activas y destacadas
SELECT 
    'Categorías Activas' as tipo,
    COUNT(*) as cantidad
FROM event_categories 
WHERE is_active = true
UNION ALL
SELECT 
    'Categorías Destacadas' as tipo,
    COUNT(*) as cantidad
FROM event_categories 
WHERE is_featured = true;
