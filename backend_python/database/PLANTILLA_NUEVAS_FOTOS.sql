-- Plantilla para añadir nuevas fotos históricas de Zaragoza
-- Copia este bloque y modifica los datos para cada foto

-- IMPORTANTE: Para obtener coordenadas:
-- 1. Ve a Google Maps
-- 2. Click derecho en el lugar exacto
-- 3. Click en las coordenadas que aparecen
-- 4. Se copiarán en formato: latitud, longitud
-- Ejemplo: 41.656648, -0.878611

-- ESTRUCTURA:
INSERT INTO photos (
    title,              -- Título de la foto
    description,        -- Descripción detallada
    year,              -- Año exacto (o NULL si usas year_from/year_to)
    year_from,         -- Año aproximado desde (o NULL si usas year)
    year_to,           -- Año aproximado hasta (o NULL si usas year)
    era,               -- Época: 'Años 20', 'Años 30', 'Años 50', 'Años 70'
    zone,              -- Zona: 'Centro', 'Casco Histórico', 'Delicias', 'Universidad', etc.
    lat,               -- Latitud (ejemplo: 41.656648)
    lng,               -- Longitud (ejemplo: -0.878611)
    image_url,         -- Ruta a imagen completa
    thumb_url,         -- Ruta a miniatura
    source,            -- Fuente de la imagen
    author,            -- Autor/fotógrafo
    rights,            -- Derechos de autor
    tags               -- Etiquetas como ARRAY
) VALUES (
    'Plaza del Pilar en los años 40',
    'Vista panorámica de la Plaza del Pilar con la Basílica al fondo y el ayuntamiento a la izquierda',
    1945,              -- Año exacto
    NULL,              -- No usar year_from si tienes year
    NULL,              -- No usar year_to si tienes year
    'Años 40',
    'Centro',
    41.656648,         -- LAT: Cambia esto por tu coordenada
    -0.878611,         -- LNG: Cambia esto por tu coordenada
    '/uploads/plaza_pilar_1945.jpg',
    '/uploads/thumbs/plaza_pilar_1945.jpg',
    'Archivo Municipal de Zaragoza',
    'Desconocido',
    'Dominio público',
    ARRAY['Plaza del Pilar', 'Basílica', 'Centro histórico', 'años 40']
);

-- EJEMPLO 2: Con rango de años (cuando no sabes el año exacto)
INSERT INTO photos (
    title,
    description,
    year,
    year_from,
    year_to,
    era,
    zone,
    lat,
    lng,
    image_url,
    thumb_url,
    source,
    author,
    rights,
    tags
) VALUES (
    'Mercado Central',
    'El Mercado Central en día de mercado con gran afluencia de público',
    NULL,              -- NULL porque usamos rango
    1930,              -- Aproximadamente entre 1930-1940
    1940,
    'Años 30',
    'Centro',
    41.657932,
    -0.879471,
    '/uploads/mercado_central.jpg',
    '/uploads/thumbs/mercado_central.jpg',
    'Colección particular',
    'Anónimo',
    'Uso educativo',
    ARRAY['Mercado Central', 'comercio', 'vida cotidiana']
);

-- EJEMPLO 3: Con coordenadas de Google Maps
-- 1. Ve a: https://www.google.com/maps/@41.6488226,-0.8890853,15z
-- 2. Click derecho en el punto exacto donde se tomó la foto
-- 3. Click en las coordenadas
-- 4. Pégalas aquí:

INSERT INTO photos (
    title,
    description,
    year,
    year_from,
    year_to,
    era,
    zone,
    lat,
    lng,
    image_url,
    thumb_url,
    source,
    author,
    rights,
    tags
) VALUES (
    'TU TÍTULO AQUÍ',
    'TU DESCRIPCIÓN AQUÍ',
    1950,
    NULL,
    NULL,
    'Años 50',
    'Centro',
    41.XXXXXX,  -- 👈 Pega aquí la latitud de Google Maps
    -0.XXXXXX,  -- 👈 Pega aquí la longitud de Google Maps
    '/uploads/tu_imagen.jpg',
    '/uploads/thumbs/tu_imagen.jpg',
    'Tu fuente',
    'Autor',
    'Derechos',
    ARRAY['tag1', 'tag2', 'tag3']
);
