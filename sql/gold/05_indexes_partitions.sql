-- Particiones: 1990-2035 + DEFAULT. El ETL de oro amplía el rango si los datos lo exigen.
SELECT gold.ensure_event_partitions(1990, 2035);
CREATE TABLE IF NOT EXISTS gold.fact_events_default PARTITION OF gold.fact_events DEFAULT;

-- Índices B-Tree en todas las FK de los hechos (se propagan a las particiones)
CREATE UNIQUE INDEX IF NOT EXISTS ux_fact_events_bk ON gold.fact_events (game_event_id, date_key);
CREATE INDEX IF NOT EXISTS ix_fe_date ON gold.fact_events (date_key);
CREATE INDEX IF NOT EXISTS ix_fe_game ON gold.fact_events (game_key);
CREATE INDEX IF NOT EXISTS ix_fe_comp ON gold.fact_events (competition_key);
CREATE INDEX IF NOT EXISTS ix_fe_club ON gold.fact_events (club_key);
CREATE INDEX IF NOT EXISTS ix_fe_player ON gold.fact_events (player_key);
CREATE INDEX IF NOT EXISTS ix_fe_assist ON gold.fact_events (assist_player_key);
CREATE INDEX IF NOT EXISTS ix_fe_referee ON gold.fact_events (referee_key);
-- Hash en event_type_key (cardinalidad baja, igualdad)
CREATE INDEX IF NOT EXISTS ixh_fe_event_type ON gold.fact_events USING HASH (event_type_key);

CREATE INDEX IF NOT EXISTS ix_fa_date ON gold.fact_appearances (date_key);
CREATE INDEX IF NOT EXISTS ix_fa_game ON gold.fact_appearances (game_key);
CREATE INDEX IF NOT EXISTS ix_fa_player ON gold.fact_appearances (player_key);
CREATE INDEX IF NOT EXISTS ix_fa_club ON gold.fact_appearances (club_key);
CREATE INDEX IF NOT EXISTS ix_fa_comp ON gold.fact_appearances (competition_key);

CREATE INDEX IF NOT EXISTS ix_fv_date ON gold.fact_valuations (date_key);
CREATE INDEX IF NOT EXISTS ix_fv_club ON gold.fact_valuations (club_key);

CREATE INDEX IF NOT EXISTS ix_dg_comp ON gold.dim_game (competition_key);
CREATE INDEX IF NOT EXISTS ix_dg_referee ON gold.dim_game (referee_key);
CREATE INDEX IF NOT EXISTS ix_dg_home ON gold.dim_game (home_club_key);
CREATE INDEX IF NOT EXISTS ix_dg_away ON gold.dim_game (away_club_key);
CREATE INDEX IF NOT EXISTS ix_dg_season ON gold.dim_game (season);
