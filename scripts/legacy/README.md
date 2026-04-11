# Scripts legacy

Scripts de mantenimiento y carga puntual usados durante el desarrollo
del proyecto. No forman parte del runtime de la aplicacion y se
ejecutan manualmente cuando hace falta.

| Script                     | Proposito                                                              |
|----------------------------|------------------------------------------------------------------------|
| `add_photo.py`             | Anadir una foto individual a la BD desde linea de comandos             |
| `assign_zones.py`          | Recalcular el campo `zone` de las fotos a partir de su geolocalizacion |
| `fix_metadata_years.py`    | Normalizar/arreglar los campos `year`, `year_from`, `year_to`          |
| `import_flickr.py`         | Importar fotos desde el scraper de Flickr                              |
| `prepare_barrios_sql.py`   | Generar un SQL con los poligonos de barrios                            |

Ejecutar siempre con el `.env` del proyecto cargado, por ejemplo:

```bash
python scripts/legacy/add_photo.py --help
```
