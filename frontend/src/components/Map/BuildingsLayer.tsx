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

// Cache cliente por firma (bbox redondeado + zoom + años). Evita refetch en pan corto.
const CLIENT_CACHE_TTL = 60_000; // 1 min
const CLIENT_CACHE_MAX = 32;
const clientCache = new Map<string, { ts: number; data: GeoJSON.FeatureCollection }>();

function cacheKey(
  b: { minLng: number; minLat: number; maxLng: number; maxLat: number },
  zoom: number,
  yearFrom?: number,
  yearTo?: number,
): string {
  const r = (v: number) => v.toFixed(4);
  return `${r(b.minLng)},${r(b.minLat)},${r(b.maxLng)},${r(b.maxLat)}|z${zoom}|${yearFrom ?? ''}|${yearTo ?? ''}`;
}

function buildPopupHtml(props: {
  year_built?: number | null;
  current_use?: string | null;
  cadastral_ref?: string | null;
}): string {
  return `
    <div style="min-width:160px;font-family:system-ui,sans-serif;">
      <strong>${props.year_built ? `Construido en ${props.year_built}` : 'Año desconocido'}</strong>
      ${props.current_use ? `<br><span style="color:#555;">Uso: ${props.current_use}</span>` : ''}
      ${props.cadastral_ref ? `<br><span style="color:#777;font-size:11px;">Ref: ${props.cadastral_ref}</span>` : ''}
    </div>
  `;
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
        // Renderizador canvas (más rápido cuando hay miles de features)
        interactive: true,
      };
    };

    // Popup lazy: se enlaza sólo al hacer click en la feature (evita bindPopup por feature al cargar)
    const onEachFeature = (_feature: GeoJSON.Feature, layer: L.Layer) => {
      const pathLayer = layer as L.Path & {
        bindPopup?: (html: string) => L.Layer;
        openPopup?: () => void;
        on?: (events: Record<string, (e: L.LeafletMouseEvent) => void>) => void;
      };

      pathLayer.on?.({
        click: (e: L.LeafletMouseEvent) => {
          const feature = (e.target as { feature?: GeoJSON.Feature }).feature;
          const props = (feature?.properties || {}) as Parameters<typeof buildPopupHtml>[0];
          L.popup({ autoPan: false })
            .setLatLng(e.latlng)
            .setContent(buildPopupHtml(props))
            .openOn(map);
        },
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
        renderer: L.canvas({ padding: 0.2 }),
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

      const bounds = map.getBounds();
      const bboxParams = {
        minLng: bounds.getWest(),
        minLat: bounds.getSouth(),
        maxLng: bounds.getEast(),
        maxLat: bounds.getNorth(),
      };

      // Cache-hit: pintar sin red
      const key = cacheKey(bboxParams, zoom, yearFrom, yearTo);
      const cached = clientCache.get(key);
      if (cached && Date.now() - cached.ts < CLIENT_CACHE_TTL) {
        if (!layerRef.current) return;
        layerRef.current.clearLayers();
        layerRef.current.addData(cached.data as GeoJSON.GeoJsonObject);
        return;
      }

      if (abortRef.current) abortRef.current.abort();
      abortRef.current = new AbortController();

      try {
        // Límite adaptativo: menos features en zoom bajo → mucho más rápido
        const limit = zoom >= 16 ? 5000 : zoom >= 15 ? 3500 : 2500;
        const data = await fetchBuildingsGeoJSON(
          {
            min_lng: bboxParams.minLng,
            min_lat: bboxParams.minLat,
            max_lng: bboxParams.maxLng,
            max_lat: bboxParams.maxLat,
          },
          zoom,
          yearFrom,
          yearTo,
          limit,
          abortRef.current.signal,
        );

        if (!layerRef.current) return;
        layerRef.current.clearLayers();
        layerRef.current.addData(data as GeoJSON.GeoJsonObject);

        clientCache.set(key, { ts: Date.now(), data: data as GeoJSON.FeatureCollection });
        if (clientCache.size > CLIENT_CACHE_MAX) {
          const firstKey = clientCache.keys().next().value;
          if (firstKey !== undefined) clientCache.delete(firstKey);
        }
      } catch (error) {
        const err = error as Error & { name?: string };
        if (err.name !== 'AbortError') {
          console.error('Error loading buildings layer:', error);
        }
      }
    };

    const debouncedLoad = () => {
      if (timeoutId) clearTimeout(timeoutId);
      // Debounce más corto: percepción más inmediata tras activar capa o pan
      timeoutId = setTimeout(() => {
        void loadBuildings();
      }, 200);
    };

    map.on('moveend', debouncedLoad);
    map.on('zoomend', debouncedLoad);
    // Primera carga inmediata (sin debounce) al montar/activar
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
