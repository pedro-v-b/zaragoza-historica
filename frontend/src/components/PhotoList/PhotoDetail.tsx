import React, { useState, useCallback } from 'react';
import { Photo } from '../../types';
import { PhotoFullscreen } from './PhotoFullscreen';

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

  const formatYear = (photo: Photo): string => {
    if (photo.year) return photo.year.toString();
    if (photo.year_from && photo.year_to) return `${photo.year_from} - ${photo.year_to}`;
    if (photo.year_from) return `Desde ${photo.year_from}`;
    if (photo.year_to) return `Hasta ${photo.year_to}`;
    return 'Fecha desconocida';
  };

  const openFullImage = () => setShowFullscreen(true);
  const closeFullscreen = useCallback(() => setShowFullscreen(false), []);

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
            onClick={openFullImage}
            style={{ cursor: 'pointer' }}
            title="Clic para ver imagen completa"
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

      {showFullscreen && (
        <PhotoFullscreen photo={photo} onClose={closeFullscreen} />
      )}
    </div>
  );
};
