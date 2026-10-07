# Capa bronce

- **Propósito:** aterrizar los 7 CSV tal cual vienen, sin correcciones.
- **Tablas:** `bronze.competitions`, `clubs`, `players`, `games`, `player_valuations`, `appearances`, `game_events`.
- **Tipado:** todo `TEXT`. Columnas de linaje: `_load_id`, `_loaded_at`, `_source_file`, `_row_id`.
- **Carga:** `TRUNCATE ... RESTART IDENTITY` + `COPY` por chunks (RNF01). Idempotente (RNF07).
- **Tolerancia a fallos (RNF09):** utf-8 con respaldo latin-1; líneas malformadas se omiten y se cuentan
  (el conteo es aproximado si hay saltos de línea dentro de campos entre comillas).
- **Columnas:** el DDL contempla el esquema habitual del dataset (Kaggle `davidcariboo/player-scores`).
  Se alinea por nombre de encabezado; columnas faltantes quedan NULL y las extra se ignoran con aviso.
- **Auditoría:** una fila por tabla en `meta.etl_audit` (leídas, descartadas, insertadas).
