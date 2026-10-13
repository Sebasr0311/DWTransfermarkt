# Módulo ETL Capa Plata (`etl/silver`)

Este paquete implementa las transformaciones de calidad, tipado, normalización y verificación de integridad referencial desde `bronze` hacia `silver`.

---

## Componentes

### `transform_silver.py`
- **Operaciones Set-Based:** Ejecuta transformaciones masivas en el motor PostgreSQL mediante consultas `INSERT INTO silver.* SELECT ... FROM bronze.*`.
- **Reglas de Calidad EDA (E01–E10):**
  - Tipado de datos (`INT`, `NUMERIC`, `DATE`, `BOOLEAN`).
  - Imputación de nulos a `0` para métricas deportivas (E01) y `'Desconocido'` para textos (E03).
  - Preservación de `NULL` para valores de mercado no informados (E02).
  - Conversión de fechas a ISO-8601 mediante `meta.to_date` (E04).
  - Deduplicación determinista mediante `DISTINCT ON` (E05).
  - Validación de rangos en minutos (`0–130`) y métricas no negativas (E06).
  - Verificación de claves foráneas contra entidades padre (E07).
  - Conversión segura de cadenas no numéricas a `NULL` mediante `meta.to_int` / `meta.to_num` (E09).
- **Idempotencia:** Utiliza `ON CONFLICT (...) DO UPDATE` permitiendo reejecutar el pipeline con total seguridad.
- **Auditoría:** Registra las filas procesadas en `meta.etl_audit` y los registros descartados con su motivo y regla en `meta.etl_rejected`.
