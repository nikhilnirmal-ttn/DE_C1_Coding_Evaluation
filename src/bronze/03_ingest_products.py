"""Bronze ingestion for products.csv."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from bronze_common import (
    BronzeConfig,
    default_config,
    format_dry_run_report,
    ingest_entity_to_bronze,
)

ENTITY = "products"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ingest products.csv into de_c1_coding_evaluation.bronze.bronze_products."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate the CSV locally without writing to Delta.",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Directory containing products.csv (default: project data/).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = default_config() if args.data_dir is None else BronzeConfig(data_dir=args.data_dir)

    try:
        result = ingest_entity_to_bronze(ENTITY, config, dry_run=args.dry_run)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.dry_run:
        print(format_dry_run_report([result]))
    else:
        print(
            f"Wrote {result['row_count']} row(s) to {result['target_table']} "
            f"using mode={result['write_mode']}."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
