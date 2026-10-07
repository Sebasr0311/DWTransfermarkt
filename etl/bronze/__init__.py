"""Capa Bronce: Ingesta de datos crudos desde archivos CSV hacia PostgreSQL."""
from etl.bronze import extract_bronze

__all__ = ["extract_bronze"]
