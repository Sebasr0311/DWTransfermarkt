# Expansión Controlada de Datos a 10,5 M de Registros

Este documento describe el método, justificación, arquitectura, integridad, reversibilidad y limitaciones de la expansión controlada de datos implementada en el Data Warehouse `DWTransfermarkt`.

---

## 1. Justificación y Objetivo

El Data Warehouse `DWTransfermarkt` fue cargado y validado a partir de los datos reales extraídos de la plataforma Transfermarkt (vía datasets abiertos de Kaggle / `dcaribou/transfermarkt-datasets`). 

El estado base real en la capa `silver` suma **3.625.525 registros** distribuidos en 7 tablas de negocio. Sin embargo, los requerimientos arquitectónicos de la propuesta estipulan una prueba de estrés de volumetría objetivo de **10.565.088 registros**, con el fin de evaluar:
- Particionamiento por rango en tablas de hechos masivas (`gold.fact_events`).
- Desempeño y concurrencia en vistas materializadas (`gold.agg_*`).
- Tiempos de respuesta sub-segundo en consultas analíticas y reportes OLAP.
- Comportamiento de índices y consumo físico en disco bajo volúmenes de producción a gran escala.

Para cubrir la brecha de **6.939.563 registros** sin contaminar ni degradar los datos reales, se implementó una **estrategia de clonación controlada, determinista, trazable y 100% reversible**.

---

## 2. Metodología: Clonación Controlada

A diferencia de generadores sintéticos puramente aleatorios que generan datos incoherentes o violan distribuciones reales (por ejemplo, partidos de 50 goles o jugadores nacidos en el año 3000), la **clonación controlada** conserva fielmente las propiedades estadísticas y distribuciones del fútbol profesional:

1. **Partidos Sintéticos (`silver.games`):**
   - Se seleccionan partidos reales como plantilla determinista.
   - Cada clon conserva exactamente la competición, clubes contendientes, temporada, fecha del partido, marcador (goles local y visitante), estadio y árbitro original.
   - Solo se asigna un nuevo identificador en un rango reservado no solapable: `game_id >= 900.000.000` (`900000000 + idx`).

2. **Eventos de Partido (`silver.game_events`):**
   - Constituye la fuente principal del volumen (~5,72 millones de registros sintéticos).
   - Cada partido sintético clona los eventos de su partido real de origen.
   - Se genera una clave de negocio única con prefijo `SYN-{pase}-{game_event_id_original}`.
   - Se preserva el tipo de evento (gol, tarjeta, sustitución, etc.), club involucrado, jugador principal y jugadores secundarios (asistencia, sustitución).
   - Para evitar duplicidad exacta en la dimensión temporal del partido, se aplica una perturbación acotada del minuto: $\Delta \in [-3, +3]$ minutos, restringido estrictamente mediante `mod(hashtext(...), 7) - 3` y acotado al rango válido de fútbol `[0, 130]` minutos.

3. **Apariciones de Jugadores (`silver.appearances`):**
   - Se completan 81.056 apariciones sintéticas (alcanzando el objetivo de propuesta de 1.894.350 filas en plata) clonando alineaciones de los partidos sintéticos.
   - Las claves de negocio adoptan el prefijo `SYN-1-{appearance_id_original}`.
   - Se conservan minutos jugados, goles, asistencias y tarjetas registradas.

4. **Valoraciones de Mercado (`silver.player_valuations`):**
   - Se completan 728.699 valoraciones sintéticas (alcanzando 1.385.000 filas en plata) para jugadores reales existentes.
   - Se generan en fechas **no utilizadas previamente** por el jugador (respetando la clave primaria `(player_id, valuation_date)`), evaluando fechas candidatas desplazadas a intervalos quincenales.
   - El valor de mercado sintético se deriva del valor real vecino multiplicado por un factor determinista en el rango $[0.95, 1.05]$:
     $$\text{valor\_sintetico} = \text{round}(\text{valor\_real} \times (0.95 + 0.10 \times \text{factor\_hash}), 2)$$
   - Los valores nunca son negativos y mantienen la curva de valuación del futbolista.

---

## 3. Trazabilidad y Honestidad Técnica

Todo registro en el sistema cuenta con etiquetado explícito y permanente:
- **Capa Plata (`silver`):**
  - Columna `origin VARCHAR(10) NOT NULL DEFAULT 'real'` con restricción `CHECK (origin IN ('real', 'sintetico'))`.
  - Columna `synthetic_batch UUID NULL` que almacena el identificador único del lote de expansión (`run_id`).
- **Capa Oro (`gold`):**
  - Columna `is_synthetic BOOLEAN NOT NULL DEFAULT FALSE` en `dim_game`, `fact_events`, `fact_appearances` y `fact_valuations`.
- **Auditoría (`meta.etl_audit`):**
  - Cada fase de la expansión se audita con `layer = 'expand'`, identificando filas leídas, insertadas y estado `OK`.

---

## 4. Garantía de Integridad Referencial y Calidad

1. **Cero Huérfanos:**
   - Todos los partidos sintéticos apuntan a competiciones y clubes reales válidos.
   - Todos los eventos y apariciones sintéticos apuntan a partidos sintéticos existentes y a jugadores/clubes reales existentes.
   - Todas las valoraciones apuntan a jugadores reales existentes.
   - En la capa dimensional `gold`, todas las dimensiones (`dim_competition`, `dim_club`, `dim_player`, `dim_referee`, `dim_event_type`) y dimensiones de contexto (`dim_date`, `dim_game`) resuelven el 100% de las llaves sustitutas.
2. **Cero Duplicados:**
   - Se respeta estrictamente la unicidad de las claves primarias y de negocio en cada capa.
3. **Aislamiento Analítico:**
   - Las vistas materializadas de negocio (`gold.agg_player_season`, `gold.agg_club_season`, `gold.agg_events_15min`, `gold.agg_discipline_ref`, `gold.agg_home_away`) filtran explícitamente `is_synthetic = FALSE`.
   - Las métricas de goleadores, puntos de campeonato, minutos jugados y tarjetas coinciden **bit a bit** antes y después de la expansión.
4. **Verificación por Checksum:**
   - Cada tabla real se valida mediante conteo y suma de hash `sum(hashtext(ROW(...)::text)::bigint)` sobre las columnas reales.

---

## 5. Reversibilidad e Idempotencia

El proceso es completamente idempotente y reversible:
- **Idempotencia:** Antes de ejecutar cualquier generación, `expand` ejecuta automáticamente un rollback de registros sintéticos anteriores.
- **Rollback:** El comando:
  ```bash
  python -m etl.run_pipeline --layer expand --rollback
  ```
  elimina en cascada todos los registros con `origin = 'sintetico'` en `silver` y con `is_synthetic = TRUE` en `gold`, refresca las agregaciones y restituye la base de datos a sus **3.625.525 registros reales intactos**.

---

## 6. Limitaciones del Conjunto Sintético

- **Propósito:** Los datos sintéticos fueron creados exclusivamente para evaluación de estrés físico, rendimiento de consultas, planes de ejecución e índices en bases de datos a escala de 10,5+ millones de registros.
- **Analítica de Negocio:** No deben emplearse datos sintéticos para inferir conclusiones estadísticas, históricas ni deportivas sobre equipos o jugadores. Toda analítica de negocio se canaliza a través de las vistas agregadas filtradas o consultas con `WHERE is_synthetic = FALSE`.
