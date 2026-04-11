# Migraciones de base de datos

Este directorio contiene las migraciones incrementales del esquema,
aplicables sobre una base de datos ya inicializada con los scripts
de `backend_python/database/` (`01_schema.sql`, `02_seeds.sql`, etc.).

## Convención de nombres

`NNN_descripcion_breve.sql` — donde `NNN` es un entero de 3 digitos
consecutivo (001, 002, 003...). Ejemplos:

- `001_add_photo_tags_index.sql`
- `002_add_buildings_decade_column.sql`

## Reglas

1. **Nunca modifiques una migracion ya aplicada.** Si necesitas
   rectificar algo, crea una nueva migracion que lo corrija.
2. Cada migracion debe ser **idempotente** cuando sea posible
   (`CREATE TABLE IF NOT EXISTS`, `ALTER TABLE ... IF NOT EXISTS`...).
3. Incluye en la cabecera del fichero un comentario breve con la
   fecha y el objetivo de la migracion.
4. Registra cada migracion aplicada en la tabla `schema_migrations`
   (ver `000_schema_migrations.sql`).

## Aplicacion

```bash
python backend_python/database/migrations/apply.py
```

El script busca migraciones no aplicadas (comparando con la tabla
`schema_migrations`), las ejecuta en orden y registra su aplicacion.
