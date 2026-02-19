import React from 'react';
import { Photo } from '../../types';

interface PhotoListProps {
  photos: Photo[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  loading: boolean;
  selectedPhotoId: number | null;
  onPhotoClick: (photo: Photo) => void;
  onPageChange: (page: number) => void;
}

export const PhotoList: React.FC<PhotoListProps> = ({
  photos,
  total,
  page,
  pageSize,
  totalPages,
  loading,
  selectedPhotoId,
  onPhotoClick,
  onPageChange,
}) => {
  const formatYear = (photo: Photo): string => {
    if (photo.year) return photo.year.toString();
    if (photo.year_from && photo.year_to) return `${photo.year_from}-${photo.year_to}`;
    if (photo.year_from) return `Desde ${photo.year_from}`;
    if (photo.year_to) return `Hasta ${photo.year_to}`;
    return 'Fecha desconocida';
  };

  if (loading) {
    return (
      <div className="photo-list">
        <div className="loading">
          <p>Cargando fotos...</p>
        </div>
      </div>
    );
  }

  if (photos.length === 0) {
    return (
      <div className="photo-list">
        <div className="empty-state">
          <p>No se encontraron fotos con los filtros seleccionados</p>
        </div>
      </div>
    );
  }

  return (
    <div className="photo-list">
      <div className="photo-list-header">
        <h2>Resultados</h2>
        <div className="results-info">
          Mostrando {photos.length} de {total} fotos
        </div>
      </div>

      <div className="photo-items">
        {photos.map((photo) => (
          <div
            key={photo.id}
            className={`photo-card ${selectedPhotoId === photo.id ? 'active' : ''}`}
            onClick={() => onPhotoClick(photo)}
          >
            <div className="photo-card-thumbnail">
              <img
                src={photo.thumb_url}
                alt={photo.title}
                onError={(e) => {
                  (e.target as HTMLImageElement).src = 'https://via.placeholder.com/100?text=Sin+imagen';
                }}
              />
            </div>
            <div className="photo-card-content">
              <div className="photo-card-title">{photo.title}</div>
              <div className="photo-card-year">{formatYear(photo)}</div>
              {photo.zone && <div className="photo-card-zone">{photo.zone}</div>}
              {photo.description && (
                <div className="photo-card-description">{photo.description}</div>
              )}
            </div>
          </div>
        ))}
      </div>

      {totalPages > 1 && (
        <div className="pagination">
          <button onClick={() => onPageChange(page - 1)} disabled={page === 1}>
            ← Anterior
          </button>
          <span className="pagination-info">
            Página {page} de {totalPages}
          </span>
          <button onClick={() => onPageChange(page + 1)} disabled={page === totalPages}>
            Siguiente →
          </button>
        </div>
      )}
    </div>
  );
};
