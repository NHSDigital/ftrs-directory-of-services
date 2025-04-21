import logging
from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path
from typing import Annotated

import numpy as np
import pandas as pd
from pipeline.validators import validate_paths
import pyarrow as pa
import pyarrow.parquet as pq
from typer import Option

from pipeline.common import Constants
from pipeline.db_utils import (
    get_gp_endpoints,
    get_gp_practices,
    get_serviceendpoints_columns_count,
    get_services_columns_count,
    get_services_size,
)
from pipeline.s3_utils.s3_bucket_wrapper import BucketWrapper


def format_endpoints(gp_practice_endpoints: pd.DataFrame) -> pd.DataFrame:
    """Format the endpoints DataFrame."""
    endpoint_columns = [
        "id",
        "endpointorder",
        "transport",
        "format",
        "interaction",
        "businessscenario",
        "address",
        "comment",
        "iscompressionenabled",
    ]
    grouped_endpoints = gp_practice_endpoints.groupby("serviceid")[endpoint_columns]
    endpoint_data = (
        grouped_endpoints.apply(lambda group: group.to_dict(orient="records"))
        .reset_index()
        .rename(columns={0: "endpoints"})
    )

    return pd.DataFrame(
        data=endpoint_data,
        columns=["serviceid", "endpoints"],
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
    result = gp_practice_df.merge(grouped_endpoints, on="serviceid", how="left").drop(
        columns=["serviceid"]
    ).fillna(np.nan).replace([np.nan], [None])
    # @marksp: The fillna, and replace are to fix my pandas default to NaN 
    #   You can't just default to None despite checking a number of places, 
    #   so I needed to default to soemthing else first

    # Force all null values in the endpoints column to be empty lists
    for row in result.loc[result.endpoints.isnull(), "endpoints"].index:
        result.at[row, "endpoints"] = []

    return result


def extract_gp_practices(db_uri: str) -> pd.DataFrame:
    gp_practice_df = get_gp_practices(db_uri)
    gp_practice_endpoints_df = get_gp_endpoints(db_uri)

    grouped_endpoints = format_endpoints(gp_practice_endpoints_df)
    gp_practice_extract = merge_gp_practice_with_endpoints(
        gp_practice_df, grouped_endpoints
    )
    logging_gp_practice_metrics(gp_practice_extract, db_uri)
    return gp_practice_extract


def store_local(
    gp_practice_extract: pd.DataFrame,
    output_path: Path,
    clone_timestamp: str,
    file_name: str,
) -> None:
    gp_practice_extract.to_parquet(
        output_path / Constants.GP_PRACTICE_EXTRACT_FILE,
        engine="pyarrow",
        index=False,
        compression="zstd",
    )


def convert_to_parquet_buffer(gp_practice_extract: pd.DataFrame) -> BytesIO:
    buffer = BytesIO()
    table = pa.Table.from_pandas(gp_practice_extract)
    pq.write_table(table, buffer)
    return buffer


def store_s3(gp_practice_extract: pd.DataFrame, s3_output_uri: str) -> None:
    buffer = convert_to_parquet_buffer(gp_practice_extract)
    buffer.seek(0)  # Reset buffer position
    bucket_wrapper = BucketWrapper(s3_output_uri)
    bucket_wrapper.s3_upload_file(buffer, "dos-gp-practice-extract.parquet")


def extract(
    db_uri: Annotated[str, Option(..., help="URI to connect to the source database")],
    output_path: Annotated[
        Path | None, Option(..., help="Path to save the extracted data")
    ] = None,
    s3_output_uri: Annotated[
        str | None,
        Option(
            ...,
            help="Path to save the extracted data in S3, in the format s3://<s3_bucket_name>/<s3_bucket_path>",
        ),
    ] = None,
) -> None:
    """
    Extract GP practice data from the source database and save it to the specified path.
    """
    # Validate output path is correct, would use decarator but Typer is blocking it
    validate_paths(output_path, s3_output_uri, 'output_path', 's3_output_uri')

    if output_path is not None:
        output_path = output_path / datetime.now(UTC).strftime("%Y-%m-%dT%H-%M-%S")
        output_path.mkdir(parents=True, exist_ok=True)

    logging.info(f"Extracting data to {output_path}")
    extract_gp_practice_df = extract_gp_practices(db_uri)
    clone_timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")

    if output_path:
        logging.info(f"Extracting data to {output_path}")
        output_path.mkdir(parents=True, exist_ok=True)
        store_local(
            extract_gp_practice_df,
            output_path,
            clone_timestamp,
            "dos-gp-practice-extract",
        )

    if s3_output_uri:
        logging.info(f"Extracting data to {s3_output_uri}")
        store_s3(extract_gp_practice_df, s3_output_uri)
