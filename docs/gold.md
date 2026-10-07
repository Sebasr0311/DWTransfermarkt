# Capa oro: modelo estrella

```
                    dim_date            dim_competition        dim_referee
                       |                      |                     |
dim_player ---- fact_appearances ----- dim_game ------------- dim_club
    |                                      |
    +------- fact_events (partic.) --------+---- dim_event_type
    +------- fact_valuations
```

## Grano
- `fact_events`: un evento de partido (gol, tarjeta, sustitución…). Partición anual por `date_key`.
- `fact_appearances`: un jugador en un partido.
- `fact_valuations`: una valoración de mercado de un jugador en una fecha.

## Dimensiones y jerarquías
- `dim_date`: día → semana/mes → trimestre → año; `season` = año de inicio de temporada (jul–jun).
- `dim_competition`: confederación → país → competición.
- `dim_club`: competición doméstica → club.
- `dim_player`: posición → sub-posición → jugador; país de ciudadanía.
- `dim_game`: temporada → ronda → partido (con local, visitante, árbitro, estadio).
- `dim_referee`, `dim_event_type`.

## Medidas y reglas
- `minute_bucket`: 0 = 0–14, 1 = 15–29, …, 6 = 90 o más. `is_home`: el club del evento es el local.
- Llaves de negocio (`game_event_id`, `appearance_id`, `(player_key, date_key)`) para idempotencia.
- Índices B-Tree en FK, Hash en `event_type_key`, único en llaves de negocio.
- Vistas materializadas: `agg_player_season`, `agg_club_season`, `agg_events_15min`, `agg_discipline_ref`, `agg_home_away`.
