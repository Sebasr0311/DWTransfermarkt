# Módulo de Expansión Controlada de Datos Sintéticos (`etl/expansion`)

Este paquete implementa la expansión controlada, determinista, trazable y reversible del Data Warehouse `DWTransfermarkt` desde el volumen base real (~3,62 millones de registros en plata) hasta cumplir con la meta de volumetría de la propuesta (**>= 10.565.088 registros**).

## Principios de Diseño

1. **Honestidad y Trazabilidad Permanente:**
   - En la capa `silver`, cada registro generado incluye `origin = 'sintetico'` y el identificador `synthetic_batch` (UUID).
   - En la capa `gold`, las dimensiones y hechos generados incluyen `is_synthetic = TRUE`.
   - Ningún dato sintético puede confundirse con datos reales.

2. **Inalterabilidad de Datos Reales:**
   - Los registros reales (`origin = 'real'`, `is_synthetic = FALSE`) no se modifican, eliminan ni reordenan.
   - Su integridad se audita mediante conteos exactos y sumas de verificación criptográficas/hash por tabla.

3. **Integridad Referencial Estricta (0 Huérfanos):**
   - Los partidos sintéticos (`silver.games`, IDs `>= 900000000`) conservan referencias a competiciones, clubes, estadios y árbitros reales.
   - Los eventos sintéticos (`silver.game_events`, prefijo `SYN-`) y apariciones sintéticas (`silver.appearances`, prefijo `SYN-`) referencian partidos sintéticos existentes y clubes/jugadores reales.
   - Las valoraciones sintéticas (`silver.player_valuations`) se generan para jugadores reales en fechas no utilizadas previamente, respetando la clave primaria compuesta `(player_id, valuation_date)`.

4. **Determinismo:**
   - La semilla fija (`seed = 42`, `setseed(0.42)`) garantiza resultados idénticos en cada ejecución.

5. **Idempotencia y Reversibilidad:**
   - Ejecutar la expansión ejecuta automáticamente un rollback de corridas sintéticas previas.
   - El flag `--rollback` elimina todo registro sintético de `silver` y `gold`, refresca las vistas materializadas y devuelve la base de datos exactamente a su estado base original.

6. **Aislamiento Analítico:**
   - Las vistas materializadas de negocio (`gold.agg_*`) calculan métricas exclusivamente sobre `is_synthetic = FALSE`, asegurando que las estadísticas de negocio no sufran distorsión por las pruebas de volumen.

## Comandos de Ejecución

### Expansión de volumen:
```bash
python -m etl.run_pipeline --layer expand --target-total 10565088
```

### Reversión completa (Rollback):
```bash
python -m etl.run_pipeline --layer expand --rollback
```
