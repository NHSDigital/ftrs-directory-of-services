from datetime import UTC, datetime
from typing import Annotated

import pandas as pd
from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import MigrationETLPipelineLogBase
from ftrs_data_layer.models import HealthcareService, Location, Organisation
from typer import Option

from pipeline.utils.file_io import (
    read_parquet_file,
    write_parquet_file,
)
from pipeline.utils.validators import validate_path

transform_logger = Logger.get(service="transform")


def transform_gp_practices(
    df: pd.DataFrame, current_timestamp: datetime
) -> pd.DataFrame:
    if df.empty:
        err_msg = "No data found in the input DataFrame"
        raise ValueError(err_msg)

    # Replace pandas.NA with None to avoid Pydantic validation errors
    df = df.replace({pd.NA: None})

    gp_practices = []
    for _, row in df.iterrows():
        organisation = Organisation.from_dos(
            data=row,
            created_datetime=current_timestamp,
            updated_datetime=current_timestamp,
        )

        location = Location.from_dos(
            data=row,
            created_datetime=current_timestamp,
            updated_datetime=current_timestamp,
            organisation_id=organisation.id,
        )

        service = HealthcareService.from_dos(
            data=row,
            created_datetime=current_timestamp,
            updated_datetime=current_timestamp,
            organisation_id=organisation.id,
            location_id=location.id,
        )

        gp_practices.append(
            {
                "organisation": organisation.model_dump(mode="json"),
                "healthcare-service": service.model_dump(mode="json"),
                "location": location.model_dump(mode="json"),
            }
        )

    return pd.DataFrame(gp_practices)


def transform(
    input: Annotated[
        str,
        Option(help="File or S3 path to read the extracted data"),
    ],
    output: Annotated[
        str,
        Option(..., help="File or S3 path to save the transformed data"),
    ],
) -> None:
    """
    Transform the GP practice data from the input path and save it to the output path.
    """
    input_type, input_path = validate_path(input, should_file_exist=True)
    output_type, output_path = validate_path(output, should_file_exist=False)

    transform_logger.log(
        MigrationETLPipelineLogBase.ETL_TRANSFORM_001,
        input_path=input_path,
        output_path=output_path,
    )

    extract_df = read_parquet_file(input_type, input_path)
    current_timestamp = datetime.now(UTC)
    gp_practices_df = transform_gp_practices(extract_df, current_timestamp)

    write_parquet_file(output_type, output_path, gp_practices_df)

    transform_logger.log(MigrationETLPipelineLogBase.ETL_TRANSFORM_002)


def lambda_handler(event: dict, context: any) -> None:
    """
    AWS Lambda entrypoint for transforming data.
    This function will be triggered by an S3 event.
    """

    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"]
    s3_input_uri = f"s3://{bucket}/{key}"
    s3_output_uri = f"s3://{bucket}/transform/transform.parquet"

    transform(input=s3_input_uri, output=s3_output_uri)
