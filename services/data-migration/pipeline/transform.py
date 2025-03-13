import logging
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import pandas as pd
from pydantic import BaseModel

from packages.data_models import Endpoints, Organisation

# Logging has been created to track unmappable/un-transformable data
    # Logging includes totals and percentage calculations of transformed and un-transformed data
# Transformed data is output into a suitable format
# Implemented as a Python function that could be called via CLI or Lambda invocation
# Implemented transformations and any issues must be documented in the register of data issues created in FDOS-151

class GPPractice(BaseModel):
    organisation: Organisation
    endpoints: list[Endpoints] | None

def create_GP_practices_list(df: pd.DataFrame, current_timestamp: str) -> list[GPPractice]:
    gp_practices = []
    for index, row in df.iterrows():
        if df.empty:
            logging.error("No data found")
            return
        
        organisation = Organisation(
            id=uuid4(),
            identifier_ODS_ODSCode=row['odscode'],
            active=True,
            name=row['name'],
            telecom=None, # data dictionary doesnt give a data type for this so i've made it str and none
            type=row['type'],
            createdBy='ROBOT',
            createdDateTime=current_timestamp,
            modifiedBy='ROBOT',
            modifiedDateTime=current_timestamp,
        )

        endpoints_data = row.get('endpoints', [])
        endpoints = []
        if endpoints_data is None:
            logging.error("No endpoints found for the organisation")
            gp_practices.append(GPPractice(organisation=organisation, endpoints=None))
            continue
        for endpoint_data in endpoints_data:
            endpoint = Endpoints(
                id=uuid4(),
                identifier_oldDoS_id=endpoint_data.get('endpointid'),
                status='active',
                connectionType=endpoint_data.get('transport'),
                name=None,
                description=endpoint_data.get('businessscenario'), 
                payloadType='' if endpoint_data.get('transport') == 'telno' else endpoint_data.get('interaction'),
                address=endpoint_data.get('address'),
                managedByOrganisation=organisation.id,
                service=None, # defaulting to none - will need to be linked properly
                order=endpoint_data.get('endpointorder'),
                isCompressionEnabled=endpoint_data.get('iscompressionenabled') == 'compressed',
                format='' if endpoint_data.get('transport') == 'telno' else endpoint_data.get('format'),
                createdBy='ROBOT',
                createdDateTime=current_timestamp,
                modifiedBy='ROBOT',
                modifiedDateTime=current_timestamp,
            )
            endpoints.append(endpoint)
        gp_practices.append(GPPractice(organisation=organisation, endpoints=endpoints))

    return gp_practices

def convert_list_to_dict(gp_practices: list[GPPractice]) -> dict:
    gp_dicts = [gp.model_dump() for gp in gp_practices]
    gp_dicts = convert_UUID_to_string(gp_dicts)
    return gp_dicts

def convert_UUID_to_string(gp_dicts: dict) -> list[GPPractice]:
    for gp_dict in gp_dicts:
        gp_dict['organisation']['id'] = str(gp_dict['organisation']['id'])
        if gp_dict['endpoints']:
            for endpoint in gp_dict['endpoints']:
                endpoint['id'] = str(endpoint['id'])
                endpoint['managedByOrganisation'] = str(endpoint['managedByOrganisation'])

    return gp_dicts

def logging_metrics(gp_practices: list[GPPractice]) -> None:
    logging.info(f"Total number of GP practices: {len(gp_practices)}")

def transform(input_path: Path, output_path: Path) -> None:
    logging.info(f"Transforming data from {input_path} to {output_path}")

    current_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    df = pd.read_parquet(input_path)

    gp_practices = create_GP_practices_list(df, current_timestamp)
    gp_dicts = convert_list_to_dict(gp_practices)
    gp_df = pd.DataFrame(gp_dicts)

    gp_df.to_parquet(
        output_path / f"dos-gp-practice-transform-{current_timestamp}.parquet",
        engine="pyarrow",
        index=False,
        compression="zstd",
    )

    logging_metrics(gp_df)

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
