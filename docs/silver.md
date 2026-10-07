# Capa plata

- **Propósito:** datos limpios, tipados e íntegros (PK, FK, CHECK).
- **Orden de carga:** competitions → clubs → players → games → appearances → game_events → player_valuations.
- **Tablas:** igual que en bronce, con nombres de columna ajustados (`date` → `game_date` / `valuation_date`).
- **Integridad (RNF02):** FK estrictas; los huérfanos no entran (ver E07 en `reglas_eda.md`).
- **Fechas (RNF05):** `DATE` ISO-8601 vía `meta.to_date` (acepta ISO, AAAA/MM/DD, DD/MM/AAAA, DD-MM-AAAA).
- **Nulos (RNF06):** goles, asistencias, tarjetas y minutos → 0; textos → `'Desconocido'`; valor de mercado → NULL.
- **Idempotencia:** `INSERT ... ON CONFLICT DO UPDATE`.
- **Trazabilidad:** `meta.etl_audit` (conteos por fase) y `meta.etl_rejected` (rechazados y resúmenes).
- **`game_events.game_event_id`:** si el CSV no lo trae, se deriva con `md5` de los campos del evento.
