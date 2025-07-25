from typing import Annotated

import numpy as np
import pandas as pd
from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import MigrationETLPipelineLogBase
from typer import Option

from pipeline.utils.db_config import DatabaseConfig
from pipeline.utils.dos_db import (
    get_clinical_codes,
    get_gp_day_opening_times,
    get_gp_endpoints,
    get_gp_practices,
    get_gp_specified_opening_times,
    get_serviceendpoints_columns_count,
    get_services_columns_count,
    get_services_size,
)
from pipeline.utils.file_io import (
    write_parquet_file,
)
from pipeline.utils.opening_times import (
    format_openingtimes,
    merge_gp_practice_with_openingtimes,
)
from pipeline.utils.secret_utils import get_secret
from pipeline.utils.validators import validate_path


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

    extract_logger = Logger.get(service="extract")
    extract_logger.log(
        MigrationETLPipelineLogBase.ETL_EXTRACT_002,
        service_profiles_percentage=service_profiles_percentage,
    )
    extract_logger.log(
        MigrationETLPipelineLogBase.ETL_EXTRACT_003,
        data_fields_percentage=data_fields_percentage,
    )


def merge_gp_practice_with_endpoints(
    gp_practice_df: pd.DataFrame, grouped_endpoints: pd.DataFrame
) -> pd.DataFrame:
    # We use the no_silent_downcasting option, with replace and infer objects to ensure that all possible
    #   nullables are outputted as NoneTypes, and not NaN etc
    with pd.option_context("future.no_silent_downcasting", True):
        result = (
            gp_practice_df.merge(grouped_endpoints, on="serviceid", how="left")
            .replace([np.nan], [None])
            .infer_objects(copy=False)
        )

    # Force all null values in the endpoints column to be empty lists
    for row in result.loc[result.endpoints.isnull(), "endpoints"].index:
        result.at[row, "endpoints"] = []

    return result


def extract_gp_practices(db_uri: str) -> pd.DataFrame:
    gp_practice_df = get_gp_practices(db_uri)

    # Extract endpoint information
    gp_practice_endpoints_df = get_gp_endpoints(db_uri)
    grouped_endpoints = format_endpoints(gp_practice_endpoints_df)
    gp_practice_extract = merge_gp_practice_with_endpoints(
        gp_practice_df, grouped_endpoints
    )

    # Extract Opening Time information
    gp_practice_day_openingtime_df = get_gp_day_opening_times(db_uri)
    gp_practice_specified_openingtime_df = get_gp_specified_opening_times(db_uri)
    grouped_openingtimes = format_openingtimes(
        gp_practice_day_openingtime_df, gp_practice_specified_openingtime_df
    )
    clinical_codes_df = get_clinical_codes(db_uri)
    gp_practice_extract = gp_practice_extract.merge(
        clinical_codes_df, on="serviceid", how="left"
    )
    gp_practice_extract = merge_gp_practice_with_openingtimes(
        gp_practice_extract, grouped_openingtimes
    )
    logging_gp_practice_metrics(gp_practice_extract, db_uri)
    return gp_practice_extract


def extract(
    db_uri: Annotated[str, Option(..., help="URI to connect to the source database")],
    output: Annotated[
        str,
        Option(..., help="S3 URI or file path to save the extracted data"),
    ],
) -> None:
    """
    Extract GP practice data from the source database and save it to the specified path.
    """
    path_type, output_path = validate_path(output, should_file_exist=False)
    extract_logger = Logger.get(service="extract")

    extract_logger.log(
        MigrationETLPipelineLogBase.ETL_EXTRACT_001, output_path=output_path
    )
    extract_gp_practice_df = extract_gp_practices(db_uri)

    write_parquet_file(path_type, output_path, extract_gp_practice_df)
    extract_logger.log(MigrationETLPipelineLogBase.ETL_EXTRACT_004)


def lambda_handler(event: dict, context: object) -> dict[str, any] | None:
    """
    AWS Lambda handler function.
    Parameters:
    - event: dict, contains the event data passed to the function.
    - context: object, provides runtime information to the handler.
    Returns:
    - dict: Response object with status code and body.
    """
    db_credentials = get_secret(
        DatabaseConfig.source_db_credentials(), transform="json"
    )
    db_config = DatabaseConfig(**db_credentials)

    extract(
        db_config.connection_string,
        output=event["s3_output_uri"],
    )
