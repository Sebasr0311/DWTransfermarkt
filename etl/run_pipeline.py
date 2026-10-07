"""Orquestador del pipeline: python -m etl.run_pipeline --layer all|bronze|silver|gold --chunk-size N"""
import argparse
import uuid

from etl.bronze import extract_bronze
from etl.common import config
from etl.gold import load_gold, refresh_aggregations
from etl.silver import transform_silver


def main():
    ap = argparse.ArgumentParser(description="Pipeline ETL DWH Transfermarkt")
    ap.add_argument("--layer", choices=["all", "bronze", "silver", "gold"], default="all")
    ap.add_argument("--chunk-size", type=int, default=config.CHUNK_SIZE)
    args = ap.parse_args()

    run_id = str(uuid.uuid4())
    print(f"run_id={run_id} layer={args.layer} chunk_size={args.chunk_size}")
    if args.layer in ("all", "bronze"):
        extract_bronze.run(run_id, args.chunk_size)
    if args.layer in ("all", "silver"):
        transform_silver.run(run_id)
    if args.layer in ("all", "gold"):
        load_gold.run(run_id)
        refresh_aggregations.run(run_id)
    print("Pipeline terminado")


if __name__ == "__main__":
    main()
