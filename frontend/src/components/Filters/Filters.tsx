import React, { useState, useEffect } from 'react';
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
    era?: string;
    q?: string;
    onlyInViewport: boolean;
  }) => void;
  selectedZone?: string;
  onZoneHover?: (zone: string | null) => void;
  onZoneSelect?: (zone: string | null) => void;
}

// Presets de rangos de años
const YEAR_PRESETS = [
  { label: 'Todo', from: null, to: null },
  { label: '2010–hoy', from: 2010, to: 2024 },
  { label: '2000–2010', from: 2000, to: 2010 },
  { label: '1975–2000', from: 1975, to: 2000 },
  { label: '1950–1975', from: 1950, to: 1975 },
  { label: '1900–1950', from: 1900, to: 1950 },
  { label: 'Antes de 1900', from: null, to: 1900 },
];

export const Filters: React.FC<FiltersProps> = ({
  onFilterChange,
  selectedZone,
  onZoneHover,
  onZoneSelect,
}) => {
  const [metadata, setMetadata] = useState<FilterMetadata | null>(null);
  const [barrios, setBarrios] = useState<Barrio[]>([]);
  const [yearFrom, setYearFrom] = useState<string>('');
  const [yearTo, setYearTo] = useState<string>('');
  const [activePreset, setActivePreset] = useState<number>(0);
  const [zone, setZone] = useState<string>('');
  const [selectedEra, setSelectedEra] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [onlyInViewport, setOnlyInViewport] = useState<boolean>(false);
  const [barrioExpanded, setBarrioExpanded] = useState<boolean>(false);
  const [tematicoExpanded, setTematicoExpanded] = useState<boolean>(false);

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

  // Inicializar rango cuando se carga metadata
  useEffect(() => {
    if (metadata) {
      setYearFrom(metadata.yearRange.min.toString());
      setYearTo(metadata.yearRange.max.toString());
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
      barriosList.sort((a, b) => a.name.localeCompare(b.name));
      setBarrios(barriosList);
    } catch (error) {
      console.error('Error loading barrios:', error);
    }
  };

  // Seleccionar preset de rango
  const handlePreset = (index: number) => {
    if (!metadata) return;
    const preset = YEAR_PRESETS[index];
    const from = preset.from ?? metadata.yearRange.min;
    const to = preset.to ?? metadata.yearRange.max;
    setYearFrom(from.toString());
    setYearTo(to.toString());
    setActivePreset(index);
    onFilterChange({
      yearFrom: from,
      yearTo: to,
      zone: zone || undefined,
      era: selectedEra || undefined,
      q: searchQuery || undefined,
      onlyInViewport,
    });
  };

  // Validar y clampar año al perder foco
  const handleYearBlur = (field: 'from' | 'to') => {
    if (!metadata) return;
    const { min, max } = metadata.yearRange;

    if (field === 'from') {
      let v = parseInt(yearFrom, 10);
      if (isNaN(v)) v = min;
      v = Math.max(min, Math.min(v, parseInt(yearTo, 10) || max));
      setYearFrom(v.toString());
    } else {
      let v = parseInt(yearTo, 10);
      if (isNaN(v)) v = max;
      v = Math.min(max, Math.max(v, parseInt(yearFrom, 10) || min));
      setYearTo(v.toString());
    }
    setActivePreset(-1);
  };

  // Porcentaje lineal para barra visual
  const getBarPercent = (year: number): number => {
    if (!metadata) return 0;
    const { min, max } = metadata.yearRange;
    return ((year - min) / (max - min)) * 100;
  };

  const handleApplyFilters = () => {
    const from = parseInt(yearFrom, 10);
    const to = parseInt(yearTo, 10);
    onFilterChange({
      yearFrom: isNaN(from) ? undefined : from,
      yearTo: isNaN(to) ? undefined : to,
      zone: zone || undefined,
      era: selectedEra || undefined,
      q: searchQuery || undefined,
      onlyInViewport,
    });
  };

  const handleZoneSelect = (selectedBarrio: string) => {
    const newZone = zone === selectedBarrio ? '' : selectedBarrio;
    setZone(newZone);
    onZoneSelect?.(newZone || null);
    const from = parseInt(yearFrom, 10);
    const to = parseInt(yearTo, 10);
    onFilterChange({
      yearFrom: isNaN(from) ? undefined : from,
      yearTo: isNaN(to) ? undefined : to,
      zone: newZone || undefined,
      era: selectedEra || undefined,
      q: searchQuery || undefined,
      onlyInViewport,
    });
  };

  const handleEraSelect = (eraName: string) => {
    const newEra = selectedEra === eraName ? '' : eraName;
    setSelectedEra(newEra);
    const from = parseInt(yearFrom, 10);
    const to = parseInt(yearTo, 10);
    onFilterChange({
      yearFrom: isNaN(from) ? undefined : from,
      yearTo: isNaN(to) ? undefined : to,
      zone: zone || undefined,
      era: newEra || undefined,
      q: searchQuery || undefined,
      onlyInViewport,
    });
  };

  const handleResetFilters = () => {
    if (metadata) {
      setYearFrom(metadata.yearRange.min.toString());
      setYearTo(metadata.yearRange.max.toString());
    }
    setActivePreset(0);
    setZone('');
    setSelectedEra('');
    setSearchQuery('');
    setOnlyInViewport(false);
    onZoneSelect?.(null);
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
          <>
            {/* Inputs numéricos */}
            <div className="year-inputs">
              <div className="year-input-group">
                <label>Desde</label>
                <input
                  type="number"
                  value={yearFrom}
                  min={metadata.yearRange.min}
                  max={metadata.yearRange.max}
                  onChange={(e) => { setYearFrom(e.target.value); setActivePreset(-1); }}
                  onBlur={() => handleYearBlur('from')}
                  onKeyDown={(e) => e.key === 'Enter' && handleApplyFilters()}
                />
              </div>
              <span className="year-input-separator">—</span>
              <div className="year-input-group">
                <label>Hasta</label>
                <input
                  type="number"
                  value={yearTo}
                  min={metadata.yearRange.min}
                  max={metadata.yearRange.max}
                  onChange={(e) => { setYearTo(e.target.value); setActivePreset(-1); }}
                  onBlur={() => handleYearBlur('to')}
                  onKeyDown={(e) => e.key === 'Enter' && handleApplyFilters()}
                />
              </div>
            </div>

            {/* Barra visual del rango seleccionado */}
            <div className="year-visual-bar">
              <div className="year-visual-track" />
              <div
                className="year-visual-range"
                style={{
                  left: `${getBarPercent(parseInt(yearFrom, 10) || metadata.yearRange.min)}%`,
                  width: `${getBarPercent(parseInt(yearTo, 10) || metadata.yearRange.max) - getBarPercent(parseInt(yearFrom, 10) || metadata.yearRange.min)}%`,
                }}
              />
            </div>
            <div className="year-range-labels">
              <span>{metadata.yearRange.min}</span>
              <span>{metadata.yearRange.max}</span>
            </div>

            {/* Presets de rango rápido */}
            <div className="year-presets">
              {YEAR_PRESETS.map((preset, i) => (
                <button
                  key={preset.label}
                  className={`year-preset-btn ${activePreset === i ? 'active' : ''}`}
                  onClick={() => handlePreset(i)}
                >
                  {preset.label}
                </button>
              ))}
            </div>
          </>
        )}
      </div>

      {/* Filtro temático por época histórica */}
      <div className="filter-section filter-section-collapsible">
        <button
          className="filter-section-toggle"
          onClick={() => setTematicoExpanded((v) => !v)}
        >
          <h3>Temático</h3>
          <svg
            className={`toggle-chevron ${tematicoExpanded ? 'expanded' : ''}`}
            width="16" height="16" viewBox="0 0 16 16" fill="none"
          >
            <path d="M4 6L8 10L12 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
        {tematicoExpanded && (
          <div className="era-list">
            {metadata?.eras && metadata.eras.length > 0 ? (
              <>
                {selectedEra && (
                  <button
                    className="era-item era-clear"
                    onClick={() => handleEraSelect('')}
                  >
                    ✕ Limpiar selección
                  </button>
                )}
                {metadata.eras.map((eraName) => (
                  <button
                    key={eraName}
                    className={`era-item ${selectedEra === eraName ? 'active' : ''}`}
                    onClick={() => handleEraSelect(eraName)}
                  >
                    {eraName}
                  </button>
                ))}
              </>
            ) : (
              <p className="filter-hint">No hay épocas disponibles</p>
            )}
          </div>
        )}
      </div>

      {/* Filtro por zona/barrio (colapsable) */}
      <div className="filter-section filter-section-collapsible">
        <button
          className="filter-section-toggle"
          onClick={() => setBarrioExpanded((v) => !v)}
        >
          <h3>Barrio / Zona</h3>
          <svg
            className={`toggle-chevron ${barrioExpanded ? 'expanded' : ''}`}
            width="16" height="16" viewBox="0 0 16 16" fill="none"
          >
            <path d="M4 6L8 10L12 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
        {barrioExpanded && (
          <>
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
          </>
        )}
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
