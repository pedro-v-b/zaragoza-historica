import { useState, useEffect, useCallback } from 'react';
import { Routes, Route } from 'react-router-dom';
import { Layout, Header } from './components/Layout';
import { Filters } from './components/Filters';
import { MapView } from './components/Map';
import { PhotoList } from './components/PhotoList';
import {
  AdminLogin,
  AdminDashboard,
  AdminLayout,
  ProtectedRoute,
} from './components/Admin';
import { Photo } from './types';
import { getPhotos } from './services/api';
import { useDebounce } from './hooks/useDebounce';
import './index.css';

// Componente principal del mapa (vista pública)
function MapApp() {
  // Estado de fotos y filtros
  const [photos, setPhotos] = useState<Photo[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [totalPages, setTotalPages] = useState(0);
  const [loading, setLoading] = useState(false);

  // Estado de filtros
  const [yearFrom, setYearFrom] = useState<number | undefined>();
  const [yearTo, setYearTo] = useState<number | undefined>();
  const [era, setEra] = useState<string | undefined>();
  const [zone, setZone] = useState<string | undefined>();
  const [searchQuery, setSearchQuery] = useState<string | undefined>();
  const [bbox, setBbox] = useState<string | undefined>();
  const [onlyInViewport, setOnlyInViewport] = useState(false);

  // Estado UI
  const [selectedPhotoId, setSelectedPhotoId] = useState<number | null>(null);
  const [centerOnPhoto, setCenterOnPhoto] = useState<Photo | null>(null);

  // Debounce del bbox para evitar demasiadas peticiones al mover el mapa
  const debouncedBbox = useDebounce(bbox, 800);

  // Cargar fotos cuando cambian los filtros
  useEffect(() => {
    loadPhotos();
  }, [yearFrom, yearTo, era, zone, searchQuery, page, debouncedBbox, onlyInViewport]);

  const loadPhotos = async () => {
    setLoading(true);
    try {
      const filters: any = {
        page,
        pageSize,
      };

      if (yearFrom) filters.yearFrom = yearFrom;
      if (yearTo) filters.yearTo = yearTo;
      if (era) filters.era = era;
      if (zone) filters.zone = zone;
      if (searchQuery) filters.q = searchQuery;
      if (onlyInViewport && debouncedBbox) filters.bbox = debouncedBbox;

      const response = await getPhotos(filters);
      setPhotos(response.items);
      setTotal(response.total);
      setTotalPages(response.totalPages);
    } catch (error) {
      console.error('Error loading photos:', error);
      setPhotos([]);
      setTotal(0);
      setTotalPages(0);
    } finally {
      setLoading(false);
    }
  };

  // Handler para cambio de filtros desde el panel de filtros
  const handleFilterChange = useCallback(
    (filters: {
      yearFrom?: number;
      yearTo?: number;
      era?: string;
      zone?: string;
      q?: string;
      onlyInViewport: boolean;
    }) => {
      setYearFrom(filters.yearFrom);
      setYearTo(filters.yearTo);
      setEra(filters.era);
      setZone(filters.zone);
      setSearchQuery(filters.q);
      setOnlyInViewport(filters.onlyInViewport);
      setPage(1); // Reset a primera página
    },
    []
  );

  // Handler para movimiento del mapa
  const handleMapMove = useCallback((newBbox: string) => {
    setBbox(newBbox);
  }, []);

  // Handler para click en foto (desde lista o mapa)
  const handlePhotoClick = useCallback((photo: Photo) => {
    setSelectedPhotoId(photo.id);
    setCenterOnPhoto(photo);
  }, []);

  // Handler para cambio de página
  const handlePageChange = useCallback((newPage: number) => {
    setPage(newPage);
  }, []);

  return (
    <Layout>
      {/* Sidebar izquierda: Filtros */}
      <div className="sidebar-left">
        <Header />
        <Filters onFilterChange={handleFilterChange} />
      </div>

      {/* Mapa central */}
      <MapView
        photos={photos}
        selectedPhotoId={selectedPhotoId}
        onMapMove={handleMapMove}
        onPhotoClick={handlePhotoClick}
        centerOnPhoto={centerOnPhoto}
      />

      {/* Sidebar derecha: Lista de resultados */}
      <div className="sidebar-right">
        <PhotoList
          photos={photos}
          total={total}
          page={page}
          pageSize={pageSize}
          totalPages={totalPages}
          loading={loading}
          selectedPhotoId={selectedPhotoId}
          onPhotoClick={handlePhotoClick}
          onPageChange={handlePageChange}
        />
      </div>
    </Layout>
  );
}

// App con rutas
function App() {
  return (
    <Routes>
      {/* Ruta pública - Mapa */}
      <Route path="/" element={<MapApp />} />

      {/* Rutas de administración */}
      <Route path="/admin/login" element={<AdminLogin />} />
      <Route
        path="/admin"
        element={
          <ProtectedRoute>
            <AdminLayout>
              <AdminDashboard />
            </AdminLayout>
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

export default App;
