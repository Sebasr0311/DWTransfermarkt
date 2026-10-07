"""Transformación bronze -> silver: tipado, reglas EDA E01-E09, deduplicación y FKs (SQL set-based)."""
import json

from etl.common.audit import Audit
from etl.common.db import get_connection

I, N, D = "meta.to_int", "meta.to_num", "meta.to_date"
XDATE = 'x."date"'


def blank(c):
    return f"NULLIF(btrim({c}),'')"


def txt(c):  # E03: nulos en textos -> 'Desconocido'
    return f"COALESCE({blank(c)},'Desconocido')"


def i32(e):
    return f"(CASE WHEN ({e}) BETWEEN -2147483648 AND 2147483647 THEN ({e})::int END)"


def i16(e):
    return f"(CASE WHEN ({e}) BETWEEN -32768 AND 32767 THEN ({e})::smallint END)"


def badnum(c, fn):  # E09: texto en columna numérica -> NULL controlado (se cuenta)
    return f"(CASE WHEN {blank(c)} IS NOT NULL AND {fn}({c}) IS NULL THEN 1 ELSE 0 END)"


def rejects(*conds):
    """conds: (condición SQL, regla, motivo). Devuelve las columnas _rule y _reason (primera que aplique)."""
    rule = "CASE " + " ".join(f"WHEN {c} THEN '{r}'" for c, r, _ in conds) + " END AS _rule"
    reason = "CASE " + " ".join(f"WHEN {c} THEN '{m}'" for c, _, m in conds) + " END AS _reason"
    return f"{rule}, {reason}"


def date_bad(raw, parsed):  # E04: fecha obligatoria nula o no interpretable
    return f"({parsed} IS NULL)", "E04", "Fecha ausente o no interpretable"


# --- definiciones por tabla: (stg_sql, columnas de silver, llave) ------------------------------

def competitions():
    sql = f"""
    SELECT b._row_id, {blank('b.competition_id')} AS competition_id, {txt('b."name"')} AS "name",
      {txt('b."type"')} AS "type", {txt('b.country_name')} AS country_name,
      {txt('b.confederation')} AS confederation, 0 AS _e09, 0 AS _fknull,
      {rejects((f"{blank('b.competition_id')} IS NULL OR length(btrim(b.competition_id)) > 10", 'E10', 'Llave de negocio nula o inválida'))}
    FROM bronze.competitions b"""
    return sql, ["competition_id", '"name"', '"type"', "country_name", "confederation"], "competition_id"


def clubs():
    sql = f"""
    WITH x AS (SELECT b.*, {I}(b.club_id) AS cid, {I}(b.squad_size) AS sq, {N}(b.average_age) AS age FROM bronze.clubs b)
    SELECT x._row_id, {i32('x.cid')} AS club_id, {txt('x."name"')} AS "name",
      p.competition_id AS domestic_competition_id, {txt('x.stadium_name')} AS stadium_name,
      {i16('CASE WHEN x.sq >= 0 THEN x.sq END')} AS squad_size,
      (CASE WHEN x.age BETWEEN 0 AND 99.9 THEN round(x.age,1) END)::numeric(4,1) AS average_age,
      {badnum('x.squad_size', I)} + {badnum('x.average_age', N)} AS _e09,
      (CASE WHEN {blank('x.domestic_competition_id')} IS NOT NULL AND p.competition_id IS NULL THEN 1 ELSE 0 END) AS _fknull,
      {rejects(("x.cid IS NULL OR x.cid NOT BETWEEN 0 AND 2147483647", 'E10', 'Llave de negocio nula o inválida'))}
    FROM x LEFT JOIN silver.competitions p ON p.competition_id = {blank('x.domestic_competition_id')}"""
    return sql, ["club_id", '"name"', "domestic_competition_id", "stadium_name", "squad_size", "average_age"], "club_id"


def players():
    sql = f"""
    WITH x AS (SELECT b.*, {I}(b.player_id) AS pid, {I}(b.current_club_id) AS cid, {D}(b.date_of_birth) AS dob,
                      {I}(b.height_in_cm) AS h, {N}(b.market_value_in_eur) AS mv FROM bronze.players b)
    SELECT x._row_id, {i32('x.pid')} AS player_id, {txt('x."name"')} AS "name", {txt('x."position"')} AS "position",
      {txt('x.sub_position')} AS sub_position, x.dob AS date_of_birth,
      {txt('x.country_of_citizenship')} AS country_of_citizenship, {txt('x.foot')} AS foot,
      {i16('CASE WHEN x.h BETWEEN 0 AND 260 THEN x.h END')} AS height_in_cm,
      c.club_id AS current_club_id,
      (CASE WHEN x.mv >= 0 AND x.mv < 1e12 THEN round(x.mv,2) END)::numeric(14,2) AS market_value_in_eur,
      {badnum('x.height_in_cm', I)} + {badnum('x.market_value_in_eur', N)} AS _e09,
      (CASE WHEN x.cid IS NOT NULL AND c.club_id IS NULL THEN 1 ELSE 0 END) AS _fknull,
      {rejects(("x.pid IS NULL OR x.pid NOT BETWEEN 0 AND 2147483647", 'E10', 'Llave de negocio nula o inválida'),
               (f"{blank('x.date_of_birth')} IS NOT NULL AND x.dob IS NULL", 'E04', 'Fecha de nacimiento no interpretable'))}
    FROM x LEFT JOIN silver.clubs c ON c.club_id = x.cid"""
    cols = ["player_id", '"name"', '"position"', "sub_position", "date_of_birth", "country_of_citizenship",
            "foot", "height_in_cm", "current_club_id", "market_value_in_eur"]
    return sql, cols, "player_id"


def games():
    sql = f"""
    WITH x AS (SELECT b.*, {I}(b.game_id) AS gid, {blank('b.competition_id')} AS comp, {I}(b.season) AS se,
                      {D}(b."date") AS gdate, {I}(b.home_club_id) AS hid, {I}(b.away_club_id) AS aid,
                      {I}(b.home_club_goals) AS hg, {I}(b.away_club_goals) AS ag, {I}(b.attendance) AS att
               FROM bronze.games b)
    SELECT x._row_id, {i32('x.gid')} AS game_id, c.competition_id AS competition_id, {i16('x.se')} AS season,
      {txt('x."round"')} AS "round", x.gdate AS game_date, h.club_id AS home_club_id, a.club_id AS away_club_id,
      COALESCE({i16('CASE WHEN x.hg >= 0 THEN x.hg END')}, 0) AS home_club_goals,
      COALESCE({i16('CASE WHEN x.ag >= 0 THEN x.ag END')}, 0) AS away_club_goals,
      {txt('x.stadium')} AS stadium, {i32('CASE WHEN x.att >= 0 THEN x.att END')} AS attendance,
      {txt('x.referee')} AS referee,
      {badnum('x.season', I)} + {badnum('x.attendance', I)} + {badnum('x.home_club_goals', I)} + {badnum('x.away_club_goals', I)} AS _e09,
      0 AS _fknull,
      {rejects(("x.gid IS NULL OR x.gid NOT BETWEEN 0 AND 2147483647", 'E10', 'Llave de negocio nula o inválida'),
               date_bad('x."date"', 'x.gdate'),
               ("x.se IS NULL OR x.se NOT BETWEEN 1900 AND 2100", 'E09', 'Temporada no numérica o fuera de rango'),
               ("c.competition_id IS NULL", 'E07', 'Competición inexistente (huérfano)'),
               ("h.club_id IS NULL", 'E07', 'Club local inexistente (huérfano)'),
               ("a.club_id IS NULL", 'E07', 'Club visitante inexistente (huérfano)'),
               ("x.hg < 0 OR x.ag < 0", 'E06', 'Goles negativos'))}
    FROM x LEFT JOIN silver.competitions c ON c.competition_id = x.comp
           LEFT JOIN silver.clubs h ON h.club_id = x.hid
           LEFT JOIN silver.clubs a ON a.club_id = x.aid"""
    cols = ["game_id", "competition_id", "season", '"round"', "game_date", "home_club_id", "away_club_id",
            "home_club_goals", "away_club_goals", "stadium", "attendance", "referee"]
    return sql, cols, "game_id"


def appearances():
    num = ["goals", "assists", "yellow_cards", "red_cards", "minutes_played"]
    sql = f"""
    WITH x AS (SELECT b.*, {blank('b.appearance_id')} AS apid, {I}(b.game_id) AS gid, {I}(b.player_id) AS pid,
                      {I}(b.player_club_id) AS cid, {D}(b."date") AS adate,
                      {I}(b.goals) AS g, {I}(b.assists) AS a, {I}(b.yellow_cards) AS y, {I}(b.red_cards) AS r,
                      {I}(b.minutes_played) AS m FROM bronze.appearances b)
    SELECT x._row_id, x.apid AS appearance_id, g.game_id AS game_id, p.player_id AS player_id,
      c.club_id AS player_club_id, COALESCE(x.adate, g.game_date) AS game_date,
      COALESCE({i16('x.g')}, 0) AS goals, COALESCE({i16('x.a')}, 0) AS assists,
      COALESCE({i16('x.y')}, 0) AS yellow_cards, COALESCE({i16('x.r')}, 0) AS red_cards,
      COALESCE({i16('x.m')}, 0) AS minutes_played,
      {' + '.join(badnum('x.' + c, I) for c in num)} AS _e09, 0 AS _fknull,
      {rejects(("x.apid IS NULL OR length(x.apid) > 40", 'E10', 'Llave de negocio nula o inválida'),
               (f"{blank(XDATE)} IS NOT NULL AND x.adate IS NULL", 'E04', 'Fecha no interpretable'),
               ("g.game_id IS NULL", 'E07', 'Partido inexistente (huérfano)'),
               ("p.player_id IS NULL", 'E07', 'Jugador inexistente (huérfano)'),
               ("c.club_id IS NULL", 'E07', 'Club inexistente (huérfano)'),
               ("x.g < 0 OR x.a < 0 OR x.y < 0 OR x.r < 0 OR x.m < 0 OR x.m > 130", 'E06', 'Valor negativo o minutos fuera de 0-130'))}
    FROM x LEFT JOIN silver.games g ON g.game_id = x.gid
           LEFT JOIN silver.players p ON p.player_id = x.pid
           LEFT JOIN silver.clubs c ON c.club_id = x.cid"""
    cols = ["appearance_id", "game_id", "player_id", "player_club_id", "game_date", "goals", "assists",
            "yellow_cards", "red_cards", "minutes_played"]
    return sql, cols, "appearance_id"


def game_events():
    sql = f"""
    WITH x AS (SELECT b.*, COALESCE({blank('b.game_event_id')},
                        md5(concat_ws('|', b.game_id, b."date", b."minute", b."type", b.club_id, b.player_id,
                                      b.description, b.player_in_id, b.player_assist_id))) AS eid,
                      {I}(b.game_id) AS gid, {D}(b."date") AS edate, {I}(b."minute") AS mi,
                      {I}(b.club_id) AS cid, {I}(b.player_id) AS pid,
                      {I}(b.player_in_id) AS pin, {I}(b.player_assist_id) AS pas FROM bronze.game_events b)
    SELECT x._row_id, x.eid AS game_event_id, g.game_id AS game_id, COALESCE(x.edate, g.game_date) AS game_date,
      {i16('CASE WHEN x.mi BETWEEN 0 AND 130 THEN x.mi END')} AS "minute", {txt('x."type"')} AS "type",
      c.club_id AS club_id, p.player_id AS player_id, {blank('x.description')} AS description,
      {i32('x.pin')} AS player_in_id, {i32('x.pas')} AS player_assist_id,
      {badnum('x."minute"', I)} + {badnum('x.player_in_id', I)} + {badnum('x.player_assist_id', I)} AS _e09,
      (CASE WHEN x.pid IS NOT NULL AND p.player_id IS NULL THEN 1 ELSE 0 END) AS _fknull,
      {rejects(("length(x.eid) > 64", 'E10', 'Llave de negocio inválida'),
               (f"{blank(XDATE)} IS NOT NULL AND x.edate IS NULL", 'E04', 'Fecha no interpretable'),
               ("g.game_id IS NULL", 'E07', 'Partido inexistente (huérfano)'),
               ("c.club_id IS NULL", 'E07', 'Club inexistente (huérfano)'),
               ("x.mi < 0 OR x.mi > 130", 'E06', 'Minuto fuera de 0-130'))}
    FROM x LEFT JOIN silver.games g ON g.game_id = x.gid
           LEFT JOIN silver.clubs c ON c.club_id = x.cid
           LEFT JOIN silver.players p ON p.player_id = x.pid"""
    cols = ["game_event_id", "game_id", "game_date", '"minute"', '"type"', "club_id", "player_id",
            "description", "player_in_id", "player_assist_id"]
    return sql, cols, "game_event_id"


def player_valuations():
    sql = f"""
    WITH x AS (SELECT b.*, {I}(b.player_id) AS pid, {D}(b."date") AS vdate, {N}(b.market_value_in_eur) AS mv,
                      {I}(b.current_club_id) AS cid FROM bronze.player_valuations b)
    SELECT x._row_id, p.player_id AS player_id, x.vdate AS valuation_date,
      (CASE WHEN x.mv >= 0 AND x.mv < 1e12 THEN round(x.mv,2) END)::numeric(14,2) AS market_value_in_eur,
      {i32('x.cid')} AS current_club_id,
      {badnum('x.market_value_in_eur', N)} + {badnum('x.current_club_id', I)} AS _e09, 0 AS _fknull,
      {rejects(date_bad('x."date"', 'x.vdate'),
               ("p.player_id IS NULL", 'E07', 'Jugador inexistente (huérfano)'))}
    FROM x LEFT JOIN silver.players p ON p.player_id = x.pid"""
    cols = ["player_id", "valuation_date", "market_value_in_eur", "current_club_id"]
    return sql, cols, "player_id, valuation_date"


TABLAS = {
    "competitions": competitions, "clubs": clubs, "players": players, "games": games,
    "appearances": appearances, "game_events": game_events, "player_valuations": player_valuations,
}


def _resumen_rejected(cur, run_id, table, rule, reason, n):
    if n:
        cur.execute(
            "INSERT INTO meta.etl_rejected (run_id, table_name, rule_id, reason, raw_record) VALUES (%s,%s,%s,%s,%s)",
            (run_id, table, rule, reason, json.dumps({"filas_afectadas": int(n)})))


def procesar(conn, audit: Audit, run_id: str, table: str):
    stg_sql, cols, key = TABLAS[table]()
    audit_id = audit.start(table)
    cur = conn.cursor()
    try:
        cur.execute("DROP TABLE IF EXISTS stg")
        cur.execute(f"CREATE TEMP TABLE stg AS {stg_sql}")
        cur.execute("SELECT count(*), count(*) FILTER (WHERE _reason IS NULL), "
                    "COALESCE(sum(_e09),0), COALESCE(sum(_fknull),0) FROM stg")
        leidas, validas, e09, fknull = cur.fetchone()
        rechazadas = leidas - validas

        # Rechazados (E04, E06, E07, E10) -> meta.etl_rejected
        cur.execute(
            "INSERT INTO meta.etl_rejected (run_id, table_name, rule_id, reason, raw_record) "
            "SELECT %s, %s, _rule, _reason, to_jsonb(s) - ARRAY['_row_id','_rule','_reason','_e09','_fknull'] "
            "FROM stg s WHERE _reason IS NOT NULL", (run_id, table))

        # Carga idempotente: deduplicación (E05) + upsert
        colnames = [c.strip('"') for c in cols]
        keycols = [k.strip() for k in key.split(",")]
        sets = ", ".join(f'"{c}" = EXCLUDED."{c}"' for c in colnames if c not in keycols)
        collist = ", ".join(cols)
        cur.execute(
            f"INSERT INTO silver.{table} ({collist}) "
            f"SELECT DISTINCT ON ({key}) {collist} FROM stg WHERE _reason IS NULL ORDER BY {key}, _row_id DESC "
            f"ON CONFLICT ({key}) DO UPDATE SET {sets}")
        insertadas = cur.rowcount
        duplicadas = validas - insertadas
        _resumen_rejected(cur, run_id, table, "E05", "Duplicados por llave de negocio (se conserva uno)", duplicadas)
        _resumen_rejected(cur, run_id, table, "E09", "Celdas no numéricas convertidas a NULL", e09)
        _resumen_rejected(cur, run_id, table, "E07", "FK opcional sin padre: se anuló, fila conservada", fknull)
        conn.commit()
        audit.finish(audit_id, read=leidas, transformed=validas, discarded=rechazadas + duplicadas, inserted=insertadas)
        print(f"[silver] {table}: leídas={leidas} rechazadas={rechazadas} duplicadas={duplicadas} "
              f"insertadas={insertadas} E09={e09} FK_anuladas={fknull}")
        return insertadas
    except Exception:
        conn.rollback()
        audit.finish(audit_id, status="ERROR")
        raise
    finally:
        cur.close()


def run(run_id: str, chunk_size: int | None = None) -> dict:
    audit = Audit(run_id, "silver")
    conn = get_connection()
    resumen = {}
    try:
        for table in TABLAS:
            with conn.cursor() as cur:
                cur.execute(f"SELECT count(*) FROM bronze.{table}")
                if cur.fetchone()[0] == 0:
                    print(f"[silver] bronze.{table} vacío -> se omite")
                    resumen[table] = "BRONCE_VACIO"
                    continue
            resumen[table] = procesar(conn, audit, run_id, table)
    finally:
        conn.close()
        audit.close()
    return resumen
