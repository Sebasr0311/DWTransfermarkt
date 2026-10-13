# Módulo ETL Capa Bronce (`etl/bronze`)

Este paquete orquesta la ingesta cruda de los 7 archivos CSV desde `data/raw/` hacia el esquema `bronze`.

---

## Componentes

### `extract_bronze.py`
- **Carga Masiva Eficiente:** Lee los archivos por bloques configurables (`CHUNK_SIZE`, por defecto 100.000 filas) y los inserta utilizando el comando `COPY` de PostgreSQL (RNF01).
- **Idempotencia:** Ejecuta `TRUNCATE ... RESTART IDENTITY` en cada tabla antes de la ingesta (RNF07).
- **Tolerancia a Fallos y Codificación:** Lee en `utf-8` con degradación automática a `latin-1` ante caracteres no reconocidos.
- **Conteo Preciso:** Implementa lectura estándar con `csv.reader` para contabilizar correctamente filas lógicas en archivos con campos multilínea entre comillas, evitando falsos descartes.
- **Alineación de Metadatos y Linaje:** Inyecta en cada fila `_load_id` (UUID), `_loaded_at`, `_source_file` y `_row_id`.
- **Auditoría:** Registra las métricas de filas leídas, descartadas e insertadas en `meta.etl_audit`.
