-- Esquemas del DWH (arquitectura medallón + metadatos)
CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;
CREATE SCHEMA IF NOT EXISTS meta;

-- RF11: auditoría y linaje por fase
CREATE TABLE IF NOT EXISTS meta.etl_audit (
  audit_id BIGSERIAL PRIMARY KEY, run_id UUID NOT NULL, layer VARCHAR(10) NOT NULL,
  table_name VARCHAR(60) NOT NULL, rows_read BIGINT, rows_transformed BIGINT,
  rows_discarded BIGINT, rows_inserted BIGINT, status VARCHAR(10),
  started_at TIMESTAMP DEFAULT now(), finished_at TIMESTAMP);

CREATE TABLE IF NOT EXISTS meta.etl_rejected (
  rejected_id BIGSERIAL PRIMARY KEY, run_id UUID, table_name VARCHAR(60),
  rule_id VARCHAR(5), reason TEXT, raw_record JSONB, created_at TIMESTAMP DEFAULT now());

CREATE INDEX IF NOT EXISTS ix_etl_audit_run ON meta.etl_audit (run_id);
CREATE INDEX IF NOT EXISTS ix_etl_rejected_run ON meta.etl_rejected (run_id, table_name, rule_id);

-- Funciones de conversión segura (devuelven NULL si el texto no se interpreta)
CREATE OR REPLACE FUNCTION meta.to_int(t TEXT) RETURNS BIGINT
LANGUAGE sql IMMUTABLE PARALLEL SAFE AS $$
  SELECT CASE WHEN t ~ '^\s*[-+]?\d{1,15}(\.\d+)?\s*$' THEN round(btrim(t)::numeric)::bigint END
$$;

CREATE OR REPLACE FUNCTION meta.to_num(t TEXT) RETURNS NUMERIC
LANGUAGE sql IMMUTABLE PARALLEL SAFE AS $$
  SELECT CASE WHEN t ~ '^\s*[-+]?(\d{1,15}(\.\d*)?|\.\d+)\s*$' THEN btrim(t)::numeric END
$$;

-- Acepta ISO (con o sin hora), AAAA/MM/DD, DD/MM/AAAA y DD-MM-AAAA. Resultado: DATE ISO-8601 o NULL.
CREATE OR REPLACE FUNCTION meta.to_date(t TEXT) RETURNS DATE
LANGUAGE plpgsql IMMUTABLE PARALLEL SAFE AS $$
BEGIN
  t := btrim(t);
  IF t IS NULL OR t = '' THEN RETURN NULL; END IF;
  IF t ~ '^\d{4}-\d{2}-\d{2}' THEN RETURN substr(t, 1, 10)::date;
  ELSIF t ~ '^\d{4}/\d{2}/\d{2}' THEN RETURN to_date(substr(t, 1, 10), 'YYYY/MM/DD');
  ELSIF t ~ '^\d{1,2}/\d{1,2}/\d{4}' THEN RETURN to_date(substring(t from '^\d{1,2}/\d{1,2}/\d{4}'), 'DD/MM/YYYY');
  ELSIF t ~ '^\d{1,2}-\d{1,2}-\d{4}' THEN RETURN to_date(substring(t from '^\d{1,2}-\d{1,2}-\d{4}'), 'DD-MM-YYYY');
  END IF;
  RETURN NULL;
EXCEPTION WHEN others THEN
  RETURN NULL;
END $$;
