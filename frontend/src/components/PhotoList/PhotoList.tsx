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

// Skeleton Loading Component
const SkeletonCard: React.FC = () => (
  <div className="skeleton-card">
    <div className="skeleton-thumb" />
    <div className="skeleton-content">
      <div className="skeleton-line medium" />
      <div className="skeleton-line tiny" />
      <div className="skeleton-line short" />
    </div>
  </div>
);

const SkeletonLoading: React.FC = () => (
  <div className="photo-list">
    <div className="photo-list-header">
      <h2>Resultados</h2>
      <div className="results-info">Cargando fotos...</div>
    </div>
    <div className="skeleton-container">
      {[...Array(6)].map((_, i) => (
        <SkeletonCard key={i} />
      ))}
    </div>
  </div>
);

export const PhotoList: React.FC<PhotoListProps> = ({
  photos,
  total,
  page,
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
    return <SkeletonLoading />;
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
        {photos.map((photo, index) => (
          <div
            key={photo.id}
            className={`photo-card ${selectedPhotoId === photo.id ? 'active' : ''}`}
            onClick={() => onPhotoClick(photo)}
            style={{ animationDelay: `${index * 0.05}s` }}
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
            Anterior
          </button>
          <span className="pagination-info">
            Pagina {page} de {totalPages}
          </span>
          <button onClick={() => onPageChange(page + 1)} disabled={page === totalPages}>
            Siguiente
          </button>
        </div>
      )}
    </div>
  );
};
