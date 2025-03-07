import logging
from pathlib import Path


def load(db_uri: str, input_path: Path) -> None:
    logging.info(f"Loading data from {input_path}")
    logging.error("Not implemented yet")


def main(args: list[str] | None = None) -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Load data to destination")
    parser.add_argument(
        "--input-path", type=Path, required=True, help="Path to load the extracted data"
    )
    parser.add_argument(
        "--db-uri", type=str, required=True, help="URI to connect to the database"
    )
    args = parser.parse_args(args)
    load(args.db_uri, args.input_path)
