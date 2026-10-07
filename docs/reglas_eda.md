# Reglas EDA

| ID | Regla | Acción | Dónde se implementa |
|---|---|---|---|
| E01 | Nulos en goles, asistencias, tarjetas, minutos | Imputar 0 | `COALESCE(..., 0)` en silver |
| E02 | Nulos en valor de mercado | Mantener NULL | players, player_valuations |
| E03 | Nulos en textos | `'Desconocido'` | helper `txt()` |
| E04 | Fechas en formato mixto | ISO-8601; si no se interpreta, rechazar | `meta.to_date` |
| E05 | Duplicados por llave de negocio | Conservar uno (el último) | `DISTINCT ON` + `ON CONFLICT` |
| E06 | Minuto fuera de 0–130 o valores negativos | Rechazar | silver |
| E07 | FK sin padre | Rechazar y registrar | silver |
| E08 | Codificación/delimitador corrupto | Reintentar y contar | bronze (utf-8 → latin-1) |
| E09 | Texto en columna numérica | NULL controlado y contar | silver (`meta.to_int/to_num`) |
| E10 | Llave de negocio nula o inválida (regla adicional) | Rechazar | silver |

## Decisiones
- **E07 en FK opcionales** (`players.current_club_id`, `clubs.domestic_competition_id`, `game_events.player_id`):
  la fila se conserva con la FK en NULL y se registra un resumen E07 en `meta.etl_rejected`.
  En FK obligatorias la fila se rechaza.
- **Métricas numéricas no deportivas** (`squad_size`, `average_age`, `attendance`, `height_in_cm`): se dejan NULL, no 0
  (un 0 falsearía promedios). Solo E01 imputa 0.
- **Fecha opcional ausente** (fecha de nacimiento): NULL. Fecha obligatoria ausente: rechazo, salvo
  `appearances` y `game_events`, que heredan la fecha del partido.
- E05 y E09 se resumen con una fila (`filas_afectadas`) por tabla y corrida en `meta.etl_rejected`.
