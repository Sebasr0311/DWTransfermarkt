"""Refresca las vistas materializadas de gold (RF10)."""
from etl.common.audit import Audit
from etl.common.db import get_connection

VISTAS = ["agg_player_season", "agg_club_season", "agg_events_15min", "agg_discipline_ref", "agg_home_away"]


def run(run_id: str, chunk_size: int | None = None) -> dict:
    audit = Audit(run_id, "gold")
    conn = get_connection(autocommit=True)  # REFRESH CONCURRENTLY no corre dentro de una transacción
    try:
        with conn.cursor() as cur:
            for v in VISTAS:
                audit_id = audit.start(v)
                cur.execute(f"REFRESH MATERIALIZED VIEW CONCURRENTLY gold.{v}")
                cur.execute(f"SELECT count(*) FROM gold.{v}")
                n = cur.fetchone()[0]
                audit.finish(audit_id, read=n, transformed=n, inserted=n)
                print(f"[gold] {v}: {n} filas")
    finally:
        conn.close()
        audit.close()
    return {}
