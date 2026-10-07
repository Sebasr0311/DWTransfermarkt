-- Capa ORO: modelo estrella. Dimensiones con llave sustituta y llave de negocio UNIQUE.
CREATE TABLE IF NOT EXISTS gold.dim_date (
  date_key INT PRIMARY KEY,               -- AAAAMMDD
  full_date DATE NOT NULL UNIQUE,
  year SMALLINT NOT NULL, quarter SMALLINT NOT NULL, month SMALLINT NOT NULL,
  month_name VARCHAR(12) NOT NULL, week SMALLINT NOT NULL,
  season SMALLINT NOT NULL);              -- año de inicio de temporada (jul-jun)

CREATE TABLE IF NOT EXISTS gold.dim_competition (
  competition_key SERIAL PRIMARY KEY, competition_id VARCHAR(10) NOT NULL UNIQUE,
  "name" TEXT, "type" TEXT, country_name TEXT, confederation TEXT);

CREATE TABLE IF NOT EXISTS gold.dim_club (
  club_key SERIAL PRIMARY KEY, club_id INT NOT NULL UNIQUE,
  "name" TEXT, domestic_competition_id VARCHAR(10), stadium_name TEXT,
  squad_size SMALLINT, average_age NUMERIC(4,1));

CREATE TABLE IF NOT EXISTS gold.dim_player (
  player_key SERIAL PRIMARY KEY, player_id INT NOT NULL UNIQUE,
  "name" TEXT, "position" TEXT, sub_position TEXT, date_of_birth DATE,
  country_of_citizenship TEXT, foot TEXT, height_in_cm SMALLINT);

CREATE TABLE IF NOT EXISTS gold.dim_referee (
  referee_key SERIAL PRIMARY KEY, referee_name TEXT NOT NULL UNIQUE);

CREATE TABLE IF NOT EXISTS gold.dim_event_type (
  event_type_key SERIAL PRIMARY KEY, event_type_name TEXT NOT NULL UNIQUE);

CREATE TABLE IF NOT EXISTS gold.dim_game (
  game_key SERIAL PRIMARY KEY, game_id INT NOT NULL UNIQUE,
  competition_key INT NOT NULL REFERENCES gold.dim_competition(competition_key),
  referee_key INT NOT NULL REFERENCES gold.dim_referee(referee_key),
  home_club_key INT NOT NULL REFERENCES gold.dim_club(club_key),
  away_club_key INT NOT NULL REFERENCES gold.dim_club(club_key),
  date_key INT NOT NULL REFERENCES gold.dim_date(date_key),
  season SMALLINT NOT NULL, "round" TEXT, game_date DATE NOT NULL,
  home_club_goals SMALLINT, away_club_goals SMALLINT, stadium TEXT, attendance INT,
  is_synthetic BOOLEAN NOT NULL DEFAULT FALSE);

-- Hechos
CREATE TABLE IF NOT EXISTS gold.fact_events (
  event_key BIGSERIAL,
  game_event_id VARCHAR(64) NOT NULL,     -- llave de negocio (idempotencia)
  date_key INT NOT NULL REFERENCES gold.dim_date(date_key),
  game_key INT NOT NULL REFERENCES gold.dim_game(game_key),
  competition_key INT NOT NULL REFERENCES gold.dim_competition(competition_key),
  club_key INT NOT NULL REFERENCES gold.dim_club(club_key),
  player_key INT REFERENCES gold.dim_player(player_key),
  assist_player_key INT REFERENCES gold.dim_player(player_key),
  referee_key INT NOT NULL REFERENCES gold.dim_referee(referee_key),
  event_type_key INT NOT NULL REFERENCES gold.dim_event_type(event_type_key),
  "minute" SMALLINT, minute_bucket SMALLINT, is_home BOOLEAN,
  is_synthetic BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY (event_key, date_key)
) PARTITION BY RANGE (date_key);

CREATE TABLE IF NOT EXISTS gold.fact_appearances (
  appearance_key BIGSERIAL PRIMARY KEY,
  appearance_id VARCHAR(40) NOT NULL UNIQUE,
  date_key INT NOT NULL REFERENCES gold.dim_date(date_key),
  game_key INT NOT NULL REFERENCES gold.dim_game(game_key),
  player_key INT NOT NULL REFERENCES gold.dim_player(player_key),
  club_key INT NOT NULL REFERENCES gold.dim_club(club_key),
  competition_key INT NOT NULL REFERENCES gold.dim_competition(competition_key),
  goals SMALLINT, assists SMALLINT, yellow_cards SMALLINT, red_cards SMALLINT, minutes_played SMALLINT,
  is_synthetic BOOLEAN NOT NULL DEFAULT FALSE);

CREATE TABLE IF NOT EXISTS gold.fact_valuations (
  valuation_key BIGSERIAL PRIMARY KEY,
  date_key INT NOT NULL REFERENCES gold.dim_date(date_key),
  player_key INT NOT NULL REFERENCES gold.dim_player(player_key),
  club_key INT REFERENCES gold.dim_club(club_key),
  market_value_eur NUMERIC(14,2),
  is_synthetic BOOLEAN NOT NULL DEFAULT FALSE,
  UNIQUE (player_key, date_key));

-- Crea particiones anuales de fact_events (date_key = AAAAMMDD) para el rango de años dado
CREATE OR REPLACE FUNCTION gold.ensure_event_partitions(y_from INT, y_to INT) RETURNS VOID
LANGUAGE plpgsql AS $$
DECLARE y INT;
BEGIN
  FOR y IN y_from..y_to LOOP
    EXECUTE format(
      'CREATE TABLE IF NOT EXISTS gold.fact_events_%s PARTITION OF gold.fact_events FOR VALUES FROM (%s) TO (%s)',
      y, y * 10000 + 101, (y + 1) * 10000 + 101);
  END LOOP;
END $$;
