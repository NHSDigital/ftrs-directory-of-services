from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

from pipeline.validators import StatusEnum

ods_processor_logger = Logger.get(service="ods_processor")

ods_processor_logger = Logger.get(service="ods_processor")


def transfrom_into_payload(
    organisation_data: dict, primary_role_data: dict, ods_code: str
) -> dict:
    transformed_payload = {
        "active": organisation_data.Status == StatusEnum.active,
        "name": organisation_data.Name,
        "telecom": (
            organisation_data.Contact.value if organisation_data.Contact else None
        ),
        "type": primary_role_data.displayName,
        "modified_by": "ODS_ETL_PIPELINE",
    }
    ods_processor_logger.log(
        OdsETLPipelineLogBase.ETL_PROCESSOR_026,
        ods_code=ods_code,
    )
    return transformed_payload
