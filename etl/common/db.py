"""Conexión a PostgreSQL con psycopg2."""
import psycopg2

from etl.common import config


def get_connection(dbname: str | None = None, autocommit: bool = False):
    conn = psycopg2.connect(
        host=config.PG_HOST, port=config.PG_PORT, user=config.PG_USER,
        password=config.PG_PASSWORD, dbname=dbname or config.PG_DATABASE,
    )
    conn.autocommit = autocommit
    return conn
