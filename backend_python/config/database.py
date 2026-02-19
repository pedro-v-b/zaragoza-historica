"""
Configuración de conexión a PostgreSQL + PostGIS
"""
import os
import sys
from typing import Optional
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

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
                
                cls._connection_pool = pool.SimpleConnectionPool(
                    minconn=1,
                    maxconn=20,
                    dsn=conn_string,
                    cursor_factory=RealDictCursor
                )
                
                cls._initialized = True
                print("[OK] Pool de conexiones PostgreSQL creado")
            except Exception as e:
                print(f"[ERROR] Error creando pool de conexiones: {e}")
                import traceback
                traceback.print_exc()
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
            print("[OK] Pool de conexiones cerrado")
    
    @classmethod
    async def test_connection(cls) -> bool:
        """Verifica la conexión a la base de datos"""
        try:
            conn = cls.get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT NOW(), PostGIS_Version() as postgis_version")
                result = cursor.fetchone()
                print(f"[OK] Conectado a PostgreSQL: {result['now']}, PostGIS: {result['postgis_version']}")
                cursor.close()
                return True
            finally:
                cls.return_connection(conn)
        except Exception as e:
            print(f"[ERROR] Error conectando a la base de datos: {e}")
            return False

# NO inicializar automáticamente - se hará de forma diferida
