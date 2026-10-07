"""Extracción CSV -> bronze por chunks con COPY (RNF01, RNF07, RNF09)."""
import io
import uuid

import pandas as pd

from etl.common import config
from etl.common.audit import Audit
from etl.common.db import get_connection

ENCODINGS = ("utf-8", "latin-1")  # RNF09: utf-8 con respaldo latin-1


def _bronze_columns(cur, table: str) -> list[str]:
    cur.execute(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema='bronze' AND table_name=%s AND left(column_name, 1) != '_' "
        "ORDER BY ordinal_position", (table,))
    return [r[0] for r in cur.fetchall()]


def _count_lines(path) -> int:
    n = 0
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            n += block.count(b"\n")
    return n


def _load_with_encoding(conn, table, path, cols, chunk_size, encoding, load_id):
    """Carga el archivo completo con una codificación. Devuelve (filas leídas, columnas faltantes, extras)."""
    header = pd.read_csv(path, nrows=0, dtype=str, encoding=encoding).columns
    header_map = {c: c.strip().lower() for c in header}
    use = [orig for orig, norm in header_map.items() if norm in cols]
    missing = [c for c in cols if c not in header_map.values()]
    extra = [orig for orig, norm in header_map.items() if norm not in cols]
    load_cols = cols + ["_load_id", "_source_file"]
    copy_sql = (f"COPY bronze.{table} ({', '.join(chr(34) + c + chr(34) for c in load_cols)}) "
                "FROM STDIN WITH (FORMAT csv, NULL '\\N')")
    rows = 0
    with conn.cursor() as cur:
        cur.execute(f"TRUNCATE bronze.{table} RESTART IDENTITY")
        reader = pd.read_csv(path, dtype=str, chunksize=chunk_size, on_bad_lines="skip",
                             encoding=encoding, usecols=use, keep_default_na=False, na_values=[""])
        for chunk in reader:
            chunk.columns = [header_map[c] for c in chunk.columns]
            chunk = chunk.reindex(columns=cols)
            chunk["_load_id"] = load_id
            chunk["_source_file"] = path.name
            buf = io.StringIO()
            chunk.to_csv(buf, index=False, header=False, na_rep="\\N")
            buf.seek(0)
            cur.copy_expert(copy_sql, buf)
            rows += len(chunk)
    return rows, missing, extra


def run(run_id: str, chunk_size: int = config.CHUNK_SIZE) -> dict:
    audit = Audit(run_id, "bronze")
    conn = get_connection()
    resumen = {}
    try:
        for table, filename in config.CSV_FILES.items():
            path = config.RAW_DIR / filename
            if not path.exists():
                print(f"[bronze] FALTA {path} -> se omite {table}")
                resumen[table] = "FALTA_ARCHIVO"
                continue
            audit_id = audit.start(table)
            with conn.cursor() as cur:
                cols = _bronze_columns(cur, table)
            load_id = str(uuid.uuid4())
            rows = missing = extra = None
            retried = 0
            for i, enc in enumerate(ENCODINGS):
                try:
                    rows, missing, extra = _load_with_encoding(conn, table, path, cols, chunk_size, enc, load_id)
                    conn.commit()
                    break
                except UnicodeDecodeError:
                    conn.rollback()
                    retried += 1  # E08: reintento con otra codificación
                    print(f"[bronze] {table}: {enc} falló, reintentando con la siguiente")
            if rows is None:
                audit.finish(audit_id, status="ERROR")
                raise RuntimeError(f"No se pudo decodificar {path}")
            skipped = max(_count_lines(path) - 1 - rows, 0)  # aproximado (saltos de línea dentro de comillas)
            audit.finish(audit_id, read=rows + skipped, transformed=rows, discarded=skipped, inserted=rows)
            print(f"[bronze] {table}: {rows} filas, {skipped} líneas omitidas, reintentos={retried}, "
                  f"columnas faltantes={missing}, columnas extra ignoradas={extra}")
            resumen[table] = rows
    finally:
        conn.close()
        audit.close()
    return resumen
