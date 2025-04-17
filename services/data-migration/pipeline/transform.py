import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
from ftrs_data_layer.models import Organisation
from typer import Option

from pipeline.common import Constants


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
    output_path: Path = Option(..., help="Path to save the transformed data"),
) -> None:
    """
    Transform the GP practice data from the input path and save it to the output path.
    """
    output_path.mkdir(parents=True, exist_ok=True)

    logging.info(f"Transforming data from {input_path} to {output_path}")
if not (output_path or s3_output_uri) or (output_path and s3_output_uri):
    logging.error("Provide only one valid argument: either output path or s3 uri.")
    raise InvalidArgumentsError()
    current_timestamp = datetime.now()
    extract_dataframe = pd.read_parquet(input_path / Constants.GP_PRACTICE_EXTRACT_FILE)
    gp_practices_df = transform_gp_practices(extract_dataframe, current_timestamp)

    gp_practices_df.to_parquet(
        output_path / Constants.GP_PRACTICE_TRANSFORM_FILE,
        engine="pyarrow",
        index=False,
        compression="zstd",
    )

    return {Constants.GP_PRACTICE_TRANSFORM: gp_practices_df}
