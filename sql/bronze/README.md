# Scripts DDL Capa Bronce (`sql/bronze`)

Este directorio contiene los scripts DDL para la inicialización del esquema de auditoría y la capa cruda de ingesta.

---

## Estructura de Scripts y Orden de Ejecución

1. **`00_init_database.sql`:**
   - Habilita las extensiones necesarias en PostgreSQL (`uuid-ossp`).
   - Crea los esquemas de la arquitectura: `meta`, `bronze`, `silver`, `gold`.
   - Crea las tablas transversales de gobernanza:
     - `meta.etl_audit`: Linaje y auditoría de ejecución por fase.
     - `meta.etl_rejected`: Registro de filas descartadas y reglas de calidad infringidas.
   - Crea funciones de conversión robustas: `meta.to_date`, `meta.to_int`, `meta.to_num`.

2. **`01_tables_raw.sql`:**
   - Define las 7 tablas de ingesta en `bronze`: `competitions`, `clubs`, `players`, `games`, `player_valuations`, `appearances`, `game_events`.
   - Todas las columnas de datos se definen como `TEXT`.
   - Incorpora columnas técnicas de linaje: `_load_id`, `_loaded_at`, `_source_file`, `_row_id`.
