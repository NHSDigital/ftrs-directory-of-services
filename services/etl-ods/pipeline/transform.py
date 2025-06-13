from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

from pipeline.validators import StatusEnum
from fhir.resources.R4B.organization import Organization

ods_processor_logger = Logger.get(service="ods_processor")

def transfrom_into_payload(org_resource: Organization) -> dict:
    result = {
        "resourceType": org_resource.get("resourceType"),
        "id" : org_resource.get("id"),
        "meta": org_resource.get("meta"),
        "extension": org_resource.get("resourceType"),
        "active":org_resource.get("active"),
        "name":org_resource.get("name"),
        "telecom": org_resource.get("telecom", None),
    }
    ods_processor_logger.log(
        OdsETLPipelineLogBase.ETL_PROCESSOR_026,
        ods_code=ods_code,
    )
    return result
