from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.contactpoint import ContactPoint
from fhir.resources.R4B.identifier import Identifier
from fhir.resources.R4B.organization import Organization, OrganizationContact
from ftrs_common.fhir.base_mapper import FhirMapper
from ftrs_common.fhir.fhir_validator import FhirValidator
from ftrs_data_layer.models import Organisation

TYPE_TO_CODE = {
    "GP PRACTICE": "76",
}


class OrganizationMapper(FhirMapper):
    def to_fhir(self, organisation: Organisation) -> Organization:
        organization_id = str(organisation.id)  # ensure string
        name = organisation.name
        active = organisation.active
        identifier = self._create_identifier(
            ods_code=organisation.identifier_ODS_ODSCode
        )
        contact = (
            [self._create_organization_contact_from_internal(organisation.telecom)]
            if organisation.telecom
            else None
        )

        org = Organization.model_validate(
            {
                "id": organization_id,
                "identifier": identifier,
                "active": active,
                "name": name,
                "contact": contact,
            }
        )

        return org

    def from_fhir(self, fhir_resource: Organization) -> Organisation:
        """
        Convert a FHIR Organization resource to the internal OrganisationPayload Pydantic model.
        """
        telecom = self._get_org_telecom(fhir_resource)
        org_type = self._get_org_type(fhir_resource)
        id_value = str(fhir_resource.id)

        return Organisation(
            identifier_ODS_ODSCode=fhir_resource.identifier[0].value,
            id=id_value,
            name=fhir_resource.name,
            active=fhir_resource.active,
            telecom=telecom,
            type=org_type,
            modifiedBy="ODS_ETL_PIPELINE",
        )

    def from_ods_fhir_to_fhir(self, ods_fhir_organization: dict) -> Organization:
        """
        Convert a FHIR ODS Organization resource a FHIR Organization resource.
        """
        required_fields = {
            "resourceType": "Organization",
            "active": ods_fhir_organization.get("active"),
            "type": self._create_codable_concept_for_type(ods_fhir_organization),
            "name": ods_fhir_organization.get("name"),
            "id": ods_fhir_organization.get("identifier", {}).get("value"),
        }
        telecom = ods_fhir_organization.get("telecom")
        if telecom:
            # Wrap ContactPoint(s) in OrganizationContact as required by FHIR spec
            contact_points = self._create_contact_point_from_ods(telecom)
            if contact_points:
                required_fields["contact"] = [
                    OrganizationContact.model_validate({"telecom": contact_points})
                ]

        fhir_organisation = FhirValidator.validate(required_fields, Organization)
        return fhir_organisation

    def _get_org_type(self, fhir_org: Organization) -> str | None:
        org_type = None
        if hasattr(fhir_org, "type") and fhir_org.type:
            type_obj = fhir_org.type[0]
            if getattr(type_obj, "text", None):
                org_type = type_obj.text
        return org_type

    def _get_org_telecom(self, fhir_org: Organization) -> str | None:
        if hasattr(fhir_org, "contact") and fhir_org.contact:
            for contact in fhir_org.contact:
                phone_value = self._find_phone_in_contact(contact)
                if phone_value:
                    return phone_value
        return None

    def _find_phone_in_contact(self, contact: OrganizationContact) -> str | None:
        if hasattr(contact, "telecom") and contact.telecom:
            for t in contact.telecom:
                if getattr(t, "system", None) == "phone":
                    return t.value
        return None

    def _extract_role_from_extension(self, ods_org: dict) -> str | None:
        for ext in ods_org.get("extension", []):
            if self._is_org_role_extension(ext) and self._is_primary_role(ext):
                return self._get_role_display_from_extension(ext)
        return None

    def _is_org_role_extension(self, ext: dict) -> bool:
        return (
            ext.get("url")
            == "https://fhir.nhs.uk/STU3/StructureDefinition/Extension-ODSAPI-OrganizationRole-1"
        )

    def _is_primary_role(self, ext: dict) -> bool:
        return any(
            sub_ext.get("url") == "primaryRole" and sub_ext.get("valueBoolean") is True
            for sub_ext in ext.get("extension", [])
        )

    def _get_role_display_from_extension(self, ext: dict) -> str | None:
        for sub_ext in ext.get("extension", []):
            if sub_ext.get("url") == "role":
                value_coding = sub_ext.get("valueCoding")
                if value_coding and "display" in value_coding:
                    return value_coding["display"]
        return None

    def _create_codable_concept_for_type(self, ods_org: dict) -> list[CodeableConcept]:
        org_type = self._extract_role_from_extension(ods_org)
        return [
            CodeableConcept.model_validate(
                {
                    "coding": [
                        {
                            "system": "todo",
                            "code": TYPE_TO_CODE.get(org_type),
                            "display": org_type,
                        }
                    ]
                }
            )
        ]

    def _create_organisation_contact_from_ods(self, telecom: list[dict]) -> list[OrganizationContact]:
        """Create a list of OrganizationContact objects from the telecom information in the ODS Organization resource.
        This defaults to mapping all telecom entries with system "phone" from ODS to a 'work' ContactPoint.
        """
        contact_points = []
        for t in telecom:
            if t.get("system") == "phone":
                contact_point = t.copy()
                contact_point["use"] = "work"
                contact_points.append(ContactPoint.model_validate(contact_point))
        if contact_points:
            return [OrganizationContact.model_validate({"telecom": contact_points})]
        return []

    def _create_contact_point_from_internal(self, telecom: str) -> ContactPoint:
        return ContactPoint.model_validate(
            {
                "system": "phone",
                "value": telecom,
            }
        )

    def _create_organization_contact_from_internal(
        self, telecom: str
    ) -> OrganizationContact:
        return OrganizationContact.model_validate(
            {
                "telecom": [
                    {
                        "system": "phone",
                        "value": telecom,
                    }
                ]
            }
        )

    def _create_identifier(self, ods_code: str) -> list[Identifier]:
        identifier = Identifier.model_validate(
            {
                "use": "official",
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": ods_code,
            }
        )

        return [identifier]
