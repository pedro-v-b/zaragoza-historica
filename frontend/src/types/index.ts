// Types compartidos con el backend
export interface Photo {
  id: number;
  title: string;
  description?: string;
  year?: number;
  year_from?: number;
  year_to?: number;
  era?: string;
  zone?: string;
  lat: number;
  lng: number;
  image_url: string;
  thumb_url: string;
  source?: string;
  author?: string;
  rights?: string;
  tags?: string[];
  created_at: string;
  updated_at: string;
}

export interface PhotoFilters {
  bbox?: string;
  yearFrom?: number;
  yearTo?: number;
  era?: string;
  zone?: string;
  q?: string;
  page?: number;
  pageSize?: number;
  randomOrder?: boolean;
  seed?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface MapLayer {
  id: number;
  name: string;
  year?: number;
  type: 'plan' | 'ortho' | 'current';
  tile_url_template?: string;
  attribution?: string;
  min_zoom: number;
  max_zoom: number;
  bounds?: {
    north: number;
    south: number;
    east: number;
    west: number;
  };
  is_active: boolean;
  display_order: number;
}

export interface FilterMetadata {
  eras: string[];
  zones: string[];
  yearRange: {
    min: number;
    max: number;
  };
}

export interface BBox {
  minLng: number;
  minLat: number;
  maxLng: number;
  maxLat: number;
}

// Auth types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface UserResponse {
  id: number;
  username: string;
  role: string;
  is_active: boolean;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: UserResponse;
}

// Admin form types
export interface PhotoFormData {
  title: string;
  description?: string;
  year?: number;
  year_from?: number;
  year_to?: number;
  era?: string;
  zone?: string;
  lat: number;
  lng: number;
  source?: string;
  author?: string;
  rights?: string;
  tags?: string[];
}
