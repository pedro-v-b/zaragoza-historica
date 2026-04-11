import React, { useState, useEffect, useCallback } from 'react';
import { Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Navbar } from './components/Navbar';
import { Filters } from './components/Filters';
import { MapView } from './components/Map';
import { PhotoList, PhotoDetail, PhotoFullscreen } from './components/PhotoList';
import { ContactoPage } from './components/Pages';
import { HistoricalContext } from './components/HistoricalContext/HistoricalContext';
import {
  AdminLogin,
  AdminDashboard,
  AdminLayout,
  ProtectedRoute,
} from './components/Admin';
import { Photo } from './types';
import { getPhotos, getMapPhotos } from './services/api';
import { useDebounce } from './hooks/useDebounce';
import './index.css';

// Componente principal del mapa (vista pública)
function MapApp() {
  // Estado de fotos y filtros
  const [mapPhotos, setMapPhotos] = useState<Photo[]>([]);
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
  const [era, setEra] = useState<string | undefined>();
  const [searchQuery, setSearchQuery] = useState<string | undefined>();
  const [bbox, setBbox] = useState<string | undefined>();
  const [onlyInViewport, setOnlyInViewport] = useState(false);

  // Semilla para el orden aleatorio de la lista lateral.
  // Regenerada en cada cambio de filtros para mezclar resultados, pero estable
  // al paginar para que una misma foto no aparezca en dos paginas distintas.
  const [listSeed, setListSeed] = useState<number>(() => Math.random() * 2 - 1);

  // Estado UI
  const [selectedPhotoId, setSelectedPhotoId] = useState<number | null>(null);
  const [centerOnPhoto, setCenterOnPhoto] = useState<Photo | null>(null);
  const [hoveredZone, setHoveredZone] = useState<string | null>(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [rightSidebarCollapsed, setRightSidebarCollapsed] = useState(false);
  const [showPhotoDetail, setShowPhotoDetail] = useState(false);
  const [detailPhoto, setDetailPhoto] = useState<Photo | null>(null);
  const [fullscreenPhoto, setFullscreenPhoto] = useState<Photo | null>(null);
  const [showHistoricalContext, setShowHistoricalContext] = useState(false);

  // Debounce del bbox para evitar demasiadas peticiones al mover el mapa
  const debouncedBbox = useDebounce(bbox, 800);

  // 1. Cargar TODAS las fotos para el MAPA
  useEffect(() => {
    loadMapPhotos();
  }, [yearFrom, yearTo, zone, era, searchQuery]);

  // Regenerar la semilla del orden aleatorio cada vez que cambian los filtros
  // (pero no al cambiar solo de pagina, para mantener la paginacion estable).
  useEffect(() => {
    setListSeed(Math.random() * 2 - 1);
  }, [yearFrom, yearTo, zone, era, searchQuery, debouncedBbox, onlyInViewport]);

  // 2. Cargar fotos para la LISTA lateral
  useEffect(() => {
    loadPhotos();
  }, [yearFrom, yearTo, zone, era, searchQuery, page, debouncedBbox, onlyInViewport, listSeed]);

  const loadMapPhotos = async () => {
    try {
      const filters: any = {};
      if (yearFrom) filters.yearFrom = yearFrom;
      if (yearTo) filters.yearTo = yearTo;
      if (zone) filters.zone = zone;
      if (era) filters.era = era;
      if (searchQuery) filters.q = searchQuery;

      const items = await getMapPhotos(filters);
      setMapPhotos(items);
    } catch (error) {
      console.error('Error loading map photos:', error);
    }
  };

  const loadPhotos = async () => {
    setLoading(true);
    try {
      const filters: any = { page, pageSize, randomOrder: true, seed: listSeed };
      if (yearFrom) filters.yearFrom = yearFrom;
      if (yearTo) filters.yearTo = yearTo;
      if (zone) filters.zone = zone;
      if (era) filters.era = era;
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
      era?: string;
      q?: string;
      onlyInViewport: boolean;
    }) => {
      setYearFrom(filters.yearFrom);
      setYearTo(filters.yearTo);
      setZone(filters.zone);
      setEra(filters.era);
      setSearchQuery(filters.q);
      setOnlyInViewport(filters.onlyInViewport);
      setPage(1);
      setShowHistoricalContext(false); // Cerrar contexto al cambiar filtros
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

  // Handler para click en foto desde el mapa: abre fullscreen directamente
  const handlePhotoClick = useCallback(async (photo: any) => {
    setSelectedPhotoId(photo.id);
    setCenterOnPhoto(photo);

    if (!photo.description && photo.id) {
      try {
        const { getPhotoById } = await import('./services/api');
        const fullPhoto = await getPhotoById(photo.id);
        setFullscreenPhoto(fullPhoto);
      } catch (error) {
        console.error('Error fetching full photo details:', error);
        setFullscreenPhoto(photo);
      }
    } else {
      setFullscreenPhoto(photo);
    }
  }, []);

  // Handler para click en foto desde la lista lateral: centra el mapa sobre el
  // marcador y abre su popup (MapView se encarga de expandir el cluster).
  const handleListPhotoClick = useCallback((photo: any) => {
    setSelectedPhotoId(photo.id);
    // Nueva referencia en cada click para forzar re-disparo del efecto aunque
    // sea la misma foto.
    setCenterOnPhoto({ ...photo });
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

  // Toggle sidebars
  const toggleSidebar = useCallback(() => {
    setSidebarCollapsed((prev) => !prev);
  }, []);

  const toggleRightSidebar = useCallback(() => {
    setRightSidebarCollapsed((prev) => !prev);
  }, []);

  // Escuchar el evento del botón de filtros de la navbar en móvil
  useEffect(() => {
    const handler = () => toggleSidebar();
    window.addEventListener('toggle-mobile-filters', handler);
    return () => window.removeEventListener('toggle-mobile-filters', handler);
  }, [toggleSidebar]);

  // Handler para cambio de página
  const handlePageChange = useCallback((newPage: number) => {
    setPage(newPage);
  }, []);

  return (
    <Layout>
      {/* Backdrop móvil: cierra la sidebar al tocar fuera */}
      {!sidebarCollapsed && (
        <div
          className="mobile-sidebar-backdrop"
          onClick={() => setSidebarCollapsed(true)}
          aria-hidden="true"
        />
      )}

      {/* Sidebar izquierda: Filtros (Colapsable) */}
      <div className={`sidebar-left ${sidebarCollapsed ? 'collapsed' : ''}`}>
        <div className="sidebar-header">
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
          photos={mapPhotos}
          selectedPhotoId={selectedPhotoId}
          onMapMove={handleMapMove}
          onPhotoClick={handlePhotoClick}
          centerOnPhoto={centerOnPhoto}
          selectedZone={zone}
          hoveredZone={hoveredZone}
          onZoneSelect={handleZoneSelect}
          yearFrom={yearFrom}
          yearTo={yearTo}
        />
        {rightSidebarCollapsed && (
          <button
            className="sidebar-open-btn sidebar-open-right"
            onClick={toggleRightSidebar}
            title="Mostrar panel"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M3 5H17M3 10H17M3 15H17" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </button>
        )}
      </div>

      {/* Sidebar derecha: Detalle / Contexto histórico / Lista */}
      <div className={`sidebar-right ${rightSidebarCollapsed ? 'collapsed' : ''}`}>
        <button
          className="sidebar-close-btn sidebar-close-right"
          onClick={toggleRightSidebar}
          title="Ocultar panel"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          </svg>
        </button>
        {showPhotoDetail && detailPhoto ? (
          <PhotoDetail
            photo={detailPhoto}
            onClose={handleCloseDetail}
            onBackToList={handleBackToList}
          />
        ) : showHistoricalContext && yearFrom !== undefined ? (
          <HistoricalContext
            year={yearFrom}
            onClose={() => setShowHistoricalContext(false)}
          />
        ) : (
          <>
            {yearFrom !== undefined && (
              <button
                className="history-context-toggle"
                onClick={() => setShowHistoricalContext(true)}
                title={`Ver contexto histórico del año ${yearFrom}`}
              >
                <span className="history-context-toggle-icon">📅</span>
                Contexto histórico de {yearFrom}
              </button>
            )}
            <PhotoList
              photos={photos}
              total={total}
              page={page}
              pageSize={pageSize}
              totalPages={totalPages}
              loading={loading}
              selectedPhotoId={selectedPhotoId}
              onPhotoClick={handleListPhotoClick}
              onPageChange={handlePageChange}
            />
          </>
        )}
      </div>

      {/* Modal fullscreen de foto */}
      {fullscreenPhoto && (
        <PhotoFullscreen
          photo={fullscreenPhoto}
          onClose={() => {
            setFullscreenPhoto(null);
            setSelectedPhotoId(null);
          }}
        />
      )}
    </Layout>
  );
}

// Wrapper con Navbar para páginas públicas
function PublicLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="app-with-navbar">
      <Navbar />
      <div className="app-content">
        {children}
      </div>
    </div>
  );
}

// App con rutas
function App() {
  return (
    <Routes>
      {/* Rutas públicas con Navbar */}
      <Route path="/" element={<PublicLayout><MapApp /></PublicLayout>} />
<Route path="/contacto" element={<PublicLayout><ContactoPage /></PublicLayout>} />

      {/* Rutas de administración (sin Navbar) */}
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
