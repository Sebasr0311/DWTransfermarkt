# Capa Oro: Modelo de Constelación de Hechos (Kimball Bus Architecture)

La capa **Gold** implementa un modelo multidimensional de **Constelación de Hechos (Fact Constellation Schema)** fundamentado en la metodología de Ralph Kimball (*The Data Warehouse Lifecycle Toolkit*). 

Este modelo sustituye la concepción inicial de un esquema estrella único con una tabla central de eventos, separando los procesos de negocio en tablas de hechos independientes según su grano específico para preservar la aditividad de las métricas numéricas y garantizar la coherencia analítica en Power BI y consultas OLAP.

---

## 1. Justificación Arquitectónica: ¿Por qué Constelación?

En el análisis original de Transfermarkt, modelar exclusivamente `game_events` como la tabla central de hechos presentaba tres limitaciones críticas:
1. **Grano incompatible:** Un evento de partido ocurre a nivel de minuto para una incidencia puntual (ej. tarjeta, gol, cambio). Forzar métricas acumuladas de partido (minutos jugados por un futbolista que no tuvo incidencias, alineaciones) provocaba duplicidades o requería registros vacíos artificiales.
2. **Pérdida de aditividad:** `game_events` es en esencia una *Factless Fact Table* (tabla de hechos sin hechos numéricos acumulables). No permitía responder directamente sumatorias de rendimiento (total de goles, asistencias y minutos de un jugador en una temporada) sin incurrir en *fan traps* o *chasm traps*.
3. **Múltiples procesos de negocio:** En el negocio del fútbol profesional coexisten tres dinámicas claramente diferenciadas:
   - **Rendimiento deportivo en partido:** Acumulados de 90 minutos por jugador.
   - **Incidencias discretas:** Sucesos cronometrados al minuto.
   - **Valoraciones financieras:** Tasaciones periódicas de mercado que cambian en fechas específicas.

La solución arquitectónica es la **Constelación de Hechos**, donde múltiples tablas de hechos comparten un conjunto de **dimensiones conformadas**.

---

## 2. Diagrama del Modelo de Constelación

```
                    ┌──────────────┐     ┌─────────────────┐     ┌─────────────┐
                    │  dim_fecha   │     │ dim_competicion │     │ dim_arbitro │
                    └──────┬───────┘     └────────┬────────┘     └──────┬──────┘
                           │                      │                     │
┌─────────────┐            │                      │                     │
│ dim_jugador ├──────┐     │                      │                     │
└──────┬──────┘      │     │                      │                     │
       │             ▼     ▼                      ▼                     ▼
       │      ┌─────────────────────────────┐   ┌─────────────────────────────┐
       │      │ hecho_rendimiento_jugador   │   │         dim_partido         │
       │      │ (Métricas Aditivas:         │   │ (Contexto del partido:      │
       │      │  goles, asist, tarjetas,    │   │  marcador, local, visitante,│
       │      │  minutos jugados)           │   │  árbitro, estadio)          │
       │      └──────────────┬──────────────┘   └──────────────┬──────────────┘
       │                     │                                 │
       │                     │         ┌───────────────┐       │
       │                     └─────────►   dim_club    ◄───────┘
       │                               └───────▲───────┘
       │                                       │
       │      ┌─────────────────────────────┐  │
       ├─────►│ hecho_eventos_partido       ├──┼───────────────┐
       │      │ (Factless particionada:     │  │               │
       │      │  minuto, franja_15min)      │  │               ▼
       │      └─────────────────────────────┘  │       ┌──────────────────┐
       │                                       │       │ dim_tipo_evento  │
       │      ┌─────────────────────────────┐  │       └──────────────────┘
       └─────►│ hecho_valoraciones_mercado  ├──┘
              │ (Snapshot periódico:        │
              │  valor_mercado_eur)         │
              └─────────────────────────────┘
```

---

## 3. Matriz de Bus de Arquitectura (Kimball Bus Matrix)

La matriz vincula los tres procesos de negocio analíticos con las dimensiones conformadas compartidas:

| Proceso de Negocio / Tabla de Hechos | `dim_fecha` | `dim_competicion` | `dim_club` | `dim_jugador` | `dim_arbitro` | `dim_tipo_evento` | `dim_partido` |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Rendimiento de Jugador** (`hecho_rendimiento_jugador`) | **X** | **X** | **X** | **X** | | | **X** |
| **2. Incidencias de Partido** (`hecho_eventos_partido`) | **X** | **X** | **X** | **X** | **X** | **X** | **X** |
| **3. Tasaciones Financieras** (`hecho_valoraciones_mercado`) | **X** | | **X** | **X** | | | |

---

## 4. Diccionario de Datos: Dimensiones Conformadas

Todas las dimensiones implementan una clave sustituta entera (`*_key`) como clave primaria física, y mantienen la clave natural de negocio de Transfermarkt (`*_id`) con restricción `UNIQUE` para asegurar idempotencia.

### 4.1. `gold.dim_fecha`
- **Propósito:** Dimensión temporal con calendario completo de fechas de partidos y valoraciones.
- **Grano:** Un día calendario.
- **Clave Primaria:** `fecha_key` (Entero en formato `AAAAMMDD`, ej: `20230528`).
- **Atributos:** `fecha_completa` (DATE UNIQUE), `anio`, `trimestre`, `mes`, `nombre_mes`, `semana`, `temporada` (año de inicio del ciclo futbolístico, ej: julio 2023 a junio 2024 corresponde a temporada 2023).

### 4.2. `gold.dim_competicion`
- **Propósito:** Torneos y ligas internacionales y domésticas.
- **Grano:** Una competición deportiva.
- **Clave Primaria:** `competicion_key` (SERIAL). Clave natural: `competicion_id` (VARCHAR(10) UNIQUE, ej: `'ES1'`).
- **Atributos:** `nombre`, `tipo` (`first_tier`, `domestic_cup`, etc.), `pais`, `confederacion` (UEFA, CONMEBOL, etc.).

### 4.3. `gold.dim_club`
- **Propósito:** Clubes de fútbol participantes.
- **Grano:** Una institución deportiva.
- **Clave Primaria:** `club_key` (SERIAL). Clave natural: `club_id` (INT UNIQUE).
- **Relación:** `competicion_key` (FK hacia `dim_competicion`) para su liga doméstica principal.
- **Atributos:** `nombre`, `estadio`, `tamanio_plantilla`, `edad_promedio`.

### 4.4. `gold.dim_jugador`
- **Propósito:** Futbolistas profesionales.
- **Grano:** Un jugador individual.
- **Clave Primaria:** `jugador_key` (SERIAL). Clave natural: `jugador_id` (INT UNIQUE).
- **Atributos:** `nombre`, `posicion` (`Goalkeeper`, `Defender`, `Midfield`, `Attack`), `sub_posicion`, `fecha_nacimiento`, `pais_ciudadania`, `pie` (`left`, `right`, `both`), `altura_cm`.

### 4.5. `gold.dim_arbitro`
- **Propósito:** Árbitros oficiales designados en los encuentros.
- **Grano:** Un colegiado.
- **Clave Primaria:** `arbitro_key` (SERIAL).
- **Atributos:** `nombre_arbitro` (TEXT UNIQUE).

### 4.6. `gold.dim_tipo_evento`
- **Propósito:** Catálogo unificado de tipos de incidencias reglamentarias.
- **Grano:** Una categoría de evento.
- **Clave Primaria:** `tipo_evento_key` (SERIAL).
- **Atributos:** `nombre_tipo_evento` (TEXT UNIQUE: `'Goals'`, `'Cards'`, `'Substitutions'`, `'Shootout'`, etc.).

### 4.7. `gold.dim_partido`
- **Propósito:** Dimensión degenerada/conformada que preserva el contexto de cada encuentro deportivo.
- **Grano:** Un partido de fútbol de 90 minutos (o con tiempo extra/penales).
- **Clave Primaria:** `partido_key` (SERIAL). Clave natural: `partido_id` (INT UNIQUE).
- **Claves Foráneas:** `competicion_key`, `arbitro_key`, `club_local_key`, `club_visitante_key`, `fecha_key`.
- **Atributos:** `temporada`, `jornada`, `fecha_partido`, `goles_local`, `goles_visitante`, `estadio`, `asistencia`, `es_sintetico` (BOOLEAN).

---

## 5. Diccionario de Datos: Tablas de Hechos

### 5.1. `gold.hecho_rendimiento_jugador`
- **Propósito:** Registrar las estadísticas acumuladas de actuación individual por jugador en cada partido.
- **Grano:** La participación/alineación de un jugador en un partido específico.
- **Clave Primaria:** `rendimiento_key` (BIGSERIAL). Clave natural: `aparicion_id` (VARCHAR(40) UNIQUE).
- **Claves Foráneas Dimensionales:**
  - `fecha_key` → `dim_fecha`
  - `partido_key` → `dim_partido`
  - `jugador_key` → `dim_jugador`
  - `club_key` → `dim_club`
  - `competicion_key` → `dim_competicion`
- **Métricas Aditivas:**
  - `minutos_jugados` (INT): Cantidad de minutos disputados en el encuentro (0–130).
  - `goles` (SMALLINT): Goles marcados por el futbolista en el partido.
  - `asistencias` (SMALLINT): Asistencias registradas.
  - `tarjetas_amarillas` (SMALLINT): Tarjetas amarillas recibidas (0, 1 o 2).
  - `tarjetas_rojas` (SMALLINT): Tarjetas rojas directas o por doble amarilla.
- **Atributo de Linaje:** `es_sintetico` (BOOLEAN NOT NULL DEFAULT FALSE).
- **Casos de Uso / Requerimientos:** Rankings de goleadores y asistidores (RF01), rendimiento por posición y edad (RF02), scouting Sub-23 (RF08).

### 5.2. `gold.hecho_eventos_partido` (Particionada por Rango Anual)
- **Propósito:** Capturar la ocurrencia temporal exacta de incidencias individuales durante el tiempo reglamentario o compensatorio.
- **Grano:** Una incidencia puntual de partido en un minuto específico.
- **Tipo Dimensional:** *Factless Fact Table* con atributos discretos de evento.
- **Estrategia de Particionamiento Físico:** Particionamiento declarativo por rango (`PARTITION BY RANGE (fecha_key)`). Particiones anuales desde 1990 hasta 2035 (`hecho_eventos_partido_1990` ... `hecho_eventos_partido_2035`) y partición por defecto (`hecho_eventos_partido_default` con 0 filas).
- **Clave Primaria Compuesta:** `(evento_key, fecha_key)`. Clave de negocio: `evento_partido_id` (VARCHAR(64)).
- **Claves Foráneas Dimensionales:**
  - `fecha_key` → `dim_fecha`
  - `partido_key` → `dim_partido`
  - `competicion_key` → `dim_competicion`
  - `club_key` → `dim_club`
  - `jugador_key` → `dim_jugador` (NULL si no aplica)
  - `jugador_asistencia_key` → `dim_jugador` (NULL si no hubo asistencia)
  - `arbitro_key` → `dim_arbitro`
  - `tipo_evento_key` → `dim_tipo_evento`
- **Atributos de Evento:**
  - `minuto` (SMALLINT): Minuto en que ocurrió la acción (0–130).
  - `franja_15min` (SMALLINT): Franja temporal de 15 minutos (0: 0–14, 1: 15–29, 2: 30–44, 3: 45–59, 4: 60–74, 5: 75–89, 6: 90+).
  - `es_local` (BOOLEAN): Indica si el club que generó el evento era el equipo local.
  - `es_sintetico` (BOOLEAN NOT NULL DEFAULT FALSE).
- **Casos de Uso / Requerimientos:** Distribución temporal de incidencias y fatiga en tramos finales (RF07), análisis de rigor y disciplina arbitral (RF06).

### 5.3. `gold.hecho_valoraciones_mercado`
- **Propósito:** Almacenar la evolución histórica del valor económico estimado de los futbolistas.
- **Grano:** La tasación de mercado de un jugador en una fecha determinada.
- **Clave Primaria:** `valoracion_key` (BIGSERIAL). Clave natural compuesta: `(jugador_id, fecha_valoracion)`.
- **Claves Foráneas Dimensionales:**
  - `fecha_key` → `dim_fecha`
  - `jugador_key` → `dim_jugador`
  - `club_key` → `dim_club`
- **Métrica Semi-Aditiva:**
  - `valor_mercado_eur` (NUMERIC(14,2)): Valor de tasación en euros en ese punto del tiempo (semi-aditiva: se puede promediar en el tiempo o sumar entre compañeros de plantilla en una misma fecha, pero no sumar a lo largo de fechas del mismo jugador).
- **Atributo de Linaje:** `es_sintetico` (BOOLEAN NOT NULL DEFAULT FALSE).
- **Casos de Uso / Requerimientos:** Correlación entre valor de nómina y puntos obtenidos en liga (RF05), tasación por posición y edad (RF08).

---

## 6. Vistas Materializadas de Agregación (RF10)

Para asegurar tiempos de respuesta analítica inferiores a 1 segundo en Power BI, la capa Gold incluye 5 vistas materializadas. Cada una posee un índice único para permitir actualización concurrente sin bloqueo (`REFRESH MATERIALIZED VIEW CONCURRENTLY`) y excluye datos sintéticos (`es_sintetico = FALSE`):

### 6.1. `gold.agg_jugador_temporada_liga`
- **Grano:** Rendimiento consolidado por `(jugador_key, competicion_key, temporada)`.
- **Métricas:** Partidos disputados, minutos totales, goles, asistencias, tarjetas amarillas y rojas, promedio de gol por 90 minutos (`goles_por_90`), ranking de goleador en esa liga/temporada (`ranking_goleador`).
- **Índice Único:** `(jugador_key, competicion_key, temporada)`.
- **Requerimientos Resueltos:** RF01, RF02, RF08.

### 6.2. `gold.agg_club_temporada`
- **Grano:** Desempeño y valoración por `(club_key, temporada)`.
- **Métricas:** Partidos jugados, victorias, empates, derrotas, goles a favor, goles en contra, diferencia de gol, puntos obtenidos, valor promedio de plantilla (`valor_plantilla_promedio_eur`).
- **Índice Único:** `(club_key, temporada)`.
- **Requerimientos Resueltos:** RF04, RF05.

### 6.3. `gold.agg_eventos_15min`
- **Grano:** Incidencias por `(competicion_key, temporada, franja_15min, tipo_evento_key)`.
- **Métricas:** Total de eventos (`total_eventos`), porcentaje del total del partido (`pct_del_total`).
- **Índice Único:** `(competicion_key, temporada, franja_15min, tipo_evento_key)`.
- **Requerimientos Resueltos:** RF07.

### 6.4. `gold.agg_disciplina_arbitro`
- **Grano:** Comportamiento disciplinario por `(arbitro_key, temporada)`.
- **Métricas:** Partidos dirigidos, total de tarjetas amarillas y rojas, promedio de tarjetas por partido (`tarjetas_por_partido`), promedio por 90 minutos.
- **Índice Único:** `(arbitro_key, temporada)`.
- **Requerimientos Resueltos:** RF06.

### 6.5. `gold.agg_local_visitante`
- **Grano:** Balance geográfico/de campo por `(competicion_key, temporada)`.
- **Métricas:** Partidos analizados, victorias locales, empates, victorias visitantes, porcentaje de victoria local (`pct_victoria_local`), promedio de goles local y visitante.
- **Índice Único:** `(competicion_key, temporada)`.
- **Requerimientos Resueltos:** RF09.

---

## 7. Optimización Física y Tiempos de Respuesta

- **Índices B-Tree:** En todas las claves foráneas de las tres tablas de hechos y en las claves de negocio de las dimensiones.
- **Índice Hash:** En `gold.hecho_eventos_partido(tipo_evento_key)` para acelerar consultas de igualdad en Power BI sobre tipos de incidencias puntuales.
- **Partition Pruning:** La partición por rango en `hecho_eventos_partido` descarta automáticamente particiones irrelevantes al filtrar por `fecha_key` o temporadas.
- **Tiempos de Respuesta Medidos:**
  - Rankings de goleadores (RF01): **0,017 s**
  - Tablas de posiciones de clubes (RF04): **0,001 s**
  - Distribución temporal en franjas (RF07): **0,302 s**
  - Disciplina arbitral (RF06): **0,002 s**
  - Balance local vs visitante (RF09): **0,000 s**
  - Cruce de eventos por competición (join masivo de 6,75M filas): **0,386 s**
  - Todos los benchmarks se encuentran muy por debajo del SLA contractual de **3,00 segundos**.
