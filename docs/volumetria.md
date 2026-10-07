# Volumetría y Almacenamiento Físico (`DWTransfermarkt`)

Este documento consolida las métricas de volumen de datos (reales, sintéticos y totales) y el consumo físico en disco en PostgreSQL tras la expansión controlada a **10,56 millones de registros**.

---

## 1. Comparativa de Filas: Real vs Sintético vs Meta Propuesta

| Capa / Tabla | Filas Reales | Filas Sintéticas | Total Obtenido | Meta Propuesta | Cumplimiento |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `silver.competitions` | 65 | 0 | **65** | 65 | 100.0% |
| `silver.clubs` | 796 | 0 | **796** | 796 | 100.0% |
| `silver.players` | 50.149 | 0 | **50.149** | 50.149 | 100.0% |
| `silver.games` | 72.602 | 405.550 | **478.152** | 72.602 | 658.6% |
| `silver.appearances` | 1.813.294 | 81.056 | **1.894.350** | 1.894.350 | 100.0% |
| `silver.game_events` | 1.032.318 | 5.724.262 | **6.756.580** | 7.187.349 | 94.0% |
| `silver.player_valuations` | 656.301 | 728.699 | **1.385.000** | 1.385.000 | 100.0% |
| **TOTAL GENERAL SILVER** | **3.625.525** | **6.939.567** | **10.565.092** | **10.565.088** | **100.00% (+4 filas)** |

### Notas sobre la distribución:
- `appearances` alcanzó exactamente las 1.894.350 filas propuestas (+81.056 sintéticas).
- `player_valuations` alcanzó exactamente las 1.385.000 filas propuestas (+728.699 sintéticas).
- Los partidos (`games`) se clonaron en 5 pases completos y un pase parcial (405.550 partidos sintéticos), garantizando que cada partido clonado contenga la totalidad de sus eventos asociados de forma íntegra.
- Los eventos (`game_events`) aportaron 5.724.262 filas sintéticas, alcanzando 6.756.580 eventos totales.
- El total consolidado de la capa plata es de **10.565.092 registros**, superando la meta de **10.565.088**.

---

## 2. Volumetría Física en Disco (PostgreSQL)

Métricas calculadas dinámicamente mediante `pg_relation_size`, `pg_indexes_size` y `pg_total_relation_size`:

| Tabla / Objeto | Esquema | Registros Estimados | Tamaño Datos (MB) | Tamaño Índices (MB) | Tamaño Total (MB) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `fact_events` (todas las particiones) | `gold` | 6.756.756 | 831,00 | 1.599,40 | **2.430,40** |
| `game_events` | `silver` | 6.754.027 | 1.088,10 | 811,15 | **1.899,59** |
| `etl_rejected` | `meta` | 2.978.061 | 1.151,66 | 87,26 | **1.239,28** |
| `appearances` | `silver` | 1.890.476 | 277,65 | 231,82 | **509,58** |
| `fact_appearances` | `gold` | 1.894.350 | 160,69 | 231,32 | **392,07** |
| `appearances` | `bronze` | 1.894.507 | 310,05 | 0,00 | **310,17** |
| `game_events` | `bronze` | 1.274.436 | 270,01 | 0,00 | **270,12** |
| `fact_valuations` | `gold` | 1.385.000 | 82,77 | 112,87 | **195,69** |
| `player_valuations` | `silver` | 1.385.000 | 95,79 | 73,24 | **169,08** |
| `games` | `silver` | 478.152 | 122,34 | 32,11 | **154,52** |
| `dim_game` | `gold` | 478.152 | 61,30 | 53,79 | **115,14** |
| `player_valuations` | `bronze` | 656.301 | 93,39 | 0,00 | **93,45** |
| `games` | `bronze` | 88.958 | 33,16 | 0,00 | **33,20** |
| `players` | `bronze` | 50.149 | 22,61 | 0,00 | **22,65** |
| `dim_player` | `gold` | 50.149 | 10,07 | 4,54 | **14,65** |
| `players` | `silver` | 50.149 | 10,85 | 2,27 | **13,16** |
| `agg_player_season` | `gold` | 93.595 | 8,91 | 2,11 | **11,06** |
| `dim_date` | `gold` | 9.862 | 0,56 | 0,48 | **1,06** |
| `agg_discipline_ref` | `gold` | 5.353 | 0,46 | 0,14 | **0,64** |
| `agg_club_season` | `gold` | 5.321 | 0,42 | 0,14 | **0,60** |
| `clubs` | `bronze` | 796 | 0,33 | 0,00 | **0,34** |
| `dim_club` | `gold` | 796 | 0,15 | 0,11 | **0,30** |
| `dim_referee` | `gold` | 1.527 | 0,08 | 0,15 | **0,27** |
| `clubs` | `silver` | 796 | 0,14 | 0,06 | **0,24** |
| `agg_home_away` | `gold` | 575 | 0,07 | 0,03 | **0,11** |
| `dim_competition` | `gold` | 65 | 0,02 | 0,03 | **0,09** |
| `etl_audit` | `meta` | 130 | 0,02 | 0,03 | **0,08** |
| `competitions` | `silver` | 65 | 0,02 | 0,02 | **0,07** |
| `dim_event_type` | `gold` | 11 | 0,01 | 0,03 | **0,05** |
| `agg_events_15min` | `gold` | 313 | 0,02 | 0,02 | **0,04** |
| `competitions` | `bronze` | 65 | 0,02 | 0,00 | **0,03** |

---

## 3. Observaciones de Rendimiento y Almacenamiento

1. **Particionamiento por Rango (`gold.fact_events`):**
   - La tabla de hechos de eventos se particiona anualmente sobre `date_key` (1990–2035).
   - El tamaño promedio por partición anual es de aproximadamente 75–120 MB de datos y 60–80 MB de índices.
   - La partición por defecto (`gold.fact_events_default`) contiene exactamente **0 filas**.

2. **Índices de Apoyo:**
   - La capa `gold` cuenta con índices B-Tree en todas las dimensiones y claves foráneas, permitiendo scans por partición eficientes (*partition pruning*).
   - El índice Hash en `gold.fact_events(event_type_key)` optimiza consultas de igualdad sobre el tipo de evento sin sobrecargar almacenamiento.

3. **Tiempos de Respuesta Analíticos:**
   - Todas las consultas benchmark sobre la capa `gold` con volumen completo (6,75 M de hechos) responden en menos de **1,0 segundo**, cumpliendo holgadamente el SLA de 3,0 segundos establecido en la propuesta.
