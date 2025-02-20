import logging
from pathlib import Path


def load(db_uri: str, input_path: Path) -> None:
    logging.info(f"Loading data from {input_path}")
    logging.error("Not implemented yet")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Load data to destination")
    parser.add_argument(
        "--input-path", type=Path, help="Path to load the extracted data"
    )
    parser.add_argument("--db-uri", type=str, help="URI to connect to the database")
    args = parser.parse_args()
    load(args.db_uri, args.input_path)
