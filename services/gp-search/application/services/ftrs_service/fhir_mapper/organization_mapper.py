from fhir.resources.R4B.address import Address
from fhir.resources.R4B.contactpoint import ContactPoint
from fhir.resources.R4B.identifier import Identifier
from fhir.resources.R4B.organization import Organization
from services.ftrs_service.repository.dynamo import (
    OrganizationRecord,
    OrganizationValue,
)


class OrganizationMapper:
    def map_to_organization_resource(
        self, organization_record: OrganizationRecord
    ) -> Organization:
        organization_value = organization_record.value

        organization_id = organization_value.id
        name = organization_value.name
        active = organization_value.active
        identifier = self._create_identifier(organization_value)
        telecom = self._create_telecom(organization_value)
        address = self._create_dummy_address()

        org = Organization.model_validate(
            {
                "id": organization_id,
                "identifier": identifier,
                "active": active,
                "name": name,
                "telecom": telecom,
                "address": address,
            }
        )

        return org

    def _create_identifier(
        self, organization_value: OrganizationValue
    ) -> list[Identifier]:
        identifier = Identifier.model_validate(
            {
                "use": "official",
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": organization_value.identifier_ODS_ODSCode,
            }
        )

        return [identifier]

    def _create_telecom(
        self, organization_value: OrganizationValue
    ) -> list[ContactPoint]:
        telecom_entry = ContactPoint.model_validate(
            {
                "system": "phone",
                "value": organization_value.telecom,
            }
        )

        return [telecom_entry]

    def _create_dummy_address(self) -> list[Address]:
        address = Address.model_validate(
            {
                "line": ["Dummy Medical Practice", "Dummy Street"],
                "city": "Dummy City",
                "postalCode": "DU00 0MY",
                "country": "ENGLAND",
            }
        )

        return [address]
