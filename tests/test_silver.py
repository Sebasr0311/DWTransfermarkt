"""Pruebas de la capa plata: huérfanos = 0, duplicados, rangos y cuadre contra la auditoría."""
import pytest

from etl.common.db import get_connection

FKS = [
    ("clubs", "domestic_competition_id", "competitions", "competition_id"),
    ("players", "current_club_id", "clubs", "club_id"),
    ("games", "competition_id", "competitions", "competition_id"),
    ("games", "home_club_id", "clubs", "club_id"),
    ("games", "away_club_id", "clubs", "club_id"),
    ("appearances", "game_id", "games", "game_id"),
    ("appearances", "player_id", "players", "player_id"),
    ("appearances", "player_club_id", "clubs", "club_id"),
    ("game_events", "game_id", "games", "game_id"),
    ("game_events", "club_id", "clubs", "club_id"),
    ("game_events", "player_id", "players", "player_id"),
    ("player_valuations", "player_id", "players", "player_id"),
]
LLAVES = {"appearances": "appearance_id", "game_events": "game_event_id", "players": "player_id",
          "clubs": "club_id", "games": "game_id", "competitions": "competition_id"}


@pytest.fixture(scope="module")
def cur():
    conn = get_connection(autocommit=True)
    yield conn.cursor()
    conn.close()


@pytest.mark.parametrize("hija,col,padre,pk", FKS)
def test_sin_huerfanos(cur, hija, col, padre, pk):
    cur.execute(f"SELECT count(*) FROM silver.{hija} c LEFT JOIN silver.{padre} p ON p.{pk} = c.{col} "
                f"WHERE c.{col} IS NOT NULL AND p.{pk} IS NULL")
    assert cur.fetchone()[0] == 0


@pytest.mark.parametrize("tabla,llave", LLAVES.items())
def test_sin_duplicados(cur, tabla, llave):
    cur.execute(f"SELECT count(*) FROM (SELECT {llave} FROM silver.{tabla} GROUP BY 1 HAVING count(*) > 1) x")
    assert cur.fetchone()[0] == 0


def test_rangos(cur):
    cur.execute('SELECT count(*) FROM silver.game_events WHERE "minute" < 0 OR "minute" > 130')
    assert cur.fetchone()[0] == 0
    cur.execute("SELECT count(*) FROM silver.appearances WHERE minutes_played NOT BETWEEN 0 AND 130 "
                "OR goals < 0 OR yellow_cards < 0 OR red_cards < 0")
    assert cur.fetchone()[0] == 0


def test_fechas_obligatorias(cur):
    for t, c in [("games", "game_date"), ("appearances", "game_date"), ("game_events", "game_date"),
                 ("player_valuations", "valuation_date")]:
        cur.execute(f"SELECT count(*) FROM silver.{t} WHERE {c} IS NULL")
        assert cur.fetchone()[0] == 0


@pytest.mark.parametrize("tabla", list(LLAVES) + ["player_valuations"])
def test_cuadre_con_auditoria(cur, tabla):
    """leídas = insertadas + descartadas (rechazadas + duplicadas) en la última corrida de silver."""
    cur.execute("SELECT rows_read, rows_discarded, rows_inserted FROM meta.etl_audit WHERE layer='silver' "
                "AND table_name=%s AND status='OK' ORDER BY audit_id DESC LIMIT 1", (tabla,))
    fila = cur.fetchone()
    if fila is None:
        pytest.skip("silver aún no se ha ejecutado")
    assert fila[0] == fila[1] + fila[2]
