import React, { useState, useEffect, useCallback } from 'react';
import { Photo, PhotoFormData } from '../../types';
import { getPhotos, createPhoto, updatePhoto, deletePhoto } from '../../services/api';
import { PhotoTable } from './PhotoTable';
import { PhotoForm } from './PhotoForm';

export const AdminDashboard: React.FC = () => {
  const [photos, setPhotos] = useState<Photo[]>([]);
  const [loading, setLoading] = useState(true);
  const [formLoading, setFormLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingPhoto, setEditingPhoto] = useState<Photo | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);

  const loadPhotos = useCallback(async () => {
    setLoading(true);
    try {
      const response = await getPhotos({ page, pageSize: 20 });
      setPhotos(response.items);
      setTotalPages(response.totalPages);
      setTotal(response.total);
    } catch (error) {
      console.error('Error loading photos:', error);
    } finally {
      setLoading(false);
    }
  }, [page]);

  useEffect(() => {
    loadPhotos();
  }, [loadPhotos]);

  const handleNewPhoto = () => {
    setEditingPhoto(null);
    setShowForm(true);
  };

  const handleEdit = (photo: Photo) => {
    setEditingPhoto(photo);
    setShowForm(true);
  };

  const handleDelete = async (photo: Photo) => {
    try {
      await deletePhoto(photo.id);
      loadPhotos();
    } catch (error) {
      console.error('Error deleting photo:', error);
      alert('Error al eliminar la foto');
    }
  };

  const handleFormSubmit = async (data: PhotoFormData, imageFile?: File) => {
    setFormLoading(true);
    try {
      if (editingPhoto) {
        await updatePhoto(editingPhoto.id, data, imageFile);
      } else {
        await createPhoto(data, imageFile!);
      }
      setShowForm(false);
      setEditingPhoto(null);
      loadPhotos();
    } catch (error) {
      throw error;
    } finally {
      setFormLoading(false);
    }
  };

  const handleFormCancel = () => {
    setShowForm(false);
    setEditingPhoto(null);
  };

  return (
    <div className="admin-dashboard">
      <div className="admin-toolbar">
        <div className="admin-toolbar-left">
          <h2>Gestion de Fotos</h2>
          <span className="admin-count">{total} fotos en total</span>
        </div>
        <div className="admin-toolbar-right">
          <button className="btn btn-primary" onClick={handleNewPhoto}>
            + Nueva foto
          </button>
        </div>
      </div>

      <PhotoTable
        photos={photos}
        loading={loading}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />

      {totalPages > 1 && (
        <div className="admin-pagination">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
          >
            Anterior
          </button>
          <span>
            Pagina {page} de {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
          >
            Siguiente
          </button>
        </div>
      )}

      {showForm && (
        <PhotoForm
          photo={editingPhoto}
          onSubmit={handleFormSubmit}
          onCancel={handleFormCancel}
          loading={formLoading}
        />
      )}
    </div>
  );
};
