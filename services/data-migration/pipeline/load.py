import logging
from pathlib import Path
from typing import Annotated

import pandas as pd
from ftrs_data_layer.models import HealthcareService, Organisation
from ftrs_data_layer.repository.dynamodb import (
    DocumentLevelRepository,
)
from typer import Option

from pipeline.common import (
    TABLE,
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


def load_table(
    input_df: list[pd.Series],
    table: TABLE,
    table_name: str,
    endpoint_url: str | None = None,
) -> None:
    """
    Load the items into the specified table.
    """
    match table:
        case TABLE.ORGANISATION:
            model = Organisation
        case TABLE.SERVICE:
            model = HealthcareService

    repository = DocumentLevelRepository[model](
        table_name=table_name,
        model_cls=model,
        endpoint_url=endpoint_url,
    )

    # Not all records will contain all tables (e.g. As a service may share the org or location with another service)
    input_df = [item for item in input_df if table in item.keys()]

    logging.info(f"Loading {len(input_df)} {table}s into {table}")

    count = 0
    for row in input_df:
        item = model.model_validate(row[table])
        repository.create(item)
        count += 1

    logging.info(f"Loaded {count} {table}s into the database.")


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

    path = get_parquet_path(input_path, s3_input_uri, "gp_practices.parquet")

    org_data = retrieve_gp_practice_data(path)

    for table in [TABLE.ORGANISATION, TABLE.SERVICE]:
        load_table(
            input_df=org_data,
            table=table,
            table_name=get_table_name(table, env.value, workspace),
            endpoint_url=endpoint_url,
        )
