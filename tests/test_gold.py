"""Pruebas de la capa oro: integridad de hechos/dimensiones e idempotencia."""
import uuid

import pytest

from etl.common.db import get_connection
from etl.gold import load_gold, refresh_aggregations
from etl.silver import transform_silver

TABLAS_GOLD = ["dim_date", "dim_competition", "dim_club", "dim_player", "dim_referee", "dim_event_type",
               "dim_game", "fact_events", "fact_appearances", "fact_valuations"]


@pytest.fixture(scope="module")
def cur():
    conn = get_connection(autocommit=True)
    yield conn.cursor()
    conn.close()


def _conteos(cur):
    out = {}
    for t in TABLAS_GOLD:
        cur.execute(f"SELECT count(*) FROM gold.{t}")
        out[t] = cur.fetchone()[0]
    return out


def test_hechos_sin_huerfanos(cur):
    consultas = [
        "SELECT count(*) FROM gold.fact_events f LEFT JOIN gold.dim_game d USING (game_key) WHERE d.game_id IS NULL",
        "SELECT count(*) FROM gold.fact_events f LEFT JOIN gold.dim_club d USING (club_key) WHERE d.club_id IS NULL",
        "SELECT count(*) FROM gold.fact_appearances f LEFT JOIN gold.dim_player d USING (player_key) WHERE d.player_id IS NULL",
        "SELECT count(*) FROM gold.fact_valuations f LEFT JOIN gold.dim_player d USING (player_key) WHERE d.player_id IS NULL",
    ]
    for q in consultas:
        cur.execute(q)
        assert cur.fetchone()[0] == 0


def test_minute_bucket_en_rango(cur):
    cur.execute("SELECT count(*) FROM gold.fact_events WHERE minute_bucket NOT BETWEEN 0 AND 6")
    assert cur.fetchone()[0] == 0


def test_sin_filas_en_particion_default(cur):
    cur.execute("SELECT count(*) FROM gold.fact_events_default")
    assert cur.fetchone()[0] == 0


def test_idempotencia_silver_y_gold(cur):
    """Reejecutar silver + gold no cambia los conteos (el bronce no se vuelve a cargar)."""
    cur.execute("SELECT count(*) FROM silver.games")
    if cur.fetchone()[0] == 0:
        pytest.skip("sin datos cargados")
    antes = _conteos(cur)
    run_id = str(uuid.uuid4())
    transform_silver.run(run_id)
    load_gold.run(run_id)
    refresh_aggregations.run(run_id)
    assert _conteos(cur) == antes
