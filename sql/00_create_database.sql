-- Se ejecuta conectado a la base 'postgres'.
-- scripts/setup_database.py lo omite si la base ya existe (CREATE DATABASE no admite IF NOT EXISTS).
-- Los esquemas bronze, silver, gold y meta se crean en meta/01_schema_meta.sql (ya dentro de la nueva base).
CREATE DATABASE dwh_transfermarkt;
