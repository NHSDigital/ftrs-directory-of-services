import logging
from datetime import datetime
from pathlib import Path

import pandas as pd

from pipeline.db_utils import (
    get_gp_endpoints,
    get_gp_practices,
    get_serviceendpoints_columns_count,
    get_services_columns_count,
    get_services_size,
)


def format_endpoints(gp_practice_endpoints: pd.DataFrame) -> pd.DataFrame:
    # combining all the endpoint columns into one column
    return (
        gp_practice_endpoints.groupby(["serviceid"])[
            [
                "id",
                "endpointorder",
                "transport",
                "format",
                "interaction",
                "businessscenario",
                "address",
                "comment",
                "iscompressionenabled",
                "serviceid",
            ]
        ]
        .apply(
            lambda x: x.apply(
                lambda row: {
                    "endpointid": row["id"],
                    "endpointorder": row["endpointorder"],
                    "transport": row["transport"],
                    "format": row["format"],
                    "interaction": row["interaction"],
                    "businessscenario": row["businessscenario"],
                    "address": row["address"],
                    "comment": row["comment"],
                    "iscompressionenabled": row["iscompressionenabled"],
                    "serviceid": row["serviceid"],
                },
                axis=1,
            ).tolist()
        )
        .reset_index(name="endpoints")
    )


def calculate_service_profiles_percentage(
    gp_practice_extract_size: int, services_size: int
) -> float:
    return round(gp_practice_extract_size / services_size * 100, 2)


def calculate_data_fields_percentage(
    gp_practice_extract_column: int,
    services_columns: int,
    serviceendpoints_columns: int,
) -> float:
    return round(
        gp_practice_extract_column
        / (services_columns + serviceendpoints_columns)
        * 100,
        2,
    )


def logging_gp_practice_metrics(gp_practice_extract: pd.DataFrame, db_uri: str) -> None:
    services_size = get_services_size(db_uri)
    gp_practice_extract_size = len(gp_practice_extract)
    service_profiles_percentage = calculate_service_profiles_percentage(
        gp_practice_extract_size, services_size
    )

    services_columns = get_services_columns_count(db_uri)
    serviceendpoints_columns = get_serviceendpoints_columns_count(db_uri)
    gp_practice_extract_column = gp_practice_extract.shape[1]
    data_fields_percentage = calculate_data_fields_percentage(
        gp_practice_extract_column, services_columns, serviceendpoints_columns
    )

    logging.info(f"Percentage of service profiles: {service_profiles_percentage}%")
    logging.info(f"Percentage of all data fields: {data_fields_percentage}%")


def merge_gp_practice_with_endpoints(
    gp_practice_df: pd.DataFrame, grouped_endpoints: pd.DataFrame
) -> pd.DataFrame:
    return gp_practice_df.merge(grouped_endpoints, on="serviceid", how="left").drop(
        columns=["serviceid"]
    )


def extract_gp_practice(db_uri: str, output_path: Path, clone_timestamp: str) -> None:
    gp_practice_df = get_gp_practices(db_uri)
    gp_practice_endpoints_df = get_gp_endpoints(db_uri)

    grouped_endpoints = format_endpoints(gp_practice_endpoints_df)
    gp_practice_extract = merge_gp_practice_with_endpoints(
        gp_practice_df, grouped_endpoints
    )

    gp_practice_extract.to_parquet(
        output_path / f"dos-gp-practice-extract-{clone_timestamp}.parquet",
        engine="pyarrow",
        index=False,
        compression="zstd",
    )

    logging_gp_practice_metrics(gp_practice_extract, db_uri)


def extract(db_uri: str, output_path: Path) -> None:
    logging.info(f"Extracting data to {output_path}")
    output_path.mkdir(parents=True, exist_ok=True)
    clone_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    extract_gp_practice(db_uri, output_path, clone_timestamp)


def main(args: list[str] | None = None) -> None:
    import argparse

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

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
