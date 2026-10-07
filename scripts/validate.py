"""Corre sql/validations, muestra volumetría y tiempos de consultas típicas de gold."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from etl.common import config  # noqa: E402
from etl.common.db import get_connection  # noqa: E402

CONSULTAS_GOLD = {
    "goleadores por temporada": "SELECT player_key, season, goles FROM gold.agg_player_season ORDER BY goles DESC LIMIT 20",
    "tabla de posiciones": "SELECT club_key, puntos FROM gold.agg_club_season WHERE season = (SELECT max(season) FROM gold.agg_club_season) ORDER BY puntos DESC LIMIT 20",
    "eventos por franja de 15 min": "SELECT minute_bucket, count(*) FROM gold.fact_events GROUP BY 1 ORDER BY 1",
    "tarjetas por árbitro": "SELECT referee_key, sum(tarjetas_por_90) FROM gold.agg_discipline_ref GROUP BY 1 ORDER BY 2 DESC NULLS LAST LIMIT 20",
    "local vs visitante": "SELECT * FROM gold.agg_home_away LIMIT 50",
    "eventos por competición (join)": "SELECT dc.name, count(*) FROM gold.fact_events fe JOIN gold.dim_competition dc USING (competition_key) GROUP BY 1 ORDER BY 2 DESC LIMIT 20",
}

TAMANOS = """
SELECT n.nspname || '.' || c.relname AS tabla, pg_relation_size(c.oid) AS datos,
       pg_indexes_size(c.oid) AS indices, pg_total_relation_size(c.oid) AS total
FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind IN ('r','p','m') AND n.nspname IN ('bronze','silver','gold','meta')
  AND NOT c.relispartition
ORDER BY total DESC
"""


def main() -> int:
    conn = get_connection(autocommit=True)
    cur = conn.cursor()
    sql = (config.SQL_DIR / "validations" / "99_validations.sql").read_text(encoding="utf-8")
    cur.execute(sql)
    fallos = 0
    print("== Validaciones ==")
    for nombre, n in cur.fetchall():
        ok = n == 0
        fallos += not ok
        print(f"{'PASA ' if ok else 'FALLA'}  {nombre}: {n}")

    print("\n== Volumetría ==")
    cur.execute(TAMANOS)
    for tabla, d, i, t in cur.fetchall():
        print(f"{tabla:40s} datos={d/1e6:10.1f} MB  índices={i/1e6:10.1f} MB  total={t/1e6:10.1f} MB")

    print("\n== Tiempos de consultas gold (objetivo < 3 s) ==")
    for nombre, q in CONSULTAS_GOLD.items():
        t0 = time.perf_counter()
        cur.execute(q)
        cur.fetchall()
        seg = time.perf_counter() - t0
        ok = seg < 3
        fallos += not ok
        print(f"{'PASA ' if ok else 'FALLA'}  {nombre}: {seg:.2f} s")
    conn.close()
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
