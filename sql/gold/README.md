# Capa ORO (SQL)
Modelo estrella: dimensiones con llave sustituta y tres hechos (`fact_events` particionada por rango de `date_key`).
Incluye índices B-Tree/Hash y vistas materializadas de agregación para Power BI.
Orden: 04 (tablas), 05 (índices y particiones), 06 (agregaciones).
