"""Pruebas de la capa bronce: conteos y auditoría de carga."""
import pytest

from etl.common.db import get_connection

TABLAS = ["competitions", "clubs", "players", "games", "player_valuations", "appearances", "game_events"]


@pytest.fixture(scope="module")
def cur():
    conn = get_connection(autocommit=True)
    yield conn.cursor()
    conn.close()


def test_tablas_bronze_existen(cur):
    cur.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema='bronze'")
    assert cur.fetchone()[0] == len(TABLAS)


@pytest.mark.parametrize("tabla", TABLAS)
def test_conteo_coincide_con_auditoria(cur, tabla):
    cur.execute(f"SELECT count(*) FROM bronze.{tabla}")
    n = cur.fetchone()[0]
    if n == 0:
        pytest.skip(f"bronze.{tabla} sin datos (faltan CSV en data/raw)")
    cur.execute("SELECT rows_inserted FROM meta.etl_audit WHERE layer='bronze' AND table_name=%s "
                "AND status='OK' ORDER BY audit_id DESC LIMIT 1", (tabla,))
    assert cur.fetchone()[0] == n
