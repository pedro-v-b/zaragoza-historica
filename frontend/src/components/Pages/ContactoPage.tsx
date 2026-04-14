import React from 'react';

export const ContactoPage: React.FC = () => {
  return (
    <div className="contacto-page">
      <div className="contacto-container">
        <header className="contacto-header">
          <h1>Sobre Zaragoza Historica</h1>
          <p>Un archivo visual geolocalizado de la memoria de la ciudad</p>
        </header>

        <section className="contacto-section">
          <div className="section-icon">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M16 4C10.4772 4 6 8.47715 6 14C6 21 16 28 16 28C16 28 26 21 26 14C26 8.47715 21.5228 4 16 4Z" stroke="currentColor" strokeWidth="2"/>
              <circle cx="16" cy="14" r="4" stroke="currentColor" strokeWidth="2"/>
            </svg>
          </div>
          <h2>Que es este proyecto</h2>
          <p>
            <strong>Zaragoza Historica</strong> es un mapa interactivo que te permite viajar en
            el tiempo por las calles de Zaragoza. Pincha cualquier punto y descubre como era
            ese mismo lugar hace 50, 100 o mas de 150 anos, a traves de fotografias historicas
            situadas exactamente donde fueron tomadas.
          </p>
          <p>
            La idea es sencilla: recuperar la memoria visual de la ciudad y hacerla accesible
            a todo el mundo. Vecinos que quieren recordar como era su barrio, estudiantes que
            investigan el pasado, curiosos que descubren Zaragoza por primera vez... cualquiera
            puede usar este archivo para mirar la ciudad con otros ojos.
          </p>
        </section>

        <section className="contacto-section">
          <div className="section-icon">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="16" cy="16" r="14" stroke="currentColor" strokeWidth="2"/>
              <path d="M16 8V16L22 20" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </div>
          <h2>Como usarlo</h2>
          <p>
            Navega por el mapa como lo harias en cualquier mapa online: arrastra para moverte
            y usa la rueda del raton (o pellizca en el movil) para hacer zoom. Cada marcador
            es una fotografia historica; pulsalo para abrirla a pantalla completa y leer su
            descripcion, fecha y contexto.
          </p>
          <p>
            Desde el panel lateral puedes filtrar por <strong>ano</strong>, <strong>barrio</strong>
            o <strong>epoca historica</strong>, y con el boton <strong>Capas</strong> cambiar
            el mapa actual por ortofotos antiguas para comparar como se ha transformado la ciudad.
          </p>
        </section>

        <section className="contacto-section">
          <div className="section-icon">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M4 10L16 4L28 10L16 16L4 10Z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round"/>
              <path d="M4 16L16 22L28 16" stroke="currentColor" strokeWidth="2" strokeLinejoin="round"/>
              <path d="M4 22L16 28L28 22" stroke="currentColor" strokeWidth="2" strokeLinejoin="round"/>
            </svg>
          </div>
          <h2>Primera version: esto es solo el principio</h2>
          <p>
            Lo que ves hoy es una <strong>primera version</strong> del proyecto. Ya reune cientos
            de fotografias historicas situadas sobre el mapa, pero la idea a largo plazo es mucho
            mas ambiciosa: convertir Zaragoza Historica en un gran <strong>archivo de memoria
            historica</strong> de la ciudad, abierto y geolocalizado.
          </p>
        </section>

        <section className="contacto-section">
          <div className="section-icon">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M16 4V28M4 16H28" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              <circle cx="16" cy="16" r="12" stroke="currentColor" strokeWidth="2"/>
            </svg>
          </div>
          <h2>Proximas actualizaciones</h2>
          <div className="roadmap-list">
            <div className="roadmap-item">
              <h3>Sube tus propias fotografias</h3>
              <p>
                Estamos preparando un sistema para que cualquier usuario pueda aportar sus
                fotos antiguas y situarlas en el mapa. Esas imagenes que duermen en cajones
                familiares tambien forman parte de la memoria de Zaragoza.
              </p>
            </div>
            <div className="roadmap-item">
              <h3>Mas alla de la fotografia</h3>
              <p>
                Proximas versiones incluiran otros documentos graficos geolocalizados:
                <strong> cortometrajes</strong>, fragmentos de <strong>peliculas</strong>,
                <strong> videoclips</strong> y grabaciones historicas rodadas en la ciudad.
                Poder ver no solo una foto fija, sino la calle moviendose en el pasado.
              </p>
            </div>
            <div className="roadmap-item">
              <h3>Noticias y articulos del pasado</h3>
              <p>
                Cruzaremos los datos del mapa con <strong>noticias historicas</strong>,
                <strong> sucesos</strong> y <strong>articulos</strong> de la ciudad para que,
                al pulsar un punto, puedas leer tambien lo que alli ocurrio y lo que la prensa
                de la epoca conto sobre ese lugar.
              </p>
            </div>
          </div>
        </section>

        <section className="contacto-section">
          <div className="section-icon">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M6 26V10L16 4L26 10V26" stroke="currentColor" strokeWidth="2" strokeLinejoin="round"/>
              <path d="M12 26V16H20V26" stroke="currentColor" strokeWidth="2" strokeLinejoin="round"/>
            </svg>
          </div>
          <h2>El objetivo</h2>
          <p>
            Crear un <strong>archivo grafico geolocalizado de Zaragoza</strong> que reuna, en un
            unico lugar, imagenes, videos, noticias y testimonios asociados a cada rincon de la
            ciudad. Un proyecto vivo de memoria historica, construido entre todos, que permita
            recordar, aprender y reconocer la ciudad en la que vivimos.
          </p>
        </section>

        <section className="contacto-section">
          <div className="section-icon">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="16" cy="10" r="6" stroke="currentColor" strokeWidth="2"/>
              <path d="M6 28C6 22.4772 10.4772 18 16 18C21.5228 18 26 22.4772 26 28" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </div>
          <h2>Sobre el autor</h2>
          <p>
            Zaragoza Historica nace como <strong>Trabajo de Fin de Grado</strong> del ciclo
            formativo de Desarrollo de Aplicaciones Multiplataforma (DAM). Las fotografias
            actuales provienen en su mayoria del archivo comunitario <strong>Zaragoza Antigua</strong>
            en Flickr, y los mapas historicos los proporciona el <strong>Instituto Geografico
            Nacional (IGN)</strong>. Todos los contenidos se usan con fines educativos y de
            divulgacion del patrimonio.
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
              <span className="contact-label">Estado</span>
              <span className="contact-value">Primera version publica</span>
            </div>
          </div>
        </section>

        <footer className="contacto-footer">
          <p>Zaragoza Historica - La memoria visual de la ciudad, en un mapa</p>
        </footer>
      </div>
    </div>
  );
};
