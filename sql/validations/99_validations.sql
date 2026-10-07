-- Cada fila: (check_name, failures). Todas deben devolver failures = 0.
SELECT * FROM (
  -- Huérfanos en silver (LEFT JOIN debe devolver 0 filas)
  SELECT 'orphans silver.clubs->competitions' AS check_name, count(*) AS failures
    FROM silver.clubs c LEFT JOIN silver.competitions p ON p.competition_id = c.domestic_competition_id
    WHERE c.domestic_competition_id IS NOT NULL AND p.competition_id IS NULL
  UNION ALL SELECT 'orphans silver.players->clubs', count(*)
    FROM silver.players c LEFT JOIN silver.clubs p ON p.club_id = c.current_club_id
    WHERE c.current_club_id IS NOT NULL AND p.club_id IS NULL
  UNION ALL SELECT 'orphans silver.games->competitions', count(*)
    FROM silver.games c LEFT JOIN silver.competitions p ON p.competition_id = c.competition_id WHERE p.competition_id IS NULL
  UNION ALL SELECT 'orphans silver.games->clubs(home)', count(*)
    FROM silver.games c LEFT JOIN silver.clubs p ON p.club_id = c.home_club_id WHERE p.club_id IS NULL
  UNION ALL SELECT 'orphans silver.games->clubs(away)', count(*)
    FROM silver.games c LEFT JOIN silver.clubs p ON p.club_id = c.away_club_id WHERE p.club_id IS NULL
  UNION ALL SELECT 'orphans silver.appearances->games', count(*)
    FROM silver.appearances c LEFT JOIN silver.games p ON p.game_id = c.game_id WHERE p.game_id IS NULL
  UNION ALL SELECT 'orphans silver.appearances->players', count(*)
    FROM silver.appearances c LEFT JOIN silver.players p ON p.player_id = c.player_id WHERE p.player_id IS NULL
  UNION ALL SELECT 'orphans silver.appearances->clubs', count(*)
    FROM silver.appearances c LEFT JOIN silver.clubs p ON p.club_id = c.player_club_id WHERE p.club_id IS NULL
  UNION ALL SELECT 'orphans silver.game_events->games', count(*)
    FROM silver.game_events c LEFT JOIN silver.games p ON p.game_id = c.game_id WHERE p.game_id IS NULL
  UNION ALL SELECT 'orphans silver.game_events->clubs', count(*)
    FROM silver.game_events c LEFT JOIN silver.clubs p ON p.club_id = c.club_id WHERE p.club_id IS NULL
  UNION ALL SELECT 'orphans silver.game_events->players', count(*)
    FROM silver.game_events c LEFT JOIN silver.players p ON p.player_id = c.player_id
    WHERE c.player_id IS NOT NULL AND p.player_id IS NULL
  UNION ALL SELECT 'orphans silver.player_valuations->players', count(*)
    FROM silver.player_valuations c LEFT JOIN silver.players p ON p.player_id = c.player_id WHERE p.player_id IS NULL

  -- Huérfanos en gold
  UNION ALL SELECT 'orphans gold.fact_events->dim_game', count(*)
    FROM gold.fact_events f LEFT JOIN gold.dim_game d ON d.game_key = f.game_key WHERE d.game_key IS NULL
  UNION ALL SELECT 'orphans gold.fact_events->dim_club', count(*)
    FROM gold.fact_events f LEFT JOIN gold.dim_club d ON d.club_key = f.club_key WHERE d.club_key IS NULL
  UNION ALL SELECT 'orphans gold.fact_events->dim_event_type', count(*)
    FROM gold.fact_events f LEFT JOIN gold.dim_event_type d ON d.event_type_key = f.event_type_key WHERE d.event_type_key IS NULL
  UNION ALL SELECT 'orphans gold.fact_appearances->dim_game', count(*)
    FROM gold.fact_appearances f LEFT JOIN gold.dim_game d ON d.game_key = f.game_key WHERE d.game_key IS NULL
  UNION ALL SELECT 'orphans gold.fact_appearances->dim_player', count(*)
    FROM gold.fact_appearances f LEFT JOIN gold.dim_player d ON d.player_key = f.player_key WHERE d.player_key IS NULL
  UNION ALL SELECT 'orphans gold.fact_appearances->dim_club', count(*)
    FROM gold.fact_appearances f LEFT JOIN gold.dim_club d ON d.club_key = f.club_key WHERE d.club_key IS NULL
  UNION ALL SELECT 'orphans gold.fact_valuations->dim_player', count(*)
    FROM gold.fact_valuations f LEFT JOIN gold.dim_player d ON d.player_key = f.player_key WHERE d.player_key IS NULL

  -- Duplicados por llave de negocio
  UNION ALL SELECT 'dups silver.games', count(*) FROM (SELECT game_id FROM silver.games GROUP BY 1 HAVING count(*) > 1) x
  UNION ALL SELECT 'dups silver.appearances', count(*) FROM (SELECT appearance_id FROM silver.appearances GROUP BY 1 HAVING count(*) > 1) x
  UNION ALL SELECT 'dups silver.game_events', count(*) FROM (SELECT game_event_id FROM silver.game_events GROUP BY 1 HAVING count(*) > 1) x
  UNION ALL SELECT 'dups silver.player_valuations', count(*) FROM (SELECT player_id, valuation_date FROM silver.player_valuations GROUP BY 1,2 HAVING count(*) > 1) x
  UNION ALL SELECT 'dups gold.dim_game', count(*) FROM (SELECT game_id FROM gold.dim_game GROUP BY 1 HAVING count(*) > 1) x
  UNION ALL SELECT 'dups gold.fact_events', count(*) FROM (SELECT game_event_id, date_key FROM gold.fact_events GROUP BY 1,2 HAVING count(*) > 1) x
  UNION ALL SELECT 'dups gold.fact_appearances', count(*) FROM (SELECT appearance_id FROM gold.fact_appearances GROUP BY 1 HAVING count(*) > 1) x
  UNION ALL SELECT 'dups gold.fact_valuations', count(*) FROM (SELECT player_key, date_key FROM gold.fact_valuations GROUP BY 1,2 HAVING count(*) > 1) x
  UNION ALL SELECT 'dups gold.dim_player', count(*) FROM (SELECT player_id FROM gold.dim_player GROUP BY 1 HAVING count(*) > 1) x

  -- Fechas obligatorias sin NULL
  UNION ALL SELECT 'nulls silver.games.game_date', count(*) FROM silver.games WHERE game_date IS NULL
  UNION ALL SELECT 'nulls silver.appearances.game_date', count(*) FROM silver.appearances WHERE game_date IS NULL
  UNION ALL SELECT 'nulls silver.game_events.game_date', count(*) FROM silver.game_events WHERE game_date IS NULL
  UNION ALL SELECT 'nulls silver.player_valuations.valuation_date', count(*) FROM silver.player_valuations WHERE valuation_date IS NULL

  -- Rangos
  UNION ALL SELECT 'range silver.game_events.minute', count(*) FROM silver.game_events WHERE "minute" < 0 OR "minute" > 130
  UNION ALL SELECT 'range silver.appearances.minutes_played', count(*) FROM silver.appearances WHERE minutes_played < 0 OR minutes_played > 130

  -- Restricciones de dominio origin
  UNION ALL SELECT 'invalid silver.games.origin', count(*) FROM silver.games WHERE origin NOT IN ('real', 'sintetico')
  UNION ALL SELECT 'invalid silver.appearances.origin', count(*) FROM silver.appearances WHERE origin NOT IN ('real', 'sintetico')
  UNION ALL SELECT 'invalid silver.game_events.origin', count(*) FROM silver.game_events WHERE origin NOT IN ('real', 'sintetico')
  UNION ALL SELECT 'invalid silver.player_valuations.origin', count(*) FROM silver.player_valuations WHERE origin NOT IN ('real', 'sintetico')

  -- Partición default de gold.fact_events vacía
  UNION ALL SELECT 'gold.fact_events default partition rows', count(*) FROM gold.fact_events_default
) v ORDER BY check_name;
