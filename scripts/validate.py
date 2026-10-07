"""Valida integridad, volumen, checksums de datos reales, agregaciones y rendimiento."""
import sys
import time
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from etl.common import config  # noqa: E402
from etl.common.db import get_connection  # noqa: E402

# Checksums esperados para datos reales (establecidos antes de la expansión)
BASELINE_CHECKSUMS = {
    "competitions": (65, -7132307758,
                     "competition_id, name, type, country_name, confederation"),
    "clubs": (796, -46340764361,
              "club_id, name, domestic_competition_id, stadium_name, squad_size, average_age"),
    "players": (50149, 15712675432,
                "player_id, name, position, sub_position, date_of_birth, country_of_citizenship, foot, height_in_cm, current_club_id, market_value_in_eur"),
    "games": (72602, 776084486429,
              "game_id, competition_id, season, round, game_date, home_club_id, away_club_id, home_club_goals, away_club_goals, stadium, attendance, referee"),
    "appearances": (1813294, -2786230826709,
                    "appearance_id, game_id, player_id, player_club_id, game_date, goals, assists, yellow_cards, red_cards, minutes_played"),
    "game_events": (1032318, 1422080252746,
                    "game_event_id, game_id, game_date, minute, type, club_id, player_id, description, player_in_id, player_assist_id"),
    "player_valuations": (656301, 425532711250,
                          "player_id, valuation_date, market_value_in_eur, current_club_id"),
}

BASELINE_AGGREGATIONS = {
    "agg_player_season": (
        "SELECT count(*), sum(partidos), sum(goles), sum(asistencias), sum(minutos) FROM gold.agg_player_season",
        (93595, Decimal("1813294"), Decimal("168551"), Decimal("133214"), Decimal("124172145")),
    ),
    "agg_club_season": (
        "SELECT count(*), sum(partidos), sum(goles_favor), sum(goles_contra), sum(puntos), sum(valor_plantilla) FROM gold.agg_club_season",
        (5321, Decimal("145204"), Decimal("202819"), Decimal("202819"), Decimal("200373"), Decimal("448668243000.00")),
    ),
    "agg_events_15min": (
        "SELECT count(*), sum(eventos) FROM gold.agg_events_15min",
        (313, Decimal("1032318")),
    ),
    "agg_discipline_ref": (
        "SELECT count(*), sum(partidos), sum(amarillas), sum(rojas), sum(minutos) FROM gold.agg_discipline_ref",
        (5353, Decimal("64761"), Decimal("264922"), Decimal("6368"), Decimal("124172145")),
    ),
    "agg_home_away": (
        "SELECT count(*), sum(partidos), sum(victorias_local), sum(empates), sum(victorias_visitante) FROM gold.agg_home_away",
        (575, Decimal("72602"), Decimal("32692"), Decimal("17433"), Decimal("22477")),
    ),
}

CONSULTAS_GOLD = {
    "goleadores por temporada": "SELECT player_key, season, goles FROM gold.agg_player_season ORDER BY goles DESC LIMIT 20",
    "tabla de posiciones": "SELECT club_key, puntos FROM gold.agg_club_season WHERE season = (SELECT max(season) FROM gold.agg_club_season) ORDER BY puntos DESC LIMIT 20",
    "eventos por franja de 15 min": "SELECT minute_bucket, count(*) FROM gold.fact_events GROUP BY 1 ORDER BY 1",
    "tarjetas por árbitro": "SELECT referee_key, sum(tarjetas_por_90) FROM gold.agg_discipline_ref GROUP BY 1 ORDER BY 2 DESC NULLS LAST LIMIT 20",
    "local vs visitante": "SELECT * FROM gold.agg_home_away LIMIT 50",
    "eventos por competición (join)": "SELECT dc.name, count(*) FROM gold.fact_events fe JOIN gold.dim_competition dc USING (competition_key) GROUP BY 1 ORDER BY 2 DESC LIMIT 20",
}

TAMANOS = """
SELECT n.nspname || '.' || c.relname AS tabla,
       COALESCE(c.reltuples::bigint, 0) AS registros,
       CASE WHEN c.relkind = 'p' THEN (
         SELECT COALESCE(sum(pg_relation_size(inhrelid))::bigint, 0) FROM pg_inherits WHERE inhparent = c.oid
       ) ELSE pg_relation_size(c.oid) END AS datos,
       CASE WHEN c.relkind = 'p' THEN (
         SELECT COALESCE(sum(pg_indexes_size(inhrelid))::bigint, 0) FROM pg_inherits WHERE inhparent = c.oid
       ) ELSE pg_indexes_size(c.oid) END AS indices,
       CASE WHEN c.relkind = 'p' THEN (
         SELECT COALESCE(sum(pg_total_relation_size(inhrelid))::bigint, 0) FROM pg_inherits WHERE inhparent = c.oid
       ) ELSE pg_total_relation_size(c.oid) END AS total
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind IN ('r','p','m') AND n.nspname IN ('bronze','silver','gold','meta')
  AND NOT c.relispartition
ORDER BY total DESC;
"""


def main() -> int:
    conn = get_connection(autocommit=True)
    cur = conn.cursor()
    fallos = 0

    print("================================================================================")
    print("                    INFORME DE VALIDACIÓN DWH TRANSFERMARKT                     ")
    print("================================================================================\n")

    # 1. Desglose de filas por tabla en silver (real vs sintético)
    print("== 1. Conteo de filas en silver (Real vs Sintético) ==")
    tablas_silver = [
        ("competitions", False),
        ("clubs", False),
        ("players", False),
        ("games", True),
        ("appearances", True),
        ("game_events", True),
        ("player_valuations", True),
    ]

    tot_real = 0
    tot_syn = 0
    tot_general = 0
    filas_reporte = []

    for tabla, tiene_origen in tablas_silver:
        if tiene_origen:
            cur.execute(f"SELECT count(*) FILTER (WHERE origin = 'real'), count(*) FILTER (WHERE origin = 'sintetico') FROM silver.{tabla}")
            r, s = cur.fetchone()
        else:
            cur.execute(f"SELECT count(*) FROM silver.{tabla}")
            r = cur.fetchone()[0]
            s = 0
        t = r + s
        tot_real += r
        tot_syn += s
        tot_general += t
        filas_reporte.append((f"silver.{tabla}", r, s, t))

    print(f"{'Tabla':<28} | {'Real':>12} | {'Sintético':>12} | {'Total':>12}")
    print("-" * 72)
    for nombre, r, s, t in filas_reporte:
        print(f"{nombre:<28} | {r:>12,d} | {s:>12,d} | {t:>12,d}")
    print("-" * 72)
    print(f"{'TOTAL SILVER':<28} | {tot_real:>12,d} | {tot_syn:>12,d} | {tot_general:>12,d}")

    meta_target = 10565088
    ok_target = tot_general >= meta_target
    print(f"Meta objetivo propuesta      : {meta_target:,} filas")
    print(f"Estado de la meta            : {'PASA' if ok_target else 'FALLA'} ({tot_general:,} >= {meta_target:,})\n")
    if not ok_target:
        fallos += 1

    # 2. Checksums de integridad de datos reales
    print("== 2. Integridad de filas reales (Checksums y Conteos) ==")
    for tabla, (exp_cnt, exp_chk, cols) in BASELINE_CHECKSUMS.items():
        filtro = "WHERE origin = 'real'" if tabla in ["games", "appearances", "game_events", "player_valuations"] else ""
        cur.execute(f"SELECT count(*), sum(hashtext(ROW({cols})::text)::bigint) FROM silver.{tabla} {filtro}")
        cnt, chk = cur.fetchone()
        ok_c = (cnt == exp_cnt)
        ok_h = (chk == exp_chk)
        ok = ok_c and ok_h
        if not ok:
            fallos += 1
        estado = "PASA " if ok else "FALLA"
        print(f"{estado}  silver.{tabla:<18} count={cnt:>9,d} (exp {exp_cnt:>9,d}) | chk={chk} (exp {exp_chk})")

    # 3. Integridad de Vistas Materializadas de Agregación (gold.agg_*)
    print("\n== 3. Integridad de Vistas Agregadas (is_synthetic = FALSE) ==")
    for vista, (query, exp_tuple) in BASELINE_AGGREGATIONS.items():
        cur.execute(query)
        actual = cur.fetchone()
        ok = (actual == exp_tuple)
        if not ok:
            fallos += 1
        estado = "PASA " if ok else "FALLA"
        print(f"{estado}  gold.{vista:<18} valores coincidentes con línea base real: {ok}")

    # 4. Validaciones de integridad referencial, duplicados y reglas de negocio
    print("\n== 4. Validaciones de Esquema y Reglas de Negocio (99_validations.sql) ==")
    sql = (config.SQL_DIR / "validations" / "99_validations.sql").read_text(encoding="utf-8")
    cur.execute(sql)
    val_fallos = 0
    for nombre, n in cur.fetchall():
        ok = n == 0
        if not ok:
            fallos += 1
            val_fallos += 1
        print(f"{'PASA ' if ok else 'FALLA'}  {nombre}: {n}")
    print(f"Total fallos en 99_validations: {val_fallos}")

    # 5. Volumetría física
    print("\n== 5. Volumetría Física en Disco (PostgreSQL) ==")
    cur.execute(TAMANOS)
    print(f"{'Tabla / Vista':<32} | {'Registros':>12} | {'Datos (MB)':>12} | {'Índices (MB)':>12} | {'Total (MB)':>12}")
    print("-" * 90)
    for tabla, reg, d, i, t in cur.fetchall():
        print(f"{tabla:<32} | {reg:>12,d} | {d / 1e6:>12.2f} | {i / 1e6:>12.2f} | {t / 1e6:>12.2f}")

    # 6. Tiempos de respuesta en consultas típicas sobre gold
    print("\n== 6. Tiempos de Consultas Gold (Objetivo < 3.0 s) ==")
    for nombre, q in CONSULTAS_GOLD.items():
        t0 = time.perf_counter()
        cur.execute(q)
        cur.fetchall()
        seg = time.perf_counter() - t0
        ok = seg < 3.0
        if not ok:
            fallos += 1
        print(f"{'PASA ' if ok else 'FALLA'}  {nombre:<30}: {seg:.3f} s")

    print("\n================================================================================")
    print(f"RESULTADO GLOBAL: {'TODAS LAS VALIDACIONES PASARON (0 FALLOS)' if fallos == 0 else f'HUBO {fallos} FALLOS'}")
    print("================================================================================")

    conn.close()
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
