import io
import logging
from datetime import datetime, UTC
from pathlib import Path

import pandas as pd
from typing import Annotated

from pipeline.exceptions import InvalidArgumentsError, S3BucketAccessError
from ftrs_data_layer.models import Organisation
from typer import Option

from pipeline.common import Constants
from pipeline.s3_utils.s3_bucket_wrapper import BucketWrapper


def transform_gp_practices(
    df: pd.DataFrame, current_timestamp: datetime
) -> pd.DataFrame:
    if df.empty:
        err_msg = "No data found in the input DataFrame"
        raise ValueError(err_msg)

    gp_practices = []
    for _, row in df.iterrows():
        organisation = Organisation.from_dos(
            data=row,
            created_datetime=current_timestamp,
            updated_datetime=current_timestamp,
        )
        gp_practices.append({"organisation": organisation.model_dump(mode="json")})

    return pd.DataFrame(gp_practices)


def transform(
    input_path: Path = Option(..., help="Path to read the extracted data"),
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
    Transform the GP practice data from the input path and save it to the output path.
    """
    if not (output_path or s3_output_uri):
       logging.error("Neither output_path nor s3_output_uri is provided.")
       raise InvalidArgumentsError()
    elif output_path and s3_output_uri:
      logging.error("Provide only one valid argument: either output path or s3 uri.")
      raise InvalidArgumentsError()

    current_timestamp = datetime.now()
    extract_dataframe = pd.read_parquet(input_path / Constants.GP_PRACTICE_EXTRACT_FILE)
    gp_practices_df = transform_gp_practices(extract_dataframe, current_timestamp)

    if s3_output_uri and (s3_output_uri != "" or s3_output_uri != "None"):
        put_object_to_s3(s3_output_uri,input_path, gp_practices_df)
    else:
        output_path = output_path / datetime.now(UTC).strftime("%Y-%m-%dT%H-%M-%S")
        output_path.mkdir(parents=True, exist_ok=True)
        logging.info(f"Transforming data from {input_path} to {output_path}")
        gp_practices_df.to_parquet(
            output_path / Constants.GP_PRACTICE_TRANSFORM_FILE,
            engine="pyarrow",
            index=False,
            compression="zstd",
        )
    return {Constants.GP_PRACTICE_TRANSFORM: gp_practices_df}

def put_object_to_s3(
    s3_output_uri: str, input_path: Path, transform_gp_dataframe: pd.DataFrame
) -> None:
    """
    Upload the transformed data to S3.
    """
    s3bucketObject = BucketWrapper(s3_output_uri)
    if s3bucketObject.s3_bucket_exists():
        logging.info(
            f"Transforming data from {input_path} to S3 bucket {s3_output_uri}"
        )
        gpBuffer = io.BytesIO()
        transform_gp_dataframe.to_parquet(
            gpBuffer, engine="pyarrow", index=False, compression="zstd"
        )
        gpBuffer.seek(0)
        fileName = f"{datetime.now(UTC).strftime("%Y-%m-%dT%H-%M-%S")}/{Constants.GP_PRACTICE_TRANSFORM_FILE}"
        s3bucketObject.s3_upload_file(
            gpBuffer,fileName
        )
        logging.info(f"Data transformed and uploaded to S3 bucket {s3_output_uri}/{fileName}")
    else:
        logging.error(
            f"Bucket {s3_output_uri} does not exist or you don't have access to it."
        )
        raise S3BucketAccessError()
