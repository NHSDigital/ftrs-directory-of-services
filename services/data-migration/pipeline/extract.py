import json
import logging
from typing import Annotated

import boto3
import numpy as np
import pandas as pd
from typer import Option

from pipeline.utils.db_config import DatabaseConfig
from pipeline.utils.dos_db import (
    get_gp_endpoints,
    get_gp_practices,
    get_serviceendpoints_columns_count,
    get_services_columns_count,
    get_services_size,
)
from pipeline.utils.file_io import (
    write_parquet_file,
)
from pipeline.utils.secret_wrapper import GetSecretWrapper
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

    logging.info(f"Percentage of service profiles: {service_profiles_percentage}%")
    logging.info(f"Percentage of all data fields: {data_fields_percentage}%")


def merge_gp_practice_with_endpoints(
    gp_practice_df: pd.DataFrame, grouped_endpoints: pd.DataFrame
) -> pd.DataFrame:
    # We use the no_silent_downcasting option, with replace and infer objects to ensure that all possible
    #   nullables are outputted as NoneTypes, and not NaN etc
    with pd.option_context("future.no_silent_downcasting", True):
        result = (
            gp_practice_df.merge(grouped_endpoints, on="serviceid", how="left")
            .drop(columns=["serviceid"])
            .replace([np.nan], [None])
            .infer_objects(copy=False)
        )

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

    logging.info(f"Extracting data to {output_path}")
    extract_gp_practice_df = extract_gp_practices(db_uri)

    write_parquet_file(path_type, output_path, extract_gp_practice_df)
    logging.info("Data extraction completed successfully.")


def lambda_handler(event: dict, context: object) -> dict[str, any] | None:
    """
    AWS Lambda handler function.
    Parameters:
    - event: dict, contains the event data passed to the function.
    - context: object, provides runtime information to the handler.
    Returns:
    - dict: Response object with status code and body.
    """
    try:
        print("Received event:", json.dumps(event))

        client = boto3.client("secretsmanager")
        wrapper = GetSecretWrapper(client)
        db_credentials = wrapper.get_secret(DatabaseConfig.SOURCE_DB_CREDENTIALS)
        db_credentials_dict = json.loads(db_credentials)

        db_config = DatabaseConfig(
            host=db_credentials_dict["host"],
            port=db_credentials_dict["port"],
            user=db_credentials_dict["username"],
            password=db_credentials_dict["password"],
            db_name=db_credentials_dict["dbname"],
        )

        extract(
            db_config.get_db_uri(),
            s3_output_uri=event["s3_output_uri"],
        )

    except Exception as e:
        print("Error:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal Server Error"}),
        }
