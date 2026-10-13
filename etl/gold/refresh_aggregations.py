"""Refresca las vistas materializadas de gold de forma concurrente (RF10)."""
from etl.common.audit import Audit
from etl.common.db import get_connection

VISTAS = [
    "agg_jugador_temporada_liga",
    "agg_club_temporada",
    "agg_eventos_15min",
    "agg_disciplina_arbitro",
    "agg_local_visitante",
]


def run(run_id: str, chunk_size: int | None = None) -> dict:
    audit = Audit(run_id, "gold")
    conn = get_connection(autocommit=True)  # REFRESH CONCURRENTLY requiere correr fuera de transacción
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
