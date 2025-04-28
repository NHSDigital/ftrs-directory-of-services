import logging
from datetime import UTC, datetime
from typing import Annotated

import pandas as pd
from ftrs_data_layer.models import Organisation
from typer import Option

from pipeline.constants import (
    Constants,
)
from pipeline.utils.file_io import (
    read_parquet_file,
    write_parquet_file,
)
from pipeline.utils.validators import validate_path


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
    input_type, input_path = validate_path(input)
    output_type, output_path = validate_path(output)

    logging.info(f"Transforming data from {input_path} to {output_path}")

    extract_df = read_parquet_file(input_type, input_path)
    current_timestamp = datetime.now(UTC)
    gp_practices_df = transform_gp_practices(extract_df, current_timestamp)

    write_parquet_file(output_type, output_path, gp_practices_df)

    logging.info("Transform completed successfully.")
    return {Constants.GP_PRACTICE_TRANSFORM: gp_practices_df}
