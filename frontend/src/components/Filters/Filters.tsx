import React, { useState, useEffect } from 'react';
import { FilterMetadata } from '../../types';
import { getFilterMetadata } from '../../services/api';

interface FiltersProps {
  onFilterChange: (filters: {
    yearFrom?: number;
    yearTo?: number;
    era?: string;
    zone?: string;
    q?: string;
    onlyInViewport: boolean;
  }) => void;
}

export const Filters: React.FC<FiltersProps> = ({ onFilterChange }) => {
  const [metadata, setMetadata] = useState<FilterMetadata | null>(null);
  const [yearFrom, setYearFrom] = useState<string>('');
  const [yearTo, setYearTo] = useState<string>('');
  const [era, setEra] = useState<string>('');
  const [zone, setZone] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [onlyInViewport, setOnlyInViewport] = useState<boolean>(false);

  useEffect(() => {
    loadMetadata();
  }, []);

  const loadMetadata = async () => {
    try {
      const data = await getFilterMetadata();
      setMetadata(data);
    } catch (error) {
      console.error('Error loading filter metadata:', error);
    }
  };

  const handleApplyFilters = () => {
    onFilterChange({
      yearFrom: yearFrom ? parseInt(yearFrom, 10) : undefined,
      yearTo: yearTo ? parseInt(yearTo, 10) : undefined,
      era: era || undefined,
      zone: zone || undefined,
      q: searchQuery || undefined,
      onlyInViewport,
    });
  };

  const handleResetFilters = () => {
    setYearFrom('');
    setYearTo('');
    setEra('');
    setZone('');
    setSearchQuery('');
    setOnlyInViewport(false);
    onFilterChange({ onlyInViewport: false });
  };

  return (
    <div className="filters-panel">
      {/* Búsqueda de texto */}
      <div className="filter-section">
        <h3>Búsqueda</h3>
        <input
          type="text"
          placeholder="Buscar en título, descripción o tags..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleApplyFilters()}
        />
      </div>

      {/* Filtro por año */}
      <div className="filter-section">
        <h3>Rango de años</h3>
        {metadata && (
          <p style={{ fontSize: '12px', color: '#999', marginBottom: '10px' }}>
            Disponible: {metadata.yearRange.min} - {metadata.yearRange.max}
          </p>
        )}
        <div className="year-inputs">
          <div>
            <label>Desde</label>
            <input
              type="number"
              placeholder={metadata?.yearRange.min.toString()}
              value={yearFrom}
              onChange={(e) => setYearFrom(e.target.value)}
              min={metadata?.yearRange.min}
              max={metadata?.yearRange.max}
            />
          </div>
          <div>
            <label>Hasta</label>
            <input
              type="number"
              placeholder={metadata?.yearRange.max.toString()}
              value={yearTo}
              onChange={(e) => setYearTo(e.target.value)}
              min={metadata?.yearRange.min}
              max={metadata?.yearRange.max}
            />
          </div>
        </div>
      </div>

      {/* Filtro por época */}
      <div className="filter-section">
        <h3>Época</h3>
        <select value={era} onChange={(e) => setEra(e.target.value)}>
          <option value="">Todas las épocas</option>
          {metadata?.eras.map((e) => (
            <option key={e} value={e}>
              {e}
            </option>
          ))}
        </select>
      </div>

      {/* Filtro por zona */}
      <div className="filter-section">
        <h3>Zona</h3>
        <select value={zone} onChange={(e) => setZone(e.target.value)}>
          <option value="">Todas las zonas</option>
          {metadata?.zones.map((z) => (
            <option key={z} value={z}>
              {z}
            </option>
          ))}
        </select>
      </div>

      {/* Filtro solo en viewport */}
      <div className="filter-section">
        <div className="checkbox-filter">
          <input
            type="checkbox"
            id="onlyInViewport"
            checked={onlyInViewport}
            onChange={(e) => setOnlyInViewport(e.target.checked)}
          />
          <label htmlFor="onlyInViewport">Solo fotos en pantalla del mapa</label>
        </div>
      </div>

      {/* Acciones */}
      <div className="filter-section">
        <div className="filter-actions">
          <button className="btn btn-primary" onClick={handleApplyFilters}>
            Aplicar filtros
          </button>
          <button className="btn btn-secondary" onClick={handleResetFilters}>
            Limpiar
          </button>
        </div>
      </div>
    </div>
  );
};
