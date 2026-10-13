# Módulo ETL Capa Oro (`etl/gold`)

Este paquete implementa la carga y actualización del modelo dimensional de **Constelación de Hechos (Kimball Bus)** en el esquema `gold`.

---

## Componentes

### 1. `load_gold.py`
Orquesta la transformación desde las tablas relacionales de `silver` hacia las entidades dimensionales en español:
- **Dimensiones Conformadas:**
  - `dim_fecha`: Genera el calendario analítico completo con atributos temporales y cálculo de temporada futbolística (julio–junio).
  - `dim_competicion`, `dim_club`, `dim_jugador`, `dim_arbitro`, `dim_tipo_evento`: Carga dimensiones maestras resolviendo claves sustitutas enteras (`*_key`) y garantizando unicidad en sus identificadores de negocio.
  - `dim_partido`: Dimensión de contexto de partido que resuelve claves foráneas hacia clubes (local/visitante), árbitros, competiciones y calendario, preservando el marcador y el flag `es_sintetico`.
- **Tablas de Hechos (Constelación):**
  - `hecho_rendimiento_jugador`: Carga métricas aditivas individuales por partido (`goles`, `asistencias`, `tarjetas_amarillas`, `tarjetas_rojas`, `minutos_jugados`) resolviendo claves foráneas sustitutas.
  - `hecho_eventos_partido`: Carga incidencias discretas de juego por lotes anuales; calcula la franja temporal `franja_15min` (0 a 6 para 90+), el atributo booleano `es_local` y asegura la asignación a las particiones físicas por rango en `fecha_key`.
  - `hecho_valoraciones_mercado`: Carga las tasaciones periódicas históricas de los futbolistas con su valor de mercado en euros (`valor_mercado_eur`).

### 2. `refresh_aggregations.py`
Ejecuta la actualización concurrente de las 5 vistas materializadas sin bloquear operaciones de lectura:
- `REFRESH MATERIALIZED VIEW CONCURRENTLY gold.agg_jugador_temporada_liga;`
- `REFRESH MATERIALIZED VIEW CONCURRENTLY gold.agg_club_temporada;`
- `REFRESH MATERIALIZED VIEW CONCURRENTLY gold.agg_eventos_15min;`
- `REFRESH MATERIALIZED VIEW CONCURRENTLY gold.agg_disciplina_arbitro;`
- `REFRESH MATERIALIZED VIEW CONCURRENTLY gold.agg_local_visitante;`
