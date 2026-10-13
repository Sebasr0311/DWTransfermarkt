# DWH Transfermarkt

Data Warehouse en **PostgreSQL** con **Arquitectura Medallón** (bronze → silver → gold), **Modelo de Constelación de Hechos (Kimball Bus Architecture)** y pipeline ETL automatizado en Python.
Proyecto integrador de Bases de Datos Avanzadas (Ingeniería de Sistemas, Universidad Popular del Cesar). Consolida y procesa más de **10,5 millones de registros** de Transfermarkt para analítica multidimensional y tableros en Power BI.

---

## 1. Arquitectura General del Sistema

El flujo de datos sigue el patrón Medallón complementado con un esquema de gobernanza y auditoría transversal:

```
CSV (data/raw) ──COPY por chunks──> bronze (TEXT crudo + metadatos de linaje)
                                      │
                                      ├── limpieza, tipado, reglas EDA E01-E10, FKs
                                      ▼
                                    silver (Tablas normalizadas, PK/FK, CHECK, origin)
                                      │
                                      ├── resolución de claves sustitutas y métricas
                                      ▼
                                    gold (Constelación: dim_*, hecho_*, agg_*)
                                      │
                                      └── Consumo analítico (Power BI / Consultas OLAP)

Esquema meta: meta.etl_audit (auditoría y linaje) / meta.etl_rejected (calidad y descartes)
```

### Convención de Nomenclatura por Capa
- **Capas Bronze y Silver:** Se mantienen en **inglés técnico** (`competitions`, `clubs`, `players`, `games`, `appearances`, `game_events`, `player_valuations`) para preservar el linaje y trazabilidad directa con la fuente original de Transfermarkt.
- **Capa Gold:** Diseñada en **español profesional de negocio** (`dim_*`, `hecho_*`, `agg_*`), estandarizando el vocabulario para usuarios finales, analistas y reportes en Power BI.

---

## 2. Modelo Dimensional: Constelación de Hechos (Kimball)

A diferencia de un esquema estrella único con una sola tabla de hechos central (que forzaría la mezcla de granos incompatibles), se implementó una **Constelación de Hechos (Fact Constellation Schema)** alineada con la matriz de procesos de negocio de Kimball (*Kimball Architecture Bus*):

```
                   dim_fecha          dim_competicion       dim_arbitro
                       │                     │                   │
dim_jugador ── hecho_rendimiento_jugador ── dim_partido ────── dim_club
     │                                       │
     ├─── hecho_eventos_partido (partic.) ───┴── dim_tipo_evento
     │
     └─── hecho_valoraciones_mercado
```

### Tablas de Hechos (Procesos de Negocio)
1. **`gold.hecho_rendimiento_jugador`:** Grano a nivel de participación de un jugador en un partido (90 min). Contiene métricas aditivas acumuladas: `goles`, `asistencias`, `tarjetas_amarillas`, `tarjetas_rojas`, `minutos_jugados`.
2. **`gold.hecho_eventos_partido`:** Grano a nivel de incidencia puntual de partido en un minuto específico (gol, tarjeta, sustitución). Es una *Factless Fact Table* particionada por rango anual en `fecha_key` (1990–2035) con atributos `minuto`, `franja_15min` (0–6) y `es_local`.
3. **`gold.hecho_valoraciones_mercado`:** Grano a nivel de tasación periódica de un jugador en una fecha dada. Métrica semi-aditiva: `valor_mercado_eur`.

### Dimensiones Conformadas Compartidas
- **`gold.dim_fecha`:** Jerarquía Día → Semana/Mes → Trimestre → Año; temporada deportiva (julio–junio).
- **`gold.dim_competicion`:** Confederación → País → Competición (`tipo`: liga o copa).
- **`gold.dim_club`:** Club con estadio, tamaño de plantilla, edad promedio y enlace a su liga doméstica (`competicion_key`).
- **`gold.dim_jugador`:** Jugador con posición, sub-posición, fecha de nacimiento, país de ciudadanía, pie dominante y altura.
- **`gold.dim_arbitro`:** Nombre estandarizado del árbitro.
- **`gold.dim_tipo_evento`:** Catálogo de incidencias (Goals, Cards, Substitutions, Shootout, etc.).
- **`gold.dim_partido`:** Dimensión de contexto de partido con clubes contendientes, marcador final, árbitro, estadio y asistencia.

### Vistas Materializadas de Agregación
Optimizadas con índices únicos para refresco concurrente (`REFRESH MATERIALIZED VIEW CONCURRENTLY`) y filtrado estricto de datos sintéticos (`es_sintetico = FALSE`):
- **`gold.agg_jugador_temporada_liga`:** Rendimiento por jugador, torneo y temporada (satisface RF01, RF02, RF08).
- **`gold.agg_club_temporada`:** Puntos, goles a favor/contra y valor promedio de plantilla por club y temporada (RF04, RF05).
- **`gold.agg_eventos_15min`:** Frecuencia temporal de goles y tarjetas por franjas de 15 minutos (RF07).
- **`gold.agg_disciplina_arbitro`:** Promedio de tarjetas por partido y por 90 minutos por colegiado (RF06).
- **`gold.agg_local_visitante`:** Balance victorias local vs visitante y promedio de goles por liga (RF09).

---

## 3. Expansión Controlada a 10,5 Millones de Registros

Para evaluar el comportamiento físico, particionamiento e índices bajo alta concurrencia y estrés:
- **Volumen Real Base:** 3.625.525 filas en plata provenientes de los CSV originales.
- **Volumen Total Expandido:** **10.565.092 filas** en plata (cumpliendo y superando la meta de 10.565.088).
- **Trazabilidad y Cero Contaminación:**
  - En `silver`: columna `origin` (`'real'` vs `'sintetico'`) y `synthetic_batch` (UUID).
  - En `gold`: columna `es_sintetico` (`FALSE` vs `TRUE`).
  - Las vistas materializadas excluyen datos sintéticos garantizando que las estadísticas históricas reales no se alteren.
- **Reversibilidad Total:** Rollback instantáneo e idempotente mediante `--rollback`.

---

## 4. Requisitos del Sistema

- **Python:** 3.10+ (probado en Python 3.12 y 3.13 con entorno virtual `.venv`).
- **PostgreSQL:** 14+ (probado en PostgreSQL 16 vía Docker y PostgreSQL 18 local).
- **Docker Desktop:** Opcional, para ejecución inmediata con `docker-compose.yml` (`postgres:16`).
- **Archivos de Origen:** CSVs de Transfermarkt en `data/raw/`:
  - `competitions.csv`, `clubs.csv`, `players.csv`, `games.csv`, `player_valuations.csv`, `appearances.csv`, `game_events.csv`.

---

## 5. Instalación y Puesta en Marcha

### 1. Clonar el repositorio y configurar entorno
```powershell
git clone https://github.com/Sebasr0311/DWTransfermarkt.git
cd DWTransfermarkt
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env     # Configurar credenciales de PostgreSQL en .env
```

### 2. Despliegue con Docker (Opcional si no se cuenta con PostgreSQL local)
```powershell
docker compose up -d
```

### 3. Ejecución del Pipeline ETL Completo
```powershell
# 1) Creación de base de datos, esquemas DDL, índices y funciones
python scripts/setup_database.py

# 2) Carga de datos reales por capas (bronze -> silver -> gold)
python -m etl.run_pipeline --layer all --chunk-size 100000

# 3) Expansión controlada a 10,5 millones de registros
python -m etl.run_pipeline --layer expand --target-total 10565088

# 4) Validación integral de calidad, volumetría y tiempos OLAP
python scripts/validate.py

# 5) Batería de pruebas automatizadas con pytest (55 pruebas)
pytest -v
```

### Ejecución por Capas Separadas
```powershell
python -m etl.run_pipeline --layer bronze --chunk-size 100000
python -m etl.run_pipeline --layer silver
python -m etl.run_pipeline --layer gold
python -m etl.run_pipeline --layer expand
```

### Reversión de Datos Sintéticos (Rollback)
```powershell
python -m etl.run_pipeline --layer expand --rollback
```

---

## 6. Estructura del Proyecto

```
DWTransfermarkt/
├── data/raw/             # Archivos CSV fuente de Transfermarkt
├── docs/                 # Documentación técnica exhaustiva
│   ├── bronze.md         # Especificación de ingesta y linaje crudo
│   ├── silver.md         # Reglas de limpieza, tipado e integridad
│   ├── gold.md           # Modelo de Constelación de Hechos y vistas
│   ├── reglas_eda.md     # Catálogo de reglas EDA E01 a E10
│   ├── expansion.md      # Metodología y trazabilidad de datos sintéticos
│   ├── volumetria.md     # Métricas físicas de almacenamiento y benchmarks
│   └── herramientas_utilizadas.txt # Inventario tecnológico
├── etl/                  # Scripts de extracción, transformación y carga
│   ├── bronze/           # Ingesta masiva con COPY por chunks
│   ├── silver/           # Transformaciones SQL set-based y calidad
│   ├── gold/             # Carga dimensional, llaves sustitutas y agregaciones
│   ├── expansion/        # Módulo de clonación controlada y rollback
│   └── run_pipeline.py   # Orquestador central por CLI
├── sql/                  # Scripts DDL organizados por capa
│   ├── bronze/           # DDL esquemas crudos y metadatos
│   ├── silver/           # DDL esquemas tipados, PK/FK y CHECK
│   ├── gold/             # DDL constelación, particiones y vistas
│   └── validations/      # Consultas SQL de verificación de integridad
├── scripts/              # Scripts utilitarios (setup_database, validate)
├── tests/                # Pruebas automatizadas (pytest)
├── docker-compose.yml    # Contenedor PostgreSQL 16
├── requirements.txt      # Dependencias de Python
└── HERRAMIENTAS_UTILIZADAS.txt # Ficha técnica de herramientas
```

---

## 7. Verificación y Resultados Clave

- **Integridad:** 0 registros huérfanos, 0 duplicados no controlados en PK/FK, 0 violaciones de partición.
- **Rendimiento OLAP:** Consultas sobre el modelo de hechos con >6,75 millones de registros responden en **< 0,39 segundos** (SLA requerido < 3,0 s).
- **Pruebas:** 55/55 pruebas unitarias y de integración pasando exitosamente en `pytest`.
