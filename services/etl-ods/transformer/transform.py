from fhir.resources.R4B.organization import Organization as FhirOrganisation
from ftrs_common.fhir.r4b.organisation_mapper import OrganizationMapper
from ftrs_common.logger import Logger

ods_transformer_logger = Logger.get(service="ods_transformer")


def transform_to_payload(ods_fhir: dict) -> FhirOrganisation:
    """
    Convert ODS FHIR resource to a FhirOrganisation resource.
    """
    organisation = OrganizationMapper().from_ods_fhir_to_fhir(ods_fhir)
    return organisation
