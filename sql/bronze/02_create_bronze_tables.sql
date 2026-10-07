-- Capa BRONCE: copia cruda de los CSV. Todo TEXT, sin correcciones.
-- Columnas de linaje: _load_id, _loaded_at, _source_file (+ _row_id para ordenar/deduplicar).
CREATE TABLE IF NOT EXISTS bronze.competitions (
  competition_id TEXT, competition_code TEXT, "name" TEXT, sub_type TEXT, "type" TEXT,
  country_id TEXT, country_name TEXT, domestic_league_code TEXT, confederation TEXT, total_clubs TEXT, url TEXT,
  _row_id BIGSERIAL, _load_id UUID, _loaded_at TIMESTAMP DEFAULT now(), _source_file TEXT);

CREATE TABLE IF NOT EXISTS bronze.clubs (
  club_id TEXT, club_code TEXT, "name" TEXT, domestic_competition_id TEXT, total_market_value TEXT,
  squad_size TEXT, average_age TEXT, foreigners_number TEXT, foreigners_percentage TEXT,
  national_team_players TEXT, stadium_name TEXT, stadium_seats TEXT, net_transfer_record TEXT,
  coach_name TEXT, last_season TEXT, filename TEXT, url TEXT,
  _row_id BIGSERIAL, _load_id UUID, _loaded_at TIMESTAMP DEFAULT now(), _source_file TEXT);

CREATE TABLE IF NOT EXISTS bronze.players (
  player_id TEXT, first_name TEXT, last_name TEXT, "name" TEXT, last_season TEXT, current_club_id TEXT,
  player_code TEXT, country_of_birth TEXT, city_of_birth TEXT, country_of_citizenship TEXT,
  date_of_birth TEXT, sub_position TEXT, "position" TEXT, foot TEXT, height_in_cm TEXT,
  contract_expiration_date TEXT, agent_name TEXT, image_url TEXT,
  international_caps TEXT, international_goals TEXT, current_national_team_id TEXT, url TEXT,
  current_club_domestic_competition_id TEXT, current_club_name TEXT,
  market_value_in_eur TEXT, highest_market_value_in_eur TEXT,
  _row_id BIGSERIAL, _load_id UUID, _loaded_at TIMESTAMP DEFAULT now(), _source_file TEXT);

CREATE TABLE IF NOT EXISTS bronze.games (
  game_id TEXT, competition_id TEXT, season TEXT, "round" TEXT, "date" TEXT, home_club_id TEXT,
  away_club_id TEXT, home_club_goals TEXT, away_club_goals TEXT, home_club_position TEXT,
  away_club_position TEXT, home_club_manager_name TEXT, away_club_manager_name TEXT, stadium TEXT,
  attendance TEXT, referee TEXT, url TEXT, home_club_formation TEXT, away_club_formation TEXT,
  home_club_name TEXT, away_club_name TEXT, aggregate TEXT, competition_type TEXT,
  _row_id BIGSERIAL, _load_id UUID, _loaded_at TIMESTAMP DEFAULT now(), _source_file TEXT);

CREATE TABLE IF NOT EXISTS bronze.appearances (
  appearance_id TEXT, game_id TEXT, player_id TEXT, player_club_id TEXT, player_current_club_id TEXT,
  "date" TEXT, player_name TEXT, competition_id TEXT, yellow_cards TEXT, red_cards TEXT,
  goals TEXT, assists TEXT, minutes_played TEXT,
  _row_id BIGSERIAL, _load_id UUID, _loaded_at TIMESTAMP DEFAULT now(), _source_file TEXT);

CREATE TABLE IF NOT EXISTS bronze.game_events (
  game_event_id TEXT, "date" TEXT, game_id TEXT, "minute" TEXT, "type" TEXT, club_id TEXT,
  club_name TEXT, player_id TEXT, description TEXT, player_in_id TEXT, player_assist_id TEXT,
  _row_id BIGSERIAL, _load_id UUID, _loaded_at TIMESTAMP DEFAULT now(), _source_file TEXT);

CREATE TABLE IF NOT EXISTS bronze.player_valuations (
  player_id TEXT, "date" TEXT, market_value_in_eur TEXT, current_club_name TEXT,
  current_club_id TEXT, player_club_domestic_competition_id TEXT,
  _row_id BIGSERIAL, _load_id UUID, _loaded_at TIMESTAMP DEFAULT now(), _source_file TEXT);
