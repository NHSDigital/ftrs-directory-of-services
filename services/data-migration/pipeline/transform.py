import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

import pandas as pd

from packages.data_models import Endpoints, Organisation


def create_organisation(row: pd.Series, current_timestamp: str) -> Organisation:
    return Organisation(
        id=uuid4(),
        identifier_ODS_ODSCode=row["odscode"],
        active=True,
        name=row["name"],
        telecom=None,
        type=row["type"],
        createdBy="ROBOT",
        createdDateTime=current_timestamp,
        modifiedBy="ROBOT",
        modifiedDateTime=current_timestamp,
    )


def create_endpoint(
    endpoint_data: Dict[str, str], organisation_id: uuid4, current_timestamp: str
) -> Endpoints:
    return Endpoints(
        id=uuid4(),
        identifier_oldDoS_id=endpoint_data.get("endpointid"),
        status="active",
        connectionType=endpoint_data.get("transport"),
        name=None,
        description=endpoint_data.get("businessscenario"),
        payloadType=""
        if endpoint_data.get("transport") == "telno"
        else endpoint_data.get("interaction"),
        address=endpoint_data.get("address"),
        managedByOrganisation=organisation_id,
        service=None,
        order=endpoint_data.get("endpointorder"),
        isCompressionEnabled=endpoint_data.get("iscompressionenabled") == "compressed",
        format=""
        if endpoint_data.get("transport") == "telno"
        else endpoint_data.get("format"),
        createdBy="ROBOT",
        createdDateTime=current_timestamp,
        modifiedBy="ROBOT",
        modifiedDateTime=current_timestamp,
    )


def convert_UUID_to_string(gp_dicts: dict) -> Dict[str, Any]:
    for gp_dict in gp_dicts:
        gp_dict["organisation"]["id"] = str(gp_dict["organisation"]["id"])
        if gp_dict["endpoints"]:
            for endpoint in gp_dict["endpoints"]:
                endpoint["id"] = str(endpoint["id"])
                endpoint["managedByOrganisation"] = str(
                    endpoint["managedByOrganisation"]
                )

    return gp_dicts


def create_GP_practices_dict(
    df: pd.DataFrame, current_timestamp: str
) -> List[Dict[str, Any]]:
    if df.empty:
        logging.error("No data found")
        return []

    gp_practices = []
    for _, row in df.iterrows():
        organisation = create_organisation(row, current_timestamp)
        endpoints_data = row.get("endpoints", [])
        if endpoints_data is None:
            logging.error("No endpoints found for the organisation")
            gp_practices.append(
                {"organisation": organisation.model_dump(), "endpoints": None}
            )
            continue

        endpoints = [
            create_endpoint(ed, organisation.id, current_timestamp)
            for ed in endpoints_data
        ]
        gp_practices.append(
            {
                "organisation": organisation.model_dump(),
                "endpoints": [ep.model_dump() for ep in endpoints],
            }
        )

    return gp_practices


def transform(input_path: Path, output_path: Path) -> None:
    logging.info(f"Transforming data from {input_path} to {output_path}")

    current_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    extract_dataframe = pd.read_parquet(input_path)

    gp_practices = create_GP_practices_dict(extract_dataframe, current_timestamp)
    gp_practices = convert_UUID_to_string(gp_practices)
    transform_gp_dataframe = pd.DataFrame(gp_practices)

    transform_gp_dataframe.to_parquet(
        output_path / f"dos-gp-practice-transform-{current_timestamp}.parquet",
        engine="pyarrow",
        index=False,
        compression="zstd",
    )


def main(args: list[str] | None = None) -> None:
    import argparse

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Extract data from source")
    parser.add_argument(
        "--input-path", type=Path, required=True, help="Path to read the extracted data"
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        required=True,
        help="Path to save the extracted data",
    )
    args = parser.parse_args(args)
    transform(args.input_path, args.output_path)
