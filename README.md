# DWH Transfermarkt

Data Warehouse en **PostgreSQL** con Arquitectura Medallón (bronze → silver → gold), modelo estrella y ETL en Python.
Proyecto integrador de Bases de Datos Avanzadas (Ingeniería de Sistemas, Universidad Popular del Cesar). Consolida
~10,5 millones de registros de Transfermarkt para analítica en Power BI.

```
CSV (data/raw) --COPY por chunks--> bronze (TEXT crudo)
                                      --limpieza, tipos, FK--> silver (PK/FK, CHECK)
                                                                 --estrella--> gold (dim_*, fact_*, agg_*)
meta.etl_audit / meta.etl_rejected: auditoría y linaje de cada fase
```

## Requisitos
- Python 3.10+ y PostgreSQL 14+ (o Docker Desktop con `docker-compose.yml`, imagen `postgres:16`).
- CSV de Transfermarkt en `data/raw/`: `competitions.csv`, `clubs.csv`, `players.csv`, `games.csv`,
  `player_valuations.csv`, `appearances.csv`, `game_events.csv`.

## Instalación
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env     # editar credenciales (el .env no se versiona)
```

## Uso
```powershell
docker compose up -d                      # solo si no tienes PostgreSQL local
python scripts/setup_database.py          # 1) crea la base, esquemas y tablas
python -m etl.run_pipeline --layer all --chunk-size 100000   # 2) y 3) carga + silver + gold
python scripts/validate.py                # 4) validaciones, volumetría y tiempos
pytest                                    # pruebas
```
Capas por separado: `--layer bronze|silver|gold`. El pipeline es idempotente.

## Estructura
`sql/` DDL por capa · `etl/` pipeline Python · `scripts/` utilidades · `docs/` documentación por capa · `tests/` pytest.
Más detalle en `docs/bronze.md`, `docs/silver.md`, `docs/gold.md` y `docs/reglas_eda.md`.
