import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Photo } from '../../types';

interface PhotoFullscreenProps {
  photo: Photo;
  onClose: () => void;
}

export const PhotoFullscreen: React.FC<PhotoFullscreenProps> = ({ photo, onClose }) => {
  const [zoom, setZoom] = useState(1);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const imageContainerRef = useRef<HTMLDivElement>(null);

  const pinchStartDistanceRef = useRef<number | null>(null);
  const pinchStartZoomRef = useRef<number>(1);
  const touchPanStartRef = useRef<{ x: number; y: number; posX: number; posY: number } | null>(null);

  const formatYear = (photo: Photo): string => {
    if (photo.year) return photo.year.toString();
    if (photo.year_from && photo.year_to) return `${photo.year_from} - ${photo.year_to}`;
    if (photo.year_from) return `Desde ${photo.year_from}`;
    if (photo.year_to) return `Hasta ${photo.year_to}`;
    return 'Fecha desconocida';
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', handleKeyDown);
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = '';
    };
  }, [onClose]);

  const handleWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? -0.2 : 0.2;
    setZoom((prev) => Math.min(Math.max(prev + delta, 0.5), 5));
  }, []);

  const zoomIn = () => setZoom((prev) => Math.min(prev + 0.5, 5));
  const zoomOut = () => setZoom((prev) => Math.max(prev - 0.5, 0.5));
  const resetZoom = () => { setZoom(1); setPosition({ x: 0, y: 0 }); };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (zoom > 1) {
      setIsDragging(true);
      setDragStart({ x: e.clientX - position.x, y: e.clientY - position.y });
    }
  };

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (isDragging && zoom > 1) {
      setPosition({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y });
    }
  }, [isDragging, dragStart, zoom]);

  const handleMouseUp = () => setIsDragging(false);

  // ----- Touch handlers: pinch-zoom + pan -----
  const distance = (t1: React.Touch, t2: React.Touch) => {
    const dx = t1.clientX - t2.clientX;
    const dy = t1.clientY - t2.clientY;
    return Math.hypot(dx, dy);
  };

  const handleTouchStart = (e: React.TouchEvent) => {
    if (e.touches.length === 2) {
      pinchStartDistanceRef.current = distance(e.touches[0], e.touches[1]);
      pinchStartZoomRef.current = zoom;
      touchPanStartRef.current = null;
    } else if (e.touches.length === 1 && zoom > 1) {
      const t = e.touches[0];
      touchPanStartRef.current = { x: t.clientX, y: t.clientY, posX: position.x, posY: position.y };
      pinchStartDistanceRef.current = null;
    }
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (e.touches.length === 2 && pinchStartDistanceRef.current != null) {
      e.preventDefault();
      const d = distance(e.touches[0], e.touches[1]);
      const ratio = d / pinchStartDistanceRef.current;
      const newZoom = Math.min(Math.max(pinchStartZoomRef.current * ratio, 0.5), 5);
      setZoom(newZoom);
    } else if (e.touches.length === 1 && touchPanStartRef.current && zoom > 1) {
      e.preventDefault();
      const t = e.touches[0];
      const s = touchPanStartRef.current;
      setPosition({ x: s.posX + (t.clientX - s.x), y: s.posY + (t.clientY - s.y) });
    }
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    if (e.touches.length < 2) pinchStartDistanceRef.current = null;
    if (e.touches.length === 0) touchPanStartRef.current = null;
  };

  return (
    <div className="fullscreen-modal" onClick={onClose}>
      <div className={`fullscreen-content ${zoom > 1 ? 'zoomed' : ''}`} onClick={(e) => e.stopPropagation()}>
        <button className="fullscreen-close" onClick={onClose} title="Cerrar (Esc)">
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
          onTouchStart={handleTouchStart}
          onTouchMove={handleTouchMove}
          onTouchEnd={handleTouchEnd}
          onTouchCancel={handleTouchEnd}
          style={{
            cursor: zoom > 1 ? (isDragging ? 'grabbing' : 'grab') : 'zoom-in',
            touchAction: 'none',
          }}
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
            Usa la rueda del ratón o pellizca para hacer zoom
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
  );
};
