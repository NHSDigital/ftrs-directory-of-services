from fhir.resources.R4B.identifier import Identifier
from fhir.resources.R4B.organization import Organization as FhirOrganization
from ftrs_data_layer.domain import Organisation

from functions.constants import ODS_ORG_CODE_IDENTIFIER_SYSTEM


class OrganizationMapper:
    def map_to_fhir_organization(self, organisation: Organisation) -> FhirOrganization:
        organization_id = str(organisation.id)
        name = organisation.name
        active = organisation.active
        identifier = self._create_identifier(organisation)

        fhir_organization = FhirOrganization.model_validate(
            {
                "id": organization_id,
                "identifier": identifier,
                "active": active,
                "name": name,
            }
        )
        return fhir_organization

    def _create_identifier(self, organisation: Organisation) -> list[Identifier]:
        identifier = Identifier.model_validate(
            {
                "use": "official",
                "system": ODS_ORG_CODE_IDENTIFIER_SYSTEM,
                "value": organisation.identifier_ODS_ODSCode,
            }
        )

        return [identifier]
