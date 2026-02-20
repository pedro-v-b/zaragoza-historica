import React, { useState, useEffect, useRef, useCallback } from 'react';
import { FilterMetadata } from '../../types';
import { getFilterMetadata } from '../../services/api';

interface Barrio {
  name: string;
  originalName: string;
}

interface FiltersProps {
  onFilterChange: (filters: {
    yearFrom?: number;
    yearTo?: number;
    zone?: string;
    q?: string;
    onlyInViewport: boolean;
  }) => void;
  selectedZone?: string;
  onZoneHover?: (zone: string | null) => void;
  onZoneSelect?: (zone: string | null) => void;
}

export const Filters: React.FC<FiltersProps> = ({
  onFilterChange,
  selectedZone,
  onZoneHover,
  onZoneSelect,
}) => {
  const [metadata, setMetadata] = useState<FilterMetadata | null>(null);
  const [barrios, setBarrios] = useState<Barrio[]>([]);
  const [yearRange, setYearRange] = useState<[number, number]>([1850, 2024]);
  const [zone, setZone] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [onlyInViewport, setOnlyInViewport] = useState<boolean>(false);

  // Referencias para el slider
  const sliderRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState<'min' | 'max' | null>(null);

  useEffect(() => {
    loadMetadata();
    loadBarrios();
  }, []);

  // Sincronizar zona seleccionada desde props
  useEffect(() => {
    if (selectedZone !== undefined) {
      setZone(selectedZone);
    }
  }, [selectedZone]);

  // Inicializar rango de años cuando se carga metadata
  useEffect(() => {
    if (metadata) {
      setYearRange([metadata.yearRange.min, metadata.yearRange.max]);
    }
  }, [metadata]);

  const loadMetadata = async () => {
    try {
      const data = await getFilterMetadata();
      setMetadata(data);
    } catch (error) {
      console.error('Error loading filter metadata:', error);
    }
  };

  const loadBarrios = async () => {
    try {
      const response = await fetch('/barrios-zaragoza-wgs84.geojson');
      const geojson = await response.json();
      const barriosList: Barrio[] = geojson.features.map((f: any) => ({
        name: f.properties.name || f.properties.JUNTA,
        originalName: f.properties.name || f.properties.JUNTA,
      }));
      // Ordenar alfabeticamente
      barriosList.sort((a, b) => a.name.localeCompare(b.name));
      setBarrios(barriosList);
    } catch (error) {
      console.error('Error loading barrios:', error);
    }
  };

  // Lógica del slider de rango
  const getSliderValue = useCallback((clientX: number): number => {
    if (!sliderRef.current || !metadata) return yearRange[0];
    const rect = sliderRef.current.getBoundingClientRect();
    const percent = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
    const value = Math.round(metadata.yearRange.min + percent * (metadata.yearRange.max - metadata.yearRange.min));
    return value;
  }, [metadata, yearRange]);

  const handleSliderMouseDown = (handle: 'min' | 'max') => (e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(handle);
  };

  const handleSliderMouseMove = useCallback((e: MouseEvent) => {
    if (!isDragging || !metadata) return;
    const value = getSliderValue(e.clientX);

    setYearRange(prev => {
      if (isDragging === 'min') {
        return [Math.min(value, prev[1] - 1), prev[1]];
      } else {
        return [prev[0], Math.max(value, prev[0] + 1)];
      }
    });
  }, [isDragging, getSliderValue, metadata]);

  const handleSliderMouseUp = useCallback(() => {
    if (isDragging) {
      setIsDragging(null);
      // Aplicar filtros al soltar
      handleApplyFilters();
    }
  }, [isDragging]);

  // Event listeners para drag
  useEffect(() => {
    if (isDragging) {
      window.addEventListener('mousemove', handleSliderMouseMove);
      window.addEventListener('mouseup', handleSliderMouseUp);
      return () => {
        window.removeEventListener('mousemove', handleSliderMouseMove);
        window.removeEventListener('mouseup', handleSliderMouseUp);
      };
    }
  }, [isDragging, handleSliderMouseMove, handleSliderMouseUp]);

  const handleApplyFilters = () => {
    onFilterChange({
      yearFrom: yearRange[0],
      yearTo: yearRange[1],
      zone: zone || undefined,
      q: searchQuery || undefined,
      onlyInViewport,
    });
  };

  const handleZoneSelect = (selectedBarrio: string) => {
    const newZone = zone === selectedBarrio ? '' : selectedBarrio;
    setZone(newZone);
    onZoneSelect?.(newZone || null);
    onFilterChange({
      yearFrom: yearRange[0],
      yearTo: yearRange[1],
      zone: newZone || undefined,
      q: searchQuery || undefined,
      onlyInViewport,
    });
  };

  const handleResetFilters = () => {
    if (metadata) {
      setYearRange([metadata.yearRange.min, metadata.yearRange.max]);
    }
    setZone('');
    setSearchQuery('');
    setOnlyInViewport(false);
    onZoneSelect?.(null);
    onFilterChange({ onlyInViewport: false });
  };

  // Calcular posición de los handles
  const getHandlePosition = (value: number): number => {
    if (!metadata) return 0;
    return ((value - metadata.yearRange.min) / (metadata.yearRange.max - metadata.yearRange.min)) * 100;
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

      {/* Filtro por año - Slider de rango */}
      <div className="filter-section">
        <h3>Rango de años</h3>
        {metadata && (
          <>
            <div className="year-range-display">
              <span className="year-value">{yearRange[0]}</span>
              <span className="year-separator">—</span>
              <span className="year-value">{yearRange[1]}</span>
            </div>
            <div className="year-slider" ref={sliderRef}>
              <div className="slider-track" />
              <div
                className="slider-range"
                style={{
                  left: `${getHandlePosition(yearRange[0])}%`,
                  width: `${getHandlePosition(yearRange[1]) - getHandlePosition(yearRange[0])}%`,
                }}
              />
              <div
                className={`slider-handle slider-handle-min ${isDragging === 'min' ? 'active' : ''}`}
                style={{ left: `${getHandlePosition(yearRange[0])}%` }}
                onMouseDown={handleSliderMouseDown('min')}
                title={yearRange[0].toString()}
              />
              <div
                className={`slider-handle slider-handle-max ${isDragging === 'max' ? 'active' : ''}`}
                style={{ left: `${getHandlePosition(yearRange[1])}%` }}
                onMouseDown={handleSliderMouseDown('max')}
                title={yearRange[1].toString()}
              />
            </div>
            <div className="year-range-labels">
              <span>{metadata.yearRange.min}</span>
              <span>{metadata.yearRange.max}</span>
            </div>
          </>
        )}
      </div>

      {/* Filtro por zona/barrio */}
      <div className="filter-section">
        <h3>Barrio / Zona</h3>
        <p className="filter-hint">Selecciona un barrio para ver solo sus fotos</p>
        <div className="zone-list">
          {zone && (
            <button
              className="zone-item zone-clear"
              onClick={() => handleZoneSelect('')}
            >
              ✕ Limpiar selección
            </button>
          )}
          {barrios.map((barrio) => (
            <button
              key={barrio.name}
              className={`zone-item ${zone === barrio.name ? 'active' : ''}`}
              onClick={() => handleZoneSelect(barrio.name)}
              onMouseEnter={() => onZoneHover?.(barrio.name)}
              onMouseLeave={() => onZoneHover?.(null)}
            >
              {barrio.name}
            </button>
          ))}
        </div>
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
