"""Orchestrate Bronze ingestion for all entities."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from bronze_common import BronzeConfig, default_config, format_dry_run_report, run_ingestion


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Ingest customers, products, and orders CSVs into "
            "de_c1_coding_evaluation.bronze Delta tables."
        )
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate all CSV files locally without writing to Delta.",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Directory containing source CSV files (default: project data/).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = default_config() if args.data_dir is None else BronzeConfig(data_dir=args.data_dir)

    try:
        if args.dry_run:
            results = run_ingestion(config, dry_run=True)
            print(format_dry_run_report(results))
            return 0

        from pyspark.sql import SparkSession

        spark = SparkSession.builder.getOrCreate()
        results = run_ingestion(config, spark=spark, dry_run=False)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    for result in results:
        print(
            f"[{result['entity']}] wrote {result['row_count']} row(s) to "
            f"{result['target_table']} (mode={result['write_mode']})."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
