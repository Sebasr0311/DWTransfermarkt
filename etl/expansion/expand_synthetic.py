"""Módulo de expansión controlada de datos sintéticos (RF12).

Genera datos sintéticos mediante clonación controlada para alcanzar el objetivo
de volumen (>= 10.565.088 filas en silver) preservando integridad referencial,
determinismo e idempotencia, sin tocar datos reales.
"""
import uuid
from typing import Dict, Tuple

from etl.common.audit import Audit
from etl.common.db import get_connection
from etl.gold import load_gold, refresh_aggregations

# Constantes del modelo de expansión
BASE_SYNTHETIC_GAME_ID = 900000000
PROPOSAL_TARGET_APPEARANCES = 1894350
PROPOSAL_TARGET_VALUATIONS = 1385000
LARGE_TABLES = [
    "silver.games",
    "silver.appearances",
    "silver.game_events",
    "silver.player_valuations",
    "gold.dim_game",
    "gold.fact_events",
    "gold.fact_appearances",
    "gold.fact_valuations",
]


def calcular_plan_expansion(conn, target_total: int) -> dict:
    """Calcula las filas requeridas por tabla para cumplir el target_total."""
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM silver.competitions")
    cnt_comp = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM silver.clubs")
    cnt_club = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM silver.players")
    cnt_play = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM silver.games WHERE origin = 'real'")
    cnt_games_real = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM silver.appearances WHERE origin = 'real'")
    cnt_app_real = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM silver.game_events WHERE origin = 'real'")
    cnt_events_real = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM silver.player_valuations WHERE origin = 'real'")
    cnt_val_real = cur.fetchone()[0]

    total_real = (cnt_comp + cnt_club + cnt_play + cnt_games_real +
                  cnt_app_real + cnt_events_real + cnt_val_real)

    gap = max(0, target_total - total_real)

    # 1. Metas específicas de la propuesta para apariciones y valoraciones
    needed_app = max(0, PROPOSAL_TARGET_APPEARANCES - cnt_app_real)
    needed_val = max(0, PROPOSAL_TARGET_VALUATIONS - cnt_val_real)

    # 2. El resto del volumen proviene de juegos y eventos sintéticos
    remaining_gap = max(0, gap - (needed_app + needed_val))

    # Obtener juegos reales que tienen eventos
    cur.execute("""
        SELECT g.game_id, count(e.game_event_id) AS event_cnt
        FROM silver.games g
        JOIN silver.game_events e ON e.game_id = g.game_id AND e.origin = 'real'
        WHERE g.origin = 'real'
        GROUP BY g.game_id
        ORDER BY g.game_id
    """)
    games_with_events = cur.fetchall()
    n_games_base = len(games_with_events)
    n_events_base = sum(x[1] for x in games_with_events)
    full_pass_rows = n_games_base + n_events_base

    full_passes = remaining_gap // full_pass_rows
    rem_partial = remaining_gap - (full_passes * full_pass_rows)

    cum = 0
    partial_games = 0
    partial_events = 0
    for gid, ecnt in games_with_events:
        if cum >= rem_partial and remaining_gap > 0:
            break
        cum += (1 + ecnt)
        partial_games += 1
        partial_events += ecnt

    total_syn_games = (full_passes * n_games_base) + partial_games
    total_syn_events = (full_passes * n_events_base) + partial_events

    total_syn_rows = needed_app + needed_val + total_syn_games + total_syn_events
    total_projected = total_real + total_syn_rows

    plan = {
        "target_total": target_total,
        "total_real": total_real,
        "gap": gap,
        "needed_app": needed_app,
        "needed_val": needed_val,
        "remaining_gap": remaining_gap,
        "full_passes": full_passes,
        "n_games_base": n_games_base,
        "n_events_base": n_events_base,
        "partial_games": partial_games,
        "partial_events": partial_events,
        "total_syn_games": total_syn_games,
        "total_syn_events": total_syn_events,
        "total_syn_rows": total_syn_rows,
        "total_projected": total_projected,
    }
    cur.close()
    return plan


def rollback(run_id: str | None = None) -> dict:
    """Elimina todas las filas sintéticas de silver y gold de forma reversible."""
    batch_id = run_id or str(uuid.uuid4())
    audit = Audit(batch_id, "expand")
    conn = get_connection(autocommit=True)
    cur = conn.cursor()
    borradas = {}
    print(f"[rollback] Iniciando reversión de datos sintéticos (batch={batch_id})...")
    try:
        # 1. Limpieza en gold (hechos y dimensiones sintéticas)
        cur.execute("DELETE FROM gold.fact_events WHERE is_synthetic = TRUE")
        borradas["gold.fact_events"] = cur.rowcount
        cur.execute("DELETE FROM gold.fact_appearances WHERE is_synthetic = TRUE")
        borradas["gold.fact_appearances"] = cur.rowcount
        cur.execute("DELETE FROM gold.fact_valuations WHERE is_synthetic = TRUE")
        borradas["gold.fact_valuations"] = cur.rowcount
        cur.execute("DELETE FROM gold.dim_game WHERE is_synthetic = TRUE")
        borradas["gold.dim_game"] = cur.rowcount

        # 2. Limpieza en silver (en orden inverso de dependencias FK)
        cur.execute("DELETE FROM silver.game_events WHERE origin = 'sintetico'")
        borradas["silver.game_events"] = cur.rowcount
        cur.execute("DELETE FROM silver.appearances WHERE origin = 'sintetico'")
        borradas["silver.appearances"] = cur.rowcount
        cur.execute("DELETE FROM silver.player_valuations WHERE origin = 'sintetico'")
        borradas["silver.player_valuations"] = cur.rowcount
        cur.execute("DELETE FROM silver.games WHERE origin = 'sintetico'")
        borradas["silver.games"] = cur.rowcount

        for tabla, n in borradas.items():
            print(f"[rollback] {tabla}: {n} filas sintéticas eliminadas")

        # 3. Refrescar agregaciones de gold
        print("[rollback] Refrescando vistas agregadas de gold...")
        refresh_aggregations.run(batch_id)

        # 4. Auditoría
        aid = audit.start("rollback_all")
        total_borradas = sum(borradas.values())
        audit.finish(aid, read=total_borradas, transformed=total_borradas,
                     discarded=total_borradas, inserted=0, status="OK")
        print(f"[rollback] Reversión completada. Total filas eliminadas: {total_borradas}")
        return borradas
    finally:
        cur.close()
        conn.close()
        audit.close()


def expand(run_id: str | None = None, target_total: int = 10565088) -> dict:
    """Ejecuta la expansión controlada de datos sintéticos hasta target_total."""
    batch_id = run_id or str(uuid.uuid4())
    audit = Audit(batch_id, "expand")
    conn = get_connection(autocommit=True)
    cur = conn.cursor()

    try:
        # Fijar semilla determinista en PostgreSQL
        cur.execute("SELECT setseed(0.42)")

        # Idempotencia: rollback previo automático
        rollback(batch_id)

        # Cálculo del tamaño y plan
        plan = calcular_plan_expansion(conn, target_total)
        print("\n=== PLAN DE EXPANSIÓN CONTROLADA ===")
        print(f"Meta total solicitada       : {plan['target_total']:,} filas")
        print(f"Total datos reales (silver) : {plan['total_real']:,} filas")
        print(f"Brecha a cubrir             : {plan['gap']:,} filas")
        print("--- Distribución sintética calculada ---")
        print(f"  player_valuations         : +{plan['needed_val']:,} filas")
        print(f"  appearances               : +{plan['needed_app']:,} filas")
        print(f"  games (partidos clonados) : +{plan['total_syn_games']:,} filas (passes={plan['full_passes']})")
        print(f"  game_events               : +{plan['total_syn_events']:,} filas")
        print(f"Total sintético a generar   : {plan['total_syn_rows']:,} filas")
        print(f"Total proyectado en silver  : {plan['total_projected']:,} filas")
        print("=====================================\n")

        # 1. Crear tabla temporal de juegos base indexados
        cur.execute("DROP TABLE IF EXISTS temp_ranked_games")
        cur.execute("""
            CREATE TEMP TABLE temp_ranked_games AS
            SELECT row_number() OVER (ORDER BY g.game_id)::int AS rnk,
                   g.game_id, g.competition_id, g.season, g."round",
                   g.game_date, g.home_club_id, g.away_club_id,
                   g.home_club_goals, g.away_club_goals, g.stadium,
                   g.attendance, g.referee
            FROM silver.games g
            WHERE g.origin = 'real'
              AND g.game_id IN (SELECT DISTINCT game_id FROM silver.game_events WHERE origin = 'real')
        """)
        cur.execute("CREATE UNIQUE INDEX ix_trg_rnk ON temp_ranked_games (rnk)")
        cur.execute("CREATE INDEX ix_trg_gid ON temp_ranked_games (game_id)")

        # 2. Generar juegos sintéticos (por pases)
        print("[expand] Insertando partidos sintéticos (silver.games)...")
        aid_games = audit.start("silver.games")
        total_games_inserted = 0
        n_base = plan["n_games_base"]

        total_passes = plan["full_passes"] + (1 if plan["partial_games"] > 0 else 0)
        for p in range(1, total_passes + 1):
            max_rnk = n_base if p <= plan["full_passes"] else plan["partial_games"]
            if max_rnk <= 0:
                continue
            cur.execute("""
                INSERT INTO silver.games (game_id, competition_id, season, "round", game_date,
                                          home_club_id, away_club_id, home_club_goals, away_club_goals,
                                          stadium, attendance, referee, origin, synthetic_batch)
                SELECT %(base_id)s + (%(pass)s - 1) * %(n_base)s + rnk,
                       competition_id, season, "round", game_date, home_club_id, away_club_id,
                       home_club_goals, away_club_goals, stadium, attendance, referee,
                       'sintetico', %(batch_id)s
                FROM temp_ranked_games
                WHERE rnk <= %(max_rnk)s
            """, {
                "base_id": BASE_SYNTHETIC_GAME_ID,
                "pass": p,
                "n_base": n_base,
                "max_rnk": max_rnk,
                "batch_id": batch_id,
            })
            total_games_inserted += cur.rowcount

        audit.finish(aid_games, read=total_games_inserted, transformed=total_games_inserted,
                     discarded=0, inserted=total_games_inserted, status="OK")
        print(f"[expand] silver.games: {total_games_inserted:,} filas sintéticas insertadas")

        # 3. Generar eventos sintéticos (silver.game_events) por pases
        print("[expand] Insertando eventos sintéticos (silver.game_events)...")
        aid_events = audit.start("silver.game_events")
        total_events_inserted = 0

        for p in range(1, total_passes + 1):
            max_rnk = n_base if p <= plan["full_passes"] else plan["partial_games"]
            if max_rnk <= 0:
                continue
            cur.execute("""
                INSERT INTO silver.game_events (game_event_id, game_id, game_date, "minute", "type",
                                               club_id, player_id, description, player_in_id, player_assist_id,
                                               origin, synthetic_batch)
                SELECT 'SYN-' || %(pass)s || '-' || e.game_event_id,
                       %(base_id)s + (%(pass)s - 1) * %(n_base)s + rg.rnk,
                       rg.game_date,
                       CASE WHEN e."minute" IS NULL THEN NULL
                            ELSE LEAST(130, GREATEST(0, e."minute" + mod(hashtext(e.game_event_id || '-' || %(pass)s::text), 7) - 3))
                       END,
                       e."type",
                       e.club_id,
                       e.player_id,
                       e.description,
                       e.player_in_id,
                       e.player_assist_id,
                       'sintetico',
                       %(batch_id)s
                FROM temp_ranked_games rg
                JOIN silver.game_events e ON e.game_id = rg.game_id AND e.origin = 'real'
                WHERE rg.rnk <= %(max_rnk)s
            """, {
                "pass": p,
                "base_id": BASE_SYNTHETIC_GAME_ID,
                "n_base": n_base,
                "max_rnk": max_rnk,
                "batch_id": batch_id,
            })
            cnt_p = cur.rowcount
            total_events_inserted += cnt_p
            print(f"[expand]   Pase {p}/{total_passes}: {cnt_p:,} eventos insertados")

        audit.finish(aid_events, read=total_events_inserted, transformed=total_events_inserted,
                     discarded=0, inserted=total_events_inserted, status="OK")
        print(f"[expand] silver.game_events: {total_events_inserted:,} filas sintéticas insertadas")

        # 4. Generar apariciones sintéticas (silver.appearances)
        print("[expand] Insertando apariciones sintéticas (silver.appearances)...")
        aid_app = audit.start("silver.appearances")
        cur.execute("""
            INSERT INTO silver.appearances (appearance_id, game_id, player_id, player_club_id, game_date,
                                            goals, assists, yellow_cards, red_cards, minutes_played,
                                            origin, synthetic_batch)
            SELECT 'SYN-1-' || a.appearance_id,
                   %(base_id)s + rg.rnk,
                   a.player_id,
                   a.player_club_id,
                   rg.game_date,
                   a.goals,
                   a.assists,
                   a.yellow_cards,
                   a.red_cards,
                   a.minutes_played,
                   'sintetico',
                   %(batch_id)s
            FROM temp_ranked_games rg
            JOIN silver.appearances a ON a.game_id = rg.game_id AND a.origin = 'real'
            ORDER BY rg.rnk, a.player_id
            LIMIT %(needed_app)s
        """, {
            "base_id": BASE_SYNTHETIC_GAME_ID,
            "needed_app": plan["needed_app"],
            "batch_id": batch_id,
        })
        total_app_inserted = cur.rowcount
        audit.finish(aid_app, read=total_app_inserted, transformed=total_app_inserted,
                     discarded=0, inserted=total_app_inserted, status="OK")
        print(f"[expand] silver.appearances: {total_app_inserted:,} filas sintéticas insertadas")

        # 5. Generar valoraciones sintéticas (silver.player_valuations)
        print("[expand] Insertando valoraciones sintéticas (silver.player_valuations)...")
        aid_val = audit.start("silver.player_valuations")
        cur.execute("""
            WITH candidates AS (
              SELECT v.player_id,
                     (v.valuation_date + (s.offset_step * 14 || ' days')::interval)::date AS vdate,
                     round(v.market_value_in_eur * (0.95 + 0.10 * ((hashtext(v.player_id::text || '-' || v.valuation_date::text || '-' || s.offset_step::text) & 2147483647)::numeric / 2147483647.0)), 2) AS mv,
                     v.current_club_id
              FROM silver.player_valuations v
              CROSS JOIN (VALUES (1), (2), (3)) AS s(offset_step)
              WHERE v.origin = 'real'
            ),
            uniq AS (
              SELECT DISTINCT ON (c.player_id, c.vdate) c.player_id, c.vdate, c.mv, c.current_club_id
              FROM candidates c
              LEFT JOIN silver.player_valuations exist
                ON exist.player_id = c.player_id AND exist.valuation_date = c.vdate
              WHERE exist.player_id IS NULL
              ORDER BY c.player_id, c.vdate
            )
            INSERT INTO silver.player_valuations (player_id, valuation_date, market_value_in_eur, current_club_id, origin, synthetic_batch)
            SELECT player_id, vdate, mv, current_club_id, 'sintetico', %(batch_id)s
            FROM uniq
            LIMIT %(needed_val)s
        """, {
            "needed_val": plan["needed_val"],
            "batch_id": batch_id,
        })
        total_val_inserted = cur.rowcount
        audit.finish(aid_val, read=total_val_inserted, transformed=total_val_inserted,
                     discarded=0, inserted=total_val_inserted, status="OK")
        print(f"[expand] silver.player_valuations: {total_val_inserted:,} filas sintéticas insertadas")

        # 6. Verificación de conteo total en silver
        cur.execute("""
            SELECT count(*) FROM (
                SELECT 1 FROM silver.competitions
                UNION ALL SELECT 1 FROM silver.clubs
                UNION ALL SELECT 1 FROM silver.players
                UNION ALL SELECT 1 FROM silver.games
                UNION ALL SELECT 1 FROM silver.appearances
                UNION ALL SELECT 1 FROM silver.game_events
                UNION ALL SELECT 1 FROM silver.player_valuations
            ) t
        """)
        total_silver = cur.fetchone()[0]
        print(f"\n[expand] TOTAL FILAS EN SILVER: {total_silver:,} (meta >= {target_total:,})")

        # 7. Propagar a capa gold
        print("\n[expand] Propagando datos a capa gold...")
        load_gold.run(batch_id)

        # 8. Refrescar agregaciones
        print("[expand] Refrescando vistas agregadas de gold...")
        refresh_aggregations.run(batch_id)

        # 9. VACUUM ANALYZE en tablas grandes
        print("[expand] Ejecutando VACUUM ANALYZE en tablas grandes...")
        for t in LARGE_TABLES:
            try:
                cur.execute(f"VACUUM ANALYZE {t}")
            except Exception as e:
                print(f"[expand] Advertencia al optimizar {t}: {e}")

        # 10. Validar partición por defecto
        cur.execute("SELECT count(*) FROM gold.fact_events_default")
        def_cnt = cur.fetchone()[0]
        if def_cnt > 0:
            print(f"[expand] ALERTA: gold.fact_events_default contiene {def_cnt} filas")
        else:
            print("[expand] OK: gold.fact_events_default tiene 0 filas")

        return {
            "batch_id": batch_id,
            "total_silver": total_silver,
            "games_sinteticos": total_games_inserted,
            "events_sinteticos": total_events_inserted,
            "appearances_sinteticas": total_app_inserted,
            "valuations_sinteticas": total_val_inserted,
        }
    finally:
        cur.close()
        conn.close()
        audit.close()
