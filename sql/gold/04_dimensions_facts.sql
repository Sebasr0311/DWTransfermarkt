-- Capa ORO: Modelo de Constelación de Hechos con Dimensiones Conformadas (Metodología Kimball).
-- Dimensiones con llave sustituta (_key) y llave de negocio (_id) UNIQUE.

CREATE TABLE IF NOT EXISTS gold.dim_fecha (
  fecha_key INT PRIMARY KEY,               -- AAAAMMDD
  fecha_completa DATE NOT NULL UNIQUE,
  anio SMALLINT NOT NULL,
  trimestre SMALLINT NOT NULL,
  mes SMALLINT NOT NULL,
  nombre_mes VARCHAR(12) NOT NULL,
  semana SMALLINT NOT NULL,
  temporada SMALLINT NOT NULL              -- Año de inicio de temporada (jul-jun)
);

CREATE TABLE IF NOT EXISTS gold.dim_competicion (
  competicion_key SERIAL PRIMARY KEY,
  competicion_id VARCHAR(10) NOT NULL UNIQUE,
  "nombre" TEXT,
  "tipo" TEXT,
  pais TEXT,
  confederacion TEXT
);

CREATE TABLE IF NOT EXISTS gold.dim_club (
  club_key SERIAL PRIMARY KEY,
  club_id INT NOT NULL UNIQUE,
  "nombre" TEXT,
  competicion_key INT REFERENCES gold.dim_competicion(competicion_key),
  estadio TEXT,
  tamanio_plantilla SMALLINT,
  edad_promedio NUMERIC(4,1)
);

CREATE TABLE IF NOT EXISTS gold.dim_jugador (
  jugador_key SERIAL PRIMARY KEY,
  jugador_id INT NOT NULL UNIQUE,
  "nombre" TEXT,
  "posicion" TEXT,
  sub_posicion TEXT,
  fecha_nacimiento DATE,
  pais_ciudadania TEXT,
  pie TEXT,
  altura_cm SMALLINT
);

CREATE TABLE IF NOT EXISTS gold.dim_arbitro (
  arbitro_key SERIAL PRIMARY KEY,
  nombre_arbitro TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS gold.dim_tipo_evento (
  tipo_evento_key SERIAL PRIMARY KEY,
  nombre_tipo_evento TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS gold.dim_partido (
  partido_key SERIAL PRIMARY KEY,
  partido_id INT NOT NULL UNIQUE,
  competicion_key INT NOT NULL REFERENCES gold.dim_competicion(competicion_key),
  arbitro_key INT NOT NULL REFERENCES gold.dim_arbitro(arbitro_key),
  club_local_key INT NOT NULL REFERENCES gold.dim_club(club_key),
  club_visitante_key INT NOT NULL REFERENCES gold.dim_club(club_key),
  fecha_key INT NOT NULL REFERENCES gold.dim_fecha(fecha_key),
  temporada SMALLINT NOT NULL,
  "jornada" TEXT,
  fecha_partido DATE NOT NULL,
  goles_local SMALLINT,
  goles_visitante SMALLINT,
  estadio TEXT,
  asistencia INT,
  es_sintetico BOOLEAN NOT NULL DEFAULT FALSE
);

-- ============================================================================
-- TABLAS DE HECHOS (CONSTELACIÓN)
-- ============================================================================

-- 1. Hecho de Eventos/Incidencias Discretas (Factless Fact Table particionada por rango)
CREATE TABLE IF NOT EXISTS gold.hecho_eventos_partido (
  evento_key BIGSERIAL,
  evento_partido_id VARCHAR(64) NOT NULL,     -- Llave de negocio para idempotencia
  fecha_key INT NOT NULL REFERENCES gold.dim_fecha(fecha_key),
  partido_key INT NOT NULL REFERENCES gold.dim_partido(partido_key),
  competicion_key INT NOT NULL REFERENCES gold.dim_competicion(competicion_key),
  club_key INT NOT NULL REFERENCES gold.dim_club(club_key),
  jugador_key INT REFERENCES gold.dim_jugador(jugador_key),
  jugador_asistencia_key INT REFERENCES gold.dim_jugador(jugador_key),
  arbitro_key INT NOT NULL REFERENCES gold.dim_arbitro(arbitro_key),
  tipo_evento_key INT NOT NULL REFERENCES gold.dim_tipo_evento(tipo_evento_key),
  "minuto" SMALLINT,
  franja_15min SMALLINT,                      -- 0: 0-14, 1: 15-29, ..., 6: 90+
  es_local BOOLEAN,
  es_sintetico BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY (evento_key, fecha_key)
) PARTITION BY RANGE (fecha_key);

-- 2. Hecho de Rendimiento Deportivo del Jugador (Métricas Aditivas: goles, asistencias, minutos)
CREATE TABLE IF NOT EXISTS gold.hecho_rendimiento_jugador (
  rendimiento_key BIGSERIAL PRIMARY KEY,
  aparicion_id VARCHAR(40) NOT NULL UNIQUE,   -- Llave de negocio para idempotencia
  fecha_key INT NOT NULL REFERENCES gold.dim_fecha(fecha_key),
  partido_key INT NOT NULL REFERENCES gold.dim_partido(partido_key),
  jugador_key INT NOT NULL REFERENCES gold.dim_jugador(jugador_key),
  club_key INT NOT NULL REFERENCES gold.dim_club(club_key),
  competicion_key INT NOT NULL REFERENCES gold.dim_competicion(competicion_key),
  goles SMALLINT DEFAULT 0,
  asistencias SMALLINT DEFAULT 0,
  tarjetas_amarillas SMALLINT DEFAULT 0,
  tarjetas_rojas SMALLINT DEFAULT 0,
  minutos_jugados SMALLINT DEFAULT 0,
  es_sintetico BOOLEAN NOT NULL DEFAULT FALSE
);

-- 3. Hecho de Valoraciones Financieras (Snapshot periódico semi-aditivo)
CREATE TABLE IF NOT EXISTS gold.hecho_valoraciones_mercado (
  valoracion_key BIGSERIAL PRIMARY KEY,
  fecha_key INT NOT NULL REFERENCES gold.dim_fecha(fecha_key),
  jugador_key INT NOT NULL REFERENCES gold.dim_jugador(jugador_key),
  club_key INT REFERENCES gold.dim_club(club_key),
  valor_mercado_eur NUMERIC(14,2),
  es_sintetico BOOLEAN NOT NULL DEFAULT FALSE,
  UNIQUE (jugador_key, fecha_key)
);

-- Función para generar particiones anuales en hecho_eventos_partido
CREATE OR REPLACE FUNCTION gold.asegurar_particiones_eventos(y_from INT, y_to INT) RETURNS VOID
LANGUAGE plpgsql AS $$
DECLARE y INT;
BEGIN
  FOR y IN y_from..y_to LOOP
    EXECUTE format(
      'CREATE TABLE IF NOT EXISTS gold.hecho_eventos_partido_%s PARTITION OF gold.hecho_eventos_partido FOR VALUES FROM (%s) TO (%s)',
      y, y * 10000 + 101, (y + 1) * 10000 + 101);
  END LOOP;
END $$;
