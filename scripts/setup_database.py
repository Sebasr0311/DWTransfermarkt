"""Ejecuta todos los .sql en orden numérico y deja la base creada y lista."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from etl.common import config  # noqa: E402
from etl.common.db import get_connection  # noqa: E402


def sql_files():
    files = [p for p in config.SQL_DIR.rglob("*.sql") if re.match(r"\d{2}_", p.name)]
    # 00 (CREATE DATABASE) y 99 (validaciones) no forman parte del esquema
    files = [p for p in files if not p.name.startswith(("00_", "99_"))]
    return sorted(files, key=lambda p: p.name)


def main():
    conn = get_connection(dbname="postgres", autocommit=True)
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname=%s", (config.PG_DATABASE,))
        if cur.fetchone():
            print(f"Base {config.PG_DATABASE} ya existe")
        else:
            cur.execute((config.SQL_DIR / "00_create_database.sql").read_text(encoding="utf-8")
                        .replace("dwh_transfermarkt", config.PG_DATABASE))
            print(f"Base {config.PG_DATABASE} creada")
    conn.close()

    conn = get_connection(autocommit=True)
    with conn.cursor() as cur:
        for path in sql_files():
            cur.execute(path.read_text(encoding="utf-8"))
            print(f"OK  {path.relative_to(config.SQL_DIR)}")
    conn.close()


if __name__ == "__main__":
    main()
