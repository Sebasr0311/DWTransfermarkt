-- Script 07: Migración histórica consolidada en DDLs base
-- NOTA ARQUITECTÓNICA: Las columnas de linaje sintético ('origin' y 'synthetic_batch' en silver,
-- y 'es_sintetico' en gold) ya se encuentran declaradas de forma nativa en:
--   - sql/silver/03_create_silver_tables.sql
--   - sql/gold/04_dimensions_facts.sql
-- Este script se preserva como no-op idempotente para mantener la secuencia numérica histórica.
DO $$
BEGIN
  -- Sin operaciones pendientes: esquema base consolidado.
  NULL;
END $$;
