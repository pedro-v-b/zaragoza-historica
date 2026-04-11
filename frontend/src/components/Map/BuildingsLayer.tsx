import { useEffect, useRef } from 'react';
import L from 'leaflet';
import { fetchBuildingsGeoJSON } from '../../services/api';
import { getColorForDecade } from '../../utils/buildingColors';

interface BuildingsLayerProps {
  map: L.Map | null;
  visible: boolean;
  yearFrom?: number;
  yearTo?: number;
}

export default function BuildingsLayer({
  map,
  visible,
  yearFrom,
  yearTo,
}: BuildingsLayerProps) {
  const layerRef = useRef<L.GeoJSON | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    if (!map) return;

    const styleFeature = (feature?: GeoJSON.Feature): L.PathOptions => {
      const props = (feature?.properties || {}) as { decade?: number | null };
      return {
        fillColor: getColorForDecade(props.decade),
        fillOpacity: 0.65,
        color: '#2f2f2f',
        weight: 0.4,
        opacity: 0.75,
      };
    };

    const onEachFeature = (feature: GeoJSON.Feature, layer: L.Layer) => {
      const props = (feature.properties || {}) as {
        year_built?: number | null;
        current_use?: string | null;
        cadastral_ref?: string | null;
      };
      const popup = `
        <div style="min-width:160px;font-family:system-ui,sans-serif;">
          <strong>${props.year_built ? `Construido en ${props.year_built}` : 'Año desconocido'}</strong>
          ${props.current_use ? `<br><span style="color:#555;">Uso: ${props.current_use}</span>` : ''}
          ${props.cadastral_ref ? `<br><span style="color:#777;font-size:11px;">Ref: ${props.cadastral_ref}</span>` : ''}
        </div>
      `;

      const pathLayer = layer as L.Path;
      if ('bindPopup' in pathLayer) {
        (pathLayer as L.Path & { bindPopup: (html: string) => void }).bindPopup(popup);
      }

      pathLayer.on?.({
        mouseover: (e: L.LeafletMouseEvent) => {
          const target = e.target as L.Path;
          target.setStyle({ weight: 1.2, color: '#ffffff', fillOpacity: 0.85 });
        },
        mouseout: (e: L.LeafletMouseEvent) => {
          if (layerRef.current) {
            layerRef.current.resetStyle(e.target as L.Path);
          }
        },
      });
    };

    if (!layerRef.current) {
      layerRef.current = L.geoJSON(undefined, {
        style: styleFeature,
        onEachFeature,
      });
    }

    return () => {
      if (abortRef.current) {
        abortRef.current.abort();
        abortRef.current = null;
      }
      if (layerRef.current && map.hasLayer(layerRef.current)) {
        map.removeLayer(layerRef.current);
      }
    };
  }, [map]);

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

  useEffect(() => {
    if (!map || !layerRef.current) return;

    let timeoutId: ReturnType<typeof setTimeout> | null = null;

    const loadBuildings = async () => {
      if (!visible) {
        layerRef.current?.clearLayers();
        return;
      }

      const zoom = map.getZoom();
      if (zoom < 14) {
        layerRef.current?.clearLayers();
        return;
      }

      if (abortRef.current) abortRef.current.abort();
      abortRef.current = new AbortController();

      try {
        const bounds = map.getBounds();
        const data = await fetchBuildingsGeoJSON(
          {
            min_lng: bounds.getWest(),
            min_lat: bounds.getSouth(),
            max_lng: bounds.getEast(),
            max_lat: bounds.getNorth(),
          },
          zoom,
          yearFrom,
          yearTo,
          5000,
          abortRef.current.signal
        );

        if (!layerRef.current) return;
        layerRef.current.clearLayers();
        layerRef.current.addData(data as GeoJSON.GeoJsonObject);
      } catch (error) {
        const err = error as Error & { name?: string };
        if (err.name !== 'AbortError') {
          console.error('Error loading buildings layer:', error);
        }
      }
    };

    const debouncedLoad = () => {
      if (timeoutId) clearTimeout(timeoutId);
      timeoutId = setTimeout(() => {
        void loadBuildings();
      }, 500);
    };

    map.on('moveend', debouncedLoad);
    map.on('zoomend', debouncedLoad);
    void loadBuildings();

    return () => {
      if (timeoutId) clearTimeout(timeoutId);
      map.off('moveend', debouncedLoad);
      map.off('zoomend', debouncedLoad);
      if (abortRef.current) {
        abortRef.current.abort();
        abortRef.current = null;
      }
    };
  }, [map, visible, yearFrom, yearTo]);

  return null;
}
