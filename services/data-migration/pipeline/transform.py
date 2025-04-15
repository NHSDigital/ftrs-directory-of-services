import logging
from datetime import datetime
from pathlib import Path
from typing import Dict
from uuid import UUID, uuid4

import pandas as pd
from ftrs_data_layer.models import Endpoint, Organisation
from typer import Option

from pipeline.common import Constants


def create_organisation(row: pd.Series, current_timestamp: datetime) -> Organisation:
    organisation_id = uuid4()

    return Organisation(
        id=organisation_id,
        identifier_ODS_ODSCode=row["odscode"],
        active=True,
        name=row["name"],
        telecom=None,
        type=row["type"],
        createdBy="ROBOT",
        createdDateTime=current_timestamp,
        modifiedBy="ROBOT",
        modifiedDateTime=current_timestamp,
        endpoints=[],
    )


def create_endpoint(
    endpoint_data: Dict[str, str], organisation_id: UUID, current_timestamp: str
) -> Endpoint:
    payload_type = (
        None
        if endpoint_data.get("transport") == "telno"
        else endpoint_data.get("interaction")
    )
    format = (
        None
        if endpoint_data.get("transport") == "telno"
        else endpoint_data.get("format")
    )

    return Endpoint(
        id=uuid4(),
        identifier_oldDoS_id=endpoint_data.get("id"),
        status="active",
        connectionType=endpoint_data.get("transport"),
        name=None,
        description=endpoint_data.get("businessscenario"),
        payloadType=payload_type,
        address=endpoint_data.get("address"),
        managedByOrganisation=organisation_id,
        service=None,
        order=endpoint_data.get("endpointorder"),
        isCompressionEnabled=endpoint_data.get("iscompressionenabled") == "compressed",
        format=format,
        createdBy="ROBOT",
        createdDateTime=current_timestamp,
        modifiedBy="ROBOT",
        modifiedDateTime=current_timestamp,
    )


def transform_gp_practices(
    df: pd.DataFrame, current_timestamp: datetime
) -> pd.DataFrame:
    if df.empty:
        err_msg = "No data found in the input DataFrame"
        raise ValueError(err_msg)

    gp_practices = []
    for _, row in df.iterrows():
        organisation = create_organisation(row, current_timestamp)

        endpoints_data = row.get("endpoints", [])
        if endpoints_data is None or len(endpoints_data) == 0:
            logging.info(f"No endpoints found for organisation {organisation.id}")
            endpoints_data = []

        organisation.endpoints = [
            create_endpoint(ep, organisation.id, current_timestamp)
            for ep in endpoints_data
        ]
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
