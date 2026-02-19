-- Seeds de ejemplo para Zaragoza Histórica
-- 8 fotografías históricas ficticias con coordenadas reales de Zaragoza

-- Insertar fotos históricas (lat/lng reales de lugares emblemáticos de Zaragoza)
INSERT INTO photos (title, description, year, year_from, year_to, era, zone, lat, lng, image_url, thumb_url, source, author, rights, tags) VALUES
(
    'Plaza del Pilar con el Tranvía',
    'Vista de la Plaza del Pilar con el antiguo tranvía cruzando frente a la Basílica. Se puede observar el pavimento original de la plaza y el tráfico de la época.',
    1935,
    1930,
    1940,
    'Años 30',
    'Casco Histórico',
    41.656648,
    -0.878611,
    '/uploads/plaza-pilar-1935.jpg',
    '/uploads/thumbs/plaza-pilar-1935.jpg',
    'Archivo Municipal de Zaragoza',
    'Fotógrafo desconocido',
    'Dominio público',
    ARRAY['Plaza del Pilar', 'tranvía', 'Basílica', 'transporte']
),
(
    'Puente de Piedra en construcción',
    'Obras de remodelación del histórico Puente de Piedra sobre el río Ebro. Imagen única de las labores de refuerzo estructural.',
    1948,
    NULL,
    NULL,
    'Años 40',
    'Casco Histórico',
    41.658333,
    -0.879722,
    '/uploads/puente-piedra-1948.jpg',
    '/uploads/thumbs/puente-piedra-1948.jpg',
    'Colección particular Familia García',
    'Manuel García López',
    'Copyright herederos',
    ARRAY['Puente de Piedra', 'Ebro', 'obras', 'infraestructura']
),
(
    'Mercado Central en día de mercado',
    'Bullicioso día de mercado en el Mercado Central de Zaragoza. Vendedores y compradores abarrotan los puestos de frutas y verduras.',
    1952,
    1950,
    1955,
    'Años 50',
    'Centro',
    41.652500,
    -0.887222,
    '/uploads/mercado-central-1952.jpg',
    '/uploads/thumbs/mercado-central-1952.jpg',
    'Fototeca del Ayuntamiento',
    'José Galiay',
    'Dominio público',
    ARRAY['Mercado Central', 'comercio', 'vida cotidiana']
),
(
    'Paseo Independencia nevado',
    'El Paseo de la Independencia completamente nevado. Una gran nevada histórica que paralizó la ciudad durante tres días.',
    1963,
    NULL,
    NULL,
    'Años 60',
    'Centro',
    41.650833,
    -0.889444,
    '/uploads/paseo-independencia-1963.jpg',
    '/uploads/thumbs/paseo-independencia-1963.jpg',
    'Archivo Heraldo de Aragón',
    'Archivo Heraldo',
    'Copyright Heraldo de Aragón',
    ARRAY['Paseo Independencia', 'nieve', 'meteorología', 'calle']
),
(
    'Antigua Estación del Norte',
    'Fachada principal de la antigua Estación del Norte, demolida en los años 70. Arquitectura ferroviaria de hierro y cristal característica de la época.',
    1928,
    1925,
    1930,
    'Años 20',
    'Delicias',
    41.647222,
    -0.912778,
    '/uploads/estacion-norte-1928.jpg',
    '/uploads/thumbs/estacion-norte-1928.jpg',
    'Archivo Renfe Patrimonio',
    'Estudio fotográfico Coyne',
    'Dominio público',
    ARRAY['Estación del Norte', 'ferrocarril', 'arquitectura', 'desaparecido']
),
(
    'Feria de Muestras en el Parque Primo de Rivera',
    'Inauguración de la Feria de Muestras en el actual Parque Grande. Carpas y pabellones de las empresas expositoras.',
    1941,
    NULL,
    NULL,
    'Años 40',
    'Parque Grande',
    41.632778,
    -0.902500,
    '/uploads/feria-muestras-1941.jpg',
    '/uploads/thumbs/feria-muestras-1941.jpg',
    'Feria de Zaragoza - Archivo histórico',
    'Reportero Feria',
    'Copyright Feria de Zaragoza',
    ARRAY['Feria de Muestras', 'Parque Grande', 'economía', 'evento']
),
(
    'Universidad y Paraninfo',
    'Vista del edificio Paraninfo de la Universidad de Zaragoza desde la plaza. Estudiantes cruzan la calle hacia las facultades.',
    1968,
    1965,
    1970,
    'Años 60',
    'Universidad',
    41.644167,
    -0.893611,
    '/uploads/paraninfo-1968.jpg',
    '/uploads/thumbs/paraninfo-1968.jpg',
    'Archivo Universidad de Zaragoza',
    'Servicio fotográfico UZ',
    'Universidad de Zaragoza',
    ARRAY['Universidad', 'Paraninfo', 'educación', 'estudiantes']
),
(
    'Aljafería vista desde el exterior',
    'El Palacio de la Aljafería antes de su restauración. Estado previo a las obras de recuperación como sede de las Cortes de Aragón.',
    1975,
    1970,
    1980,
    'Años 70',
    'Romareda',
    41.656944,
    -0.897500,
    '/uploads/aljaferia-1975.jpg',
    '/uploads/thumbs/aljaferia-1975.jpg',
    'Archivo DGA',
    'Servicio patrimonio DGA',
    'Gobierno de Aragón',
    ARRAY['Aljafería', 'palacio', 'patrimonio', 'restauración']
);

-- Insertar capas de mapa (actual + 2 históricas placeholder)
INSERT INTO map_layers (name, year, type, tile_url_template, attribution, min_zoom, max_zoom, is_active, display_order) VALUES
(
    'Mapa Actual',
    NULL,
    'current',
    'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    10,
    19,
    true,
    1
),
(
    'Plano histórico 1935',
    1935,
    'plan',
    NULL, -- PLACEHOLDER: aquí irían tiles de plano escaneado georeferenciado
    'Plano histórico - Archivo Municipal Zaragoza',
    12,
    17,
    true,
    2
),
(
    'Ortofoto histórica 1960',
    1960,
    'ortho',
    NULL, -- PLACEHOLDER: aquí irían tiles de ortofoto histórica
    'Ortofoto histórica - CNIG/IGN',
    12,
    18,
    true,
    3
);

-- Verificar que las geometrías se han creado correctamente
SELECT id, title, year, zone, ST_AsText(geometry) as geom FROM photos;
