-- Vistas Materializadas de Agregación en Capa ORO (RF10)
-- Todas cuentan con índice único para permitir REFRESH CONCURRENTLY y filtran datos sintéticos (es_sintetico = FALSE).

-- 1. Rendimiento y Goleadores por Jugador, Competición y Temporada (Resuelve RF01 y RF08)
CREATE MATERIALIZED VIEW IF NOT EXISTS gold.agg_jugador_temporada_liga AS
SELECT hr.jugador_key,
       hr.competicion_key,
       dp.temporada,
       count(*) AS partidos,
       sum(hr.goles) AS goles,
       sum(hr.asistencias) AS asistencias,
       sum(hr.minutos_jugados) AS minutos,
       sum(hr.tarjetas_amarillas) AS amarillas,
       sum(hr.tarjetas_rojas) AS rojas,
       (dp.temporada - extract(year FROM dj.fecha_nacimiento))::int AS edad
FROM gold.hecho_rendimiento_jugador hr
JOIN gold.dim_partido dp ON dp.partido_key = hr.partido_key
JOIN gold.dim_jugador dj ON dj.jugador_key = hr.jugador_key
WHERE hr.es_sintetico = FALSE
GROUP BY hr.jugador_key, hr.competicion_key, dp.temporada, dj.fecha_nacimiento;

CREATE UNIQUE INDEX IF NOT EXISTS ux_agg_jugador_temporada_liga 
  ON gold.agg_jugador_temporada_liga (jugador_key, competicion_key, temporada);

-- 2. Tabla de Posiciones y Valor de Plantilla por Club y Temporada (Resuelve RF05)
CREATE MATERIALIZED VIEW IF NOT EXISTS gold.agg_club_temporada AS
WITH partidos AS (
  SELECT club_local_key AS club_key, temporada, goles_local AS gf, goles_visitante AS gc 
  FROM gold.dim_partido WHERE es_sintetico = FALSE
  UNION ALL
  SELECT club_visitante_key, temporada, goles_visitante, goles_local 
  FROM gold.dim_partido WHERE es_sintetico = FALSE
),
resumen AS (
  SELECT club_key, temporada,
         count(*) AS partidos,
         sum(gf) AS goles_favor,
         sum(gc) AS goles_contra,
         sum(CASE WHEN gf > gc THEN 3 WHEN gf = gc THEN 1 ELSE 0 END) AS puntos
  FROM partidos GROUP BY club_key, temporada
),
ultimo_valor AS (
  SELECT DISTINCT ON (hvm.jugador_key, df.temporada)
         hvm.jugador_key, df.temporada, hvm.club_key, hvm.valor_mercado_eur
  FROM gold.hecho_valoraciones_mercado hvm
  JOIN gold.dim_fecha df ON df.fecha_key = hvm.fecha_key
  WHERE hvm.es_sintetico = FALSE AND hvm.club_key IS NOT NULL AND hvm.valor_mercado_eur IS NOT NULL
  ORDER BY hvm.jugador_key, df.temporada, hvm.fecha_key DESC
),
valor AS (
  SELECT club_key, temporada, sum(valor_mercado_eur) AS valor_plantilla
  FROM ultimo_valor GROUP BY club_key, temporada
)
SELECT r.club_key, r.temporada, r.partidos, r.goles_favor, r.goles_contra, r.puntos, v.valor_plantilla
FROM resumen r
LEFT JOIN valor v ON v.club_key = r.club_key AND v.temporada = r.temporada;

CREATE UNIQUE INDEX IF NOT EXISTS ux_agg_club_temporada 
  ON gold.agg_club_temporada (club_key, temporada);

-- 3. Distribución de Incidencias en Franjas de 15 Minutos (Resuelve RF07)
CREATE MATERIALIZED VIEW IF NOT EXISTS gold.agg_eventos_15min AS
SELECT hep.tipo_evento_key,
       hep.franja_15min,
       df.temporada,
       count(*) AS total_eventos
FROM gold.hecho_eventos_partido hep
JOIN gold.dim_fecha df ON df.fecha_key = hep.fecha_key
WHERE hep.es_sintetico = FALSE AND hep.franja_15min IS NOT NULL
GROUP BY hep.tipo_evento_key, hep.franja_15min, df.temporada;

CREATE UNIQUE INDEX IF NOT EXISTS ux_agg_eventos_15min 
  ON gold.agg_eventos_15min (tipo_evento_key, franja_15min, temporada);

-- 4. Disciplina Arbitral por 90 Minutos y Temporada (Resuelve RF06)
CREATE MATERIALIZED VIEW IF NOT EXISTS gold.agg_disciplina_arbitro AS
SELECT dp.arbitro_key,
       dp.temporada,
       count(DISTINCT dp.partido_key) AS partidos,
       sum(hr.tarjetas_amarillas) AS amarillas,
       sum(hr.tarjetas_rojas) AS rojas,
       sum(hr.minutos_jugados) AS minutos,
       round(sum(hr.tarjetas_amarillas + hr.tarjetas_rojas) * 90.0 / NULLIF(sum(hr.minutos_jugados), 0), 4) AS tarjetas_por_90,
       round((sum(hr.tarjetas_amarillas) + sum(hr.tarjetas_rojas))::numeric / NULLIF(count(DISTINCT dp.partido_key), 0), 3) AS tarjetas_por_partido
FROM gold.hecho_rendimiento_jugador hr
JOIN gold.dim_partido dp ON dp.partido_key = hr.partido_key
WHERE hr.es_sintetico = FALSE AND dp.es_sintetico = FALSE
GROUP BY dp.arbitro_key, dp.temporada;

CREATE UNIQUE INDEX IF NOT EXISTS ux_agg_disciplina_arbitro 
  ON gold.agg_disciplina_arbitro (arbitro_key, temporada);

-- 5. Rendimiento Local vs Visitante por Competición y Temporada (Resuelve RF04)
CREATE MATERIALIZED VIEW IF NOT EXISTS gold.agg_local_visitante AS
SELECT competicion_key,
       temporada,
       count(*) AS partidos,
       sum((goles_local > goles_visitante)::int) AS victorias_local,
       sum((goles_local = goles_visitante)::int) AS empates,
       sum((goles_local < goles_visitante)::int) AS victorias_visitante,
       round(avg(goles_local), 3) AS goles_local_prom,
       round(avg(goles_visitante), 3) AS goles_visitante_prom
FROM gold.dim_partido 
WHERE es_sintetico = FALSE
GROUP BY competicion_key, temporada;

CREATE UNIQUE INDEX IF NOT EXISTS ux_agg_local_visitante 
  ON gold.agg_local_visitante (competicion_key, temporada);
