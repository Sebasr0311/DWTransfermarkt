"""Carga silver -> gold: dimensiones, hechos con llaves sustitutas, minute_bucket e is_home. Idempotente."""
from etl.common.audit import Audit
from etl.common.db import get_connection

MESES = "ARRAY['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']"

DIMENSIONES = {
    "dim_competition": ("silver.competitions", """
        INSERT INTO gold.dim_competition (competition_id, "name", "type", country_name, confederation)
        SELECT competition_id, "name", "type", country_name, confederation FROM silver.competitions
        ON CONFLICT (competition_id) DO UPDATE SET "name"=EXCLUDED."name", "type"=EXCLUDED."type",
          country_name=EXCLUDED.country_name, confederation=EXCLUDED.confederation"""),
    "dim_club": ("silver.clubs", """
        INSERT INTO gold.dim_club (club_id, "name", domestic_competition_id, stadium_name, squad_size, average_age)
        SELECT club_id, "name", domestic_competition_id, stadium_name, squad_size, average_age FROM silver.clubs
        ON CONFLICT (club_id) DO UPDATE SET "name"=EXCLUDED."name",
          domestic_competition_id=EXCLUDED.domestic_competition_id, stadium_name=EXCLUDED.stadium_name,
          squad_size=EXCLUDED.squad_size, average_age=EXCLUDED.average_age"""),
    "dim_player": ("silver.players", """
        INSERT INTO gold.dim_player (player_id, "name", "position", sub_position, date_of_birth,
                                     country_of_citizenship, foot, height_in_cm)
        SELECT player_id, "name", "position", sub_position, date_of_birth, country_of_citizenship, foot, height_in_cm
        FROM silver.players
        ON CONFLICT (player_id) DO UPDATE SET "name"=EXCLUDED."name", "position"=EXCLUDED."position",
          sub_position=EXCLUDED.sub_position, date_of_birth=EXCLUDED.date_of_birth,
          country_of_citizenship=EXCLUDED.country_of_citizenship, foot=EXCLUDED.foot,
          height_in_cm=EXCLUDED.height_in_cm"""),
    "dim_referee": ("silver.games", """
        INSERT INTO gold.dim_referee (referee_name) SELECT DISTINCT referee FROM silver.games
        ON CONFLICT (referee_name) DO NOTHING"""),
    "dim_event_type": ("silver.game_events", """
        INSERT INTO gold.dim_event_type (event_type_name) SELECT DISTINCT "type" FROM silver.game_events
        ON CONFLICT (event_type_name) DO NOTHING"""),
}

DIM_GAME = """
INSERT INTO gold.dim_game (game_id, competition_key, referee_key, home_club_key, away_club_key, date_key,
                           season, "round", game_date, home_club_goals, away_club_goals, stadium, attendance, is_synthetic)
SELECT g.game_id, dc.competition_key, dr.referee_key, dh.club_key, da.club_key,
       to_char(g.game_date, 'YYYYMMDD')::int, g.season, g."round", g.game_date,
       g.home_club_goals, g.away_club_goals, g.stadium, g.attendance,
       (g.origin = 'sintetico')
FROM silver.games g
JOIN gold.dim_competition dc ON dc.competition_id = g.competition_id
JOIN gold.dim_referee dr ON dr.referee_name = g.referee
JOIN gold.dim_club dh ON dh.club_id = g.home_club_id
JOIN gold.dim_club da ON da.club_id = g.away_club_id
ON CONFLICT (game_id) DO UPDATE SET competition_key=EXCLUDED.competition_key, referee_key=EXCLUDED.referee_key,
  home_club_key=EXCLUDED.home_club_key, away_club_key=EXCLUDED.away_club_key, date_key=EXCLUDED.date_key,
  season=EXCLUDED.season, "round"=EXCLUDED."round", game_date=EXCLUDED.game_date,
  home_club_goals=EXCLUDED.home_club_goals, away_club_goals=EXCLUDED.away_club_goals,
  stadium=EXCLUDED.stadium, attendance=EXCLUDED.attendance, is_synthetic=EXCLUDED.is_synthetic"""

# Hechos: se cargan por año (rango de fechas) para acotar el tamaño de cada transacción.
FACT_EVENTS = """
INSERT INTO gold.fact_events (game_event_id, date_key, game_key, competition_key, club_key, player_key,
                              assist_player_key, referee_key, event_type_key, "minute", minute_bucket, is_home, is_synthetic)
SELECT e.game_event_id, to_char(e.game_date, 'YYYYMMDD')::int, dg.game_key, dg.competition_key, dc.club_key,
       dp.player_key, da.player_key, dg.referee_key, et.event_type_key, e."minute",
       CASE WHEN e."minute" IS NULL THEN NULL ELSE LEAST(e."minute" / 15, 6) END,
       (dc.club_key = dg.home_club_key),
       (e.origin = 'sintetico')
FROM silver.game_events e
JOIN gold.dim_game dg ON dg.game_id = e.game_id
JOIN gold.dim_club dc ON dc.club_id = e.club_id
JOIN gold.dim_event_type et ON et.event_type_name = e."type"
LEFT JOIN gold.dim_player dp ON dp.player_id = e.player_id
LEFT JOIN gold.dim_player da ON da.player_id = e.player_assist_id
WHERE e.game_date >= %(d0)s AND e.game_date < %(d1)s
ON CONFLICT (game_event_id, date_key) DO UPDATE SET game_key=EXCLUDED.game_key,
  competition_key=EXCLUDED.competition_key, club_key=EXCLUDED.club_key, player_key=EXCLUDED.player_key,
  assist_player_key=EXCLUDED.assist_player_key, referee_key=EXCLUDED.referee_key,
  event_type_key=EXCLUDED.event_type_key, "minute"=EXCLUDED."minute",
  minute_bucket=EXCLUDED.minute_bucket, is_home=EXCLUDED.is_home, is_synthetic=EXCLUDED.is_synthetic
WHERE (gold.fact_events.game_key, gold.fact_events.club_key, gold.fact_events.player_key,
       gold.fact_events.assist_player_key, gold.fact_events.event_type_key, gold.fact_events."minute",
       gold.fact_events.is_home, gold.fact_events.is_synthetic)
  IS DISTINCT FROM (EXCLUDED.game_key, EXCLUDED.club_key, EXCLUDED.player_key, EXCLUDED.assist_player_key,
                    EXCLUDED.event_type_key, EXCLUDED."minute", EXCLUDED.is_home, EXCLUDED.is_synthetic)"""

FACT_APPEARANCES = """
INSERT INTO gold.fact_appearances (appearance_id, date_key, game_key, player_key, club_key, competition_key,
                                   goals, assists, yellow_cards, red_cards, minutes_played, is_synthetic)
SELECT a.appearance_id, to_char(a.game_date, 'YYYYMMDD')::int, dg.game_key, dp.player_key, dc.club_key,
       dg.competition_key, a.goals, a.assists, a.yellow_cards, a.red_cards, a.minutes_played,
       (a.origin = 'sintetico')
FROM silver.appearances a
JOIN gold.dim_game dg ON dg.game_id = a.game_id
JOIN gold.dim_player dp ON dp.player_id = a.player_id
JOIN gold.dim_club dc ON dc.club_id = a.player_club_id
WHERE a.game_date >= %(d0)s AND a.game_date < %(d1)s
ON CONFLICT (appearance_id) DO UPDATE SET date_key=EXCLUDED.date_key, game_key=EXCLUDED.game_key,
  player_key=EXCLUDED.player_key, club_key=EXCLUDED.club_key, competition_key=EXCLUDED.competition_key,
  goals=EXCLUDED.goals, assists=EXCLUDED.assists, yellow_cards=EXCLUDED.yellow_cards,
  red_cards=EXCLUDED.red_cards, minutes_played=EXCLUDED.minutes_played, is_synthetic=EXCLUDED.is_synthetic
WHERE (gold.fact_appearances.date_key, gold.fact_appearances.game_key, gold.fact_appearances.player_key,
       gold.fact_appearances.club_key, gold.fact_appearances.goals, gold.fact_appearances.assists,
       gold.fact_appearances.yellow_cards, gold.fact_appearances.red_cards, gold.fact_appearances.minutes_played,
       gold.fact_appearances.is_synthetic)
  IS DISTINCT FROM (EXCLUDED.date_key, EXCLUDED.game_key, EXCLUDED.player_key, EXCLUDED.club_key,
                    EXCLUDED.goals, EXCLUDED.assists, EXCLUDED.yellow_cards, EXCLUDED.red_cards,
                    EXCLUDED.minutes_played, EXCLUDED.is_synthetic)"""

FACT_VALUATIONS = """
INSERT INTO gold.fact_valuations (date_key, player_key, club_key, market_value_eur, is_synthetic)
SELECT to_char(v.valuation_date, 'YYYYMMDD')::int, dp.player_key, dc.club_key, v.market_value_in_eur,
       (v.origin = 'sintetico')
FROM silver.player_valuations v
JOIN gold.dim_player dp ON dp.player_id = v.player_id
LEFT JOIN gold.dim_club dc ON dc.club_id = v.current_club_id
WHERE v.valuation_date >= %(d0)s AND v.valuation_date < %(d1)s
ON CONFLICT (player_key, date_key) DO UPDATE SET club_key=EXCLUDED.club_key,
  market_value_eur=EXCLUDED.market_value_eur, is_synthetic=EXCLUDED.is_synthetic
WHERE (gold.fact_valuations.club_key, gold.fact_valuations.market_value_eur, gold.fact_valuations.is_synthetic)
  IS DISTINCT FROM (EXCLUDED.club_key, EXCLUDED.market_value_eur, EXCLUDED.is_synthetic)"""


def _ejecutar(conn, audit, tabla, sql_leidas, sql_carga, params=None):
    audit_id = audit.start(tabla)
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT count(*) FROM {sql_leidas}")
        leidas = cur.fetchone()[0]
        cur.execute(sql_carga, params or {})
        afectadas = cur.rowcount
        conn.commit()
        audit.finish(audit_id, read=leidas, transformed=leidas, discarded=max(leidas - afectadas, 0), inserted=afectadas)
        print(f"[gold] {tabla}: leídas={leidas} insertadas/actualizadas={afectadas}")
    except Exception:
        conn.rollback()
        audit.finish(audit_id, status="ERROR")
        raise
    finally:
        cur.close()


def _cargar_hechos(conn, audit, tabla, origen, sql, anios):
    """Carga un hecho año por año; el audit registra el total de la tabla."""
    audit_id = audit.start(tabla)
    leidas = afectadas = 0
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT count(*) FROM {origen}")
        leidas = cur.fetchone()[0]
        for y in anios:
            cur.execute(sql, {"d0": f"{y}-01-01", "d1": f"{y + 1}-01-01"})
            afectadas += cur.rowcount
            conn.commit()
        audit.finish(audit_id, read=leidas, transformed=leidas, discarded=max(leidas - afectadas, 0), inserted=afectadas)
        print(f"[gold] {tabla}: leídas={leidas} insertadas/actualizadas={afectadas}")
    except Exception:
        conn.rollback()
        audit.finish(audit_id, status="ERROR")
        raise
    finally:
        cur.close()


def run(run_id: str, chunk_size: int | None = None) -> dict:
    audit = Audit(run_id, "gold")
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT min(d), max(d) FROM (
              SELECT min(game_date) d FROM silver.games UNION ALL SELECT max(game_date) FROM silver.games
              UNION ALL SELECT min(game_date) FROM silver.appearances UNION ALL SELECT max(game_date) FROM silver.appearances
              UNION ALL SELECT min(game_date) FROM silver.game_events UNION ALL SELECT max(game_date) FROM silver.game_events
              UNION ALL SELECT min(valuation_date) FROM silver.player_valuations
              UNION ALL SELECT max(valuation_date) FROM silver.player_valuations) t""")
        dmin, dmax = cur.fetchone()
        if dmin is None:
            print("[gold] silver sin fechas (vacío) -> nada que cargar")
            return {}
        y0, y1 = dmin.year, dmax.year

        # dim_date: todas las fechas del rango (años completos) y particiones de fact_events
        cur.execute(f"""
            INSERT INTO gold.dim_date (date_key, full_date, year, quarter, month, month_name, week, season)
            SELECT to_char(d, 'YYYYMMDD')::int, d::date, extract(year FROM d), extract(quarter FROM d),
                   extract(month FROM d), ({MESES})[extract(month FROM d)::int], extract(week FROM d),
                   CASE WHEN extract(month FROM d) >= 7 THEN extract(year FROM d) ELSE extract(year FROM d) - 1 END
            FROM generate_series(make_date(%s,1,1), make_date(%s,12,31), interval '1 day') d
            ON CONFLICT (date_key) DO NOTHING""", (y0, y1))
        cur.execute("SELECT gold.ensure_event_partitions(%s, %s)", (y0, y1))
        conn.commit()
        print(f"[gold] dim_date y particiones cubren {y0}-{y1}")

        for nombre, (origen, sql) in DIMENSIONES.items():
            _ejecutar(conn, audit, nombre, origen, sql)
        _ejecutar(conn, audit, "dim_game", "silver.games", DIM_GAME)

        anios = range(y0, y1 + 1)
        _cargar_hechos(conn, audit, "fact_events", "silver.game_events", FACT_EVENTS, anios)
        _cargar_hechos(conn, audit, "fact_appearances", "silver.appearances", FACT_APPEARANCES, anios)
        _cargar_hechos(conn, audit, "fact_valuations", "silver.player_valuations", FACT_VALUATIONS, anios)
        return {"rango": (y0, y1)}
    finally:
        cur.close()
        conn.close()
        audit.close()
