-- Índices y Particionamiento Físico en Capa ORO

-- 1. Particiones para hecho_eventos_partido (1990-2035 + DEFAULT)
SELECT gold.asegurar_particiones_eventos(1990, 2035);
CREATE TABLE IF NOT EXISTS gold.hecho_eventos_partido_default PARTITION OF gold.hecho_eventos_partido DEFAULT;

-- 2. Índices B-Tree y Hash en hecho_eventos_partido (propagados a las particiones)
CREATE UNIQUE INDEX IF NOT EXISTS ux_hecho_eventos_bk ON gold.hecho_eventos_partido (evento_partido_id, fecha_key);
CREATE INDEX IF NOT EXISTS ix_hep_fecha ON gold.hecho_eventos_partido (fecha_key);
CREATE INDEX IF NOT EXISTS ix_hep_partido ON gold.hecho_eventos_partido (partido_key);
CREATE INDEX IF NOT EXISTS ix_hep_competicion ON gold.hecho_eventos_partido (competicion_key);
CREATE INDEX IF NOT EXISTS ix_hep_club ON gold.hecho_eventos_partido (club_key);
CREATE INDEX IF NOT EXISTS ix_hep_jugador ON gold.hecho_eventos_partido (jugador_key);
CREATE INDEX IF NOT EXISTS ix_hep_asistencia ON gold.hecho_eventos_partido (jugador_asistencia_key);
CREATE INDEX IF NOT EXISTS ix_hep_arbitro ON gold.hecho_eventos_partido (arbitro_key);
CREATE INDEX IF NOT EXISTS ixh_hep_tipo_evento ON gold.hecho_eventos_partido USING HASH (tipo_evento_key);
CREATE INDEX IF NOT EXISTS ix_hep_es_sintetico ON gold.hecho_eventos_partido (es_sintetico);

-- 3. Índices en hecho_rendimiento_jugador
CREATE INDEX IF NOT EXISTS ix_hrj_fecha ON gold.hecho_rendimiento_jugador (fecha_key);
CREATE INDEX IF NOT EXISTS ix_hrj_partido ON gold.hecho_rendimiento_jugador (partido_key);
CREATE INDEX IF NOT EXISTS ix_hrj_jugador ON gold.hecho_rendimiento_jugador (jugador_key);
CREATE INDEX IF NOT EXISTS ix_hrj_club ON gold.hecho_rendimiento_jugador (club_key);
CREATE INDEX IF NOT EXISTS ix_hrj_competicion ON gold.hecho_rendimiento_jugador (competicion_key);
CREATE INDEX IF NOT EXISTS ix_hrj_es_sintetico ON gold.hecho_rendimiento_jugador (es_sintetico);

-- 4. Índices en hecho_valoraciones_mercado
CREATE INDEX IF NOT EXISTS ix_hvm_fecha ON gold.hecho_valoraciones_mercado (fecha_key);
CREATE INDEX IF NOT EXISTS ix_hvm_club ON gold.hecho_valoraciones_mercado (club_key);
CREATE INDEX IF NOT EXISTS ix_hvm_es_sintetico ON gold.hecho_valoraciones_mercado (es_sintetico);

-- 5. Índices en dimensiones para optimizar joins del star schema
CREATE INDEX IF NOT EXISTS ix_dp_competicion ON gold.dim_partido (competicion_key);
CREATE INDEX IF NOT EXISTS ix_dp_arbitro ON gold.dim_partido (arbitro_key);
CREATE INDEX IF NOT EXISTS ix_dp_local ON gold.dim_partido (club_local_key);
CREATE INDEX IF NOT EXISTS ix_dp_visitante ON gold.dim_partido (club_visitante_key);
CREATE INDEX IF NOT EXISTS ix_dp_temporada ON gold.dim_partido (temporada);
CREATE INDEX IF NOT EXISTS ix_dp_es_sintetico ON gold.dim_partido (es_sintetico);
CREATE INDEX IF NOT EXISTS ix_dc_competicion ON gold.dim_club (competicion_key);
