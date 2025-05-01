import logging
from enum import Enum
from typing import Annotated

import pandas as pd
from ftrs_data_layer.models import DBModel, HealthcareService, Location, Organisation
from ftrs_data_layer.repository.dynamodb import DocumentLevelRepository
from typer import Option

from pipeline.constants import TargetEnvironment
from pipeline.utils.file_io import read_parquet_file
from pipeline.utils.validators import validate_path


class TABLE(Enum):
    ORGANISATION = "organisation"
    SERVICE = "healthcare-service"
    LOCATION = "location"


def get_model(table: TABLE) -> DBModel:
    match table:
        case TABLE.ORGANISATION:
            return Organisation
        case TABLE.SERVICE:
            return HealthcareService
        case TABLE.LOCATION:
            return Location


def get_table_name(entity_type: str, env: str, workspace: str | None = None) -> str:
    """
    Build a DynamoDB table name based on the entity type, environment, and optional workspace.
    """
    table_name = f"ftrs-dos-db-{env}-{entity_type}"
    if workspace:
        table_name = f"{table_name}-{workspace}"

    return table_name


def save_to_table(
    input_df: pd.DataFrame,
    table: TABLE,
    table_name: str,
    endpoint_url: str | None = None,
) -> None:
    """
    Load the organisations into the specified table.
    """
    repository = DocumentLevelRepository[table.value](
        table_name=table_name,
        model_cls=Organisation,
        endpoint_url=endpoint_url,
    )

    model = get_model(table)

    logging.info(f"Loading {len(input_df)} {table.value}s into {table.value}")
    count = 0
    for row in input_df.to_dict(orient="records"):
        if table.value in row:
            item = model.model_validate(row[table.value])
            repository.create(item)
            count += 1

    logging.info(f"Loaded {count} {table.value}s into the database.")


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
    path_type, input_path = validate_path(input, should_file_exist=True)
    gp_practice_df = read_parquet_file(path_type, input_path)

    for table in [TABLE.ORGANISATION, TABLE.LOCATION, TABLE.SERVICE]:
        save_to_table(
            input_df=gp_practice_df,
            table=table,
            table_name=get_table_name(table.value, env.value, workspace),
            endpoint_url=endpoint_url,
        )

    logging.info(
        f"Data loaded successfully into {env.value} environment (workspace: {workspace or 'default'})"
    )
