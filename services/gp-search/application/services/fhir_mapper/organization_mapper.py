"""Organization Mapper Service - Maps organization raw_data to FHIR Organization resources."""

#  amazonq-ignore-next-line
from typing import Any

from fhir.resources.R4B.address import Address
from fhir.resources.R4B.contactpoint import ContactPoint
from fhir.resources.R4B.identifier import Identifier
from fhir.resources.R4B.organization import Organization


class OrganizationMapper:
    """Service to map organization raw_data to FHIR Organization resources."""

    def map_to_organization(self, raw_data: dict[str, Any]) -> Organization:
        """Map organization raw_data from DynamoDB to a FHIR Organization resource.

        Args:
            raw_data: The organization raw_data from DynamoDB

        Returns:
            A FHIR Organization resource

        """
        # Set basic properties - handle both raw and parsed formats

        raw_organisation = raw_data.get("value", {})

        organization_id = raw_organisation.get("id")
        name = raw_organisation.get("name")
        active = raw_organisation.get("active")

        # Map ODS code to identifier

        identifier = self._create_identifier(raw_organisation)

        # Map telecom if available
        telecom_list = self._process_telecom_data(raw_organisation)

        address = self._create_address(raw_organisation)

        org_dict = {
            "id": organization_id,
            "identifier": identifier,
            "active": active,
            "name": name,
            "telecom": telecom_list,
            "address": address,
        }
        org = Organization.model_validate(org_dict)

        return org

    def _create_identifier(self, raw_organisation: dict) -> list[Identifier]:
        identifier = Identifier.model_validate(
            {
                "use": "official",
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": raw_organisation.get("identifier_ODS_ODSCode"),
            }
        )

        return [identifier]

    def _process_telecom_data(
        self,
        data: dict[str, Any],
    ) -> list[ContactPoint] | None:
        telecom = data.get("telecom")

        return [telecom] if telecom else None

    def _create_address(self, data: dict[str, Any]) -> list[Address]:
        # TODO: Dynamo DB data does not include address, make dummy data
        address = Address.model_validate(
            {
                "line": ["Dummy Medical Practice", "Dummy Street"],
                "city": "Dummy City",
                "postalCode": "DU00 0MY",
                "country": "ENGLAND",
            }
        )

        return [address]
