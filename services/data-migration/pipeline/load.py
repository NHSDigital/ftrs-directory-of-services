import os
from enum import Enum
from typing import Annotated

import pandas as pd
from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import MigrationETLPipelineLogBase
from ftrs_data_layer.models import DBModel, HealthcareService, Location, Organisation
from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository
from typer import Option

from pipeline.constants import TargetEnvironment
from pipeline.utils.file_io import read_parquet_file
from pipeline.utils.validators import validate_path

load_logger = Logger.get(service="load")


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
    table_name = f"ftrs-dos-{env}-database-{entity_type}"
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
    repository = AttributeLevelRepository[table.value](
        table_name=table_name,
        model_cls=Organisation,
        endpoint_url=endpoint_url,
    )

    model = get_model(table)
    len_input_df = len(input_df)
    table_value = table.value
    load_logger.log(
        MigrationETLPipelineLogBase.ETL_LOAD_001,
        len_input_df=len_input_df,
        table_value=table_value,
    )
    count = 0
    for row in input_df.to_dict(orient="records"):
        if table.value in row:
            item = model.model_validate(row[table.value])
            repository.create(item)
            count += 1

    load_logger.log(
        MigrationETLPipelineLogBase.ETL_LOAD_002, count=count, table_value=table_value
    )


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

    env_value = env.value
    workspace_value = workspace or "default"
    load_logger.log(
        MigrationETLPipelineLogBase.ETL_LOAD_003,
        env_value=env_value,
        workspace_value=workspace_value,
    )


def lambda_handler(event: dict, context: dict) -> None:
    """
    AWS Lambda entrypoint for loading data.
    This function will be triggered by an S3 event.
    """
    s3_bucket = event["Records"][0]["s3"]["bucket"]["name"]
    s3_key = event["Records"][0]["s3"]["object"]["key"]

    s3_input_uri = f"s3://{s3_bucket}/{s3_key}"

    env = os.environ.get("ENVIRONMENT")
    workspace = os.environ.get("WORKSPACE")

    load(
        input=s3_input_uri,
        env=TargetEnvironment(env),
        workspace=workspace,
    )
