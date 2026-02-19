// API Client para comunicación con el backend
import { Photo, PhotoFilters, PaginatedResponse, MapLayer, FilterMetadata, PhotoFormData } from '../types';
import { getToken } from './auth';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

/**
 * Obtiene fotos con filtros
 */
export async function getPhotos(filters: PhotoFilters): Promise<PaginatedResponse<Photo>> {
  const params = new URLSearchParams();

  if (filters.bbox) params.append('bbox', filters.bbox);
  if (filters.yearFrom !== undefined) params.append('yearFrom', filters.yearFrom.toString());
  if (filters.yearTo !== undefined) params.append('yearTo', filters.yearTo.toString());
  if (filters.era) params.append('era', filters.era);
  if (filters.zone) params.append('zone', filters.zone);
  if (filters.q) params.append('q', filters.q);
  if (filters.page) params.append('page', filters.page.toString());
  if (filters.pageSize) params.append('pageSize', filters.pageSize.toString());

  const response = await fetch(`${API_BASE_URL}/photos?${params.toString()}`);
  
  if (!response.ok) {
    throw new Error(`Error fetching photos: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Obtiene detalle de una foto
 */
export async function getPhotoById(id: number): Promise<Photo> {
  const response = await fetch(`${API_BASE_URL}/photos/${id}`);
  
  if (!response.ok) {
    throw new Error(`Error fetching photo ${id}: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Obtiene metadatos para filtros (épocas, zonas, rango años)
 */
export async function getFilterMetadata(): Promise<FilterMetadata> {
  const response = await fetch(`${API_BASE_URL}/photos/metadata/filters`);
  
  if (!response.ok) {
    throw new Error(`Error fetching filter metadata: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Obtiene capas del mapa
 */
export async function getMapLayers(): Promise<MapLayer[]> {
  const response = await fetch(`${API_BASE_URL}/layers`);

  if (!response.ok) {
    throw new Error(`Error fetching map layers: ${response.statusText}`);
  }

  return response.json();
}

// ============== ADMIN API ==============

/**
 * Helper para obtener headers de autenticación
 */
function getAuthHeaders(): HeadersInit {
  const token = getToken();
  if (!token) {
    throw new Error('No autenticado');
  }
  return {
    'Authorization': `Bearer ${token}`,
  };
}

/**
 * Crea una nueva foto
 */
export async function createPhoto(data: PhotoFormData, imageFile: File): Promise<Photo> {
  const formData = new FormData();

  // Añadir campos del formulario
  formData.append('title', data.title);
  if (data.description) formData.append('description', data.description);
  if (data.year) formData.append('year', data.year.toString());
  if (data.year_from) formData.append('year_from', data.year_from.toString());
  if (data.year_to) formData.append('year_to', data.year_to.toString());
  if (data.era) formData.append('era', data.era);
  if (data.zone) formData.append('zone', data.zone);
  formData.append('lat', data.lat.toString());
  formData.append('lng', data.lng.toString());
  if (data.source) formData.append('source', data.source);
  if (data.author) formData.append('author', data.author);
  if (data.rights) formData.append('rights', data.rights);
  if (data.tags && data.tags.length > 0) {
    formData.append('tags', JSON.stringify(data.tags));
  }

  // Añadir imagen
  formData.append('image', imageFile);

  const response = await fetch(`${API_BASE_URL}/photos`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error al crear la foto');
  }

  return response.json();
}

/**
 * Actualiza una foto existente
 */
export async function updatePhoto(id: number, data: PhotoFormData, imageFile?: File): Promise<Photo> {
  const formData = new FormData();

  // Añadir campos del formulario
  formData.append('title', data.title);
  if (data.description) formData.append('description', data.description);
  if (data.year) formData.append('year', data.year.toString());
  if (data.year_from) formData.append('year_from', data.year_from.toString());
  if (data.year_to) formData.append('year_to', data.year_to.toString());
  if (data.era) formData.append('era', data.era);
  if (data.zone) formData.append('zone', data.zone);
  formData.append('lat', data.lat.toString());
  formData.append('lng', data.lng.toString());
  if (data.source) formData.append('source', data.source);
  if (data.author) formData.append('author', data.author);
  if (data.rights) formData.append('rights', data.rights);
  if (data.tags && data.tags.length > 0) {
    formData.append('tags', JSON.stringify(data.tags));
  }

  // Añadir imagen si se proporciona
  if (imageFile) {
    formData.append('image', imageFile);
  }

  const response = await fetch(`${API_BASE_URL}/photos/${id}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error al actualizar la foto');
  }

  return response.json();
}

/**
 * Elimina una foto
 */
export async function deletePhoto(id: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/photos/${id}`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error al eliminar la foto');
  }
}
