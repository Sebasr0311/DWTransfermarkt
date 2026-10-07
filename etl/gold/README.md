# ETL oro
`load_gold.py` puebla `dim_date`, dimensiones y hechos resolviendo llaves sustitutas (por año, idempotente).
Calcula `minute_bucket` (franjas de 15 min, 6 = 90+) e `is_home`, y crea las particiones del rango real de fechas.
`refresh_aggregations.py` refresca las vistas materializadas con `CONCURRENTLY`.
