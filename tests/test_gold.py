"""Pruebas de la capa oro: integridad de la constelación de hechos/dimensiones e idempotencia."""
import uuid

import pytest

from etl.common.db import get_connection
from etl.gold import load_gold, refresh_aggregations
from etl.silver import transform_silver

TABLAS_GOLD = [
    "dim_fecha",
    "dim_competicion",
    "dim_club",
    "dim_jugador",
    "dim_arbitro",
    "dim_tipo_evento",
    "dim_partido",
    "hecho_eventos_partido",
    "hecho_rendimiento_jugador",
    "hecho_valoraciones_mercado",
]


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
        "SELECT count(*) FROM gold.hecho_eventos_partido f LEFT JOIN gold.dim_partido d USING (partido_key) WHERE d.partido_id IS NULL",
        "SELECT count(*) FROM gold.hecho_eventos_partido f LEFT JOIN gold.dim_club d USING (club_key) WHERE d.club_id IS NULL",
        "SELECT count(*) FROM gold.hecho_rendimiento_jugador f LEFT JOIN gold.dim_jugador d USING (jugador_key) WHERE d.jugador_id IS NULL",
        "SELECT count(*) FROM gold.hecho_valoraciones_mercado f LEFT JOIN gold.dim_jugador d USING (jugador_key) WHERE d.jugador_id IS NULL",
    ]
    for q in consultas:
        cur.execute(q)
        assert cur.fetchone()[0] == 0


def test_franja_15min_en_rango(cur):
    cur.execute("SELECT count(*) FROM gold.hecho_eventos_partido WHERE franja_15min NOT BETWEEN 0 AND 6")
    assert cur.fetchone()[0] == 0


def test_sin_filas_en_particion_default(cur):
    cur.execute("SELECT count(*) FROM gold.hecho_eventos_partido_default")
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
