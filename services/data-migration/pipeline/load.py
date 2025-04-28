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


from pipeline.constants import Constants, TargetEnvironment
from pipeline.utils.validators import validate_path
from pipeline.utils.file_io import read_parquet_file


def get_table_name(entity_type: str, env: str, workspace: str | None = None) -> str:
    """
    Build a DynamoDB table name based on the entity type, environment, and optional workspace.
    """
    table_name = f"ftrs-dos-db-{env}-{entity_type}"
    if workspace:
        table_name = f"{table_name}-{workspace}"

    return table_name


def load_organisations(
    input_df: pd.DataFrame,
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
    for row in input_df.to_dict(orient="records"):
        organisation = Organisation.model_validate(row["organisation"])
        org_repository.create(organisation)


def load(
    input: Annotated[str, Option(help="File or S3 path to the transformed data file")],
    env: Annotated[TargetEnvironment, Option(help="Environment to load the data into")],
    workspace: Annotated[
        str | None, Option(help="Workspace to load the data into")
    ] = None,
    endpoint_url: Annotated[
        str | None, Option(help="URL to connect to local DynamoDB")
    ] = None,
) -> None:
    """
    Load the extracted data into the database.
    """
    path_type, input_path = validate_path(input)
    gp_practice_df = read_parquet_file(path_type, input_path)

    load_organisations(
        input_df=gp_practice_df,
        table_name=get_table_name("organisation", env.value, workspace),
        endpoint_url=endpoint_url,
    )

    logging.info(
        f"Data loaded successfully into {env.value} environment (workspace: {workspace or 'default'})"
    )
