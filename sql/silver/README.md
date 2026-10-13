# Scripts DDL Capa Plata (`sql/silver`)

Este directorio contiene los scripts DDL que estructuran el modelo relacional tipado y normalizado de la capa `silver`.

---

## Estructura de Scripts y Orden de Ejecución

1. **`02_tables_typed.sql`:**
   - Define las 7 tablas normalizadas en `silver`: `competitions`, `clubs`, `players`, `games`, `appearances`, `game_events`, `player_valuations`.
   - Asigna tipos nativos (`INT`, `SMALLINT`, `NUMERIC`, `DATE`, `BOOLEAN`).
   - Define claves primarias (`PK`) y restricciones `CHECK` para rangos válidos (minutos entre 0 y 130, métricas no negativas).
   - Incorpora columnas para trazabilidad de datos sintéticos: `origin` (`'real'` vs `'sintetico'`) y `synthetic_batch` (`UUID`).

2. **`03_foreign_keys.sql`:**
   - Aplica las restricciones de clave foránea (`FK`) entre tablas:
     - `clubs(domestic_competition_id)` → `competitions(competition_id)`
     - `players(current_club_id)` → `clubs(club_id)`
     - `games(competition_id)` → `competitions(competition_id)`
     - `games(home_club_id)` / `(away_club_id)` → `clubs(club_id)`
     - `appearances(game_id)`, `(player_id)`, `(player_club_id)` → tablas padre
     - `game_events(game_id)`, `(club_id)`, `(player_id)` → tablas padre
     - `player_valuations(player_id)`, `(current_club_id)` → tablas padre

3. **`07_add_origin_columns.sql`:**
   - Script complementario e idempotente para asegurar la existencia de las columnas `origin` y `synthetic_batch` en entornos preexistentes.
