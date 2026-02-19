// API Client para comunicación con el backend
import { Photo, PhotoFilters, PaginatedResponse, MapLayer, FilterMetadata } from '../types';

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
