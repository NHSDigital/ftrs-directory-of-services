import logging
from pathlib import Path


def extract(db_uri: str, output_path: Path) -> None:
    logging.info(f"Extracting data to {output_path}")
    logging.error("Not implemented yet")


def main(args: list[str] | None = None) -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Extract data from source")
    parser.add_argument(
        "--db-uri", type=str, required=True, help="URI to connect to the database"
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        required=True,
        help="Path to save the extracted data",
    )
    args = parser.parse_args(args)
    extract(args.db_uri, args.output_path)
