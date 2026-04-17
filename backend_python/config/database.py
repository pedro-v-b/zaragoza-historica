"""
Configuración de conexión a PostgreSQL + PostGIS
"""
import os
import sys
import logging
from typing import Optional
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Configurar codificación en Windows antes de todo
if sys.platform == 'win32':
    # Establecer variables de entorno para PostgreSQL
    os.environ['PGCLIENTENCODING'] = 'UTF8'
    # Intentar configurar el locale
    try:
        import locale
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        except:
            pass

load_dotenv()

class Database:
    """Gestor de conexiones a PostgreSQL"""
    
    _connection_pool: Optional[pool.SimpleConnectionPool] = None
    _initialized = False
    _conn_params = None
    
    @classmethod
    def _get_conn_params(cls):
        """Obtiene los parámetros de conexión"""
        if cls._conn_params is None:
            cls._conn_params = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': int(os.getenv('DB_PORT', '5432')),
                'database': os.getenv('DB_NAME', 'zaragoza_historica'),
                'user': os.getenv('DB_USER', 'zaragoza_user'),
                'password': os.getenv('DB_PASSWORD', 'zaragoza_pass'),
            }
        return cls._conn_params
    
    @classmethod
    def initialize(cls):
        """Inicializa el pool de conexiones (lazy initialization)"""
        if cls._initialized:
            return
        
        if cls._connection_pool is None:
            try:
                params = cls._get_conn_params()
                
                # Crear connection string explícita para evitar issues de encoding
                conn_string = (
                    f"host={params['host']} "
                    f"port={params['port']} "
                    f"dbname={params['database']} "
                    f"user={params['user']} "
                    f"password={params['password']} "
                    f"client_encoding=UTF8"
                )
                
                minconn = int(os.getenv('DB_POOL_MIN', '1'))
                maxconn = int(os.getenv('DB_POOL_MAX', '20'))
                if maxconn < minconn:
                    maxconn = minconn

                cls._connection_pool = pool.SimpleConnectionPool(
                    minconn=minconn,
                    maxconn=maxconn,
                    dsn=conn_string,
                    cursor_factory=RealDictCursor
                )
                
                cls._initialized = True
                logger.info("Pool de conexiones PostgreSQL creado (min=%d, max=%d)", minconn, maxconn)
            except Exception as e:
                logger.exception("Error creando pool de conexiones: %s", e)
                raise
    
    @classmethod
    def get_connection(cls):
        """Obtiene una conexión del pool"""
        if not cls._initialized:
            cls.initialize()
        return cls._connection_pool.getconn()
    
    @classmethod
    def return_connection(cls, conn):
        """Devuelve una conexión al pool"""
        if cls._connection_pool is not None:
            cls._connection_pool.putconn(conn)
    
    @classmethod
    def close_all(cls):
        """Cierra todas las conexiones del pool"""
        if cls._connection_pool is not None:
            cls._connection_pool.closeall()
            logger.info("Pool de conexiones cerrado")
    
    @classmethod
    async def test_connection(cls) -> bool:
        """Verifica la conexión a la base de datos"""
        try:
            conn = cls.get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT NOW(), PostGIS_Version() as postgis_version")
                result = cursor.fetchone()
                logger.info("Conectado a PostgreSQL: %s, PostGIS: %s", result['now'], result['postgis_version'])
                cursor.close()
                return True
            finally:
                cls.return_connection(conn)
        except Exception as e:
            logger.error("Error conectando a la base de datos: %s", e)
            return False

# NO inicializar automáticamente - se hará de forma diferida
