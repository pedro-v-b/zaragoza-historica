import React, { useState, useEffect } from 'react';
import { getHistoricalContext, HistoricalContext as HistoricalContextData } from '../../services/api';

interface HistoricalContextProps {
  year: number;
  onClose: () => void;
}

export const HistoricalContext: React.FC<HistoricalContextProps> = ({ year, onClose }) => {
  const [data, setData] = useState<HistoricalContextData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({
    eventos: true,
    noticias: true,
    urbanismo: false,
    movilidad: false,
  });

  useEffect(() => {
    setLoading(true);
    setError(null);
    getHistoricalContext(year)
      .then(setData)
      .catch(() => setError('No hay datos disponibles para este año'))
      .finally(() => setLoading(false));
  }, [year]);

  const toggle = (key: string) =>
    setExpanded(prev => ({ ...prev, [key]: !prev[key] }));

  if (loading) {
    return (
      <div className="hc-panel">
        <div className="hc-header">
          <div className="hc-title-row">
            <span className="hc-year-badge">{year}</span>
            <span className="hc-title-text">Contexto histórico</span>
          </div>
          <button className="hc-close-btn" onClick={onClose} title="Ver fotos">✕</button>
        </div>
        <div className="hc-loading">Cargando datos históricos...</div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="hc-panel">
        <div className="hc-header">
          <div className="hc-title-row">
            <span className="hc-year-badge">{year}</span>
            <span className="hc-title-text">Contexto histórico</span>
          </div>
          <button className="hc-close-btn" onClick={onClose} title="Ver fotos">✕</button>
        </div>
        <div className="hc-error">{error || 'Sin datos disponibles'}</div>
      </div>
    );
  }

  return (
    <div className="hc-panel">
      {/* Cabecera */}
      <div className="hc-header">
        <div className="hc-title-row">
          <span className="hc-year-badge">{data.year}</span>
          <span className="hc-title-text">Contexto histórico</span>
        </div>
        <button className="hc-close-btn" onClick={onClose} title="Ver fotos">✕</button>
      </div>

      <div className="hc-body">
        {/* Alcalde */}
        {data.alcalde && (
          <div className="hc-alcalde-block">
            <span className="hc-block-label">Gobierno municipal</span>
            <p className="hc-alcalde-text">{data.alcalde}</p>
          </div>
        )}

        {/* Secciones colapsables */}
        <HcSection
          icon="🗓️"
          title="Eventos"
          items={data.eventos}
          sectionKey="eventos"
          expanded={expanded.eventos}
          onToggle={() => toggle('eventos')}
        />
        <HcSection
          icon="📰"
          title="Noticias y sociedad"
          items={data.noticias_sociedad_sucesos}
          sectionKey="noticias"
          expanded={expanded.noticias}
          onToggle={() => toggle('noticias')}
        />
        <HcSection
          icon="🏛️"
          title="Urbanismo"
          items={data.urbanismo}
          sectionKey="urbanismo"
          expanded={expanded.urbanismo}
          onToggle={() => toggle('urbanismo')}
        />
        <HcSection
          icon="🚌"
          title="Movilidad y transporte"
          items={data.movilidad_transporte}
          sectionKey="movilidad"
          expanded={expanded.movilidad}
          onToggle={() => toggle('movilidad')}
        />
      </div>
    </div>
  );
};

interface HcSectionProps {
  icon: string;
  title: string;
  items: string[] | null | undefined;
  sectionKey: string;
  expanded: boolean;
  onToggle: () => void;
}

const HcSection: React.FC<HcSectionProps> = ({
  icon,
  title,
  items,
  expanded,
  onToggle,
}) => {
  if (!items || items.length === 0) return null;

  return (
    <div className={`hc-section ${expanded ? 'hc-section--open' : ''}`}>
      <button className="hc-section-btn" onClick={onToggle}>
        <span className="hc-section-icon">{icon}</span>
        <span className="hc-section-title">{title}</span>
        <span className="hc-chevron">{expanded ? '▾' : '▸'}</span>
      </button>
      {expanded && (
        <ul className="hc-list">
          {items.map((item, i) => (
            <li key={i} className="hc-list-item">{item}</li>
          ))}
        </ul>
      )}
    </div>
  );
};
