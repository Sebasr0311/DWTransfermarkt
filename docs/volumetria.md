# Volumetría y Almacenamiento Físico (`DWTransfermarkt`)

Este documento consolida las métricas de volumen de datos (reales, sintéticos y totales), el consumo físico de almacenamiento en disco en PostgreSQL y los tiempos de respuesta analítica tras la carga completa y la expansión controlada a **10,56 millones de registros**.

---

## 1. Comparativa de Filas: Real vs Sintético vs Meta Propuesta

### 1.1. Capa Plata (`silver`)

| Tabla / Entidad | Filas Reales | Filas Sintéticas | Total Obtenido | Meta Propuesta | Cumplimiento |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `silver.competitions` | 65 | 0 | **65** | 65 | 100.0% |
| `silver.clubs` | 796 | 0 | **796** | 796 | 100.0% |
| `silver.players` | 50.149 | 0 | **50.149** | 50.149 | 100.0% |
| `silver.games` | 72.602 | 405.550 | **478.152** | 72.602 | 658.6% |
| `silver.appearances` | 1.813.294 | 81.056 | **1.894.350** | 1.894.350 | 100.0% |
| `silver.game_events` | 1.032.318 | 5.724.262 | **6.756.580** | 7.187.349 | 94.0% |
| `silver.player_valuations` | 656.301 | 728.699 | **1.385.000** | 1.385.000 | 100.0% |
| **TOTAL GENERAL SILVER** | **3.625.525** | **6.939.567** | **10.565.092** | **10.565.088** | **100.00% (+4 filas)** |

### 1.2. Capa Oro (`gold` - Modelo Constelación)

| Entidad Dimensional | Tipo de Objeto | Registros Totales | Grano / Observación |
| :--- | :---: | :---: | :--- |
| `gold.hecho_eventos_partido` | Tabla de Hechos (Particionada) | **6.755.738** | Incidencias puntuales por minuto (1990–2035) |
| `gold.hecho_rendimiento_jugador` | Tabla de Hechos | **1.894.350** | Actuaciones acumuladas de jugador por partido |
| `gold.hecho_valoraciones_mercado` | Tabla de Hechos | **1.385.000** | Tasaciones de mercado históricas periódicas |
| `gold.dim_partido` | Dimensión de Contexto | **478.152** | Partidos jugados con marcadores y árbitros |
| `gold.dim_jugador` | Dimensión Conformada | **50.149** | Futbolistas únicos |
| `gold.dim_fecha` | Dimensión Calendario | **9.862** | Días calendario entre 1990 y 2026 |
| `gold.dim_club` | Dimensión Conformada | **796** | Clubes profesionales |
| `gold.dim_arbitro` | Dimensión Conformada | **1.527** | Árbitros oficiales |
| `gold.dim_competicion` | Dimensión Conformada | **65** | Ligas y copas |
| `gold.dim_tipo_evento` | Dimensión Conformada | **11** | Tipos de eventos reglamentarios |
| `gold.agg_jugador_temporada_liga` | Vista Materializada | **167.477** | Agregado jugador por torneo y temporada |
| `gold.agg_disciplina_arbitro` | Vista Materializada | **5.353** | Agregado disciplinario por árbitro |
| `gold.agg_club_temporada` | Vista Materializada | **5.321** | Agregado de clubes por temporada |
| `gold.agg_local_visitante` | Vista Materializada | **575** | Balance victorias local vs visitante |
| `gold.agg_eventos_15min` | Vista Materializada | **313** | Distribución de eventos en franjas de 15 min |

---

## 2. Volumetría Física en Disco (PostgreSQL)

Métricas medidas directamente en el motor PostgreSQL mediante `pg_relation_size`, `pg_indexes_size` y `pg_total_relation_size`:

| Tabla / Objeto | Esquema | Registros | Tamaño Datos (MB) | Tamaño Índices (MB) | Tamaño Total (MB) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `hecho_eventos_partido` (particiones) | `gold` | 6.755.738 | 831,03 | 1.596,69 | **2.428,35** |
| `game_events` | `silver` | 6.732.136 | 1.235,80 | 783,06 | **2.019,23** |
| `appearances` | `silver` | 1.889.943 | 314,56 | 217,09 | **531,76** |
| `etl_rejected` | `meta` | 1.018.618 | 406,22 | 29,84 | **436,20** |
| `hecho_rendimiento_jugador` | `gold` | 1.894.350 | 160,69 | 230,39 | **391,14** |
| `appearances` | `bronze` | 1.892.723 | 310,05 | 0,00 | **310,17** |
| `game_events` | `bronze` | 1.274.387 | 270,01 | 0,00 | **270,12** |
| `player_valuations` | `silver` | 1.385.000 | 140,61 | 75,45 | **216,12** |
| `dim_partido` | `gold` | 478.152 | 106,88 | 89,47 | **196,42** |
| `hecho_valoraciones_mercado` | `gold` | 1.385.000 | 82,77 | 112,57 | **195,40** |
| `player_valuations` | `bronze` | 656.301 | 93,39 | 0,00 | **93,45** |
| `games` | `silver` | 478.152 | 75,41 | 17,44 | **92,91** |
| `games` | `bronze` | 88.958 | 33,16 | 0,00 | **33,20** |
| `agg_jugador_temporada_liga` | `gold` | 167.477 | 16,94 | 7,04 | **24,01** |
| `players` | `bronze` | 50.149 | 22,61 | 0,00 | **22,65** |
| `dim_jugador` | `gold` | 50.149 | 10,07 | 4,54 | **14,65** |
| `players` | `silver` | 50.149 | 10,85 | 2,27 | **13,16** |
| `dim_fecha` | `gold` | 9.862 | 0,56 | 0,48 | **1,06** |
| `agg_disciplina_arbitro` | `gold` | 5.353 | 0,46 | 0,14 | **0,64** |
| `agg_club_temporada` | `gold` | 5.321 | 0,42 | 0,14 | **0,60** |
| `dim_club` | `gold` | 796 | 0,15 | 0,16 | **0,34** |
| `clubs` | `bronze` | 796 | 0,33 | 0,00 | **0,34** |
| `dim_arbitro` | `gold` | 1.527 | 0,08 | 0,15 | **0,27** |
| `clubs` | `silver` | 796 | 0,14 | 0,06 | **0,24** |
| `agg_local_visitante` | `gold` | 575 | 0,05 | 0,04 | **0,12** |
| `dim_competicion` | `gold` | 65 | 0,02 | 0,03 | **0,09** |
| `competitions` | `silver` | 65 | 0,02 | 0,02 | **0,07** |
| `etl_audit` | `meta` | 93 | 0,02 | 0,03 | **0,07** |
| `agg_eventos_15min` | `gold` | 313 | 0,02 | 0,02 | **0,06** |
| `dim_tipo_evento` | `gold` | 11 | 0,01 | 0,03 | **0,05** |
| `competitions` | `bronze` | 65 | 0,02 | 0,00 | **0,03** |

---

## 3. Estrategias de Rendimiento y Almacenamiento Físico

### 3.1. Particionamiento por Rango (`gold.hecho_eventos_partido`)
- La tabla de hechos masiva se particiona anualmente sobre `fecha_key` abarcando el intervalo 1990–2035.
- El motor aplica **partition pruning**, escaneando únicamente las particiones correspondientes a las temporadas consultadas.
- La partición por defecto (`gold.hecho_eventos_partido_default`) contiene exactamente **0 filas**, demostrando que el 100% de los eventos resuelven una partición anual válida.

### 3.2. Indexación Estratégica
- **Índices B-Tree:** Presentes en todas las dimensiones y en todas las claves foráneas de las tres tablas de hechos (`fecha_key`, `partido_key`, `jugador_key`, `club_key`, `competicion_key`, `arbitro_key`).
- **Índice Hash:** En `gold.hecho_eventos_partido(tipo_evento_key)` para consultas analíticas de alta selectividad sobre el tipo de incidencia con un bajo costo de almacenamiento.
- **Índices Únicos en Vistas Materializadas:** Permiten su refresco concurrente sin bloqueos de lectura (`REFRESH MATERIALIZED VIEW CONCURRENTLY`).

### 3.3. Tiempos de Respuesta Analíticos (Benchmarks OLAP)
Ejecutados sobre la base de datos completa con más de 6,75 millones de hechos cargados:

| Caso de Uso / Consulta Analítica | Requerimiento | Tiempo Medido | SLA Requerido | Cumplimiento |
| :--- | :---: | :---: | :---: | :---: |
| Top Goleadores por Temporada y Liga | RF01 | **0,017 s** | < 3,00 s | **ÓPTIMO** (176x más rápido) |
| Tabla de Posiciones y Puntos de Clubes | RF04 | **0,001 s** | < 3,00 s | **ÓPTIMO** (3000x más rápido) |
| Incidencias por Franja de 15 Minutos | RF07 | **0,302 s** | < 3,00 s | **ÓPTIMO** (10x más rápido) |
| Estadísticas de Tarjetas por Árbitro | RF06 | **0,002 s** | < 3,00 s | **ÓPTIMO** (1500x más rápido) |
| Balance Histórico Local vs Visitante | RF09 | **0,000 s** | < 3,00 s | **ÓPTIMO** (Instantáneo) |
| Cruce Masivo de Eventos por Competición | Escaneo / Join | **0,386 s** | < 3,00 s | **ÓPTIMO** (7.8x más rápido) |
