import logging
from pathlib import Path
from typing import Annotated, Type

import pandas as pd
from ftrs_data_layer.models import Organisation
from ftrs_data_layer.repository.dynamodb import (
    DocumentLevelRepository,
    DynamoDBRepository,
)
from typer import Option

from pipeline.common import (
    Constants,
    TargetEnvironment,
    get_parquet_path,
    get_table_name,
)
from pipeline.extract import validate_paths


def retrieve_gp_practice_data(
    input_path: Path,
) -> None:
    """
    Load the GP practice data from the specified input path.
    """
    logging.info(f"Loading data from {input_path}")
    return pd.read_parquet(input_path).to_dict(orient="records")


def load_organisations(
    input_df: list[pd.Series],
    table_name: str,
    endpoint_url: str | None = None,
    repository_cls: Type[DynamoDBRepository] = DocumentLevelRepository,
) -> None:
    """
    Load the organisations into the specified table.
    """
    org_repository = repository_cls[Organisation](
        table_name=table_name,
        model_cls=Organisation,
        endpoint_url=endpoint_url,
    )

    logging.info(f"Loading {len(input_df)} organisations into {table_name}")

    count = 0
    for row in input_df:
        organisation = Organisation.model_validate(row["organisation"])
        org_repository.create(organisation)
        count += 1

    logging.info(f"Loaded {count} organisations into the database.")


def load(
    env: TargetEnvironment = Option(help="Environment to load the data into"),
    workspace: str | None = Option(None, help="Workspace to load the data into"),
    input_path: Annotated[
        Path | None, Option(..., help="Path to load the transformed data")
    ] = None,
    s3_input_uri: Annotated[
        str | None,
        Option(
            ...,
            help="Path to load the transformed data in S3, in the format s3://<s3_bucket_name>/<s3_bucket_path>",
        ),
    ] = None,
    endpoint_url: str | None = Option(None, help="URL to connect to local DynamoDB"),
) -> None:
    """
    Load the extracted data into the database.
    """
    validate_paths(input_path, s3_input_uri)

    parquet_path = get_parquet_path(
        input_path, s3_input_uri, Constants.GP_PRACTICE_TRANSFORM_FILE
    )

    gp_data = retrieve_gp_practice_data(parquet_path)
    load_organisations(
        input_df=gp_data,
        table_name=get_table_name("organisation", env.value, workspace),
        endpoint_url=endpoint_url,
    )
