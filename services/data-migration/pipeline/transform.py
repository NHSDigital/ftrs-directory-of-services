import logging
from pathlib import Path


def transform(input_path: Path, output_path: Path) -> None:
    logging.info(f"Transforming data from {input_path} to {output_path}")
    logging.error("Not implemented yet")


def main(args: list[str] | None = None) -> None:
    import argparse

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Extract data from source")
    parser.add_argument(
        "--input-path", type=Path, required=True, help="Path to read the extracted data"
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        required=True,
        help="Path to save the extracted data",
    )
    args = parser.parse_args(args)
    transform(args.input_path, args.output_path)
