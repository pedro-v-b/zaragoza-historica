import React, { useState, useEffect, useCallback } from 'react';
import { Photo, PhotoFormData } from '../../types';
import { getPhotos, createPhoto, updatePhoto, deletePhoto } from '../../services/api';
import { PhotoTable } from './PhotoTable';
import { PhotoForm } from './PhotoForm';

// Todos los barrios y zonas de Zaragoza
const BARRIOS_ZARAGOZA = [
  // Distrito Centro
  'Casco Historico',
  'Centro',
  'San Pablo',
  'La Magdalena',
  'San Miguel',
  'Tenerías',
  // Distrito Casco Historico
  'San Felipe',
  'El Gancho',
  // Distrito Universidad
  'Universidad',
  'San Jose',
  'La Paz',
  'San Vicente de Paul',
  // Distrito Delicias
  'Delicias',
  'Ciudad Jardin',
  'Monsalud',
  // Distrito San Jose
  'Torrero',
  'La Paz',
  'Venecia',
  // Distrito Las Fuentes
  'Las Fuentes',
  // Distrito Almozara
  'La Almozara',
  'Las Armas',
  // Distrito Oliver-Valdefierro
  'Oliver',
  'Valdefierro',
  // Distrito Torrero-La Paz
  'Torrero',
  'La Paz',
  'Venecia',
  'San Antonio de Padua',
  // Distrito Actur-Rey Fernando
  'Actur',
  'Rey Fernando',
  'Parque Goya',
  // Distrito El Rabal
  'El Rabal',
  'Arrabal',
  'Cogullada',
  'Picarral',
  'Jesus',
  // Distrito Casablanca
  'Casablanca',
  'Valdespartera',
  'Montecanal',
  'Rosales del Canal',
  'Arcosur',
  // Distrito Santa Isabel
  'Santa Isabel',
  'Movera',
  // Distrito Miralbueno
  'Miralbueno',
  // Barrios rurales norte
  'Juslibol',
  'San Juan de Mozarrifar',
  'Montanana',
  'Penanflor',
  'San Gregorio',
  'Villamayor de Gallego',
  // Barrios rurales oeste
  'Alfocea',
  'Garrapinillos',
  'La Joyosa',
  'Marlofa',
  'Monzalbarba',
  'Villarrapa',
  // Barrios rurales sur
  'Casetas',
  'Venta del Olivar',
  'Torre Medina',
  // Zonas emblematicas
  'Plaza del Pilar',
  'La Seo',
  'La Aljaferia',
  'Expo',
  'Puerto Venecia',
  'Gran Via',
  'Paseo Independencia',
  'Plaza de Aragon',
  'Plaza de Espana',
  'Puente de Piedra',
  'Ribera del Ebro',
  'Parque Grande',
  'Parque del Agua',
].sort();

export const AdminDashboard: React.FC = () => {
  const [photos, setPhotos] = useState<Photo[]>([]);
  const [loading, setLoading] = useState(true);
  const [formLoading, setFormLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingPhoto, setEditingPhoto] = useState<Photo | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchZone, setSearchZone] = useState('');

  const loadPhotos = useCallback(async () => {
    setLoading(true);
    try {
      const response = await getPhotos({
        page,
        pageSize: 20,
        q: searchQuery || undefined,
        zone: searchZone || undefined,
      });
      setPhotos(response.items);
      setTotalPages(response.totalPages);
      setTotal(response.total);
    } catch (error) {
      console.error('Error loading photos:', error);
    } finally {
      setLoading(false);
    }
  }, [page, searchQuery, searchZone]);

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

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    loadPhotos();
  };

  const handleClearSearch = () => {
    setSearchQuery('');
    setSearchZone('');
    setPage(1);
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

      {/* Barra de busqueda */}
      <form className="admin-search-bar" onSubmit={handleSearch}>
        <div className="search-field">
          <label htmlFor="search-title">Buscar por titulo</label>
          <input
            id="search-title"
            type="text"
            placeholder="Escribe para buscar..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <div className="search-field">
          <label htmlFor="search-zone">Filtrar por barrio</label>
          <select
            id="search-zone"
            value={searchZone}
            onChange={(e) => setSearchZone(e.target.value)}
          >
            <option value="">Todos los barrios</option>
            {BARRIOS_ZARAGOZA.map((barrio) => (
              <option key={barrio} value={barrio}>{barrio}</option>
            ))}
          </select>
        </div>
        <div className="search-actions">
          <button type="submit" className="btn btn-primary">
            Buscar
          </button>
          {(searchQuery || searchZone) && (
            <button type="button" className="btn btn-secondary" onClick={handleClearSearch}>
              Limpiar
            </button>
          )}
        </div>
      </form>

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
