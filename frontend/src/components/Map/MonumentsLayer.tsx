import { useEffect, useRef } from 'react';
import L from 'leaflet';
import { fetchMonuments, Monument } from '../../services/api';

interface MonumentsLayerProps {
  map: L.Map | null;
  visible: boolean;
}

const monumentIcon = L.divIcon({
  className: 'monument-marker',
  html: `<div class="monument-marker-inner">
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 2L3 7V22H21V7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
      <path d="M9 22V12H15V22" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
    </svg>
  </div>`,
  iconSize: [28, 28],
  iconAnchor: [14, 14],
  popupAnchor: [0, -16],
});

function buildPopup(m: Monument): string {
  const imgSrc = m.image || 'https://via.placeholder.com/360x200/f5f0eb/a99e9e?text=Sin+imagen';

  const estiloBadge = m.estilo
    ? `<span class="monument-badge">${m.estilo}</span>`
    : '';
  const datacionBadge = m.datacion
    ? `<span class="monument-badge monument-badge-date">${m.datacion}</span>`
    : '';

  const addressLine = m.address
    ? `<p class="monument-address">${m.address}</p>`
    : '';

  const linkBtn = m.url
    ? `<a class="btn btn-primary popup-btn" href="${m.url}" target="_blank" rel="noopener noreferrer">Ver en Zaragoza.es</a>`
    : '';

  return `
    <div class="popup-content">
      <div class="popup-image-container">
        <img src="${imgSrc}" alt="${m.title}" onerror="this.src='https://via.placeholder.com/360x200/f5f0eb/a99e9e?text=Sin+imagen'" />
      </div>
      <div class="popup-body">
        <h3>${m.title}</h3>
        <div class="monument-badges">${estiloBadge}${datacionBadge}</div>
        ${addressLine}
        ${linkBtn}
      </div>
    </div>
  `;
}

export default function MonumentsLayer({ map, visible }: MonumentsLayerProps) {
  const layerRef = useRef<L.LayerGroup | null>(null);
  const loadedRef = useRef(false);

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

  // Cargar monumentos una sola vez (son 179, caben todos en una llamada)
  useEffect(() => {
    if (!visible || loadedRef.current || !layerRef.current) return;
    loadedRef.current = true;

    fetchMonuments()
      .then((monuments) => {
        if (!layerRef.current) return;
        monuments.forEach((m) => {
          const marker = L.marker([m.lat, m.lon], { icon: monumentIcon });
          marker.bindPopup(buildPopup(m), {
            maxWidth: 360,
            minWidth: 320,
            className: 'custom-popup',
          });
          layerRef.current!.addLayer(marker);
        });
      })
      .catch((err) => console.error('Error loading monuments:', err));
  }, [visible]);

  return null;
}
