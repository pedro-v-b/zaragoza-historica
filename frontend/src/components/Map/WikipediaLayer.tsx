import { useEffect, useRef } from 'react';
import L from 'leaflet';
import { fetchWikipediaArticles, WikipediaArticle } from '../../services/api';

interface WikipediaLayerProps {
  map: L.Map | null;
  visible: boolean;
}

// Icono personalizado de Wikipedia
const wikipediaIcon = L.divIcon({
  className: 'wikipedia-marker',
  html: `<div class="wikipedia-marker-inner">W</div>`,
  iconSize: [28, 28],
  iconAnchor: [14, 14],
  popupAnchor: [0, -16],
});

// Calcular radio en metros entre dos puntos geográficos
function getViewportRadius(map: L.Map): number {
  const center = map.getCenter();
  const bounds = map.getBounds();
  const corner = bounds.getNorthEast();
  const dist = center.distanceTo(corner);
  // Limitar al máximo de la API de Wikipedia (10km)
  return Math.min(Math.round(dist), 10000);
}

function buildPopup(article: WikipediaArticle): string {
  const imgSrc = article.thumbnail || 'https://via.placeholder.com/360x200/f5f0eb/a99e9e?text=Sin+imagen';

  const extractText = article.extract
    ? article.extract.length > 150
      ? article.extract.substring(0, 150) + '...'
      : article.extract
    : '';

  return `
    <div class="popup-content">
      <div class="popup-image-container">
        <img src="${imgSrc}" alt="${article.title}" onerror="this.src='https://via.placeholder.com/360x200/f5f0eb/a99e9e?text=Sin+imagen'" />
      </div>
      <div class="popup-body">
        <h3>${article.title}</h3>
        ${extractText ? `<p class="wiki-popup-extract">${extractText}</p>` : ''}
        <a class="btn btn-primary popup-btn" href="${article.url}" target="_blank" rel="noopener noreferrer">
          Leer en Wikipedia
        </a>
      </div>
    </div>
  `;
}

export default function WikipediaLayer({ map, visible }: WikipediaLayerProps) {
  const layerRef = useRef<L.LayerGroup | null>(null);
  const loadedIdsRef = useRef<Set<number>>(new Set());

  // Crear la capa
  useEffect(() => {
    if (!map) return;

    if (!layerRef.current) {
      layerRef.current = L.layerGroup();
    }

    return () => {
      if (layerRef.current && map.hasLayer(layerRef.current)) {
        map.removeLayer(layerRef.current);
      }
    };
  }, [map]);

  // Toggle visibilidad
  useEffect(() => {
    if (!map || !layerRef.current) return;

    if (visible) {
      if (!map.hasLayer(layerRef.current)) {
        layerRef.current.addTo(map);
      }
    } else if (map.hasLayer(layerRef.current)) {
      map.removeLayer(layerRef.current);
    }
  }, [map, visible]);

  // Cargar artículos dinámicamente al mover/zoom del mapa
  useEffect(() => {
    if (!map || !layerRef.current) return;

    let timeoutId: ReturnType<typeof setTimeout> | null = null;

    const loadArticles = async () => {
      if (!visible) return;

      const center = map.getCenter();
      const radius = getViewportRadius(map);

      try {
        const articles = await fetchWikipediaArticles(
          center.lat,
          center.lng,
          radius,
          500,
        );

        articles.forEach((article) => {
          // No duplicar marcadores ya presentes
          if (loadedIdsRef.current.has(article.pageid)) return;
          loadedIdsRef.current.add(article.pageid);

          const marker = L.marker([article.lat, article.lon], { icon: wikipediaIcon });
          marker.bindPopup(buildPopup(article), {
            maxWidth: 360,
            minWidth: 320,
            className: 'custom-popup',
          });
          layerRef.current!.addLayer(marker);
        });
      } catch (err) {
        console.error('Error loading Wikipedia articles:', err);
      }
    };

    const debouncedLoad = () => {
      if (timeoutId) clearTimeout(timeoutId);
      timeoutId = setTimeout(() => {
        void loadArticles();
      }, 600);
    };

    map.on('moveend', debouncedLoad);
    // Carga inicial
    void loadArticles();

    return () => {
      if (timeoutId) clearTimeout(timeoutId);
      map.off('moveend', debouncedLoad);
    };
  }, [map, visible]);

  return null;
}
