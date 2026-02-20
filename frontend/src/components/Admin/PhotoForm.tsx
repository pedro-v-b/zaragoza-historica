import React, { useState, useEffect, useRef } from 'react';
import { Photo, PhotoFormData } from '../../types';
import { LocationPicker } from './LocationPicker';

interface PhotoFormProps {
  photo?: Photo | null;
  onSubmit: (data: PhotoFormData, imageFile?: File) => Promise<void>;
  onCancel: () => void;
  loading: boolean;
}

const initialFormData: PhotoFormData = {
  title: '',
  description: '',
  year: undefined,
  year_from: undefined,
  year_to: undefined,
  era: '',
  zone: '',
  lat: 41.6488,
  lng: -0.8891,
  source: '',
  author: '',
  rights: '',
  tags: [],
};

const ERAS = [
  'Siglo XIX',
  'Anos 1900',
  'Anos 10',
  'Anos 20',
  'Anos 30',
  'Anos 40',
  'Anos 50',
  'Anos 60',
  'Anos 70',
  'Anos 80',
  'Anos 90',
  'Anos 2000',
];

const ZONES = [
  // Distrito Centro
  'Casco Historico',
  'Centro',
  'San Pablo',
  'La Magdalena',
  'San Miguel',
  'Tenerias',
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
  // Distrito Torrero-La Paz
  'Torrero',
  'Venecia',
  'San Antonio de Padua',
  // Distrito Las Fuentes
  'Las Fuentes',
  // Distrito Almozara
  'La Almozara',
  'Las Armas',
  // Distrito Oliver-Valdefierro
  'Oliver',
  'Valdefierro',
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
  'Romareda',
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

export const PhotoForm: React.FC<PhotoFormProps> = ({
  photo,
  onSubmit,
  onCancel,
  loading,
}) => {
  const [formData, setFormData] = useState<PhotoFormData>(initialFormData);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [tagsInput, setTagsInput] = useState('');
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const isEditing = !!photo;

  useEffect(() => {
    if (photo) {
      setFormData({
        title: photo.title,
        description: photo.description || '',
        year: photo.year,
        year_from: photo.year_from,
        year_to: photo.year_to,
        era: photo.era || '',
        zone: photo.zone || '',
        lat: photo.lat,
        lng: photo.lng,
        source: photo.source || '',
        author: photo.author || '',
        rights: photo.rights || '',
        tags: photo.tags || [],
      });
      setTagsInput(photo.tags?.join(', ') || '');
      setImagePreview(photo.thumb_url);
    } else {
      setFormData(initialFormData);
      setTagsInput('');
      setImagePreview(null);
    }
    setImageFile(null);
    setError(null);
  }, [photo]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;

    setFormData((prev) => ({
      ...prev,
      [name]:
        name === 'year' || name === 'year_from' || name === 'year_to' || name === 'lat' || name === 'lng'
          ? value ? parseFloat(value) : undefined
          : value,
    }));
  };

  const handleLocationChange = (lat: number, lng: number) => {
    setFormData((prev) => ({
      ...prev,
      lat,
      lng,
    }));
  };

  const handleTagsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setTagsInput(value);

    const tags = value
      .split(',')
      .map((tag) => tag.trim())
      .filter((tag) => tag.length > 0);

    setFormData((prev) => ({ ...prev, tags }));
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validar tipo
      if (!file.type.startsWith('image/')) {
        setError('El archivo debe ser una imagen');
        return;
      }

      // Validar tamaño (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        setError('La imagen no puede superar los 10MB');
        return;
      }

      setImageFile(file);
      setError(null);

      // Crear preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validaciones
    if (!formData.title.trim()) {
      setError('El titulo es obligatorio');
      return;
    }

    if (!formData.lat || !formData.lng) {
      setError('Las coordenadas son obligatorias');
      return;
    }

    if (!isEditing && !imageFile) {
      setError('La imagen es obligatoria para nuevas fotos');
      return;
    }

    try {
      await onSubmit(formData, imageFile || undefined);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al guardar');
    }
  };

  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{isEditing ? 'Editar foto' : 'Nueva foto'}</h2>
          <button className="modal-close" onClick={onCancel}>&times;</button>
        </div>

        <form onSubmit={handleSubmit} className="photo-form">
          {error && <div className="admin-error">{error}</div>}

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="title">Titulo *</label>
              <input
                type="text"
                id="title"
                name="title"
                value={formData.title}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group full-width">
              <label htmlFor="description">Descripcion</label>
              <textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows={3}
              />
            </div>
          </div>

          <div className="form-row three-cols">
            <div className="form-group">
              <label htmlFor="year">Ano exacto</label>
              <input
                type="number"
                id="year"
                name="year"
                value={formData.year || ''}
                onChange={handleChange}
                min={1800}
                max={2030}
              />
            </div>
            <div className="form-group">
              <label htmlFor="year_from">Ano desde</label>
              <input
                type="number"
                id="year_from"
                name="year_from"
                value={formData.year_from || ''}
                onChange={handleChange}
                min={1800}
                max={2030}
              />
            </div>
            <div className="form-group">
              <label htmlFor="year_to">Ano hasta</label>
              <input
                type="number"
                id="year_to"
                name="year_to"
                value={formData.year_to || ''}
                onChange={handleChange}
                min={1800}
                max={2030}
              />
            </div>
          </div>

          <div className="form-row two-cols">
            <div className="form-group">
              <label htmlFor="era">Epoca</label>
              <select id="era" name="era" value={formData.era} onChange={handleChange}>
                <option value="">Seleccionar epoca</option>
                {ERAS.map((era) => (
                  <option key={era} value={era}>{era}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="zone">Zona</label>
              <select id="zone" name="zone" value={formData.zone} onChange={handleChange}>
                <option value="">Seleccionar zona</option>
                {ZONES.map((zone) => (
                  <option key={zone} value={zone}>{zone}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Selector de ubicacion en mapa */}
          <LocationPicker
            lat={formData.lat}
            lng={formData.lng}
            onLocationChange={handleLocationChange}
          />

          {/* Campos ocultos de lat/lng para el formulario */}
          <div className="form-row two-cols" style={{ display: 'none' }}>
            <div className="form-group">
              <label htmlFor="lat">Latitud *</label>
              <input
                type="number"
                id="lat"
                name="lat"
                value={formData.lat}
                onChange={handleChange}
                step="0.000001"
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="lng">Longitud *</label>
              <input
                type="number"
                id="lng"
                name="lng"
                value={formData.lng}
                onChange={handleChange}
                step="0.000001"
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="image">
                Imagen {!isEditing && '*'}
              </label>
              <input
                type="file"
                id="image"
                ref={fileInputRef}
                accept="image/*"
                onChange={handleImageChange}
              />
              {imagePreview && (
                <div className="image-preview">
                  <img src={imagePreview} alt="Preview" />
                </div>
              )}
            </div>
          </div>

          <div className="form-row three-cols">
            <div className="form-group">
              <label htmlFor="source">Fuente</label>
              <input
                type="text"
                id="source"
                name="source"
                value={formData.source}
                onChange={handleChange}
                placeholder="Ej: Archivo Municipal"
              />
            </div>
            <div className="form-group">
              <label htmlFor="author">Autor</label>
              <input
                type="text"
                id="author"
                name="author"
                value={formData.author}
                onChange={handleChange}
              />
            </div>
            <div className="form-group">
              <label htmlFor="rights">Derechos</label>
              <input
                type="text"
                id="rights"
                name="rights"
                value={formData.rights}
                onChange={handleChange}
                placeholder="Ej: Dominio publico"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group full-width">
              <label htmlFor="tags">Tags (separados por coma)</label>
              <input
                type="text"
                id="tags"
                name="tags"
                value={tagsInput}
                onChange={handleTagsChange}
                placeholder="Ej: plaza, tranvia, fiestas"
              />
            </div>
          </div>

          <div className="form-actions">
            <button type="button" className="btn btn-secondary" onClick={onCancel}>
              Cancelar
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Guardando...' : isEditing ? 'Actualizar' : 'Crear foto'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
