from pipeline.validators import StatusEnum


def transfrom_into_payload(organisation_data: dict, primary_role_data: dict) -> dict:
    return {
        "active": organisation_data.Status == StatusEnum.active,
        "name": organisation_data.Name,
        "telecom": (
            organisation_data.Contact.value if organisation_data.Contact else None
        ),
        "type": primary_role_data.displayName,
        "modified_by": "ODS_ETL_PIPELINE",
    }
