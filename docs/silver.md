# Capa Plata: Limpieza, Tipado e Integridad Relacional

La capa **Silver** consolida los datos de Transfermarkt en un modelo relacional normalizado con tipos de datos nativos, claves primarias (`PK`), claves foráneas (`FK`), restricciones `CHECK` y reglas estrictas de calidad EDA (E01–E10).

---

## 1. Principios de Transformación y Calidad

- **Tipado Fuerte:** Los campos de texto crudo de bronce son transformados a sus tipos nativos de PostgreSQL (`INT`, `SMALLINT`, `NUMERIC`, `DATE`, `BOOLEAN`).
- **Nombres Claros de Columna:** Se eliminan ambigüedades de nombres reservados de SQL:
  - `date` en `games` y `game_events` → `game_date`.
  - `date` en `player_valuations` → `valuation_date`.
- **Derivación de Llaves de Negocio Faltantes:** Si `game_events.game_event_id` viene ausente en el archivo CSV fuente, se deriva de forma determinista mediante el hash `md5` de la combinación de campos del evento (`game_id`, `minute`, `type`, `club_id`, `player_id`, `description`).
- **Trazabilidad y Origen:** Cada tabla incluye:
  - `origin VARCHAR(10) NOT NULL DEFAULT 'real'` con restricción `CHECK (origin IN ('real', 'sintetico'))`.
  - `synthetic_batch UUID NULL` que asocia los registros expandidos a su lote de generación.

---

## 2. Orden de Carga y Resolución de Dependencias

Para asegurar que las restricciones de clave foránea (`FK`) se cumplan sin violaciones referenciales, la carga se ejecuta en el siguiente orden secuencial:
1. `silver.competitions` (entidad independiente raíz)
2. `silver.clubs` (depende de `competitions` para `domestic_competition_id`)
3. `silver.players` (depende de `clubs` para `current_club_id`)
4. `silver.games` (depende de `competitions` y de `clubs` para local y visitante)
5. `silver.appearances` (depende de `games`, `players` y `clubs`)
6. `silver.game_events` (depende de `games`, `clubs` y opcionalmente `players`)
7. `silver.player_valuations` (depende de `players` y opcionalmente `clubs`)

---

## 3. Implementación de Reglas EDA (E01–E10)

| ID | Regla de Calidad | Acción Técnica Implementada |
| :--- | :--- | :--- |
| **E01** | Nulos en métricas deportivas (goles, asistencias, tarjetas, minutos) | Imputación a `0` mediante `COALESCE(campo, 0)`. |
| **E02** | Nulos en valor de mercado | Preservar `NULL` (no imputar 0 para no falsear promedios). |
| **E03** | Nulos en textos descriptivos | Imputar `'Desconocido'` mediante función de normalización. |
| **E04** | Fechas en formatos mixtos | Conversión a `DATE` ISO-8601 vía `meta.to_date`; rechazar si no es interpretable. |
| **E05** | Duplicados por clave natural de negocio | Conservar el último registro válido con `DISTINCT ON (...)` y deduplicar en destino. |
| **E06** | Minutos fuera de rango válido o métricas negativas | Restricción `CHECK (minute BETWEEN 0 AND 130)` y tarjetas/goles `>= 0`. Filas fuera de rango se rechazan. |
| **E07** | Huérfanos sin padre referencial | En FKs obligatorias, la fila se descarta y se registra en `meta.etl_rejected`. En FKs opcionales, la FK queda `NULL` y se audita el caso. |
| **E08** | Codificación o delimitadores corruptos | Recuperación en ingesta Bronze (UTF-8 con fallback Latin-1). |
| **E09** | Textos en columnas numéricas | Conversión segura a `NULL` controlado (`meta.to_int` / `meta.to_num`) con registro de conteo. |
| **E10** | Clave de negocio nula o vacía | Rechazo inmediato de la fila y registro en auditoría. |

---

## 4. Idempotencia y Auditoría Transversal

- **Operación Set-Based:** Toda la transformación de Bronce a Plata se ejecuta mediante consultas SQL de conjunto (`INSERT INTO silver.* SELECT ... FROM bronze.*`), garantizando alto rendimiento y transaccionalidad.
- **Idempotencia:** La sentencia de inserción utiliza `ON CONFLICT (llave_primaria) DO UPDATE` para permitir reejecuciones completas o parciales sin duplicar registros.
- **Auditoría de Rechazos:** El esquema `meta` centraliza la gobernanza:
  - `meta.etl_audit`: Métricas de filas leídas, insertadas y tiempos de ejecución por tabla.
  - `meta.etl_rejected`: Registro de registros descartados con indicación de tabla, clave de negocio rechazada, regla infringida y motivo del descarte.
