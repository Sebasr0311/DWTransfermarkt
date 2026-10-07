-- Migración: marcas de origen real vs sintético
-- Silver: origin ('real' | 'sintetico') y synthetic_batch (UUID)
ALTER TABLE silver.games
  ADD COLUMN IF NOT EXISTS origin VARCHAR(10) NOT NULL DEFAULT 'real' CHECK (origin IN ('real','sintetico')),
  ADD COLUMN IF NOT EXISTS synthetic_batch UUID NULL;

ALTER TABLE silver.appearances
  ADD COLUMN IF NOT EXISTS origin VARCHAR(10) NOT NULL DEFAULT 'real' CHECK (origin IN ('real','sintetico')),
  ADD COLUMN IF NOT EXISTS synthetic_batch UUID NULL;

ALTER TABLE silver.game_events
  ADD COLUMN IF NOT EXISTS origin VARCHAR(10) NOT NULL DEFAULT 'real' CHECK (origin IN ('real','sintetico')),
  ADD COLUMN IF NOT EXISTS synthetic_batch UUID NULL;

ALTER TABLE silver.player_valuations
  ADD COLUMN IF NOT EXISTS origin VARCHAR(10) NOT NULL DEFAULT 'real' CHECK (origin IN ('real','sintetico')),
  ADD COLUMN IF NOT EXISTS synthetic_batch UUID NULL;

-- Índices en silver para filtrado y rollback eficiente
CREATE INDEX IF NOT EXISTS ix_sg_origin ON silver.games (origin);
CREATE INDEX IF NOT EXISTS ix_sa_origin ON silver.appearances (origin);
CREATE INDEX IF NOT EXISTS ix_se_origin ON silver.game_events (origin);
CREATE INDEX IF NOT EXISTS ix_sv_origin ON silver.player_valuations (origin);

-- Gold: is_synthetic (BOOLEAN)
ALTER TABLE gold.dim_game
  ADD COLUMN IF NOT EXISTS is_synthetic BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE gold.fact_events
  ADD COLUMN IF NOT EXISTS is_synthetic BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE gold.fact_appearances
  ADD COLUMN IF NOT EXISTS is_synthetic BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE gold.fact_valuations
  ADD COLUMN IF NOT EXISTS is_synthetic BOOLEAN NOT NULL DEFAULT FALSE;

-- Índices en gold para filtrado rápido por sintético
CREATE INDEX IF NOT EXISTS ix_dg_is_synthetic ON gold.dim_game (is_synthetic);
CREATE INDEX IF NOT EXISTS ix_fe_is_synthetic ON gold.fact_events (is_synthetic);
CREATE INDEX IF NOT EXISTS ix_fa_is_synthetic ON gold.fact_appearances (is_synthetic);
CREATE INDEX IF NOT EXISTS ix_fv_is_synthetic ON gold.fact_valuations (is_synthetic);
