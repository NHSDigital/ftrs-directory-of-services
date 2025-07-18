from fhir.resources.R4B.organization import Organization as FhirOrganisation
from ftrs_common.fhir.r4b.organisation_mapper import OrganizationMapper
from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

ods_processor_logger = Logger.get(service="ods_processor")


def transform_to_payload(ods_fhir: dict, ods_code: str) -> FhirOrganisation:
    """
    Convert ODS FHIR resource to a FhirOrganisation resource.
    """
    organisation = OrganizationMapper().from_ods_fhir_to_fhir(ods_fhir)
    ods_processor_logger.log(
        OdsETLPipelineLogBase.ETL_PROCESSOR_026,
        ods_code=ods_code,
    )
    return organisation
