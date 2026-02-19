import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet.markercluster';
import { Photo, MapLayer } from '../../types';
import { getMapLayers } from '../../services/api';

// Fix para iconos de Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

interface MapViewProps {
  photos: Photo[];
  selectedPhotoId: number | null;
  onMapMove: (bbox: string) => void;
  onPhotoClick: (photo: Photo) => void;
  centerOnPhoto?: Photo | null;
}

export const MapView: React.FC<MapViewProps> = ({
  photos,
  selectedPhotoId,
  onMapMove,
  onPhotoClick,
  centerOnPhoto,
}) => {
  const mapRef = useRef<L.Map | null>(null);
  const markersLayerRef = useRef<L.LayerGroup | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [layers, setLayers] = useState<MapLayer[]>([]);
  const [currentLayerId, setCurrentLayerId] = useState<number | null>(null);
  const baseLayersRef = useRef<{ [key: number]: L.TileLayer }>({});
  const initializedRef = useRef<boolean>(false);

  // Inicializar mapa
  useEffect(() => {
    if (!containerRef.current || initializedRef.current) return;
    
    initializedRef.current = true;

    // Crear mapa centrado en Zaragoza
    const map = L.map(containerRef.current, {
      center: [41.6488, -0.8891], // Plaza del Pilar
      zoom: 13,
      zoomControl: true,
      minZoom: 3,
      maxZoom: 19,
      preferCanvas: true,
    });

    // Capa base por defecto (OpenStreetMap)
    const defaultLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 19,
      minZoom: 3,
    });
    defaultLayer.addTo(map);

    // Guardar referencia del mapa primero
    mapRef.current = map;

    // Crear un layer group simple para los marcadores (sin clustering por ahora)
    const markersLayer = L.layerGroup();
    markersLayer.addTo(map);
    
    markersLayerRef.current = markersLayer;

    // Cargar capas disponibles
    loadMapLayers();

    // Evento moveend con debounce manual
    let moveTimeout: ReturnType<typeof setTimeout>;
    map.on('moveend', () => {
      clearTimeout(moveTimeout);
      moveTimeout = setTimeout(() => {
        const bounds = map.getBounds();
        const bbox = `${bounds.getWest()},${bounds.getSouth()},${bounds.getEast()},${bounds.getNorth()}`;
        onMapMove(bbox);
      }, 500);
    });

    return () => {
      initializedRef.current = false;
      map.remove();
    };
  }, []);

  // Cargar capas del mapa
  const loadMapLayers = async () => {
    try {
      const layersData = await getMapLayers();
      setLayers(layersData);
      if (layersData.length > 0) {
        setCurrentLayerId(layersData[0].id);
      }
    } catch (error) {
      console.error('Error loading map layers:', error);
    }
  };

  // Actualizar marcadores cuando cambian las fotos
  useEffect(() => {
    if (!mapRef.current || !markersLayerRef.current) return;

    const markersLayer = markersLayerRef.current;
    markersLayer.clearLayers();

    photos.forEach((photo) => {
      const marker = L.marker([photo.lat, photo.lng]);

      // Popup con info de la foto
      const popupContent = `
        <div class="popup-content">
          <img src="${photo.thumb_url}" alt="${photo.title}" onerror="this.src='https://via.placeholder.com/200?text=Sin+imagen'" />
          <h3>${photo.title}</h3>
          <p><strong>Año:</strong> ${photo.year || `${photo.year_from || '?'} - ${photo.year_to || '?'}`}</p>
          ${photo.zone ? `<p><strong>Zona:</strong> ${photo.zone}</p>` : ''}
          <button class="btn btn-primary" onclick="window.handlePhotoClick(${photo.id})">
            Ver detalle completo
          </button>
        </div>
      `;

      marker.bindPopup(popupContent, { maxWidth: 250 });

      // Resaltar marcador si está seleccionado
      if (photo.id === selectedPhotoId) {
        marker.setIcon(
          L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
            shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41],
          })
        );
      }

      markersLayer.addLayer(marker);
    });
  }, [photos, selectedPhotoId]);

  // Centrar mapa en foto seleccionada
  useEffect(() => {
    if (centerOnPhoto && mapRef.current) {
      mapRef.current.setView([centerOnPhoto.lat, centerOnPhoto.lng], 16, {
        animate: true,
      });
    }
  }, [centerOnPhoto]);

  // Exponer función para que el popup pueda llamarla
  useEffect(() => {
    (window as any).handlePhotoClick = (photoId: number) => {
      const photo = photos.find((p) => p.id === photoId);
      if (photo) {
        onPhotoClick(photo);
      }
    };

    return () => {
      delete (window as any).handlePhotoClick;
    };
  }, [photos, onPhotoClick]);

  // Cambiar capa base
  const handleLayerChange = (layerId: number) => {
    if (!mapRef.current) return;

    const map = mapRef.current;
    const layer = layers.find((l) => l.id === layerId);
    if (!layer) return;

    // Remover capa actual
    Object.values(baseLayersRef.current).forEach((l) => map.removeLayer(l));

    // Agregar nueva capa
    if (layer.tile_url_template) {
      if (!baseLayersRef.current[layerId]) {
        baseLayersRef.current[layerId] = L.tileLayer(layer.tile_url_template, {
          attribution: layer.attribution || '',
          minZoom: layer.min_zoom,
          maxZoom: layer.max_zoom,
        });
      }
      baseLayersRef.current[layerId].addTo(map);
    } else {
      // Capa por defecto si no tiene tiles
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: layer.attribution || '&copy; OpenStreetMap',
      }).addTo(map);
    }

    setCurrentLayerId(layerId);
  };

  return (
    <div className="map-container">
      <div ref={containerRef} style={{ height: '100%', width: '100%' }} />

      {/* Control de capas */}
      {layers.length > 0 && (
        <div className="layer-control">
          <h4>🗺️ Capas del mapa</h4>
          {layers.map((layer) => (
            <label key={layer.id}>
              <input
                type="radio"
                name="layer"
                checked={currentLayerId === layer.id}
                onChange={() => handleLayerChange(layer.id)}
              />
              {layer.name}
              {layer.year && ` (${layer.year})`}
              {!layer.tile_url_template && ' 📌'}
            </label>
          ))}
          <p style={{ fontSize: '11px', color: '#999', marginTop: '10px' }}>
            📌 = Capa en desarrollo (placeholder)
          </p>
        </div>
      )}
    </div>
  );
};
