# ETL bronce
`extract_bronze.py` lee cada CSV de `data/raw/` por chunks (`CHUNK_SIZE`) y lo carga con `COPY` a `bronze.*`.
Prueba utf-8 y cae a latin-1; las líneas malformadas se omiten y se cuentan en `meta.etl_audit`.
Alinea las columnas por nombre de encabezado: las faltantes quedan NULL y las extra se ignoran (se reporta).
