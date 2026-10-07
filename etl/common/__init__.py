"""Módulo de utilidades comunes: configuración, base de datos y auditoría."""
from etl.common.audit import Audit
from etl.common.db import get_connection

__all__ = ["Audit", "get_connection"]
