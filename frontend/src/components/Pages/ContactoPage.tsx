import React from 'react';

export const ContactoPage: React.FC = () => {
  return (
    <div className="contacto-page">
      <div className="contacto-container">
        <header className="contacto-header">
          <h1>Acerca del proyecto</h1>
          <p>Archivo visual geolocalizado de la memoria urbana de Zaragoza</p>
        </header>

        <section className="contacto-section">
          <h2>Descripcion</h2>
          <p>
            <strong>Zaragoza Historica</strong> es una plataforma web cartografica que reune,
            organiza y pone a disposicion del publico fotografias historicas de la ciudad,
            asociando cada imagen a las coordenadas exactas del lugar donde fue tomada. El
            objetivo es facilitar la consulta visual del pasado urbano a traves de un unico
            punto de acceso: un mapa interactivo, navegable desde cualquier dispositivo.
          </p>
          <p>
            La aplicacion esta orientada tanto al publico general interesado en la evolucion
            de la ciudad como a investigadores, docentes, asociaciones vecinales y profesionales
            del patrimonio que necesiten acceder de forma estructurada a material grafico
            historico localizado con precision.
          </p>
        </section>

        <section className="contacto-section">
          <h2>Funcionalidades actuales</h2>
          <p>
            En su version presente, la plataforma permite explorar el fondo fotografico sobre
            el mapa de la ciudad, aplicar filtros por periodo cronologico, barrio o epoca
            historica, y consultar cada imagen en detalle junto con su ficha descriptiva.
            Ademas, incorpora capas cartograficas historicas procedentes de servicios oficiales,
            lo que habilita la comparacion directa entre el trazado actual y representaciones
            del territorio correspondientes a distintos momentos del pasado.
          </p>
        </section>

        <section className="contacto-section">
          <h2>Estado del desarrollo</h2>
          <p>
            La version accesible en la actualidad constituye una <strong>primera entrega
            publica</strong> del proyecto. Aunque ofrece un conjunto significativo de
            fotografias georreferenciadas y las herramientas necesarias para su consulta,
            se concibe como el punto de partida de un archivo en crecimiento continuo, que
            sera ampliado en sucesivas fases con nuevas fuentes, funcionalidades y tipologias
            documentales.
          </p>
        </section>

        <section className="contacto-section">
          <h2>Lineas de trabajo futuras</h2>
          <div className="roadmap-list">
            <div className="roadmap-item">
              <h3>Sistema de aportaciones ciudadanas</h3>
              <p>
                Se esta disenando un modulo de ingesta de fotografias que permitira a los
                usuarios contribuir con imagenes procedentes de archivos particulares o
                familiares, integrandolas en el mapa previa validacion. De este modo, el
                repositorio crecera gracias a la colaboracion directa de la ciudadania.
              </p>
            </div>
            <div className="roadmap-item">
              <h3>Ampliacion a otros documentos graficos</h3>
              <p>
                En proximas actualizaciones se incorporaran tipologias documentales
                adicionales, como cortometrajes, fragmentos de peliculas, videoclips y
                grabaciones audiovisuales rodadas en la ciudad, tambien geolocalizadas sobre
                los puntos en los que fueron registradas.
              </p>
            </div>
            <div className="roadmap-item">
              <h3>Cruce con fuentes textuales historicas</h3>
              <p>
                Esta previsto enriquecer cada ubicacion con noticias, sucesos y articulos
                procedentes de hemerotecas y publicaciones historicas, de forma que la consulta
                de un punto del mapa ofrezca no solo el material grafico disponible, sino
                tambien el contexto narrativo asociado al lugar.
              </p>
            </div>
          </div>
        </section>

        <section className="contacto-section">
          <h2>Objetivo a largo plazo</h2>
          <p>
            El proposito ultimo del proyecto es consolidar un <strong>archivo grafico
            geolocalizado de la memoria historica de Zaragoza</strong>, que integre en una
            misma interfaz imagen, audiovisual y fuente escrita. Se aspira a ofrecer un recurso
            publico, abierto y sostenido en el tiempo, util para la conservacion del patrimonio
            visual, la investigacion academica, la divulgacion educativa y el reconocimiento
            colectivo del entorno urbano.
          </p>
        </section>

        <section className="contacto-section">
          <h2>Origen academico</h2>
          <p>
            Zaragoza Historica se ha desarrollado como <strong>Trabajo de Fin de Grado</strong>
            del ciclo formativo de grado superior en Desarrollo de Aplicaciones Multiplataforma
            (DAM). El fondo fotografico inicial procede en su mayor parte del archivo comunitario
            <strong> Zaragoza Antigua</strong> alojado en Flickr, mientras que las capas
            cartograficas historicas son servidas por el
            <strong> Instituto Geografico Nacional</strong> a traves de sus servicios oficiales
            de mapas. Todo el contenido se utiliza con finalidad educativa, divulgativa y de
            puesta en valor del patrimonio.
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
          <p>Zaragoza Historica - Memoria visual de la ciudad sobre el mapa</p>
        </footer>
      </div>
    </div>
  );
};
