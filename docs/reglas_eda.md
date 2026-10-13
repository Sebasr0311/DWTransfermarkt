# Reglas EDA y Criterios de Limpieza de Datos

Este documento define el catálogo de reglas de calidad y limpieza de datos (E01 a E10) aplicadas durante la transformación de la capa **Bronze** hacia la capa **Silver**, garantizando que la posterior carga dimensional en la capa **Gold** (Modelo de Constelación de Hechos) opere sobre datos íntegros, tipados y consistentes.

---

## 1. Catálogo de Reglas de Calidad (E01 – E10)

| ID | Regla | Acción Técnica | Dónde se Implementa |
|---|---|---|---|
| **E01** | Nulos en métricas deportivas acumulables (goles, asistencias, tarjetas, minutos jugados) | Imputar `0` | `COALESCE(columna, 0)` en consultas SQL de Silver (`appearances`, `game_events`). |
| **E02** | Nulos en valor de mercado | Mantener `NULL` | Preservado en `silver.players` y `silver.player_valuations`. No se imputa 0 para evitar distorsionar medias salariales y de cotización. |
| **E03** | Nulos en textos descriptivos (nombres, estadios, posiciones, árbitros) | Imputar `'Desconocido'` | Función helper `txt()` en Silver. |
| **E04** | Fechas en formatos mixtos o inconsistentes | Normalizar a formato ISO-8601 (`AAAA-MM-DD`); si no se puede interpretar, rechazar la fila | Función PL/pgSQL `meta.to_date()`. |
| **E05** | Duplicados por clave natural de negocio | Conservar el último registro cronológico o más completo | Cláusula `DISTINCT ON (...)` y deduplicación `ON CONFLICT` en Silver. |
| **E06** | Minuto fuera del rango de fútbol `[0, 130]` o métricas deportivas negativas | Rechazar la fila | Restricciones `CHECK (minute BETWEEN 0 AND 130)` y validación en carga Silver. |
| **E07** | Huérfanos sin padre referencial en claves foráneas | En FK obligatoria: rechazar la fila.<br>En FK opcional: colocar FK en `NULL` y auditar | Validaciones `EXISTS` en Silver; rechazos registrados en `meta.etl_rejected`. |
| **E08** | Codificación corrupta o delimitadores alterados en archivos de entrada | Reintento automático con codificación alternativa | Ingesta Bronze (`utf-8` con fallback a `latin-1`). |
| **E09** | Textos o caracteres no numéricos en columnas numéricas | Conversión controlada a `NULL` sin abortar el pipeline | Funciones `meta.to_int()` y `meta.to_num()` con resumen en `meta.etl_rejected`. |
| **E10** | Clave natural de negocio nula o vacía | Rechazar la fila | Filtro `WHERE business_key IS NOT NULL AND business_key <> ''` en Silver. |

---

## 2. Decisiones Arquitectónicas y Casos Especiales

1. **Gestión de Claves Foráneas Opcionales (E07):**
   - En relaciones de jerarquía flexible donde el dato del padre no siempre existe en el fútbol real (por ejemplo, `players.current_club_id` para jugadores libres/retirados, `clubs.domestic_competition_id` para clubes sin liga asignada, o `game_events.player_id` para incidencias colectivas o arbitrales), la fila se conserva con la clave en `NULL` y se emite un resumen E07 en `meta.etl_rejected`.
   - En claves foráneas estructurales obligatorias (como un evento sin partido asociado o una aparición sin jugador), la fila se descarta íntegramente.

2. **Diferenciación entre Métricas Deportivas y Atributos Descriptivos Numéricos:**
   - Solo las métricas de rendimiento deportivo (goles, asistencias, tarjetas y minutos) se imputan a `0` (E01).
   - Atributos cuantitativos de contexto (`squad_size`, `average_age`, `attendance`, `height_in_cm`) se mantienen en `NULL` si no están informados, impidiendo que un cero artificial distorsione cálculos agregados como la edad promedio de una plantilla o la altura promedio de una selección.

3. **Propagación hacia la Capa Gold (Constelación):**
   - Las reglas EDA garantizan que cuando los datos se cargan en `gold.hecho_rendimiento_jugador`, `gold.hecho_eventos_partido` y `gold.hecho_valoraciones_mercado`, el 100% de las claves foráneas hacia las dimensiones conformadas (`dim_fecha`, `dim_competicion`, `dim_club`, `dim_jugador`, `dim_arbitro`, `dim_tipo_evento`, `dim_partido`) se resuelven de forma determinista y sin registros huérfanos.
