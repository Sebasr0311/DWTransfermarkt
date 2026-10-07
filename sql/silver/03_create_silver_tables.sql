-- Capa PLATA: datos limpios, tipados, con PK/FK y CHECK.
CREATE TABLE IF NOT EXISTS silver.competitions (
  competition_id VARCHAR(10) PRIMARY KEY,
  "name" TEXT NOT NULL, "type" TEXT NOT NULL, country_name TEXT NOT NULL, confederation TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS silver.clubs (
  club_id INT PRIMARY KEY,
  "name" TEXT NOT NULL,
  domestic_competition_id VARCHAR(10) REFERENCES silver.competitions(competition_id),
  stadium_name TEXT NOT NULL,
  squad_size SMALLINT CHECK (squad_size >= 0),
  average_age NUMERIC(4,1) CHECK (average_age >= 0));

CREATE TABLE IF NOT EXISTS silver.players (
  player_id INT PRIMARY KEY,
  "name" TEXT NOT NULL, "position" TEXT NOT NULL, sub_position TEXT NOT NULL,
  date_of_birth DATE,
  country_of_citizenship TEXT NOT NULL, foot TEXT NOT NULL,
  height_in_cm SMALLINT CHECK (height_in_cm BETWEEN 0 AND 260),
  current_club_id INT REFERENCES silver.clubs(club_id),
  market_value_in_eur NUMERIC(14,2) CHECK (market_value_in_eur >= 0));

CREATE TABLE IF NOT EXISTS silver.games (
  game_id INT PRIMARY KEY,
  competition_id VARCHAR(10) NOT NULL REFERENCES silver.competitions(competition_id),
  season SMALLINT NOT NULL, "round" TEXT NOT NULL,
  game_date DATE NOT NULL,
  home_club_id INT NOT NULL REFERENCES silver.clubs(club_id),
  away_club_id INT NOT NULL REFERENCES silver.clubs(club_id),
  home_club_goals SMALLINT NOT NULL DEFAULT 0 CHECK (home_club_goals >= 0),
  away_club_goals SMALLINT NOT NULL DEFAULT 0 CHECK (away_club_goals >= 0),
  stadium TEXT NOT NULL, attendance INT CHECK (attendance >= 0), referee TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS silver.appearances (
  appearance_id VARCHAR(40) PRIMARY KEY,
  game_id INT NOT NULL REFERENCES silver.games(game_id),
  player_id INT NOT NULL REFERENCES silver.players(player_id),
  player_club_id INT NOT NULL REFERENCES silver.clubs(club_id),
  game_date DATE NOT NULL,
  goals SMALLINT NOT NULL DEFAULT 0 CHECK (goals >= 0),
  assists SMALLINT NOT NULL DEFAULT 0 CHECK (assists >= 0),
  yellow_cards SMALLINT NOT NULL DEFAULT 0 CHECK (yellow_cards >= 0),
  red_cards SMALLINT NOT NULL DEFAULT 0 CHECK (red_cards >= 0),
  minutes_played SMALLINT NOT NULL DEFAULT 0 CHECK (minutes_played BETWEEN 0 AND 130));

CREATE TABLE IF NOT EXISTS silver.game_events (
  game_event_id VARCHAR(64) PRIMARY KEY,
  game_id INT NOT NULL REFERENCES silver.games(game_id),
  game_date DATE NOT NULL,
  "minute" SMALLINT CHECK ("minute" BETWEEN 0 AND 130),
  "type" TEXT NOT NULL,
  club_id INT NOT NULL REFERENCES silver.clubs(club_id),
  player_id INT REFERENCES silver.players(player_id),
  description TEXT,
  player_in_id INT, player_assist_id INT);

CREATE TABLE IF NOT EXISTS silver.player_valuations (
  player_id INT NOT NULL REFERENCES silver.players(player_id),
  valuation_date DATE NOT NULL,
  market_value_in_eur NUMERIC(14,2) CHECK (market_value_in_eur >= 0),
  current_club_id INT,
  PRIMARY KEY (player_id, valuation_date));

-- Índices de apoyo para las FK usadas en joins del ETL
CREATE INDEX IF NOT EXISTS ix_s_appearances_game ON silver.appearances (game_id);
CREATE INDEX IF NOT EXISTS ix_s_appearances_player ON silver.appearances (player_id);
CREATE INDEX IF NOT EXISTS ix_s_events_game ON silver.game_events (game_id);
CREATE INDEX IF NOT EXISTS ix_s_events_player ON silver.game_events (player_id);
CREATE INDEX IF NOT EXISTS ix_s_games_date ON silver.games (game_date);
