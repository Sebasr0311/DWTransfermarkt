"""Carga silver -> gold: dimensiones conformadas y constelación de hechos con llaves sustitutas. Idempotente."""
from etl.common.audit import Audit
from etl.common.db import get_connection

MESES = "ARRAY['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']"

DIMENSIONES = {
    "dim_competicion": ("silver.competitions", """
        INSERT INTO gold.dim_competicion (competicion_id, "nombre", "tipo", pais, confederacion)
        SELECT competition_id, "name", "type", country_name, confederation FROM silver.competitions
        ON CONFLICT (competicion_id) DO UPDATE SET "nombre"=EXCLUDED."nombre", "tipo"=EXCLUDED."tipo",
          pais=EXCLUDED.pais, confederacion=EXCLUDED.confederacion"""),
    "dim_club": ("silver.clubs", """
        INSERT INTO gold.dim_club (club_id, "nombre", competicion_key, estadio, tamanio_plantilla, edad_promedio)
        SELECT c.club_id, c."name", dc.competicion_key, c.stadium_name, c.squad_size, c.average_age
        FROM silver.clubs c
        LEFT JOIN gold.dim_competicion dc ON dc.competicion_id = c.domestic_competition_id
        ON CONFLICT (club_id) DO UPDATE SET "nombre"=EXCLUDED."nombre",
          competicion_key=EXCLUDED.competicion_key, estadio=EXCLUDED.estadio,
          tamanio_plantilla=EXCLUDED.tamanio_plantilla, edad_promedio=EXCLUDED.edad_promedio"""),
    "dim_jugador": ("silver.players", """
        INSERT INTO gold.dim_jugador (jugador_id, "nombre", "posicion", sub_posicion, fecha_nacimiento,
                                     pais_ciudadania, pie, altura_cm)
        SELECT player_id, "name", "position", sub_position, date_of_birth, country_of_citizenship, foot, height_in_cm
        FROM silver.players
        ON CONFLICT (jugador_id) DO UPDATE SET "nombre"=EXCLUDED."nombre", "posicion"=EXCLUDED."posicion",
          sub_posicion=EXCLUDED.sub_posicion, fecha_nacimiento=EXCLUDED.fecha_nacimiento,
          pais_ciudadania=EXCLUDED.pais_ciudadania, pie=EXCLUDED.pie,
          altura_cm=EXCLUDED.altura_cm"""),
    "dim_arbitro": ("silver.games", """
        INSERT INTO gold.dim_arbitro (nombre_arbitro) SELECT DISTINCT referee FROM silver.games
        ON CONFLICT (nombre_arbitro) DO NOTHING"""),
    "dim_tipo_evento": ("silver.game_events", """
        INSERT INTO gold.dim_tipo_evento (nombre_tipo_evento) SELECT DISTINCT "type" FROM silver.game_events
        ON CONFLICT (nombre_tipo_evento) DO NOTHING"""),
}

DIM_PARTIDO = """
INSERT INTO gold.dim_partido (partido_id, competicion_key, arbitro_key, club_local_key, club_visitante_key, fecha_key,
                             temporada, "jornada", fecha_partido, goles_local, goles_visitante, estadio, asistencia, es_sintetico)
SELECT g.game_id, dc.competicion_key, dr.arbitro_key, dh.club_key, da.club_key,
       to_char(g.game_date, 'YYYYMMDD')::int, g.season, g."round", g.game_date,
       g.home_club_goals, g.away_club_goals, g.stadium, g.attendance,
       (g.origin = 'sintetico')
FROM silver.games g
JOIN gold.dim_competicion dc ON dc.competicion_id = g.competition_id
JOIN gold.dim_arbitro dr ON dr.nombre_arbitro = g.referee
JOIN gold.dim_club dh ON dh.club_id = g.home_club_id
JOIN gold.dim_club da ON da.club_id = g.away_club_id
ON CONFLICT (partido_id) DO UPDATE SET competicion_key=EXCLUDED.competicion_key, arbitro_key=EXCLUDED.arbitro_key,
  club_local_key=EXCLUDED.club_local_key, club_visitante_key=EXCLUDED.club_visitante_key, fecha_key=EXCLUDED.fecha_key,
  temporada=EXCLUDED.temporada, "jornada"=EXCLUDED."jornada", fecha_partido=EXCLUDED.fecha_partido,
  goles_local=EXCLUDED.goles_local, goles_visitante=EXCLUDED.goles_visitante,
  estadio=EXCLUDED.estadio, asistencia=EXCLUDED.asistencia, es_sintetico=EXCLUDED.es_sintetico"""

# Hechos: se cargan por año (rango de fechas) para acotar el tamaño de cada transacción.
HECHO_EVENTOS = """
INSERT INTO gold.hecho_eventos_partido (evento_partido_id, fecha_key, partido_key, competicion_key, club_key, jugador_key,
                                       jugador_asistencia_key, arbitro_key, tipo_evento_key, "minuto", franja_15min, es_local, es_sintetico)
SELECT e.game_event_id, to_char(e.game_date, 'YYYYMMDD')::int, dp.partido_key, dp.competicion_key, dc.club_key,
       dj.jugador_key, da.jugador_key, dp.arbitro_key, et.tipo_evento_key, e."minute",
       CASE WHEN e."minute" IS NULL THEN NULL ELSE LEAST(e."minute" / 15, 6) END,
       (dc.club_key = dp.club_local_key),
       (e.origin = 'sintetico')
FROM silver.game_events e
JOIN gold.dim_partido dp ON dp.partido_id = e.game_id
JOIN gold.dim_club dc ON dc.club_id = e.club_id
JOIN gold.dim_tipo_evento et ON et.nombre_tipo_evento = e."type"
LEFT JOIN gold.dim_jugador dj ON dj.jugador_id = e.player_id
LEFT JOIN gold.dim_jugador da ON da.jugador_id = e.player_assist_id
WHERE e.game_date >= %(d0)s AND e.game_date < %(d1)s
ON CONFLICT (evento_partido_id, fecha_key) DO UPDATE SET partido_key=EXCLUDED.partido_key,
  competicion_key=EXCLUDED.competicion_key, club_key=EXCLUDED.club_key, jugador_key=EXCLUDED.jugador_key,
  jugador_asistencia_key=EXCLUDED.jugador_asistencia_key, arbitro_key=EXCLUDED.arbitro_key,
  tipo_evento_key=EXCLUDED.tipo_evento_key, "minuto"=EXCLUDED."minuto",
  franja_15min=EXCLUDED.franja_15min, es_local=EXCLUDED.es_local, es_sintetico=EXCLUDED.es_sintetico
WHERE (gold.hecho_eventos_partido.partido_key, gold.hecho_eventos_partido.club_key, gold.hecho_eventos_partido.jugador_key,
       gold.hecho_eventos_partido.jugador_asistencia_key, gold.hecho_eventos_partido.tipo_evento_key, gold.hecho_eventos_partido."minuto",
       gold.hecho_eventos_partido.es_local, gold.hecho_eventos_partido.es_sintetico)
  IS DISTINCT FROM (EXCLUDED.partido_key, EXCLUDED.club_key, EXCLUDED.jugador_key, EXCLUDED.jugador_asistencia_key,
                    EXCLUDED.tipo_evento_key, EXCLUDED."minuto", EXCLUDED.es_local, EXCLUDED.es_sintetico)"""

HECHO_RENDIMIENTO = """
INSERT INTO gold.hecho_rendimiento_jugador (aparicion_id, fecha_key, partido_key, jugador_key, club_key, competicion_key,
                                           goles, asistencias, tarjetas_amarillas, tarjetas_rojas, minutos_jugados, es_sintetico)
SELECT a.appearance_id, to_char(a.game_date, 'YYYYMMDD')::int, dp.partido_key, dj.jugador_key, dc.club_key,
       dp.competicion_key, a.goals, a.assists, a.yellow_cards, a.red_cards, a.minutes_played,
       (a.origin = 'sintetico')
FROM silver.appearances a
JOIN gold.dim_partido dp ON dp.partido_id = a.game_id
JOIN gold.dim_jugador dj ON dj.jugador_id = a.player_id
JOIN gold.dim_club dc ON dc.club_id = a.player_club_id
WHERE a.game_date >= %(d0)s AND a.game_date < %(d1)s
ON CONFLICT (aparicion_id) DO UPDATE SET fecha_key=EXCLUDED.fecha_key, partido_key=EXCLUDED.partido_key,
  jugador_key=EXCLUDED.jugador_key, club_key=EXCLUDED.club_key, competicion_key=EXCLUDED.competicion_key,
  goles=EXCLUDED.goles, asistencias=EXCLUDED.asistencias, tarjetas_amarillas=EXCLUDED.tarjetas_amarillas,
  tarjetas_rojas=EXCLUDED.tarjetas_rojas, minutos_jugados=EXCLUDED.minutos_jugados, es_sintetico=EXCLUDED.es_sintetico
WHERE (gold.hecho_rendimiento_jugador.fecha_key, gold.hecho_rendimiento_jugador.partido_key, gold.hecho_rendimiento_jugador.jugador_key,
       gold.hecho_rendimiento_jugador.club_key, gold.hecho_rendimiento_jugador.goles, gold.hecho_rendimiento_jugador.asistencias,
       gold.hecho_rendimiento_jugador.tarjetas_amarillas, gold.hecho_rendimiento_jugador.tarjetas_rojas, gold.hecho_rendimiento_jugador.minutos_jugados,
       gold.hecho_rendimiento_jugador.es_sintetico)
  IS DISTINCT FROM (EXCLUDED.fecha_key, EXCLUDED.partido_key, EXCLUDED.jugador_key, EXCLUDED.club_key,
                    EXCLUDED.goles, EXCLUDED.asistencias, EXCLUDED.tarjetas_amarillas, EXCLUDED.tarjetas_rojas,
                    EXCLUDED.minutos_jugados, EXCLUDED.es_sintetico)"""

HECHO_VALORACIONES = """
INSERT INTO gold.hecho_valoraciones_mercado (fecha_key, jugador_key, club_key, valor_mercado_eur, es_sintetico)
SELECT to_char(v.valuation_date, 'YYYYMMDD')::int, dj.jugador_key, dc.club_key, v.market_value_in_eur,
       (v.origin = 'sintetico')
FROM silver.player_valuations v
JOIN gold.dim_jugador dj ON dj.jugador_id = v.player_id
LEFT JOIN gold.dim_club dc ON dc.club_id = v.current_club_id
WHERE v.valuation_date >= %(d0)s AND v.valuation_date < %(d1)s
ON CONFLICT (jugador_key, fecha_key) DO UPDATE SET club_key=EXCLUDED.club_key,
  valor_mercado_eur=EXCLUDED.valor_mercado_eur, es_sintetico=EXCLUDED.es_sintetico
WHERE (gold.hecho_valoraciones_mercado.club_key, gold.hecho_valoraciones_mercado.valor_mercado_eur, gold.hecho_valoraciones_mercado.es_sintetico)
  IS DISTINCT FROM (EXCLUDED.club_key, EXCLUDED.valor_mercado_eur, EXCLUDED.es_sintetico)"""


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

        # dim_fecha: todas las fechas del rango (años completos) y particiones de hecho_eventos_partido
        cur.execute(f"""
            INSERT INTO gold.dim_fecha (fecha_key, fecha_completa, anio, trimestre, mes, nombre_mes, semana, temporada)
            SELECT to_char(d, 'YYYYMMDD')::int, d::date, extract(year FROM d), extract(quarter FROM d),
                   extract(month FROM d), ({MESES})[extract(month FROM d)::int], extract(week FROM d),
                   CASE WHEN extract(month FROM d) >= 7 THEN extract(year FROM d) ELSE extract(year FROM d) - 1 END
            FROM generate_series(make_date(%s,1,1), make_date(%s,12,31), interval '1 day') d
            ON CONFLICT (fecha_key) DO NOTHING""", (y0, y1))
        cur.execute("SELECT gold.asegurar_particiones_eventos(%s, %s)", (y0, y1))
        conn.commit()
        print(f"[gold] dim_fecha y particiones cubren {y0}-{y1}")

        for nombre, (origen, sql) in DIMENSIONES.items():
            _ejecutar(conn, audit, nombre, origen, sql)
        _ejecutar(conn, audit, "dim_partido", "silver.games", DIM_PARTIDO)

        anios = range(y0, y1 + 1)
        _cargar_hechos(conn, audit, "hecho_eventos_partido", "silver.game_events", HECHO_EVENTOS, anios)
        _cargar_hechos(conn, audit, "hecho_rendimiento_jugador", "silver.appearances", HECHO_RENDIMIENTO, anios)
        _cargar_hechos(conn, audit, "hecho_valoraciones_mercado", "silver.player_valuations", HECHO_VALORACIONES, anios)
        return {"rango": (y0, y1)}
    finally:
        cur.close()
        conn.close()
        audit.close()
