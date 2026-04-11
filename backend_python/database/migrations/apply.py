"""
Aplicador simple de migraciones SQL.

Busca ficheros NNN_*.sql en este mismo directorio, comprueba cuales
no estan en la tabla schema_migrations y los ejecuta en orden.
"""
import os
import sys
import logging

import psycopg2
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("migrate")

MIGRATIONS_DIR = os.path.dirname(os.path.abspath(__file__))


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME") or os.getenv("POSTGRES_DB"),
        user=os.getenv("DB_USER") or os.getenv("POSTGRES_USER"),
        password=os.getenv("DB_PASSWORD") or os.getenv("POSTGRES_PASSWORD"),
    )


def list_migration_files() -> list[str]:
    files = [
        f for f in os.listdir(MIGRATIONS_DIR)
        if f.endswith(".sql") and f[:3].isdigit()
    ]
    return sorted(files)


def already_applied(conn) -> set[str]:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT to_regclass('public.schema_migrations')"
        )
        exists = cur.fetchone()[0] is not None
        if not exists:
            return set()
        cur.execute("SELECT version FROM schema_migrations")
        return {row[0] for row in cur.fetchall()}


def apply_migration(conn, filename: str) -> None:
    path = os.path.join(MIGRATIONS_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        sql = f.read()
    version = filename[:-4]
    with conn.cursor() as cur:
        cur.execute(sql)
        cur.execute(
            "INSERT INTO schema_migrations (version) VALUES (%s) "
            "ON CONFLICT (version) DO NOTHING",
            (version,),
        )
    conn.commit()
    logger.info("Aplicada migracion %s", version)


def main() -> int:
    try:
        conn = get_connection()
    except Exception as exc:
        logger.error("No se pudo conectar a la BD: %s", exc)
        return 1

    try:
        applied = already_applied(conn)
        pending = [f for f in list_migration_files() if f[:-4] not in applied]

        if not pending:
            logger.info("No hay migraciones pendientes")
            return 0

        for filename in pending:
            try:
                apply_migration(conn, filename)
            except Exception as exc:
                conn.rollback()
                logger.exception("Fallo aplicando %s: %s", filename, exc)
                return 1
        logger.info("Aplicadas %d migraciones", len(pending))
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
