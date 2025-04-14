import logging
from pathlib import Path
from typing import Type

import pandas as pd
from ftrs_data_layer.models import Organisation
from ftrs_data_layer.repository.dynamodb import (
    DocumentLevelRepository,
    DynamoDBRepository,
)
from typer import Option

from pipeline.common import Constants, TargetEnvironment, get_table_name


def _retrieve_gp_practice_data(
    input_path: Path,
) -> None:
    """
    Load the GP practice data from the specified input path.
    """
    file_path = input_path / Constants.GP_PRACTICE_TRANSFORM_FILE
    if not file_path.exists() or not file_path.is_file():
        error_msg = f"File not found: {file_path}"
        raise FileNotFoundError(error_msg)

    logging.info(f"Loading data from {file_path}")
    return pd.read_parquet(file_path).to_dict(orient="records")


def _load_organisations(
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
    input_path: Path = Option(..., help="Path to load the extracted data"),
    endpoint_url: str | None = Option(None, help="URL to connect to local DynamoDB"),
) -> None:
    """
    Load the extracted data into the database.
    """
    gp_data = _retrieve_gp_practice_data(input_path)
    _load_organisations(
        input_df=gp_data,
        table_name=get_table_name("organisation", env.value, workspace),
        endpoint_url=endpoint_url,
    )
