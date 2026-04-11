import React from 'react';

export const ContactoPage: React.FC = () => {
  return (
    <div className="contacto-page">
      <div className="contacto-container">
        <header className="contacto-header">
          <h1>Sobre Zaragoza Historica</h1>
          <p>Un viaje visual por la historia de nuestra ciudad</p>
        </header>

        <section className="contacto-section">
          <div className="section-icon">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="16" cy="16" r="14" stroke="currentColor" strokeWidth="2"/>
              <path d="M16 8V16L22 20" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </div>
          <h2>El Proyecto</h2>
          <p>
            <strong>Zaragoza Historica</strong> es una aplicacion web que permite explorar la historia visual
            de Zaragoza a traves de fotografias historicas geolocalizadas en un mapa interactivo.
            El proyecto nace como Trabajo de Fin de Grado (TFG) del Grado Superior en Desarrollo
            de Aplicaciones Multiplataforma (DAM).
          </p>
          <p>
            La aplicacion combina tecnologias modernas de desarrollo web con servicios cartograficos
            historicos del Instituto Geografico Nacional (IGN), permitiendo superponer fotografias
            antiguas sobre mapas de diferentes epocas.
          </p>
        </section>

        <section className="contacto-section">
          <div className="section-icon">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M16 4L4 10V22L16 28L28 22V10L16 4Z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round"/>
              <path d="M4 10L16 16M16 16L28 10M16 16V28" stroke="currentColor" strokeWidth="2"/>
            </svg>
          </div>
          <h2>Tecnologias Utilizadas</h2>
          <div className="tech-grid">
            <div className="tech-item">
              <h3>Frontend</h3>
              <ul>
                <li>React 18 con TypeScript</li>
                <li>Vite como bundler</li>
                <li>Leaflet para mapas interactivos</li>
                <li>CSS puro para estilos</li>
              </ul>
            </div>
            <div className="tech-item">
              <h3>Backend</h3>
              <ul>
                <li>Python con FastAPI</li>
                <li>PostgreSQL con PostGIS</li>
                <li>Autenticacion JWT</li>
                <li>API REST documentada</li>
              </ul>
            </div>
            <div className="tech-item">
              <h3>Cartografia</h3>
              <ul>
                <li>Servicios WMS del IGN</li>
                <li>Ortofotos PNOA historicas</li>
                <li>Minutas cartograficas</li>
                <li>Vuelo Americano 1956-57</li>
              </ul>
            </div>
          </div>
        </section>

        <section className="contacto-section">
          <div className="section-icon">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M16 4C10.4772 4 6 8.47715 6 14C6 21 16 28 16 28C16 28 26 21 26 14C26 8.47715 21.5228 4 16 4Z" stroke="currentColor" strokeWidth="2"/>
              <circle cx="16" cy="14" r="4" stroke="currentColor" strokeWidth="2"/>
            </svg>
          </div>
          <h2>Fuentes de Datos</h2>
          <p>
            Las fotografias historicas provienen principalmente del archivo <strong>Zaragoza Antigua</strong>
            en Flickr, una coleccion comunitaria que recopila imagenes historicas de la ciudad.
            Todas las imagenes se utilizan con fines educativos y de divulgacion del patrimonio historico.
          </p>
          <p>
            Los mapas historicos son proporcionados por el <strong>Instituto Geografico Nacional (IGN)</strong>
            a traves de sus servicios WMS publicos, incluyendo ortofotos del Plan Nacional de
            Ortofotografia Aerea (PNOA) y cartografia historica.
          </p>
        </section>

        <section className="contacto-section">
          <div className="section-icon">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="16" cy="10" r="6" stroke="currentColor" strokeWidth="2"/>
              <path d="M6 28C6 22.4772 10.4772 18 16 18C21.5228 18 26 22.4772 26 28" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </div>
          <h2>Contacto</h2>
          <p>
            Este proyecto ha sido desarrollado como parte del Trabajo de Fin de Grado
            del ciclo formativo de Desarrollo de Aplicaciones Multiplataforma.
          </p>
          <div className="contact-info">
            <div className="contact-item">
              <span className="contact-label">Proyecto</span>
              <span className="contact-value">TFG DAM - Zaragoza Historica</span>
            </div>
            <div className="contact-item">
              <span className="contact-label">Ano</span>
              <span className="contact-value">2026</span>
            </div>
            <div className="contact-item">
              <span className="contact-label">Licencia</span>
              <span className="contact-value">Uso educativo</span>
            </div>
          </div>
        </section>

        <footer className="contacto-footer">
          <p>Zaragoza Historica - Explorando el pasado de nuestra ciudad</p>
        </footer>
      </div>
    </div>
  );
};
