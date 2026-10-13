# Scripts DDL Capa Oro (`sql/gold`)

Este directorio contiene los scripts DDL que definen el modelo multidimensional de **Constelación de Hechos (Kimball Bus)**, sus particiones físicas, índices de rendimiento y vistas materializadas de agregación.

---

## Estructura de Scripts y Orden de Ejecución

1. **`04_dimensions_facts.sql`:**
   - Define las 7 dimensiones conformadas en español: `dim_fecha`, `dim_competicion`, `dim_club`, `dim_jugador`, `dim_arbitro`, `dim_tipo_evento` y la dimensión de contexto `dim_partido`.
   - Implementa claves primarias sustitutas (`SERIAL` / `BIGSERIAL`) e índices de unicidad en claves naturales de negocio (`UNIQUE`).
   - Define las 3 tablas de hechos de la constelación:
     - `hecho_rendimiento_jugador` (Métricas aditivas acumuladas de partido).
     - `hecho_eventos_partido` (Factless fact table particionada por rango anual en `fecha_key`).
     - `hecho_valoraciones_mercado` (Métrica semi-aditiva periódica de valor de mercado).

2. **`05_indexes_partitions.sql`:**
   - Crea las particiones anuales por rango físico para `hecho_eventos_partido` (particiones 1990 a 2035 y partición default).
   - Crea índices B-Tree en todas las claves foráneas de las tablas de hechos y dimensiones.
   - Crea índice Hash en `hecho_eventos_partido(tipo_evento_key)` para optimizar filtros de igualdad en Power BI.

3. **`06_aggregations.sql`:**
   - Define las 5 vistas materializadas analíticas con filtro estricto `WHERE es_sintetico = FALSE`:
     - `agg_jugador_temporada_liga`: Rendimiento individual y ranking por torneo y temporada.
     - `agg_club_temporada`: Puntos, goles y valor de plantilla por club y temporada.
     - `agg_eventos_15min`: Frecuencia temporal de goles y tarjetas por franjas de 15 minutos.
     - `agg_disciplina_arbitro`: Tarjetas por partido y por 90 minutos por colegiado.
     - `agg_local_visitante`: Balance de victorias local vs visitante.
   - Crea índices únicos sobre cada vista para habilitar el refresco concurrente (`REFRESH MATERIALIZED VIEW CONCURRENTLY`).
