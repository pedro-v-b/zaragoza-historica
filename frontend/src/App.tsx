import { useState, useEffect, useCallback } from 'react';
import { Routes, Route } from 'react-router-dom';
import { Layout, Header } from './components/Layout';
import { Filters } from './components/Filters';
import { MapView } from './components/Map';
import { PhotoList, PhotoDetail } from './components/PhotoList';
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
  const [zone, setZone] = useState<string | undefined>();
  const [searchQuery, setSearchQuery] = useState<string | undefined>();
  const [bbox, setBbox] = useState<string | undefined>();
  const [onlyInViewport, setOnlyInViewport] = useState(false);

  // Estado UI
  const [selectedPhotoId, setSelectedPhotoId] = useState<number | null>(null);
  const [centerOnPhoto, setCenterOnPhoto] = useState<Photo | null>(null);
  const [hoveredZone, setHoveredZone] = useState<string | null>(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [showPhotoDetail, setShowPhotoDetail] = useState(false);
  const [detailPhoto, setDetailPhoto] = useState<Photo | null>(null);

  // Debounce del bbox para evitar demasiadas peticiones al mover el mapa
  const debouncedBbox = useDebounce(bbox, 800);

  // Cargar fotos cuando cambian los filtros
  useEffect(() => {
    loadPhotos();
  }, [yearFrom, yearTo, zone, searchQuery, page, debouncedBbox, onlyInViewport]);

  const loadPhotos = async () => {
    setLoading(true);
    try {
      const filters: any = {
        page,
        pageSize,
      };

      if (yearFrom) filters.yearFrom = yearFrom;
      if (yearTo) filters.yearTo = yearTo;
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
      zone?: string;
      q?: string;
      onlyInViewport: boolean;
    }) => {
      setYearFrom(filters.yearFrom);
      setYearTo(filters.yearTo);
      setZone(filters.zone);
      setSearchQuery(filters.q);
      setOnlyInViewport(filters.onlyInViewport);
      setPage(1); // Reset a primera página
    },
    []
  );

  // Handler para selección de zona desde el mapa o filtros
  const handleZoneSelect = useCallback((zoneName: string | null) => {
    setZone(zoneName || undefined);
    setPage(1);
  }, []);

  // Handler para movimiento del mapa
  const handleMapMove = useCallback((newBbox: string) => {
    setBbox(newBbox);
  }, []);

  // Handler para click en foto (desde lista o mapa)
  const handlePhotoClick = useCallback((photo: Photo) => {
    setSelectedPhotoId(photo.id);
    setCenterOnPhoto(photo);
    setDetailPhoto(photo);
    setShowPhotoDetail(true);
  }, []);

  // Handler para cerrar detalle
  const handleCloseDetail = useCallback(() => {
    setShowPhotoDetail(false);
    setDetailPhoto(null);
    setSelectedPhotoId(null);
  }, []);

  // Handler para volver a la lista
  const handleBackToList = useCallback(() => {
    setShowPhotoDetail(false);
  }, []);

  // Toggle sidebar
  const toggleSidebar = useCallback(() => {
    setSidebarCollapsed((prev) => !prev);
  }, []);

  // Handler para cambio de página
  const handlePageChange = useCallback((newPage: number) => {
    setPage(newPage);
  }, []);

  return (
    <Layout>
      {/* Sidebar izquierda: Filtros (Colapsable) */}
      <div className={`sidebar-left ${sidebarCollapsed ? 'collapsed' : ''}`}>
        <div className="sidebar-header">
          <Header />
          <button
            className="sidebar-close-btn"
            onClick={toggleSidebar}
            title="Ocultar filtros"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </button>
        </div>
        <Filters
          onFilterChange={handleFilterChange}
          selectedZone={zone}
          onZoneHover={setHoveredZone}
          onZoneSelect={handleZoneSelect}
        />
      </div>

      {/* Mapa central */}
      <div className="map-wrapper">
        {sidebarCollapsed && (
          <button
            className="sidebar-open-btn"
            onClick={toggleSidebar}
            title="Mostrar filtros"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M3 5H17M3 10H17M3 15H17" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </button>
        )}
        <MapView
          photos={photos}
          selectedPhotoId={selectedPhotoId}
          onMapMove={handleMapMove}
          onPhotoClick={handlePhotoClick}
          centerOnPhoto={centerOnPhoto}
          selectedZone={zone}
          hoveredZone={hoveredZone}
          onZoneSelect={handleZoneSelect}
        />
      </div>

      {/* Sidebar derecha: Lista de resultados o Detalle */}
      <div className="sidebar-right">
        {showPhotoDetail && detailPhoto ? (
          <PhotoDetail
            photo={detailPhoto}
            onClose={handleCloseDetail}
            onBackToList={handleBackToList}
          />
        ) : (
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
        )}
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
