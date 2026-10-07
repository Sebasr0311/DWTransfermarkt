-- RF10: vistas materializadas de agregación (todas con índice único para REFRESH CONCURRENTLY)
CREATE MATERIALIZED VIEW IF NOT EXISTS gold.agg_player_season AS
SELECT fa.player_key, dg.season,
       count(*) AS partidos,
       sum(fa.goals) AS goles, sum(fa.assists) AS asistencias, sum(fa.minutes_played) AS minutos,
       sum(fa.yellow_cards) AS amarillas, sum(fa.red_cards) AS rojas,
       (dg.season - extract(year FROM dp.date_of_birth))::int AS edad
FROM gold.fact_appearances fa
JOIN gold.dim_game dg ON dg.game_key = fa.game_key
JOIN gold.dim_player dp ON dp.player_key = fa.player_key
GROUP BY fa.player_key, dg.season, dp.date_of_birth;
CREATE UNIQUE INDEX IF NOT EXISTS ux_agg_player_season ON gold.agg_player_season (player_key, season);

CREATE MATERIALIZED VIEW IF NOT EXISTS gold.agg_club_season AS
WITH partidos AS (
  SELECT home_club_key AS club_key, season, home_club_goals AS gf, away_club_goals AS gc FROM gold.dim_game
  UNION ALL
  SELECT away_club_key, season, away_club_goals, home_club_goals FROM gold.dim_game),
resumen AS (
  SELECT club_key, season, count(*) AS partidos, sum(gf) AS goles_favor, sum(gc) AS goles_contra,
         sum(CASE WHEN gf > gc THEN 3 WHEN gf = gc THEN 1 ELSE 0 END) AS puntos
  FROM partidos GROUP BY club_key, season),
ultimo_valor AS (
  SELECT DISTINCT ON (fv.player_key, dd.season) fv.player_key, dd.season, fv.club_key, fv.market_value_eur
  FROM gold.fact_valuations fv JOIN gold.dim_date dd ON dd.date_key = fv.date_key
  WHERE fv.club_key IS NOT NULL AND fv.market_value_eur IS NOT NULL
  ORDER BY fv.player_key, dd.season, fv.date_key DESC),
valor AS (
  SELECT club_key, season, sum(market_value_eur) AS valor_plantilla FROM ultimo_valor GROUP BY club_key, season)
SELECT r.club_key, r.season, r.partidos, r.goles_favor, r.goles_contra, r.puntos, v.valor_plantilla
FROM resumen r LEFT JOIN valor v ON v.club_key = r.club_key AND v.season = r.season;
CREATE UNIQUE INDEX IF NOT EXISTS ux_agg_club_season ON gold.agg_club_season (club_key, season);

CREATE MATERIALIZED VIEW IF NOT EXISTS gold.agg_events_15min AS
SELECT fe.event_type_key, fe.minute_bucket, dd.season, count(*) AS eventos
FROM gold.fact_events fe JOIN gold.dim_date dd ON dd.date_key = fe.date_key
WHERE fe.minute_bucket IS NOT NULL
GROUP BY fe.event_type_key, fe.minute_bucket, dd.season;
CREATE UNIQUE INDEX IF NOT EXISTS ux_agg_events_15min ON gold.agg_events_15min (event_type_key, minute_bucket, season);

CREATE MATERIALIZED VIEW IF NOT EXISTS gold.agg_discipline_ref AS
SELECT dg.referee_key, dg.season,
       count(DISTINCT dg.game_key) AS partidos,
       sum(fa.yellow_cards) AS amarillas, sum(fa.red_cards) AS rojas,
       sum(fa.minutes_played) AS minutos,
       round(sum(fa.yellow_cards + fa.red_cards) * 90.0 / NULLIF(sum(fa.minutes_played), 0), 4) AS tarjetas_por_90,
       round((sum(fa.yellow_cards) + sum(fa.red_cards))::numeric / NULLIF(count(DISTINCT dg.game_key), 0), 3) AS tarjetas_por_partido
FROM gold.fact_appearances fa JOIN gold.dim_game dg ON dg.game_key = fa.game_key
GROUP BY dg.referee_key, dg.season;
CREATE UNIQUE INDEX IF NOT EXISTS ux_agg_discipline_ref ON gold.agg_discipline_ref (referee_key, season);

CREATE MATERIALIZED VIEW IF NOT EXISTS gold.agg_home_away AS
SELECT competition_key, season, count(*) AS partidos,
       sum((home_club_goals > away_club_goals)::int) AS victorias_local,
       sum((home_club_goals = away_club_goals)::int) AS empates,
       sum((home_club_goals < away_club_goals)::int) AS victorias_visitante,
       round(avg(home_club_goals), 3) AS goles_local_prom,
       round(avg(away_club_goals), 3) AS goles_visitante_prom
FROM gold.dim_game GROUP BY competition_key, season;
CREATE UNIQUE INDEX IF NOT EXISTS ux_agg_home_away ON gold.agg_home_away (competition_key, season);
