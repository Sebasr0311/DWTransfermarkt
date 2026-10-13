# Capa Bronce: Ingesta Cruda y Linaje

La capa **Bronze** es el punto de entrada crudo de los datos de Transfermarkt hacia PostgreSQL. Su objetivo es persistir fielmente los archivos fuente sin aplicar transformaciones ni correcciones de negocio, garantizando linaje y reproducibilidad.

---

## 1. Principios de Diseño
- **Preservación Fiel:** Todas las columnas se definen como `TEXT` para evitar pérdidas de información o fallos prematuros de casteo de tipos durante la ingesta inicial.
- **Linaje Obligatorio:** Cada tabla incorpora 4 metadatos técnicos de auditoría:
  - `_load_id`: Identificador único UUID de la corrida ETL.
  - `_loaded_at`: Marca temporal (`TIMESTAMPTZ`) de la carga.
  - `_source_file`: Nombre del archivo CSV fuente procesado.
  - `_row_id`: Clave sustituta autoincremental (`BIGSERIAL`) para trazabilidad física de filas.
- **Idempotencia:** La recarga de cada tabla ejecuta `TRUNCATE ... RESTART IDENTITY` antes de insertar mediante `COPY` por bloques (RNF07).

---

## 2. Tablas de Ingesta
Correspondencia 1 a 1 con los archivos CSV en `data/raw/`:
1. `bronze.competitions` ← `competitions.csv`
2. `bronze.clubs` ← `clubs.csv`
3. `bronze.players` ← `players.csv`
4. `bronze.games` ← `games.csv`
5. `bronze.player_valuations` ← `player_valuations.csv`
6. `bronze.appearances` ← `appearances.csv`
7. `bronze.game_events` ← `game_events.csv`

---

## 3. Manejo de Errores y Tolerancia a Fallos (RNF09)
- **Codificación:** Intento inicial en `utf-8` con degradación automática a `latin-1` en caso de caracteres corruptos (E08).
- **Conteo Preciso de Filas en CSVs Multilínea:** Se utiliza el analizador estándar `csv.reader` para contabilizar las filas reales del archivo fuente. Esto resuelve el error común de contar saltos de línea físicos simples (`\n`), evitando que descripciones o textos con saltos internos entre comillas inflen erróneamente el conteo de filas descartadas.
- **Alineación de Columnas:** Las columnas se empatan dinámicamente por nombre de encabezado contra el DDL. Si un CSV no incluye una columna opcional, se inserta como `NULL`; si incluye columnas adicionales no definidas en el modelo, se ignoran emitiendo advertencia de linaje.
- **Auditoría:** Cada ejecución registra en `meta.etl_audit` las métricas de:
  - `rows_read`: Total de filas leídas del archivo.
  - `rows_skipped`: Filas descartadas por corrupción estructural de delimitadores.
  - `rows_inserted`: Filas efectivamente persistidas en la tabla de bronce.
  - `status`: `'OK'` o `'FAILED'`.
