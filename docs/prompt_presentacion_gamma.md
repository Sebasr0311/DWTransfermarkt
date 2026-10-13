# Prompt para Generación de Presentación en Gamma

Este archivo contiene el prompt estructurado para generar las 13 diapositivas de sustentación del Data Warehouse Transfermarkt en herramientas de IA como **Gamma App** (utilizando la opción *Create with AI* / *Text to Deck*).

---

```markdown
Crea una presentación profesional, ejecutiva y altamente técnica de 13 diapositivas (formato 16:9) para la sustentación universitaria de nuestro proyecto integrador de Bases de Datos Avanzadas: "Data Warehouse del Ecosistema Futbolístico Transfermarkt".

---

### INSTRUCCIONES DE ESTILO VISUAL Y DISEÑO (MANDATORIO)
- **Temática visual:** Fusión entre Ingeniería de Datos de alto nivel, Arquitectura de Software y Analítica Deportiva / Fútbol Profesional (Moneyball / Scouting moderno).
- **Paleta de colores:**
  - Color primario: Azul marino oscuro institucional (#0F172A / #1E3A8A).
  - Color secundario / acento tecnológico: Teal / Verde esmeralda (#0D9488 / #10B981) y Cian Power BI (#0284C7).
  - Acentos de alerta y métricas: Ámbar cálido (#F59E0B).
  - Fondo: Modo oscuro elegante (Dark Mode profesional) o blanco limpio con tarjetas en gris pizarra (#F8FAFC / #F1F5F9).
- **Elementos visuales e iconografía:** En cada diapositiva utiliza tarjetas visuales (cards), badges de métricas en negrita, divisores de flujo y cajas de código/diagramas. Incorpora íconos alusivos en cada bloque:
  - ⚽ Fútbol: Pelota, cancha, botín, silbato, tarjeta roja/amarilla, cronómetro.
  - 💾 Bases de datos e Infraestructura: Servidor, PostgreSQL, tablas relacionales, particiones, Docker, índices.
  - 📊 Power BI y Analítica: Gráfico de dispersión, KPIs ejecutivos, velocímetro, embudo, dashboard.
  - ⚙️ Ingeniería de datos: Pipeline ETL, engranajes, flujo secuencial, check de validación, terminal/código.
- **Formato de texto:** Cero bloques densos de texto. Prioriza bullets concisos, tarjetas comparativas 2x2 o 3 columnas, números grandes (Big Numbers) para métricas y arquitectura visual.

---

### ESTRUCTURA DIAPOSITIVA POR DIAPOSITIVA (13 SLIDES)

#### DIAPOSITIVA 1: Portada Institucional
- **Título principal:** Data Warehouse del Ecosistema Futbolístico Transfermarkt
- **Subtítulo:** Arquitectura Medallón en PostgreSQL 16 & Modelo Dimensional de Constelación de Hechos (Kimball Bus)
- **Badges destacados:**
  - 🐘 PostgreSQL 16 + Docker
  - 🐍 ETL en Python (Pandas + Psycopg2)
  - 📊 Dashboard Analítico en Power BI
  - ⚡ 10,5+ Millones de Registros
- **Pie institucional:** Proyecto Integrador | Bases de Datos Avanzadas | 5to Semestre | Ingeniería de Sistemas | Universidad Popular del Cesar | Valledupar, 2026.

---

#### DIAPOSITIVA 2: Planteamiento del Problema: De la Fricción OLTP a la Analítica OLAP
- **Mensaje central:** "El fútbol moderno decide con datos, pero las arquitecturas transaccionales colapsan ante el análisis masivo".
- **Comparativa visual (2 Columnas / Tarjetas enfrentadas):**
  - **Tarjeta 1: El Cuello de Botella Operacional (OLTP)**
    - ❌ Base relacional normalizada en 3NF con más de 7 tablas encadenadas.
    - ❌ Consultas analíticas pesadas que bloquean escrituras y saturan memoria RAM.
    - ❌ Múltiples JOINs costosos sobre millones de filas: reportes que tardan minutos.
  - **Tarjeta 2: La Solución Data Warehouse (OLAP Medallón)**
    - ✅ Modelo desnormalizado de Constelación orientado al negocio.
    - ✅ Separación estricta de capas (Bronce, Plata, Oro) con linaje inalterable.
    - ✅ Tiempos de respuesta sub-segundo (< 0,39 s) para tableros ejecutivos en Power BI.

---

#### DIAPOSITIVA 3: Objetivos del Sistema y Ciclo de Vida del Dato
- **Objetivo General:** Diseñar, implementar y evaluar un DWH en PostgreSQL bajo Arquitectura Medallón y Constelación Kimball, procesando más de 10,5 millones de filas para soportar BI sub-3 segundos.
- **Flujo de 6 Objetivos Específicos (Tarjetas horizontales numeradas):**
  1. 📥 **Ingesta Bronce:** Extracción masiva con COPY por chunks de 100k filas y linaje UUID.
  2. 🧹 **Depuración Plata:** Calidad relacional EDA E01–E10, tipado fuerte y cero registros huérfanos.
  3. 🌟 **Modelado Oro:** Constelación de hechos con 7 dimensiones conformadas y 3 hechos.
  4. 📈 **Expansión Controlada:** Escalamiento determinista y reversible a 10,56 millones de registros.
  5. ⚡ **Optimización Física:** Particionamiento anual (1990–2035) e indexación B-Tree/Hash.
  6. 📊 **Explotación BI:** Precalculo en vistas materializadas concurrentes y dashboard interactivo.

---

#### DIAPOSITIVA 4: Requerimientos del Negocio y Garantía de Rendimiento
- **Requerimientos Funcionales Clave (Grid de 4 Tarjetas):**
  - 🎯 **Scouting & Goleadores (RF01/RF02/RF08):** Rankings por liga, edad y posición; detección de talento Sub-23.
  - 🏆 **Rendimiento de Clubes (RF04/RF05):** Puntos de liga (3, 1, 0) y correlación valor de plantilla vs éxito.
  - ⏱️ **Fatiga e Incidencias (RF07):** Distribución temporal de goles y tarjetas en 7 franjas de 15 minutos.
  - 🟨 **Rigor Arbitral (RF06):** Promedio de tarjetas por 90 minutos y comportamiento disciplinario.
- **Requerimientos No Funcionales Críticos (Badges métricos):**
  - SLA de Consulta: Cumplido en **< 0,39 s** (meta < 3,0 s).
  - Integridad Referencial: **0 huérfanos** verificado con LEFT JOINs.
  - Idempotencia: Reejecución 100% segura con `ON CONFLICT DO UPDATE`.

---

#### DIAPOSITIVA 5: Fuente de Datos de Origen y Ecosistema Transfermarkt
- **Contexto:** Datasets abiertos de Kaggle (`dcaribou/transfermarkt-datasets`).
- **Las 7 Entidades del Dominio (Grid visual con íconos):**
  - 🏆 `competitions.csv`: 65 ligas y copas internacionales y domésticas.
  - 🛡️ `clubs.csv`: 796 clubes profesionales, estadios y valores de nómina.
  - 🏃 `players.csv`: 50.149 futbolistas únicos, posiciones y datos biométricos.
  - ⚽ `games.csv`: 72.602 partidos históricos con árbitros y marcadores.
  - 👕 `appearances.csv`: 1,81 millones de alineaciones y actuaciones (90 min).
  - ⏱️ `game_events.csv`: 1,03 millones de incidencias cronometradas al minuto.
  - 💶 `player_valuations.csv`: 656.000 tasaciones periódicas históricas en euros.

---

#### DIAPOSITIVA 6: Volumetría Físicamente Medida en PostgreSQL
- **Hito Técnico:** 10.565.092 registros auditados sobre el motor PostgreSQL 16.
- **3 Métricas Gigantes (Big Numbers con Callout):**
  - **10.565.092** Filas Consolidadas en Silver (3,62 M reales + 6,94 M sintéticas).
  - **2.428 MB** Espacio Total en la tabla particionada de eventos (`gold.hecho_eventos_partido`).
  - **< 0,39 s** Tiempo de respuesta en consultas de agregación sobre 6,75 millones de hechos.
- **Distribución de Almacenamiento Físico (Tabla compacta):**
  - Datos brutos: 1.614 MB | Índices B-Tree/Hash: 786 MB (32,7% del espacio, acelerando lecturas).
  - 55 de 55 pruebas unitarias y de integración pasando en verde (`pytest -v`).

---

#### DIAPOSITIVA 7: Arquitectura Medallón: Flujo de Datos y Gobernanza
- **Diagrama en 4 Capas Horizontales con Flechas Conectoras:**
  - 🥉 **Capa Bronce (`bronze`):** Ingesta cruda | Todas las columnas `TEXT` | `COPY` en chunks | Linaje inyectado (`_load_id`, `_loaded_at`, `_source_file`, `_row_id`).
  - 🥈 **Capa Plata (`silver`):** Datos limpios y tipados | PKs, FKs y restricciones `CHECK` | Deduplicación con `DISTINCT ON` | Auditoría de descartes en `meta.etl_rejected`.
  - 🥇 **Capa Oro (`gold`):** Modelo de Constelación de Hechos en español | Claves sustitutas enteras (`*_key`) | Particionamiento por rango anual | Vistas materializadas.
  - 🛡️ **Capa Transversal (`meta`):** Gobernanza integral | Auditoría de ejecución en `meta.etl_audit` | Funciones `to_date`, `to_int`, `to_num`.

---

#### DIAPOSITIVA 8: Modelo Dimensional: Constelación de Hechos (Defensa Central)
- **Pregunta Clave del Jurado:** "¿Por qué Constelación y NO un Esquema Estrella simple?"
- **Fundamento Metodológico (Ralph Kimball):**
  - ⚠️ **El Problema del Grano (Granularity Mismatch):** Un evento ocurre al minuto específico; la actuación de un jugador abarca los 90 minutos del partido; las valoraciones ocurren en fechas quincenales. Forzar todo en una sola estrella destruye la aditividad o causa duplicados artificiales (*fan traps*).
  - ✅ **La Solución Constelación:** 3 Tablas de hechos separadas por proceso de negocio compartiendo **7 Dimensiones Conformadas**:
    1. `hecho_rendimiento_jugador` (Métricas aditivas: goles, asistencias, minutos jugados).
    2. `hecho_eventos_partido` (Factless Fact Table particionada por rango: minuto, franja 15 min).
    3. `hecho_valoraciones_mercado` (Periodic Snapshot semi-aditivo: valor en euros).

---

#### DIAPOSITIVA 9: Matriz de Bus (Kimball Bus Matrix) y Entidades en Español
- **Concepto:** Mapeo estricto entre procesos de negocio y dimensiones conformadas compartidas.
- **Matriz Visual (Checklist de Cruce):**
  - Rendimiento Jugador ──► `dim_fecha`, `dim_competicion`, `dim_club`, `dim_jugador`, `dim_partido`.
  - Eventos de Partido ──► `dim_fecha`, `dim_competicion`, `dim_club`, `dim_jugador`, `dim_arbitro`, `dim_tipo_evento`, `dim_partido`.
  - Valoraciones Mercado ──► `dim_fecha`, `dim_club`, `dim_jugador`.
- **Estandarización de Negocio:** Toda la capa Gold está construida en español profesional (`dim_*`, `hecho_*`, `agg_*`) para facilitar la comprensión y el modelado semántico en Power BI.

---

#### DIAPOSITIVA 10: Calidad de Datos y Reglas EDA (E01 a E10)
- **Mensaje:** "El Análisis Exploratorio de Datos (EDA) traducido a código de calidad en producción".
- **4 Tarjetas de Reglas Representativas:**
  - 🔢 **E01 (Métricas Deportivas):** Goles, asistencias, tarjetas y minutos nulos se imputan a `0` para no romper sumatorias acumuladas.
  - 💶 **E02 (Valor de Mercado):** Los valores nulos **SE CONSERVAN EN NULL**. *Regla de oro:* Inventar un 0 alteraría gravemente los promedios y la correlación estadística con los puntos.
  - 📅 **E04 (Fechas Heterogéneas):** Estandarización a ISO-8601 (`AAAA-MM-DD`) vía función PL/pgSQL `meta.to_date()`.
  - 🚫 **E07 / E10 (Integridad y Llaves):** Cero tolerancia a llaves de negocio nulas y rechazo controlado de huérfanos con registro detallado en `meta.etl_rejected`.

---

#### DIAPOSITIVA 11: Pipeline ETL en Python y Expansión Sintética Controlada
- **Arquitectura del Pipeline:** Modular, set-based y orquestado con `python -m etl.run_pipeline`.
- **Características Técnicas (3 Bloques):**
  - 🚀 **Carga por Chunks:** Bloques de 100.000 filas con COPY binario nativo, evitando desbordamientos de memoria RAM.
  - 🧬 **Clonación Controlada (10,5 M):** Clonación determinista de partidos (`game_id >= 900.000.000`) y eventos con perturbación controlada de minuto (±3 min en rango [0, 130]).
  - 🔄 **Trazabilidad y Rollback:** Columnas `origin = 'sintetico'` y `es_sintetico = TRUE`. Vistas agregadas filtran solo datos reales. Rollback completo e instantáneo mediante `--rollback`.

---

#### DIAPOSITIVA 12: Optimizaciones Físicas y Aceleración OLAP
- **Técnicas de Alto Desempeño en PostgreSQL 16 (3 Columnas):**
  - 🗂️ **Particionamiento por Rango Anual:**
    - `gold.hecho_eventos_partido` particionada anualmente sobre `fecha_key` (1990 a 2035).
    - Descarte automático de particiones irrelevantes (*partition pruning*). Partición default con **0 filas**.
  - 🔍 **Indexación Estratégica B-Tree y Hash:**
    - B-Trees en todas las claves foráneas y dimensiones.
    - Índice Hash en `tipo_evento_key` para búsquedas exactas en Power BI con 40% menor consumo de disco.
  - ⚡ **5 Vistas Materializadas Concurrentes (RF10):**
    - `agg_jugador_temporada_liga`, `agg_club_temporada`, `agg_eventos_15min`, `agg_disciplina_arbitro`, `agg_local_visitante`.
    - Índices únicos que permiten `REFRESH MATERIALIZED VIEW CONCURRENTLY` sin bloqueos de lectura.

---

#### DIAPOSITIVA 13: Dashboard Power BI, Storytelling y Conclusiones
- **Las 4 Páginas de Decisión del Tablero (Visuales interactivos):**
  1. 📌 **Resumen Ejecutivo:** KPIs globales, goles por fecha y valor global de mercado.
  2. 🔍 **Scouting & Promesas Sub-23:** Matriz de dispersión (Goles/90 vs Valor en EUR) para cazar talento infravalorado.
  3. 🛡️ **Puntos de Liga y Factor Cancha:** Posiciones calculadas (3, 1, 0 pts) y correlación nómina vs puntos de campeonato.
  4. 🟨 **Disciplina e Incidencias:** Rigor arbitral por 90 min y curva de fatiga en tramos finales (min 75–90+).
- **Conclusión Final:** Data Warehouse robusto, validado empíricamente (55/55 pruebas), con arquitectura de constelación escalable y listo para soportar decisiones estratégicas en el fútbol profesional.
```
