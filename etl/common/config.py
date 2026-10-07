"""Configuración del ETL: lee .env, tamaño de chunk y rutas."""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = int(os.getenv("PG_PORT", "5432"))
PG_USER = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "")
PG_DATABASE = os.getenv("PG_DATABASE", "dwh_transfermarkt")

# RNF01: chunk parametrizable (10.000 a 200.000 filas)
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "100000"))
RAW_DIR = (ROOT / os.getenv("RAW_DIR", "data/raw")).resolve()
SQL_DIR = ROOT / "sql"

# Tabla de bronce -> archivo CSV (orden de carga respeta dependencias)
CSV_FILES = {
    "competitions": "competitions.csv",
    "clubs": "clubs.csv",
    "players": "players.csv",
    "games": "games.csv",
    "player_valuations": "player_valuations.csv",
    "appearances": "appearances.csv",
    "game_events": "game_events.csv",
}
