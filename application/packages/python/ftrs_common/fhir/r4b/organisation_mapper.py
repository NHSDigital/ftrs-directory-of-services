from fhir.resources.R4B.contactpoint import ContactPoint
from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.organization import Organization
from ftrs_common.fhir.base_mapper import FhirMapper
from ftrs_common.fhir.fhir_validator import FhirValidator
from ftrs_data_layer.models import Organisation


TYPE_TO_CODE = {
    "GP PRACTICE": "76",
}

class OrganizationMapper(FhirMapper):
    def to_fhir(self, model_obj):
        return super().to_fhir(model_obj)

    def from_fhir(self, fhir_resource):
        """
        Convert a FHIR Organization resource to the internal OrganisationPayload Pydantic model.
        """
        name = fhir_resource.name if hasattr(fhir_resource, "name") else None
        active = fhir_resource.active if hasattr(fhir_resource, "active") else None
        telecom = self._get_org_telecom(fhir_resource)

        org_type = self._get_org_type(fhir_resource)

        return Organisation(
            identifier_ODS_ODSCode=fhir_resource.id,
            name=name,
            active=active if active is not None else False,
            telecom=telecom,
            type=org_type,
            modified_by="ODS_ETL_PIPELINE",
        )

    def from_ods_fhir_to_fhir(self, ods_fhir_organization) -> Organization:
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
            required_fields["telecom"] = self._create_contact_point_from_telecom(telecom)

        fhir_organisation = FhirValidator.validate(required_fields, Organization)
        return fhir_organisation

    def _get_org_type(self, fhir_org: Organization) -> str | None:
        org_type = None
        if hasattr(fhir_org, "type") and fhir_org.type:
            type_obj = fhir_org.type[0]
            if getattr(type_obj, "text", None):
                org_type = type_obj.text
            elif getattr(type_obj, "coding", None) and type_obj.coding:
                org_type = type_obj.coding[0].display or type_obj.coding[0].code
        return org_type

    def _get_org_telecom(self, fhir_org: Organization) -> list[ContactPoint] | None:
        if hasattr(fhir_org, "telecom") and fhir_org.telecom:
            for t in fhir_org.telecom:
                if getattr(t, "system", None) == "phone":
                    return t.value
        return None

    def _extract_role_from_extension(self, ods_org: dict) -> str | None:
        for ext in ods_org.get("extension", []):
            if self._is_org_role_extension(ext) and self._is_primary_role(ext):
                return self._get_role_display_from_extension(ext)
        return None

    def _is_org_role_extension(self, ext: dict) -> bool:
        return ext.get("url") == "https://fhir.nhs.uk/STU3/StructureDefinition/Extension-ODSAPI-OrganizationRole-1"

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


    def _create_codable_concept_for_type(self, ods_org: dict) -> list[dict]:
        org_type = self._extract_role_from_extension(ods_org)
        return [
            {
                "coding": [
                    {
                        "system": "todo",
                        "code": TYPE_TO_CODE.get(org_type),
                        "display": org_type,
                    }
                ]
            }
        ]

    def _create_contact_point_from_telecom(self, telecom: dict) -> list[ContactPoint]:
        contact_points = []
        for t in telecom:
            if t.get("system") == "phone":
                contact_point = t.copy()
                if "use" not in contact_point:
                    contact_point["use"] = "work"
                contact_points.append(ContactPoint.model_validate(contact_point).model_dump(exclude_none=True))
        return contact_points
