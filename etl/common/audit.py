"""Auditoría y linaje (RF11): escribe en meta.etl_audit usando una conexión propia (autocommit)."""
from etl.common.db import get_connection


class Audit:
    def __init__(self, run_id: str, layer: str):
        self.run_id = run_id
        self.layer = layer
        self._conn = get_connection(autocommit=True)

    def start(self, table_name: str) -> int:
        with self._conn.cursor() as cur:
            cur.execute(
                "INSERT INTO meta.etl_audit (run_id, layer, table_name, status) "
                "VALUES (%s, %s, %s, 'RUNNING') RETURNING audit_id",
                (self.run_id, self.layer, table_name),
            )
            return cur.fetchone()[0]

    def finish(self, audit_id: int, read=0, transformed=0, discarded=0, inserted=0, status="OK"):
        with self._conn.cursor() as cur:
            cur.execute(
                "UPDATE meta.etl_audit SET rows_read=%s, rows_transformed=%s, rows_discarded=%s, "
                "rows_inserted=%s, status=%s, finished_at=now() WHERE audit_id=%s",
                (read, transformed, discarded, inserted, status, audit_id),
            )

    def close(self):
        self._conn.close()
