// API Client para comunicación con el backend
import { Photo, PhotoFilters, PaginatedResponse, FilterMetadata, PhotoFormData } from '../types';
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
  if (filters.randomOrder) params.append('randomOrder', 'true');
  if (filters.seed !== undefined) params.append('seed', filters.seed.toString());

  const response = await fetch(`${API_BASE_URL}/photos?${params.toString()}`);
  
  if (!response.ok) {
    throw new Error(`Error fetching photos: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Obtiene datos ligeros para el mapa (optimizado)
 */
export async function getMapPhotos(filters: any): Promise<any[]> {
  const params = new URLSearchParams();

  if (filters.yearFrom !== undefined) params.append('yearFrom', filters.yearFrom.toString());
  if (filters.yearTo !== undefined) params.append('yearTo', filters.yearTo.toString());
  if (filters.era) params.append('era', filters.era);
  if (filters.zone) params.append('zone', filters.zone);
  if (filters.q) params.append('q', filters.q);

  const response = await fetch(`${API_BASE_URL}/map?${params.toString()}`);
  
  if (!response.ok) {
    throw new Error(`Error fetching map photos: ${response.statusText}`);
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

// ============== WIKIPEDIA API ==============

export interface WikipediaArticle {
  pageid: number;
  title: string;
  lat: number;
  lon: number;
  extract: string;
  url: string;
  thumbnail: string | null;
}

export async function fetchWikipediaArticles(
  lat: number = 41.6488,
  lon: number = -0.8891,
  radius: number = 10000,
  limit: number = 200,
): Promise<WikipediaArticle[]> {
  const params = new URLSearchParams({
    lat: lat.toString(),
    lon: lon.toString(),
    radius: radius.toString(),
    limit: limit.toString(),
  });

  const response = await fetch(`${API_BASE_URL}/wikipedia?${params.toString()}`);
  if (!response.ok) {
    throw new Error(`Error fetching Wikipedia articles: ${response.statusText}`);
  }

  const data = await response.json();
  return data.articles;
}

// ============== MONUMENTS API ==============

export interface Monument {
  id: number;
  title: string;
  description: string;
  estilo: string;
  datacion: string;
  address: string;
  horario: string;
  image: string | null;
  url: string;
  lat: number;
  lon: number;
}

export async function fetchMonuments(): Promise<Monument[]> {
  const response = await fetch(`${API_BASE_URL}/monuments`);
  if (!response.ok) {
    throw new Error(`Error fetching monuments: ${response.statusText}`);
  }
  const data = await response.json();
  return data.monuments;
}

// ============== HISTORICAL CONTEXT API ==============

export interface HistoricalContext {
  year: number;
  alcalde: string | null;
  eventos: string[] | null;
  noticias_sociedad_sucesos: string[] | null;
  urbanismo: string[] | null;
  movilidad_transporte: string[] | null;
}

// ============== BUILDINGS / CATASTRO API ==============

export interface BuildingFeature {
  type: 'Feature';
  geometry: GeoJSON.Geometry;
  properties: {
    id: number;
    cadastral_ref: string | null;
    year_built: number | null;
    decade: number | null;
    current_use: string | null;
  };
}

export interface BuildingsGeoJSON {
  type: 'FeatureCollection';
  features: BuildingFeature[];
  metadata: {
    total: number;
    bbox: [number, number, number, number];
    zoom: number;
  };
}

export async function fetchBuildingsGeoJSON(
  bounds: {
    min_lng: number;
    min_lat: number;
    max_lng: number;
    max_lat: number;
  },
  zoom: number,
  yearFrom?: number,
  yearTo?: number,
  limit = 5000,
  signal?: AbortSignal
): Promise<BuildingsGeoJSON> {
  const params = new URLSearchParams({
    min_lng: bounds.min_lng.toString(),
    min_lat: bounds.min_lat.toString(),
    max_lng: bounds.max_lng.toString(),
    max_lat: bounds.max_lat.toString(),
    zoom: zoom.toString(),
    limit: limit.toString(),
  });

  if (yearFrom !== undefined) params.set('year_from', yearFrom.toString());
  if (yearTo !== undefined) params.set('year_to', yearTo.toString());

  const response = await fetch(`${API_BASE_URL}/buildings/geojson?${params.toString()}`, { signal });
  if (!response.ok) {
    throw new Error(`Error fetching buildings GeoJSON: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Obtiene el contexto histórico de todos los años disponibles (1900-2025)
 */
export async function getAllHistoricalContext(): Promise<HistoricalContext[]> {
  const response = await fetch(`${API_BASE_URL}/history`);

  if (!response.ok) {
    throw new Error(`Error fetching all historical context: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Obtiene el contexto histórico de Zaragoza para un año concreto
 */
export async function getHistoricalContext(year: number): Promise<HistoricalContext> {
  const response = await fetch(`${API_BASE_URL}/history/${year}`);

  if (!response.ok) {
    throw new Error(`Error fetching historical context for year ${year}: ${response.statusText}`);
  }

  return response.json();
}

// ============== ADMIN API ==============

/**
 * Helper para obtener headers de autenticación
 */
function getAuthHeaders(includeContentType: boolean = true): HeadersInit {
  const token = getToken();
  if (!token) {
    throw new Error('No autenticado');
  }
  const headers: HeadersInit = {
    'Authorization': `Bearer ${token}`,
  };
  if (includeContentType) {
    headers['Content-Type'] = 'application/json';
  }
  return headers;
}

/**
 * Helper para obtener solo el token (para FormData)
 */
function getAuthToken(): string {
  const token = getToken();
  if (!token) {
    throw new Error('No autenticado');
  }
  return token;
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
    headers: {
      'Authorization': `Bearer ${getAuthToken()}`,
    },
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
    headers: {
      'Authorization': `Bearer ${getAuthToken()}`,
    },
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
