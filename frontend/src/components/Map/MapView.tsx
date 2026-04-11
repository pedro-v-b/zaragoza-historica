import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet.markercluster';
import 'leaflet.markercluster/dist/MarkerCluster.css';
import 'leaflet.markercluster/dist/MarkerCluster.Default.css';
import { Photo } from '../../types';
import BuildingsLayer from './BuildingsLayer';
import BuildingsLegend from './BuildingsLegend';
import WikipediaLayer from './WikipediaLayer';
import MonumentsLayer from './MonumentsLayer';

// Definición de capas históricas WMS
interface HistoricalLayer {
  id: string;
  name: string;
  year: string;
  wmsLayer: string;
  wmsUrl: string;
  attribution: string;
}

// URLs de los servicios WMS del IGN
const WMS_PNOA = 'https://www.ign.es/wms/pnoa-historico';
const WMS_MINUTAS = 'https://www.ign.es/wms/minutas-cartograficas';
const WMS_MTN = 'https://www.ign.es/wms/primera-edicion-mtn';

// Capas con cobertura verificada para Zaragoza
const HISTORICAL_LAYERS: HistoricalLayer[] = [
  // Mapa base moderno
  { id: 'modern', name: 'Mapa Actual', year: '2024', wmsLayer: '', wmsUrl: '', attribution: '' },

  // Ortofotos PNOA con cobertura en Zaragoza
  { id: 'pnoa2015', name: 'PNOA Ortofoto', year: '2015', wmsLayer: 'PNOA2015', wmsUrl: WMS_PNOA, attribution: 'IGN-CNIG' },
  { id: 'pnoa2012', name: 'PNOA Ortofoto', year: '2012', wmsLayer: 'PNOA2012', wmsUrl: WMS_PNOA, attribution: 'IGN-CNIG' },
  { id: 'pnoa2009', name: 'PNOA Ortofoto', year: '2009', wmsLayer: 'PNOA2009', wmsUrl: WMS_PNOA, attribution: 'IGN-CNIG' },
  { id: 'pnoa2006', name: 'PNOA Ortofoto', year: '2006', wmsLayer: 'PNOA2006', wmsUrl: WMS_PNOA, attribution: 'IGN-CNIG' },

  // Vuelos históricos con cobertura en Zaragoza
  { id: 'sigpac', name: 'SIGPAC', year: '1997-2003', wmsLayer: 'SIGPAC', wmsUrl: WMS_PNOA, attribution: 'IGN-CNIG' },
  { id: 'olistat', name: 'OLISTAT', year: '1997-98', wmsLayer: 'OLISTAT', wmsUrl: WMS_PNOA, attribution: 'IGN-CNIG' },
  { id: 'americano', name: 'Vuelo Americano B', year: '1956-57', wmsLayer: 'AMS_1956-1957', wmsUrl: WMS_PNOA, attribution: 'IGN-CNIG' },

  // Cartografía histórica IGN
  { id: 'mtn50', name: 'MTN50 1ª Edición', year: '1915-1960', wmsLayer: 'MTN50', wmsUrl: WMS_MTN, attribution: 'IGN - Primera Edición MTN' },
  { id: 'mtn25', name: 'MTN25 1ª Edición', year: '1935-1960', wmsLayer: 'MTN25', wmsUrl: WMS_MTN, attribution: 'IGN - Primera Edición MTN' },
  { id: 'catastrones', name: 'Catastrones', year: '1870-1950', wmsLayer: 'catastrones', wmsUrl: WMS_MTN, attribution: 'IGN - Catastrones históricos' },
  { id: 'minutas', name: 'Minutas Cartográficas', year: '1870-1920', wmsLayer: 'Minutas', wmsUrl: WMS_MINUTAS, attribution: 'IGN - Minutas Cartográficas' },
];

// Fix para iconos de Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// Icono personalizado para marcadores normales
const defaultIcon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

// Icono para marcador seleccionado
const selectedIcon = L.icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

interface MapViewProps {
  photos: Photo[];
  selectedPhotoId: number | null;
  onMapMove: (bbox: string) => void;
  onPhotoClick: (photo: Photo) => void;
  centerOnPhoto?: Photo | null;
  selectedZone?: string;
  hoveredZone?: string | null;
  onZoneSelect?: (zone: string | null) => void;
  yearFrom?: number;
  yearTo?: number;
}

export const MapView: React.FC<MapViewProps> = ({
  photos,
  selectedPhotoId,
  onMapMove,
  onPhotoClick,
  centerOnPhoto,
  selectedZone,
  hoveredZone,
  onZoneSelect,
  yearFrom,
  yearTo,
}) => {
  const mapRef = useRef<L.Map | null>(null);
  const markersLayerRef = useRef<L.MarkerClusterGroup | null>(null);
  const markersByIdRef = useRef<Map<number, L.Marker>>(new Map());
  const barriosLayerRef = useRef<L.GeoJSON | null>(null);
  const barriosDataRef = useRef<any>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [currentLayerId, setCurrentLayerId] = useState<string>('modern');
  const [showBarrios, setShowBarrios] = useState<boolean>(false);
  const [showBuildings, setShowBuildings] = useState<boolean>(false);
  const [showWikipedia, setShowWikipedia] = useState<boolean>(false);
  const [showMonuments, setShowMonuments] = useState<boolean>(false);
  const [showLayerControl, setShowLayerControl] = useState<boolean>(false);
  const [mapInstance, setMapInstance] = useState<L.Map | null>(null);
  const baseLayerRef = useRef<L.TileLayer | L.TileLayer.WMS | null>(null);
  const modernLayerRef = useRef<L.TileLayer | null>(null);
  const initializedRef = useRef<boolean>(false);

  // Refs para acceder a valores actuales en callbacks
  const onZoneSelectRef = useRef(onZoneSelect);
  const selectedZoneRef = useRef(selectedZone);

  // Actualizar refs cuando cambian los props
  useEffect(() => {
    onZoneSelectRef.current = onZoneSelect;
    selectedZoneRef.current = selectedZone;
  }, [onZoneSelect, selectedZone]);

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

    // Capa base moderna (CartoDB Positron)
    const modernLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
      maxZoom: 19,
      minZoom: 3,
    });
    modernLayer.addTo(map);
    modernLayerRef.current = modernLayer;
    baseLayerRef.current = modernLayer;

    // Guardar referencia del mapa primero
    mapRef.current = map;
    setMapInstance(map);

    // Crear MarkerClusterGroup con configuracion personalizada
    const markersLayer = (L as any).markerClusterGroup({
      chunkedLoading: true,
      spiderfyOnMaxZoom: true,
      showCoverageOnHover: false,
      zoomToBoundsOnClick: true,
      maxClusterRadius: 60, 
      disableClusteringAtZoom: 20, // Nunca desactivar clustering dentro del rango de zoom normal
      iconCreateFunction: (cluster: any) => {
        const count = cluster.getChildCount();
        let size = 'small';
        let dimension = 36;

        if (count >= 100) {
          size = 'large';
          dimension = 50;
        } else if (count >= 10) {
          size = 'medium';
          dimension = 42;
        }

        return L.divIcon({
          html: `<div class="cluster-inner">${count}</div>`,
          className: `marker-cluster marker-cluster-${size}`,
          iconSize: L.point(dimension, dimension),
        });
      },
    });
    markersLayer.addTo(map);

    markersLayerRef.current = markersLayer;

    // Cargar y mostrar barrios de Zaragoza
    loadBarrios();

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

    // Detectar cambios de tamaño del contenedor (ej: al colapsar sidebars)
    const resizeObserver = new ResizeObserver(() => {
      map.invalidateSize({ animate: false });
    });
    resizeObserver.observe(containerRef.current);

    return () => {
      resizeObserver.disconnect();
      initializedRef.current = false;
      setMapInstance(null);
      map.remove();
    };
  }, []);

  // Obtener estilo del barrio segun estado
  const getBarrioStyle = (featureName: string, isHovered: boolean, isSelected: boolean) => {
    if (isSelected) {
      return {
        color: '#5A8A9F',
        weight: 3,
        opacity: 1,
        fillColor: '#7CA5B8',
        fillOpacity: 0.4,
      };
    }
    if (isHovered) {
      return {
        color: '#5A8A9F',
        weight: 3,
        opacity: 1,
        fillColor: '#7CA5B8',
        fillOpacity: 0.35,
      };
    }
    // Si hay una zona seleccionada, atenuar las demas
    if (selectedZone && featureName !== selectedZone) {
      return {
        color: '#B8C4CE',
        weight: 1,
        opacity: 0.4,
        fillColor: '#E2E8ED',
        fillOpacity: 0.1,
      };
    }
    return {
      color: '#7CA5B8',
      weight: 2,
      opacity: 0.8,
      fillColor: '#B8D4E3',
      fillOpacity: 0.15,
    };
  };

  // Cargar barrios de Zaragoza
  const loadBarrios = async () => {
    try {
      const response = await fetch('/barrios-zaragoza-wgs84.geojson');
      const geojson = await response.json();
      barriosDataRef.current = geojson;

      const barriosLayer = L.geoJSON(geojson, {
        style: (feature) => {
          const name = feature?.properties?.name || feature?.properties?.JUNTA || '';
          return getBarrioStyle(name, false, false);
        },
        onEachFeature: (feature, layer) => {
          const name = feature.properties?.name || feature.properties?.JUNTA || 'Desconocido';
          layer.bindTooltip(name, {
            permanent: false,
            direction: 'center',
            className: 'barrio-tooltip',
          });

          // Guardar el nombre en el layer para referencia
          (layer as any).barrioName = name;

          layer.on({
            mouseover: (e) => {
              const target = e.target;
              if (!selectedZone || target.barrioName === selectedZone) {
                target.setStyle(getBarrioStyle(name, true, false));
                target.bringToFront();
              }
            },
            mouseout: (e) => {
              const target = e.target;
              const isSelected = target.barrioName === selectedZone;
              target.setStyle(getBarrioStyle(target.barrioName, false, isSelected));
            },
            click: (e) => {
              L.DomEvent.stopPropagation(e);
              const clickedZone = (e.target as any).barrioName;
              // Si ya está seleccionado, deseleccionar
              if (selectedZoneRef.current === clickedZone) {
                onZoneSelectRef.current?.(null);
              } else {
                onZoneSelectRef.current?.(clickedZone);
              }
            },
          });
        },
      });

      barriosLayerRef.current = barriosLayer;
      // Solo añadir al mapa si showBarrios está activo (por defecto no lo está)
    } catch (error) {
      console.error('Error loading barrios:', error);
    }
  };


  // Actualizar marcadores cuando cambian las fotos
  useEffect(() => {
    if (!mapRef.current || !markersLayerRef.current) return;

    const markersLayer = markersLayerRef.current;
    markersLayer.clearLayers();
    markersByIdRef.current.clear();

    const newMarkers: L.Marker[] = [];

    photos.forEach((photo) => {
      // Validar coordenadas antes de crear marcador
      if (isNaN(photo.lat) || isNaN(photo.lng)) {
        return;
      }

      // Usar icono seleccionado o normal
      const icon = photo.id === selectedPhotoId ? selectedIcon : defaultIcon;
      const marker = L.marker([photo.lat, photo.lng], { icon });
      markersByIdRef.current.set(photo.id, marker);

      // Popup mejorado con estilo mas limpio (360px ancho, 200px imagen)
      const popupContent = `
        <div class="popup-content">
          <div class="popup-image-container" onclick="window.handlePhotoClick(${photo.id})" style="cursor:pointer">
            <img src="${photo.thumb_url}" alt="${photo.title}" onerror="this.src='https://via.placeholder.com/360x200/f5f0eb/a99e9e?text=Sin+imagen'" />
          </div>
          <div class="popup-body">
            <h3>${photo.title}</h3>
            <button class="btn btn-primary popup-btn" onclick="window.handlePhotoClick(${photo.id})">
              Ver detalle
            </button>
          </div>
        </div>
      `;

      marker.bindPopup(popupContent, {
        maxWidth: 360,
        minWidth: 320,
        className: 'custom-popup',
      });

      newMarkers.push(marker);
    });
    
    markersLayer.addLayers(newMarkers);
  }, [photos, selectedPhotoId]);

  // Centrar mapa en foto seleccionada y abrir su popup (como si se hubiera
  // hecho click directamente sobre el marcador). Si esta dentro de un cluster,
  // MarkerClusterGroup.zoomToShowLayer() se encarga de expandirlo primero.
  useEffect(() => {
    if (!centerOnPhoto || !mapRef.current) return;
    const marker = markersByIdRef.current.get(centerOnPhoto.id);
    const markersLayer = markersLayerRef.current;
    if (marker && markersLayer) {
      markersLayer.zoomToShowLayer(marker, () => {
        marker.openPopup();
      });
    } else {
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

  // Toggle visibilidad de barrios
  useEffect(() => {
    if (!mapRef.current || !barriosLayerRef.current) return;

    if (showBarrios) {
      barriosLayerRef.current.addTo(mapRef.current);
    } else {
      mapRef.current.removeLayer(barriosLayerRef.current);
    }
  }, [showBarrios]);

  // Actualizar estilos cuando cambia hoveredZone o selectedZone
  useEffect(() => {
    if (!barriosLayerRef.current) return;

    barriosLayerRef.current.eachLayer((layer: any) => {
      const name = layer.barrioName;
      if (!name) return;

      const isHovered = name === hoveredZone;
      const isSelected = name === selectedZone;

      layer.setStyle(getBarrioStyle(name, isHovered, isSelected));

      // Traer al frente si esta seleccionado o en hover
      if (isHovered || isSelected) {
        layer.bringToFront();
      }
    });
  }, [hoveredZone, selectedZone]);

  // Centrar mapa en barrio seleccionado
  useEffect(() => {
    if (!mapRef.current || !barriosLayerRef.current || !selectedZone) return;

    barriosLayerRef.current.eachLayer((layer: any) => {
      if (layer.barrioName === selectedZone) {
        const bounds = layer.getBounds();
        mapRef.current?.fitBounds(bounds, { padding: [50, 50], maxZoom: 15 });
      }
    });
  }, [selectedZone]);

  // Cambiar capa base (moderna o histórica WMS)
  const handleLayerChange = (layerId: string) => {
    if (!mapRef.current) return;

    const map = mapRef.current;
    const layer = HISTORICAL_LAYERS.find((l) => l.id === layerId);
    if (!layer) return;

    // Remover capa actual
    if (baseLayerRef.current) {
      map.removeLayer(baseLayerRef.current);
    }

    // Agregar nueva capa
    if (layerId === 'modern') {
      // Capa moderna (CartoDB Positron)
      if (!modernLayerRef.current) {
        modernLayerRef.current = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
          maxZoom: 19,
          minZoom: 3,
        });
      }
      modernLayerRef.current.addTo(map);
      baseLayerRef.current = modernLayerRef.current;
    } else {
      // Capa histórica WMS (IGN)
      const wmsLayer = L.tileLayer.wms(layer.wmsUrl, {
        layers: layer.wmsLayer,
        format: 'image/png',
        transparent: true,
        attribution: `&copy; <a href="https://www.ign.es">${layer.attribution}</a>`,
        maxZoom: 19,
        minZoom: 8,
      });
      wmsLayer.addTo(map);
      baseLayerRef.current = wmsLayer;
    }

    setCurrentLayerId(layerId);
  };

  return (
    <div className="map-container">
      <div ref={containerRef} style={{ height: '100%', width: '100%' }} />

      {/* Botón para abrir/cerrar control de capas */}
      <button
        className={`layer-control-toggle ${showLayerControl ? 'active' : ''}`}
        onClick={() => setShowLayerControl(!showLayerControl)}
        title={showLayerControl ? 'Cerrar capas' : 'Capas del mapa'}
      >
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M10 2L2 6L10 10L18 6L10 2Z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"/>
          <path d="M2 10L10 14L18 10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M2 14L10 18L18 14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </button>

      {/* Overlay para cerrar al hacer clic fuera */}
      {showLayerControl && (
        <div
          className="layer-control-overlay"
          onClick={() => setShowLayerControl(false)}
        />
      )}

      {/* Control de capas */}
      {showLayerControl && (
        <div className="layer-control">
          <div className="layer-control-header">
            <h4>Capas del mapa</h4>
            <button
              className="layer-control-close"
              onClick={() => setShowLayerControl(false)}
              title="Cerrar"
            >
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M1 1L13 13M1 13L13 1" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
            </button>
          </div>

          {/* Toggle de barrios */}
          <div className="layer-section">
            <label className={`layer-toggle ${showBarrios ? 'active' : ''}`}>
              <input
                type="checkbox"
                checked={showBarrios}
                onChange={(e) => setShowBarrios(e.target.checked)}
              />
              <span className="layer-name">
                Límites de barrios
              </span>
            </label>
            <label className={`layer-toggle ${showBuildings ? 'active' : ''}`}>
              <input
                type="checkbox"
                checked={showBuildings}
                onChange={(e) => setShowBuildings(e.target.checked)}
              />
              <span className="layer-name">
                Edificios (Catastro)
              </span>
            </label>
            <label className={`layer-toggle ${showWikipedia ? 'active' : ''}`}>
              <input
                type="checkbox"
                checked={showWikipedia}
                onChange={(e) => setShowWikipedia(e.target.checked)}
              />
              <span className="layer-name">
                Wikipedia
              </span>
            </label>
            <label className={`layer-toggle ${showMonuments ? 'active' : ''}`}>
              <input
                type="checkbox"
                checked={showMonuments}
                onChange={(e) => setShowMonuments(e.target.checked)}
              />
              <span className="layer-name">
                Monumentos y patrimonio
              </span>
            </label>
          </div>

          {/* Capas históricas */}
          <div className="layer-section">
            <span className="layer-section-title">Capas históricas</span>
            {HISTORICAL_LAYERS.map((layer) => (
              <label key={layer.id} className={currentLayerId === layer.id ? 'active' : ''}>
                <input
                  type="radio"
                  name="layer"
                  checked={currentLayerId === layer.id}
                  onChange={() => handleLayerChange(layer.id)}
                />
                <span className="layer-name">
                  {layer.name}
                  <span className="layer-year">{layer.year}</span>
                </span>
              </label>
            ))}
          </div>
        </div>
      )}

      <BuildingsLayer
        map={mapInstance}
        visible={showBuildings}
        yearFrom={yearFrom}
        yearTo={yearTo}
      />
      <BuildingsLegend visible={showBuildings} />
      <WikipediaLayer
        map={mapInstance}
        visible={showWikipedia}
      />
      <MonumentsLayer
        map={mapInstance}
        visible={showMonuments}
      />
    </div>
  );
};
