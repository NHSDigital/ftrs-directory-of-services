from pipeline.extract import extract_telecom
from pipeline.validators import StatusEnum


def transfrom_into_payload(organisation_data: dict, primary_role_data: dict) -> dict:
    return {
        "active": organisation_data.Status == StatusEnum.active,
        "name": organisation_data.Name,
        "telecom": extract_telecom(organisation_data),
        "type": primary_role_data.displayName,
        "modified_by": "ODS_ETL_PIPELINE",
    }
