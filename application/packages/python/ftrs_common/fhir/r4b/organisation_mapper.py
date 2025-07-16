from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.identifier import Identifier
from fhir.resources.R4B.organization import Organization as FhirOrganisation
from ftrs_common.fhir.base_mapper import FhirMapper
from ftrs_common.fhir.fhir_validator import FhirValidator
from ftrs_data_layer.models import Organisation

TYPE_TO_CODE = {
    "GP PRACTICE": "76",
}


class OrganizationMapper(FhirMapper):
    def _build_meta_profile(self) -> dict:
        return {
            "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
        }

    def _build_identifier(self, ods_code: str) -> list[Identifier]:
        return [
            Identifier.model_validate(
                {
                    "use": "official",
                    "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                    "value": ods_code,
                }
            )
        ]

    def _build_telecom(self, telecom: str | None) -> list[dict]:
        if telecom:
            return [{"system": "phone", "value": telecom, "use": "work"}]
        return []

    def _build_type(self, org_type_value: str) -> list[CodeableConcept]:
        return [
            CodeableConcept.model_validate(
                {
                    "coding": [
                        {
                            "system": "TO-DO",  # Use correct system if available
                            "code": org_type_value if org_type_value else "GP Service",
                            "display": org_type_value
                            if org_type_value
                            else "GP Service",
                        }
                    ],
                    "text": org_type_value if org_type_value else "GP Service",
                }
            )
        ]

    def to_fhir(self, organisation: Organisation) -> FhirOrganisation:
        org_dict = {
            "resourceType": "Organization",
            "id": str(organisation.id),
            "meta": self._build_meta_profile(),
            "active": organisation.active,
            "name": organisation.name,
            "type": self._build_type(getattr(organisation, "type", None)),
            "identifier": self._build_identifier(organisation.identifier_ODS_ODSCode),
            "telecom": self._build_telecom(organisation.telecom),
        }
        org = FhirOrganisation.model_validate(org_dict)
        return org

    def from_fhir(self, fhir_resource: FhirOrganisation) -> Organisation:
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

    def from_ods_fhir_to_fhir(self, ods_fhir_organization: dict) -> FhirOrganisation:
        required_fields = {
            "resourceType": "Organization",
            "id": ods_fhir_organization.get("id"),
            "meta": self._build_meta_profile(),
            "active": ods_fhir_organization.get("active"),
            "name": ods_fhir_organization.get("name"),
            "type": self._build_type(ods_fhir_organization.get("type")),
            "identifier": self._build_identifier(
                ods_fhir_organization.get("identifier", {}).get("value")
            ),
            "telecom": ods_fhir_organization.get("telecom", []),
        }
        fhir_organisation = FhirValidator.validate(required_fields, FhirOrganisation)
        return fhir_organisation

    def _get_org_type(self, fhir_org: FhirOrganisation) -> str | None:
        if hasattr(fhir_org, "type") and fhir_org.type:
            type_obj = fhir_org.type[0]
            if getattr(type_obj, "text", None):
                return type_obj.text
        return None

    def _get_org_telecom(self, fhir_org: FhirOrganisation) -> str | None:
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
