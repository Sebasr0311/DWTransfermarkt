"""Pruebas unitarias y de integración para la expansión controlada (RF12)."""
from decimal import Decimal
import pytest

from etl.common.db import get_connection

BASELINE_CHECKSUMS = {
    "competitions": (65, -7132307758, "competition_id, name, type, country_name, confederation"),
    "clubs": (796, -46340764361, "club_id, name, domestic_competition_id, stadium_name, squad_size, average_age"),
    "players": (50149, 15712675432, "player_id, name, position, sub_position, date_of_birth, country_of_citizenship, foot, height_in_cm, current_club_id, market_value_in_eur"),
    "games": (72602, 776084486429, "game_id, competition_id, season, round, game_date, home_club_id, away_club_id, home_club_goals, away_club_goals, stadium, attendance, referee"),
    "appearances": (1813294, -2786230826709, "appearance_id, game_id, player_id, player_club_id, game_date, goals, assists, yellow_cards, red_cards, minutes_played"),
    "game_events": (1032318, 1422080252746, "game_event_id, game_id, game_date, minute, type, club_id, player_id, description, player_in_id, player_assist_id"),
    "player_valuations": (656301, 425532711250, "player_id, valuation_date, market_value_in_eur, current_club_id"),
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


@pytest.fixture(scope="module")
def cur():
    conn = get_connection(autocommit=True)
    yield conn.cursor()
    conn.close()


def test_volumen_minimo_silver(cur):
    """El total de filas en silver debe ser >= 10.565.088."""
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
    total = cur.fetchone()[0]
    assert total >= 10565088


def test_marcas_origen_correctas(cur):
    """Todo registro debe tener origin en ('real','sintetico') y los sintéticos tener batch."""
    for t in ["games", "appearances", "game_events", "player_valuations"]:
        cur.execute(f"SELECT count(*) FROM silver.{t} WHERE origin NOT IN ('real', 'sintetico')")
        assert cur.fetchone()[0] == 0
        cur.execute(f"SELECT count(*) FROM silver.{t} WHERE origin = 'sintetico' AND synthetic_batch IS NULL")
        assert cur.fetchone()[0] == 0


def test_integridad_referencial_silver_y_gold(cur):
    """Cero huérfanos en todas las llaves foráneas de silver y gold."""
    consultas = [
        "SELECT count(*) FROM silver.games c LEFT JOIN silver.competitions p USING (competition_id) WHERE p.competition_id IS NULL",
        "SELECT count(*) FROM silver.games c LEFT JOIN silver.clubs p ON p.club_id = c.home_club_id WHERE p.club_id IS NULL",
        "SELECT count(*) FROM silver.games c LEFT JOIN silver.clubs p ON p.club_id = c.away_club_id WHERE p.club_id IS NULL",
        "SELECT count(*) FROM silver.appearances c LEFT JOIN silver.games p USING (game_id) WHERE p.game_id IS NULL",
        "SELECT count(*) FROM silver.appearances c LEFT JOIN silver.players p USING (player_id) WHERE p.player_id IS NULL",
        "SELECT count(*) FROM silver.game_events c LEFT JOIN silver.games p USING (game_id) WHERE p.game_id IS NULL",
        "SELECT count(*) FROM silver.game_events c LEFT JOIN silver.clubs p USING (club_id) WHERE p.club_id IS NULL",
        "SELECT count(*) FROM silver.player_valuations c LEFT JOIN silver.players p USING (player_id) WHERE p.player_id IS NULL",
        "SELECT count(*) FROM gold.fact_events f LEFT JOIN gold.dim_game d USING (game_key) WHERE d.game_key IS NULL",
        "SELECT count(*) FROM gold.fact_appearances f LEFT JOIN gold.dim_game d USING (game_key) WHERE d.game_key IS NULL",
        "SELECT count(*) FROM gold.fact_appearances f LEFT JOIN gold.dim_player d USING (player_key) WHERE d.player_key IS NULL",
        "SELECT count(*) FROM gold.fact_valuations f LEFT JOIN gold.dim_player d USING (player_key) WHERE d.player_key IS NULL",
    ]
    for q in consultas:
        cur.execute(q)
        assert cur.fetchone()[0] == 0


@pytest.mark.parametrize("tabla", list(BASELINE_CHECKSUMS.keys()))
def test_checksums_datos_reales(cur, tabla):
    """Los datos reales no sufren alteración ni degradación."""
    exp_cnt, exp_chk, cols = BASELINE_CHECKSUMS[tabla]
    filtro = "WHERE origin = 'real'" if tabla in ["games", "appearances", "game_events", "player_valuations"] else ""
    cur.execute(f"SELECT count(*), sum(hashtext(ROW({cols})::text)::bigint) FROM silver.{tabla} {filtro}")
    cnt, chk = cur.fetchone()
    assert cnt == exp_cnt
    assert chk == exp_chk


@pytest.mark.parametrize("vista", list(BASELINE_AGGREGATIONS.keys()))
def test_agregaciones_oro_inalteradas(cur, vista):
    """Las vistas agregadas en gold solo consideran datos reales."""
    query, exp_tuple = BASELINE_AGGREGATIONS[vista]
    cur.execute(query)
    actual = cur.fetchone()
    assert actual == exp_tuple


def test_cero_filas_en_particion_default(cur):
    """La partición default de gold.fact_events no debe tener filas."""
    cur.execute("SELECT count(*) FROM gold.fact_events_default")
    assert cur.fetchone()[0] == 0
