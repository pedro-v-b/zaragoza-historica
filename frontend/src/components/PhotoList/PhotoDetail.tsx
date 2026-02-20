import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Photo } from '../../types';

interface PhotoDetailProps {
  photo: Photo;
  onClose: () => void;
  onBackToList: () => void;
}

export const PhotoDetail: React.FC<PhotoDetailProps> = ({
  photo,
  onClose,
  onBackToList,
}) => {
  const [showFullscreen, setShowFullscreen] = useState(false);
  const [zoom, setZoom] = useState(1);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const imageContainerRef = useRef<HTMLDivElement>(null);

  const formatYear = (photo: Photo): string => {
    if (photo.year) return photo.year.toString();
    if (photo.year_from && photo.year_to) return `${photo.year_from} - ${photo.year_to}`;
    if (photo.year_from) return `Desde ${photo.year_from}`;
    if (photo.year_to) return `Hasta ${photo.year_to}`;
    return 'Fecha desconocida';
  };

  const openFullImage = () => {
    setShowFullscreen(true);
    setZoom(1);
    setPosition({ x: 0, y: 0 });
  };

  const closeFullscreen = useCallback(() => {
    setShowFullscreen(false);
    setZoom(1);
    setPosition({ x: 0, y: 0 });
  }, []);

  // Cerrar con tecla Escape
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && showFullscreen) {
        closeFullscreen();
      }
    };

    if (showFullscreen) {
      document.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = '';
    };
  }, [showFullscreen, closeFullscreen]);

  // Zoom con rueda del ratón
  const handleWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? -0.2 : 0.2;
    setZoom((prev) => Math.min(Math.max(prev + delta, 0.5), 5));
  }, []);

  // Zoom con botones
  const zoomIn = () => setZoom((prev) => Math.min(prev + 0.5, 5));
  const zoomOut = () => setZoom((prev) => Math.max(prev - 0.5, 0.5));
  const resetZoom = () => {
    setZoom(1);
    setPosition({ x: 0, y: 0 });
  };

  // Drag para mover imagen cuando hay zoom
  const handleMouseDown = (e: React.MouseEvent) => {
    if (zoom > 1) {
      setIsDragging(true);
      setDragStart({ x: e.clientX - position.x, y: e.clientY - position.y });
    }
  };

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (isDragging && zoom > 1) {
      setPosition({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y,
      });
    }
  }, [isDragging, dragStart, zoom]);

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  return (
    <div className="photo-detail">
      <div className="photo-detail-header">
        <h2>Detalle de foto</h2>
        <button className="photo-detail-close" onClick={onClose} title="Cerrar">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M1 1L13 13M1 13L13 1" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          </svg>
        </button>
      </div>

      <div className="photo-detail-content">
        <div className="photo-detail-image">
          <img
            src={photo.image_url}
            alt={photo.title}
            onError={(e) => {
              (e.target as HTMLImageElement).src = 'https://via.placeholder.com/400x300/f5f7f9/94a3af?text=Sin+imagen';
            }}
          />
          <button className="photo-detail-image-expand" onClick={openFullImage} title="Ver imagen completa">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M11 1H17V7M7 17H1V11M17 1L10 8M1 17L8 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        </div>

        <div className="photo-detail-body">
          <h1 className="photo-detail-title">{photo.title}</h1>

          <div className="photo-detail-meta">
            <span className="badge badge-year">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="7" cy="7" r="6" stroke="currentColor" strokeWidth="1.5"/>
                <path d="M7 4V7L9 9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
              </svg>
              {formatYear(photo)}
            </span>
            {photo.zone && (
              <span className="badge badge-zone">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M7 1C4.5 1 2.5 3 2.5 5.5C2.5 9 7 13 7 13C7 13 11.5 9 11.5 5.5C11.5 3 9.5 1 7 1Z" stroke="currentColor" strokeWidth="1.5"/>
                  <circle cx="7" cy="5.5" r="1.5" stroke="currentColor" strokeWidth="1.5"/>
                </svg>
                {photo.zone}
              </span>
            )}
            {photo.era && (
              <span className="badge badge-era">
                {photo.era}
              </span>
            )}
          </div>

          {photo.description && (
            <p className="photo-detail-description">{photo.description}</p>
          )}

          {photo.tags && photo.tags.length > 0 && (
            <div className="photo-detail-tags">
              <div className="photo-detail-tags-title">Etiquetas</div>
              <div className="photo-detail-tags-list">
                {photo.tags.map((tag, index) => (
                  <span key={index} className="photo-detail-tag">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {(photo.source || photo.author || photo.rights) && (
            <div className="photo-detail-info">
              {photo.source && (
                <div className="photo-detail-info-row">
                  <span className="photo-detail-info-label">Fuente</span>
                  <span className="photo-detail-info-value">{photo.source}</span>
                </div>
              )}
              {photo.author && (
                <div className="photo-detail-info-row">
                  <span className="photo-detail-info-label">Autor</span>
                  <span className="photo-detail-info-value">{photo.author}</span>
                </div>
              )}
              {photo.rights && (
                <div className="photo-detail-info-row">
                  <span className="photo-detail-info-label">Derechos</span>
                  <span className="photo-detail-info-value">{photo.rights}</span>
                </div>
              )}
            </div>
          )}

          <button className="photo-detail-back" onClick={onBackToList}>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M10 12L6 8L10 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Volver a la lista
          </button>
        </div>
      </div>

      {/* Modal de imagen a pantalla completa */}
      {showFullscreen && (
        <div className="fullscreen-modal" onClick={closeFullscreen}>
          <div className="fullscreen-content" onClick={(e) => e.stopPropagation()}>
            <button className="fullscreen-close" onClick={closeFullscreen} title="Cerrar (Esc)">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
            </button>

            <div
              className="fullscreen-image"
              ref={imageContainerRef}
              onWheel={handleWheel}
              onMouseDown={handleMouseDown}
              onMouseMove={handleMouseMove}
              onMouseUp={handleMouseUp}
              onMouseLeave={handleMouseUp}
              style={{ cursor: zoom > 1 ? (isDragging ? 'grabbing' : 'grab') : 'zoom-in' }}
            >
              <img
                src={photo.image_url}
                alt={photo.title}
                style={{
                  transform: `scale(${zoom}) translate(${position.x / zoom}px, ${position.y / zoom}px)`,
                  transition: isDragging ? 'none' : 'transform 0.2s ease-out',
                }}
                draggable={false}
                onError={(e) => {
                  (e.target as HTMLImageElement).src = 'https://via.placeholder.com/800x600/f5f7f9/94a3af?text=Sin+imagen';
                }}
              />

              {/* Controles de zoom */}
              <div className="zoom-controls">
                <button onClick={zoomOut} title="Alejar" disabled={zoom <= 0.5}>
                  <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <circle cx="10" cy="10" r="7" stroke="currentColor" strokeWidth="2"/>
                    <path d="M7 10H13" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  </svg>
                </button>
                <span className="zoom-level">{Math.round(zoom * 100)}%</span>
                <button onClick={zoomIn} title="Acercar" disabled={zoom >= 5}>
                  <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <circle cx="10" cy="10" r="7" stroke="currentColor" strokeWidth="2"/>
                    <path d="M10 7V13M7 10H13" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  </svg>
                </button>
                <button onClick={resetZoom} title="Restablecer zoom">
                  <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <path d="M3 10C3 6.13401 6.13401 3 10 3C13.866 3 17 6.13401 17 10C17 13.866 13.866 17 10 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                    <path d="M3 6V10H7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </button>
              </div>

              <div className="zoom-hint">
                Usa la rueda del ratón para hacer zoom
              </div>
            </div>

            <div className="fullscreen-info">
              <h1 className="fullscreen-title">{photo.title}</h1>

              <div className="fullscreen-meta">
                <div className="fullscreen-meta-item">
                  <span className="fullscreen-meta-label">Fecha</span>
                  <span className="fullscreen-meta-value">{formatYear(photo)}</span>
                </div>
                {photo.zone && (
                  <div className="fullscreen-meta-item">
                    <span className="fullscreen-meta-label">Zona</span>
                    <span className="fullscreen-meta-value">{photo.zone}</span>
                  </div>
                )}
                {photo.era && (
                  <div className="fullscreen-meta-item">
                    <span className="fullscreen-meta-label">Época</span>
                    <span className="fullscreen-meta-value">{photo.era}</span>
                  </div>
                )}
              </div>

              {photo.description && (
                <div className="fullscreen-description">
                  <h3>Descripción</h3>
                  <p>{photo.description}</p>
                </div>
              )}

              {photo.tags && photo.tags.length > 0 && (
                <div className="fullscreen-tags">
                  <h3>Etiquetas</h3>
                  <div className="fullscreen-tags-list">
                    {photo.tags.map((tag, index) => (
                      <span key={index} className="fullscreen-tag">{tag}</span>
                    ))}
                  </div>
                </div>
              )}

              {(photo.source || photo.author || photo.rights) && (
                <div className="fullscreen-credits">
                  <h3>Créditos</h3>
                  {photo.source && <p><strong>Fuente:</strong> {photo.source}</p>}
                  {photo.author && <p><strong>Autor:</strong> {photo.author}</p>}
                  {photo.rights && <p><strong>Derechos:</strong> {photo.rights}</p>}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
