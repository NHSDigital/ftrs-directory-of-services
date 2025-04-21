import logging
from datetime import datetime
from pathlib import Path
from typing import Annotated

import pandas as pd
from ftrs_data_layer.models import Organisation
from typer import Option

from pipeline.common import Constants
from pipeline.validators import validate_paths


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
    input_path: Annotated[
        Path | None, Option(..., help="Path to read the extracted data")
    ] = None,
    s3_input_uri: Annotated[
        str | None,
        Option(
            ...,
            help="Path to save the extracted data in S3, in the format s3://<s3_bucket_name>/<s3_bucket_path>",
        ),
    ] = None,
    output_path: Path = Option(..., help="Path to save the transformed data"),
) -> None:
    """
    Transform the GP practice data from the input path and save it to the output path.
    """
    # Validate output path is correct, would use decarator but Typer is blocking it
    validate_paths(input_path, s3_input_uri, "input_path", "s3_input_uri")

    output_path.mkdir(parents=True, exist_ok=True)
    current_timestamp = datetime.now()

    if input_path is not None:
        logging.info(
            f"Transforming data from {input_path}/{Constants.GP_PRACTICE_EXTRACT_FILE} to {output_path}"
        )
        extract_dataframe = pd.read_parquet(
            input_path / Constants.GP_PRACTICE_EXTRACT_FILE
        )
    else:
        logging.info(
            f"Transforming data from {s3_input_uri}/{Constants.GP_PRACTICE_EXTRACT_FILE} to {output_path}"
        )
        extract_dataframe = pd.read_parquet(
            f"{s3_input_uri}/{Constants.GP_PRACTICE_EXTRACT_FILE}"
        )

    gp_practices_df = transform_gp_practices(extract_dataframe, current_timestamp)

    gp_practices_df.to_parquet(
        output_path / Constants.GP_PRACTICE_TRANSFORM_FILE,
        engine="pyarrow",
        index=False,
        compression="zstd",
    )

    return {Constants.GP_PRACTICE_TRANSFORM: gp_practices_df}
