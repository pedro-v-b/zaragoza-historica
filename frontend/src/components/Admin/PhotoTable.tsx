import React from 'react';
import { Photo } from '../../types';

interface PhotoTableProps {
  photos: Photo[];
  loading: boolean;
  onEdit: (photo: Photo) => void;
  onDelete: (photo: Photo) => void;
}

export const PhotoTable: React.FC<PhotoTableProps> = ({
  photos,
  loading,
  onEdit,
  onDelete,
}) => {
  const formatYear = (photo: Photo): string => {
    if (photo.year) return photo.year.toString();
    if (photo.year_from && photo.year_to) return `${photo.year_from}-${photo.year_to}`;
    if (photo.year_from) return `Desde ${photo.year_from}`;
    if (photo.year_to) return `Hasta ${photo.year_to}`;
    return '-';
  };

  const handleDelete = (photo: Photo) => {
    if (window.confirm(`¿Eliminar la foto "${photo.title}"? Esta accion no se puede deshacer.`)) {
      onDelete(photo);
    }
  };

  if (loading) {
    return (
      <div className="admin-loading">
        <p>Cargando fotos...</p>
      </div>
    );
  }

  if (photos.length === 0) {
    return (
      <div className="admin-empty">
        <p>No hay fotos registradas</p>
      </div>
    );
  }

  return (
    <div className="admin-table-container">
      <table className="admin-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Imagen</th>
            <th>Titulo</th>
            <th>Ano</th>
            <th>Zona</th>
            <th>Epoca</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {photos.map((photo) => (
            <tr key={photo.id}>
              <td className="table-id">{photo.id}</td>
              <td className="table-thumb">
                <img
                  src={photo.thumb_url}
                  alt={photo.title}
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = 'https://via.placeholder.com/60?text=Sin+imagen';
                  }}
                />
              </td>
              <td className="table-title">{photo.title}</td>
              <td className="table-year">{formatYear(photo)}</td>
              <td className="table-zone">{photo.zone || '-'}</td>
              <td className="table-era">{photo.era || '-'}</td>
              <td className="table-actions">
                <button
                  className="btn btn-small btn-edit"
                  onClick={() => onEdit(photo)}
                  title="Editar"
                >
                  Editar
                </button>
                <button
                  className="btn btn-small btn-danger"
                  onClick={() => handleDelete(photo)}
                  title="Eliminar"
                >
                  Eliminar
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
