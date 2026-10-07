# ETL plata
`transform_silver.py` convierte bronce a plata con SQL set-based: tipado, imputación de nulos, deduplicación y chequeo de FK.
Los rechazados van a `meta.etl_rejected` con su regla (E04, E06, E07, E10) y se resumen E05/E09.
La carga usa `INSERT ... ON CONFLICT DO UPDATE`, por lo que es reejecutable.
